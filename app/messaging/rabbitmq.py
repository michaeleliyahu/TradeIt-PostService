"""RabbitMQ connection management and messaging utilities."""
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from aio_pika import connect_robust, Message, ExchangeType
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractExchange
from app.core.config import settings

logger = logging.getLogger(__name__)


class RabbitMQManager:
    """
    RabbitMQ connection and messaging manager.
    
    Handles connection management, exchange setup, and message publishing
    for post-related events.
    """
    
    def __init__(self):
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.exchange: Optional[AbstractExchange] = None
        
    async def connect(self) -> None:
        """
        Establish connection to RabbitMQ server.
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            self.connection = await connect_robust(
                settings.rabbitmq_url,
                loop=asyncio.get_event_loop()
            )
            self.channel = await self.connection.channel()
            
            # Declare exchange for post events
            self.exchange = await self.channel.declare_exchange(
                settings.post_exchange,
                ExchangeType.TOPIC,
                durable=True
            )
            
            logger.info(f"Connected to RabbitMQ at {settings.rabbitmq_url}")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise ConnectionError(f"RabbitMQ connection failed: {e}")
    
    async def disconnect(self) -> None:
        """Close RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")
    
    async def publish_event(
        self, 
        event_data: Dict[str, Any], 
        routing_key: str = None
    ) -> None:
        """
        Publish an event to RabbitMQ exchange.
        
        Args:
            event_data: Event data to publish
            routing_key: Routing key for the message
            
        Raises:
            RuntimeError: If not connected to RabbitMQ
            Exception: If publishing fails
        """
        if not self.exchange:
            raise RuntimeError("Not connected to RabbitMQ")
        
        routing_key = routing_key or settings.post_routing_key
        
        try:
            message_body = json.dumps(event_data, default=str)
            message = Message(
                message_body.encode(),
                content_type="application/json",
                delivery_mode=2  # Make message persistent
            )
            
            await self.exchange.publish(
                message,
                routing_key=routing_key
            )
            
            logger.info(f"Published event: {event_data.get('event_type')} to {routing_key}")
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if RabbitMQ connection is healthy.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            return (
                self.connection and 
                not self.connection.is_closed and
                self.channel and
                not self.channel.is_closed
            )
        except Exception:
            return False


# Global RabbitMQ manager instance
rabbitmq_manager = RabbitMQManager()


async def get_rabbitmq_manager() -> RabbitMQManager:
    """
    Dependency to get RabbitMQ manager instance.
    
    Returns:
        RabbitMQManager: Global RabbitMQ manager instance
    """
    return rabbitmq_manager