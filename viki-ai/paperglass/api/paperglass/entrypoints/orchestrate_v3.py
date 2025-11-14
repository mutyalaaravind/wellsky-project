import sys,os
import traceback
import uuid



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import datetime
import time
from typing import Any, List, Dict
from kink import inject
from paperglass.domain.models import AppConfig, AppTenantConfig, ClassifiedPage, Document, DocumentOperation, DocumentOperationDefinition, DocumentOperationInstance, DocumentOperationInstanceLog, DocumentStatus, ExtractedClinicalData, ExtractedMedication, Medication,Page, PageLabel, MedicalCodingRawData
from paperglass.domain.model_toc import PageTOC, DocumentTOC
from paperglass.usecases.configuration import get_config
from paperglass.usecases.commands import (
    ClassifyPage,
    CreateAppConfiguration, 
    CreateDefaultMedicationDocumentOperationDefinition, 
    CreateOrUpdateDocumentOperation, 
    CreateDocumentOperationInstance, 
    CreateDocumentOperationInstanceLog, 
    CreateEvidence, 
    CreatePage, 
    CreateorUpdateMedicationProfile, 
    CreateorUpdateMedicationProfile, 
    ExecuteCustomPrompt,
    ExtractClinicalData, 
    ExtractMedication, 
    ExtractText,
    ExtractTextAndClassify, 
    GetDocument, 
    MedispanMatching,
    PerformOCR, 
    SplitPages, 
    AssembleTOC,
    ExtractConditionsData,
)
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.domain.values import Configuration, DocumentOperationStatus, DocumentOperationStep, DocumentStatusType, PageText, Result
from paperglass.usecases.commands import ClassifyPage, CreateDefaultMedicationDocumentOperationDefinition, CreateOrUpdateDocumentOperation, CreateDocumentOperationInstance, CreateDocumentOperationInstanceLog, CreateEvidence, CreatePage, CreateorUpdateMedicationProfile, ExecuteCustomPrompt, ExtractMedication, ExtractText, GetDocument, PerformOCR, SplitPages, AssembleTOC, NormalizeMedications
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.domain.values import DocumentOperationStatus, DocumentOperationStep, DocumentStatusType, DocumentOperationType
from paperglass.infrastructure.ports import IQueryPort, IStoragePort, IUnitOfWorkManagerPort
from paperglass.usecases.orchestrator import DocumentProcessorAgent
from paperglass.domain.models_common import OrchestrationException
from paperglass.domain.utils.exception_utils import exceptionToMap, getTrimmedStacktraceAsString
from paperglass.usecases.orchestrator import orchestrate

import asyncio
import argparse
import json

from paperglass.settings import STAGE,ORCHESTRATION_MEDICALEXTRACTION_STEP_NORMALIZATION_ENABLED

from paperglass.entrypoints.orchestrate_document_medication_grader import GraderOrchestrationAgent

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

SPAN_BASE: str = "CONTROLLER:orchestrator:"
from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils
from opentelemetry.trace.status import Status, StatusCode
opentelemetry = OpenTelemetryUtils(SPAN_BASE)

CHECK_FOR_NEW_DOCUMENT_INTERVAL_IN_MINS = 30


def get_args():
    parser = argparse.ArgumentParser(description='Orchestrate the extraction of medication data from a document')
    parser.add_argument('--documentId', type=str, help='The document id')
    return parser.parse_args()

@inject()
async def test_extract_step_optimized(document_id:str, page_id: str, page_number:int, query:IQueryPort, command_handler:ICommandHandlingPort):
    document_operation_instance_id = uuid.uuid4().hex
    document_operation_definition_id = uuid.uuid4().hex
    document = Document(**await query.get_document(document_id))
    
    extract_prompt1 = """
    You are expert medical transcriber. 
    Taking each page of the document attached, 
    can you extract comprehensive details with all the text elements on the given page?
    
    Output expected:
    Page: #X
    Comprehensive Details:
    **[section header]**
        [section comprehensive details]
    """
    
    extract_prompt2 = """
    You are expert medical transcriber. 
    Taking each page of the document attached, 
    can you extract comprehensive details with all the text elements on the given page?
    Additionally, please extract medications in <MEDICATIONS> section and conditions in <CONDITIONS> section.
    
    Output expected:
    <EXTRACT>
    Page: #X
    Comprehensive Details:
    **[section header]**
        [section comprehensive details]
    </EXTRACT>
    <MEDICATIONS>
    </MEDICATIONS>
    <CONDITIONS>
    </CONDITIONS>
    """
    classify_prompt = """
    Your are a medical expert. Your job is to extract text from medical documents. Please take a look at this page:
    You must extract all text from the page and label each section with one of the following labels:
    - medications
    - conditions

    Example response:

    ```
    # demographics
    (All text that is related to demographics)

    # medications
    (All text that is related to medications)

    # procedures
    (All text that is related to procedures)

    # medications
    (More text that is related to medications, located elsewhere on the page)
    ```

    RULES:
    1. Each label MUST be preceded by a '#' symbol.
    2. Text MUST be extracted from the page exactly as it appears.
    3. Use ONLY labels that were provided above: do NOT make up new labels.
    4. If a section CANNOT be labeled with any of the provided labels, do NOT include it in the response.

    """
    model = "gemini-1.5-flash-002"
    
    page1:Page= await command_handler.handle_command(ExtractText(app_id=document.app_id, 
                                                                        tenant_id=document.tenant_id,
                                                                        patient_id=document.patient_id,
                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                        document_id=document.id, 
                                                                        page_id=page_id, 
                                                                        page_number=page_number,
                                                                        prompt=extract_prompt1,
                                                                        model = model
                                                                        ))
    
    
    # print(f"page1 : {page1.text}")
    page2:Page= await command_handler.handle_command(ExtractTextAndClassify(app_id=document.app_id, 
                                                                        tenant_id=document.tenant_id,
                                                                        patient_id=document.patient_id,
                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                        document_id=document.id, 
                                                                        page_id=page_id, 
                                                                        page_number=page_number,
                                                                        prompt=extract_prompt2,
                                                                        model = model
                                                                        ))
    # print(f"page2 : {page2.text}")
    print(f"page1 : {page1.text}")
    print(f"page2 : {page2.text}")
    assert page1.text == page2.text, "ExtractText and ExtractTextAndClassify should return same text"
    return True

if __name__ == '__main__':
    args = get_args()
    asyncio.run(orchestrate(document_id=args.documentId,force_new_instance=False))
    # asyncio.run(test_extract_step_optimized(document_id="f7aa2f3aa3b411efada70242ac120004", 
    #                                         page_id="13e1d616a2c111efa0d90242ac120005", 
    #                                         page_number=1)
    #             )