import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import test, geo_test, items
from app.db.mongo import init_db, close_db

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Items API",
    description="API for managing items",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(test.router)
app.include_router(geo_test.router)
app.include_router(items.router)

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    logger.info("Starting up application")
    init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    logger.info("Shutting down application")
    close_db()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
