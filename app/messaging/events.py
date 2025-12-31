"""Event publishing utilities for post service."""
import logging
from typing import Dict, Any, Optional
from uuid import UUID
from app.messaging.rabbitmq import rabbitmq_manager
from app.schemas.post import (
    PostCreatedEvent, 
    PostUpdatedEvent, 
    PostDeletedEvent
)

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Event publisher for post-related events.
    
    Handles publishing of post lifecycle events to RabbitMQ
    for other services to consume.
    """
    
    def __init__(self):
        self.manager = rabbitmq_manager
    
    async def publish_post_created(
        self, 
        post_id: UUID, 
        user_id: UUID, 
        title: str, 
        content: str, 
        tags: Optional[list] = None
    ) -> None:
        """
        Publish post creation event.
        
        Args:
            post_id: ID of the created post
            user_id: ID of the user who created the post
            title: Post title
            content: Post content
            tags: Optional list of tags
        """
        try:
            event = PostCreatedEvent(
                post_id=post_id,
                user_id=user_id,
                title=title,
                content=content,
                tags=tags
            )
            
            await self.manager.publish_event(
                event_data=event.model_dump(),
                routing_key="post.created"
            )
            
            logger.info(f"Published post created event for post {post_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish post created event: {e}")
            # Don't raise - event publishing should not break the main flow
    
    async def publish_post_updated(
        self, 
        post_id: UUID, 
        user_id: UUID, 
        changes: Dict[str, Any]
    ) -> None:
        """
        Publish post update event.
        
        Args:
            post_id: ID of the updated post
            user_id: ID of the user who updated the post
            changes: Dictionary of changes made to the post
        """
        try:
            event = PostUpdatedEvent(
                post_id=post_id,
                user_id=user_id,
                changes=changes
            )
            
            await self.manager.publish_event(
                event_data=event.model_dump(),
                routing_key="post.updated"
            )
            
            logger.info(f"Published post updated event for post {post_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish post updated event: {e}")
    
    async def publish_post_deleted(
        self, 
        post_id: UUID, 
        user_id: UUID
    ) -> None:
        """
        Publish post deletion event.
        
        Args:
            post_id: ID of the deleted post
            user_id: ID of the user who deleted the post
        """
        try:
            event = PostDeletedEvent(
                post_id=post_id,
                user_id=user_id
            )
            
            await self.manager.publish_event(
                event_data=event.model_dump(),
                routing_key="post.deleted"
            )
            
            logger.info(f"Published post deleted event for post {post_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish post deleted event: {e}")


# Global event publisher instance
event_publisher = EventPublisher()


def get_event_publisher() -> EventPublisher:
    """
    Dependency to get event publisher instance.
    
    Returns:
        EventPublisher: Global event publisher instance
    """
    return event_publisher