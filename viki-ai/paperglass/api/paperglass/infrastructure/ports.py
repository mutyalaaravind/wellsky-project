from contextlib import AbstractAsyncContextManager
from typing import Dict, List, Optional, Tuple, Type, TypeVar, Union, Any
from datetime import datetime

from pydantic import BaseModel

from vertexai.generative_models import Part

from ..usecases.commands import Command
from ..domain.events import Event

from ..domain.models import Aggregate, AppConfig, AppTenantConfig, ClassifiedPage, Document, DocumentMedicationProfile2, DocumentOperation, DocumentOperationDefinition, DocumentOperationInstance, DocumentOperationInstanceLog, ExtractedMedication, MedicalCodingRawData, MedicationProfile, MedispanDrug, Page, PageLabel, PageOperation, EntityRetryConfig, UserEnteredMedicationAggregate, VectorIndex, ConfigurationSettings
from paperglass.domain.model_testing import E2ETestCase, E2ETestCaseSummaryResults, E2ETestCaseResults
from paperglass.domain.model_entities import EntitySchemaAggregate

from ..domain.models_common import Code
from ..domain.values import AnnotationType,ConfigurationTest, DocumentSettings, HostAttachment, HostMedicationAddModel, HostFreeformMedicationAddModel, HostMedication, HostMedicationUpdateModel, OCRType,ImportedMedication, PageText

from ..settings import MULTIMODAL_MODEL

AT = TypeVar('AT', bound=Aggregate)


class IUnitOfWork(AbstractAsyncContextManager):
    """
    Interface to persist entities, events, and commands atomically.
    """

    async def __aenter__(self) -> "IUnitOfWork":
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError
    
    def set_context(self, context: dict):
        raise NotImplementedError
    
    def get_context(self) -> dict:
        raise NotImplementedError

    async def get(self, type: Type[AT], id: str) -> Optional[AT]:
        raise NotImplementedError
    
    async def create_sync(self, agg: Aggregate):
        raise NotImplementedError

    def register_new(self, agg: Aggregate):
        raise NotImplementedError

    def register_dirty(self, agg: Aggregate):
        raise NotImplementedError

    def register_removed(self, agg: Aggregate):
        raise NotImplementedError

    async def start_event_processing(self, event: Event) -> bool:
        """
        Notify persistence about intent to process an event.
        Return false if event was already processed.
        """
        raise NotImplementedError

    def finish_event_processing(self, event: Event):
        """
        Notify persistence about completion of event processing.
        Throw error if event was already processed.
        """
        raise NotImplementedError

    def create_command(self, command: Command):
        """
        Create command for asynchronous processing.
        """
        raise NotImplementedError

    async def start_command_processing(self, command: Command) -> bool:
        """
        Notify persistence about intent to process a command.
        Return false if command was already processed.
        """
        raise NotImplementedError

    def finish_command_processing(self, command: Command):
        """
        Notify persistence about completion of command processing.
        Throw error if command was already processed.
        """
        raise NotImplementedError


class IUnitOfWorkManagerPort:
    """
    Factory for IUnitOfWork instantiation.
    """

    def start(self) -> IUnitOfWork:
        raise NotImplementedError


class IStoragePort:
    async def put_document(self, app_id:str, tenant_id:str, patient_id:str, document_id: str, content: bytes) -> str:
        raise NotImplementedError
    
    async def put_documentoperationinstancelog(self, log:DocumentOperationInstanceLog) -> str:
        raise NotImplementedError
    
    async def list_documentoperationinstancelogs(self, document_id:str, doc_op_instance_id:str) -> List[DocumentOperationInstanceLog]:
        raise NotImplementedError
    
    async def list_documents_json(self, path: str) -> List[dict]:
        raise NotImplementedError
    
    async def put_report(self,content, path:str, file_name:str) -> str:
        raise NotImplementedError

    async def put_report_binary(self, content:bytes, path:str, file_name:str, content_type:str) -> str:
        raise NotImplementedError
    
    async def get_report(self, path, file_name) -> bytes:
        raise NotImplementedError

    async def get_document_raw(self, storage_uri: str) -> bytes:
        raise NotImplementedError

    async def get_document(self, app_id:str, tenant_id:str, patient_id:str, document_id: str) -> bytes:
        raise NotImplementedError

    async def get_document_pdf_url(self, app_id:str, tenant_id:str, patient_id:str,document_id: str) -> str:
        raise NotImplementedError

    async def put_document_page(self, app_id:str, tenant_id:str, patient_id:str, document_id: str, page_number: int, content: bytes) -> str:
        raise NotImplementedError

    async def get_document_page(self, app_id:str, tenant_id:str,patient_id:str, document_id: str, page_number: int) -> bytes:
        raise NotImplementedError

    async def put_page_ocr(self, app_id:str, tenant_id:str, patient_id:str,document_id:str, page_id: str, content: bytes,ocr_type:OCRType) -> str:
        raise NotImplementedError
    
    async def write_text(self, bucket_name: str, path: str, content: str, content_type=None) -> bool:
        raise NotImplementedError

    async def get_page_ocr(self, app_id:str, tenant_id:str, patient_id:str,document_id:str, page_id: str, ocr_type:OCRType) -> bytes:
        raise NotImplementedError

    async def put_page_result(self, type: str, result_id: str, content: bytes) -> str:
        raise NotImplementedError

    async def get_page_result(self, type: str, result_id: str) -> bytes:
        raise NotImplementedError

    async def put_document_page_annotations(
        self, document_id: str, page_result_id: str, annotation_type: str, content: bytes
    ) -> str:
        raise NotImplementedError

    async def get_document_page_annotations(
        self, document_id: str, page_result_id: str, annotation_type: AnnotationType
    ) -> bytes:
        raise NotImplementedError
    
    async def get_object_metadata(self, storage_uri: str
    ) -> Dict[str, Any]:
        raise NotImplementedError

    async def get_external_document_raw(self, storage_uri: str) -> bytes:
        raise NotImplementedError

    async def put_fhir_bundle(self, document_id: str, content: bytes) -> str:
        raise NotImplementedError

    async def get_fhir_bundle(self, document_id) -> bytes:
        raise NotImplementedError

    # async def get_signed_url(self, bucket: str, path: str) -> str:
    #     raise NotImplementedError

class IQueryPort:

    async def list_notes(self) -> List[dict]:
        raise NotImplementedError
    
    async def get_note(self, note_id: str) -> dict:
        raise NotImplementedError
    async def get_app_config(self, app_id: str) -> AppConfig:
        raise NotImplementedError
    
    async def list_app_configs(self, limit: int = 50, offset: int = 0) -> List[AppConfig]:
        raise NotImplementedError
    
    async def get_test_config(self, test_id: str) -> ConfigurationTest:
        raise NotImplementedError
    
    async def get_test_case_golden_dataset(self, no_of_doc) ->  List[dict]:
        raise NotImplementedError
    
    async def list_testcases(self, no_of_doc:int=None) -> List[E2ETestCase]:
        raise NotImplementedError
    
    async def get_testcase_by_id(self, id: str) -> E2ETestCase:
        raise NotImplementedError
    
    async def get_testcase_by_document_id(self, document_id :str) -> E2ETestCase:
        raise NotImplementedError
        
    async def get_testcase_by_name(self, name:str) -> List[E2ETestCase]:
        raise NotImplementedError
    
    async def list_documents_in_test_run(self, run_id: str) -> List[Document]:
        raise NotImplementedError
    
    async def get_testcase_results_summary_latest(self, mode:str):
        raise NotImplementedError
    
    async def get_testcase_results_summary_by_runid(self, run_id: str) -> List[E2ETestCaseSummaryResults]:
        raise NotImplementedError

    async def get_testcase_results_details_by_runid(self, run_id: str) -> List[E2ETestCaseResults]:
        raise NotImplementedError
    
    async def get_testcase_results_details_by_testcase_and_runid(self, run_id: str, testcase_id) -> E2ETestCaseResults:
        raise NotImplementedError
    
    async def get_app_tenant_config(self, app_id: str, tenant_id: str) -> AppTenantConfig:
        raise NotImplementedError

    async def list_documents(self, patient_id: str) -> List[dict]:
        raise NotImplementedError
    
    async def list_documents_count(self, patient_id: str) -> List[dict]:
        raise NotImplementedError
    
    async def list_documents_with_offset(self, patient_id: str, start_at:str, end_at: str, limit:int) -> List[dict]:
        raise NotImplementedError

    async def get_document(self, document_id: str) -> dict:
        raise NotImplementedError

    async def get_document_by_source_storage_uri(self, source_storage_uri: str,tenant_id:str,patient_id:str) -> dict:
        raise NotImplementedError
        
    async def get_document_by_sha256(self, source_sha256: str, tenant_id: str, patient_id: str)-> dict:
        raise NotImplementedError

    async def get_document_by_source_id(self, source_id: str, app_id: str, tenant_id: str, patient_id: str)-> dict:
        raise NotImplementedError

    async def get_document_statuses(self, document_id: str, execution_id:str) -> List[dict]:
        raise NotImplementedError

    async def list_document_events(self, document_id: str) -> List[dict]:
        raise NotImplementedError

    async def delete_document(self, document_id: str) -> None:
        raise NotImplementedError

    async def get_page(self, document_id: str, page_number: int) -> dict:
        raise NotImplementedError
    
    async def get_page_by_id(self,page_id: int) -> dict:
        raise NotImplementedError
    
    async def get_page_by_document_operation_instance_id(self, document_id: str, doc_operation_instance_id: str,page_number: int) -> Page:
        raise NotImplementedError

    async def get_page_result(self, result_id: str) -> bytes:
        raise NotImplementedError

    async def get_page_labels(self, page_id:str) -> Dict[str, str]:
        raise NotImplementedError

    async def get_classified_page(self, page_id: str) -> ClassifiedPage:
        raise NotImplementedError

    async def find_contents_by_label(self, patient_id: str, label: str) -> List[Tuple[str, int, int, str]]:
        raise NotImplementedError

    async def get_contents_by_label(self, page_id: str, label: str) -> List[Tuple[str, int, int, str]]:
        raise NotImplementedError

    # async def get_embeddings_list(self, patient_id: str) -> List[VectorIndex]:
    #     raise NotImplementedError

    # async def get_doc_page_annotations(self, document_id: str) -> List[DocumentAnnotationsAggregate]:
    #     raise NotImplementedError

    async def get_documents_by_created(self, created:str) -> List[Document]:
        raise NotImplementedError

    async def get_medications(self, document_id: str,page_id:str) -> List[dict]:
        raise NotImplementedError

    async def get_active_medications(self, document_id: str,page_number:int) -> List[dict]:
        raise NotImplementedError

    async def get_medications_by_document(self, document_id: str) -> List[dict]:
        raise NotImplementedError

    async def get_extracted_medication(self, id:str) -> ExtractedMedication:
        raise NotImplementedError
    
    async def get_extracted_medications_by_operation_instance_id(self, document_id:str, operation_instance_id:str) -> List[ExtractedMedication]:
        raise NotImplementedError

    async def get_evidences_by_document(self, document_id: str,execution_id:str) -> List[dict]:
        raise NotImplementedError

    async def get_evidences_by_document_operation_instance(self, document_id: str,doc_operation_instance_id:str) -> List[dict]:
        raise NotImplementedError

    async def list_document_medication_profile_by_document(self, document_id: str) -> List[dict]:
        raise NotImplementedError

    async def add_document_medication_profile(self, key: str, command=Command) -> dict:
        raise NotImplementedError

    async def delete_document_medication_profile(self, document_id: str, key: str) -> dict:
        raise NotImplementedError

    async def get_document_medication_profile_by_key(self, key: str) -> List[DocumentMedicationProfile2]:
        raise NotImplementedError

    async def get_document_operation_definition_by_op_type(self, operation_type: str) -> List[DocumentOperationDefinition]:
        raise NotImplementedError

    async def get_document_operation_instances_by_document_id(self, document_id: str, operation_type:str) -> List[DocumentOperation]:
        raise NotImplementedError
    
    async def get_document_operation_instance_log_by_step_id(self, document_id: str, document_operation_instance_id:str, page_number: int, step_id:str) -> DocumentOperationInstanceLog:
        raise NotImplementedError
    
    async def get_document_operation_instance_log_by_id(self, id:str) -> DocumentOperationInstanceLog:
        raise NotImplementedError
    
    async def get_document_operation_instance_by_id(self, id:str) -> DocumentOperationInstance:
        raise NotImplementedError

    async def get_document_operation_instance_logs_by_document_id(self, document_id: str, doc_operation_instance_id:str) -> List[DocumentOperationInstanceLog]:
        raise NotImplementedError

    async def get_document_operation_by_document_id(self, document_id: str,operation_type:str) -> List[DocumentOperationDefinition]:
        raise NotImplementedError
    
    async def get_document_operation_definition_by_id(self, id: str) -> DocumentOperationDefinition:
        raise NotImplementedError

    async def get_medication_profile_by_patient_id(self, patient_id: str) -> MedicationProfile:
        raise NotImplementedError

    async def get_user_entered_medication_by_reconcilled_medication_id(self, reconcilled_medication_id:str) -> UserEnteredMedicationAggregate:
        raise NotImplementedError

    async def get_medispan_by_id(self, medispan_id: str) -> dict:
        raise NotImplementedError

    async def get_configuration(self, key: str) -> ConfigurationSettings:
        raise NotImplementedError
    
    async def get_extracted_clinical_data_by_type_doc_id_and_doc_operation_instance_id(self, type:str, document_id:str, doc_operation_instance_id:str):
        raise NotImplementedError
    
    async def get_extracted_clinical_data_by_id(self, id:str):
        raise NotImplementedError
    
    async def get_extracted_conditions_by_document_operation_instance(self, document_id:str, doc_operation_instance_id:str) -> List[MedicalCodingRawData]:
        raise NotImplementedError
    
    async def get_page_operation(self, page_id: str, document_operation_instance_id:str,extraction_type:PageLabel) -> PageOperation:
        raise NotImplementedError
    
    async def get_all_page_operations(self, document_id:str, document_operation_instance_id:str,extraction_type:PageLabel) -> List[PageOperation]:
        raise NotImplementedError
    
    async def get_page_texts(self, document_id:str, document_operation_instance_id:str) -> List[PageText]:
        raise NotImplementedError
    
    async def get_entity_retry_config(self,entity_id:str, entity_type:str) -> EntityRetryConfig:
        raise NotImplementedError
    
    async def get_documents_by_time_range(self, time_threshold: datetime) -> List[Document]:
        raise NotImplementedError

    async def get_entity_schema_by_id(self, schema_id: str) -> Optional['EntitySchemaAggregate']:
        raise NotImplementedError

    async def get_entity_schema_by_app_id_and_schema_id(self, app_id: str, schema_id: str) -> Optional['EntitySchemaAggregate']:
        raise NotImplementedError

    async def get_entity_schema_by_fqn(self, fqn: str) -> Optional['EntitySchemaAggregate']:
        raise NotImplementedError

    async def get_all_entity_schemas(self, app_id: Optional[str] = None) -> List['EntitySchemaAggregate']:
        raise NotImplementedError

    async def get_document_entity_toc_by_document_id(self, document_id: str) -> List[dict]:
        raise NotImplementedError

    async def get_document_entity_toc_by_document_id_and_run_id(self, document_id: str, run_id: str) -> Optional[dict]:
        raise NotImplementedError

    async def get_entities_by_document_and_entity_type(self, document_id: str, entity_type: str) -> List[dict]:
        raise NotImplementedError


class IDocumentAIAdapter:
    async def process_document(
        self, processor_type: str, storage_uri: str, mime_type: str = 'application/pdf'
    ) -> List[Dict]:
        raise NotImplementedError


class ISearchAdapter:
    async def search(self, identifier: str, search_query: str, serving_config: str) -> List[dict]:
        raise NotImplementedError


class ISearchFHIRAdapter:
    async def search(self, identifier: str, search_query: str, serving_config: str) -> List[dict]:
        raise NotImplementedError


class ISearchIndexer:
    async def index(self, identifier: str, gcs_uri: str, mime_type: str):
        raise NotImplementedError

    async def index_fhir(self):
        raise NotImplementedError


class IEmbeddingsAdapter:
    # @abstractmethod
    # def create_index(self,dimension, metric):
    #     pass
    async def upsert(self, vector_index: VectorIndex):
        raise NotImplementedError

    async def search(allow_list: list[str], search_term: list[str]):
        raise NotImplementedError


class IEmbeddings2Adapter(IEmbeddingsAdapter):
    pass


class IPromptAdapter:

    async def predict(self, prompt_text, model):
        raise NotImplementedError()

    async def multi_modal_predict(
        self, items: List[Union[str, Tuple[bytes, str]]], model="gemini-1.5-flash-001", metadata: Optional[dict] = None
    ):
        raise NotImplementedError()

    async def multi_modal_predict_2(
        self, items: List[Union[str, Part, Tuple[bytes, str]]], model=MULTIMODAL_MODEL, metadata: Optional[dict] = None
    ):
        raise NotImplementedError()

    # async def multi_modal_predict_2(
    #     self, items: List[Union[str, Part, Tuple[bytes, str]]], model=MULTIMODAL_MODEL, metadata: Optional[dict] = None
    # ):
    #     raise NotImplementedError()


class IFhirStoreAdapter:

    def post(self, type, payload):
        raise NotImplementedError()

    def get(self, type, id):
        raise NotImplementedError()

    def put(self, type, id):
        raise NotImplementedError()

    def patch(self, type, id):
        raise NotImplementedError()

    def search(self, type, arguments, count=10, page_token=None):
        raise NotImplementedError()

    def delete(self, type, id):
        raise NotImplementedError()

    def execute_bundle(self, type, entry):
        raise NotImplementedError()

    def build_bundle_entry(self, resource_type, method, payload, condition=None, conditional_url=None, id=None):
        raise NotImplementedError()


class ISettingsPort:

    async def get_document_settings(self, patient_id: str) -> str:
        raise NotImplementedError

    async def save_document_settings(self, settings: DocumentSettings):
        raise NotImplementedError


class ICloudTaskPort:

    async def create_task(self, token,location, service_account_email, queue, url,payload):
        raise NotImplementedError()
    
    async def create_task_v2(self, location, service_account_email, queue, url, payload, http_headers: Dict[str, str] = {}, token:str = None, schedule_time: datetime = None):
        raise NotImplementedError()

class IRelevancyFilterPort:
    async def filter(self, search_term: str, results: List[dict], enable_llm: bool = False, max_results=1, metadata={}) -> List[MedispanDrug]:
        raise NotImplementedError()

    async def re_rank(self, search_term: str, results: List[dict], model: str, prompt: str, enable_llm: bool = False, max_results=1, metadata = {} ) -> Tuple[MedispanDrug, dict]:
        raise NotImplementedError()

class IMedispanPort:
    class Error(Exception):
        pass

    class Drug(BaseModel):
        id: str
        class Strength(BaseModel):
            value: Optional[str] = None
            unit: Optional[str] = None

        class Package(BaseModel):
            size: float
            unit: str
            quantity: Optional[int] = None

        brand_name: str
        generic_name: str
        full_name: Optional[str] = None
        route: Optional[str]
        form: str
        strength: Strength
        package: Optional[Package]
        meta: Optional[Dict] = None
        score: Optional[Dict] = {}

    async def search_medications(self, search_term: str, strict_match:bool) -> List[MedispanDrug]:
        raise NotImplementedError

class IApplicationIntegration:

    async def start(self, integration_project_name, json_payload, trigger_id):
        raise NotImplementedError()

class IHHHAdapter:

    async def get_medications(self,patient_id: str, token:str) -> List[HostMedication]:
        raise NotImplementedError

    async def create_medication(self,  patient_id: str,token: str, user_id:str, medication:HostMedicationAddModel):
        raise NotImplementedError

    async def create_freeform_medication(self,  patient_id: str,token: str, user_id:str, medication:HostFreeformMedicationAddModel):
        raise NotImplementedError

    async def update_medication(self,  patient_id: str,token: str, user_id:str, medication:HostMedicationUpdateModel):
        raise NotImplementedError

    async def delete_medication(self, patient_id: str, token: str, user_id: str, host_medication_id: str):
        raise NotImplementedError

    async def get_attachments(self,  tenant_id:str, patient_id: str, token:str,uploaded_date_cut_off_window_in_days: int) -> List[HostAttachment]:
        raise NotImplementedError
    
    async def get_attachment_metadata(self,  tenant_id:str, file_name:str,external_storage_file:str) -> List[HostAttachment]:
        raise NotImplementedError

    async def get_classifications(self, token: str) -> List[Code]:
        raise NotImplementedError

class IMessagingPort:
    async def publish(
            self,        
            topic: str,
            message: Dict
        ):
        raise NotImplementedError
