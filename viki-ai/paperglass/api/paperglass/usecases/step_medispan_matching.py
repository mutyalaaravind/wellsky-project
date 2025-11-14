import json
from typing import List
import traceback
from kink import inject

from paperglass.settings import (
    MEDISPAN_LLM_SCORING_ENABLED,
    MEDICATION_MATCHING_VERSION,
    MEDICATION_MATCHING_BATCH_SIZE,
)
from paperglass.domain.utils.array_utils import chunk_array, split_tuple_object
from paperglass.domain.utils.exception_utils import exceptionToMap
from paperglass.domain.util_json import convertToJson
from paperglass.domain.time import now_utc

from paperglass.domain.models import (
    DocumentOperationInstanceLog,
    ExtractedMedication,
    MedispanDrug,
    OperationMeta,
    
)
from paperglass.domain.models_common import (
    OrchestrationExceptionWithContext,
)

from paperglass.domain.values import (
    Configuration,
    MedicationValue,
    MedispanMedicationValue,    
    MedispanStatus,    
    DocumentOperationType,
    DocumentOperationStatus,
    
)
from paperglass.usecases.document_operation_instance_log import DocumentOperationInstanceLogService, does_success_operation_instance_exist
from paperglass.usecases.commands import (
    MedispanMatching
)
from paperglass.infrastructure.ports import (
    IUnitOfWork,
    IMedispanPort,
    IPromptAdapter,
    IRelevancyFilterPort,
    IQueryPort
)

from paperglass.log import getLogger, labels, CustomLogger
LOGGER = CustomLogger(__name__)

#OpenTelemetry instrumentation
SPAN_BASE: str = "APP:command_handling:"
from ..domain.utils.opentelemetry_utils import OpenTelemetryUtils
opentelemetry = OpenTelemetryUtils(SPAN_BASE)



class IStepMedispanMatching:
    async def run(self, command: MedispanMatching, uow: IUnitOfWork):
        raise NotImplementedError()

class StepMedispanMatchingResolver(IStepMedispanMatching):
    async def run(self, command: MedispanMatching, uow: IUnitOfWork, config:Configuration) -> List[ExtractedMedication]:
        
        if config.medispan_matching_version not in REGISTRY:
            raise ValueError(f"StepMedispanMatchingResolver:  Invalid medication matching version: {config.medispan_matching_version}")        

        adapter = REGISTRY[config.medispan_matching_version]()
        return await adapter.run(command, uow)
    

class StepMedispanMatchingAdapter_v1(IStepMedispanMatching):

    @inject
    async def run(self, command: MedispanMatching, uow: IUnitOfWork,
                             prompt_adapter:IPromptAdapter,
                             medispan_port:IMedispanPort,
                             relevancy_filter_adapter:IRelevancyFilterPort,
                             query:IQueryPort
                             ) -> List[ExtractedMedication]:
        LOGGER.debug("MedispanMatching: Running MedispanMatchingAdapter_v1")
        thisSpanName = "medispan_matching_v1"
        start_datetime = now_utc()

        extra = command.toExtra()

        operation_context = {
                "page_id": command.page_id,
                "page_number": command.page_number,
                "settings": {
                    "MEDISPAN_LLM_SCORING_ENABLED": MEDISPAN_LLM_SCORING_ENABLED
                },
                "model": {
                    "name": command.model,
                },
                "prompt_template": command.prompt
            }

        with await opentelemetry.getSpan(thisSpanName) as span:
            try:
                span.set_attribute("document_id", command.document_id)
                span.set_attribute("page_id", command.page_id)
                span.set_attribute("page_number", command.page_number)
                
                doc_logger = DocumentOperationInstanceLogService()

                opMeta:OperationMeta = OperationMeta(
                    type=DocumentOperationType.MEDICATION_EXTRACTION,
                    step = command.step_id,
                    document_id = command.document_id,
                    page_number = command.page_number,
                    document_operation_def_id=command.document_operation_definition_id,
                    document_operation_instance_id=command.document_operation_instance_id,
                    priority = command.priority
                )

                LOGGER.info('ExtractMedication: Extracting medication for documentId %s from page %s', command.document_id, command.page_number, extra=extra)
                success_log_exists, log =  await does_success_operation_instance_exist(command.document_id, command.document_operation_instance_id,command.page_number,command.step_id)
                if success_log_exists:
                    extracted_medications = await query.get_extracted_medications_by_operation_instance_id(command.document_id, command.document_operation_instance_id, extra=extra)
                    return [x for x in extracted_medications if x.page_number == command.page_number]

                if not command.extracted_medications:
                    LOGGER.debug("MedispanMatching: Extracted medications for document %s page %s is %s.  No matching to perform.  Returning input as result", command.document_id, command.page_number, command.extracted_medications, extra=extra)
                    operation_context['error'] = {"message": 'Extracted medications not found: ' + str(command.extracted_medications)}
                    doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_operation_instance_id=command.document_operation_instance_id,
                                                                                document_operation_definition_id=command.document_operation_definition_id,
                                                                                document_id=command.document_id,
                                                                                step_id= command.step_id,
                                                                                start_datetime=start_datetime,
                                                                                context=operation_context,
                                                                                page_number=command.page_number,
                                                                                status = DocumentOperationStatus.COMPLETED)
                    #uow.register_new(doc_operation_instance_log)
                    await doc_logger.save(doc_operation_instance_log, uow)

                    extra.update({
                        "branch": "no_extracted_medications",
                        "elapsed_time": doc_operation_instance_log.elapsed_time
                    })
                    LOGGER.info("Step::%s completed", command.step_id, extra=extra)

                    return []

                med_log_details = []

                filter_adapter_context = []
                output_medications = []
                idx = 0
                for extracted_medication in command.extracted_medications:
                    with await opentelemetry.getSpan(thisSpanName + ":medication") as span1:

                        extra2 = {
                            "index": idx,
                            "medication": extracted_medication.dict()
                        }
                        extra2.update(extra)

                        medispan_matched_medication:MedispanMedicationValue = None
                        medispan_status = MedispanStatus.UNMATCHED

                        this_med_log_details = {}

                        try:
                            extracted_medication_value = MedicationValue(
                                                                            name=extracted_medication.medication.name,
                                                                            strength=extracted_medication.medication.strength,
                                                                            dosage=extracted_medication.medication.dosage,
                                                                            route=extracted_medication.medication.route,
                                                                            frequency=extracted_medication.medication.frequency,
                                                                            instructions=extracted_medication.medication.instructions or extracted_medication.medication.frequency, # HHH maps frequency to instrutions
                                                                            form = extracted_medication.medication.form,
                                                                            start_date=extracted_medication.medication.start_date,
                                                                            end_date=extracted_medication.medication.end_date,
                                                                            discontinued_date=extracted_medication.medication.discontinued_date
                                                                        )

                            search_term: str = extracted_medication_value.fully_qualified_name
                            extra2["search_term"] = search_term

                            medispan_port_result: List[MedispanDrug] = await medispan_port.search_medications(search_term)
                            # If initial search does not return any results, try searching with just the first word of the medication name
                            if not medispan_port_result:
                                search_term = f"{extracted_medication_value.name.split(' ')[0]}"
                                LOGGER.debug("MedispanMatching: Initial search for medication '%s' did not yield any results.  Trying search with just the first word of the medication name: '%s'", extracted_medication_value.fully_qualified_name, search_term, extra=extra2)
                                medispan_port_result: List[MedispanDrug] = await medispan_port.search_medications(search_term)
                                this_med_log_details['medispan_search_term'] = search_term
                            else:
                                this_med_log_details['medispan_search_term'] = extracted_medication_value.fully_qualified_name

                            if medispan_port_result:
                                this_med_log_details['medispan_results'] = json.dumps([x.dict() for x in medispan_port_result], indent=2)
                            else:
                                this_med_log_details['medispan_results'] = None

                            opMeta.iteration = idx

                            filter_adapter_context.append({
                                "search_term": search_term,
                                "medispan_search_results": medispan_port_result,
                                "model": command.model,
                                "prompt": command.prompt
                            })

                            medispan_results_tuple = await relevancy_filter_adapter.re_rank(search_term, medispan_port_result, model=command.model, prompt=command.prompt, enable_llm=MEDISPAN_LLM_SCORING_ENABLED, metadata=opMeta.dict())
                            medispan_port_result, context = medispan_results_tuple
                            medispan_drug:MedispanDrug = medispan_port_result

                            this_med_log_details['medispan_drug'] = medispan_drug.dict() if medispan_drug else None

                            operation_context.update(context)
                            LOGGER.debug("MedispanMatching: Medispan drug for medication %s: %s", extracted_medication.medication.name, medispan_drug, extra=extra2)
                            if medispan_drug:
                                medispan_matched_medication = MedispanMedicationValue(
                                                                            medispan_id=medispan_drug.id,
                                                                            name=medispan_drug.GenericName,
                                                                            name_original=medispan_drug.NameDescription,
                                                                            #dosage=medispan_drug.strength.value + " " + medispan_drug.strength.unit if medispan_drug.strength else None,
                                                                            strength=medispan_drug.Strength+ " " + medispan_drug.StrengthUnitOfMeasure if medispan_drug.Strength else None,
                                                                            form=medispan_drug.Dosage_Form,
                                                                            route=medispan_drug.Route)

                                medispan_status = MedispanStatus.MATCHED

                                extracted_medication.set_medispan_medication(medispan_matched_medication)
                                extracted_medication.set_medispan_status(medispan_status)

                                extracted_medication.execution_id = command.execution_id
                                extracted_medication.document_operation_instance_id = command.document_operation_instance_id
                                #uow.register_new(extracted_medication)

                                this_med_log_details["medispan_filter_results"] = medispan_matched_medication.dict()

                            else:
                                LOGGER.debug("No medispan medication found for medication %s", extracted_medication.medication.name, extra=extra2)

                        except Exception as e:
                            extra2["error"] = exceptionToMap(e)
                            LOGGER.error('ExtractMedication: Error in searching medispan for medication %s: %s', extracted_medication.medication.name, str(e), extra=extra2)
                            medispan_status = MedispanStatus.ERRORED
                            this_med_log_details['error'] = {"message": 'Error in searching medispan for medication: ' + str(command.extracted_medications)}

                        this_med_log_details['medispan_status'] = medispan_status
                        med_log_details.append(this_med_log_details)

                        LOGGER.warning("ExtractedMedication: %s", extracted_medication.dict(), extra=extra2)

                        output_medications.append(extracted_medication)

                        idx += 1

                # End of medication loop -------------------------------------------------------------------------------------

                operation_context['medications'] = output_medications
                operation_context["medication_count"] = len(output_medications) if output_medications else 0
                operation_context['medispan_log_details'] = med_log_details
                operation_context["step_results"] = [x.dict() for x in output_medications]
                operation_context["medispan_matching_context"] = filter_adapter_context

                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_operation_instance_id=command.document_operation_instance_id,
                                                                                document_operation_definition_id=command.document_operation_definition_id,
                                                                                document_id=command.document_id,
                                                                                step_id= command.step_id,
                                                                                start_datetime=start_datetime,
                                                                                context=operation_context,
                                                                                page_number=command.page_number,
                                                                                status = DocumentOperationStatus.COMPLETED)
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)

                extra.update({
                    "branch": "extracted_medications",
                    "medication_count": len(output_medications) if output_medications else 0,
                    "elapsed_time": doc_operation_instance_log.elapsed_time
                })
                LOGGER.info("Step::%s completed", command.step_id, extra=extra)
                
                for medication in output_medications:
                    uow.register_new(medication)
                
                return output_medications
            except Exception as e:
                extra["error"] = exceptionToMap(e)
                LOGGER.error("MedispanMatching: Error in medispan matching: %s", str(e), exc_info=True, extra=extra)
                raise OrchestrationExceptionWithContext("Error in medispan matching", details=str(e), context=operation_context)


class StepMedispanMatchingAdapter_v2(IStepMedispanMatching):

    @inject
    async def run(self, command: MedispanMatching, uow: IUnitOfWork,
                             prompt_adapter:IPromptAdapter,
                             medispan_port:IMedispanPort,
                             relevancy_filter_adapter:IRelevancyFilterPort,
                             query:IQueryPort
                             ) -> List[ExtractedMedication]:
        
        LOGGER.debug("MedispanMatching: Running MedispanMatchingAdapter_v2")
        thisSpanName = "medispan_matching"
        start_datetime = now_utc()

        extra = command.toExtra()

        with await opentelemetry.getSpan(thisSpanName) as span:
            span.set_attribute("document_id", command.document_id)
            span.set_attribute("page_id", command.page_id)
            span.set_attribute("page_number", command.page_number)
            operation_context = {
                "page_id": command.page_id,
                "page_number": command.page_number,
                "settings": {
                    "MEDISPAN_LLM_SCORING_ENABLED": MEDISPAN_LLM_SCORING_ENABLED
                },
                "model": {
                    "name": command.model,
                },
                "priority": command.priority,
            }
            doc_logger = DocumentOperationInstanceLogService()

            opMeta:OperationMeta = OperationMeta(
                type=DocumentOperationType.MEDICATION_EXTRACTION,
                step = command.step_id,
                document_id = command.document_id,
                page_number = command.page_number,
                document_operation_def_id=command.document_operation_definition_id,
                document_operation_instance_id=command.document_operation_instance_id,
                priority = command.priority
            )

            LOGGER.debug('ExtractMedication: Extracting medication for documentId %s from page %s', command.document_id, command.page_number, extra=extra)
            success_log_exists, log =  await does_success_operation_instance_exist(command.document_id, command.document_operation_instance_id,command.page_number,command.step_id)
            existing_extracted_medications = []
            existing_extracted_medications = await query.get_extracted_medications_by_operation_instance_id(command.document_id, command.document_operation_instance_id)
            existing_extracted_medications = [x for x in existing_extracted_medications if x and x.page_number == command.page_number]
            if success_log_exists and not command.is_test:
                return existing_extracted_medications

            if not command.extracted_medications:
                LOGGER.debug("MedispanMatching: Extracted medications for document %s page %s is %s.  No matching to perform.  Returning input as result", command.document_id, command.page_number, command.extracted_medications, extra=extra)
                operation_context['error'] = {"message": 'Extracted medications not found: ' + str(command.extracted_medications)}
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context=operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.COMPLETED)
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)

                extra2= {
                    "branch": "no_extracted_medications",
                    "elapsed_time": doc_operation_instance_log.elapsed_time
                }
                extra2.update(extra)
                LOGGER.info("Step::%s completed", command.step_id, extra=extra2)

                return []

            med_log_details = []

            medispan_local_db = {}
            medispan_search_results = []

            med_log_db = {}

            idx = 0
            
            new_extracted_medication = []
            # check for any new medication that has not been processed
            for med in command.extracted_medications:
                is_existing_medication = True if len([x for x in existing_extracted_medications if x.id == med.id]) > 0 else False
                if not is_existing_medication:
                    new_extracted_medication.append(med)
            
            for extracted_medication in new_extracted_medication:
                
                this_med_log_details = med_log_db.get(extracted_medication.id, {})
                this_med_log_details["index"] = idx

                with await opentelemetry.getSpan(thisSpanName + ":medispan_search") as span1:
                    medispan_matched_medication:MedispanMedicationValue = None
                    medispan_status = MedispanStatus.UNMATCHED

                    try:
                        extracted_medication_value = MedicationValue(
                                                                        name=extracted_medication.medication.name,
                                                                        strength=extracted_medication.medication.strength,
                                                                        dosage=extracted_medication.medication.dosage,
                                                                        route=extracted_medication.medication.route,
                                                                        frequency=extracted_medication.medication.frequency,
                                                                        instructions=extracted_medication.medication.instructions or extracted_medication.medication.frequency, # HHH maps frequency to instrutions
                                                                        form = extracted_medication.medication.form,
                                                                        start_date=extracted_medication.medication.start_date,
                                                                        end_date=extracted_medication.medication.end_date,
                                                                        discontinued_date=extracted_medication.medication.discontinued_date
                                                                    )

                        search_term: str = extracted_medication_value.fully_qualified_name

                        medispan_port_result: List[MedispanDrug] = await medispan_port.search_medications(search_term)
                        # If initial search does not return any results, try searching with just the first word of the medication name
                        if not medispan_port_result:
                            search_term = f"{extracted_medication_value.name.split(' ')[0]}"
                            LOGGER.debug("MedispanMatching: Initial search for medication '%s' did not yield any results.  Trying search with just the first word of the medication name: '%s'", extracted_medication_value.fully_qualified_name, search_term, extra=extra)
                            medispan_port_result: List[MedispanDrug] = await medispan_port.search_medications(search_term)
                            this_med_log_details['medispan_search_term'] = search_term
                        else:
                            this_med_log_details['medispan_search_term'] = extracted_medication_value.fully_qualified_name

                        if medispan_port_result:
                            this_med_log_details['medispan_results'] = json.dumps([x.dict() for x in medispan_port_result], indent=2)
                        else:
                            this_med_log_details['medispan_results'] = None

                        opMeta.iteration = idx

                        medispan_result = {
                            "id": extracted_medication.id,
                            "index": idx,
                            "medication_name": search_term,
                            "medispan_options": [x.dict() for x in medispan_port_result]
                        }
                        medispan_search_results.append(medispan_result)

                        # Populate local medispan db for later use
                        for medispan in medispan_port_result:                            
                            medispan_local_db[medispan.id] = medispan

                        med_log_db[extracted_medication.id] = this_med_log_details

                        idx += 1

                    except Exception as e:
                        extra2 = {
                            "error": exceptionToMap(e),
                        }
                        extra2.update(extra)
                        
                        LOGGER.error('ExtractMedication: Error in searching medispan for medication %s: %s.', extracted_medication.medication.name, str(e), extra=extra2)
                        medispan_status = MedispanStatus.ERRORED
                        this_med_log_details['error'] = {"message": 'Error in searching medispan for medication: ' + str(new_extracted_medication)}
                        
                        med_log_db[extracted_medication.id] = this_med_log_details

                        idx += 1 # Needed for matching the LLM result back to the right medication.
                        continue

            # End of medication 1 loop -------------------------------------------------------------------------------------

            # LLM Best Match Filter
            matching_context = {}
            llm_result_db = {}
            LOGGER.debug("MedispanMatching: Applying LLM filter to medispan search results", extra=extra)
            prompt_metadata = opMeta.dict()
            prompt_metadata.update(extra)
            with await opentelemetry.getSpan(thisSpanName + ":medispan_filter") as span1:
                #Perform Medispan LLM Match
                filtered_medications, matching_context = await self.medispan_matching(prompt_template=command.prompt, model=command.model, prompt_input=medispan_search_results, metadata=prompt_metadata)
                for llm_result in filtered_medications:
                    llm_result_db[llm_result["id"]] = llm_result
            
            LOGGER.debug("matching_context: %s", matching_context, extra=extra)
            
            
            # Apply Medispan match to the extracted medications
            output_medications = []
            LOGGER.debug("MedispanMatching: Applying medispan match to extracted medications", extra=extra)
            with await opentelemetry.getSpan(thisSpanName + ":medispan_apply") as span1:
                for extracted_medication in new_extracted_medication:                
                    this_med_log_details = med_log_db.get(extracted_medication.id, {})
                    try:
                        # Get the LLM result for this medication
                        llm_result = llm_result_db.get(extracted_medication.id)

                        # If result then find the medispan medication and apply to 
                        if llm_result:
                            medispan_drug:MedispanDrug = medispan_local_db.get(llm_result["medispan_id"])

                            this_med_log_details['medispan_drug'] = medispan_drug.dict() if medispan_drug else None

                            LOGGER.debug("MedispanMatching: Medispan drug for medication %s: %s", extracted_medication.medication.name, medispan_drug, extra=extra)
                            if medispan_drug:
                                composite_strength = medispan_drug.Strength
                                if medispan_drug.StrengthUnitOfMeasure:
                                    composite_strength += " " + medispan_drug.StrengthUnitOfMeasure
                                    
                                medispan_matched_medication = MedispanMedicationValue(
                                                                            medispan_id=medispan_drug.id,
                                                                            name=medispan_drug.GenericName,
                                                                            name_original=medispan_drug.NameDescription,
                                                                            #dosage=medispan_drug.strength.value + " " + medispan_drug.strength.unit if medispan_drug.strength else None,
                                                                            strength=composite_strength,
                                                                            form=medispan_drug.Dosage_Form,
                                                                            route=medispan_drug.Route)

                                medispan_status = MedispanStatus.MATCHED

                                extracted_medication.set_medispan_medication(medispan_matched_medication)
                                extracted_medication.set_medispan_status(medispan_status)

                                extracted_medication.execution_id = command.execution_id
                                extracted_medication.document_operation_instance_id = command.document_operation_instance_id
                                
                                #uow.register_new(extracted_medication)

                                this_med_log_details["medispan_filter_results"] = medispan_matched_medication.dict()

                            else:
                                LOGGER.debug("No medispan medication found for medication %s", extracted_medication.medication.name, extra=extra)

                    except Exception as e:
                        extra["error"] = exceptionToMap(e)
                        LOGGER.error('ExtractMedication: Error in searching medispan for medication %s: %s', extracted_medication.medication.name, str(e), extra=extra)
                        medispan_status = MedispanStatus.ERRORED
                        this_med_log_details['error'] = {"message": 'Error in searching medispan for medication: ' + str(new_extracted_medication)}

                    this_med_log_details['medispan_status'] = medispan_status
                    med_log_db[extracted_medication.id] = this_med_log_details

                    extra2 = {
                        "index": idx,
                        "extracted_medication": extracted_medication.dict(),
                    }
                    extra2.update(extra)

                    LOGGER.warning("ExtractedMedication: %s", extracted_medication.dict(), extra=extra2)

                    output_medications.append(extracted_medication)

                    idx += 1

            # End of medication 2 loop -------------------------------------------------------------------------------------

            log_detail_list = [x for x in med_log_db.values()]
            log_detail_list = sorted(log_detail_list, key=lambda obj: obj["index"])
            
            operation_context['medications'] = output_medications
            operation_context["medication_count"] = len(output_medications) if output_medications else 0
            operation_context['medispan_log_details'] = log_detail_list
            operation_context['step_command'] = command.dict()
            operation_context["step_results"] = [x.dict() for x in output_medications]
            operation_context.update(matching_context)     

            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context=operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.COMPLETED)
            await doc_logger.save(doc_operation_instance_log, uow)

            extra2= {                
                "branch": "extracted_medications",
                "medication_count": len(output_medications) if output_medications else 0,
                "elapsed_time": doc_operation_instance_log.elapsed_time
            }
            extra2.update(extra)
            LOGGER.info("Step::%s completed", command.step_id, extra=extra2)
            
            for medication in output_medications:
                uow.register_new(medication)
            
            return output_medications
        
    async def medispan_matching(self, prompt_template, model, prompt_input, batch_size=MEDICATION_MATCHING_BATCH_SIZE, metadata={}):
        batches = chunk_array(prompt_input, batch_size)

        output = []
        context = {
            "batch_context": []
        }
        context.update(metadata)
        idx = 0
        for batch in batches:
            results, batch_context = await self.medispanmatching_batch(prompt_template, model, batch, metadata=metadata)
            output.extend(results)
            batch_context["batch_index"] = idx

            context["batch_context"].append(batch_context)

            idx += 1
        return output, context

    @inject
    async def medispanmatching_batch(self, prompt_template, model, prompt_input, prompt: IPromptAdapter, metadata={}):        

        start_time = now_utc()
        extra = {}
        extra.update(metadata)

        med_db = {}
        medispan_db = {}        

        med_list = []

        # Populate local kv stores
        for med in prompt_input:            
            id = med["id"]
            med_db[id] = med        

            med_list.append({
                "id": med["id"],
                "medication_name": med["medication_name"]
            })

            medispan_options = med["medispan_options"]
            for medispan in medispan_options:
                medispan_db[medispan["id"]] = medispan            

        # Create a unique list of medispan options
        #LOGGER.debug("Med DB: %s", med_db)
        medispan_list = list(medispan_db.values())

        #LOGGER.debug("Medispan DB: %s", json.dumps(medispan_list, indent=2))

        this_prompt = prompt_template.replace("{SEARCH_TERM}", json.dumps(med_list, indent=2))
        this_prompt = this_prompt.replace("{DATA}", json.dumps(medispan_list, indent=2))

        batch_context = {
            "batch_size": len(prompt_input),
            "prompt": this_prompt,
            "medication_list": med_list,
            "medispan_list": medispan_list
        }

        LOGGER.debug("Prompt: %s", this_prompt)
        LOGGER.debug("Prompt size: %s", len(this_prompt))

        results = None
        try:
            LOGGER.debug("== Executing Medispan Match prompt ====================================================================================")
            results = await prompt.multi_modal_predict_2([this_prompt], model=model, metadata=metadata)
            LOGGER.debug("== Execution of Medispan Match complete ==================================================================================")
            batch_context["prompt_results"] = results
            batch_context["prompt_results_size"] = len(results)            
                        
            try:
                results = convertToJson(results)
            except Exception as e:   
                extra.update(batch_context)
                extra["error"] = exceptionToMap(e)
                LOGGER.warning("MedispanMatching: Error in prompt conversion to JSON: %s", str(e), extra=extra)
                #raise OrchestrationExceptionWithContext("Medispan_matching: Error in prompt conversion", context=batch_context)
                # sometimes prompt output is wierd e.g: 
                # ```json[]```There are no entries in the MATCH LIST, so no matches can be made.  The response is an empty JSON array.
                # so instead of raising exception, we will just return empty list
                results = []

            LOGGER.debug("Results: %s", json.dumps(results, indent=2))
        except Exception as e:            
            batch_context["error"] = exceptionToMap(e)
            extra.update(batch_context)
            LOGGER.error("MedispanMatching: Error in prompt execution: %s", str(e), extra=extra)
            raise OrchestrationExceptionWithContext("Medispan_matching: Error in prompt execution", context=batch_context)

        result_db = {}
        for result in results:
            id, medispanid = split_tuple_object(result)
            result_db[id] = medispanid

        #LOGGER.debug("ResultDB: %s", json.dumps(result_db, indent=2))

        # Create output list of matches
        output = []
        idx= 0
        for item in med_db.keys():
            extra2 = {
                "index": idx,
                "key": item
            }
            id = item
            med = med_db[id]
            
            if not med:
                extra2["message"] = "Medication found not matching to medispan list passed to prompt"
                LOGGER.warning("Medication found not matching to medispan list passed to prompt: %s", id, extra=extra2)
                continue

            idx = med["index"]
            medication_name = med["medication_name"]

            LOGGER.debug("Item: %s medication_name: %s", id, medication_name, extra=extra2)

            medispan_id = None
            if item in result_db:
                LOGGER.debug("Found medispanid for id: %s", id, extra=extra2)
                medispan_id = result_db[item]
            else:
                LOGGER.debug("No medispanid found for id: %s", id, extra=extra2)
            
            output.append({
                    "id": id,
                    "index": idx,
                    "medication_name": medication_name,
                    "medispan_id": medispan_id,
                    "medispan_name": medispan_db[medispan_id]["NameDescription"] if medispan_id else None
                }
            )
            idx += 1

        end_time = now_utc()
        elapsed_time = end_time - start_time            
        LOGGER.debug("Elapsed Time: %s  End time: %s", elapsed_time.total_seconds(), end_time, extra=extra)

        batch_context["step_results"] = output

        return output, batch_context

REGISTRY = {
    "1": StepMedispanMatchingAdapter_v1,
    "2": StepMedispanMatchingAdapter_v2
}