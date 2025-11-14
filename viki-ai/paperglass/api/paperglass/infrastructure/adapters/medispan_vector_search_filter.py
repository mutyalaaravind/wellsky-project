from typing import List
import json

from kink import inject

from paperglass.domain.models import MedispanDrug
from paperglass.settings import (
    MEDISPAN_LLM_SCORING_ENABLED,
    MEDISPAN_TOKEN_BACKOFF,
    MULTIMODAL_MODEL
)

from paperglass.domain.string_utils import remove_parentheses_substrings, contains_paranthetical

from ...domain.values import (
    
    MedicationValue,
    MedispanMedicationValue,
    MedispanStatus,
    Page as PageModel,
)

from paperglass.infrastructure.ports import (
    IMedispanPort,
    IRelevancyFilterPort,
    IPromptAdapter
)

from paperglass.log import getLogger, labels
LOGGER = getLogger(__name__)

PROMPT = """
    For the GIVEN MEDICATION, can you find the best med match from the MATCH LIST given below. Please follow these instructions:
    1) The name of medication should be present in the "content" field of the MATCH LIST entries
    2) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength
    3) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form
    4) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route
    5) Otherwise, return "{}" and specific what attributes were not found 

    GIVEN MEDICATION:
    {SEARCH_TERM}

    MATCH LIST:    
"""

class MedispanVectorSearchFilterAdapter(IRelevancyFilterPort):

    
    @inject
    def __init__(self, medispan_port:IMedispanPort, prompt: IPromptAdapter):        
        self.medispan_port = medispan_port    
        self.prompt = prompt    
    
    @inject
    async def filter(self, search_term: str, medispan_medications: List[MedispanDrug], enable_llm: bool = False, metadata={}) -> List[MedispanDrug]:
        
        if not enable_llm:
            LOGGER.debug("LLM is not enabled. Returning medispan medications.")
            return medispan_medications
        
        results = []
        if medispan_medications:

            LOGGER.debug("Number of medispan medications: %s", len(medispan_medications))
            this_prompt = PROMPT.replace("{SEARCH_TERM}", search_term)
            this_prompt = this_prompt + json.dumps(medispan_medications, indent=2)            
            LOGGER.debug("MedispanVectorSearchFilterAdapter prompt: %s", this_prompt)

            prompt_results = await self.prompt.multi_modal_predict_2( 
                        items = [this_prompt],
                        response_mime_type = "application/json",
                        model = MULTIMODAL_MODEL,
                        metadata = metadata 
                )

            results = json.loads(prompt_results)

            #LOGGER.debug("List of medications before LLM filtering for term '$s': %s", search_term, json.dumps(medispan_medications, indent=2))
            #LOGGER.debug("List of medications after LLM filtering for term '$s': %s", search_term, json.dumps(results, indent=2))

            if not results:
                LOGGER.warning("No prompt results returned for search term: %s  Returning all possible options", search_term)
                results = medispan_medications               
            if not isinstance(results, list):
                LOGGER.debug("Only one result passed the filter.  Floating the best medication to the top of the list")
                med_id = results["id"]
                results = self._sort_results(med_id, medispan_medications)                
            else:
                LOGGER.debug("Returning %s results passed the filter", len(results))
                results

            results = self._sort_results(medispan_medications[0]["id"], results)

        return results

    def _sort_results(self, id, medispan_medications: List[MedispanDrug]):
        for med in medispan_medications:
            if med.id == id:
                medispan_medications.remove(med)
                medispan_medications.insert(0, med)
                break
        return medispan_medications
                