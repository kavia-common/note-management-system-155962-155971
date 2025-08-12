from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import init_db
from .routes.notes import router as notes_router

# Initialize settings
settings = get_settings()

# Tags metadata for OpenAPI
openapi_tags_metadata: List[dict] = [
    {
        "name": "Notes",
        "description": "Operations for creating, listing, fetching, updating, and deleting notes.",
    }
]

# Create FastAPI application with metadata for docs
app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    openapi_tags=openapi_tags_metadata,
)

# CORS configuration
allow_origins = settings.cors_allow_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize database schema on app startup."""
    init_db(settings.notes_db_path)


# Health check endpoint
# PUBLIC_INTERFACE
@app.get(
    "/",
    summary="Health Check",
    description="Basic health check endpoint to verify the service is running.",
)
def health_check():
    """Return basic health status."""
    return {"status": "ok", "app": settings.app_title, "version": settings.app_version}


# Register API routers
app.include_router(notes_router)
