import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from viki_shared.utils.logger import getLogger

from routers import admin, llm_models, cloud_tasks, onboard, templates, app_config, logging_v2 as logging_router, demo_subjects, documents, metrics, pipelines, entities, reports, user_profiles, roles, reference_lists
from settings import Settings
from infrastructure.bindings import configure_dependencies
from middleware.auth_middleware import AuthMiddleware
from middleware.auto_headers import AutoHeadersMiddleware

# Initialize settings and logger
settings = Settings()
logger = getLogger(__name__)

# Set logging level based on DEBUG setting
log_level = logging.DEBUG if settings.DEBUG else logging.INFO
logging.getLogger().setLevel(log_level)

# Configure dependency injection
configure_dependencies()

app = FastAPI(
    title="Admin API",
    description="Admin API service for managing system administration tasks",
    version="0.1.0",
    redirect_slashes=False,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add auto headers middleware
app.add_middleware(AutoHeadersMiddleware)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(llm_models.router, prefix="/api/v1/llm-models", tags=["llm-models"])
app.include_router(cloud_tasks.router, prefix="/api/v1", tags=["cloud-tasks"])
app.include_router(onboard.router, prefix="/api/v1/onboard", tags=["onboard"])
app.include_router(templates.router, prefix="/api/v1", tags=["templates"])
app.include_router(app_config.router, prefix="/api/v1/config", tags=["config"])
app.include_router(logging_router.router, prefix="/api/v1/logs", tags=["logging"])
app.include_router(demo_subjects.router, prefix="/api/v1/demo", tags=["demo-subjects"])
app.include_router(documents.router, prefix="/api/v1/demo", tags=["documents"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])
app.include_router(pipelines.router, prefix="/api/v1/pipelines", tags=["pipelines"])
app.include_router(entities.router, prefix="/api/v1/entities", tags=["entities"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(user_profiles.router, prefix="/api/v1/profiles", tags=["user-profiles"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(reference_lists.router, prefix="/api/v1/reference-lists", tags=["reference-lists"])


@app.get("/")
async def root():
    return {"message": "Admin API is running", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "admin-api"}