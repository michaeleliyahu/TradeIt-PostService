"""Posts router for CRUD operations."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.messaging.events import get_event_publisher, EventPublisher
from app.services.post_service import create_post_service, PostService
from app.api.routers.auth import get_current_user, get_optional_user
from app.schemas.post import (
    PostCreate, 
    PostUpdate, 
    PostResponse, 
    PostListResponse, 
    PostSearchQuery
)

router = APIRouter(prefix="/posts", tags=["posts"])


def get_post_service(
    db: AsyncSession = Depends(get_db),
    event_publisher: EventPublisher = Depends(get_event_publisher)
) -> PostService:
    """Dependency to get post service instance."""
    return create_post_service(db, event_publisher)


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: UUID = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service)
):
    """
    Create a new post.
    
    Args:
        post_data: Post creation data
        current_user: Current authenticated user ID
        post_service: Post service dependency
        
    Returns:
        PostResponse: Created post data
    """
    return await post_service.create_post(post_data, current_user)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: UUID,
    post_service: PostService = Depends(get_post_service)
):
    """
    Get a specific post by ID.
    
    Args:
        post_id: ID of the post to retrieve
        post_service: Post service dependency
        
    Returns:
        PostResponse: Post data
    """
    return await post_service.get_post(post_id)


@router.get("/", response_model=PostListResponse)
async def search_posts(
    query: str = Query(None, description="Search query for title and content"),
    tags: List[str] = Query(None, description="Filter by tags"),
    user_id: UUID = Query(None, description="Filter by user ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    post_service: PostService = Depends(get_post_service)
):
    """
    Search posts with optional filters and pagination.
    
    Args:
        query: Optional search query for title and content
        tags: Optional list of tags to filter by
        user_id: Optional user ID to filter by
        page: Page number for pagination
        page_size: Number of items per page
        post_service: Post service dependency
        
    Returns:
        PostListResponse: Paginated search results
    """
    search_query = PostSearchQuery(
        query=query,
        tags=tags,
        user_id=user_id,
        page=page,
        page_size=page_size
    )
    
    return await post_service.search_posts(search_query)


@router.get("/users/{user_id}", response_model=PostListResponse)
async def get_user_posts(
    user_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    post_service: PostService = Depends(get_post_service)
):
    """
    Get posts by a specific user with pagination.
    
    Args:
        user_id: ID of the user whose posts to retrieve
        page: Page number for pagination
        page_size: Number of items per page
        post_service: Post service dependency
        
    Returns:
        PostListResponse: Paginated user posts
    """
    return await post_service.get_user_posts(user_id, page, page_size)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    post_data: PostUpdate,
    current_user: UUID = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service)
):
    """
    Update an existing post.
    
    Args:
        post_id: ID of the post to update
        post_data: Post update data
        current_user: Current authenticated user ID
        post_service: Post service dependency
        
    Returns:
        PostResponse: Updated post data
    """
    return await post_service.update_post(post_id, post_data, current_user)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    current_user: UUID = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service)
):
    """
    Delete a post.
    
    Args:
        post_id: ID of the post to delete
        current_user: Current authenticated user ID
        post_service: Post service dependency
    """
    await post_service.delete_post(post_id, current_user)


@router.get("/me/posts", response_model=PostListResponse)
async def get_my_posts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UUID = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service)
):
    """
    Get posts of the current authenticated user.
    
    Args:
        page: Page number for pagination
        page_size: Number of items per page
        current_user: Current authenticated user ID
        post_service: Post service dependency
        
    Returns:
        PostListResponse: Paginated current user posts
    """
    return await post_service.get_user_posts(current_user, page, page_size)