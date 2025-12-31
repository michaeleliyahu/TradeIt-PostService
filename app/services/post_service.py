"""Post service for business logic operations."""
import logging
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.post import PostRepository
from app.messaging.events import EventPublisher
from app.schemas.post import (
    PostCreate, 
    PostUpdate, 
    PostResponse, 
    PostListResponse, 
    PostSearchQuery
)
from app.models.post import Post

logger = logging.getLogger(__name__)


class PostService:
    """
    Service class for post-related business logic.
    
    Handles business operations for posts including creation,
    updates, deletion, and search functionality.
    """
    
    def __init__(
        self, 
        post_repository: PostRepository, 
        event_publisher: EventPublisher
    ):
        self.post_repository = post_repository
        self.event_publisher = event_publisher
    
    async def create_post(self, post_data: PostCreate, user_id: UUID) -> PostResponse:
        """
        Create a new post.
        
        Args:
            post_data: Post creation data
            user_id: ID of the user creating the post
            
        Returns:
            Created post response data
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            # Create post in database
            post = await self.post_repository.create_post(post_data, user_id)
            
            # Publish post creation event
            await self.event_publisher.publish_post_created(
                post_id=post.id,
                user_id=post.user_id,
                title=post.title,
                content=post.content,
                tags=post.tags
            )
            
            logger.info(f"Post created successfully: {post.id}")
            
            return PostResponse.model_validate(post)
            
        except Exception as e:
            logger.error(f"Failed to create post: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create post"
            )
    
    async def get_post(self, post_id: UUID) -> PostResponse:
        """
        Get a post by ID.
        
        Args:
            post_id: ID of the post to retrieve
            
        Returns:
            Post response data
            
        Raises:
            HTTPException: If post not found
        """
        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        return PostResponse.model_validate(post)
    
    async def get_user_posts(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 20
    ) -> PostListResponse:
        """
        Get posts by user ID with pagination.
        
        Args:
            user_id: ID of the user
            page: Page number
            page_size: Number of posts per page
            
        Returns:
            Paginated list of posts
        """
        posts, total = await self.post_repository.get_posts_by_user(
            user_id, page, page_size
        )
        
        return PostListResponse(
            items=[PostResponse.model_validate(post) for post in posts],
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total,
            has_prev=page > 1
        )
    
    async def search_posts(self, search_query: PostSearchQuery) -> PostListResponse:
        """
        Search posts based on query parameters.
        
        Args:
            search_query: Search parameters
            
        Returns:
            Paginated search results
        """
        posts, total = await self.post_repository.search_posts(search_query)
        
        return PostListResponse(
            items=[PostResponse.model_validate(post) for post in posts],
            total=total,
            page=search_query.page,
            page_size=search_query.page_size,
            has_next=(search_query.page * search_query.page_size) < total,
            has_prev=search_query.page > 1
        )
    
    async def update_post(
        self, 
        post_id: UUID, 
        post_data: PostUpdate, 
        user_id: UUID
    ) -> PostResponse:
        """
        Update an existing post.
        
        Args:
            post_id: ID of the post to update
            post_data: Update data
            user_id: ID of the user requesting the update
            
        Returns:
            Updated post response data
            
        Raises:
            HTTPException: If post not found or user not authorized
        """
        # Get existing post
        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check if user owns the post
        if post.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this post"
            )
        
        # Store original values for change tracking
        original_data = {
            "title": post.title,
            "content": post.content,
            "tags": post.tags
        }
        
        # Update post
        updated_post = await self.post_repository.update_post(post, post_data)
        
        # Determine changes for event
        changes = {}
        update_dict = post_data.model_dump(exclude_unset=True)
        for field, new_value in update_dict.items():
            if original_data.get(field) != new_value:
                changes[field] = {
                    "old": original_data.get(field),
                    "new": new_value
                }
        
        # Publish update event if there are changes
        if changes:
            await self.event_publisher.publish_post_updated(
                post_id=updated_post.id,
                user_id=user_id,
                changes=changes
            )
        
        logger.info(f"Post updated successfully: {post_id}")
        
        return PostResponse.model_validate(updated_post)
    
    async def delete_post(self, post_id: UUID, user_id: UUID) -> None:
        """
        Delete a post.
        
        Args:
            post_id: ID of the post to delete
            user_id: ID of the user requesting the deletion
            
        Raises:
            HTTPException: If post not found or user not authorized
        """
        # Get existing post
        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check if user owns the post
        if post.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this post"
            )
        
        # Soft delete post
        await self.post_repository.delete_post(post)
        
        # Publish deletion event
        await self.event_publisher.publish_post_deleted(
            post_id=post_id,
            user_id=user_id
        )
        
        logger.info(f"Post deleted successfully: {post_id}")


def create_post_service(
    db: AsyncSession, 
    event_publisher: EventPublisher
) -> PostService:
    """
    Factory function to create PostService instance.
    
    Args:
        db: Database session
        event_publisher: Event publisher instance
        
    Returns:
        PostService instance
    """
    post_repository = PostRepository(db)
    return PostService(post_repository, event_publisher)