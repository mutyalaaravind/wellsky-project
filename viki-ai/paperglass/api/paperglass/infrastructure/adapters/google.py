import asyncio
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple, Type, Any
from json import loads
from itertools import chain
from functools import partial
from google.auth import compute_engine
import uuid
import random

from google.cloud import firestore, storage  # type: ignore
from google.cloud.firestore_v1.base_query import FieldFilter
from gcloud.aio.storage import Blob, Storage
import google.auth
from google.auth.transport import requests
from paperglass.domain.util_json import DateTimeEncoder
from paperglass.settings import FIRESTORE_EMULATOR_HOST, GCP_FIRESTORE_DB


from ..ports import (
    AT,
    IApplicationIntegration,
    ICloudTaskPort,
    IQueryPort,
    IStoragePort,
    IUnitOfWork,
    IUnitOfWorkManagerPort,
)
from paperglass.domain.values import AnnotationType, EmbeddingChunkingStartegy, EmbeddingStrategy, OCRType, PageText, UserEnteredMedication  # type: ignore
from paperglass.domain.values import AnnotationType, EmbeddingChunkingStartegy, EmbeddingStrategy, OCRType, DocumentOperationType, ConfigurationTest , DocumentOperationStatus  # type: ignore
from ...domain.events import Event
from ...usecases.commands import Command
from paperglass.domain.time import now_utc
from ...domain.models import (
    Aggregate,
    AppConfig,
    AppTenantConfig,
    ClassifiedPage,
    CustomPromptResult,
    ExtractedClinicalData,
    HostAttachmentAggregate,
    Medication,
    Document,
    Document,    
    DocumentMedicationProfile2,
    DocumentOperation,
    DocumentOperationDefinition,
    DocumentOperationInstance,
    DocumentOperationInstanceLog,
    DocumentStatus,
    Evidences,
    ExtractedMedication,
    ExtractedConditions,
    ImportedMedicationAggregate,
    ImportedGeneralMedicationAggregate,
    Medication,
    MedicationProfile,
    # DocumentAnnotations,
    # DocumentAnnotationsAggregate,
    # NamedEntityExtractionAggregate,
    Note,
    Page,
    PageLabel,
    PageOperation,
    EntityRetryConfig,
    UserEnteredMedicationAggregate,
    # PageLBI,
    # PageResult,
    # DocumentStructuredData,
    VectorIndex,
    DocumentMedicationProfile,
    MedispanDrug,
    ConfigurationSettings,
    ExtractedMedicationGrade,
    MedicalCodingRawData,
)
from ...domain.model_entities import EntitySchemaAggregate, EntityAggregate
from ...domain.model_toc import (
    DocumentTOC,
    PageTOCProfile,
    DocumentFilterState,
)
from ...domain.model_entity_toc import (
    DocumentEntityTOC,
)
from ...domain.model_generic_step import (
    GenericPromptStep
)
from paperglass.domain.model_testing import (
    E2ETestCase,
    E2ETestCaseArchive,
    E2ETestCaseSummaryResults,
    E2ETestCaseResults,    
    TestResults, 
    TestCase, 
    TestDataDetails
)
from ...domain.models_common import (
    ReferenceCodes,
    NotFoundException
)

from ...log import getLogger, CustomLogger
LOGGER = getLogger(__name__)
LOGGER2 = CustomLogger(__name__)

#OpenTelemetry instrumentation
from ...domain.utils.opentelemetry_utils import OpenTelemetryUtils


class FirestoreUnitOfWorkManagerAdapter(IUnitOfWorkManagerPort):
    # https://github.com/GoogleCloudPlatform/python-docs-samples/blob/HEAD/firestore/cloud-client/snippets.py
    class FirestoreUnitOfWork(IUnitOfWork):
        def __init__(self, db_name):
            if db_name:
                self.client = firestore.AsyncClient(database=db_name)
            else:
                self.client = firestore.AsyncClient()
            self.transaction = self.client.transaction(max_attempts=1)
            self.notes_ref = self.client.collection("paperglass_notes")
            self.documents_ref = self.client.collection("paperglass_documents")
            self.page_ref = self.client.collection("paperglass_pages")
            self.classified_page_ref = self.client.collection("paperglass_classified_pages")
            self.document_annotations_ref = self.client.collection("paperglass_document_page_annotations")
            self.page_results_ref = self.client.collection("paperglass_page_results")
            self.events_ref = self.client.collection("paperglass_events")
            self.events_processed_ref = self.client.collection("paperglass_events_processed")
            self.commands_ref = self.client.collection("paperglass_commands")
            self.commands_processed_ref = self.client.collection("paperglass_commands_processed")

            self.configurations_ref = self.client.collection("paperglass_configurations")

            self.document_status_ref = self.client.collection("paperglass_document_status")
            
            self.document_operation_definition_ref = self.client.collection("paperglass_document_operation_definition")
            self.document_operation_ref = self.client.collection("paperglass_document_operation")
            self.document_operation_instance_ref = self.client.collection("paperglass_document_operation_instance")
            self.document_operation_instance_log_ref = self.client.collection("paperglass_document_operation_instance_log")

            self.medication_ref = self.client.collection("medications_medications")
            
            self.extracted_medication_ref = self.client.collection("medications_extracted_medications")
            self.extracted_conditions_ref = self.client.collection("conditions_extracted_conditions")
            self.extracted_medication_grades_ref = self.client.collection("medications_extracted_medications_grades")
            self.medication_profile_ref = self.client.collection("medications_medication_profile")
            self.evidences_ref = self.client.collection("medications_evidences")
            
            # deprecated
            self.document_medication_profile = self.client.collection("paperglass_document_medication_profile")

            self.custom_prompt_result_ref = self.client.collection("paperglass_custom_prompt_result")

            self.user_entered_medication_ref = self.client.collection("medications_user_entered_medications")

            self.imported_medication_ref = self.client.collection("medications_imported_medications")
            self.document_toc_ref = self.client.collection("paperglass_document_toc")
            self.document_filter_state_ref = self.client.collection("paperglass_document_filter_state")

            self.document_generic_prompt_step_log = self.client.collection("paperglass_document_generic_prompt_step_log")

            self.user_entered_medication_ref = self.client.collection("medications_user_entered_medications")

            self.host_attachment_ref = self.client.collection("medications_host_attachments")

            self.reference_codes_ref = self.client.collection("paperglass_reference_codes")

            self.testcase_results_summary_ref = self.client.collection("paperglass_testcase_results_summary")
            self.testcase_results_details_ref = self.client.collection("paperglass_testcase_results_details")

            self.app_config_ref = self.client.collection("paperglass_app_config")
            
            self.e2e_testcases_ref = self.client.collection("paperglass_testcases")
            self.e2e_testcases_archive_ref = self.client.collection("paperglass_testcases_archive")
            self.e2e_testcase_results_ref = self.client.collection("paperglass_testcase_results")
            
            #Deprecated
            self.test_config_ref = self.client.collection("paperglass_e2e_test_config")
            self.test_cases_golden_dataset_ref = self.client.collection("paperglass_test_cases_golden_dataset")

            self.app_tenant_config_ref = self.client.collection("paperglass_app_tenant_config")

            self.extracted_clinical_data_ref = self.client.collection("extracted_clinical_data")

            self.medical_coding_raw_data_ref = self.client.collection("paperglass_coding")
            self.page_operation_ref = self.client.collection("paperglass_page_operation")
            
            self.retry_ref = self.client.collection("paperglass_retry")
            self.entity_schema_ref = self.client.collection("paperglass_entity_schemas")

            self.collections = {
                Note: self.notes_ref,
                Document: self.documents_ref,
                Page: self.page_ref,
                ClassifiedPage: self.classified_page_ref,
                Medication: self.medication_ref,
                DocumentStatus: self.document_status_ref,
                DocumentOperationDefinition: self.document_operation_definition_ref,
                DocumentOperation: self.document_operation_ref,
                DocumentOperationInstance: self.document_operation_instance_ref,
                DocumentOperationInstanceLog: self.document_operation_instance_log_ref,
                Evidences: self.evidences_ref,
                DocumentMedicationProfile2: self.document_medication_profile,
                ExtractedMedication: self.extracted_medication_ref,
                ExtractedConditions: self.extracted_conditions_ref,
                MedicationProfile: self.medication_profile_ref,
                CustomPromptResult: self.custom_prompt_result_ref,
                UserEnteredMedicationAggregate: self.user_entered_medication_ref,
                ImportedMedicationAggregate: self.imported_medication_ref,

                ConfigurationSettings: self.configurations_ref,

                DocumentTOC: self.document_toc_ref,

                GenericPromptStep: self.document_generic_prompt_step_log,

                UserEnteredMedicationAggregate: self.user_entered_medication_ref,
                ImportedGeneralMedicationAggregate: self.imported_medication_ref,

                DocumentFilterState: self.document_filter_state_ref,
                HostAttachmentAggregate: self.host_attachment_ref,

                ReferenceCodes: self.reference_codes_ref,

                E2ETestCase: self.e2e_testcases_ref,
                E2ETestCaseArchive: self.e2e_testcases_archive_ref,
                E2ETestCaseSummaryResults: self.testcase_results_summary_ref,
                E2ETestCaseResults: self.testcase_results_details_ref,

                #TestResults: self.testcase_results_ref,
                ExtractedMedicationGrade: self.extracted_medication_grades_ref,

                AppConfig: self.app_config_ref,
                ConfigurationTest: self.test_config_ref,
                TestDataDetails: self.test_cases_golden_dataset_ref,
                AppTenantConfig: self.app_tenant_config_ref,

                ExtractedClinicalData: self.extracted_clinical_data_ref,

                MedicalCodingRawData: self.medical_coding_raw_data_ref,
                PageOperation: self.page_operation_ref,
                
                EntityRetryConfig: self.retry_ref,
                EntitySchemaAggregate: self.entity_schema_ref
            }
            self.new = []
            self.dirty = []
            self.removed = []

            self.SPAN_BASE: str = "INFRA:FirestoreUnitOfWork:"
            self.opentelemetry = OpenTelemetryUtils(self.SPAN_BASE)

            self._context = {}
            
            self.is_anything_changed = False

        async def __aenter__(self):
            with await self.opentelemetry.getSpan("Transaction start") as span:
                extra = self._collect_extra()
                LOGGER2.debug("FirestoreUnitOfWork::__aenter__ Transaction begin", extra=extra)
                await self.transaction._begin()
                self.start_time = now_utc()
                return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            
            with await self.opentelemetry.getSpan("Transaction commit") as span:
                extra = self._collect_extra()

                elapsed_time_mid = now_utc()
                if not exc_type:
                    
                    for aggregate in chain(self.new, self.dirty, self.removed):
                        agg_ref = self._ref(aggregate)
                        agg_name = aggregate.__class__.__name__
                        while aggregate.events:
                            event = aggregate.events.pop(0)
                            classname = event.__class__.__name__
                            ctx = {
                                "aggregate_name": agg_name,
                                "operation": "event",
                                "event": classname
                            }
                            ctx.update(extra)
                            LOGGER2.debug("FirestoreUnitOfWork::__aexit__ saving event %s", classname, extra=ctx)
                            self._save_event(agg_ref, event)
                            
                    for agg in self.new:
                        ctx = extra.copy()
                        classname = agg.__class__.__name__
                        ctx["operation"] = "create"
                        ctx["aggregate"] = classname
                        try:
                            ctx["aggregateId"] = agg.id                  
                        except Exception as e:
                            pass
                        ctx["collection"] = self._collection_name(agg)
                        LOGGER2.debug("FirestoreUnitOfWork::__aexit__ creating aggregate %s", classname, extra=ctx)
                        self.transaction.create(self._ref(agg), self._serialize(agg))
                    for agg in self.dirty:
                        ctx = extra.copy()
                        classname = agg.__class__.__name__
                        ctx["operation"] = "update"
                        ctx["aggregate"] = classname
                        try:
                            ctx["aggregateId"] = agg.id                  
                        except Exception as e:
                            pass
                        ctx["collection"] = self._collection_name(agg)
                        LOGGER2.debug("FirestoreUnitOfWork::__aexit__ updating aggregate %s", classname, extra=ctx)
                        self.transaction.update(self._ref(agg), self._serialize(agg))                    
                    for agg in self.removed:
                        ctx = extra.copy()
                        classname = agg.__class__.__name__
                        ctx["operation"] = "delete"
                        ctx["aggregate"] = classname
                        try:
                            ctx["aggregateId"] = agg.id                  
                        except Exception as e:
                            pass
                        ctx["collection"] = self._collection_name(agg)
                        LOGGER2.debug("FirestoreUnitOfWork::__aexit__ deleting aggregate %s", classname, extra=ctx)
                        self.transaction.delete(self._ref(agg))
                    try:
                        elapsed_time = now_utc() - self.start_time
                        elapsed_time_mid = now_utc() - elapsed_time_mid
                        extra["txnElapsedTimeMid"] = elapsed_time_mid.total_seconds()
                        extra["txnElapsedTime"] = elapsed_time.total_seconds()
                        
                        if self.is_anything_changed:
                            await self.transaction._commit()
                            LOGGER2.info("FirestoreUnitOfWork::__aexit__ commit complete", extra=extra)
                        else:
                            LOGGER2.info("FirestoreUnitOfWork::__aexit__ no changes to commit", extra=extra)
                    except Exception as e:
                        extra["excType"] = str(e.__class__.__name__)
                        extra["excValue"] = str(e)
                        if 'Too much contention' in str(e):
                            LOGGER2.error("FirestoreUnitOfWork::__aexit__ error: Too much contention error in commit for new: %s, update: %s. Error: %s",self.new,self.dirty, e, extra=extra)
                        else:
                            LOGGER2.error("FirestoreUnitOfWork::__aexit__ error: Error in commit: %s", e, extra=extra)
                        raise e
                else:
                    with await self.opentelemetry.getSpan("Transaction Rollback") as span:
                        await self.transaction._rollback()
                        extra["excType"] = str(exc_type.__class__.__name__)
                        extra["excValue"] = str(exc_value)
                        LOGGER2.warning("FirestoreUnitOfWork::__aexit__ rollback", extra=extra)

        def _collect_extra(self):
            news = [x.__class__.__name__ for x in self.new]
            dirties = [x.__class__.__name__ for x in self.dirty]
            deletes = [x.__class__.__name__ for x in self.removed]
            extra = {
                "txnId": str(uuid.uuid4()),
                "txnCreateCount": len(self.new) if self.new else 0,
                "txnNew": news,                
                "txnUpdateCount": len(self.dirty) if self.dirty else 0,
                "txnUpdate": dirties,
                "txnDeleteCount": len(self.removed) if self.removed else 0,
                "txnDelete": deletes,
                "txnEventCount": sum(len(agg.events) for agg in chain(self.new, self.dirty, self.removed))
            }
            this_context = self.get_context()
            if this_context:
                extra.update(this_context)            
            
            return extra

        def _serialize(self, agg: Aggregate):
            return loads(agg.json(exclude={"events": True}))

        def _ref(self, agg: Aggregate):
            # Handle EntityAggregate with dynamic collection names
            if isinstance(agg, EntityAggregate):
                collection_name = agg.get_collection_name()
                return self.client.collection(collection_name).document(agg.id)
            # Handle DocumentEntityTOC with subcollection under document
            if isinstance(agg, DocumentEntityTOC):
                return self.documents_ref.document(agg.document_id).collection("entity_toc").document(agg.id)
            return self.collections[type(agg)].document(agg.id)  # type: ignore
        
        def _collection_name(self, agg: Aggregate):
            # Handle EntityAggregate with dynamic collection names
            if isinstance(agg, EntityAggregate):
                return agg.get_collection_name()
            # Handle DocumentEntityTOC with subcollection under document
            if isinstance(agg, DocumentEntityTOC):
                return f"paperglass_documents/{agg.document_id}/entity_toc"
            return self.collections[type(agg)].id
        
        def set_context(self, context: Dict):
            self._context = context

        def get_context(self) -> Dict:
            return self._context if self._context else {}

        async def get(self, type: Type[AT], id: str) -> Optional[AT]:  # type: ignore
            ref = self.collections[type].document(id)
            doc = await ref.get(transaction=self.transaction)
            if doc.exists:
                self.is_anything_changed = True
                return type.parse_obj(doc.to_dict())
            return None

        async def create_sync(self, agg: Aggregate):
            with await self.opentelemetry.getSpan("Create sync") as span:
                LOGGER2.debug("UOW create_sync: %s", agg, extra=self._collect_extra())
                if agg is None:
                    raise Exception("Aggregation object is null!!!")
                agg_ref = self._ref(agg)            
                await agg_ref.set(self._serialize(agg))

        def register_new(self, agg: Aggregate):
            self.is_anything_changed = True
            self.new.append(agg)

        def register_dirty(self, agg: Aggregate):
            self.is_anything_changed = True
            self.dirty.append(agg)            

        def register_removed(self, agg: Aggregate):
            self.is_anything_changed = True
            self.removed.append(agg)

        def register_archived(self, agg: AppConfig):
            """Archive an AppConfig to its subcollection"""
            self.is_anything_changed = True
            # Create archive document in subcollection: paperglass_app_config/{config_id}/archive/{timestamp_id}
            # Note: We use the config's UUID id as the parent document ID
            app_config_doc_ref = self.app_config_ref.document(agg.id)
            archive_subcollection_ref = app_config_doc_ref.collection("archive")
            # Use a timestamp-based ID for the archive to allow multiple archived versions
            archive_doc_id = f"{now_utc().isoformat()}_{agg.id}"
            archive_doc_ref = archive_subcollection_ref.document(archive_doc_id)
            
            # Create archive data with additional metadata
            archive_data = agg.dict()
            archive_data["archived_date"] = now_utc()
            archive_data["archived_by"] = agg.modified_by
            
            # Add to transaction
            self.transaction.create(archive_doc_ref, archive_data)

        async def start_event_processing(self, event: Event) -> bool:
            ref = self.events_processed_ref.document(event.id)
            doc = await ref.get(transaction=self.transaction)
            return not doc.exists

        def finish_event_processing(self, event: Event):
            ref = self.events_processed_ref.document(event.id)
            self.transaction.create(ref, loads(event.json(encoder=lambda o: '<not serializable>')))
            self.is_anything_changed = True

        def create_command(self, command: Command):
            ref = self.commands_ref.document(command.id)
            self.transaction.create(ref, command.dict())

        async def start_command_processing(self, command: Command) -> bool:
            ref = self.commands_processed_ref.document(command.id)
            doc = await ref.get(transaction=self.transaction)
            return not doc.exists

        def finish_command_processing(self, command: Command):
            ref = self.commands_processed_ref.document(command.id)
            self.transaction.create(ref, loads(command.json(encoder=lambda o: '<not serializable>')))
            self.is_anything_changed = True

        def _save_event(self, agg_ref: firestore.DocumentReference, event: Event):
            LOGGER.debug("Saving event %s", event)
            data = loads(event.json())
            # Save to event collection
            self.transaction.create(self.events_ref.document(event.id), data)
            # Save to aggregate event subcollection
            self.transaction.create(agg_ref.collection("events").document(event.id), data)
            

    def start(self) -> FirestoreUnitOfWork:
        if not FIRESTORE_EMULATOR_HOST:
            return self.FirestoreUnitOfWork(db_name = GCP_FIRESTORE_DB)
        return self.FirestoreUnitOfWork(db_name=None)

class FirestoreQueryAdapter(IQueryPort):
    def __init__(self, db_name):
        if not FIRESTORE_EMULATOR_HOST:
            self.client = firestore.AsyncClient(database=db_name)
            self._is_firestore_emulator = False
        else:
            self.client = firestore.AsyncClient()
            self._is_firestore_emulator = True
        self.configurations_ref = self.client.collection("paperglass_configurations")
        self.notes_ref = self.client.collection('paperglass_notes')
        self.documents_ref = self.client.collection('paperglass_documents')
        self.pages_ref = self.client.collection('paperglass_pages')
        self.classified_pages_ref = self.client.collection('paperglass_classified_pages')
        self.document_statuses_ref = self.client.collection("paperglass_document_status")
        self.document_medication_profile = self.client.collection("paperglass_document_medication_profile")
        self.extracted_medication_ref = self.client.collection("medications_medications")
        self.evidences_ref = self.client.collection("medications_evidences")
        self.extracted_medication_v2_ref = self.client.collection("medications_extracted_medications")
        self.extracted_conditions_v2_ref = self.client.collection("conditions_extracted_conditions")
        self.extracted_medication_grades_ref = self.client.collection("medications_extracted_medications_grades")
        self.document_operation_definition_ref = self.client.collection("paperglass_document_operation_definition")
        self.document_operation_ref = self.client.collection("paperglass_document_operation")
        self.medication_profile_ref = self.client.collection("medications_medication_profile")
        self.user_entered_medication_ref = self.client.collection("medications_user_entered_medications")
        self.document_operation_definition_ref = self.client.collection("paperglass_document_operation_definition")
        self.document_operation_ref = self.client.collection("paperglass_document_operation")
        self.document_operation_instance = self.client.collection("paperglass_document_operation_instance")
        self.document_operation_instance_log = self.client.collection("paperglass_document_operation_instance_log")
        self.medication_profile_ref = self.client.collection("medications_medication_profile")
        self.document_toc_ref = self.client.collection("paperglass_document_toc")
        self.medispan_medication_ref = self.client.collection("medispan_meds")
        self.app_config_ref = self.client.collection("paperglass_app_config")
        
        self.testcase_results_summary_ref = self.client.collection("paperglass_testcase_results_summary")
        self.testcase_results_details_ref = self.client.collection("paperglass_testcase_results_details")

        self.e2e_testcases_ref = self.client.collection("paperglass_testcases")
        self.test_config_ref = self.client.collection("paperglass_e2e_test_config")
        self.test_cases_golden_dataset_ref = self.client.collection("paperglass_test_cases_golden_dataset")
        self.app_tenant_config_ref = self.client.collection("paperglass_app_tenant_config")
        self.extracted_clinical_data_ref = self.client.collection("extracted_clinical_data")
        self.extracted_conditions_ref = self.client.collection("paperglass_coding")
        self.page_operation_ref = self.client.collection("paperglass_page_operation")
        self.retry_ref = self.client.collection("paperglass_retry")
        self.SPAN_BASE: str = "INFRA:FirestoreQueryAdapter:"
        self.opentelemetry = OpenTelemetryUtils(self.SPAN_BASE)
    
    async def list_notes(self) -> List[dict]:
        # query = (
        #     self.authorizations_ref.order_by('updated_at', direction=firestore.Query.DESCENDING)
        #     .limit(limit)
        #     .offset(offset)
        # )
        query = self.notes_ref
        # if before_date:
        #     query = query.start_after({'updated_at': before_date})
        return [doc.to_dict() for doc in await query.get()]

    async def get_configuration(self, key: str) -> ConfigurationSettings:
        ref = await self.configurations_ref.where("code", "==" ,key)
        doc = await ref.get()
        return ConfigurationSettings(**doc.to_dict())
    
    async def get_app_config(self, app_id: str) -> AppConfig:
        LOGGER.debug("Is firestore emulator: %s", self._is_firestore_emulator)
        ref = self.app_config_ref.where("app_id", "==" ,app_id).where("active","==",True)
        docs = await ref.get()
        if docs:
            return sorted([AppConfig(**doc.to_dict()) for doc in docs], key=lambda x: x.created_at, reverse=True)[0]
        return None
    
    async def list_app_configs(self, limit: int = 50, offset: int = 0) -> List[AppConfig]:
        LOGGER.debug("Listing app configs with limit: %s, offset: %s", limit, offset)
        LOGGER.debug("Is firestore emulator: %s", self._is_firestore_emulator)
        ref = self.app_config_ref.where("active", "==", True).order_by("created_at", direction="DESCENDING").limit(limit).offset(offset)
        docs = await ref.get()
        if docs:
            app_configs = [AppConfig(**doc.to_dict()) for doc in docs]
            LOGGER.debug("Found %s app configs", len(app_configs))
            return app_configs
        LOGGER.debug("No app configs found")
        return []
    
    #Deprecated
    async def get_test_config(self, test_id: str) -> ConfigurationTest:
        ref = self.test_config_ref.where("test_type", "==" ,test_id)
        docs = await ref.get()
        if docs:
            LOGGER2.debug("Test cases found: %s", len(docs))
            return [doc.to_dict() for doc in docs]
        LOGGER2.debug("Error in fetching test cases")
        return None
    
    async def list_testcases(self, no_of_doc:int=None) -> List[E2ETestCase]:
        ref = self.e2e_testcases_ref.where("active", "==" ,True)
        docs = await ref.get()

        if not docs:
            raise NotFoundException("Test cases not found")

        if no_of_doc == None:
            LOGGER2.debug("Test cases found: %s  Returning all testcases", len(docs))        
            return [E2ETestCase(**doc.to_dict()) for doc in docs]
        else:
            LOGGER2.debug("Test cases found: %s  Sampling %s docs", len(docs), no_of_doc)
            random_docs = random.sample(docs, min(no_of_doc, len(docs)))
            return [E2ETestCase(**doc.to_dict()) for doc in random_docs]
        
    async def get_testcase_by_id(self, id: str) -> E2ETestCase:
        ref = self.e2e_testcases_ref.document(id)
        doc = await ref.get()

        if not doc.exists:
            raise NotFoundException("Test case not found")

        return E2ETestCase(**doc.to_dict())

    async def get_testcase_by_document_id(self, document_id :str) -> E2ETestCase:
        ref = self.e2e_testcases_ref.where("test_document_id", "==", document_id).where("active", "==" ,True)
        docs = await ref.get()

        if not docs:
            raise NotFoundException("Test case not found")

        return [E2ETestCase(**doc.to_dict()) for doc in docs][0]

    async def get_testcase_by_name(self, name:str) -> List[E2ETestCase]:
        ref = self.e2e_testcases_ref.where("test_document_name", "==", name).where("active", "==" ,True)
        docs = await ref.get()

        if not docs:
            raise NotFoundException("Test cases not found")

        return [E2ETestCase(**doc.to_dict()) for doc in docs]
    
    async def list_documents_in_test_run(self, run_id: str) -> List[Document]:
        ref = self.documents_ref.where("metadata.e2e_test.testrun_id", "==" , run_id)
        docs = await ref.get()
        return [Document(**doc.to_dict()) for doc in docs]

    async def get_testcase_results_summary_latest(self, mode:str):
        ref = self.testcase_results_summary_ref.where("mode", "==", mode).where("status", "==", "COMPLETED").order_by("created_at", direction=firestore.Query.DESCENDING).limit(1)
        docs = await ref.get()
        if docs:
            LOGGER2.debug("Latest test case found: %s", len(docs))
            return [E2ETestCaseSummaryResults(**doc.to_dict()) for doc in docs]
        
        LOGGER2.debug("No latest testcase summary results found for mode %s", mode)
        return []

    async def get_testcase_results_summary_by_runid(self, run_id: str) -> List[E2ETestCaseSummaryResults]:
        ref = self.testcase_results_summary_ref.where("run_id", "==" ,run_id)
        docs = await ref.get()
        if docs:
            LOGGER2.debug("Test cases found: %s", len(docs))
            return [E2ETestCaseSummaryResults(**doc.to_dict()) for doc in docs]
        
        LOGGER2.debug("No testcase summary results found for runid %s", run_id)
        return []

    async def get_testcase_results_details_by_runid(self, run_id: str) -> List[E2ETestCaseResults]:
        ref = self.testcase_results_details_ref.where("run_id", "==" ,run_id)
        docs = await ref.get()
        if docs:
            LOGGER2.debug("Test cases found: %s", len(docs))
            return [E2ETestCaseResults(**doc.to_dict()) for doc in docs]
        
        LOGGER2.debug("No testcase results found for runid %s", run_id)
        return []

    async def get_testcase_results_details_by_testcase_and_runid(self, run_id: str, testcase_id) -> E2ETestCaseResults:
        ref = self.testcase_results_details_ref.where("run_id", "==" ,run_id).where("testcase.id", "==" ,testcase_id)
        docs = await ref.get()
        if docs:
            LOGGER2.debug("Test cases found: %s", len(docs))
            return [E2ETestCaseResults(**doc.to_dict()) for doc in docs][0]
        
        LOGGER2.debug("No testcase results found for runid %s and testcase %s", run_id, testcase_id)
        return None


    # Deprecated
    async def get_test_case_golden_dataset(self, no_of_doc:int) -> List[dict]:
        ref = self.test_cases_golden_dataset_ref.where("active", "==" ,True)
        docs = await ref.get()
        if docs:
            LOGGER2.debug("Test cases found: %s", len(docs))
            random_docs = random.sample(docs, min(no_of_doc, len(docs)))
            return [doc.to_dict() for doc in random_docs]
        LOGGER2.debug("Error in fetching test cases")
        return None
    

    async def get_test_case_golden_dataset_by_doc_id(self, document_id:str) -> TestDataDetails:
        ref = self.test_cases_golden_dataset_ref.where("active", "==" ,True).where("document_id", "==" ,document_id)
        docs = await ref.get()
        if docs:
            LOGGER2.debug("Test cases found: %s", len(docs))
            return [doc.to_dict() for doc in docs]
        LOGGER2.debug("Error in fetching test cases")
        return None
    
    async def get_app_tenant_config(self, app_id: str, tenant_id: str) -> AppTenantConfig:
        ref = self.app_tenant_config_ref.where("app_id", "==" ,app_id).where("tenant_id", "==" ,tenant_id).where("active","==",True)
        docs = await ref.get()
        if docs:
            return sorted([AppTenantConfig(**doc.to_dict()) for doc in docs], key=lambda x: x.created_at, reverse=True)[0]    
        return None
    
    async def get_note(self, note_id: str) -> dict:
        return (await self.notes_ref.document(note_id).get()).to_dict()

    async def list_documents(self, patient_id: str) -> List[dict]:
        #LOGGER.debug("List documents for patient %s", patient_id)
        query = self.documents_ref.order_by('created_at', direction=firestore.Query.DESCENDING)
        docs = await query.where('patient_id', '==', patient_id).where('active','==',True).get()
        return [doc.to_dict() for doc in docs]
    
    async def list_documents_count(self, patient_id: str) -> int:
        query = self.documents_ref.order_by('created_at', direction=firestore.Query.DESCENDING)
        aggregation_result = await query.where('patient_id', '==', patient_id).where('active','==',True).count().get()
        return aggregation_result[0][0].value
    
    async def list_documents_with_offset(self, patient_id: str, start_at: str,end_at:str, limit: int) -> List[dict]:
        query = self.documents_ref.order_by('created_at', direction=firestore.Query.DESCENDING)
        if start_at:
            docs = await query.where('patient_id', '==', patient_id).where('active','==',True).start_at({"created_at": start_at}).limit(limit).get()
        if end_at:
            docs = await query.where('patient_id', '==', patient_id).where('active','==',True).start_after({"created_at": end_at}).limit_to_last(limit).get() 
        return [doc.to_dict() for doc in docs]

    async def list_document_events(self, document_id: str) -> List[dict]:
        query = self.documents_ref.document(document_id).collection('events').order_by('created')
        events = await query.get()
        return [doc.to_dict() for doc in events]

    async def get_document(self, document_id: str) -> dict:
        ref = self.documents_ref.document(document_id)
        doc = await ref.get()
        return doc.to_dict()
    
    async def get_document_by_source_storage_uri(self, source_storage_uri: str,tenant_id:str,patient_id:str) -> dict:
        ref = self.documents_ref.where("source_storage_uri","==",source_storage_uri).where("tenant_id","==",tenant_id).where("patient_id","==",patient_id).where('active','==',True)
        docs = await ref.get()
        docs = [doc.to_dict() for doc in docs]
        return docs[0] if docs else None
    
    async def get_document_by_sha256(self, source_sha256: str, tenant_id: str, patient_id: str)-> dict:
        ref = self.documents_ref.where(filter=FieldFilter("source_sha256","==", source_sha256))
        ref = ref.where(filter=FieldFilter("tenant_id","==",tenant_id))
        ref = ref.where(filter=FieldFilter("patient_id","==",patient_id))
        ref = ref.where(filter=FieldFilter('active','==',True))
        docs = await ref.get()
        docs = [doc.to_dict() for doc in docs]
        return docs[0] if docs else None
    
    async def get_document_by_source_id(self, source_id: str, app_id: str, tenant_id: str, patient_id: str)-> dict:
        ref = self.documents_ref.where(filter=FieldFilter("source_id","==", source_id))
        ref = ref.where(filter=FieldFilter("app_id","==",app_id))
        ref = ref.where(filter=FieldFilter("tenant_id","==",tenant_id))
        ref = ref.where(filter=FieldFilter("patient_id","==",patient_id))
        ref = ref.where(filter=FieldFilter("active","==",True))
        docs = await ref.get()
        docs = [doc.to_dict() for doc in docs]
        return docs[0] if docs else None
 
    async def get_page(self, document_id: str, page_number: int) -> dict:
        query = self.pages_ref.order_by('created_at', direction=firestore.Query.DESCENDING)
        pages = await query.where('document_id', '==', document_id).where('number','==',page_number).get()
        return pages[0].to_dict() if pages else None
    
    async def get_page_by_id(self,page_id: int) -> dict:
        pages = await self.pages_ref.where('id', '==', page_id).get()
        return pages[0].to_dict() if pages else None
    
    async def delete_document(self, document_id: str) -> dict:
        ref = self.documents_ref.document(document_id)
        doc = await ref.update({'active': False})
        return doc.to_dict()

    async def get_page_result(self, result_id: str) -> dict:
        ref = self.page_results_ref.document(result_id)
        doc = await ref.get()
        return doc.to_dict()

    async def get_page_labels(self, page_id:str) -> Dict[str, str]:
        doc =  await self.classified_pages_ref.where('page_id', '==', page_id).get()
        return doc[0].to_dict().get("labels") if doc else []
    
    async def get_page_by_document_operation_instance_id(self, document_id: str, doc_operation_instance_id: str, page_number: int) -> Page:
        query = self.pages_ref.where('document_id', '==', document_id).where('document_operation_instance_id','==',doc_operation_instance_id).where("number","==",page_number)
        docs = await query.get()
        if docs:
            pages = [Page(**doc.to_dict()) for doc in docs]
            pages = sorted(pages, key=lambda x: x.created_at, reverse=True)
            return pages[0]
        return None
    
    async def get_classified_page(self, page_id: str) -> ClassifiedPage:
        docs = await self.classified_pages_ref.where('page_id', '==', page_id).get()
        return [ClassifiedPage(**doc.to_dict()) for doc in docs][0] if docs else None
        
    async def get_contents_by_label(self, page_id: str, labels: List[str]) -> List[Tuple[str, int, int, str]]:
        query = self.classified_pages_ref.where('page_id', '==', page_id).where('labels', 'array_contains_any', labels)
        docs = [doc.to_dict() for doc in await query.get()]
        labelled_contents = []
        for doc in docs:
            labelled_contents.extend([x.get("medications") for x in doc.get("labels")])
        return labelled_contents

    async def find_contents_by_label(self, patient_id: str, label: str) -> List[Tuple[str, int, int, str]]:
        query = self.page_lbis_ref.where('patient_id', '==', patient_id).where('labels', 'array_contains', label)
        docs = [doc.to_dict() for doc in await query.get()]
        return [
            (
                doc['document_id'],
                doc['chunk_index'],
                doc['relative_page_number'],
                doc['contents'][doc['labels'].index(label)],
            )
            for doc in docs
        ]
    
    async def get_documents_by_created(self, created:str) -> List[Document]:
        query = self.documents_ref.where('created_at', '>', created)
        docs = [Document(**doc.to_dict()) for doc in await query.get()]
        return docs
    
    async def get_medications(self, document_id: str,page_id:str) -> List[dict]:
        query = self.extracted_medication_ref.where('document_id', '==', document_id).where('page_id','==',page_id)
        docs = [doc.to_dict() for doc in await query.get()]
        return docs
    
    async def get_active_medications(self, document_id: str,page_number:int) -> List[dict]:
        query = self.extracted_medication_ref.where('document_id', '==', document_id).where('active','==',True)
        docs = [doc.to_dict() for doc in await query.get()]
        docs = [doc for doc in docs if doc.get("page_number") == page_number]
        return docs
    
    async def get_medications_by_document(self, document_id: str) -> List[dict]:
        query = self.extracted_medication_ref.where('document_id', '==', document_id).where('active','==',True)
        docs = [doc.to_dict() for doc in await query.get()]
        return docs
    
    #legacy
    async def get_document_statuses(self, document_id: str, execution_id:str) -> List[dict]:
        query = self.document_statuses_ref.where('document_id','==',document_id).where('execution_id','==',execution_id)
        docs = [doc.to_dict() for doc in await query.get()]
        return docs
    
    async def get_evidences_by_document(self, document_id: str,execution_id:str) -> List[dict]:
        query = self.evidences_ref.where('document_id', '==', document_id).where('execution_id','==',execution_id)
        docs = [doc.to_dict() for doc in await query.get()]
        return docs

    # Methods for managing Document TOC
    async def get_document_toc(self, document_id: str) -> Dict[str, List[PageTOCProfile]]:
        thisSpanName = "get_document_toc"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            #Get the DocumentOperation pointer for this document for the active version       
            doc_op: DocumentOperation = await self.get_document_operation_by_document_id(document_id, DocumentOperationType.TOC.value)
            if doc_op is None:
                raise NotFoundException("Document Operation " + DocumentOperationType.TOC.value+ " not found for Document ID: " + document_id)            
                    
            LOGGER.debug("Document Operation: %s", doc_op)        

            # Get the current toc for document
            query = self.document_toc_ref.where('document_id', '==', document_id).where('document_operation_instance_id','==',doc_op.active_document_operation_instance_id)
            docs = [doc.to_dict() for doc in await query.get()]
            LOGGER.debug("Document TOC: %s", docs)

            doc = docs[0] if docs else []

            return doc
    
    async def get_documents_by_time_range(self, time_threshold: datetime) -> List[Document]:
        thisSpanName = "get_documents_by_time_range"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            try:
                time_threshold_str = time_threshold.isoformat()
                query = self.documents_ref.where('created_at', '>', time_threshold_str)
                docs = await query.get()
                documents = [Document(**doc.to_dict()) for doc in docs if doc.to_dict().get('active', True)]
                documents.sort(key=lambda x: x.created_at, reverse=True)
                not_completed = []
                for doc in documents:
                    doc_ops = await self.document_operation_instance.where("document_id", "==", doc.id).get()
                    doc_ops = [doc_op.to_dict() for doc_op in doc_ops]
                    
                    if not doc_ops:
                        not_completed.append(doc)
                        continue    
                    else:    
                        for doc_op in doc_ops:
                            if doc_op.get("status") == DocumentOperationStatus.IN_PROGRESS.value:
                                not_completed.append(doc)
                                break
                return not_completed
            except Exception as e:
                LOGGER2.error("Error in get_documents_by_time_range", extra={
                    "error": str(e),
                    "time_threshold": time_threshold.isoformat()
                })
                raise       
    async def get_evidences_by_document_operation_instance(self, document_id: str,doc_operation_instance_id:str) -> List[dict]:
        thisSpanName = "get_evidences_by_document_operation_instance"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            query = self.evidences_ref.where('document_id', '==', document_id).where('document_operation_instance_id','==',doc_operation_instance_id)
            docs = [doc.to_dict() for doc in await query.get()]
            return docs[0] if docs else None
    
    # TODO:  This should be in the usecase layer and not in the query layer.  REFACTOR
    async def get_document_pageprofiles_by_document_id(self, document_id: str, profile_type: str) -> Dict[str, List[PageTOCProfile]]:
        thisSpanName = "get_document_pageprofiles_by_document_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            toc = await self.get_document_toc(document_id)

            if toc is None:
                return None

            LOGGER.debug("TOC: %s", toc)
            print(toc)

            pageProfiles = toc.get("pageProfiles")

            filteredPageProfiles = {}
            for page, profiles in pageProfiles.items():

                for profile in profiles:
                    LOGGER.debug("Profile: %s", profile)
                    if profile["type"] == profile_type:
                        filteredPageProfiles[page] = profile

            return filteredPageProfiles


    # Methods for managing Document Medication Profile ------------------------------------------------------------------------------------------------------
    async def list_document_medication_profile_by_document(self, document_id: str) -> List[dict]:
        thisSpanName = "list_document_medication_profile_by_document"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            query = self.document_medication_profile.where('document_id', '==', document_id).where('active','==',True)
            docs = [doc.to_dict() for doc in await query.get()]
            return docs
    
    async def add_document_medication_profile(self, key: str, medication_profile:DocumentMedicationProfile) -> DocumentMedicationProfile:
        thisSpanName = "add_document_medication_profile"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.document_medication_profile.document(key)
            await ref.set(medication_profile.dict())
            return medication_profile

    async def delete_document_medication_profile(self, document_id: str, key: str) -> dict:
        thisSpanName = "delete_document_medication_profile"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.documents_ref.document(key)
            doc = await ref.update({'active': False})
            return doc.to_dict()
    
    async def get_document_medication_profile_by_key(self, key: str) -> List[DocumentMedicationProfile2]:
        thisSpanName = "get_document_medication_profile_by_key"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.document_medication_profile.where('key','==',key)
            docs = await ref.get()
            return [DocumentMedicationProfile2(**doc.to_dict()) for doc in docs][0] if docs else None

    async def get_document_operation_definition_by_op_type(self, operation_type: str) -> List[DocumentOperationDefinition]:
        thisSpanName = "get_document_operation_definition_by_op_type"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.document_operation_definition_ref.where('operation_type','==',operation_type)
            docs = await ref.get()
            doc_op_definitions = [DocumentOperationDefinition(**doc.to_dict()) for doc in docs]
            return [x for x in doc_op_definitions if not x.disabled] if doc_op_definitions else []
        
    async def get_document_operation_definition_by_id(self, id: str) -> DocumentOperationDefinition:
        thisSpanName = "get_document_operation_definition_by_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.document_operation_definition_ref.document(id)
            doc = await ref.get()
            return DocumentOperationDefinition(**doc.to_dict()) if doc.exists else None

    async def get_document_operation_by_document_id(self, document_id: str, operation_type:str) -> List[DocumentOperation]:
        thisSpanName = "get_document_operation_by_document_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.document_operation_ref.where('document_id','==',document_id).where('operation_type','==',operation_type)
            docs = await ref.get()
            doc_operations= [DocumentOperation(**doc.to_dict()) for doc in docs]
            return doc_operations[0] if doc_operations else None
    
    async def get_document_operation_instances_by_document_id(self, document_id: str, operation_definition_id:str) -> List[DocumentOperationInstance]:
        thisSpanName = "get_document_operation_instances_by_document_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            #LOGGER.debug("Begining retrieval of document operation instance")
            ref = self.document_operation_instance.where('document_id','==',document_id).where('document_operation_definition_id','==',operation_definition_id)
            docs = await ref.get()
            doc_operations= [DocumentOperationInstance(**doc.to_dict()) for doc in docs]
            return doc_operations if doc_operations else None
    
    async def get_document_operation_instance_by_id(self, id:str) -> DocumentOperationInstance:
        thisSpanName = "get_document_operation_instance_by_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            #LOGGER.debug("Begining retrieval of document operation instance")
            ref = self.document_operation_instance.document(id)
            doc = await ref.get()
            if doc.exists:
                return DocumentOperationInstance(**doc.to_dict()) if doc else None
            return None
    
    async def get_document_operation_instance_logs_by_document_id(self, document_id: str, doc_operation_instance_id:str) -> List[DocumentOperationInstanceLog]:
        LOGGER.debug("get_document_operation_instance_logs_by_document_id %s %s", document_id, doc_operation_instance_id)
        thisSpanName = "get_document_operation_instance_logs_by_document_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.document_operation_instance_log.where('document_id','==',document_id).where('document_operation_instance_id','==',doc_operation_instance_id)
            docs = await ref.get()
            doc_operation_instance_logs= [DocumentOperationInstanceLog(**doc.to_dict()) for doc in docs]
            doc_operation_instance_logs.sort(key=lambda x: x.created_at, reverse=True) if doc_operation_instance_logs else None
            return doc_operation_instance_logs
    
    async def get_document_operation_instance_log_by_step_id(self, document_id: str, document_operation_instance_id:str, page_number: int, step_id:str) -> DocumentOperationInstanceLog:
        LOGGER.debug("get_document_operation_instance_logs_by_step_id %s %s %s %s", document_id, document_operation_instance_id, str(page_number), step_id)
        thisSpanName = "get_document_operation_instance_logs_by_step_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.document_operation_instance_log.where('document_id','==',document_id).where('document_operation_instance_id','==',document_operation_instance_id).where("step_id","==",step_id).where("page_number","==",page_number)
            docs = await ref.get()
            if docs:
                doc_operation_instance_logs= [DocumentOperationInstanceLog(**doc.to_dict()) for doc in docs]
                doc_operation_instance_logs.sort(key=lambda x: x.created_at, reverse=True) if doc_operation_instance_logs else None
                return doc_operation_instance_logs[0]
        return None
    

    async def get_document_operation_instance_log_by_step_id_and_status(self, document_id: str, status: str, step_id:str) -> DocumentOperationInstanceLog:
        thisSpanName = "get_document_operation_instance_logs_by_document_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.document_operation_instance_log.where('document_id','==',document_id).where("step_id","==",step_id).where("status","==",status)
            docs = await ref.get()
            if docs:
                doc_operation_instance_logs= [DocumentOperationInstanceLog(**doc.to_dict()) for doc in docs]
                doc_operation_instance_logs.sort(key=lambda x: x.created_at, reverse=True) if doc_operation_instance_logs else None
                return doc_operation_instance_logs[0]
        return None
    
    async def get_document_operation_instance_log_by_id(self, id:str) -> DocumentOperationInstanceLog:
        LOGGER.debug("get_document_operation_instance_logs_by_id %s", id)
        thisSpanName = "get_document_operation_instance_log_by_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.document_operation_instance_log.document(id)
            doc = await ref.get()
            if doc.exists:
                return DocumentOperationInstanceLog(**doc.to_dict())
        return None

    async def get_medication_profile_by_patient_id(self, patient_id: str) -> MedicationProfile:
        thisSpanName = "get_medication_profile_by_patient_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span: 
            ref = self.medication_profile_ref.where('patient_id','==',patient_id)
            docs = await ref.get()
            medication_profiles = [MedicationProfile(**doc.to_dict()) for doc in docs]
            # in case there are duplicate medication profiles. we filter by making sure the one with medications is returned
            medication_profiles = list(filter(lambda x:x.medications is not None, medication_profiles))
            return medication_profiles[0] if medication_profiles else None
    
    async def get_extracted_medication(self, id:str) -> ExtractedMedication:
        thisSpanName = "get_extracted_medication"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.extracted_medication_v2_ref.document(id)
            doc = await ref.get()
            if doc.exists:
                return ExtractedMedication(**doc.to_dict()) if doc else None
        
    async def get_extracted_condition(self, id:str) -> ExtractedConditions:
        thisSpanName = "get_extracted_condition"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.extracted_conditions_v2_ref.document(id)
            doc = await ref.get()
            if doc.exists:
                return ExtractedConditions(**doc.to_dict()) if doc else None

    async def get_extracted_medication_grades(self, document_id: str) -> ExtractedMedicationGrade:
        with await self.opentelemetry.getSpan("get_extracted_medication_grades") as span:

            doc_op: DocumentOperation = await self.get_document_operation_by_document_id(document_id, DocumentOperationType.MEDICATION_GRADER.value)
            document_operation_instance_id = doc_op.active_document_operation_instance_id

            ref = self.extracted_medication_grades_ref.where('document_id','==',document_id).where("document_operation_instance_id","==",document_operation_instance_id)
            docs = await ref.get()
            return [ExtractedMedicationGrade(**x.to_dict()) for x in docs] if docs else None
            
    async def get_extracted_medication_grade_by_document_operation_instance(self, extracted_medication_id: str, document_operation_instance_id: str) -> ExtractedMedicationGrade:
        with await self.opentelemetry.getSpan("get_extracted_medication_grade") as span:
            ref = self.extracted_medication_grades_ref.where('extracted_medication_id','==',extracted_medication_id).where("document_operation_instance_id","==",document_operation_instance_id)
            docs = await ref.get()
            return ExtractedMedicationGrade(**docs[0].to_dict()) if docs else None    
    
    async def get_extracted_medications_by_operation_instance_id(self, document_id:str, operation_instance_id:str) -> List[ExtractedMedication]:
        thisSpanName = "get_extracted_medication"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.extracted_medication_v2_ref.where("document_id",'==',document_id).where('document_operation_instance_id','==',operation_instance_id)
            docs = await ref.get()
            
            medications= [ExtractedMedication(**doc.to_dict()) for doc in docs]
            
            # rare occasion when the same medication is extracted multiple times on the same page
            # this happens in extract medication step is called multiple times for same doc_operation_instance_id
            # below code removes the duplicates and returns unique medications
            unique_medications = []
            for medication in medications:
                if len([x for x in unique_medications if x.resolved_medication.matches(medication.resolved_medication) and x.page_number == medication.page_number]) == 0:
                    unique_medications.append(medication)
            return unique_medications
        
    async def get_extracted_conditions_by_operation_instance_id(self, document_id:str, operation_instance_id:str) -> List[ExtractedConditions]:
        thisSpanName = "get_extracted_conditions"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.extracted_conditions_v2_ref.where("document_id",'==',document_id).where('document_operation_instance_id','==',operation_instance_id)
            docs = await ref.get()
            
            conditions= [ExtractedConditions(**doc.to_dict()) for doc in docs]
            
            # rare occasion when the same medication is extracted multiple times on the same page
            # this happens in extract medication step is called multiple times for same doc_operation_instance_id
            # below code removes the duplicates and returns unique medications
            unique_conditions = []
            for condition in conditions:
                unique_conditions.append(condition)
            return unique_conditions    
        
    async def get_user_entered_medication_by_reconcilled_medication_id(self, reconcilled_medication_id:str) -> UserEnteredMedicationAggregate:
        thisSpanName = "get_user_entered_medication_by_reconcilled_medication_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            ref = self.user_entered_medication_ref.where('medication_profile_reconcilled_medication_id','==',reconcilled_medication_id)
            docs = await ref.get()  

            # TODO CRITICAL:  This is a hack to handle the fact that the change_sets field is not being deserialized correctly SOMEWHERE is creating this as an object not an array
            userEnteredMedicationAggregate: UserEnteredMedicationAggregate = None                       
            if docs:
                for doc in docs:
                    LOGGER.debug("get_user_entered_medication_by_reconcilled_medication_id %s: %s", reconcilled_medication_id, doc.to_dict())          
                    doc_dict = doc.to_dict()
                    if doc_dict["change_sets"] and not isinstance(doc_dict["change_sets"], list):
                        doc_dict["change_sets"] = [doc_dict["change_sets"]]
                        LOGGER.debug("doc.change_set is not a list.  Converting to list: %s", doc_dict)

                    userEnteredMedicationAggregate = UserEnteredMedicationAggregate(**doc_dict)
                    break

            return userEnteredMedicationAggregate
        
    async def get_medispan_by_id(self, medispan_id:str) -> MedispanDrug: 
        with await self.opentelemetry.getSpan("get_medispan_by_id") as span:   
            query = self.medispan_medication_ref.where('ExternalDrugId', '==', medispan_id)            
            docs = [doc.to_dict() for doc in await query.get()]                        
            return docs[0] if docs else None
        
    async def get_extracted_clinical_data_by_type_doc_id_and_doc_operation_instance_id(self, type:str, 
                                                                                       document_id:str, 
                                                                                       doc_operation_instance_id:str):
        query = self.extracted_clinical_data_ref.where("document_id","==",document_id).where("document_operation_instance_id","==", doc_operation_instance_id).where("clinical_data_type","==",type)
        return [ExtractedClinicalData(**doc.to_dict()) for doc in await query.get()]
    
    async def get_extracted_clinical_data_by_id(self, id:str) -> ExtractedClinicalData:
        query = self.extracted_clinical_data_ref.document(id)
        doc = await query.get()
        return ExtractedClinicalData(**doc.to_dict()) if doc.exists else None
    
    async def get_extracted_conditions_by_document_operation_instance(self, document_id:str, doc_operation_instance_id:str) -> List[MedicalCodingRawData]:
        query = self.extracted_conditions_ref.where("document_id","==",document_id).where("document_operation_instance_id","==",doc_operation_instance_id)
        return [MedicalCodingRawData(**doc.to_dict()) for doc in await query.get()]

    async def get_page_operation(self, page_id: str, document_operation_instance_id:str,extraction_type:PageLabel) -> PageOperation:
        query = self.page_operation_ref.where("page_id","==",page_id).where("document_operation_instance_id","==",document_operation_instance_id).where("extraction_type","==",extraction_type)
        docs = await query.get()
        docs = [PageOperation(**doc.to_dict()) for doc in docs]
        docs_sorted = sorted(docs, key=lambda x: x.created_at, reverse=True)
        return docs_sorted[0] if docs_sorted else None
    
    async def get_all_page_operations(self, document_id:str, document_operation_instance_id:str, extraction_type:PageLabel) -> List[PageOperation]:
        query = self.page_operation_ref.where("document_id","==",document_id).where("document_operation_instance_id","==",document_operation_instance_id).where("extraction_type","==",extraction_type)
        docs = await query.get()
        page_operations = [PageOperation(**doc.to_dict()) for doc in docs]
        
        deduped_page_operations = {}
        for page_operation in page_operations:
            if page_operation.page_id not in deduped_page_operations:
                deduped_page_operations[page_operation.page_id] = page_operation
            elif page_operation.created_at > deduped_page_operations[page_operation.page_id].created_at:
                deduped_page_operations[page_operation.page_id] = page_operation

        return list(deduped_page_operations.values())
        
        # deduped_page_operations = []
        # for page_operation in page_operations:
        #     [x for x in deduped_page_operations if x.page_id == page_operation.page_id and page_operation.medication_extraction_status] or deduped_page_operations.append(page_operation)

        return page_operations
    
    async def get_page_texts(self, document_id:str, document_operation_instance_id:str) -> List[PageText]:
        query = self.pages_ref.where("document_id","==",document_id).where("document_operation_instance_id","==",document_operation_instance_id)
        docs = await query.get()
        pages:List[Page] = [Page(**doc.to_dict()) for doc in docs]
        page_texts = [PageText(pageNumber=x.number,text=x.text) for x in pages]
        return page_texts
    
    async def get_entity_retry_config(self,entity_id:str, entity_type:str):
        query = self.retry_ref.where("retry_entity_id","==",entity_id).where("retry_entity_type","==",entity_type)
        docs = await query.get()
        if docs:
            retry_entities = [EntityRetryConfig(**doc.to_dict()) for doc in docs]
            retry_entities.sort(key=lambda x: x.created_at, reverse=True)
            return retry_entities[0]
        return None
    
    async def get_entity_schema_by_id(self, schema_id: str) -> Optional[EntitySchemaAggregate]:
        """Get an entity schema by its schema_id field."""
        from ...domain.model_entities import EntitySchemaAggregate
        
        query = self.client.collection("paperglass_entity_schemas").where(filter=FieldFilter("schema_id", "==", schema_id)).where(filter=FieldFilter("active", "==", True))
        docs = await query.get()
        if docs:
            # Return the most recent schema if multiple exist
            schemas = [EntitySchemaAggregate(**doc.to_dict()) for doc in docs]
            schemas.sort(key=lambda x: x.created_at, reverse=True)
            return schemas[0]
        return None

    async def get_entity_schema_by_fqn(self, fqn: str) -> Optional[EntitySchemaAggregate]:
        """Get an entity schema by its fqn field."""
        from ...domain.model_entities import EntitySchemaAggregate
        
        query = self.client.collection("paperglass_entity_schemas").where(filter=FieldFilter("fqn", "==", fqn)).where(filter=FieldFilter("active", "==", True))
        docs = await query.get()
        if docs:
            # Return the most recent schema if multiple exist
            schemas = [EntitySchemaAggregate(**doc.to_dict()) for doc in docs]
            schemas.sort(key=lambda x: x.created_at, reverse=True)
            return schemas[0]
        return None

    async def get_entity_schema_by_app_id_and_schema_id(self, app_id: str, schema_id: str) -> Optional[EntitySchemaAggregate]:
        """Get an entity schema by app_id and schema_id fields."""
        from ...domain.model_entities import EntitySchemaAggregate

        query = self.client.collection("paperglass_entity_schemas").where(filter=FieldFilter("app_id", "==", app_id)).where(filter=FieldFilter("schema_id", "==", schema_id)).where(filter=FieldFilter("active", "==", True))
        docs = await query.get()
        if docs:
            # Return the most recent schema if multiple exist
            schemas = [EntitySchemaAggregate(**doc.to_dict()) for doc in docs]
            schemas.sort(key=lambda x: x.created_at, reverse=True)
            return schemas[0]
        return None

    async def get_all_entity_schemas(self, app_id: Optional[str] = None) -> List[EntitySchemaAggregate]:
        """Get all entity schemas, optionally filtered by app_id."""
        from ...domain.model_entities import EntitySchemaAggregate
        
        query = self.client.collection("paperglass_entity_schemas").where(filter=FieldFilter("active", "==", True))
        
        # Add app_id filter if provided
        if app_id:
            query = query.where(filter=FieldFilter("app_id", "==", app_id))
        
        docs = await query.get()
        if docs:
            # Convert to EntitySchemaAggregate objects and sort by created_at descending
            schemas = [EntitySchemaAggregate(**doc.to_dict()) for doc in docs]
            schemas.sort(key=lambda x: x.created_at, reverse=True)
            return schemas
        return []

    async def get_document_entity_toc_by_document_id(self, document_id: str) -> List[dict]:
        """Get all entity TOC entries for a document."""
        thisSpanName = "get_document_entity_toc_by_document_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            try:
                # Query the entity_toc subcollection under the document
                entity_toc_ref = self.documents_ref.document(document_id).collection("entity_toc")
                docs = await entity_toc_ref.get()
                
                if not docs:
                    return []
                
                # Convert to list of dictionaries and sort by created_at descending
                entity_toc_list = [doc.to_dict() for doc in docs]
                entity_toc_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                
                return entity_toc_list
            except Exception as e:
                LOGGER.error("Error in get_document_entity_toc_by_document_id: %s", str(e))
                return []

    async def get_document_entity_toc_by_document_id_and_run_id(self, document_id: str, run_id: str) -> Optional[dict]:
        """Get a specific entity TOC entry by document_id and run_id."""
        thisSpanName = "get_document_entity_toc_by_document_id_and_run_id"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            try:
                # Query the entity_toc subcollection under the document filtered by run_id
                entity_toc_ref = self.documents_ref.document(document_id).collection("entity_toc")
                query = entity_toc_ref.where(filter=FieldFilter("run_id", "==", run_id))
                docs = await query.get()
                
                if not docs:
                    return None
                
                # Return the first match (there should only be one per run_id)
                return [x.to_dict() for x in docs]
            except Exception as e:
                LOGGER.error("Error in get_document_entity_toc_by_document_id_and_run_id: %s", str(e))
                return None

    async def get_entities_by_document_and_entity_type(self, document_id: str, entity_type: str) -> List[dict]:
        """Get all entities of a specific type for a given document."""
        thisSpanName = "get_entities_by_document_and_entity_type"
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            try:
                # Collection name format: paperglass_entities_{entity_type}
                collection_name = f"paperglass_entities_{entity_type}"
                
                # Query entities for this document and entity type
                entity_collection = self.client.collection(collection_name)
                entity_query = entity_collection.where(filter=FieldFilter("document_id", "==", document_id)).where(filter=FieldFilter("active", "==", True))
                entity_docs = await entity_query.get()
                
                # Convert Firestore documents to dictionaries
                entities = []
                for entity_doc in entity_docs:
                    entity_data = entity_doc.to_dict()
                    entities.append(entity_data)
                
                LOGGER.debug(f"Retrieved {len(entities)} entities of type '{entity_type}' for document {document_id}")
                return entities
                
            except Exception as e:
                LOGGER.error("Error in get_entities_by_document_and_entity_type for document %s, entity_type %s: %s", document_id, entity_type, str(e))
                return []
    
class GoogleStorageAdapter(IStoragePort):
    def __init__(self, project_id, bucket_name, cloud_provider):
        self.project_id = project_id
        self.bucket_name = bucket_name
        # self.client = Storage()
        self.sync_client = storage.Client(project=project_id)
        self.cloud_provider = cloud_provider

        self.SPAN_BASE: str = "INFRA:GoogleStorageAdapter:"
        self.opentelemetry = OpenTelemetryUtils(self.SPAN_BASE)

        # self._pem = None
        # service_data = self.client.token.service_data
        # if STORAGE_FAKEGCS:
        #     # Anonymous credentials, running locally, need to patch
        #     service_data["client_email"] = "local@example.org"
        #     service_data["private_key"] = self.anonymous_key

    # @property
    # def anonymous_key(self):
    #     # https://github.com/fsouza/fake-gcs-server/issues/952
    #     if not self._pem:
    #         private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    #         self._pem = private_key.private_bytes(
    #             encoding=serialization.Encoding.PEM,
    #             format=serialization.PrivateFormat.TraditionalOpenSSL,
    #             encryption_algorithm=serialization.NoEncryption(),
    #         ).decode("utf-8")
    #     return self._pem

    def _gcs_uri(self, path: str) -> str:
        return f"gs://{self.bucket_name}/{path}"

    # gcloud.aio.storage does not support impersonated service account credentials (yet?), but we need them to sign URLs
    # https://github.com/talkiq/gcloud-aio/issues/685
    # async def put_document(
    #     self,
    #     document_id: str,
    #     content: bytes,
    # ) -> str:
    #     path = f'paperglass/documents/{document_id}/document.pdf'
    #     await self.client.upload(self.bucket_name, path, content)
    #     return self._gcs_uri(path)
    #
    # async def get_document(self, document_id: str) -> bytes:
    #     path = f'paperglass/documents/{document_id}/document.pdf'
    #     return await self.client.download(self.bucket_name, path)
    #
    # async def get_document_pdf_url(self, document_id: str) -> str:
    #     path = f'paperglass/documents/{document_id}/document.pdf'
    #     return await self._get_signed_url(self.bucket_name, path)
    #
    # async def put_document_chunk(
    #     self,
    #     document_id: str,
    #     chunk_index: int,
    #     content: bytes,
    # ) -> str:
    #     path = f'paperglass/documents/{document_id}/chunks/{chunk_index}.pdf'
    #     await self.client.upload(self.bucket_name, path, content)
    #     return self._gcs_uri(path)
    #
    # async def get_document_chunk(self, document_id: str, chunk_index: int) -> bytes:
    #     path = f'paperglass/documents/{document_id}/chunks/{chunk_index}.pdf'
    #     return await self.client.download(self.bucket_name, path)
    #
    # async def put_page_result(
    #     self,
    #     type: str,
    #     result_id: str,
    #     content: bytes,
    # ) -> str:
    #     path = f'paperglass/page_results/{type}/{result_id}.json'
    #     await self.client.upload(self.bucket_name, path, content)
    #     return self._gcs_uri(path)
    #
    # async def get_page_result(self, type: str, result_id: str) -> bytes:
    #     path = f'paperglass/page_results/{type}/{result_id}.json'
    #     return await self.client.download(self.bucket_name, path)

    # Here's a bunch of sync code for y'all folks!
    # If only Google implemented async/await in their GCS client library...
    async def put_document(self, app_id:str, tenant_id:str, patient_id:str, document_id: str, content: bytes) -> str:
        path = f"paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}/document.pdf"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        await asyncio.get_event_loop().run_in_executor(
            None,
            partial(blob.upload_from_string, content, content_type="application/pdf"),
        )
        return self._gcs_uri(path)
    
    async def put_documentoperationinstancelog(self, log:DocumentOperationInstanceLog) -> str:
        with await self.opentelemetry.getSpan("put_documentoperationinstancelog") as span:
            content = log.json()
            path = f"paperglass/documentoperationinstancelog/{log.document_id}/{log.document_operation_instance_id}/{log.id}.json"
            bucket = self.sync_client.bucket(self.bucket_name)
            blob = bucket.blob(path)
            await asyncio.get_event_loop().run_in_executor(
                None,
                partial(blob.upload_from_string, content),
            )
            return self._gcs_uri(path)
        
    async def list_documentoperationinstancelogs(self, document_id:str, doc_op_instance_id:str) -> List[DocumentOperationInstanceLog]:
        with await self.opentelemetry.getSpan("list_documentoperationinstancelogs") as span:
            LOGGER.debug("list_documentoperationinstancelogs: %s %s", document_id, doc_op_instance_id)
            path = f"paperglass/documentoperationinstancelog/{document_id}/{doc_op_instance_id}"
            dicts = await self.list_documents_json(path)
            return [DocumentOperationInstanceLog(**doc) for doc in dicts]
    
    async def list_documents_json(self, path: str) -> List[dict]:
        with await self.opentelemetry.getSpan("list_documents_json") as span:
            LOGGER.debug("list_documents_json: %s", path)
            bucket = self.sync_client.bucket(self.bucket_name)
            blobs = bucket.list_blobs(prefix=path)

            loop = asyncio.get_event_loop()
            tasks = []

            for blob in blobs:
                if blob.name.endswith('.json'):
                    task = loop.run_in_executor(
                        None,
                        partial(self._download_and_deserialize_json_blob, blob)
                    )
                    tasks.append(task)

            results = await asyncio.gather(*tasks)            
            return results
        
    def _download_and_deserialize_json_blob(self, blob):
        content = blob.download_as_text()
        return json.loads(content)


    async def put_report(self,content,path, file_name) -> str:
        path = f"paperglass/test/reports/{path}/{file_name}"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        await asyncio.get_event_loop().run_in_executor(
            None,
            partial(blob.upload_from_string, content),
        )
        return self._gcs_uri(path)
    
    async def put_report_binary(self, content:bytes, path:str, file_name:str, content_type:str) -> str:
        path = f"paperglass/test/reports/{path}/{file_name}"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        await asyncio.get_event_loop().run_in_executor(
            None,
            partial(blob.upload_from_string, content, content_type=content_type),
        )
        return self._gcs_uri(path)
    
    async def get_report(self, path, file_name) -> bytes:
        path = f"paperglass/test/reports/{path}/{file_name}"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        return await asyncio.get_event_loop().run_in_executor(None, blob.download_as_bytes)


    def extract_bucket_and_path(self, storage_uri: str) -> Tuple[str, str]:
        if storage_uri.startswith("gs://"):
            protocol_token = "gs://"        
        else:
            raise Exception("Invalid storage URI: %s  URI must start with gs:// ", storage_uri)
        
        bucket_name = storage_uri.split(protocol_token)[1].split("/", 1)[0]
        path = storage_uri.split(protocol_token)[1].split("/", 1)[1]
        return bucket_name, path

    async def get_external_document_raw(self, storage_uri: str) -> bytes:
        bucket_name, path = self.extract_bucket_and_path(storage_uri)
        bucket = self.sync_client.bucket(bucket_name)
        blob = bucket.blob(path)
        return await asyncio.get_event_loop().run_in_executor(None, blob.download_as_bytes)
    
    async def get_document_raw(self, storage_uri: str) -> bytes:
        bucket_name, path = self.extract_bucket_and_path(storage_uri)        
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        return await asyncio.get_event_loop().run_in_executor(None, blob.download_as_bytes)

    async def get_document(self, app_id:str, tenant_id:str,patient_id:str, document_id: str) -> bytes:
        path = f"paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}/document.pdf"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        return await asyncio.get_event_loop().run_in_executor(None, blob.download_as_bytes)

    async def get_document_pdf_url(self, app_id:str, tenant_id:str,patient_id:str, document_id: str) -> str:
        path = f"paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}/document.pdf"
        return await self._get_signed_url(self.bucket_name, path)

    async def put_document_page(self, app_id:str, tenant_id:str,patient_id:str, document_id: str, page_number: int, content: bytes) -> str:
        path = f"paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}/pages/{page_number}.pdf"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        await asyncio.get_event_loop().run_in_executor(
            None,
            partial(blob.upload_from_string, content, content_type="application/pdf"),
        )
        return self._gcs_uri(path)

    async def get_document_page(self, app_id:str, tenant_id:str,patient_id:str, document_id: str, page_number: int) -> bytes:
        path = f"paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}/pages/{page_number}.pdf"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        return await asyncio.get_event_loop().run_in_executor(None, blob.download_as_bytes)

    async def put_page_ocr(self, app_id:str, tenant_id:str,patient_id:str, document_id: str, page_id: int, content: bytes, ocr_type:OCRType) -> str:
        path = f"paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}/ocr/{page_id}/{ocr_type.value}.json"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        await asyncio.get_event_loop().run_in_executor(
            None,
            partial(blob.upload_from_string, content, content_type="application/json"),
        )
        return self._gcs_uri(path)
    
    async def write_text(self, bucket_name: str, path: str, content: str, content_type=None) -> bool:
        bucket = self.sync_client.bucket(bucket_name)
        blob = bucket.blob(path)
        # blob.upload_from_string(content)
        if not content_type:
            await asyncio.get_event_loop().run_in_executor(
                None,
                partial(blob.upload_from_string, content),
            )
        else:
            await asyncio.get_event_loop().run_in_executor(
                None,
                partial(blob.upload_from_string, content, content_type=content_type),
            )
        return True

    async def get_page_ocr(self, app_id:str, tenant_id:str,patient_id:str, document_id: str, page_number: int,ocr_type:OCRType) -> bytes:
        path = f"paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}/ocr/{page_number}/{ocr_type.value}.json"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        return await asyncio.get_event_loop().run_in_executor(None, blob.download_as_bytes)


    async def put_page_result(self, type: str, result_id: str, content: bytes) -> str:
        path = f"paperglass/page_results/{type}/{result_id}.json"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        await asyncio.get_event_loop().run_in_executor(
            None,
            partial(blob.upload_from_string, content, content_type="application/json"),
        )
        return self._gcs_uri(path)

    async def get_page_result(self, type: str, result_id: str) -> bytes:
        path = f"paperglass/page_results/{type}/{result_id}.json"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        return await asyncio.get_event_loop().run_in_executor(None, blob.download_as_bytes)

    async def put_document_page_annotations(
        self, document_id: str, page_result_id: str, annotation_type: AnnotationType, content: bytes
    ) -> str:
        path = f"paperglass/page_annotations/{document_id}/{page_result_id}/{annotation_type.value}.json"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        await asyncio.get_event_loop().run_in_executor(
            None,
            partial(blob.upload_from_string, content, content_type="application/json"),
        )
        return self._gcs_uri(path)

    async def get_document_page_annotations(
        self, document_id: str, page_result_id: str, annotation_type: AnnotationType
    ) -> bytes:
        path = f"paperglass/page_annotations/{document_id}/{page_result_id}/{annotation_type.value}.json"
        bucket = self.sync_client.bucket(self.bucket_name)
        blob = bucket.blob(path)
        return await asyncio.get_event_loop().run_in_executor(None, blob.download_as_bytes)
    
    async def get_object_metadata(
        self, storage_uri: str
    ) -> Dict[str, Any]:

        bucket_name, path = self.extract_bucket_and_path(storage_uri)
        bucket = self.sync_client.bucket(bucket_name)
        blob = bucket.blob(path)

        #The blob object is just a reference and does not include metadata.  We need to reload the blob to get it.
        await asyncio.get_event_loop().run_in_executor(None, blob.reload)
        metadata = await asyncio.get_event_loop().run_in_executor(None, lambda: getattr(blob, 'metadata'))

        return metadata

    def _get_signed_url_sync(self, bucket_name: str, path: str):
        # https://stackoverflow.com/a/64245028/3455614
        # credentials, _ = google.auth.default()
        # req = requests.Request()
        # credentials.refresh(req)
        #
        # client = storage.Client(project=self.project_id)
        # bucket = client.get_bucket(bucket_name)
        # blob = bucket.get_blob(path)

        # Honestly, I hate google auth gehenna. I truly hate it.

        if self.cloud_provider == "google":
            credentials, _ = google.auth.default()
            auth_request = requests.Request()
            credentials.refresh(auth_request)

            LOGGER.debug("Getting signed URL for bucket: %s, path: %s", bucket_name, path)

            bucket = self.sync_client.get_bucket(bucket_name)
            blob = bucket.get_blob(path)

            service_account_email = credentials.service_account_email
            url = blob.generate_signed_url(
                expiration=timedelta(hours=48),  # TODO: how much TTL?
                service_account_email=service_account_email,
                access_token=credentials.token,
            )

            LOGGER.debug("Obtained signed URL for bucket: %s, path: %s: %s", bucket_name, path, url)
        else:
            # Breaks in Cloud Run:
            # >  AttributeError: you need a private key to sign credentials.the credentials you are currently using <class 'google.auth.compute_engine.credentials.Credentials'> just contains a token
            blob = self.sync_client.bucket(bucket_name).blob(path)

            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=48),  # TODO: how much TTL?
                method="GET",
            )

        return url

        # if not hasattr(credentials, 'service_account_email'):
        #     # What the actuall hell, honestly?
        #     service_account_email = 'andrew.dunai@wellsky.com'
        # else:
        #     service_account_email = credentials.service_account_email
        # return blob.generate_signed_url(
        #     expiration=timedelta(hours=48), # TODO: how much TTL?
        #     service_account_email=service_account_email,
        #     access_token=credentials.token,
        # )

    async def _get_signed_url(self, bucket: str, path: str) -> str:
        # if STORAGE_FAKEGCS:
        #     async with ClientSession() as session:
        #         bucket_obj = Bucket(self.client, bucket)
        #         blob = await bucket_obj.get_blob(path, session=session)  # type: ignore
        #         url = await blob.get_signed_url(60)
        #         # Terrible hack for generating URLs that work locally, since gcloud.aio.storage has hardcoded HOST
        #         url = url.replace("https://storage.googleapis.com", "http://127.0.0.1:4443")
        #         return url

        return await asyncio.get_event_loop().run_in_executor(None, partial(self._get_signed_url_sync, bucket, path))

class CloudTaskAdapter(ICloudTaskPort):

    def __init__(self, project_id:str):
        self.project_id = project_id

        self.SPAN_BASE: str = "INFRA:CloudTaskAdapter:"
        self.opentelemetry = OpenTelemetryUtils(self.SPAN_BASE)

    async def create_task(self, token,location, service_account_email, queue, url,payload):
        from google.cloud import tasks_v2
        from proto.message import MessageToDict

        thisSpanName = "create_task"
        with await self.opentelemetry.getSpan(thisSpanName) as span:

            LOGGER.info(f"Creating task for queue: {queue}, url: {url}, payload: {payload}")

            client = tasks_v2.CloudTasksClient()
            project = self.project_id
            queue = queue
            location = location
            url = url
            service_account_email = service_account_email

            parent = client.queue_path(project, location, queue)
            task = {
                        "http_request": {  
                            "http_method": tasks_v2.HttpMethod.POST,
                            'url': url,
                            "oidc_token": {"service_account_email": service_account_email},
                            "headers": {"Content-Type": "application/json","Authorization2":'Bearer ' + token},
                            "body":json.dumps(payload,cls=DateTimeEncoder).encode(),
                        }
                    }
            response = client.create_task(parent=parent, task=task)
            LOGGER.debug("Created task: %s", response.name)
            return MessageToDict(response._pb)
    
    async def create_task_v2(self, location, service_account_email, queue, url, payload, http_headers: Dict[str, str] = {}, token:str = None, schedule_time: datetime = None):
        from google.cloud import tasks_v2
        from google.protobuf.timestamp_pb2 import Timestamp
        from proto.message import MessageToDict

        with await self.opentelemetry.getSpan("create_task_v2") as span:

            LOGGER.info(f"Creating task (v2) for queue: {queue}, url: {url}, payload: {payload}, schedule_time: {schedule_time}")

            if token:
                http_headers.update({
                    "Authorization2": f"Bearer {token}"
                })

            client = tasks_v2.CloudTasksClient()
            project = self.project_id
            queue = queue
            location = location
            url = url
            service_account_email = service_account_email

            parent = client.queue_path(project, location, queue)

            from paperglass.domain.util_json import DateTimeEncoder

            httpRequest = {  
                            "http_method": tasks_v2.HttpMethod.POST,
                            'url': url,
                            "oidc_token": {"service_account_email": service_account_email},                            
                            "body":json.dumps(payload, cls=DateTimeEncoder).encode(),
                        }
            
            headers = {
                "Content-Type": "application/json"
            }

            if http_headers:
                headers.update(http_headers)

            httpRequest["headers"] = http_headers

            task = {
                        "http_request": httpRequest
                    }
            
            if schedule_time:
                timestamp = Timestamp()
                timestamp.FromDatetime(schedule_time)
                task["schedule_time"] = timestamp

            response = client.create_task(parent=parent, task=task)
            LOGGER.debug("Created task (v2): %s", response.name)
            return MessageToDict(response._pb)

class ApplicationIntegrationAdapter(IApplicationIntegration):

    def __init__(self, project,location):
        self.project = project
        self.location = location

        self.SPAN_BASE: str = "INFRA:ApplicationIntegrationAdapter:"
        self.opentelemetry = OpenTelemetryUtils(self.SPAN_BASE)

    async def _get_token(self):
        import google.auth
        import google.auth.transport.requests
        SCOPE = "https://www.googleapis.com/auth/cloud-platform"
        credentials, project_id = google.auth.default(scopes=[SCOPE])
        # getting request object
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)  # refresh token
        token = credentials.token
        return token, project_id

    async def start(self, integration_project_name, json_payload, trigger_id):
        with await self.opentelemetry.getSpan("start") as span:
            import requests
            import json
            token, project_id = await self._get_token()
            url = f"https://integrations.googleapis.com/v2/projects/{self.project}/locations/{self.location}/integrations/{integration_project_name}:execute?triggerId={trigger_id}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            LOGGER.info(f"Starting integration execution for integration: {integration_project_name}, trigger_id: {trigger_id}, payload: {json_payload}")
            response = requests.post(url, headers=headers, json=json_payload)
            return response.json()

    async def lift(self, project, location, integration_project_name,token, json_payload, trigger_id):
        with await self.opentelemetry.getSpan("lift") as span:
            import requests
            import json
            url = f"https://integrations.googleapis.com/v2/projects/{project}/locations/{location}/integrations/{integration_project_name}:execute?triggerId={trigger_id}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            response = requests.post(url, headers=headers, json=json_payload)
            return response.json()
