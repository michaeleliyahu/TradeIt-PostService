"""Health check router for Post Service."""
from fastapi import APIRouter, Depends
from app.messaging.rabbitmq import RabbitMQManager, get_rabbitmq_manager

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": "Post Service",
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health_check(
    rabbitmq: RabbitMQManager = Depends(get_rabbitmq_manager)
):
    """
    Detailed health check including external dependencies.
    
    Args:
        rabbitmq: RabbitMQ manager dependency
        
    Returns:
        dict: Detailed health status including dependencies
    """
    rabbitmq_healthy = await rabbitmq.health_check()
    
    return {
        "status": "healthy" if rabbitmq_healthy else "degraded",
        "service": "Post Service",
        "version": "1.0.0",
        "dependencies": {
            "rabbitmq": "healthy" if rabbitmq_healthy else "unhealthy"
        }
    }