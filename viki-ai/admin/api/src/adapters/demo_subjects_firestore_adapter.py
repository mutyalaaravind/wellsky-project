import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from model_aggregates.demo_subjects import DemoSubjectAggregate, DemoSubjectsConfigAggregate
from infrastructure.demo_ports import IDemoSubjectRepository
from settings import Settings


class DemoSubjectsFirestoreAdapter(IDemoSubjectRepository):
    """Firestore adapter implementing IDemoSubjectRepository port"""
    
    def __init__(self, settings: Settings):
        """
        Initialize the Firestore adapter.
        
        Args:
            settings: Application settings containing Firestore configuration
        """
        print(f"🔥 Initializing Demo Subjects Firestore adapter")
        self.settings = settings
        self.subjects_collection_name = "admin_demo_subjects"
        
        # Initialize Firestore client
        emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST")
        if emulator_host:
            # When using emulator, use the emulator project ID
            emulator_project = "google-cloud-firestore-emulator"
            print(f"🔥 Using Firestore EMULATOR at {emulator_host}, project: {emulator_project}")
            self.client = firestore.Client(project=emulator_project)
        else:
            print(f"🔥 Using PRODUCTION Firestore - Project: {settings.GCP_PROJECT_ID}, Database: {settings.GCP_FIRESTORE_DB}")
            self.client = firestore.Client(
                project=settings.GCP_PROJECT_ID, 
                database=settings.GCP_FIRESTORE_DB
            )
        print(f"🔥 Demo Subjects Firestore adapter initialized successfully")
    
    def _aggregate_to_dict(self, aggregate) -> Dict[str, Any]:
        """Convert aggregate to dictionary for Firestore storage."""
        data = aggregate.model_dump()
        # Remove events field as it's not persisted
        data.pop('events', None)
        return data
    
    def _dict_to_subject_aggregate(self, data: Dict[str, Any]) -> DemoSubjectAggregate:
        """Convert dictionary from Firestore to DemoSubjectAggregate."""
        # Convert Firestore timestamps to Python datetime objects
        for field in ['created_at', 'updated_at']:
            if data.get(field):
                timestamp_value = data[field]
                if hasattr(timestamp_value, 'seconds'):
                    # Convert Firestore timestamp to datetime
                    from datetime import datetime, timezone
                    data[field] = datetime.fromtimestamp(timestamp_value.seconds, tz=timezone.utc)
        
        return DemoSubjectAggregate(**data)
    
    def _dict_to_config_aggregate(self, data: Dict[str, Any]) -> DemoSubjectsConfigAggregate:
        """Convert dictionary from Firestore to DemoSubjectsConfigAggregate."""
        # Convert Firestore timestamps to Python datetime objects
        for field in ['created_at', 'updated_at']:
            if data.get(field):
                timestamp_value = data[field]
                if hasattr(timestamp_value, 'seconds'):
                    # Convert Firestore timestamp to datetime
                    from datetime import datetime, timezone
                    data[field] = datetime.fromtimestamp(timestamp_value.seconds, tz=timezone.utc)
        
        return DemoSubjectsConfigAggregate(**data)
    
    async def get_subject_config(self, app_id: str) -> Optional[DemoSubjectsConfigAggregate]:
        """Get subject configuration for an app"""
        doc_ref = self.client.collection(self.subjects_collection_name).document(app_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return self._dict_to_config_aggregate(doc.to_dict())
        return None
    
    async def save_subject_config(self, config: DemoSubjectsConfigAggregate) -> DemoSubjectsConfigAggregate:
        """Save subject configuration"""
        doc_ref = self.client.collection(self.subjects_collection_name).document(config.id)
        doc_ref.set(self._aggregate_to_dict(config))
        config.clear_events()  # Clear domain events after persistence
        return config
    
    async def get_subject(self, app_id: str, subject_id: str) -> Optional[DemoSubjectAggregate]:
        """Get a specific demo subject"""
        doc_ref = self.client.collection(self.subjects_collection_name).document(app_id).collection("subjects").document(subject_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return self._dict_to_subject_aggregate(doc.to_dict())
        return None
    
    async def save_subject(self, subject: DemoSubjectAggregate) -> DemoSubjectAggregate:
        """Save a demo subject"""
        doc_ref = self.client.collection(self.subjects_collection_name).document(subject.app_id).collection("subjects").document(subject.id)
        doc_ref.set(self._aggregate_to_dict(subject))
        subject.clear_events()  # Clear domain events after persistence
        return subject
    
    async def list_subjects(self, app_id: str) -> List[DemoSubjectAggregate]:
        """List all active subjects for an app"""
        query = self.client.collection(self.subjects_collection_name).document(app_id).collection("subjects").where(
            filter=FieldFilter("active", "==", True)
        ).order_by("created_at", direction=firestore.Query.DESCENDING)
        
        docs = query.stream()
        subjects = []
        for doc in docs:
            subjects.append(self._dict_to_subject_aggregate(doc.to_dict()))
        
        return subjects
    
    async def delete_subject(self, app_id: str, subject_id: str) -> bool:
        """Delete a subject (returns True if found and deleted)"""
        subject = await self.get_subject(app_id, subject_id)
        if not subject or subject.is_deleted:
            return False
        
        subject.soft_delete()
        await self.save_subject(subject)
        return True