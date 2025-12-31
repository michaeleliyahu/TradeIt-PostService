"""Post model for SQLAlchemy ORM."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.db.base import Base


class Post(Base):
    """
    Post model representing user posts in the system.
    
    Attributes:
        id: Unique identifier for the post
        user_id: ID of the user who created the post
        title: Post title
        content: Post content/body
        tags: Optional list of tags associated with the post
        likes_count: Number of likes (denormalized for performance)
        comments_count: Number of comments (denormalized for performance)
        is_active: Whether the post is active/visible
        created_at: Post creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), nullable=True, default=list)
    likes_count = Column(Integer, nullable=False, default=0)
    comments_count = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """String representation of Post instance."""
        return f"<Post(id={self.id}, title='{self.title[:30]}...', user_id={self.user_id})>"