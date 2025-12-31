"""Pydantic schemas for post-related operations."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class PostCreate(BaseModel):
    """Schema for creating a new post."""
    title: str = Field(..., min_length=1, max_length=255, description="Post title")
    content: str = Field(..., min_length=1, description="Post content")
    tags: Optional[List[str]] = Field(default=None, description="Optional list of tags")


class PostUpdate(BaseModel):
    """Schema for updating an existing post."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Post title")
    content: Optional[str] = Field(None, min_length=1, description="Post content")
    tags: Optional[List[str]] = Field(None, description="Optional list of tags")


class PostResponse(BaseModel):
    """Schema for post response data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    title: str
    content: str
    tags: Optional[List[str]]
    likes_count: int
    comments_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PostListResponse(BaseModel):
    """Schema for paginated post list response."""
    items: List[PostResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool


class PostSearchQuery(BaseModel):
    """Schema for post search parameters."""
    query: Optional[str] = Field(None, description="Search query for title and content")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    user_id: Optional[UUID] = Field(None, description="Filter by user ID")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


# Event schemas for RabbitMQ messaging
class PostEvent(BaseModel):
    """Base schema for post events."""
    event_type: str
    post_id: UUID
    user_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PostCreatedEvent(PostEvent):
    """Schema for post creation events."""
    event_type: str = "post.created"
    title: str
    content: str
    tags: Optional[List[str]]


class PostUpdatedEvent(PostEvent):
    """Schema for post update events."""
    event_type: str = "post.updated"
    changes: dict


class PostDeletedEvent(PostEvent):
    """Schema for post deletion events."""
    event_type: str = "post.deleted"