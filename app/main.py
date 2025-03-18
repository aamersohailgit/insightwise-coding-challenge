import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import config
from app.db import init_db, close_db
from app.middleware import setup_middlewares
from app.core.logging_config import setup_logging
from app.errors import app_error_handler, validation_error_handler, generic_error_handler
from app.utils.errors import AppError
from app.features.items.routes import router as items_router
from app.features.geo.routes import router as geo_router
from app.auth.routes import router as auth_router

# Initialize logging
setup_logging(app_name="items_api")
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=config.PROJECT_NAME,
    openapi_url=f"{config.API_V1_PREFIX}/openapi.json",
    docs_url=f"{config.API_V1_PREFIX}/docs",
    redoc_url=f"{config.API_V1_PREFIX}/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up other middleware
setup_middlewares(app)

# Set up error handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Include routers
app.include_router(items_router, prefix=config.API_V1_PREFIX)
app.include_router(geo_router, prefix=config.API_V1_PREFIX)
app.include_router(auth_router, prefix=config.API_V1_PREFIX)

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    logger.info("Starting up application")
    # Initialize database
    init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    logger.info("Shutting down application")
    # Close database connection
    close_db()

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Items API",
        "docs": f"{config.API_V1_PREFIX}/docs",
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
