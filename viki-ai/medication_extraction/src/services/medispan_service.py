from copy import deepcopy
import json
import re
from typing import List

from adapters.medispan_api import MedispanAPIAdapter
from adapters.pgvector_adapter import MedispanPgVectorAdapter
from adapters.firestore_vector_adapter import MedispanFirestoreVectorAdapter
from adapters.circuit_breaker_adapter import CircuitBreakerAdapter
from settings import STEP_MEDISPANMATCH_LLM_MODEL, MEDDB_MAX_RESULTS

from models import MedispanMatchConfig
from model_metric import Metric
from prompts import PromptTemplates

from adapters.llm import StandardPromptAdapter
from adapters.medispan_firestore_vector_search import MedispanFireStoreVectorSearchAdapter
from utils.exception import OrchestrationExceptionWithContext, exceptionToMap
from utils.date import now_utc
from models import ExtractedMedication, MedicationValue, MedispanDrug, MedispanMedicationValue, MedispanStatus, OperationMeta
from utils.custom_logger import getLogger

LOGGER = getLogger(__name__)

class MedispanMatchService:
    
    def __init__(self, tenant_id:str, medispan_adapter_settings:MedispanMatchConfig, medispan_model=None):
        self.tenant_id = tenant_id
        self.medispan_adapter_settings = medispan_adapter_settings
        self.medispan_model = medispan_model
    
    def model(self):
        LOGGER.debug("Medispan Match model: %s", self.medispan_model or STEP_MEDISPANMATCH_LLM_MODEL)
        return self.medispan_model or STEP_MEDISPANMATCH_LLM_MODEL
    
    @staticmethod
    def prompt():
        return PromptTemplates.MEDISPAN_MATCH
        
    
    async def run(self, app_id, tenant_id, patient_id, 
                  document_id, page_number,
                  run_id,
                  extracted_medications_raw:List[ExtractedMedication]) -> List[ExtractedMedication]:
        
        extra = {
            "app_id": app_id,
            "tenant_id": tenant_id,
            "patient_id": patient_id,
            "document_id": document_id,
            "page_number": page_number,
            "run_id": run_id,
        }
        if self.medispan_adapter_settings and (self.tenant_id in self.medispan_adapter_settings.v2_enabled_tenants or self.medispan_adapter_settings.v2_enabled_globally):
            extra.update({
                "adapter": self.medispan_adapter_settings.v2_repo,
                "catalog": self.medispan_adapter_settings.catalog,
            })
            if self.medispan_adapter_settings.v2_repo == "alloydb":
                medispan_port = MedispanPgVectorAdapter(app_id=app_id, catalog=self.medispan_adapter_settings.catalog)
                Metric.send("EXTRACTION::MEDDB::SEARCH::ADAPTER", branch=self.medispan_adapter_settings.v2_repo, tags=extra)
            elif self.medispan_adapter_settings.v2_repo == "firestore":
                medispan_port = MedispanFirestoreVectorAdapter(app_id=app_id, catalog=self.medispan_adapter_settings.catalog)
                Metric.send("EXTRACTION::MEDDB::SEARCH::ADAPTER", branch=self.medispan_adapter_settings.v2_repo, tags=extra)
            elif self.medispan_adapter_settings.v2_repo == "alloydb-wcircuitbreaker":
                medispan_port = CircuitBreakerAdapter(app_id=app_id, catalog=self.medispan_adapter_settings.catalog)
                Metric.send("EXTRACTION::MEDDB::SEARCH::ADAPTER", branch=self.medispan_adapter_settings.v2_repo, tags=extra)
            else:
                # Default to alloydb if v2_repo is not specified
                medispan_port = MedispanPgVectorAdapter(app_id=app_id, catalog=self.medispan_adapter_settings.catalog)
                Metric.send("EXTRACTION::MEDDB::SEARCH::ADAPTER", branch="default(alloydb)", tags=extra)
        else:
            extra.update({
                "adapter": "firestore-orig",
                "catalog": "medispan"
            })
            medispan_port = MedispanFireStoreVectorSearchAdapter()
            Metric.send("EXTRACTION::MEDDB::SEARCH::ADAPTER", branch="firestore-orig", tags=extra)
            
        #step_id = "medispan_match"
        start_datetime = now_utc()
        operation_context = {}
        extra = {
            "app_id": app_id,
            "tenant_id": tenant_id,
            "patient_id": patient_id,
            "document_id": document_id,
            "page_number": page_number,
            "run_id": run_id,
        }
        operation_context = {
            "page_number": page_number,
            "model": {
                "name":self.model(),
            },
            "prompt_template": MedispanMatchService.prompt(),
        }
        extracted_medications = deepcopy(extracted_medications_raw)
        LOGGER.debug('ExtractMedication: Extracting medication for documentId %s from page %s', document_id, page_number, extra=extra)

        opMeta:OperationMeta = OperationMeta(
                type="medication_extraction",
                step = "MEDISPAN_MATCHING",
                document_id = document_id,
                page_number = page_number
            )
        
        if not extracted_medications:
            LOGGER.debug("MedispanMatching: Extracted medications for document %s page %s is %s.  No matching to perform.  Returning input as result", document_id, page_number, extracted_medications, extra=extra)
            operation_context['error'] = {"message": 'Extracted medications not found: ' + str(extracted_medications)}
            

            extra2= {
                "branch": "no_extracted_medications",
                "elapsed_time": (now_utc() - start_datetime).total_seconds()
            }
            extra2.update(extra)
            #LOGGER.info("Step::%s completed", step_id, extra=extra2)

            return [],[]

        #med_log_details = []

        medispan_local_db = {}
        medispan_search_results = []

        med_log_db = {}

        idx = 0
        
        for extracted_medication in extracted_medications:
            
            this_med_log_details = med_log_db.get(extracted_medication.id, {})
            this_med_log_details["index"] = idx

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
                #if not is_medispan_pg_vector:
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
                # else:
                #     # pgvector search path
                #     # search by name will result in keyword search which is very effecient and possibility of better result
                #     # assuming reranking will pick right values later
                #     search_term = f"{extracted_medication_value.name}"
                #     medispan_port_result: List[MedispanDrug] = await medispan_port.search_medications(search_term,
                #                                                                                     dosage_form=extracted_medication_value.dosage, 
                #                                                                                     route=extracted_medication_value.route)
                #     if medispan_port_result:
                #         this_med_log_details['medispan_search_term'] = search_term
                #     else:
                #         search_term: str = extracted_medication_value.fully_qualified_name
                    
                #         medispan_port_result: List[MedispanDrug] = await medispan_port.search_medications(search_term)
                #         this_med_log_details['medispan_search_term'] = extracted_medication_value.fully_qualified_name

                # Apply reranking if enabled and conditions are met
                medispan_port_result = self.rerank_medications(medispan_port_result, search_term, extracted_medication_value)

                # Apply limiting of results
                medispan_port_result = self._limit_results(medispan_port_result)

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
                this_med_log_details['error'] = {"message": 'Error in searching medispan for medication: ' + str(extracted_medication)}
                
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
        
        #Perform Medispan LLM Match
        filtered_medications, matching_context = await self.medispan_matching(
            prompt_template=MedispanMatchService.prompt(),
            model=self.model(),
            prompt_input=medispan_search_results,
            metadata=prompt_metadata
        )
        for llm_result in filtered_medications:
            llm_result_db[llm_result["id"]] = llm_result
        
        LOGGER.debug("matching_context: %s", matching_context, extra=extra)
        
        
        # Apply Medispan match to the extracted medications
        output_medications = []
        LOGGER.debug("MedispanMatching: Applying medispan match to extracted medications", extra=extra)
        for extracted_medication in extracted_medications:                
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
                        
                        #uow.register_new(extracted_medication)

                        this_med_log_details["medispan_filter_results"] = medispan_matched_medication.dict()

                    else:
                        LOGGER.debug("No medispan medication found for medication %s", extracted_medication.medication.name, extra=extra)

            except Exception as e:
                extra["error"] = exceptionToMap(e)
                LOGGER.error('ExtractMedication: Error in searching medispan for medication %s: %s', extracted_medication.medication.name, str(e), extra=extra)
                medispan_status = MedispanStatus.ERRORED
                this_med_log_details['error'] = {"message": 'Error in searching medispan for medication: ' + str(extracted_medication)}

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
        operation_context['step_command'] = dict()
        operation_context["step_results"] = [x.dict() for x in output_medications]
        operation_context.update(matching_context)     

        

        extra2= {                
            "branch": "extracted_medications",
            "medication_count": len(output_medications) if output_medications else 0,
            "elapsed_time": (now_utc() - start_datetime).total_seconds()
        }
        extra2.update(extra)
        #LOGGER.info("Step::%s completed", step_id, extra=extra2)
        
        
        return output_medications,medispan_search_results
        
    async def medispan_matching(self, prompt_template, model, prompt_input, batch_size=20, metadata={}):
        batches = self.chunk_array(prompt_input, batch_size)

        output = []
        context = {
            "batch_context": []
        }
        context.update(metadata)
        idx = 0
        for batch in batches:
            
            metadata.update({                
                "iteration": idx
            })

            results, batch_context = await self.medispanmatching_batch(prompt_template, model, batch,prompt_adapter=StandardPromptAdapter(), metadata=metadata)
            output.extend(results)
            batch_context["batch_index"] = idx

            context["batch_context"].append(batch_context)

            idx += 1
        return output, context

    async def medispanmatching_batch(self, prompt_template, model, prompt_input, prompt_adapter, metadata={}):        

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

        this_prompt = prompt_template.replace("{SEARCH_TERM}", json.dumps(med_list))
        this_prompt = this_prompt.replace("{DATA}", json.dumps(medispan_list))

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
            results = await prompt_adapter.multi_modal_predict_2([this_prompt], model=model, metadata=metadata)
            LOGGER.debug("== Execution of Medispan Match complete ==================================================================================")
            batch_context["prompt_results"] = results
            batch_context["prompt_results_size"] = len(results)            
            LOGGER.debug("Prompt Results: %s", json.dumps(results, indent=2))           
            try:
                # results = self.convertToJson(results)
                results = prompt_adapter.extract_json_from_response(results)
                batch_context["results"] = results
            except Exception as e:   
                extra.update(batch_context)
                extra["error"] = exceptionToMap(e)
                LOGGER.warning("MedispanMatching: Error in prompt conversion to JSON: %s %s", str(e), results, extra=extra)
                #raise OrchestrationExceptionWithContext("Medispan_matching: Error in prompt conversion", context=batch_context)
                # sometimes prompt output is wierd e.g: 
                # ```json[]```There are no entries in the MATCH LIST, so no matches can be made.  The response is an empty JSON array.
                # so instead of raising exception, we will just return empty list
                results = []
            if isinstance(results, dict):
                results = [results]
            LOGGER.debug("Results: %s", json.dumps(results, indent=2))
        except Exception as e:            
            batch_context["error"] = exceptionToMap(e)
            extra.update(batch_context)
            LOGGER.error("MedispanMatching: Error in prompt execution: %s", str(e), extra=extra)
            raise OrchestrationExceptionWithContext("Medispan_matching: Error in prompt execution", context=batch_context)

        result_db = {}
        for result in results:
            LOGGER.debug("Result item: %s", result, extra=batch_context)
            if result:
                try:
                    id, medispanid = self.split_tuple_object(result)
                    result_db[id] = medispanid
                except Exception as e:
                    extra["error"] = exceptionToMap(e)
                    extra.update(batch_context)
                    LOGGER.error("MedispanMatching: Error in result conversion: %s", str(e), extra=extra)
                    raise OrchestrationExceptionWithContext("Medispan_matching: Error in result conversion", context=batch_context)
            else:
                LOGGER.debug("Empty result item", extra=batch_context)
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
                    "medispan_name": medispan_db[medispan_id]["NameDescription"] if medispan_id and medispan_db and medispan_id in medispan_db.keys() else None
                }
            )
            idx += 1

        end_time = now_utc()
        elapsed_time = end_time - start_time            
        LOGGER.debug("Elapsed Time: %s  End time: %s", elapsed_time.total_seconds(), end_time, extra=extra)

        batch_context["step_results"] = output

        return output, batch_context

    def chunk_array(self, array, chunk_size):
        return [array[i:i + chunk_size] for i in range(0, len(array), chunk_size)]
    
    def convertToJson(self,serializedJson):
        serializedJson = serializedJson.strip()    
        if serializedJson.startswith("```json") and serializedJson.endswith("```"):
            #LOGGER.debug("Wrapped json string convert to json")
            cleanjson = serializedJson[7:]
            cleanjson = cleanjson[:-3]        
            return json.loads(cleanjson)
        else:
            #LOGGER.debug("Unwrapped json string convert to json")
            return json.loads(serializedJson)
        
    def split_tuple_object(self,t):
        t0 = list(t.keys())[0]
        t1 = list(t.values())[0]
        return t0, t1
    
    def rerank_medications(self, medispan_port_result: List[MedispanDrug], search_term: str, extracted_medication_value: MedicationValue) -> List[MedispanDrug]:
        """
        Rerank medications based on form and strength matching with proper prioritization.
        
        Priority order:
        1. Items matching both form AND strength (highest priority)
        2. Items matching strength only
        3. Items matching form only  
        4. All the rest
        
        Args:
            medispan_port_result: List of MedispanDrug objects from the search
            search_term: The search term used
            extracted_medication_value: The extracted medication value
            
        Returns:
            Reranked and limited list of MedispanDrug objects
        """
        # Check if medispan_adapter_settings is None or reranking is disabled
        if (not self.medispan_adapter_settings or 
            not self.medispan_adapter_settings.v2_settings or 
            not self.medispan_adapter_settings.v2_settings.rerank_settings or
            not self.medispan_adapter_settings.v2_settings.rerank_settings.enabled):
            LOGGER.debug("Reranking disabled by configuration")
            # Still apply result limiting even if reranking is disabled
            return self._limit_results(medispan_port_result)
        
        # Check if both form and strength reranking are disabled
        form_enabled = self.medispan_adapter_settings.v2_settings.rerank_settings.rerank_form_enabled
        strength_enabled = self.medispan_adapter_settings.v2_settings.rerank_settings.rerank_strength_enabled
        
        if not form_enabled and not strength_enabled:
            LOGGER.debug("Both form and strength reranking disabled")
            return self._limit_results(medispan_port_result)
        
        # Perform comprehensive reranking with proper prioritization
        result = self._rerank_with_priority(medispan_port_result, extracted_medication_value, form_enabled, strength_enabled)
        
        # Apply result limiting
        return self._limit_results(result)

    def rerank_medications_form(self, medispan_port_result: List[MedispanDrug], search_term: str, extracted_medication_value: MedicationValue) -> List[MedispanDrug]:
        """
        Rerank medications based on form matching.
        
        Args:
            medispan_port_result: List of MedispanDrug objects from the search
            search_term: The search term used
            extracted_medication_value: The extracted medication value
            
        Returns:
            Reranked list of MedispanDrug objects with form matches at the top
        """
        # Check if form is specified in extracted medication
        if not extracted_medication_value.form:
            LOGGER.debug("No form specified in extracted medication, skipping form reranking")
            return medispan_port_result
        
        # Separate medications that match form from those that don't
        matching_form_meds = []
        non_matching_meds = []
        
        extracted_form_lower = extracted_medication_value.form.lower()
        
        for med in medispan_port_result:
            if med.Dosage_Form and med.Dosage_Form.lower() == extracted_form_lower:
                matching_form_meds.append(med)
                LOGGER.debug("Medication '%s' with form '%s' matches extracted form '%s'", 
                           med.NameDescription, med.Dosage_Form, extracted_medication_value.form)
            else:
                non_matching_meds.append(med)
        
        # Return reranked list with matching form medications at the top
        reranked_result = matching_form_meds + non_matching_meds
        
        LOGGER.debug("Form reranking complete: %d medications moved to top based on form matching", 
                    len(matching_form_meds))
        
        return reranked_result

    def rerank_medications_strength(self, medispan_port_result: List[MedispanDrug], search_term: str, extracted_medication_value: MedicationValue) -> List[MedispanDrug]:
        """
        Rerank medications based on strength matching for eligible forms.
        This function preserves any existing form grouping by reranking within each form group.
        
        Args:
            medispan_port_result: List of MedispanDrug objects from the search
            search_term: The search term used
            extracted_medication_value: The extracted medication value
            
        Returns:
            Reranked list of MedispanDrug objects with strength matches at the top within each form group
        """
        # Check if the form is eligible for strength reranking
        if not extracted_medication_value.form:
            LOGGER.debug("No form specified in extracted medication, skipping strength reranking")
            return medispan_port_result
            
        # Check if form is in eligible forms list (case insensitive)
        eligible_forms = [form.lower() for form in self.medispan_adapter_settings.v2_settings.rerank_settings.strength_ranking_eligible_forms]
        if extracted_medication_value.form.lower() not in eligible_forms:
            LOGGER.debug("Form '%s' not in eligible forms list %s, skipping strength reranking", 
                        extracted_medication_value.form, self.medispan_adapter_settings.v2_settings.rerank_settings.strength_ranking_eligible_forms)
            return medispan_port_result
            
        # Extract numeric components from the extracted medication strength
        extracted_strength_numbers = self._extract_numeric_components(extracted_medication_value.strength)
        if not extracted_strength_numbers:
            LOGGER.debug("No numeric components found in extracted medication strength '%s', skipping strength reranking", 
                        extracted_medication_value.strength)
            return medispan_port_result
        
        # Group medications by form to preserve form-based ordering
        form_groups = {}
        for med in medispan_port_result:
            form_key = med.Dosage_Form.lower() if med.Dosage_Form else "unknown"
            if form_key not in form_groups:
                form_groups[form_key] = []
            form_groups[form_key].append(med)
        
        # Rerank within each form group
        reranked_result = []
        total_strength_matches = 0
        
        for form_key, meds_in_form in form_groups.items():
            matching_strength_meds = []
            non_matching_meds = []
            
            for med in meds_in_form:
                med_strength_numbers = self._extract_numeric_components(med.Strength)
                
                # Check if any numeric component from extracted medication is present in candidate
                if any(num in med_strength_numbers for num in extracted_strength_numbers):
                    matching_strength_meds.append(med)
                    total_strength_matches += 1
                    LOGGER.debug("Medication '%s' with strength '%s' matches extracted strength components %s", 
                               med.NameDescription, med.Strength, extracted_strength_numbers)
                else:
                    non_matching_meds.append(med)
            
            # Add reranked medications for this form group (strength matches first)
            reranked_result.extend(matching_strength_meds + non_matching_meds)
        
        LOGGER.debug("Strength reranking complete: %d medications moved to top based on strength matching", 
                    total_strength_matches)
        
        return reranked_result
    
    def _extract_numeric_components(self, strength_str: str) -> List[str]:
        """
        Extract numeric components from a strength string.
        
        Args:
            strength_str: The strength string to parse
            
        Returns:
            List of numeric components as strings
        """
        if not strength_str:
            return []
            
        # Use regex to find all numeric values (including decimals)
        numeric_pattern = r'\d+(?:\.\d+)?'
        numbers = re.findall(numeric_pattern, strength_str)
        
        return numbers
    
    def _limit_results(self, medispan_results: List[MedispanDrug]) -> List[MedispanDrug]:
        """
        Limit the results based on total_results configuration.
        
        Args:
            medispan_results: List of MedispanDrug objects
            
        Returns:
            Limited list of MedispanDrug objects
        """
        if (not self.medispan_adapter_settings or 
            not self.medispan_adapter_settings.v2_settings or 
            not self.medispan_adapter_settings.v2_settings.total_results):

            LOGGER.debug("No total_results configuration found, trimming to the universal default")            
            return medispan_results[:MEDDB_MAX_RESULTS]
        
        total_results = self.medispan_adapter_settings.v2_settings.total_results
        limited_results = medispan_results[:total_results] if medispan_results else []
        
        if len(medispan_results) > total_results:
            LOGGER.debug("Limited results from %d to %d based on total_results configuration", 
                        len(medispan_results), len(limited_results))
        
        return limited_results
    
    def _is_form_eligible_for_strength_ranking(self, form: str) -> bool:
        """
        Check if a form is eligible for strength ranking.
        
        Args:
            form: The medication form to check
            
        Returns:
            True if the form is eligible for strength ranking, False otherwise
        """
        if (not self.medispan_adapter_settings or 
            not self.medispan_adapter_settings.v2_settings or 
            not self.medispan_adapter_settings.v2_settings.rerank_settings or
            not self.medispan_adapter_settings.v2_settings.rerank_settings.strength_ranking_eligible_forms):
            return False
        
        eligible_forms = [f.lower() for f in self.medispan_adapter_settings.v2_settings.rerank_settings.strength_ranking_eligible_forms]
        return form.lower() in eligible_forms
    
    def _rerank_with_priority(self, medispan_results: List[MedispanDrug], extracted_medication_value: MedicationValue, 
                             form_enabled: bool, strength_enabled: bool) -> List[MedispanDrug]:
        """
        Rerank medications with proper priority handling.
        
        Priority order:
        1. Items matching both form AND strength (highest priority)
        2. Items matching strength only
        3. Items matching form only  
        4. All the rest
        
        Args:
            medispan_results: List of MedispanDrug objects
            extracted_medication_value: The extracted medication value
            form_enabled: Whether form reranking is enabled
            strength_enabled: Whether strength reranking is enabled
            
        Returns:
            Reranked list of MedispanDrug objects
        """
        # Initialize priority groups
        both_match = []      # Form AND strength match
        strength_only = []   # Strength match only
        form_only = []       # Form match only
        no_match = []        # No matches
        
        # Determine what we're checking for
        check_form = form_enabled and extracted_medication_value.form
        check_strength = (strength_enabled and 
                         extracted_medication_value.form and 
                         extracted_medication_value.strength and
                         self._is_form_eligible_for_strength_ranking(extracted_medication_value.form))
        
        # Get extracted strength components for comparison
        extracted_strength_numbers = []
        if check_strength:
            extracted_strength_numbers = self._extract_numeric_components(extracted_medication_value.strength)
            if not extracted_strength_numbers:
                check_strength = False
                LOGGER.debug("No numeric components found in extracted medication strength '%s', disabling strength checking", 
                            extracted_medication_value.strength)
        
        # Categorize each medication
        for med in medispan_results:
            form_matches = False
            strength_matches = False
            
            # Check form match
            if check_form:
                form_matches = (med.Dosage_Form and 
                               med.Dosage_Form.lower() == extracted_medication_value.form.lower())
            
            # Check strength match
            if check_strength:
                med_strength_numbers = self._extract_numeric_components(med.Strength)
                strength_matches = any(num in med_strength_numbers for num in extracted_strength_numbers)
            
            # Categorize based on matches
            if check_form and check_strength:
                if form_matches and strength_matches:
                    both_match.append(med)
                    LOGGER.debug("Medication '%s' matches both form '%s' and strength components %s", 
                               med.NameDescription, extracted_medication_value.form, extracted_strength_numbers)
                elif strength_matches:
                    strength_only.append(med)
                    LOGGER.debug("Medication '%s' matches strength components %s only", 
                               med.NameDescription, extracted_strength_numbers)
                elif form_matches:
                    form_only.append(med)
                    LOGGER.debug("Medication '%s' matches form '%s' only", 
                               med.NameDescription, extracted_medication_value.form)
                else:
                    no_match.append(med)
            elif check_form:
                if form_matches:
                    form_only.append(med)
                    LOGGER.debug("Medication '%s' matches form '%s'", 
                               med.NameDescription, extracted_medication_value.form)
                else:
                    no_match.append(med)
            elif check_strength:
                if strength_matches:
                    strength_only.append(med)
                    LOGGER.debug("Medication '%s' matches strength components %s", 
                               med.NameDescription, extracted_strength_numbers)
                else:
                    no_match.append(med)
            else:
                # Neither form nor strength checking enabled/applicable
                no_match.append(med)
        
        # Combine in priority order
        reranked_result = both_match + strength_only + form_only + no_match
        
        LOGGER.debug("Priority reranking complete: %d both matches, %d strength only, %d form only, %d no matches", 
                    len(both_match), len(strength_only), len(form_only), len(no_match))
        
        return reranked_result
