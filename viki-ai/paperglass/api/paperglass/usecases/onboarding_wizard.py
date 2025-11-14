import json
from logging import getLogger
from datetime import datetime
from typing import Dict, Any

from kink import inject

from paperglass.domain.time import now_utc
from paperglass.domain.utils.token_utils import mktoken2
from paperglass.domain.utils.exception_utils import exceptionToMap
from paperglass.domain.values import OrchestrationPriority
from paperglass.usecases.commands import ProcessOnboardingWizard, CreateEntitySchema
from paperglass.interface.ports import CommandError, ICommandHandlingPort
from paperglass.infrastructure.ports import IStoragePort, IUnitOfWork, ICloudTaskPort
from paperglass.log import CustomLogger

LOGGER = getLogger(__name__)
LOGGER2 = CustomLogger(__name__)


class OnboardingWizardService:
    """Service for handling onboarding wizard operations."""
    
    @inject
    def __init__(self, storage: IStoragePort, cloud_task: ICloudTaskPort, commands: ICommandHandlingPort):
        self.storage = storage
        self.cloud_task = cloud_task
        self.commands = commands
    
    async def process_onboarding_wizard(self, command: ProcessOnboardingWizard, uow: IUnitOfWork) -> Dict[str, Any]:
        """
        Process the onboarding wizard request.
        
        1. Creates a document in paperglass app_id "onboard" with tenant_id as the app_id 
           and patient_id "onboarding_wizard"
        2. Invokes a pipeline with scope "onboard" and pipeline "onboarding_wizard"
        
        Args:
            command: ProcessOnboardingWizard command containing the request data
            uow: Unit of work for database operations
            
        Returns:
            Dict containing the result of the operation
        """
        from paperglass.usecases.documents import create_document
        
        extra = command.toExtra()
        
        try:
            LOGGER.info("Processing onboarding wizard for app_id: %s, entity: %s", 
                       command.app_id, command.entity_name, extra=extra)
            
            # Step 1: Create document in paperglass app_id "onboard" 
            # with tenant_id as the app_id and patient_id "onboarding_wizard"
            onboard_app_id = "onboard"
            onboard_tenant_id = command.app_id
            onboard_patient_id = "onboarding_wizard"
            
            # Generate token for the onboard context
            token = mktoken2(onboard_app_id, onboard_tenant_id, onboard_patient_id)
            
            # Create filename based on entity name
            filename = f"onboarding_wizard_{command.entity_name}_{now_utc().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Create metadata for the document
            metadata = {
                "onboarding_wizard": {
                    "business_unit": command.business_unit,
                    "solution_id": command.solution_id,
                    "original_app_id": command.app_id,
                    "entity_name": command.entity_name,
                    "entity_data_description": command.entity_data_description,
                    "extraction_prompt": command.extraction_prompt,
                    "peak_docs_per_minute": command.peak_docs_per_minute,
                    "processing_time_sla_max": command.processing_time_sla_max,
                }
            }
            
            # Create the document
            document = await create_document(
                app_id=onboard_app_id,
                tenant_id=onboard_tenant_id,
                patient_id=onboard_patient_id,
                file_name=filename,
                uploaded_bytes=command.pdf_file,
                token=token,
                priority=OrchestrationPriority.DEFAULT,
                storage=self.storage,
                metadata=metadata
            )
            
            # Register the document for persistence
            uow.register_new(document)
            
            LOGGER.info("Created document %s for onboarding wizard", document.id, extra=extra)
            
            # Step 2: Create entity schema for the onboarding entity
            entity_schema_id = await self._create_entity_schema(command, extra)
            
            # Step 3: Invoke pipeline with scope "onboard" and pipeline "onboarding_wizard"
            # pipeline_execution_id = await self._invoke_onboarding_pipeline(
            #     command, document, onboard_app_id, onboard_tenant_id, 
            #     onboard_patient_id, token, metadata, extra
            # )
            
            result = {
                "success": True,
                "document_id": document.id,
                "entity_schema_id": entity_schema_id,
                "onboard_app_id": onboard_app_id,
                "onboard_tenant_id": onboard_tenant_id,
                "onboard_patient_id": onboard_patient_id
            }
            
            LOGGER.info("Successfully processed onboarding wizard", extra=extra)
            
            return result
            
        except Exception as e:
            error_message = str(e) if str(e) else f"Unknown error of type {type(e).__name__}"
            extra["error"] = exceptionToMap(e)
            LOGGER.error("Error processing onboarding wizard: %s", error_message, extra=extra)
            raise CommandError(f"Failed to process onboarding wizard: {error_message}") from e
    
    async def _invoke_onboarding_pipeline(self, command: ProcessOnboardingWizard, document, 
                                        onboard_app_id: str, onboard_tenant_id: str, 
                                        onboard_patient_id: str, token: str, 
                                        metadata: Dict[str, Any], extra: Dict[str, Any]) -> str:
        """
        Invoke the onboarding wizard pipeline.
        
        Args:
            command: The original command
            document: The created document
            onboard_app_id: App ID for onboard context
            onboard_tenant_id: Tenant ID for onboard context  
            onboard_patient_id: Patient ID for onboard context
            token: Authentication token
            metadata: Document metadata
            extra: Extra logging context
            
        Returns:
            Pipeline execution ID if successful, None if failed
        """
        try:
            # Prepare the payload for pipeline invocation
            pipeline_payload = {
                "business_unit": command.business_unit,
                "solution_id": command.solution_id,
                "app_id": onboard_app_id,
                "tenant_id": onboard_tenant_id,
                "patient_id": onboard_patient_id,
                "document_id": document.id,
                "page_count": document.page_count,
                "priority": OrchestrationPriority.DEFAULT.value,
                "params": {
                    "config": {
                        "entity_name": command.entity_name,
                        "entity_data_description": command.entity_data_description,
                        "extraction_prompt": command.extraction_prompt,
                        "peak_docs_per_minute": command.peak_docs_per_minute,
                        "processing_time_sla_max": command.processing_time_sla_max,
                    }
                },
                "context": metadata
            }
            
            # Import settings for pipeline invocation
            from paperglass.settings import (
                ENTITY_EXTRACTION_API_URL,
                ENTITY_EXTRACTION_LAUNCH_QUEUE_NAME,
                GCP_LOCATION_2,
                SERVICE_ACCOUNT_EMAIL
            )
            
            # Construct the pipeline URL
            url = f"{ENTITY_EXTRACTION_API_URL}/api/pipeline/onboard/onboarding_wizard/start"
            queue = ENTITY_EXTRACTION_LAUNCH_QUEUE_NAME
            
            # Invoke the pipeline via cloud task
            await self.cloud_task.create_task(
                token=token,
                location=GCP_LOCATION_2,
                service_account_email=SERVICE_ACCOUNT_EMAIL,
                queue=queue,
                url=url,
                payload=pipeline_payload
            )
            
            pipeline_execution_id = f"onboard_onboarding_wizard_{document.id}"
            
            LOGGER.info("Successfully invoked onboarding_wizard pipeline for document %s", 
                       document.id, extra=extra)
            
            return pipeline_execution_id
                
        except Exception as e:
            LOGGER.error("Failed to invoke pipeline for onboarding wizard: %s", str(e), extra=extra)
            # Don't fail the entire operation if pipeline invocation fails
            return None

