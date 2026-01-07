"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db

# Import routers
from app.routers import users, venues, sessions, collaboration

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Initialize database tables
    init_db()
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Shutting down...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(venues.router, prefix="/api/venues", tags=["venues"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(collaboration.router, prefix="/api", tags=["collaboration"])
