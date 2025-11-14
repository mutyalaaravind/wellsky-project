from datetime import datetime, timedelta
from typing import List, Optional, Dict
from adapters.pgvector_adapter import MedispanPgVectorAdapter
from adapters.firestore_vector_adapter import MedispanFirestoreVectorAdapter
from models import MedispanDrug
from model_metric import Metric
from utils.custom_logger import getLogger
from utils.date import now_utc
from utils.exception import exceptionToMap

LOGGER = getLogger(__name__)

# Time to wait between recovery attempts
RECOVERY_PROBE_INTERVAL = timedelta(minutes=1)

class CircuitBreakerAdapter:
    _instances: Dict[str, 'CircuitBreakerAdapter'] = {}
    _states: Dict[str, Dict] = {}

    def __new__(cls, app_id: str, catalog: str):
        instance_key = f"{app_id}:{catalog}"
        if instance_key not in cls._instances:
            cls._instances[instance_key] = super(CircuitBreakerAdapter, cls).__new__(cls)
            cls._states[instance_key] = {
                'is_failed': False,
                'last_failure': None
            }
        return cls._instances[instance_key]

    def __init__(self, app_id: str, catalog: str):
        self.app_id = app_id
        self.catalog = catalog
        self.instance_key = f"{app_id}:{catalog}"
        # Only initialize adapters if they haven't been initialized
        if not hasattr(self, 'primary_adapter'):
            self.primary_adapter = MedispanPgVectorAdapter(app_id=app_id, catalog=catalog)
            self.fallback_adapter = MedispanFirestoreVectorAdapter(app_id=app_id, catalog=catalog)

    def _get_state(self) -> tuple[bool, Optional[datetime]]:
        """Get circuit breaker state from class state dictionary."""
        state = self._states[self.instance_key]
        return state['is_failed'], state['last_failure']

    def _set_state(self, is_failed: bool, last_failure: Optional[datetime] = None):
        """Set circuit breaker state in class state dictionary."""
        self._states[self.instance_key] = {
            'is_failed': is_failed,
            'last_failure': last_failure
        }

    async def search_medications(self, search_term: str, **kwargs) -> List[MedispanDrug]:
        is_failed, last_failure = self._get_state()

        extra = {
            "app_id": self.app_id,
            "catalog": self.catalog,
            "search_term": search_term
        }
        
        # Check if we should attempt recovery
        if is_failed and last_failure:
            if now_utc() - last_failure > RECOVERY_PROBE_INTERVAL:
                is_failed = False
                self._set_state(False, None)
        
        # If circuit is open (failed), go straight to fallback
        if is_failed:
            extra.update({
                "circuit_state": "open",
                "last_failure": last_failure.isoformat() if last_failure else None,
                "adapter": "firestore",
                "is_tripping_event": False,
            })            
            Metric.send("EXTRACTION::MEDDB::SEARCH::CIRCUITBREAKER", branch="firestore", tags=extra)
            return await self.fallback_adapter.search_medications(search_term, **kwargs)
        
        # Try primary adapter
        try:
            results = await self.primary_adapter.search_medications(search_term, **kwargs)
            extra.update({
                "circuit_state": "closed",
                "last_failure": last_failure.isoformat() if last_failure else None,
                "adapter": "alloydb",
                "is_tripping_event": False,
            })
            Metric.send("EXTRACTION::MEDDB::SEARCH::CIRCUITBREAKER", branch="alloydb", tags=extra)
            return results
        except Exception as e:
            extra.update({
                "circuit_state": "open",
                "last_failure": last_failure.isoformat() if last_failure else None,
                "adapter": "firestore",
                "is_tripping_event": True,
                "error": exceptionToMap(e)
            })
            LOGGER.warning("AlloyDB search failed, falling back to Firestore: %s", str(e), extra=extra)
            self._set_state(True, now_utc())            
            Metric.send("EXTRACTION::MEDDB::SEARCH::CIRCUITBREAKER", branch="firestore", tags=extra)
            return await self.fallback_adapter.search_medications(search_term, **kwargs)
