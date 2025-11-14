from typing import List, Tuple
import json

from kink import inject

from paperglass.settings import (
    MEDISPAN_LLM_SCORING_ENABLED,
    MEDISPAN_LLM_SCORING_FOR_USER_ADDED_ENABLED,
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
    IPromptAdapter,
    IMedispanPort,    
)

from paperglass.infrastructure.ports import IRelevancyFilterPort

from paperglass.log import getLogger, labels
LOGGER = getLogger(__name__)

EXTRACTION_PROMPT = """
As an expert healthcare worker, given the first medications, compare the medication with the second list indicating if there is a possible mismatch.  

Each medication contains the medication name, strength, and form.  Medication strength is typically a number followed by either mass or volume units (e.g. 200 MG, 15 ML, etc.)  
Medication form is the packaging form of the medication and includes forms such as tablet, capsule, powder, etc.

Output results in json including the medispan id, name, and a boolean indicating if a mismatch is possible.

Order the results by the best match first.

The output format will be:

[
    {
        "medispan_id": "**The medispan id of the medication",
        "name": "**Name of the medication",
        "possible_mismatch": "**If a mismatch is possible then true, else false.  Output as a boolean value",
        "match_score": "**A decimal value from 0 to 1 as an indicator of how close the match was.  Output as a decimal numeric value"
    }
]
"""

class MedispanAPISearchFilterAdapter(IRelevancyFilterPort):
    
    @inject
    def __init__(self, medispan_port:IMedispanPort):        
        self.medispan_port = medispan_port        
    
    @inject
    async def filter(self, search_term: str, medispan_medications: List[dict], enable_llm: bool = False, metadata={}) -> Tuple[List[dict], dict]:
        context = {}
        results = self.aggregate(search_term, results, metadata=metadata)
        if enable_llm:
            context["llm_enabled"] = "true"
            results = self.llm_filter(search_term, results, metadata=metadata)

        return results, context

    
    async def aggregate(self,search_term: str, medispan_medications: List, enable_llm: bool, prompt, metadata={}) -> List:

        if medispan_medications is None or medispan_medications == []:
            LOGGER.warning("Medispan results for search term '%s' is an empty set", search_term)
            return medispan_medications
        
        LOGGER.debug("Medispan medications: %s", medispan_medications)

        filtered_results = {}

        cnt = 0

        if medispan_medications is None:
            LOGGER.warning("Medispan results for search term '%s' is null", search_term)
            return medispan_medications

        # Aggregation stage
        for medication in medispan_medications:            

            if medication.full_name is not None:
                med_key = medication.full_name.lower()
            else:
                med_key = ""

            if med_key not in filtered_results:
                meta = {                
                    'count': 1,
                    'externalDrugIds': [medication.id],
                }
                medication.meta = meta
                filtered_results[med_key] = medication

            else:
                filtered_medication = filtered_results[med_key]
                filtered_medication.meta['count'] += 1
                filtered_medication.meta['externalDrugIds'].append(medication.id)
                
                if medication.package is None or filtered_medication.package is None:
                    LOGGER.info("Medication: %s is missing package information", medication.full_name)
                else:
                    if medication.package.quantity and filtered_medication.package.quantity:
                        if medication.package.quantity < filtered_medication.package.quantity:
                            medication.meta = filtered_medication.meta
                            filtered_results[med_key] = medication
            
            cnt += 1

        values = list(filtered_results.values())

        # Sort by number of external drug ids (popularity context)
        values.sort(key=lambda x: x.meta['count'], reverse=True)

        # Separate preferred medications based on if the medication starts with the same word as the search term
        if True:
            preferred_values = []
            other_values = []
            search_first_word = search_term.split(" ")[0].lower()

            for value in values:
                if value.brand_name and value.brand_name.lower().startswith(search_first_word):
                    preferred_values.append(value)
                elif value.generic_name and value.generic_name.lower().startswith(search_first_word):
                    preferred_values.append(value)
                else:
                    other_values.append(value)
            values = preferred_values + other_values

            LOGGER.info("Filtered %s medispan results down to %s medications: %s", cnt, len(values), values)
        
        return values


    @inject
    async def llm_filter(search_term: str,  medispan_medications: List, prompt: IPromptAdapter, metadata={}) -> List:
        # TODO: This should be refactored into a separate function that can be chained
        
        LOGGER.debug("MEDISPAN_LLM_SCORING_ENABLED is enabled")

        values_dict_list = []
        values_map = {}

        for value in medispan_medications:
            values_dict_list.append(value.dict())
            values_map[value.id] = value

        prompt_results = await prompt.multi_modal_predict_2( 
                items = [search_term, json.dumps(values_dict_list, indent=2), EXTRACTION_PROMPT],
                response_mime_type = "application/json",
                model = MULTIMODAL_MODEL,
                metadata = metadata              
        )

        scored_results = json.loads(prompt_results)
        LOGGER.info("Prompt results:: %s", json.dumps(scored_results, indent=2))

        sorted_values = []

        for prompt_med in scored_results:
            LOGGER.debug("Prompt med: %s", json.dumps(prompt_med, indent=2))
            medispan_id = prompt_med["medispan_id"]
            medispan = values_map[medispan_id]
            
            if medispan:
                medispan.score = {
                    "overall": prompt_med["match_score"]
                }                
                sorted_values.append(medispan)
                del values_map[medispan_id]

        #Catch any remaining medispan values that were not scored
        for medispan_id, medispan in values_map.items():
            if medispan:
                medispan["score"]["overall"] = 0.0
                sorted_values.append(medispan)

        return sorted_values



