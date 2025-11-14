from pydantic import BaseModel, Field # type: ignore
from typing import Any, Dict, List, Literal, Optional, Union
from enum import Enum
from uuid import uuid1
from datetime import datetime
import pandas as pd # type: ignore
from io import BytesIO
import xlsxwriter # type: ignore
import json

from paperglass.settings import (
    VERSION
)
from paperglass.domain.time import now_utc
from paperglass.domain.util_json import JsonUtil
from paperglass.domain.utils.uuid_utils import uuid4
from paperglass.domain.models import Aggregate, AppAggregate, Document, ExtractedMedication, DocumentOperationStatus
from paperglass.domain.values import ReconcilledMedication, AccuracyAssessment

from paperglass.log import getLogger, labels, CustomLogger
LOGGER = CustomLogger(__name__)

# Modern model for E2E testing ---------------------------------------------------------------------
class E2ETestDocumentExpections(BaseModel):
    elapsed_time: int

class E2ETestPageExpections(BaseModel):
    total_count: int
    list_of_medispan_ids: List[str]
    medispan_matched_count: int
    unlisted_count: int
    medication : List[Dict[str, Any]]

class E2ETestCase(AppAggregate):
    category: str
    test_document_id: str
    test_document_name: str
    document_expectations: E2ETestDocumentExpections
    page_expections: dict[int, E2ETestPageExpections]
    active: bool = True

class E2ETestCaseArchive(E2ETestCase):
    archived_date: datetime = Field(default_factory=now_utc)
    pass


class E2ETestCaseResults(AppAggregate):
    mode: str
    run_id: str
    version: Optional[str] = VERSION
    document: Document
    test_case: E2ETestCase
    test_startdate: datetime
    assessment: AccuracyAssessment
    is_overall_passed: bool = False

class E2ETestCaseSummaryResults(AppAggregate):
    id:str = Field(default_factory=lambda: uuid4().hex)
    mode: str
    run_id: str
    version: Optional[str] = VERSION
    status: Optional[DocumentOperationStatus] = DocumentOperationStatus.IN_PROGRESS
    test_startdate: datetime
    is_overall_passed: Optional[bool] = None
    summary: Optional[dict] = {}
    test_cases: Optional[List[E2ETestCase]] = []    
    results: Optional[List[E2ETestCaseResults]] = None
    nbr_of_testcases: Optional[int] = 0
    
    def _get_nbr_of_testcases(self):
        return len(self.test_cases) if self.test_cases else 0
        
    def __init__(self, **data):
        super().__init__(**data)
        self.nbr_of_testcases = self._get_nbr_of_testcases()

    def dict(self, *args, **kwargs):
        self.nbr_of_testcases = self._get_nbr_of_testcases()
        d = super().dict(*args, **kwargs)        
        return d

    def to_xlsx(self) -> bytes:
        # Create a BytesIO buffer to save the Excel file
        output = BytesIO()

        summary_df = self.generate_summary()
        details_df = self.generate_details()
        medications_df = self.generate_medication_details()

        # Create an Excel writer using pandas
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:            
            summary_df.to_excel(writer, sheet_name='Summary', index=False),
            details_df.to_excel(writer, sheet_name='Details', index=False),
            medications_df.to_excel(writer, sheet_name='Medications', index=False)

        # Seek to the beginning of the BytesIO buffer
        output.seek(0)

        # Return the bytes of the Excel file
        return output.getvalue()

    def generate_summary(self):
        # Create a DataFrame for the summary
        summary_data = []
        summary_data.append({
            "Document Name": "Overall",
            "Document ID": "",
            "Category": "",
            "Mode": self.mode,
            "Run ID": self.run_id,
            "Version": self.version,
            "Test Start Date": self.test_startdate.replace(tzinfo=None),
            "Is Overall Passed": self.is_overall_passed
        })

        summary_data.append({
            "Document Name": "",
            "Document ID": "",
            "Category": "",
            "Mode": "",
            "Run ID": "",
            "Version": "",
            "Test Start Date": "",
            "Is Overall Passed": ""
        })

        for result in self.results:
            summary_data.append({
                "Document Name": result.document.file_name,
                "Document ID": result.document.id,                
                "Category": result.test_case.category,
                "Mode": self.mode,
                "Run ID": self.run_id,
                "Version": self.version,
                "Test Start Date": result.test_startdate.replace(tzinfo=None),
                "Is Overall Passed": result.is_overall_passed
            })

        summary_df = pd.DataFrame(summary_data)
        
        return summary_df    
            
    def generate_details(self):
        detail_data=[]
        
        # detail_data.append({
        #         "TestCaseId": "Test Case Id",
        #         "TestSourceDocumentName": "Test Source Document Name",
        #         "TestSourceDocumentId": "Test Source Document Id",
        #         "Category": "Category",
        #         "Mode": "Mode",
        #         "RunId": "Run Id",
        #         "Version": "Version",
        #         "TestStartDate": "Test Start Date",
        #         "PageNumber": "Page Number",
        #         "IsPassed": "Is Passed",
        #         "Accuracy": "Accuracy",
        #         "Recall": "Recall",                
        #         "F1Score": "F1 Score",
        #         "AccurateMedCount": "Accurate Med Count",
        #         "InaccurateMedCount": "Inaccurate Med Count",
        #         "RecalledMedCount": "Recalled Med Count",
        #         "UnRecalledMedCount": "UnRecalled Med Count",
        #         "AccurateMedList": "Accurate Meds List",
        #         "InaccurateMedList": "Inaccurate Meds List",                
        #         "RecalledMedList": "Recalled Meds List",
        #         "UnRecalledMedList": "UnRecalled Meds List",
        #     })
        
        # Of type E2ETestCaseResults
        for document_result in self.results:
            
            base_data = {
                "TestCaseId": document_result.test_case.id,
                "TestSourceDocumentName": document_result.test_case.test_document_name,
                "TestSourceDocumentId": document_result.test_case.test_document_id,
                "Category": document_result.test_case.category,
                "Mode": self.mode,
                "RunId": self.run_id,
                "Version": self.version,
                "TestStartDate": self.test_startdate.replace(tzinfo=None),
            }

            # Create row for overall document assessment
            doc_assessment = document_result.assessment
            doc_data = self._generate_assessment_data(base_data, "Overall", doc_assessment)
            detail_data.append(doc_data)

            # Create row for each page assessment
            page_number = 0
            for page_assessment in doc_assessment.subelement_accuracy_assessments:
                page_number += 1
                page_data = self._generate_assessment_data(base_data, page_number, page_assessment)
                detail_data.append(page_data)

        detail_df = pd.DataFrame(detail_data)
        
        return detail_df 
    
    def generate_medication_details(self):
        detail_data=[]
        
        # detail_data.append({
        #         "TestCaseId": "Test Case Id",
        #         "TestSourceDocumentName": "Test Source Document Name",
        #         "TestSourceDocumentId": "Test Source Document Id",
        #         "Category": "Category",
        #         "Mode": "Mode",
        #         "RunId": "Run Id",
        #         "Version": "Version",
        #         "TestStartDate": "Test Start Date",
        #         "PageNumber": "Page Number",
        #         "Type": "Type",
        #         "MedispanId": "Medispan ID",
        #         "MedicationName": "Medication Name",                                
        #     })
        
        for document_result in self.results:
            
            base_data = {
                "TestCaseId": document_result.test_case.id,
                "TestSourceDocumentName": document_result.test_case.test_document_name,
                "TestSourceDocumentId": document_result.test_case.test_document_id,
                "Category": document_result.test_case.category,
                "Mode": self.mode,
                "RunId": self.run_id,
                "Version": self.version,
                "TestStartDate": self.test_startdate.replace(tzinfo=None),
            }

            doc_assessment = document_result.assessment            

            # Create row for each page assessment
            page_number = 0
            for page_assessment in doc_assessment.subelement_accuracy_assessments:
                page_number += 1

                for item in page_assessment.not_accurate_items:
                    med = ExtractedMedication(**item)
                    item_data = {}
                    item_data.update(base_data)
                    item_data.update({
                        "PageNumber": page_number,
                        "Type": "inaccurate",
                        "MedispanId": med.medication.medispan_id if med.medication.medispan_id else med.medispan_id,
                        "MedicationName": med.medication.fully_qualified_name,
                        "json": JsonUtil.dumps(item),
                    })                    
                    detail_data.append(item_data)

                for item in page_assessment.not_recalled_items:
                    med = ExtractedMedication(**item)
                    item_data = {}
                    item_data.update(base_data)
                    item_data.update({
                        "PageNumber": page_number,
                        "Type": "unrecalled",
                        "MedispanId": med.medication.medispan_id if med.medication.medispan_id else med.medispan_id,
                        "MedicationName": med.medication.fully_qualified_name,
                        "json": JsonUtil.dumps(item),
                    })                    
                    detail_data.append(item_data)

        detail_df = pd.DataFrame(detail_data)
        
        return detail_df
    

    def _generate_assessment_data(self, base_data, page_number, assessment):
        response = {}
        response.update(base_data)

        def extract_meds_as_text(meds: List[ExtractedMedication]) -> str:
            out = []
            for med in meds:
                if isinstance(med, dict):
                    #LOGGER.debug("Extracted medication is a dict: %s", med)
                    med = ExtractedMedication(**med)
                elif isinstance(med, ExtractedMedication):
                    #LOGGER.debug("Extracted medication is an ExtractedMedication: %s", med)
                    pass
                else:
                    LOGGER.error("Could not generate assessment.  Unknown type of med: %s", type(med))
                out.append(med.medication.fully_qualified_name)

            return json.dumps(out, indent=4)

        accurate_item_list = extract_meds_as_text(assessment.accurate_items)
        inaccurate_item_list = extract_meds_as_text(assessment.not_accurate_items)
        recalled_item_list = extract_meds_as_text(assessment.recalled_items)
        unrecalled_item_list = extract_meds_as_text(assessment.not_recalled_items)

        response.update({
            "PageNumber": page_number,
            "IsPassed": assessment.is_pass,
            "Accuracy": assessment.calc_accuracy(),
            "Recall": assessment.calc_recall(),                
            "F1Score": assessment.calc_f1(),            
            "AccurateMedCount": len(assessment.accurate_items),
            "InaccurateMedCount": len(assessment.not_accurate_items),
            "RecalledMedCount": len(assessment.recalled_items),
            "UnRecalledMedCount": len(assessment.not_recalled_items),
            "AccurateMedList": accurate_item_list,
            "InaccurateMedList": inaccurate_item_list,            
            "RecalledMedList": recalled_item_list,
            "UnRecalledMedList": unrecalled_item_list
        })
        return response

# End of modern model for E2E testing ---------------------------------------------------------------------

class TestCaseInputBase(BaseModel):
    pass


class TestCaseInputsOrchestration(TestCaseInputBase):
    document_id: str
    token: str


class TestConditions(BaseModel):
    max_duration_of_test_execution: int
    medispan_matched_count: int
    unlisted_count: int
    total_count: int
    list_of_medispan_ids: List[str]
    minimum_overall_score: Optional[float] = 0.9


class TestCase(AppAggregate):
    name: str
    test_type: str
    input_data: TestCaseInputsOrchestration
    test_conditions: TestConditions


class TestResults(Aggregate):
    test_case: TestCase
    results: Dict[str, Any]

    @classmethod
    def create(cls, app_id: str, tenant_id: str, patient_id: str, test_case: TestCase, results: dict) -> 'TestResults':
        id = uuid1().hex
        instance = cls(
            id=id, app_id=app_id, tenant_id=tenant_id, patient_id=patient_id, test_case=test_case, results=results
        )
        return instance


class TestExpected(BaseModel):
    total_count: int
    list_of_medispan_ids: List[str]
    medispan_matched_count:int
    unlisted_count: int
    medication : List[Dict[str, Any]]

class TestDataDetails(Aggregate):
    id: str
    test_document: Optional[str]
    document_id: str
    active: Optional[bool] = True
    test_expected:Optional[TestExpected]
    
    @classmethod
    def create(
        cls,
        app_id: str,
        tenant_id: str,
        patient_id: str,
        test_document: str,
        document_id: str,
        test_expected: Optional[TestExpected] = None
    ) -> 'TestDataDetails':
        id = uuid1().hex
        instance = cls(
            id=id,
            app_id=app_id,
            tenant_id=tenant_id,
            patient_id=patient_id,
            test_document=test_document,
            document_id=document_id,
            test_expected=test_expected
        )
        return instance


class TestResultStage(BaseModel):
    passed: bool
    errors: List[str]
    metadata: Optional[Dict] = {}


class TestCaseType(str, Enum):
    ORCHESTRATION = "orchestration"
