import os
from kink import inject

from paperglass.domain.values import OrchestrationPriority
from paperglass.domain.string_utils import to_int
from paperglass.domain.utils.token_utils import mktoken2
from paperglass.domain.utils.exception_utils import exceptionToMap

from paperglass.domain.models_common import EntityFilter

from paperglass.usecases.commands import (
    CreateDocument,
    GetDocumentLogs,
    LoadTestPoke
)

from paperglass.usecases.orchestrator_dummy import (
    orchestrate
)

from paperglass.infrastructure.ports import (
    IUnitOfWork
)

from paperglass.log import CustomLogger
LOGGER = CustomLogger(__name__)

class E2ELoadTestAgent():
    def __init__(self, create_document):
        self.create_document = create_document

    @inject
    async def run(self, command: LoadTestPoke, uow: IUnitOfWork):
        extra = command.toExtra()
        try:
            LOGGER.debug("Current working directory: %s", os.getcwd(), extra=extra)

            with open('./paperglass/tests/load/input/load-test-10page.pdf', 'rb') as f:
                app_id = command.app_id
                tenant_id = command.tenant_id
                patient_id = command.patient_id

                file_content = f.read()

                campaign_id = "nocampaign"
                iteration_key = "noid"
                if command.metadata:
                    if "campaign_id" in command.metadata:
                        campaign_id = command.metadata["campaign_id"]
                    if "iteration_key" in command.metadata:
                        iteration_key = command.metadata["iteration_key"]

                target_filename = f"load_test_{campaign_id}_{iteration_key}.pdf"
                LOGGER.debug(target_filename, extra=extra)

                command = CreateDocument(
                    app_id=app_id,
                    tenant_id=tenant_id,
                    patient_id=patient_id, #dev: Test Automation patient
                    file_name=target_filename,
                    file=file_content,
                    token=mktoken2(app_id, tenant_id, patient_id),
                    metadata=command.metadata
                )

                LOGGER.debug("CreateDocument command for filename: %s", target_filename, extra=extra)

                await self.create_document(command, uow)

        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error("Error in load test poke: %s", str(e), extra=extra)
            raise e
        
class VertexAILoadTestAgent():
    def __init__(self, get_document_logs):
        self.get_document_logs = get_document_logs
    
    @inject
    async def run(self, command: LoadTestPoke, uow: IUnitOfWork):
        extra = command.toExtra()
        
        await orchestrate(command.document_id, 
                    force_new_instance = False, 
                    priority = OrchestrationPriority.DEFAULT)