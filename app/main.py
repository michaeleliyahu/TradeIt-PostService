"""Main FastAPI application for Post Service."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.messaging.rabbitmq import rabbitmq_manager
from app.api.routers import health, posts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    Handles RabbitMQ connection lifecycle.
    """
    # Startup
    logger.info("Starting Post Service...")
    try:
        await rabbitmq_manager.connect()
        logger.info("RabbitMQ connection established")
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        # Continue without RabbitMQ for graceful degradation
    
    yield
    
    # Shutdown
    logger.info("Shutting down Post Service...")
    try:
        await rabbitmq_manager.disconnect()
        logger.info("RabbitMQ connection closed")
    except Exception as e:
        logger.error(f"Error closing RabbitMQ connection: {e}")


# Create FastAPI app with lifespan management
app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
    description="Post Service - Manage user posts with RabbitMQ messaging",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(posts.router)


@app.get("/")
async def root():
    """
    Root endpoint providing service information.
    
    Returns:
        dict: Service metadata
    """
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "description": "Post Service API for managing user posts"
    }