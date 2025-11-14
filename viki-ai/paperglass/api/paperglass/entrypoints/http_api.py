"""
FastAPI HTTP API entrypoint for paperglass.
This provides a new HTTP API interface for other services to call endpoints.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from ..settings import (
    DEBUG, 
    STAGE, 
    VERSION,
    CLOUD_PROVIDER,
    NEW_RELIC_TRACE_ENABLED,
    NEW_RELIC_TRACE_OTLP_ENDPOINT,
    NEW_RELIC_LICENSE_KEY,
    GCP_TRACE_ENABLED,
)
from ..interface.adapters.api import api_router
from ..log import getLogger

# Import bindings to initialize dependency injection
from ..infrastructure import bindings as infrastructure_bindings
from ..interface import bindings as interface_bindings

# Set up logging
LOGGER = getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Paperglass HTTP API",
    description="HTTP API for paperglass service - provides endpoints for other services to call",
    version=VERSION,
    debug=DEBUG,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "access-control-allow-origin",
        "authorization",
        "content-type",
        "x-api-key",
        "graphql-submit-form",
        "httponly",
        "secure",
        "strict-transport-security",
        "x-content-type-options",
        "x-frame-options",
        "sentry-trace",
        "okta-token",
        "ehr-token"
    ],
)

# Include the API router
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint providing basic service information.
    """
    return {
        "service": "paperglass-http-api",
        "version": VERSION,
        "stage": STAGE,
        "description": "HTTP API for paperglass service",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "docs": "/docs" if DEBUG else "disabled",
            "redoc": "/redoc" if DEBUG else "disabled"
        }
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    """
    # Initialize dependency injection bindings
    LOGGER.info("Initializing dependency injection bindings...")
    try:
        # Import bindings to register dependencies in kink container
        from .. import infrastructure
        from .. import interface
        LOGGER.info("Dependency injection bindings initialized successfully")
    except Exception as e:
        LOGGER.error("Failed to initialize dependency injection bindings: %s", str(e))
        raise
    
    LOGGER.info("Starting Paperglass HTTP API")
    LOGGER.info("Version: %s", VERSION)
    LOGGER.info("Stage: %s", STAGE)
    LOGGER.info("Debug mode: %s", DEBUG)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    """
    LOGGER.info("Shutting down Paperglass HTTP API")

# Health check endpoint at root level for load balancers
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Simple health check endpoint for load balancers.
    """
    return {
        "status": "healthy",
        "service": "paperglass-http-api",
        "version": VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "paperglass.entrypoints.http_api:app",
        host="0.0.0.0",
        port=15003,
        reload=DEBUG,
        log_level="info"
    )
