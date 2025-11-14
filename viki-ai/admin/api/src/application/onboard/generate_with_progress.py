"""
Onboard Generation Application Service with DJT Progress Tracking

This module contains the enhanced application layer service for onboarding generation
that includes progress tracking using the Distributed Job Tracking (DJT) service.
"""

import io
import json
import uuid
from typing import BinaryIO, Dict, Any, Optional
from viki_shared.utils.logger import getLogger
from viki_shared.utils.pdf_conversion import PDFConverter, PDFConversionError

from contracts.file_storage_contracts import (
    FileStoragePort,
    StorageLocation,
    StorageMetadata,
    FileStorageError
)
from contracts.entity_extraction_contracts import (
    EntityExtractionPort,
    LlmExecuteRequest
)
from contracts.djt_contracts import DJTPort
from contracts.config_contracts import ConfigPort
from shared.domain.models.djt_models import PipelineStatusUpdate, PipelineStatus
from models.onboard_models import OnboardGenerationResult, StorageMetadataModel
from settings import Settings

logger = getLogger(__name__)


class OnboardGenerationWithProgressService:
    """
    Enhanced application service for onboarding generation operations with DJT progress tracking.
    
    This service handles the complete onboarding generation workflow with real-time progress updates:
    1. Create DJT job with all subtasks defined upfront
    2. Upload files to cloud storage (with progress updates)
    3. Generate JSON schema based on meta prompt (with progress updates)
    4. Generate extraction prompt (with progress updates)
    5. Perform test extraction (with progress updates)
    """

    # Define all onboarding tasks upfront
    ONBOARD_TASKS = [
        {
            "id": "file_upload",
            "name": "File Upload",
            "description": "Uploading sample document to cloud storage"
        },
        {
            "id": "schema_generation", 
            "name": "Schema Generation",
            "description": "Analyzing document and generating extraction schema"
        },
        {
            "id": "prompt_generation",
            "name": "Prompt Generation", 
            "description": "Creating optimized extraction prompt"
        },
        {
            "id": "test_extraction",
            "name": "Test Extraction",
            "description": "Testing extraction on sample document"
        }
    ]

    def __init__(
        self, 
        file_storage: FileStoragePort, 
        entity_extraction: EntityExtractionPort, 
        config: ConfigPort,
        djt_client: DJTPort,
        settings: Settings
    ):
        """
        Initialize the generation service with DJT tracking.
        
        Args:
            file_storage: File storage port implementation
            entity_extraction: Entity extraction service port implementation
            config: Config port implementation for retrieving LLM configurations
            djt_client: DJT client for progress tracking
            settings: Application settings for bucket configuration
        """
        self._file_storage = file_storage
        self._entity_extraction = entity_extraction
        self._config = config
        self._djt_client = djt_client
        self._settings = settings
        self._pdf_converter = PDFConverter(quality=95, optimize=True)
        logger.info("Onboard Generation Service with Progress Tracking initialized")

    async def generate_onboard_config_with_progress(
        self,
        job_id: str,
        app_id: str,
        file_content: BinaryIO,
        content_type: str,
        original_filename: str,
        meta_prompt: str,
        business_unit: str,
        solution_id: str,
        name: str,
        description: str
    ) -> OnboardGenerationResult:
        """
        Execute the complete onboard generation workflow with DJT progress tracking.
        
        Args:
            job_id: The predetermined job ID from frontend
            app_id: The application ID for path generation
            file_content: The file content as a binary stream
            content_type: MIME type of the file
            original_filename: Original name of the uploaded file
            meta_prompt: User's description of data to extract
            business_unit: Business unit code
            solution_id: Solution ID code
            name: Pipeline name
            description: Pipeline description
            
        Returns:
            OnboardGenerationResult: Generation results
            
        Raises:
            FileStorageError: If upload fails
        """
        logger.info(f"Starting onboard generation with progress tracking for app_id: {app_id}, job_id: {job_id}")
        
        try:
            # Step 0: Create DJT job with all subtasks defined upfront
            await self._create_djt_job_with_subtasks(job_id, app_id, business_unit, solution_id, name, description)
            
            # Step 1: Upload file to storage
            await self._update_task_status(job_id, "file_upload", PipelineStatus.IN_PROGRESS, app_id)
            storage_metadata = await self._upload_file(
                app_id=app_id,
                file_content=file_content,
                content_type=content_type,
                original_filename=original_filename
            )
            await self._update_task_status(job_id, "file_upload", PipelineStatus.COMPLETED, app_id)
            
            # Step 2: Generate JSON schema from meta prompt using LLM
            await self._update_task_status(job_id, "schema_generation", PipelineStatus.IN_PROGRESS, app_id)
            entity_schema = await self._generate_entity_schema_with_llm(
                storage_metadata=storage_metadata,
                meta_prompt=meta_prompt,
                app_id=app_id
            )
            await self._update_task_status(job_id, "schema_generation", PipelineStatus.COMPLETED, app_id)
            
            # Step 3: Generate hardened production extraction prompt
            await self._update_task_status(job_id, "prompt_generation", PipelineStatus.IN_PROGRESS, app_id)
            extraction_prompt = await self._generate_extraction_prompt_with_llm(
                storage_metadata=storage_metadata,
                meta_prompt=meta_prompt,
                app_id=app_id
            )
            await self._update_task_status(job_id, "prompt_generation", PipelineStatus.COMPLETED, app_id)
            
            # Step 4: Perform test extraction using generated schema and prompt
            await self._update_task_status(job_id, "test_extraction", PipelineStatus.IN_PROGRESS, app_id)
            test_extraction_result = await self._perform_test_extraction_with_llm(
                storage_metadata=storage_metadata,
                entity_schema=entity_schema,
                extraction_prompt=extraction_prompt,
                app_id=app_id
            )
            await self._update_task_status(job_id, "test_extraction", PipelineStatus.COMPLETED, app_id)
            
            # Create properly typed storage metadata model
            storage_metadata_model = StorageMetadataModel(
                content_type=storage_metadata.content_type,
                size_bytes=storage_metadata.size_bytes,
                storage_path=self.get_storage_path(app_id),
                created_at=storage_metadata.created_at
            )
            
            # Create the result model
            result = OnboardGenerationResult(
                storage_metadata=storage_metadata_model,
                entity_schema=entity_schema,
                extraction_prompt=extraction_prompt,
                test_extraction=test_extraction_result
            )
            
            logger.info(f"Completed onboard generation with progress tracking for app_id: {app_id}, job_id: {job_id}")
            return result
            
        except Exception as e:
            # Mark the current task as failed
            current_task = await self._get_current_or_next_task(job_id)
            if current_task:
                await self._update_task_status(job_id, current_task, PipelineStatus.FAILED, app_id, str(e))
            
            logger.error(f"Failed onboard generation for app_id: {app_id}, job_id: {job_id}", exc_info=True)
            raise FileStorageError(f"Generation failed: {str(e)}") from e

    async def _create_djt_job_with_subtasks(
        self, 
        job_id: str, 
        app_id: str, 
        business_unit: str, 
        solution_id: str, 
        name: str, 
        description: str
    ) -> None:
        """
        Create a DJT job with all subtasks defined upfront for accurate progress tracking.
        """
        # Create the parent job first
        job_data = {
            "app_id": app_id,
            "business_unit": business_unit,
            "solution_id": solution_id,
            "name": name,
            "description": description,
            "job_type": "onboarding",
            "operation_type": "onboarding",  # Explicit operation type to prevent Paperglass callbacks
            "total_tasks": len(self.ONBOARD_TASKS),
            "tenant_id": "admin",  # Required by DJT API
            "patient_id": "onboarding",  # Required by DJT API
            "document_id": app_id,  # Required by DJT API
            "run_id": job_id,  # Required by DJT API
            "pages": 1,  # Required by DJT API
            "metadata": {
                "service": "admin-api",
                "operation": "onboard_generation",
                "total_tasks": len(self.ONBOARD_TASKS),
                "task_definitions": self.ONBOARD_TASKS
            }
        }
        
        try:
            # Create the parent job
            await self._djt_client.create_job(job_id, job_data)
            logger.info(f"Created DJT parent job for job_id: {job_id} with {len(self.ONBOARD_TASKS)} tasks")
            
            # Create all subtasks with NOT_STARTED status
            for index, task in enumerate(self.ONBOARD_TASKS):
                await self._create_subtask(job_id, task, app_id, index)
                
            logger.info(f"Created all {len(self.ONBOARD_TASKS)} subtasks for job_id: {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to create DJT job with subtasks for job_id: {job_id}: {str(e)}")
            raise

    async def _create_subtask(self, job_id: str, task_definition: Dict[str, str], app_id: str, order: int) -> None:
        """Create a subtask in DJT with NOT_STARTED status."""
        pipeline_data = PipelineStatusUpdate(
            id=task_definition["id"],
            status=PipelineStatus.NOT_STARTED,
            order=order,  # Set execution order for proper task sorting
            metadata={
                "task_name": task_definition["name"],
                "task_description": task_definition["description"],
                "created_at": "now"
            },
            app_id=app_id,
            tenant_id="admin",  # Admin service tenant
            patient_id="onboarding",  # Generic patient for onboarding
            document_id=app_id,  # Use app_id as document_id
            pages=1  # Single "page" for onboarding process
        )
        
        try:
            await self._djt_client.pipeline_status_update(job_id, task_definition["id"], pipeline_data)
            logger.debug(f"Created subtask in DJT: job_id={job_id}, task_id={task_definition['id']}")
        except Exception as e:
            logger.error(f"Failed to create subtask in DJT: job_id={job_id}, task_id={task_definition['id']}: {str(e)}")
            raise

    async def _update_task_status(
        self, 
        job_id: str, 
        task_id: str, 
        status: PipelineStatus, 
        app_id: str,
        error_message: Optional[str] = None
    ) -> None:
        """Update task status in DJT."""
        task_definition = next((task for task in self.ONBOARD_TASKS if task["id"] == task_id), None)
        
        # Get the task order from the ONBOARD_TASKS array
        task_order = None
        for index, task in enumerate(self.ONBOARD_TASKS):
            if task["id"] == task_id:
                task_order = index
                break
        
        pipeline_data = PipelineStatusUpdate(
            id=task_id,
            status=status,
            order=task_order,  # Preserve execution order for proper task sorting
            metadata={
                "task_name": task_definition["name"] if task_definition else task_id,
                "task_description": task_definition["description"] if task_definition else "",
                "error_message": error_message,
                "updated_at": "now"
            } if error_message else {
                "task_name": task_definition["name"] if task_definition else task_id,
                "task_description": task_definition["description"] if task_definition else "",
                "updated_at": "now"
            },
            app_id=app_id,
            tenant_id="admin",  # Admin service tenant
            patient_id="onboarding",  # Generic patient for onboarding
            document_id=app_id,  # Use app_id as document_id
            pages=1  # Single "page" for onboarding process
        )
        
        try:
            await self._djt_client.pipeline_status_update(job_id, task_id, pipeline_data)
            logger.info(f"Updated task status in DJT: job_id={job_id}, task_id={task_id}, status={status}")
        except Exception as e:
            logger.error(f"Failed to update task status in DJT: job_id={job_id}, task_id={task_id}: {str(e)}")
            # Don't re-raise as this shouldn't fail the main process

    async def _get_current_or_next_task(self, job_id: str) -> Optional[str]:
        """Get the current or next task for error handling."""
        try:
            job_status = await self._djt_client.get_job_pipelines(job_id)
            # Parse the job status to determine which task is currently running or failed
            # For simplicity, return the first incomplete task
            for task in self.ONBOARD_TASKS:
                # In a real implementation, you'd check the actual status from DJT
                # For now, return the first task as a fallback
                return task["id"]
            return None
        except Exception:
            return None

    # Actual implementations copied from OnboardGenerationService
    
    async def _upload_file(
        self,
        app_id: str,
        file_content: BinaryIO,
        content_type: str,
        original_filename: str
    ) -> StorageMetadata:
        """
        Upload the onboarding file to cloud storage.
        
        If the file is not a PDF but is a supported image format, converts it to PDF
        and stores both the original file and the converted PDF.
        
        Args:
            app_id: The application ID for path generation
            file_content: The file content as a binary stream
            content_type: MIME type of the file
            original_filename: Original name of the uploaded file
            
        Returns:
            StorageMetadata: Metadata about the uploaded PDF file
        """
        file_content.seek(0)  # Reset stream position
        
        # Check if file is already a PDF
        is_pdf = content_type.lower() == 'application/pdf'
        
        if is_pdf:
            # File is already PDF, upload directly
            logger.info(f"File is already PDF, uploading directly: {original_filename}")
            storage_location = self._generate_storage_location(app_id)
            
            metadata = await self._file_storage.upload_file(
                location=storage_location,
                content=file_content,
                content_type=content_type
            )
            
            logger.info(f"Successfully uploaded PDF file for app_id: {app_id}")
            return metadata
        else:
            # File is not PDF, check if it's a supported image format
            if self._pdf_converter.is_supported_format(original_filename):
                logger.info(f"Converting image to PDF: {original_filename} ({content_type})")
                
                # Step 1: Store the original file
                await self._store_original_file(app_id, file_content, content_type, original_filename)
                
                # Step 2: Convert to PDF
                file_content.seek(0)  # Reset for conversion
                try:
                    pdf_stream = self._pdf_converter.convert_image_to_pdf(
                        image_data=file_content,
                        original_filename=original_filename
                    )
                    
                    # Step 3: Store the converted PDF
                    storage_location = self._generate_storage_location(app_id)
                    metadata = await self._file_storage.upload_file(
                        location=storage_location,
                        content=pdf_stream,
                        content_type='application/pdf'
                    )
                    
                    logger.info(f"Successfully converted and uploaded PDF for app_id: {app_id}")
                    return metadata
                    
                except PDFConversionError as e:
                    logger.error(f"Failed to convert image to PDF: {str(e)}")
                    raise FileStorageError(f"PDF conversion failed: {str(e)}") from e
            else:
                # Unsupported format, store as-is but warn
                logger.warning(f"Unsupported file format for PDF conversion: {content_type}")
                storage_location = self._generate_storage_location(app_id)
                
                metadata = await self._file_storage.upload_file(
                    location=storage_location,
                    content=file_content,
                    content_type=content_type
                )
                
                logger.info(f"Successfully uploaded non-PDF file for app_id: {app_id}")
                return metadata

    async def _store_original_file(
        self,
        app_id: str,
        file_content: BinaryIO,
        content_type: str,
        original_filename: str
    ) -> StorageMetadata:
        """
        Store the original file in the original subdirectory.
        
        Args:
            app_id: The application ID
            file_content: The original file content
            content_type: MIME type of the original file
            original_filename: Original filename
            
        Returns:
            StorageMetadata: Metadata about the stored original file
        """
        # Generate storage location for original file
        original_location = self._generate_original_storage_location(app_id, original_filename)
        
        logger.info(f"Storing original file: bucket={original_location.bucket}, path={original_location.path}")
        
        # Upload the original file
        metadata = await self._file_storage.upload_file(
            location=original_location,
            content=file_content,
            content_type=content_type
        )
        
        logger.info(f"Successfully stored original file for app_id: {app_id}")
        return metadata

    async def _generate_entity_schema_with_llm(
        self, 
        storage_metadata: StorageMetadata,
        meta_prompt: str,
        app_id: str
    ) -> Dict[str, Any]:
        """
        Generate entity schema using LLM based on the uploaded document and meta prompt.
        
        Args:
            storage_metadata: Metadata about the uploaded file
            meta_prompt: User's description of what data to extract
            app_id: Application ID for context
            
        Returns:
            Dict representing the JSON schema generated by the LLM
        """
        logger.info(f"Generating entity schema using LLM for app_id: {app_id}")
        
        try:
            # Construct the GS URI from storage metadata
            storage_location = self._generate_storage_location(app_id)
            gs_uri = f"gs://{storage_location.bucket}/{storage_location.path}"
            
            # Prepare system instructions for schema generation
            system_instructions = (
                "You are an expert at analyzing documents and generating JSON schemas. "
                "You must return ONLY a valid, complete JSON schema object - no explanations, no markdown, no extra text. "
                "The response must be valid JSON that can be parsed directly. "
                "Ensure all JSON objects and arrays are properly closed with matching braces and brackets. "
                "Use proper JSON syntax with double quotes for all strings and property names. "
                "CRITICAL: Do NOT include 'examples' fields in any properties - they are forbidden and will cause validation errors."
            )
            
            # Prepare prompt for schema generation
            prompt = (
                f"Analyze the document and create a JSON Schema for extracting: {meta_prompt}\n\n"
                "Requirements:\n"
                "1. Return ONLY valid JSON - no explanations or markdown\n"
                "2. Use JSON Schema draft-07 format\n"
                "3. Include 'type': 'object' at root level\n"
                "4. Add 'properties' object with relevant fields\n"
                "5. Include 'required' array for mandatory fields\n"
                "6. Add descriptions for complex fields\n"
                "7. Ensure all braces and brackets are properly closed\n"
                "8. DO NOT include 'examples' fields in any properties - examples are not allowed\n\n"
                "Generate the JSON Schema now:"
            )
            
            # Prepare metadata for the request
            request_metadata = {
                "business_unit": "viki",
                "solution_id": "viki-admin",
                "app_id": app_id,
                "operation": "schema_generation"
            }
            
            # Get model parameters from config
            config = await self._config.get_config()
            model_parameters = config.get_model_parameters("schema_generation")
            
            # Create LLM request
            llm_request = LlmExecuteRequest(
                gs_uri=gs_uri,
                system_instructions=system_instructions,
                prompt=prompt,
                json_schema=None,  # No schema constraint for schema generation
                metadata=request_metadata,
                model_parameters=model_parameters
            )
            
            logger.debug(f"Executing LLM request for schema generation: {gs_uri}")
            
            # Execute LLM request
            llm_response = await self._entity_extraction.execute_llm(llm_request)
            
            if llm_response.success and llm_response.content:
                logger.info(f"Successfully generated schema using LLM for app_id: {app_id}")
                return llm_response.content
            else:
                error_msg = llm_response.error_message or "Unknown LLM error"
                logger.error(f"LLM schema generation failed: {error_msg}")
                raise FileStorageError(f"Schema generation failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error generating schema with LLM: {str(e)}", exc_info=True)
            raise FileStorageError(f"Schema generation failed: {str(e)}") from e

    async def _generate_extraction_prompt_with_llm(
        self, 
        storage_metadata: StorageMetadata,
        meta_prompt: str,
        app_id: str
    ) -> str:
        """
        Generate a hardened production extraction prompt using LLM based on the uploaded document and meta prompt.
        
        Args:
            storage_metadata: Metadata about the uploaded file
            meta_prompt: User's description of what data to extract
            app_id: Application ID for context
            
        Returns:
            str: The generated production extraction prompt
        """
        logger.info(f"Generating extraction prompt using LLM for app_id: {app_id}")
        
        try:
            # Construct the GS URI from storage metadata
            storage_location = self._generate_storage_location(app_id)
            gs_uri = f"gs://{storage_location.bucket}/{storage_location.path}"
            
            # System instructions for the meta_prompt_collaborator
            system_instructions = """### Persona & Goal ###
You are the `meta_prompt_collaborator`, an expert AI assistant. Your primary goal is to collaboratively guide users in transforming their initial ideas into high-quality, complete LLM prompts or System Instructions, leveraging the principles outlined in the "Gemini Prompting Guide" (provided in full below). You aim to produce outputs that are precise, effective, and tailored to the user's objectives.

### Core Rules & Behavior ###
1.  **Output Clarification:** If the user provides an initial idea but does not specify whether they want a full "LLM Prompt" or "System Instructions," you MUST ask them to clarify their desired output format before proceeding with generation.
2.  **Explicit Generation:** Only generate a fully-formed System Instruction or LLM Prompt when the user explicitly requests it (e.g., "Okay, generate it now," "Show me the prompt," "Give me the system instructions").
3.  **Internal Review:** Before presenting any generated LLM Prompt or System Instructions to the user, internally review it for:
    *   Consistency with the user's stated goals and previous inputs.
    *   Adherence to the principles of the "Gemini Prompting Guide."
    *   Clarity, completeness, and absence of ambiguity.
    *   Resolve any identified issues. If resolution requires user input, proceed to the "Collaborative Engagement" rules.
4.  **Collaborative Engagement & Disambiguation:**
    *   If resolving an issue, disambiguating a request, or completing a prompt/System Instruction requires human decision-making or more information, you MUST engage the user.
    *   **When the User Needs to Make a Decision:**
        *   Clearly state the decision point or ambiguity.
        *   Suggest potential options. Use the `google_search` tool if research can provide more/better options or relevant examples.
        *   For each significant option, provide:
            *   A brief explanation.
            *   Potential pros and cons in the context of their goal.
            *   Examples, if applicable.
        *   Offer a recommendation based on your understanding of their goal and the "Gemini Prompting Guide."
    *   **When You Need More Feedback or Information:**
        *   Ask thoughtful, specific questions to clarify the user's intent.
        *   Suggest examples or ideas to help them articulate their needs.
        *   Offer to use the `google_search` tool to find relevant information or examples that might help them.
5.  **Iterative Refinement:** After presenting a generated prompt or System Instructions, or during the collaborative process, the user may want to make adjustments. Engage in this iterative process using the "Collaborative Engagement" methods described above.
6.  **Final Output Generation:**
    *   When the user requests the final generated output, provide the complete LLM Prompt or System Instructions based *solely* on the information gathered and agreed upon up to that point in the conversation.
    *   The generated output MUST be presented in its complete and final form, as if it were being generated for the first time based on the refined requirements.
    *   The language of the generation itself should be direct and definitive. Avoid phrases like "You could also add..." or "Here's a suggested modification..." within the generated prompt/instructions. Instead, incorporate agreed-upon elements directly.
    *   Every generated output must be self-contained and usable without needing additional context or conversational history from your interaction (though the user might have that history).

### Tone & Style ###
*   **Collaborative:** Act as a partner in the prompt design process.
*   **Expert & Guiding:** Demonstrate deep understanding of prompt engineering and the "Gemini Prompting Guide."
*   **Precise & Meticulous:** Pay close attention to detail.
*   **Helpful & Patient:** Be understanding and supportive throughout the user's design journey.
*   **Structured:** Present complex information (like options, pros/cons) in an organized manner (e.g., using bullet points).

For this specific request, I need you to generate a production-ready LLM prompt for data extraction. The prompt should be designed to extract structured data from documents similar to the one provided. 

CRITICAL: The prompt you generate must NOT include any JSON schemas, output format specifications, or structure examples. The system will handle output formatting separately through JSON schema constraints. Focus solely on extraction logic, data handling rules, and processing instructions. 

Generate the prompt now based on the document and extraction requirements."""
            
            # Prepare prompt for extraction prompt generation
            prompt = f"""Based on the provided document and the following extraction requirements, generate a complete, production-ready LLM prompt that can be used to extract structured data from similar documents.

Extraction Requirements: {meta_prompt}

The generated prompt should:
1. Be clear, specific, and unambiguous
2. Include appropriate context and instructions for accurate data extraction
3. Handle edge cases where fields might not be present
4. Include error handling instructions
5. Be robust enough for production use with similar document types

IMPORTANT: Do NOT include any JSON schema, output structure examples, or format specifications in the prompt. The output format will be handled separately by the system through a JSON schema constraint. Focus only on extraction instructions, data handling rules, and processing guidelines.

Generate the extraction prompt now. Return only the final prompt text that would be used in production, without additional commentary or explanations."""
            
            # Prepare metadata for the request
            request_metadata = {
                "business_unit": "viki",
                "solution_id": "viki-admin",
                "app_id": app_id,
                "operation": "prompt_generation"
            }
            
            # Get model parameters from config
            config = await self._config.get_config()
            model_parameters = config.get_model_parameters("prompt_generation")
            
            # Create JSON schema to ensure consistent response format
            extraction_prompt_schema = {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The complete production-ready LLM prompt for data extraction"
                    }
                },
                "required": ["prompt"],
                "additionalProperties": False
            }
            
            # Create LLM request
            llm_request = LlmExecuteRequest(
                gs_uri=gs_uri,
                system_instructions=system_instructions,
                prompt=prompt,
                json_schema=extraction_prompt_schema,  # Use schema to ensure correct response format
                metadata=request_metadata,
                model_parameters=model_parameters
            )
            
            logger.debug(f"Executing LLM request for prompt generation: {gs_uri}")
            logger.debug(f"JSON Schema for prompt generation: {extraction_prompt_schema}")
            logger.debug(f"LLM Request json_schema field: {llm_request.json_schema}")
            
            # Execute LLM request
            llm_response = await self._entity_extraction.execute_llm(llm_request)
            
            if llm_response.success and llm_response.content:
                logger.info(f"Successfully generated extraction prompt using LLM for app_id: {app_id}")
                # Extract the prompt from the JSON response using .get() method
                if isinstance(llm_response.content, dict):
                    extraction_prompt = llm_response.content.get("prompt", "")
                    if extraction_prompt:
                        return extraction_prompt
                    else:
                        logger.error(f"Empty prompt in response: {llm_response.content}")
                        raise FileStorageError("Prompt generation returned empty prompt")
                else:
                    logger.error(f"Unexpected response format from LLM: {llm_response.content}")
                    raise FileStorageError("Prompt generation returned unexpected format")
            else:
                error_msg = llm_response.error_message or "Unknown LLM error"
                logger.error(f"LLM prompt generation failed: {error_msg}")
                raise FileStorageError(f"Prompt generation failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error generating extraction prompt with LLM: {str(e)}", exc_info=True)
            raise FileStorageError(f"Prompt generation failed: {str(e)}") from e

    async def _perform_test_extraction_with_llm(
        self, 
        storage_metadata: StorageMetadata,
        entity_schema: Dict[str, Any],
        extraction_prompt: str,
        app_id: str
    ) -> Dict[str, Any]:
        """
        Perform test extraction using the generated schema and prompt on the test document.
        
        Args:
            storage_metadata: Metadata about the uploaded file
            entity_schema: The generated JSON schema for extraction
            extraction_prompt: The generated extraction prompt
            app_id: Application ID for context
            
        Returns:
            Dict containing the extracted entity data
        """
        logger.info(f"Performing test extraction using LLM for app_id: {app_id}")
        
        try:
            # Construct the GS URI from storage metadata
            storage_location = self._generate_storage_location(app_id)
            gs_uri = f"gs://{storage_location.bucket}/{storage_location.path}"
            
            # Use the generated extraction prompt directly as system instructions
            system_instructions = extraction_prompt
            
            # Simple prompt to trigger extraction
            prompt = "Please extract the data from this document according to the instructions."
            
            # Prepare metadata for the request
            request_metadata = {
                "business_unit": "viki",
                "solution_id": "viki-admin",
                "app_id": app_id,
                "operation": "test_extraction"
            }
            
            # Get model parameters from config
            config = await self._config.get_config()
            model_parameters = config.get_model_parameters("test_extraction")
            
            # Create LLM request with the entity schema as JSON schema constraint
            llm_request = LlmExecuteRequest(
                gs_uri=gs_uri,
                system_instructions=system_instructions,
                prompt=prompt,
                json_schema=entity_schema,  # Use the generated schema to constrain output
                metadata=request_metadata,
                model_parameters=model_parameters
            )
            
            logger.debug(f"Executing test extraction LLM request: {gs_uri}")
            
            # Execute LLM request
            llm_response = await self._entity_extraction.execute_llm(llm_request)
            
            if llm_response.success and llm_response.content:
                logger.info(f"Successfully performed test extraction for app_id: {app_id}")
                return llm_response.content
            else:
                error_msg = llm_response.error_message or "Unknown LLM error"
                logger.error(f"LLM test extraction failed: {error_msg}")
                # Return a failure indicator instead of raising an exception
                return {
                    "extraction_status": "failed",
                    "error_message": error_msg,
                    "extracted_data": None
                }
                
        except Exception as e:
            logger.error(f"Error performing test extraction with LLM: {str(e)}", exc_info=True)
            # Return a failure indicator instead of raising an exception
            return {
                "extraction_status": "failed", 
                "error_message": f"Test extraction failed: {str(e)}",
                "extracted_data": None
            }

    def _generate_storage_location(self, app_id: str) -> StorageLocation:
        """
        Generate the storage location for an onboarding file.
        
        The path format is: /onboarding/{app_id}/test_file/test_file.pdf
        The bucket format is: viki-admin-{environment}
        
        Args:
            app_id: The application ID
            
        Returns:
            StorageLocation: The generated storage location
        """
        # Generate bucket name based on environment
        bucket_name = f"viki-admin-{self._settings.STAGE}"
        
        # Generate file path
        file_path = f"onboarding/{app_id}/test_file/test_file.pdf"
        
        return StorageLocation(
            bucket=bucket_name,
            path=file_path
        )

    def _generate_original_storage_location(self, app_id: str, original_filename: str) -> StorageLocation:
        """
        Generate the storage location for the original file.
        
        The path format is: /onboarding/{app_id}/test_file/original/{original_filename}
        The bucket format is: viki-admin-{environment}
        
        Args:
            app_id: The application ID
            original_filename: The original filename to preserve
            
        Returns:
            StorageLocation: The generated storage location for the original file
        """
        # Generate bucket name based on environment
        bucket_name = f"viki-admin-{self._settings.STAGE}"
        
        # Generate file path for original file
        file_path = f"onboarding/{app_id}/test_file/original/{original_filename}"
        
        return StorageLocation(
            bucket=bucket_name,
            path=file_path
        )

    async def file_exists(self, app_id: str) -> bool:
        """
        Check if an onboarding file already exists for the given app_id.
        
        Args:
            app_id: The application ID
            
        Returns:
            bool: True if file exists, False otherwise
        """
        storage_location = self._generate_storage_location(app_id)
        return await self._file_storage.file_exists(storage_location)

    def get_storage_path(self, app_id: str) -> str:
        """
        Get the full storage path for an onboarding file.
        
        Args:
            app_id: The application ID
            
        Returns:
            str: The full storage path (bucket/path)
        """
        location = self._generate_storage_location(app_id)
        return f"{location.bucket}/{location.path}"