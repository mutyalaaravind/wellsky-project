import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import settings


class AutoHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that automatically adds headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        # Calculate elapsed time
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Add headers matching paperglass (excluding trace-related ones)
        response.headers["x-wsky-build"] = settings.VERSION
        response.headers["x-wsky-env"] = settings.STAGE
        response.headers["x-wsky-debug"] = str(settings.DEBUG)
        response.headers["x-wsky-project-id"] = settings.GCP_PROJECT_ID
        response.headers["x-wsky-cloud-provider"] = settings.CLOUD_PROVIDER
        response.headers["x-wsky-performance-elapsed-ms"] = str(round(elapsed_time, 1))
        
        # Add conditional header for Firestore emulator
        if settings.FIRESTORE_EMULATOR_HOST:
            response.headers["x-wsky-firestore-emulator-enabled"] = "True"
        
        return response
