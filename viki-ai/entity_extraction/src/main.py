import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from middleware.auto_headers import AutoHeadersMiddleware
from routers.config_pipeline import router as config_router
from routers.pipeline import router as pipeline_router
from routers.status import router as status_router
from routers.admin import router as admin_router
from routers.llm import router as llm_router
from util.custom_logger import getLogger

# This will be initialized in the startup event
logger = getLogger(__name__)

app = FastAPI(title="Entity Extraction API")

@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    Initializes tracing and other background tasks.
    """
    try:
        from util.tracing import initialize_tracing, instrument_libraries
        import settings
        
        # Initialize OpenTelemetry tracing
        initialize_tracing(
            service_name="entity-extraction",
            service_version="1.0.0",
            enable_gcp_exporter=settings.ENABLE_GCP_TRACE_EXPORTER,
            enable_console_exporter=settings.ENABLE_CONSOLE_TRACE_EXPORTER,
            enable_jaeger_exporter=settings.ENABLE_JAEGER_TRACE_EXPORTER,
            jaeger_endpoint=settings.JAEGER_ENDPOINT
        )
        
        # Instrument libraries for automatic tracing
        instrument_libraries()
        
        logger.info("OpenTelemetry tracing initialized successfully")
        
    except Exception as e:
        # Don't fail startup if tracing initialization fails
        logger.warning(f"Failed to initialize OpenTelemetry tracing: {e}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add auto headers middleware
app.add_middleware(AutoHeadersMiddleware)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def root():
    return {"message": "Welcome to Entity Extraction API"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include the API router
app.include_router(api_router)
# Include the config router
app.include_router(config_router, prefix="/api")
# Include the pipeline router
app.include_router(pipeline_router, prefix="/api")
# Include the status router
app.include_router(status_router, prefix="/api")
# Include the admin router
app.include_router(admin_router, prefix="/api")
# Include the LLM router
app.include_router(llm_router, prefix="/api")
