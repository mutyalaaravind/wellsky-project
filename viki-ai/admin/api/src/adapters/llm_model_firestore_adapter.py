import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from models.llm_model import LLMModel
from settings import Settings


class LLMModelFirestoreAdapter:
    """Firestore adapter for LLM model persistence."""
    
    def __init__(self, settings: Settings):
        """
        Initialize the Firestore adapter.
        
        Args:
            settings: Application settings containing Firestore configuration
        """
        print(f"🔥 Initializing Firestore adapter")
        self.settings = settings
        self.collection_name = "admin_llm_models"
        
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
        print(f"🔥 Firestore adapter initialized successfully")
    
    def _model_to_dict(self, model: LLMModel) -> Dict[str, Any]:
        """Convert LLMModel to dictionary for Firestore storage."""
        model_dict = model.model_dump()
        
        # Convert datetime objects to Firestore timestamps
        for field in ['created_at', 'updated_at', 'deleted_at']:
            if model_dict.get(field):
                if isinstance(model_dict[field], datetime):
                    model_dict[field] = model_dict[field]
                # If it's already a string, leave it as is for Firestore
        
        return model_dict
    
    def _dict_to_model(self, data: Dict[str, Any]) -> LLMModel:
        """Convert dictionary from Firestore to LLMModel."""
        # Convert Firestore timestamps to Python datetime objects
        for field in ['created_at', 'updated_at', 'deleted_at']:
            if data.get(field):
                timestamp_value = data[field]
                # Convert DatetimeWithNanoseconds to datetime
                if hasattr(timestamp_value, 'replace'):
                    # It's already a datetime-like object, keep as is
                    continue
                elif hasattr(timestamp_value, 'seconds'):
                    # Convert Firestore timestamp to datetime
                    from datetime import datetime, timezone
                    data[field] = datetime.fromtimestamp(timestamp_value.seconds, tz=timezone.utc)
        
        return LLMModel(**data)
    
    async def create_model(self, model: LLMModel) -> LLMModel:
        """
        Create a new LLM model in Firestore.
        
        Args:
            model: LLMModel instance to create
            
        Returns:
            Created LLMModel with updated timestamps
        """
        now = datetime.utcnow()
        model.created_at = now
        model.updated_at = now
        
        doc_ref = self.client.collection(self.collection_name).document(model.id)
        doc_ref.set(self._model_to_dict(model))
        
        return model
    
    async def get_model(self, model_id: str) -> Optional[LLMModel]:
        """
        Retrieve an LLM model by ID.
        
        Args:
            model_id: Unique ID of the model to retrieve
            
        Returns:
            LLMModel if found, None otherwise
        """
        doc_ref = self.client.collection(self.collection_name).document(model_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        return self._dict_to_model(doc.to_dict())
    
    async def update_model(self, model_id: str, model: LLMModel) -> Optional[LLMModel]:
        """
        Update an existing LLM model.
        
        Args:
            model_id: ID of the model to update
            model: Updated LLMModel instance
            
        Returns:
            Updated LLMModel if found, None otherwise
        """
        doc_ref = self.client.collection(self.collection_name).document(model_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        model.updated_at = datetime.utcnow()
        doc_ref.update(self._model_to_dict(model))
        
        return model
    
    async def update_model_fields(self, model_id: str, update_fields: Dict[str, Any]) -> Optional[LLMModel]:
        """
        Update specific fields of an LLM model.
        
        Args:
            model_id: ID of the model to update
            update_fields: Dictionary of fields to update
            
        Returns:
            Updated LLMModel if found, None otherwise
        """
        doc_ref = self.client.collection(self.collection_name).document(model_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        # Add updated timestamp
        update_fields['updated_at'] = datetime.utcnow()
        doc_ref.update(update_fields)
        
        # Return the updated model
        updated_doc = doc_ref.get()
        return self._dict_to_model(updated_doc.to_dict())
    
    async def soft_delete_model(self, model_id: str) -> Optional[LLMModel]:
        """
        Soft delete an LLM model by setting deleted_at timestamp.
        
        Args:
            model_id: ID of the model to delete
            
        Returns:
            Deleted LLMModel if found, None otherwise
        """
        doc_ref = self.client.collection(self.collection_name).document(model_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        now = datetime.utcnow()
        doc_ref.update({
            'deleted_at': now,
            'updated_at': now
        })
        
        # Return the updated model
        updated_doc = doc_ref.get()
        return self._dict_to_model(updated_doc.to_dict())
    
    async def list_models(self, 
                         page: int = 1, 
                         page_size: int = 10, 
                         include_deleted: bool = False) -> tuple[List[LLMModel], int]:
        """
        List LLM models with pagination.
        
        Args:
            page: Page number (1-based)
            page_size: Number of models per page
            include_deleted: Whether to include soft-deleted models
            
        Returns:
            Tuple of (models list, total count)
        """
        try:
            # Use the simplest possible Firestore query
            collection_ref = self.client.collection(self.collection_name)
            
            # Get all documents from the collection
            docs = collection_ref.get()
            print(f"🔥 Found {len(list(docs))} documents in collection")
            
            # Get documents again (docs iterator is consumed)
            docs = collection_ref.get()
            
            all_models = []
            for doc in docs:
                try:
                    print(f"🔥 Processing document {doc.id}")
                    data = doc.to_dict()
                    print(f"🔥 Document data: {data.keys()}")
                    # Filter out deleted models in memory
                    if not include_deleted and data.get('deleted_at'):
                        print(f"🔥 Skipping deleted document {doc.id}")
                        continue
                    model = self._dict_to_model(data)
                    all_models.append(model)
                    print(f"🔥 Added model {model.id} to list")
                except Exception as e:
                    print(f"Error processing document {doc.id}: {e}")
                    continue
            
            # Sort by created_at in memory
            all_models.sort(key=lambda x: x.created_at or datetime.min)
            
            # Apply pagination in memory
            total_count = len(all_models)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_models = all_models[start_idx:end_idx]
            
            return paginated_models, total_count
            
        except Exception as e:
            print(f"Error in list_models: {e}")
            return [], 0
    
    async def search_models(self, 
                           query: Optional[str] = None,
                           family: Optional[str] = None,
                           active: Optional[bool] = None,
                           page: int = 1,
                           page_size: int = 10) -> tuple[List[LLMModel], int]:
        """
        Search LLM models with filters.
        
        Args:
            query: Text search in name, description, or version
            family: Filter by model family
            active: Filter by active status
            page: Page number (1-based)
            page_size: Number of models per page
            
        Returns:
            Tuple of (models list, total count)
        """
        collection_ref = self.client.collection(self.collection_name)
        
        # Get all documents and filter in memory to avoid index requirements
        all_docs = collection_ref.get()
        
        # Apply all filtering in memory to avoid index requirements
        filtered_models = []
        for doc in all_docs:
            data = doc.to_dict()
            
            # Skip deleted models
            if data.get('deleted_at'):
                continue
                
            # Apply family filter
            if family and family.lower() not in data.get('family', '').lower():
                continue
                
            # Apply active filter
            if active is not None and data.get('active') != active:
                continue
                
            # Apply text search filter
            if query:
                query_lower = query.lower()
                if not (query_lower in data.get('name', '').lower() or 
                       query_lower in data.get('description', '').lower() or 
                       query_lower in data.get('version', '').lower()):
                    continue
            
            filtered_models.append(self._dict_to_model(data))
        
        # Sort by created_at
        filtered_models.sort(key=lambda x: x.created_at or datetime.min)
        
        # Apply pagination
        total_count = len(filtered_models)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_models = filtered_models[start_idx:end_idx]
        
        return paginated_models, total_count