# from logging import getLogger
# from typing import List
# from paperglass.domain.models_common import OrchestrationExceptionWithContext
# from paperglass.domain.utils.exception_utils import exceptionToMap
# from paperglass.infrastructure.ports import IUnitOfWorkManagerPort
# from paperglass.domain.time import now_utc
# from paperglass.domain.values import DocumentOperationStatus
# from paperglass.domain.models import DocumentOperationInstanceLog, ExtractedMedication
# from paperglass.usecases.command_handling import medispan_matching
# from paperglass.usecases.commands import MedispanMatching
# from paperglass.interface.ports import ICommandHandlingPort, IMedispanMatchCommandHandlingPort
# from kink import inject

# LOGGER = getLogger(__name__)

# class MedispanCommandHandlingUseCase(IMedispanMatchCommandHandlingPort):
    
#     @inject()
#     async def handle_command(self, command: MedispanMatching, uowm: IUnitOfWorkManagerPort):
#         operation_context = {}
#         try:
#             start_datetime = now_utc()
#             extracted_medications,operation_context = await medispan_matching(command, uowm)
#             extracted_medications:List[ExtractedMedication] = extracted_medications
#             async with uowm.start() as uow:
#                 for medication in extracted_medications:
#                     uow.register_dirty(medication)
                
#                 doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
#                                                                             tenant_id=command.tenant_id,
#                                                                             patient_id=command.patient_id,
#                                                                             document_operation_instance_id=command.document_operation_instance_id,
#                                                                             document_operation_definition_id=command.document_operation_definition_id,
#                                                                             document_id=command.document_id,
#                                                                             step_id= command.step_id,
#                                                                             start_datetime=start_datetime,
#                                                                             context=operation_context,
#                                                                             page_number=command.page_number,
#                                                                             status = DocumentOperationStatus.COMPLETED)
#                 uow.register_new(doc_operation_instance_log)
#                 return extracted_medications
#         except Exception as e:  
#             try:
#                 LOGGER.error('MedispanMatching: Error in extracting medications from documentId %s: %s', command.document_id, str(e))
#                 operation_context["page_number"] = str(command.page_id)
#                 operation_context['error'] = exceptionToMap(e)
#             except Exception as e1:
#                 LOGGER.error('Exception in medispan matching error block',str(e1))
#             raise OrchestrationExceptionWithContext(f"MedispanMatching: Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}",context=operation_context) from e
