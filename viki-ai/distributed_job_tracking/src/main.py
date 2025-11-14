from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from middleware.auto_headers import AutoHeadersMiddleware
from routers.jobs import router as jobs_router
from routers.tracking import router as tracking_router

app = FastAPI(title="Distributed Job Tracking API")

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
    return {"message": "Welcome to Distributed Job Tracking API"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include the API router
app.include_router(api_router)
# Include the jobs router
app.include_router(jobs_router, prefix="/api")
# Include the tracking router
app.include_router(tracking_router, prefix="/api")
