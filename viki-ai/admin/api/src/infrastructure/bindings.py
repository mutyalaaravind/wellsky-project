"""
This module tells Kink injector how to map ports to adapters.
"""

import os
from google.cloud import storage, firestore
from kink import di

from contracts.file_storage_contracts import FileStoragePort
from contracts.entity_extraction_contracts import EntityExtractionPort
from contracts.djt_contracts import DJTPort
from contracts.config_contracts import ConfigPort
from contracts.paperglass import PaperglassPort
from contracts.logging_contracts import ILoggingRepository, ILoggingConfigurationRepository
from contracts.reports_contracts import ReportsPort
from adapters.gcs_file_storage_adapter import GCSFileStorageAdapter
from adapters.entity_extraction_adapter import EntityExtractionAdapter
from adapters.djt_adapter import DJTAdapter
from adapters.config_adapter import ConfigAdapter
from adapters.paperglass_adapter import PaperglassAdapter
from adapters.google_cloud_logging_adapter import GoogleCloudLoggingAdapter, FirestoreLoggingConfigurationAdapter
from adapters.demo_subjects_firestore_adapter import DemoSubjectsFirestoreAdapter
from adapters.document_firestore_adapter import DocumentFirestoreAdapter
from adapters.document_gcs_adapter import DocumentGCSAdapter
from adapters.bigquery_reports_adapter import BigQueryReportsAdapter
from infrastructure.demo_ports import IDemoSubjectRepository
from infrastructure.document_ports import DocumentRepositoryPort, FileStoragePort as DocumentFileStoragePort
from usecases.logging_service import LoggingService
from usecases.demo_service import DemoSubjectService
from usecases.document_service import DocumentService
from usecases.onboard_service import OnboardService
from domain.ports.user_profile_ports import IUserProfileRepositoryPort
from domain.ports.okta_integration_port import IOktaIntegrationPort
from infrastructure.adapters.user_profile_firestore_adapter import UserProfileFirestoreAdapter
from infrastructure.adapters.okta_integration_adapter import OktaIntegrationAdapter
from application.commands.user_profile_commands import UserProfileCommandHandler
from application.queries.user_profile_queries import UserProfileQueryHandler
from application.profile_resolver import ProfileResolver
from settings import Settings

try:
    from viki_shared.adapters.gcs_adapter import GCSAdapter
except ImportError:
    # Fallback if shared library is not available
    from adapters.gcs_file_storage_adapter import GCSFileStorageAdapter as GCSAdapter


def configure_dependencies():
    """Configure dependency injection bindings."""
    settings = Settings()

    # Storage and Firestore clients
    storage_client = storage.Client(project=settings.GCP_PROJECT_ID)

    # Use default database for emulator, named database for production
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        firestore_client = firestore.AsyncClient(project=settings.GCP_PROJECT_ID)
    else:
        firestore_client = firestore.AsyncClient(project=settings.GCP_PROJECT_ID, database=settings.GCP_FIRESTORE_DB)
    
    # File storage port binding
    di[FileStoragePort] = lambda _: GCSFileStorageAdapter(storage_client)
    
    # Entity extraction port binding
    di[EntityExtractionPort] = lambda _: EntityExtractionAdapter(settings)
    
    # DJT port binding
    di[DJTPort] = lambda _: DJTAdapter(settings)
    
    # Config port binding
    di[ConfigPort] = lambda _: ConfigAdapter(settings)
    
    # Paperglass port binding
    di[PaperglassPort] = lambda _: PaperglassAdapter(settings)
    
    # Logging port bindings
    di[ILoggingRepository] = GoogleCloudLoggingAdapter(settings.GCP_PROJECT_ID)
    di[ILoggingConfigurationRepository] = FirestoreLoggingConfigurationAdapter(settings.GCP_PROJECT_ID)
    
    # Logging service binding  
    di[LoggingService] = LoggingService(
        logging_repository=di[ILoggingRepository],
        config_repository=di[ILoggingConfigurationRepository]
    )
    
    # Demo subject port binding
    di[IDemoSubjectRepository] = lambda _: DemoSubjectsFirestoreAdapter(settings)
    
    # Demo subject service binding
    di[DemoSubjectService] = lambda _: DemoSubjectService(repository=di[IDemoSubjectRepository])
    
    # Document service bindings
    gcs_adapter = GCSAdapter(storage_client, cloud_provider=settings.CLOUD_PROVIDER)
    di[DocumentFileStoragePort] = lambda _: DocumentGCSAdapter(gcs_adapter)
    di[DocumentRepositoryPort] = lambda _: DocumentFirestoreAdapter(firestore_client)
    di[DocumentService] = lambda _: DocumentService(
        document_repository=di[DocumentRepositoryPort],
        file_storage=di[DocumentFileStoragePort],
        paperglass_adapter=di[PaperglassPort],
        settings=settings
    )
    
    # Onboard service binding
    di[OnboardService] = lambda _: OnboardService(di[PaperglassPort])

    # Reports port binding
    di[ReportsPort] = lambda _: BigQueryReportsAdapter(settings)

    # User Profile port bindings
    di[IUserProfileRepositoryPort] = lambda _: UserProfileFirestoreAdapter(firestore_client)

    # Okta Integration port binding
    di[IOktaIntegrationPort] = lambda _: OktaIntegrationAdapter(settings)

    di[UserProfileCommandHandler] = lambda _: UserProfileCommandHandler(
        profile_repository=di[IUserProfileRepositoryPort],
        okta_integration=di[IOktaIntegrationPort]
    )
    di[UserProfileQueryHandler] = lambda _: UserProfileQueryHandler(di[IUserProfileRepositoryPort])

    # Profile Resolver binding
    di[ProfileResolver] = lambda _: ProfileResolver(di[IUserProfileRepositoryPort])


def get_demo_subject_service() -> DemoSubjectService:
    """Get demo subject service instance."""
    return di[DemoSubjectService]


def get_document_service() -> DocumentService:
    """Get document service instance."""
    return di[DocumentService]


def get_file_storage() -> DocumentFileStoragePort:
    """Get file storage instance."""
    return di[DocumentFileStoragePort]


def get_onboard_service() -> OnboardService:
    """Get onboard service instance."""
    return di[OnboardService]


def get_paperglass_service() -> PaperglassPort:
    """Get paperglass service instance."""
    return di[PaperglassPort]


def get_reports_service() -> ReportsPort:
    """Get reports service instance."""
    return di[ReportsPort]


def get_document_repository() -> DocumentRepositoryPort:
    """Get document repository instance."""
    return di[DocumentRepositoryPort]


def get_profile_resolver() -> ProfileResolver:
    """Get profile resolver instance."""
    return di[ProfileResolver]
