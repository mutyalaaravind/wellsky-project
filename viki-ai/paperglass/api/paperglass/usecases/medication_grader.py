from typing import List
from kink import inject
import json

from paperglass.domain.time import now_utc
from paperglass.domain.utils.array_utils import chunk_array
from paperglass.domain.util_json import DateTimeEncoder, convertToJson
from paperglass.domain.utils.array_utils import chunk_array
from paperglass.domain.models import (
    ExtractedMedication, 
    ExtractedMedicationGrade, 
    ResolvedReconcilledMedication, 
    DocumentOperationDefinition,
    DocumentOperationInstanceLog, 
    DocumentOperationStatus,
    DocumentOperationType,
    MedispanStatus,
    Score,
    OperationMeta,
)
from paperglass.domain.models_common import (
    OrchestrationException,
)
from paperglass.domain.values import (
    DocumentOperationStep,
    StepConfigPrompt,    
)
from paperglass.usecases.commands import (
    PerformGrading,
)
from paperglass.infrastructure.ports import (
    IUnitOfWork,
    IQueryPort,
    IPromptAdapter,
)

from paperglass.log import CustomLogger
LOGGER = CustomLogger(__name__)

#OpenTelemetry instrumentation
SPAN_BASE: str = "APP:medication-grader:"
from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils
opentelemetry = OpenTelemetryUtils(SPAN_BASE)


class MedicationGrader():
    def __init__(self, doc_op_def: DocumentOperationDefinition, uow: IUnitOfWork, query: IQueryPort, prompt: IPromptAdapter):   
        pass

    async def process(self, command: PerformGrading, doc_op_def: DocumentOperationDefinition) -> List[ExtractedMedication]:
        raise NotImplementedError


class MedicationGraderLLM(MedicationGrader):
    def __init__(self, doc_op_def: DocumentOperationDefinition, uow: IUnitOfWork, query: IQueryPort, prompt: IPromptAdapter):
        self.strategy = "procedural"
        self.doc_op_def = doc_op_def
        self.uow = uow
        self.query = query
        self.prompt = prompt

    @inject()
    async def process(self, command: PerformGrading) -> List[ExtractedMedication]:
        start_datetime = now_utc()
        LOGGER.debug("PerformGrading: Starting grading using %s strategy for document %s", self.strategy, command.document_id)
        with await opentelemetry.getSpan("perform_grading") as span:
            extra = {
                "app_id": command.app_id,
                "tenant_id": command.tenant_id,
                "patient_id": command.patient_id,
                "document_id": command.document_id,
                "document_operation_instance_id": command.document_operation_instance_id,
                "operation_type": DocumentOperationType.MEDICATION_GRADER.value,
                "medication_grader_strategy": self.strategy,
            }
            try:

                opMeta:OperationMeta = OperationMeta(
                    type=DocumentOperationType.MEDICATION_GRADER.value,
                    step = DocumentOperationStep.EXTRACTED_MEDICATION_GRADER,
                    document_id=command.document_id,
                    document_operation_instance_id=command.document_operation_instance_id,
                )

                from paperglass.settings import ORCHESTRATION_GRADER_PERFORMGRADING_CHUNK_SIZE

                start_time = now_utc()

                grades = []

                operation_context = {
                    "medication_grader": "LLM"
                }

                step_config: StepConfigPrompt = self.doc_op_def.get_step_config(DocumentOperationStep.EXTRACTED_MEDICATION_GRADER)

                LOGGER.info("Orchestration grader start", extra=extra)
                            
                # Retrieve medication profile patient/doc
                from paperglass.usecases.medications import get_medication_profile_by_documents,get_resolved_reconcilled_medications, get_resolved_reconcilled_medications_v3
                ret: List[ResolvedReconcilledMedication] = await get_resolved_reconcilled_medications_v3(command.document_id, command.patient_id, command.app_id, command.tenant_id, self.query)

                LOGGER.debug("PerformGrading: Resolved medications for document %s: %s", command.document_id, json.dumps([x.dict() for x in ret], indent=2, cls=DateTimeEncoder))

                # Filter medications for the target document
                filtered_medications = [
                    med for med in ret
                    if any(ex_med_ref.document_id == command.document_id for ex_med_ref in med.extracted_medication_reference)
                ]
                LOGGER.debug("PerformGrading: Filtered medications for document %s: %s", command.document_id, json.dumps([x.dict() for x in filtered_medications], indent=2, cls=DateTimeEncoder))

                extracted_medications = []
                for med in filtered_medications:
                    for ex_med_ref in med.extracted_medication_reference:
                        extracted_medication_id = ex_med_ref.extracted_medication_id                            
                        extracted_medication:ExtractedMedication = await self.query.get_extracted_medication(extracted_medication_id)                    
                        extracted_medications.append(extracted_medication)
                LOGGER.debug("PerformGrading: Extracted medications for document %s: %s", command.document_id, json.dumps([x.dict() for x in extracted_medications], indent=2, cls=DateTimeEncoder))

                extra["extractedMedicationsCount"] = len(extracted_medications)

                super_list = chunk_array(extracted_medications, ORCHESTRATION_GRADER_PERFORMGRADING_CHUNK_SIZE)
                super_grades = []
                ctr = 0
                for sub_extracted_medications in super_list:
                    LOGGER.debug("PerformGrading: Processing chunk %s of %s", ctr, len(super_list))

                    opMeta.iteration = ctr

                    # Call LLM to grade the extracted medications
                    #data_str = json.dumps([x.dict() for x in filtered_medications], indent=2, cls=DateTimeEncoder)
                    data_str = json.dumps([x.dict() for x in sub_extracted_medications], indent=2, cls=DateTimeEncoder)
                    prompt_text = step_config.prompt.replace("{{data}}", data_str)
                    LOGGER.debug("PerformGrading: Prompt text for model %s: %s", step_config.model, prompt_text)

                    LOGGER.debug("PerformGrading: Calling multi modal predict to grade extracted medications for document %s", command.document_id)
                    llm_results_raw = await self.prompt.multi_modal_predict_2([prompt_text], model=step_config.model, metadata = opMeta.dict())
                    
                    LOGGER.debug("LLM raw results for grading extracted medications: %s", "***" + llm_results_raw + "***")
                    llm_results = convertToJson(llm_results_raw)                
                    LOGGER.debug("LLM results for grading extracted medications: %s", json.dumps(llm_results, indent=2))

                    # Cast to ExtractedMedicationGrade
                    grades = [ExtractedMedicationGrade.create(**x) for x in llm_results]
                    super_grades.extend(grades)
                    LOGGER.debug("Grades for extracted medications: %s", json.dumps([x.dict() for x in grades], indent=2, cls=DateTimeEncoder))

                    elapsed_time = now_utc() - start_time                

                    # Retrieve the current score
                    avg_sum = 0
                    avg_cnt = 0
                    for grade in grades:
                        grade.medication_extraction_document_operation_instance_id = grade.document_operation_instance_id
                        grade.document_operation_instance_id = command.document_operation_instance_id
                        extra = {
                            "app_id": command.app_id,
                            "tenant_id": command.tenant_id,
                            "patient_id": command.patient_id,
                            "document_id": command.document_id,
                            "medispan_id": grade.medispan_id,                        
                            "medication_name": grade.medication.name,
                            "score": grade.score,
                            "medication_grader_strategy": self.strategy                     
                        }
                        LOGGER.info("Medication grade medication score", extra=extra)
                        self.uow.register_new(grade)
                        avg_sum += grade.score.overall
                        avg_cnt += 1

                    for extracted_med in sub_extracted_medications:
                        if extracted_med.medispan_status == MedispanStatus.MATCHED:
                            extra = {                            
                                "app_id": command.app_id,
                                "tenant_id": command.tenant_id,
                                "patient_id": command.patient_id,
                                "document_id": command.document_id,                            
                                "medication_name": extracted_med.medication.name,
                                "medispan_status": extracted_med.medispan_status,
                                "medispan_id": extracted_med.medispan_id                            
                            }
                            LOGGER.info("Medication matched to Medispan", extra=extra)
                        else:
                            extra = {                            
                                "app_id": command.app_id,
                                "tenant_id": command.tenant_id,
                                "patient_id": command.patient_id,
                                "document_id": command.document_id,
                                "medication_name": extracted_med.medication.name,
                                "medispan_status": extracted_med.medispan_status,
                            }
                            LOGGER.info("Medication not matched to Medispan", extra=extra)

                    ctr += 1

                extra["elapsed_time"] = elapsed_time
                extra["medication_avg_score"] = avg_sum / avg_cnt if avg_cnt > 0 else 0
                LOGGER.info("Grading complete for document", extra=extra)

                operation_context["prompt"] = step_config.prompt
                operation_context["model"] = step_config.model
                operation_context["extracted_medications"] = json.loads(json.dumps([x.dict() for x in sub_extracted_medications], indent=2, cls=DateTimeEncoder))
                operation_context["results"] = super_grades
                
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                    tenant_id=command.tenant_id,
                                                                                    patient_id=command.patient_id,
                                                                                    document_operation_instance_id=command.document_operation_instance_id,
                                                                                    document_operation_definition_id=self.doc_op_def.id,
                                                                                    document_id=command.document_id,
                                                                                    step_id= DocumentOperationStep.EXTRACTED_MEDICATION_GRADER,
                                                                                    start_datetime=start_datetime,
                                                                                    context=operation_context,
                                                                                    status = DocumentOperationStatus.COMPLETED)
                self.uow.register_new(doc_operation_instance_log)

                return super_grades            

            except Exception as e:
                msg = f"Exception performing grading on document {command.document_id}: {str(e)}"
                LOGGER.debug(msg)

                elapsed_time = now_utc() - start_time
                extra["elapsed_time"] = elapsed_time.total_seconds()
                extra["error"] = str(e)
                LOGGER.error("Grading failed for document", extra=extra)

                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                    tenant_id=command.tenant_id,
                                                                                    patient_id=command.patient_id,
                                                                                    document_operation_instance_id=command.document_operation_instance_id,
                                                                                    document_operation_definition_id=self.doc_op_def.id,
                                                                                    document_id=command.document_id,
                                                                                    step_id= DocumentOperationStep.EXTRACTED_MEDICATION_GRADER,
                                                                                    start_datetime=start_datetime,
                                                                                    context=operation_context,
                                                                                    status = DocumentOperationStatus.FAILED)
                self.uow.register_new(doc_operation_instance_log)

                raise OrchestrationException(msg)


class MedicationGraderProcedural(MedicationGrader):
    def __init__(self, doc_op_def: DocumentOperationDefinition, uow: IUnitOfWork, query: IQueryPort, prompt: IPromptAdapter):
        self.strategy = "procedural"
        self.doc_op_def = doc_op_def
        self.uow = uow
        self.query = query
        self.prompt = prompt

    @inject()
    async def process(self, command: PerformGrading) -> List[ExtractedMedication]:
        start_datetime = now_utc()
        LOGGER.debug("PerformGrading: Starting grading using %s strategy for document %s", self.strategy, command.document_id)
        with await opentelemetry.getSpan("perform_grading") as span:
            extra = {
                "app_id": command.app_id,
                "tenant_id": command.tenant_id,
                "patient_id": command.patient_id,
                "document_id": command.document_id,
                "document_operation_instance_id": command.document_operation_instance_id,
                "operation_type": DocumentOperationType.MEDICATION_GRADER.value,
                "medication_grader_strategy": self.strategy,
            }
            try:

                from paperglass.settings import ORCHESTRATION_GRADER_PERFORMGRADING_CHUNK_SIZE

                start_time = now_utc()

                operation_context = {
                    "medication_grader": "procedural"
                }                

                step_config: StepConfigPrompt = self.doc_op_def.get_step_config(DocumentOperationStep.EXTRACTED_MEDICATION_GRADER)

                LOGGER.info("Orchestration grader start", extra=extra)
                            
                # Retrieve medication profile patient/doc
                from paperglass.usecases.medications import get_medication_profile_by_documents,get_resolved_reconcilled_medications, get_resolved_reconcilled_medications_v3
                ret: List[ResolvedReconcilledMedication] = await get_resolved_reconcilled_medications_v3(command.document_id, command.patient_id, command.app_id, command.tenant_id, self.query)

                LOGGER.debug("PerformGrading: Resolved medications for document %s: %s", command.document_id, json.dumps([x.dict() for x in ret], indent=2, cls=DateTimeEncoder))

                # Filter medications for the target document
                LOGGER.debug("PerformGrading: Filtering medications for document %s", command.document_id)
                filtered_medications = [
                    med for med in ret
                    if any(ex_med_ref.document_id == command.document_id for ex_med_ref in med.extracted_medication_reference)
                ]
                LOGGER.debug("PerformGrading: Filtered medications for document %s: %s", command.document_id, json.dumps([x.dict() for x in filtered_medications], indent=2, cls=DateTimeEncoder))

                extracted_medications: List[ExtractedMedication] = []
                for med in filtered_medications:
                    for ex_med_ref in med.extracted_medication_reference:
                        extracted_medication_id = ex_med_ref.extracted_medication_id                            
                        extracted_medication:ExtractedMedication = await self.query.get_extracted_medication(extracted_medication_id)                    
                        extracted_medications.append(extracted_medication)
                LOGGER.debug("PerformGrading: Extracted medications for document %s: %s", command.document_id, json.dumps([x.dict() for x in extracted_medications], indent=2, cls=DateTimeEncoder))

                extra["extractedMedicationsCount"] = len(extracted_medications)

                grades = []
                avg_sum = 0
                avg_cnt = 0
                for extracted_medication in extracted_medications:
                    grade: ExtractedMedicationGrade = await self.grade(command, extracted_medication)

                    grade.medication_extraction_document_operation_instance_id = grade.document_operation_instance_id
                    grade.document_operation_instance_id = command.document_operation_instance_id
                    extra = {
                        "app_id": command.app_id,
                        "tenant_id": command.tenant_id,
                        "patient_id": command.patient_id,
                        "document_id": command.document_id,
                        "medispan_id": grade.medispan_id,                        
                        "medication_name": grade.medication.name,
                        "score": grade.score.overall,               
                        "medication_grader_strategy": self.strategy
                    }
                    LOGGER.info("Medication grade medication score", extra=extra)
                    self.uow.register_new(grade)
                    avg_sum += grade.score.overall
                    avg_cnt += 1

                    # Assess and emit metric for Medispan matching
                    if extracted_medication.medispan_status == MedispanStatus.MATCHED:
                        extra = {                            
                            "app_id": command.app_id,
                            "tenant_id": command.tenant_id,
                            "patient_id": command.patient_id,
                            "document_id": command.document_id,                            
                            "medication_name": extracted_medication.medication.name,
                            "medispan_status": extracted_medication.medispan_status,
                            "medispan_id": extracted_medication.medispan_id                            
                        }
                        LOGGER.info("Medication matched to Medispan", extra=extra)
                    else:
                        extra = {                            
                            "app_id": command.app_id,
                            "tenant_id": command.tenant_id,
                            "patient_id": command.patient_id,
                            "document_id": command.document_id,
                            "medication_name": extracted_medication.medication.name,
                            "medispan_status": extracted_medication.medispan_status,
                        }
                        LOGGER.info("Medication not matched to Medispan", extra=extra)

                    grades.append(grade)

                elapsed_time = now_utc() - start_time

                extra["elapsed_time"] = elapsed_time.total_seconds()
                extra["medication_avg_score"] = avg_sum / avg_cnt if avg_cnt > 0 else 0
                LOGGER.info("Grading complete for document", extra=extra)

                operation_context["extracted_medications"] = json.loads(json.dumps([x.dict() for x in extracted_medications], indent=2, cls=DateTimeEncoder))
                operation_context["results"] = grades
                
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                    tenant_id=command.tenant_id,
                                                                                    patient_id=command.patient_id,
                                                                                    document_operation_instance_id=command.document_operation_instance_id,
                                                                                    document_operation_definition_id=self.doc_op_def.id,
                                                                                    document_id=command.document_id,
                                                                                    step_id= DocumentOperationStep.EXTRACTED_MEDICATION_GRADER,
                                                                                    start_datetime=start_datetime,
                                                                                    context=operation_context,
                                                                                    status = DocumentOperationStatus.COMPLETED)
                self.uow.register_new(doc_operation_instance_log)



                return grades

            except Exception as e:
                msg = f"Exception performing grading on document {command.document_id}: {str(e)}"
                LOGGER.debug(msg)

                elapsed_time = now_utc() - start_time
                extra["elapsed_time"] = elapsed_time.total_seconds()
                extra["error"] = str(e)
                LOGGER.error("Grading failed for document", extra=extra)

                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                    tenant_id=command.tenant_id,
                                                                                    patient_id=command.patient_id,
                                                                                    document_operation_instance_id=command.document_operation_instance_id,
                                                                                    document_operation_definition_id=self.doc_op_def.id,
                                                                                    document_id=command.document_id,
                                                                                    step_id= DocumentOperationStep.EXTRACTED_MEDICATION_GRADER,
                                                                                    start_datetime=start_datetime,
                                                                                    context=operation_context,
                                                                                    status = DocumentOperationStatus.FAILED)
                self.uow.register_new(doc_operation_instance_log)

                raise OrchestrationException(msg)
            
    async def grade(self, command: PerformGrading, extracted_medication: ExtractedMedication) -> ExtractedMedicationGrade:        

        s = 1.0
        fields_with_issues = []

        if not extracted_medication.medication.name:
            s =- 0.5
            fields_with_issues.append("name")

        if not extracted_medication.medication.strength:
            s =- 0.5
            fields_with_issues.append("strength")
        
        if not extracted_medication.medication.form:
            s =- 0.25
            fields_with_issues.append("form")

        if not extracted_medication.medication.route:
            s =- 0.25
            fields_with_issues.append("route")
        
        if not extracted_medication.medication.frequency:
            s =- 0.25
            fields_with_issues.append("frequency")

        if not extracted_medication.medication.dosage:
            s =- 0.25
            fields_with_issues.append("dosage")

        if s < 0:
            s = 0

        score = Score(overall=s, details={})
        
        grade = ExtractedMedicationGrade.create(
            app_id=command.app_id,
            tenant_id=command.tenant_id,
            patient_id=command.patient_id,
            document_id=command.document_id,
            document_operation_instance_id=command.document_operation_instance_id,
            page_number=extracted_medication.page_number,
            extracted_medication_id=extracted_medication.id,
            medication=extracted_medication.medication,
            medispan_id=extracted_medication.medispan_id,
            score=score,
            fields_with_issues=fields_with_issues,
        )
        return grade