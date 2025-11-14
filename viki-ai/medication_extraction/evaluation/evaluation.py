import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import sys
from uuid import uuid4
from pydantic import BaseModel

# Add the src directory to the Python path to import modules from there
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from jobs import DocumentJob
from models import Document,OrchestrationPriority,MedispanMatchConfig,Page,ExtractedMedication,MedispanDrug
from google.cloud import firestore

from utils.custom_logger import getLogger
import aiohttp
import csv
LOGGER = getLogger(__name__)

class PageExpectation(BaseModel):
    list_of_medispan_ids:List[str]
    medication:List[ExtractedMedication]
    medispan_matched_count:int
    total_count:int
    unlisted_count:int

class TestCaseEvaluator:
    """
    Class for evaluating test cases from the paperglass_testcases Firestore collection.
    """
    
    def __init__(self):
        """
        Initialize the TestCaseEvaluator with a Firestore client.
        """
        # if not FIRESTORE_EMULATOR_HOST:
        #     self.client = firestore.AsyncClient(database=GCP_FIRESTORE_DB)
        #     self._is_firestore_emulator = False
        # else:
        self.client = firestore.AsyncClient(database=os.getenv("GCP_FIRESTORE_DB"))
        self.is_evaluation_mode_using_alloydb = True
        
        # Reference to the paperglass_testcases collection
        self.testcases_ref = self.client.collection("paperglass_testcases")
        self.documents_ref = self.client.collection("paperglass_documents")
    
    async def get_all_testcases(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all test cases from the paperglass_testcases collection.
        
        Args:
            limit: Optional limit on the number of test cases to retrieve
            
        Returns:
            List of test case documents
        """
        query = self.testcases_ref
        
        if limit:
            query = query.limit(limit)
        
        docs = await query.get()
        return [doc.to_dict() for doc in docs]
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific test document by its ID.
        
        Args:
            document_id: The ID of the document to retrieve
            
        Returns:
            The document data or None if not found
        """
        doc_ref = self.documents_ref.document(document_id)
        doc = await doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        else:
            LOGGER.error(f"Document with ID {document_id} not found.")
            return None
    
    async def extract_medications(self, app_id, patient_id, tenant_id, document_id, storage_uri, priority):
        medications_from_all_pages = []
        
        document_job = DocumentJob()
        
        document = Document(
            app_id=app_id,
            tenant_id=tenant_id,
            patient_id=patient_id,
            document_id=document_id,
            storage_uri=storage_uri,
            priority = OrchestrationPriority.HIGH,
            created_at = datetime.utcnow().isoformat(),
            medispan_adapter_settings= MedispanMatchConfig(v2_enabled_tenants=[],v2_enabled_globally=self.is_evaluation_mode_using_alloydb )
        )
        
        pages:List[Page] = await document_job.split_pages(document, uuid4().hex,None)
        LOGGER.info(f"Splitting document {document_id} into {len(pages)} pages")
        for page in pages:
            LOGGER.info(f"Processing page {page.page_number} with storage URI {page.storage_uri}")
            # Here you would typically call the API for each page
            medications = await document_job.medications(document, page)
            LOGGER.info(f"Extracted medications for page {page.page_number}: {medications}")
            medications = await document_job.medispan_match(document, page)
            LOGGER.info(f"medispan match for page {page.page_number}: {medications}")
            
            medications_from_all_pages.extend(medications)
            
        return medications_from_all_pages
    
    async def get_medications(self, document_job:DocumentJob, document:Document):
        pages:List[Page] = await document_job.split_pages(document, uuid4().hex,None)
        extracted_medications = []
        medispan_results = []
        llm_reranked_medications = []
        
        for page in pages:
            
            medications = await document_job.medications(document, page)
            extracted_medications.extend(medications)
            
            llm_reranked_meds,medispan_meds = await document_job.medispan_match(document, page)
            medispan_results.extend(medispan_meds)
            
            llm_reranked_medications.extend(llm_reranked_meds)
    
        return extracted_medications,medispan_results,llm_reranked_medications

    async def verify(self, medications_from_all_pages, page_expectations:Dict[str, PageExpectation]):
        
        medispan_meds_matched = []
        medispan_meds_unmatched = []
        
        medispan_ignored_medication_value_matched = []
        medispan_ignored_medication_value_unmatched = []
        
        
        # for extracted_medication in medications_from_all_pages:
        #     extracted_medication:ExtractedMedication = extracted_medication
        #     matched_med = [med for med in page_expectations[str(extracted_medication.page_number)].medication if extracted_medication.resolved_medication.matches(med.resolved_medication)]
        #     if matched_med:
        #         #LOGGER.info(f"Matched medication: {matched_med}")
        #         medispan_meds_matched.append(matched_med[0])
        #     else:
        #         #import pdb;pdb.set_trace()
        #         medispan_meds_unmatched.append(extracted_medication)
        #         #LOGGER.info(f"UMatched medication: {extracted_medication}")
                
        #     # match assuming medispan id is ignored
        #     non_medispan_matched_med = [med for med in page_expectations[str(extracted_medication.page_number)].medication if extracted_medication.resolved_medication.match_ignore_medispanid(med.resolved_medication)]
        #     if non_medispan_matched_med:
        #         #LOGGER.info(f"Matched medication: {matched_med}")
        #         medispan_ignored_medication_value_matched.append(non_medispan_matched_med[0])
        #     else:
        #         #import pdb;pdb.set_trace()
        #         medispan_ignored_medication_value_unmatched.append(extracted_medication)
        #         #LOGGER.info(f"UMatched medication: {extracted_medication}")

                
        total_expected_meds = 0
        
        for page_number, page_expectation in page_expectations.items():
            total_expected_meds += 1
            #LOGGER.info(f"Page {page_number} has {page_expectation.total_count} expected medications")
            
        if len(medispan_meds_matched) == total_expected_meds:
            LOGGER.info("All medications matched successfully.")
        else:
            LOGGER.info("Some medications did not match.")
            # LOGGER.info(f"Matched medications: {medispan_meds_matched}")
            # LOGGER.info(f"Unmatched medications: {medispan_meds_unmatched}")
            # LOGGER.info(f"Total expected medications: {total_expected_meds}")
            LOGGER.info(f"Total medispan id matched medications: {len(medispan_meds_matched)}")
            LOGGER.info(f"Total medispan id unmatched medications: {len(medispan_meds_unmatched)}")
        
        if len(medispan_ignored_medication_value_matched) == total_expected_meds:
            LOGGER.info("All medications matched successfully with ignored medispan id.")
        else:
            LOGGER.info("Some medications did not match with ignored medispan id.")
            # LOGGER.info(f"medispan ignored Matched medications: {medispan_ignored_medication_value_matched}")
            # LOGGER.info(f"medispan ignored Unmatched medications: {medispan_ignored_medication_value_unmatched}")
            # LOGGER.info(f"Total expected medications: {total_expected_meds}")
            LOGGER.info(f"Total medispan ignored matched medications: {len(medispan_ignored_medication_value_matched)}")
            LOGGER.info(f"Total medispan ignored unmatched medications: {len(medispan_ignored_medication_value_unmatched)}")
    
        result_headers = ["document_id","page_number","result","extracted_med","extracted_medispan_med","is_listed","expected_medispan_id","unmatched_medispan_id","medispan_matched","medispan_ignored_matched"]
        result_data = []
        for extracted_medication in medications_from_all_pages:
            extracted_medication:ExtractedMedication = extracted_medication
            matched_med = [med for med in page_expectations[str(extracted_medication.page_number)].medication if extracted_medication.resolved_medication.matches(med.resolved_medication)]
            if matched_med:
                #LOGGER.info(f"Matched medication: {matched_med}")
                medispan_matched = matched_med[0]
            else:
                #import pdb;pdb.set_trace()
                medispan_matched = None
                #LOGGER.info(f"UMatched medication: {extracted_medication}")
                
            # match assuming medispan id is ignored
            non_medispan_matched_med = [med for med in page_expectations[str(extracted_medication.page_number)].medication if extracted_medication.resolved_medication.match_ignore_medispanid(med.resolved_medication)]
            if non_medispan_matched_med:
                #LOGGER.info(f"Matched medication: {matched_med}")
                medispan_ignored_matched = non_medispan_matched_med[0]
            else:
                #import pdb;pdb.set_trace()
                medispan_ignored_matched = None
                #LOGGER.info(f"UMatched medication: {extracted_medication}")
                
            result_data.append({
                "document_id": extracted_medication.document_id,
                "page_number": extracted_medication.page_number,
                "result": "SUCCESS" if (extracted_medication.resolved_medication.medispan_id and matched_med) or (not extracted_medication.resolved_medication.medispan_id and medispan_ignored_matched) else "FAILURE",
                "extracted_med": extracted_medication.medication.json(),
                "extracted_medispan_med": extracted_medication.resolved_medication.json() if extracted_medication.resolved_medication.medispan_id else None,
                "is_listed": True if extracted_medication.resolved_medication.medispan_id else False,
                "unmatched_medispan_id": extracted_medication.resolved_medication.medispan_id if extracted_medication.resolved_medication.medispan_id and not medispan_matched else None, 
                "medispan_matched": medispan_matched.json() if medispan_matched else None,
                "medispan_ignored_matched": medispan_ignored_matched.json() if medispan_ignored_matched else None
            })
        LOGGER.info(f"Result data: {result_data}")
            
        await self.write_dict_to_csv(result_data, "evaluation_result.csv", result_headers)
        
    
    async def verify_mini(self,extracted_meds:List[ExtractedMedication],
                        medispan_search_results:List,
                        llm_reranked_meds:List[ExtractedMedication], 
                        page_expectations:Dict[str, PageExpectation]
                    ):
        
        headers = ["document_id","page_number","result",
                "match_type",
                "medispan_search_string",
                "llm_reranked_medispan_id","expected_med_medispan_id","extracted_med_medispan_id",
                "llm_reranked_name","expected_med_name","extracted_med_name",
                "llm_reranked_name_original","expected_med_name_original","extracted_med_name_original",
                "llm_reranked_dosage","expected_med_dosage","extracted_med_dosage",
                "llm_reranked_strength","expected_med_strength","extracted_med_strength",
                "llm_reranked_form","expected_med_form","extracted_med_form",
                "llm_reranked_route","expected_med_route","extracted_med_route",
                "llm_reranked_frequency","expected_med_frequency","extracted_med_frequency",
                "llm_reranked_instructions","expected_med_instructions","extracted_med_instructions",
                "llm_reranked_start_date","expected_med_start_date","extracted_med_start_date",
                "llm_reranked_end_date","expected_med_end_date","extracted_med_end_date",
                "llm_reranked_result","extracted_med_result",
                "extracted_med_result","llm_reranking_result",
                "medispan_search_results"]
        
        results = []
        for llm_reranked_med in llm_reranked_meds:
            result = {}
            
            llm_reranked_med:ExtractedMedication = llm_reranked_med
            
            result = {
                "document_id": llm_reranked_med.document_id,
                "page_number": llm_reranked_med.page_number,
                "llm_reranked_name": llm_reranked_med.resolved_medication.name,
                "llm_reranked_name_original": llm_reranked_med.resolved_medication.name_original,
                "llm_reranked_medispan_id": llm_reranked_med.resolved_medication.medispan_id,
                "llm_reranked_dosage": llm_reranked_med.resolved_medication.dosage,
                "llm_reranked_strength": llm_reranked_med.resolved_medication.strength,
                "llm_reranked_form": llm_reranked_med.resolved_medication.form,
                "llm_reranked_route": llm_reranked_med.resolved_medication.route,
                "llm_reranking_result": llm_reranked_med
            }
            
            matched_med = [med for med in page_expectations[str(llm_reranked_med.page_number)].medication if llm_reranked_med.resolved_medication.matches(med.resolved_medication)]
            
            if matched_med:
                result.update({
                    "result": "SUCCESS",
                    "match_type":"listed_match"  if matched_med[0].resolved_medication.medispan_id else "unlisted_match",
                    "expected_med_name": matched_med[0].resolved_medication.name,
                    "expected_med_name_original": matched_med[0].resolved_medication.name_original,
                    "expected_med_medispan_id": matched_med[0].resolved_medication.medispan_id,
                    "expected_med_dosage": matched_med[0].resolved_medication.dosage,
                    "expected_med_strength": matched_med[0].resolved_medication.strength,
                    "expected_med_form": matched_med[0].resolved_medication.form,
                    "expected_med_route": matched_med[0].resolved_medication.route,
                    "expected_med_frequency": matched_med[0].resolved_medication.frequency,
                    "expected_med_instructions": matched_med[0].resolved_medication.instructions,
                    "expected_med_start_date": matched_med[0].resolved_medication.start_date,
                    "expected_med_end_date": matched_med[0].resolved_medication.end_date,
                    "extracted_med_result": matched_med[0].resolved_medication,
                })
            else:
                # do a non medispan id match
                matched_med = [med for med in page_expectations[str(llm_reranked_med.page_number)].medication if llm_reranked_med.resolved_medication.match_ignore_medispanid(med.resolved_medication)]
                if matched_med:
                    result.update({
                        "result": "PARTIAL_SUCCESS",
                        "match_type":"forced_non_medispan_match",
                        "expected_med_name": matched_med[0].resolved_medication.name,
                        "expected_med_name_original": matched_med[0].resolved_medication.name_original,
                        "expected_med_medispan_id": matched_med[0].resolved_medication.medispan_id,
                        "expected_med_dosage": matched_med[0].resolved_medication.dosage,
                        "expected_med_strength": matched_med[0].resolved_medication.strength,
                        "expected_med_form": matched_med[0].resolved_medication.form,
                        "expected_med_route": matched_med[0].resolved_medication.route,
                        "expected_med_frequency": matched_med[0].resolved_medication.frequency,
                        "expected_med_instructions": matched_med[0].resolved_medication.instructions,
                        "expected_med_start_date": matched_med[0].resolved_medication.start_date,
                        "expected_med_end_date": matched_med[0].resolved_medication.end_date,
                    })
                else:
                    result.update({
                        "result": "FAILURE",
                        "match_type":"no_match",
                        "expected_med_name": None,
                        "expected_med_name_original": None,
                        "expected_med_medispan_id": None,
                        "expected_med_dosage": None,
                        "expected_med_strength": None,
                        "expected_med_form": None,
                        "expected_med_route": None,
                        "expected_med_frequency": None,
                        "expected_med_instructions": None,
                        "expected_med_start_date": None,
                        "expected_med_end_date": None,
                    })
                
            matched_extracted_med = [med for med in extracted_meds if llm_reranked_med.id == med.id]
                
            if matched_extracted_med:
                result.update({
                    "extracted_med_name": matched_extracted_med[0].resolved_medication.name,
                    "extracted_med_name_original": matched_extracted_med[0].resolved_medication.name_original,
                    "extracted_med_medispan_id": matched_extracted_med[0].resolved_medication.medispan_id,
                    "extracted_med_dosage": matched_extracted_med[0].resolved_medication.dosage,
                    "extracted_med_strength": matched_extracted_med[0].resolved_medication.strength,
                    "extracted_med_form": matched_extracted_med[0].resolved_medication.form,
                    "extracted_med_route": matched_extracted_med[0].resolved_medication.route,
                    "extracted_med_frequency": matched_extracted_med[0].resolved_medication.frequency,
                    "extracted_med_instructions": matched_extracted_med[0].resolved_medication.instructions,
                    "extracted_med_start_date": matched_extracted_med[0].resolved_medication.start_date,
                    "extracted_med_end_date": matched_extracted_med[0].resolved_medication.end_date,
                })
                
                medispan_search_result = [res for res in medispan_search_results if res.get("id") == matched_extracted_med[0].id ]
                
                if medispan_search_result:
                    medispan_search_string = medispan_search_result[0].get("medication_name")
                    result.update({
                        "medispan_search_string": medispan_search_string,
                        "medispan_search_results": medispan_search_result[0].get("medispan_options"),
                    })
                    
            results.append(result)
                
        await self.write_dict_to_csv(results, "evaluation_v2_results.csv", headers)
    
    async def write_dict_to_csv(self, data: List[Dict[str, Any]], file_path: str, headers: List[str]):
        """
        Write a list of dictionaries to a CSV file with specified headers.

        Args:
            data: List of dictionaries containing the data to write.
            file_path: Path to the CSV file.
            headers: List of headers for the CSV file.
        """
        try:
            with open(file_path, mode='a+', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            LOGGER.info(f"Data successfully written to {file_path}")
        except Exception as e:
            LOGGER.error(f"Failed to write data to CSV: {e}")

async def main():
    """
    Main function to demonstrate the usage of the TestCaseEvaluator.
    """
    evaluator = TestCaseEvaluator()
    
    # Get all test cases (limited to 10 for demonstration)
    test_cases = await evaluator.get_all_testcases(limit=10)
    LOGGER.info(f"Retrieved {len(test_cases)} test cases")
    
    # Print some information about each test case
    for test_case in test_cases:
        
        document = await evaluator.get_document(test_case.get("test_document_id"))
        document_id= document.get("id")
        patient_id= document.get("patient_id")
        app_id= document.get("app_id")
        tenant_id= document.get("tenant_id")
        storage_uri= document.get("storage_uri")
        priority= document.get("priority")
        
        medications_from_all_pages = await evaluator.extract_medications(
            app_id=app_id,
            patient_id=patient_id,
            tenant_id=tenant_id,
            document_id=document_id,
            storage_uri=storage_uri,
            priority=priority
        )
        #LOGGER.info(f"Extracted medications from all pages: {medications_from_all_pages}")
        # verify the result
        page_expectations = {}
        for page_number in test_case.get("page_expections").keys():
            
            page_expectation = test_case.get("page_expections").get(page_number)
            
            page_expectation_obj = PageExpectation(
                list_of_medispan_ids=page_expectation.get("list_of_medispan_ids"),
                medication=[ExtractedMedication(**med) for med in page_expectation.get("medication")],
                medispan_matched_count=page_expectation.get("medispan_matched_count"),
                total_count=page_expectation.get("total_count"),
                unlisted_count=page_expectation.get("unlisted_count")
            )
            page_expectations[str(page_number)] = page_expectation_obj
        
        await evaluator.verify(medications_from_all_pages, page_expectations)
        
async def main2():
    """
    Main function to demonstrate the usage of the TestCaseEvaluator.
    """
    evaluator = TestCaseEvaluator()
    
    # Get all test cases (limited to 10 for demonstration)
    test_cases = await evaluator.get_all_testcases(limit=10)
    LOGGER.info(f"Retrieved {len(test_cases)} test cases")
    
    storage_uris = []
    # Print some information about each test case
    for test_case in test_cases:
        
        document = await evaluator.get_document(test_case.get("test_document_id"))
        document_id= document.get("id")
        patient_id= document.get("patient_id")
        app_id= document.get("app_id")
        tenant_id= document.get("tenant_id")
        storage_uri= document.get("storage_uri")
        priority= document.get("priority")
        
        document = Document(
            app_id=app_id,
            tenant_id=tenant_id,
            patient_id=patient_id,
            document_id=document_id,
            storage_uri=storage_uri,
            priority = OrchestrationPriority.HIGH,
            created_at = datetime.utcnow().isoformat(),
            medispan_adapter_settings= MedispanMatchConfig(v2_enabled_tenants=[],v2_enabled_globally=True )
        )
        
        storage_uris.append(storage_uri)
        
        document_job = DocumentJob()
        
        extracted_medications,medispan_results,llm_reranked_meds = await evaluator.get_medications(document_job,document)
        
        page_expectations = {}
        for page_number in test_case.get("page_expections").keys():
            
            page_expectation = test_case.get("page_expections").get(page_number)
            
            page_expectation_obj = PageExpectation(
                list_of_medispan_ids=page_expectation.get("list_of_medispan_ids"),
                medication=[ExtractedMedication(**med) for med in page_expectation.get("medication")],
                medispan_matched_count=page_expectation.get("medispan_matched_count"),
                total_count=page_expectation.get("total_count"),
                unlisted_count=page_expectation.get("unlisted_count")
            )
            page_expectations[str(page_number)] = page_expectation_obj
        
        await evaluator.verify_mini(extracted_medications,medispan_results,llm_reranked_meds,page_expectations)
        
    print(storage_uris)
    
if __name__ == "__main__":
    asyncio.run(main2())