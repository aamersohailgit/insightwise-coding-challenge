import logging
import asyncio

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import test, geo_test, items
from app.db.mongo import init_db, close_db
from app.core.logging_config import setup_logging, get_logger
from app.workers.geo_worker import geo_worker
from app.api.middlewares.request_logging import add_middleware as add_request_logging_middleware

# Initialize logging first
setup_logging(app_name="items_api")
logger = get_logger(__name__)

app = FastAPI(
    title="Items API",
    description="API for managing items",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
add_request_logging_middleware(app)

# Register routes
app.include_router(test.router)
app.include_router(geo_test.router)
app.include_router(items.router)

# Background worker task
worker_task = None

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log and handle validation errors."""
    errors = exc.errors()
    error_messages = []

    for error in errors:
        location = " -> ".join([str(loc) for loc in error["loc"]])
        message = f"{location}: {error['msg']}"
        error_messages.append(message)

    error_str = ", ".join(error_messages)
    logger.error(f"Validation error: {error_str}",
                extra={"validation_errors": errors, "path": request.url.path})

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    global worker_task

    logger.info("Starting up application")

    # Initialize database
    init_db()

    # Start geo worker in the background
    worker_task = asyncio.create_task(geo_worker.start())
    logger.info("Geo worker started")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    global worker_task

    logger.info("Shutting down application")

    # Stop geo worker
    if worker_task:
        await geo_worker.stop()
        # Wait for worker to complete gracefully
        try:
            await asyncio.wait_for(worker_task, timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Geo worker did not shut down gracefully, forcing shutdown")
        worker_task = None

    # Close database connection
    close_db()

    logger.info("Application shutdown complete")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
