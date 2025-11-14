"""
Auto Headers Middleware for Admin API.
Automatically adds standardized x-wsky headers to all HTTP responses.
"""

import time
import os
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from settings import Settings


class AutoHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically adds standard x-wsky headers to all responses.

    Headers added:
    - x-wsky-build: Application version
    - x-wsky-env: Environment stage
    - x-wsky-debug: Debug mode flag
    - x-wsky-project-id: GCP project ID
    - x-wsky-cloud-provider: Cloud provider
    - x-wsky-service: Service name
    - x-wsky-performance-elapsed-ms: Request processing time in milliseconds
    - x-wsky-firestore-emulator-enabled: Conditional header when emulator is used
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and add standard headers to the response.

        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in chain

        Returns:
            Response with added headers
        """
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate elapsed time
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Get settings
        settings = Settings()

        # Add standard x-wsky headers
        response.headers["x-wsky-build"] = settings.VERSION
        response.headers["x-wsky-env"] = settings.STAGE
        response.headers["x-wsky-debug"] = str(settings.DEBUG)
        response.headers["x-wsky-project-id"] = settings.GCP_PROJECT_ID
        response.headers["x-wsky-cloud-provider"] = settings.CLOUD_PROVIDER
        response.headers["x-wsky-service"] = settings.SERVICE
        response.headers["x-wsky-performance-elapsed-ms"] = str(round(elapsed_time, 1))

        # Add conditional headers
        firestore_emulator_host = os.getenv('FIRESTORE_EMULATOR_HOST')
        if firestore_emulator_host:
            response.headers["x-wsky-firestore-emulator-enabled"] = "True"

        return response