import json
from typing import List
import re
from kink import inject


from paperglass.settings import (
    MEDICATION_EVIDENCE_MATCH_TOKEN_SIZE_THRESHOLD
)

from paperglass.domain.values import (
    Configuration,
    OCRType,    
    Annotation,
)

from paperglass.domain.models import (
    ExtractedMedication,
    Evidences,
    Page,
)

from paperglass.infrastructure.ports import (
    IQueryPort,
    IStoragePort,
)


from paperglass.log import CustomLogger
LOGGER = CustomLogger(__name__)

class EvidenceLinking():
    def __init__(self, config: Configuration):
        self.config = config        
        self.evidence_weak_matching_enabled = config.evidence_weak_matching_enabled
        self.evidence_weak_matching_firsttoken_enabled = config.evidence_weak_matching_firsttoken_enabled

    @inject
    async def get_evidence(self, app_id: str, tenant_id: str, patient_id: str, extracted_medication: ExtractedMedication, query: IQueryPort, storage: IStoragePort)->List[Annotation]:
        if extracted_medication:
            page_raw_ocr = await storage.get_page_ocr(app_id, tenant_id, patient_id, extracted_medication.document_id, extracted_medication.page_id, ocr_type=OCRType.raw)
            page = await query.get_page(extracted_medication.document_id,int(extracted_medication.page_number))
            LOGGER.debug("Page: %s", json.dumps(page, indent=4))
            if page:
                page = Page(**page)
            page_annotations = Page.get_ocr_page_line_annotations(json.loads(page_raw_ocr))

            #LOGGER.debug("Page annotations: %s", json.dumps([x.dict() for x in page_annotations], indent=4), extra=extra)            

            execution_pass = 1
            extracted_medication_name = extracted_medication.medication.name.lower()
            evidences = [x.token().dict() for x in page_annotations if extracted_medication_name in x.token().text.lower().replace('\n', '').rstrip()]            

            extra = {
                "app_id": app_id,
                "tenant_id": tenant_id,
                "patient_id": patient_id,
                "document_id": extracted_medication.document_id,
                "page_number": extracted_medication.page_number,
                "extracted_medication_id": extracted_medication.id,
                "medication_name": extracted_medication_name
            }

            try:
                #Fallback in case where the medication does not match a token specifically in the list of tokens
                if len(evidences) == 0:
                    LOGGER.warning("Pass 1:  No evidence found for extracted medication: %s  Running pass 2...", extracted_medication_name, extra=extra)
                    evidences = await self.evidence_matching_loose(extracted_medication_name, page_annotations)
                    execution_pass += 1

                tokens = []
                if len(evidences) == 0:
                    tokens = extracted_medication_name.split("-")
                    LOGGER.warning("Pass 2:  No evidence found for extracted medication: %s  Tokenizing name and running pass 3...", extracted_medication_name, extra=extra)
                    evidences = await self.evidence_multiterm_matching_loose(tokens, page_annotations)
                    execution_pass += 1

                if len(evidences) == 0 and self.evidence_weak_matching_enabled:
                    cleaned_medication_name = extracted_medication_name.replace(",", "")
                    tokens = cleaned_medication_name.split(" ")                    
                    LOGGER.warning("Pass 3:  No evidence found for tokenized extracted medication: %s  Tokenizing name on ' ' and running pass 4", tokens, extra=extra)
                    evidences = await self.evidence_multiterm_matching_weak(tokens, page_annotations)
                    execution_pass += 1

                if len(evidences) == 0 and self.evidence_weak_matching_firsttoken_enabled:
                    LOGGER.warning("Pass 4:  No evidence found for tokenized extracted medication: %s  Tokenizing name on ' ' and only sending first token running pass 5", tokens, extra=extra)
                    new_tokens = [tokens[0]]
                    evidences = await self.evidence_multiterm_matching_weak(new_tokens, page_annotations)
                    execution_pass += 1

                if len(evidences) == 0:
                    LOGGER.warning("Pass 6:  No evidence found for tokenized extracted medication: %s  No more passes", tokens, extra=extra)
                    execution_pass += 1
                
            except Exception as e:
                LOGGER.error("Exception in additional evidence search for medication '%s': %s", extracted_medication_name, str(e), extra=extra)

            extra["evidence"] = evidences
            extra["execution_pass"] = execution_pass
            if evidences and len(evidences) > 0:
                extra["evidence_count"] = len(evidences)
                LOGGER.debug("EvidenceLinking::get_evidence: Evidence found", extra=extra)
            else:
                extra["evidence_count"] = 0
                LOGGER.debug("EvidenceLinking::get_evidence: Evidence not found", extra=extra)

            return evidences
        
        else:
            return []

    async def evidence_multiterm_matching_loose(self, extracted_medication_names, page_annotations):
        results = []
        for extracted_medication_name in extracted_medication_names:
            results.extend(await self.evidence_matching_loose(extracted_medication_name, page_annotations))

        return results

    # Method that checks if ALL tokens in the search term are present in the page annotation
    async def evidence_multiterm_matching_weak(self, extracted_medication_name_tokens, page_annotations):
        
        results = []
        
        possible_match_db = {}
        idx = 0
        for extracted_medication_name_token in extracted_medication_name_tokens:
            possible_matches = await self.evidence_matching_loose(extracted_medication_name_token, page_annotations)
            for possible_match in possible_matches:
                LOGGER.debug("Possible match for '%s': %s", extracted_medication_name_token, possible_match["text"])
                annotation_text = possible_match['text']
                cleaned_annotation_text = annotation_text.replace(",", "")
                cleanse_list = self.config.evidence_weak_matching_cleansing_regex
                for cl in cleanse_list:
                    cleaned_annotation_text = re.sub(cl, '', cleaned_annotation_text)                

                annotation_tokens = cleaned_annotation_text.lower().split(" ")
                
                LOGGER.debug("Is '%s' in %s?", extracted_medication_name_token, json.dumps(annotation_tokens))
                if extracted_medication_name_token.lower() in annotation_tokens:
                    LOGGER.debug("Let's count this as a hit! %s is in %s", extracted_medication_name_token, json.dumps(annotation_tokens))
                    
                    #Give more weight to the first token in the search term
                    factor = 1
                    if idx == 0:
                        factor = 2

                    if cleaned_annotation_text in possible_match_db:
                            possible_match_db[cleaned_annotation_text]["match_count"] += factor
                    else:
                        possible_match["match_count"] = factor
                        possible_match_db[cleaned_annotation_text] = possible_match
                    
                    LOGGER.debug("Matched token: %s in annotation: %s", extracted_medication_name_token, cleaned_annotation_text)

            idx += 1
                        
        #Sort the values in possible_match_db by match_count in descending order
        sorted_possible_matches = sorted(possible_match_db.values(), key=lambda x: x["match_count"], reverse=True)

        LOGGER.debug("Possible_match_db: %s", json.dumps(possible_match_db, indent=2))
        LOGGER.debug("Sorted possible matches: %s", json.dumps(sorted_possible_matches, indent=2))

        #Cherry pick the best match
        if sorted_possible_matches and len(sorted_possible_matches) > 0:
            results.append(sorted_possible_matches[0])

        return results

    async def evidence_matching_loose(self, extracted_medication_name: str, page_annotations):
        results = []
        LOGGER.debug("Checking medication name: %s", extracted_medication_name)
        tokens = []
        for x in page_annotations:
            token_text:str = x.token().text.lower().replace('\n', '').rstrip()
            tokens.append(token_text)
            if extracted_medication_name in token_text:
                results.append(x.token().dict())
                LOGGER.debug("Found evidence for extracted medication (medicationname in tokentext): %s  token: %s", extracted_medication_name, token_text)
            if token_text in extracted_medication_name and len(token_text) >= MEDICATION_EVIDENCE_MATCH_TOKEN_SIZE_THRESHOLD:
                results.append(x.token().dict())
                LOGGER.debug("Found evidence for extracted medication (inversion: tokentext in medicationname): %s  token: %s", extracted_medication_name, token_text)
        LOGGER.debug("Tokens: %s", tokens)

        return results