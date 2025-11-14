"""
Onboard Generation Application Service

This module contains the application layer service for onboarding generation,
including file upload, JSON schema generation, and test extraction
following hexagonal architecture principles.
"""

import io
import json
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
from contracts.config_contracts import ConfigPort
from models.onboard_models import OnboardGenerationResult, StorageMetadataModel
from settings import Settings

logger = getLogger(__name__)


class OnboardGenerationService:
    """
    Application service for onboarding generation operations.
    
    This service handles the complete onboarding generation workflow:
    1. Upload files to cloud storage
    2. Generate JSON schema based on meta prompt
    3. Perform test extraction (future implementation)
    """

    def __init__(self, file_storage: FileStoragePort, entity_extraction: EntityExtractionPort, config: ConfigPort, settings: Settings):
        """
        Initialize the generation service.
        
        Args:
            file_storage: File storage port implementation
            entity_extraction: Entity extraction service port implementation
            config: Config port implementation for retrieving LLM configurations
            settings: Application settings for bucket configuration
        """
        self._file_storage = file_storage
        self._entity_extraction = entity_extraction
        self._config = config
        self._settings = settings
        self._pdf_converter = PDFConverter(quality=95, optimize=True)
        logger.info("Onboard Generation Service initialized")

    async def generate_onboard_config(
        self,
        app_id: str,
        file_content: BinaryIO,
        content_type: str,
        original_filename: str,
        meta_prompt: str
    ) -> OnboardGenerationResult:
        """
        Execute the complete onboard generation workflow.
        
        Args:
            app_id: The application ID for path generation
            file_content: The file content as a binary stream
            content_type: MIME type of the file
            original_filename: Original name of the uploaded file
            meta_prompt: User's description of data to extract
            
        Returns:
            OnboardGenerationResult: Generation results including storage metadata and schema
            
        Raises:
            FileStorageError: If upload fails
        """
        logger.info(f"Starting onboard generation for app_id: {app_id}")
        
        try:
            # Step 1: Upload file to storage
            storage_metadata = await self._upload_file(
                app_id=app_id,
                file_content=file_content,
                content_type=content_type,
                original_filename=original_filename
            )
            
            # Step 2: Generate JSON schema from meta prompt using LLM
            entity_schema = await self._generate_entity_schema_with_llm(
                storage_metadata=storage_metadata,
                meta_prompt=meta_prompt,
                app_id=app_id
            )
            
            # Step 3: Generate hardened production extraction prompt
            extraction_prompt = await self._generate_extraction_prompt_with_llm(
                storage_metadata=storage_metadata,
                meta_prompt=meta_prompt,
                app_id=app_id
            )
            
            # Step 4: Perform test extraction using generated schema and prompt
            test_extraction_result = await self._perform_test_extraction_with_llm(
                storage_metadata=storage_metadata,
                entity_schema=entity_schema,
                extraction_prompt=extraction_prompt,
                app_id=app_id
            )
            
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
            
            logger.info(f"Completed onboard generation for app_id: {app_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed onboard generation for app_id: {app_id}", exc_info=True)
            raise FileStorageError(f"Generation failed: {str(e)}") from e

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

    def _generate_entity_schema(self, meta_prompt: str) -> Dict[str, Any]:
        """
        Generate entity schema based on meta prompt.
        
        This method analyzes the meta prompt and generates a JSON schema
        for the expected extracted data structure.
        
        Args:
            meta_prompt: User's description of what data to extract
            
        Returns:
            Dict representing the JSON schema
        """
        logger.info("Generating entity schema from meta prompt")
        
        # Base schema structure
        base_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Analyze meta prompt for common patterns
        meta_lower = meta_prompt.lower()
        
        # Insurance-related fields
        if "insurance" in meta_lower:
            base_schema["properties"].update({
                "insured_name": {
                    "type": "string",
                    "description": "Full name of the insured person"
                },
                "policy_number": {
                    "type": "string",
                    "description": "Insurance policy number"
                },
                "group_number": {
                    "type": "string",
                    "description": "Insurance group number"
                }
            })
            base_schema["required"].extend(["insured_name", "policy_number"])
        
        # Dependent information
        if "dependent" in meta_lower:
            base_schema["properties"]["dependents"] = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "relationship": {"type": "string"},
                        "date_of_birth": {"type": "string", "format": "date"}
                    }
                },
                "description": "List of dependents covered by the policy"
            }
        
        # Patient-related fields
        if "patient" in meta_lower:
            base_schema["properties"].update({
                "patient_name": {
                    "type": "string",
                    "description": "Full name of the patient"
                },
                "date_of_birth": {
                    "type": "string",
                    "format": "date",
                    "description": "Patient's date of birth"
                }
            })
            base_schema["required"].extend(["patient_name", "date_of_birth"])
        
        # Medication information
        if "medication" in meta_lower:
            base_schema["properties"]["medications"] = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "dosage": {"type": "string"},
                        "frequency": {"type": "string"}
                    }
                },
                "description": "List of prescribed medications"
            }
        
        # If no specific patterns found, use a generic schema
        if not base_schema["properties"]:
            base_schema["properties"] = {
                "extracted_data": {
                    "type": "object",
                    "description": "Extracted data from the document"
                }
            }
            base_schema["required"] = ["extracted_data"]
        
        logger.info(f"Generated schema with {len(base_schema['properties'])} properties")
        return base_schema

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
                "Use proper JSON syntax with double quotes for all strings and property names."
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
                "7. Ensure all braces and brackets are properly closed\n\n"
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

For this specific request, I need you to generate a production-ready LLM prompt for data extraction. The prompt should be designed to extract structured data from documents similar to the one provided. Generate the prompt now based on the document and extraction requirements."""
            
            # Prepare prompt for extraction prompt generation
            prompt = f"""Based on the provided document and the following extraction requirements, generate a complete, production-ready LLM prompt that can be used to extract structured data from similar documents.

Extraction Requirements: {meta_prompt}

The generated prompt should:
1. Be clear, specific, and unambiguous
2. Include appropriate context and instructions for accurate data extraction
3. Handle edge cases where fields might not be present
4. Provide guidance on output format and structure
5. Include error handling instructions
6. Be robust enough for production use with similar document types

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
            
            # Create LLM request
            llm_request = LlmExecuteRequest(
                gs_uri=gs_uri,
                system_instructions=system_instructions,
                prompt=prompt,
                json_schema=None,  # No schema constraint for prompt generation
                metadata=request_metadata,
                model_parameters=model_parameters
            )
            
            logger.debug(f"Executing LLM request for prompt generation: {gs_uri}")
            
            # Execute LLM request
            llm_response = await self._entity_extraction.execute_llm(llm_request)
            
            if llm_response.success and llm_response.raw_response:
                logger.info(f"Successfully generated extraction prompt using LLM for app_id: {app_id}")
                # Parse the JSON response and extract the prompt value
                try:
                    prompt_data = json.loads(llm_response.raw_response.strip())
                    if "prompt" in prompt_data:
                        return prompt_data["prompt"]
                    else:
                        logger.error(f"LLM response missing 'prompt' key: {llm_response.raw_response}")
                        raise FileStorageError("LLM response missing 'prompt' key")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse LLM JSON response: {e}")
                    raise FileStorageError(f"Failed to parse LLM response: {e}")
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