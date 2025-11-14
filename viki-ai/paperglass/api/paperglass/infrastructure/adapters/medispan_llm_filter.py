from typing import List, Tuple
import json

from kink import inject

from paperglass.settings import (
    MEDISPAN_LLM_OPTIMIZEPROMPT_ENABLED,    
    MULTIMODAL_ADVANCED_MODEL as MULTIMODAL_MODEL
)

from paperglass.domain.string_utils import remove_parentheses_substrings, contains_paranthetical

from ...domain.values import (

    MedicationValue,
    MedispanMedicationValue,
    MedispanStatus,
    Page as PageModel,
    ConfigurationKey,
)

from ...domain.models import (    
    MedispanDrug,
    OperationMeta,
)

from paperglass.infrastructure.ports import (
    IMedispanPort,
    IPromptAdapter,
    IUnitOfWorkManagerPort,
    IQueryPort

)

from paperglass.infrastructure.ports import IRelevancyFilterPort

from paperglass.log import getLogger, labels
LOGGER = getLogger(__name__)

DEFAULT_PROMPT = """
    For the GIVEN MEDICATION, can you find the best med match from the MATCH LIST given below. Please follow these instructions:
    1) The name of medication should be present in the "content" field of the MATCH LIST entries. Otherwise say no name match
    2) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength
    3) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form
    4) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route
    5) Otherwise, return "{}" and specific what attributes were not found

    Only return the best match from the list. If no match is found, return "{}"

    GIVEN MEDICATION:
    {SEARCH_TERM}

    MATCH LIST:
"""

class MedispanLLMFilterAdapter(IRelevancyFilterPort):

    @inject
    def __init__(self, prompt: IPromptAdapter, medispan_port:IMedispanPort, query: IQueryPort):
        self.llm = prompt
        self.medispan_port = medispan_port
        self.configuration = None
        self._query = query

    
    @inject
    async def filter(self, search_term: str, medispan_medications: List[MedispanDrug], model:str = MULTIMODAL_MODEL, prompt=DEFAULT_PROMPT, enable_llm: bool = False,max_results=1, metadata={}) -> List[MedispanDrug]:
        if not enable_llm:
            LOGGER.debug("LLM is not enabled. Returning medispan medications.")
            return medispan_medications, {}
        else:
            LOGGER.debug("LLM is enabled")

        context = {}
        results = []

        if medispan_medications:

            med_dict = {}
            slim_meds = []
            for medication in medispan_medications:                
                med = {
                    "id": medication.id,
                    "name": medication.NameDescription
                }
                slim_meds.append(med)
                med_dict[medication.id] = medication

            LOGGER.debug("Number of medispan medications: %s", len(medispan_medications))
            this_prompt = prompt.replace("{SEARCH_TERM}", search_term)

            if MEDISPAN_LLM_OPTIMIZEPROMPT_ENABLED:
                this_prompt = this_prompt + json.dumps(slim_meds, indent=2)
            else:
                this_prompt = this_prompt + json.dumps([x.dict() for x in medispan_medications], indent=2)
            
            context["llm_prompt"] = this_prompt            

            prompt_results = await self.llm.multi_modal_predict_2(
                        items = [this_prompt],
                        response_mime_type = "application/json",
                        model = model,
                        metadata = metadata
                )
            results = []
            if prompt_results:
                medispan_names = [med.NameDescription for med in medispan_medications] if medispan_medications else []
                extra = {
                    "search_term": search_term,
                    "medispan_names": medispan_names,
                    "medispan_count": len(medispan_medications) if medispan_medications else 0
                }
                results = json.loads(prompt_results)
                if results and not isinstance(results, list):
                    if MEDISPAN_LLM_OPTIMIZEPROMPT_ENABLED:
                        results = med_dict[results["id"]] if results else None
                    else:
                        results = MedispanDrug(**json.loads(prompt_results))
                elif isinstance(results, list):
                    LOGGER.warning("Medispan match prompt returned an unexpected list (should be an object): %s", results, extra=extra)
                    results = MedispanDrug(**results[0]) if results else None
                elif not results:                    
                    LOGGER.warning("Medispan match prompt returned empty results: %s", results, extra=extra)
                    results = None                 
                else:
                    LOGGER.warning("Medispan match prompt returned unexpected results: %s", results, extra=extra)
                    results = None

        return results

    @inject
    async def re_rank(self, search_term: str, medispan_medications: List[MedispanDrug], model:str = MULTIMODAL_MODEL, prompt:str = DEFAULT_PROMPT , enable_llm: bool = False,max_results=1, metadata={}) -> Tuple[MedispanDrug, dict]:

        if not enable_llm:
            LOGGER.debug("LLM is not enabled. Returning medispan medications.")
            return medispan_medications

        context = {}
        results = []
        if medispan_medications:
            LOGGER.debug("Performing LLM re-ranking with model %s and prompt %s", model, prompt)
            results:MedispanDrug = await self.filter(search_term, medispan_medications, model=model, prompt=prompt, enable_llm=enable_llm, max_results=max_results, metadata=metadata)

            LOGGER.debug("Medispan llm re_rank prompt returned: %s", results)

            if results:
                LOGGER.debug("Only one result passed the filter.  Floating the best medication to the top of the list")
                context["result_count"] = 1
            else:
                LOGGER.debug("Medispan filter returned no results for search_term: %s", search_term)
                context["result_count"] = 0
            
        else:
            LOGGER.warning("No medispan medications provided for search term: %s", search_term)

        return results, context

    def _sort_results(self, id, medispan_medications: List[MedispanDrug]):
        for med in medispan_medications:
            if med.id == id:
                medispan_medications.remove(med)
                medispan_medications.insert(0, med)
                break
        return medispan_medications

    def _filter_results(self, search_term: str, medispan_medications: List[MedispanDrug]):
        first_token = search_term.split(" ")[0]
        filtered_results = []
        for med in medispan_medications:
            if first_token.lower() in med.NameDescription.lower() or first_token.lower() in med.GenericName.lower():
                filtered_results.append(med)
        return filtered_results
