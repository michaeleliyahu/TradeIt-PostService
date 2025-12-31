"""Post repository for database operations."""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate, PostSearchQuery


class PostRepository:
    """
    Repository class for post-related database operations.
    
    Provides data access layer for post entities following
    the repository pattern for clean architecture.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_post(self, post_data: PostCreate, user_id: UUID) -> Post:
        """
        Create a new post in the database.
        
        Args:
            post_data: Post creation data
            user_id: ID of the user creating the post
            
        Returns:
            Created post instance
        """
        post = Post(
            user_id=user_id,
            title=post_data.title,
            content=post_data.content,
            tags=post_data.tags or []
        )
        
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        
        return post
    
    async def get_post_by_id(self, post_id: UUID) -> Optional[Post]:
        """
        Retrieve a post by its ID.
        
        Args:
            post_id: ID of the post to retrieve
            
        Returns:
            Post instance if found, None otherwise
        """
        stmt = select(Post).where(
            and_(Post.id == post_id, Post.is_active == True)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_posts_by_user(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 20
    ) -> tuple[List[Post], int]:
        """
        Retrieve posts by user ID with pagination.
        
        Args:
            user_id: ID of the user
            page: Page number (1-based)
            page_size: Number of posts per page
            
        Returns:
            Tuple of (posts list, total count)
        """
        offset = (page - 1) * page_size
        
        # Get posts
        stmt = (
            select(Post)
            .where(and_(Post.user_id == user_id, Post.is_active == True))
            .order_by(desc(Post.created_at))
            .offset(offset)
            .limit(page_size)
        )
        result = await self.db.execute(stmt)
        posts = result.scalars().all()
        
        # Get total count
        count_stmt = select(func.count(Post.id)).where(
            and_(Post.user_id == user_id, Post.is_active == True)
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        return list(posts), total
    
    async def search_posts(self, search_query: PostSearchQuery) -> tuple[List[Post], int]:
        """
        Search posts based on query parameters.
        
        Args:
            search_query: Search parameters
            
        Returns:
            Tuple of (posts list, total count)
        """
        # Build base query
        stmt = select(Post).where(Post.is_active == True)
        count_stmt = select(func.count(Post.id)).where(Post.is_active == True)
        
        # Apply filters
        filters = []
        
        if search_query.user_id:
            filters.append(Post.user_id == search_query.user_id)
        
        if search_query.query:
            search_term = f"%{search_query.query}%"
            filters.append(
                or_(
                    Post.title.ilike(search_term),
                    Post.content.ilike(search_term)
                )
            )
        
        if search_query.tags:
            # Check if any of the search tags are in the post's tags array
            filters.append(Post.tags.overlap(search_query.tags))
        
        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))
        
        # Apply pagination and ordering
        offset = (search_query.page - 1) * search_query.page_size
        stmt = stmt.order_by(desc(Post.created_at)).offset(offset).limit(search_query.page_size)
        
        # Execute queries
        result = await self.db.execute(stmt)
        posts = result.scalars().all()
        
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        return list(posts), total
    
    async def update_post(self, post: Post, post_data: PostUpdate) -> Post:
        """
        Update an existing post.
        
        Args:
            post: Post instance to update
            post_data: Update data
            
        Returns:
            Updated post instance
        """
        update_data = post_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(post, field, value)
        
        await self.db.commit()
        await self.db.refresh(post)
        
        return post
    
    async def delete_post(self, post: Post) -> None:
        """
        Soft delete a post (mark as inactive).
        
        Args:
            post: Post instance to delete
        """
        post.is_active = False
        await self.db.commit()
    
    async def increment_likes_count(self, post_id: UUID) -> None:
        """
        Increment the likes count for a post.
        
        Args:
            post_id: ID of the post
        """
        post = await self.get_post_by_id(post_id)
        if post:
            post.likes_count += 1
            await self.db.commit()
    
    async def increment_comments_count(self, post_id: UUID) -> None:
        """
        Increment the comments count for a post.
        
        Args:
            post_id: ID of the post
        """
        post = await self.get_post_by_id(post_id)
        if post:
            post.comments_count += 1
            await self.db.commit()