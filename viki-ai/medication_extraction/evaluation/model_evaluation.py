import asyncio
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import os
import sys
from pathlib import Path
from uuid import uuid4
import json
import pandas as pd
from pydantic import BaseModel
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

# Add the src directory to the Python path to import modules from there
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from jobs import DocumentJob
from models import (
    Document, OrchestrationPriority, MedispanMatchConfig,
    Page, ExtractedMedication, MedispanDrug, MedispanStatus
)
from prompts import PromptTemplates, ModelVersions
from services.page_service import PageService
from services.medispan_service import MedispanMatchService
from utils.custom_logger import getLogger

# Rest of the code remains the same...
LOGGER = getLogger(__name__)

class PageExpectation(BaseModel):
    list_of_medispan_ids: List[str]
    medication: List[ExtractedMedication]
    medispan_matched_count: int
    total_count: int
    unlisted_count: int

class StepConfig(BaseModel):    
    """Configuration for a single pipeline step"""
    prompt: str
    model: str
    enabled: bool = True

class EvaluationConfig(BaseModel):
    """Configuration for evaluation run"""
    classify: StepConfig
    extract_medications: StepConfig
    medispan_match: StepConfig
    test_case_limit: int = 20
    
    def validate_models(self):
        """Validate model configurations"""
        available_models = ModelVersions.get_available_models()
        for step in [self.classify, self.extract_medications, self.medispan_match]:
            provider = step.model.split('-')[0]  # e.g., 'gemini' from 'gemini-pro'
            if provider not in available_models:
                raise ValueError(f"Unknown model provider: {provider}")
            if step.model not in available_models[provider].values():
                raise ValueError(f"Unknown model: {step.model}")

class StepMetrics(BaseModel):
    """Metrics for a single pipeline step"""
    success_count: int = 0
    error_count: int = 0
    total_count: int = 0
    processing_time: float = 0.0
    errors: List[str] = []

class EvaluationMetrics(BaseModel):
    """Complete metrics for all steps"""
    classify: StepMetrics = StepMetrics()
    extract_medications: StepMetrics = StepMetrics()
    medispan_match: StepMetrics = StepMetrics()
    total_processing_time: float = 0.0

class ModelEvaluator:
    """
    Evaluator for testing different model versions and prompts
    """
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.config.validate_models()
        self.document_job = DocumentJob()
        self.metrics = EvaluationMetrics()
        
        # Initialize Firestore client
        db = os.getenv('GCP_FIRESTORE_DB')
        if not db:
            raise ValueError("GCP_FIRESTORE_DB environment variable not set")
        
        self.client = firestore.AsyncClient(database=db)
        self.testcases_ref = self.client.collection("paperglass_testcases")
        self.documents_ref = self.client.collection("paperglass_documents")

    async def get_all_testcases(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve test cases from Firestore"""
        query = self.testcases_ref
        if limit:
            query = query.limit(limit)
        
        docs = await query.get()
        testcases = [doc.to_dict() for doc in docs]
        
        if not testcases:
            LOGGER.warning("No test cases found in Firestore")
            return []
        
        LOGGER.info(f"Retrieved {len(testcases)} test cases")
        return testcases

    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific test document"""
        doc_ref = self.documents_ref.document(document_id)
        doc = await doc_ref.get()
        
        if not doc.exists:
            LOGGER.error(f"Document with ID {document_id} not found")
            return None
            
        return doc.to_dict()

    async def process_document_with_expectations(self, document: Document, testcase: Dict[str, Any], page_expectations: Dict[str, PageExpectation], model_name: str) -> Dict[str, Any]:
        """Process document and compare against expected results"""
        results = {
            "test_start_date": datetime.utcnow().isoformat(),
            "test_case_id": testcase.get("id"),
            "test_source_document_name": document.storage_uri.split('/')[-1] if document.storage_uri else None,
            "test_source_document_id": testcase.get("test_document_id"),
            "test_source_document_path": document.storage_uri,
            "category": testcase.get("category", "medication"),
            "model_name": model_name,
            "run_id": str(uuid4()),  # Generate unique run ID
            "errors": [],
            "page_results": {}  # All metrics now stored at page level
        }
        
        start_time = datetime.utcnow()
        
        try:
            # Split into pages
            pages: List[Page] = await self.document_job.split_pages(document, uuid4().hex, None)
            
            for page in pages:
                try:

                    # Compare with expected medications
                    page_expectation = page_expectations.get(str(page.page_number))

                    # Medication extraction step
                    if self.config.extract_medications.enabled:
                        step_start = datetime.utcnow()
                        page_service = PageService(document, page)
                        medications = await page_service.medication()
                        self.metrics.extract_medications.total_count += len(medications)
                        self.metrics.extract_medications.success_count += len([m for m in medications if m.medication])
                        step_time = (datetime.utcnow() - step_start).total_seconds()
                        self.metrics.extract_medications.processing_time += step_time
                        
                        # Add medispan matching
                        if self.config.medispan_match.enabled:
                            medispan_step_start = datetime.utcnow()
                            llm_reranked_meds, medispan_results = await page_service.medispan_match()
                            # llm_reranked_meds = []
                            medispan_step_time = (datetime.utcnow() - medispan_step_start).total_seconds()
                            self.metrics.medispan_match.processing_time += medispan_step_time
                            self.metrics.medispan_match.total_count += len(llm_reranked_meds)
                            self.metrics.medispan_match.success_count += len([m for m in llm_reranked_meds if m.resolved_medication])
                    
                    # Calculate page-level metrics
                    extracted_medications = []
                    for med in medications:
                        if med.medication:
                            extracted_medications.append({
                                "name": str(med.medication.name).upper(),
                                "name_original": str(med.medication.name_original).upper(),
                                "medispan_id": str(med.medication.medispan_id).upper(),
                                "dosage": str(med.medication.dosage).upper(),
                                "strength": str(med.medication.strength).upper(),
                                "form": str(med.medication.form).upper(),
                                "route": str(med.medication.route).upper(),
                                "frequency": str(med.medication.frequency).upper(),
                                "instructions": str(med.medication.instructions).upper(),
                                "start_date": str(med.medication.start_date).upper(),
                                "end_date": str(med.medication.end_date).upper(),
                                "discontinued_date": str(med.medication.discontinued_date).upper(),
                                "is_long_standing": str(med.medication.is_long_standing).upper()
                            })
                            
                    page_metrics = {
                        "page_number": page.page_number,
                        "med_match_extract_time": step_time if self.config.extract_medications.enabled else 0,
                        "medspan_extract_time": medispan_step_time if self.config.medispan_match.enabled else 0
                    }

                    
                    if page_expectation:
                        expected_medications = []
                        for med in page_expectation.medication:
                            if med.medication:
                                expected_medications.append({
                                "name": str(med.medication.name).upper(),
                                "name_original": str(med.medication.name_original).upper(),
                                "medispan_id": str(med.medication.medispan_id).upper(),
                                "dosage": str(med.medication.dosage).upper(),
                                "strength": str(med.medication.strength).upper(),
                                "form": str(med.medication.form).upper(),
                                "route": str(med.medication.route).upper(),
                                "frequency": str(med.medication.frequency).upper(),
                                "instructions": str(med.medication.instructions).upper(),
                                "start_date": str(med.medication.start_date).upper(),
                                "end_date": str(med.medication.end_date).upper(),
                                "discontinued_date": str(med.medication.discontinued_date).upper(),
                                "is_long_standing": str(med.medication.is_long_standing).upper()
                            })
                        expected_medispan_ids = []
                        extracted_medispan_ids = []
                        if self.config.medispan_match.enabled:
                            # Track Medispan matching metrics
                            medispan_matches = 0
                            extracted_medispan_ids = []
                            expected_medispan_ids = page_expectation.list_of_medispan_ids

                            for llm_reranked_med in llm_reranked_meds:
                                if llm_reranked_med.resolved_medication.medispan_id:
                                    extracted_id = llm_reranked_med.resolved_medication.medispan_id
                                    extracted_medispan_ids.append(extracted_id)
                            
                            extracted_medispan_ids.sort()
                            expected_medispan_ids.sort()

                        page_metrics["expected_medications"] = expected_medications
                        page_metrics["extracted_medications"] = extracted_medications
                        page_metrics["expected_medispan_ids"] = expected_medispan_ids
                        page_metrics["extracted_medispan_ids"] = extracted_medispan_ids
                        
                    else:
                        # If there are no expectations, mark everything as accurate
                        # since we can't determine correctness
                        field_accuracies = {
                            "name": 1.0,
                            "name_original": 1.0,
                            "medispan_id": 1.0,
                            "dosage": 1.0,
                            "strength": 1.0,
                            "form": 1.0,
                            "route": 1.0,
                            "frequency": 1.0,
                            "instructions": 1.0,
                            "start_date": 1.0,
                            "end_date": 1.0,
                            "discontinued_date": 1.0,
                            "is_long_standing": 1.0
                        }
                        
                        page_metrics.update({})

                    results["page_results"][str(page.page_number)] = page_metrics
                except Exception as e:
                    error_msg = f"Error processing page {page.page_number}: {str(e)}"
                    LOGGER.error(error_msg)
                    results["errors"].append(error_msg)
                    self.metrics.extract_medications.error_count += 1
                    continue
                    
        except Exception as e:
            error_msg = f"Document level error: {str(e)}"
            LOGGER.error(error_msg)
            results["errors"].append(error_msg)
            
        return results

    async def run_evaluation(self, model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Run evaluation on testcases from Firestore"""
        evaluation_results = []
        
        # Get current model name from config if not provided
        if not model_name:
            model_name = self.config.extract_medications.model
            
        # Get testcases
        testcases = await self.get_all_testcases(limit=self.config.test_case_limit)
        LOGGER.info(f"Retrieved {len(testcases)} test cases for model: {model_name}")
        
        for c, testcase in enumerate(testcases):
            LOGGER.info(f"Processing test case {c+1} with model {model_name}")
            try:
                # Get document
                document_data = await self.get_document(testcase.get("test_document_id"))
                if not document_data:
                    LOGGER.error(f"Could not find document for test case {testcase.get('test_document_id')}")
                    continue
                    
                # Create document object
                document = Document(
                    app_id=document_data.get("app_id"),
                    tenant_id=document_data.get("tenant_id"),
                    patient_id=document_data.get("patient_id"),
                    document_id=document_data.get("id"),
                    storage_uri=document_data.get("storage_uri"),
                    priority=OrchestrationPriority.HIGH,
                    created_at=datetime.utcnow().isoformat(),
                    medispan_adapter_settings=MedispanMatchConfig(
                        v2_enabled_tenants=[],
                        v2_enabled_globally=True
                    )
                )
                
                # Get expectations
                page_expectations = {}
                for page_number, page_expectation in testcase.get("page_expections", {}).items():
                    try:
                        page_expectations[str(page_number)] = PageExpectation(
                            list_of_medispan_ids=page_expectation.get("list_of_medispan_ids"),
                            medication=[ExtractedMedication(**med) for med in page_expectation.get("medication")],
                            medispan_matched_count=page_expectation.get("medispan_matched_count"),
                            total_count=page_expectation.get("total_count"),
                            unlisted_count=page_expectation.get("unlisted_count")
                        )
                    except Exception as e:
                        LOGGER.error(f"Error parsing page expectations for page {page_number}: {str(e)}")
                        continue
                
                # Process document with test case info and model name
                result = await self.process_document_with_expectations(
                    document=document,
                    testcase=testcase,
                    page_expectations=page_expectations,
                    model_name=model_name
                )
                evaluation_results.append(result)
                
            except Exception as e:
                LOGGER.error(f"Error processing test case: {str(e)}")
                continue
            
        return evaluation_results

    async def write_results(self, results: List[Dict[str, Any]], output_file: str):
        """Write evaluation results to JSON and Excel files with three sheets: page-wise, full comparison, and Medispan-only comparison."""
        try:
            # Write JSON file as before
            json_file = output_file
            with open(json_file, 'w') as f:
                json.dump(results, f, indent=2)
            LOGGER.info(f"JSON results written to {json_file}")

            excel_file = output_file.replace('.json', '.xlsx')

            # Prepare data for original (long format) sheet
            excel_data = []
            for result in results:
                for page_num, page_result in result['page_results'].items():
                    expected_medications = [i.get('name', '') for i in page_result.get('expected_medications', {})]
                    extracted_medications = [i.get('name', '') for i in page_result.get('extracted_medications', {})]
                    expected_medications.sort()
                    extracted_medications.sort()
                    expected_medispan_ids = page_result.get('expected_medispan_ids', [])
                    extracted_medispan_ids = page_result.get('extracted_medispan_ids', [])
                    expected_medispan_ids.sort()
                    extracted_medispan_ids.sort()
                    row = {
                        'TestStartDate': result.get('test_start_date'),
                        'TestCaseId': result.get('test_case_id'),
                        'TestSourceDocumentPath': result.get('test_source_document_path'),
                        'Category': result.get('category'),
                        'ModelName': result.get('model_name'),
                        'RunId': result.get('run_id'),
                        'Med Match Processing time': page_result.get('med_match_extract_time'),
                        'Medspan Processing time': page_result.get('medspan_extract_time'),
                        'PageNumber': page_result.get('page_number'),
                        'expected_medications': expected_medications,
                        'extracted_medications': extracted_medications,
                        'expected_medispan_ids': expected_medispan_ids,
                        'extracted_medispan_ids': extracted_medispan_ids,
                    }
                    excel_data.append(row)

            if not excel_data:
                LOGGER.warning("No data to write to Excel")
                return

            # --- Write all three sheets ---
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df_long = pd.DataFrame(excel_data)
                df_long.to_excel(writer, index=False, sheet_name='Page-wise Results')

            LOGGER.info(f"Excel results written to {excel_file}")

        except Exception as e:
            LOGGER.error(f"Error writing results: {str(e)}")
            raise


async def main():
    """Run evaluation comparing two models"""
    models_to_test = [
        "gemini-2.5-flash-lite",
        # "gemini-2.5-pro",
        # "gemini-2.5-flash",
        # "gemini-2.0-flash-lite-001",
        # "gemini-1.5-flash-002",
    ]
    
    # Create configs for both models
    configs = {
        model_name: EvaluationConfig(
            classify=StepConfig(
                prompt=PromptTemplates.CLASSIFY,
                model=model_name,
                enabled=False
            ),
            extract_medications=StepConfig(
                prompt=PromptTemplates.EXTRACT_MEDICATIONS,
                model=model_name,
                enabled=True
            ),
            medispan_match=StepConfig(
                prompt=PromptTemplates.MEDISPAN_MATCH,
                model=model_name,
                enabled=False
            )
        ) for model_name in models_to_test
    }
    
    all_results = []
    
    for model_name in models_to_test:
        try:
            LOGGER.info(f"Running evaluation for model: {model_name}")
            evaluator = ModelEvaluator(configs[model_name])
            results = await evaluator.run_evaluation(model_name)
            all_results.extend(results)
        except Exception as e:
            LOGGER.error(f"Evaluation failed for model {model_name}: {str(e)}")
            continue
    try:
        # Write combined results using latest evaluator
        if all_results:
            await evaluator.write_results(all_results, "model_comparison_results.json")
            LOGGER.info("Completed model comparison")
    except Exception as e:
        LOGGER.error(f"Failed to write comparison results: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())