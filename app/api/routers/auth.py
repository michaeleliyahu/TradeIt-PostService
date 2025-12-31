"""Authentication dependency for API routes."""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
from app.core.security import get_user_id_from_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    Extract and validate current user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        UUID: Current user ID
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        user_id_str = get_user_id_from_token(credentials.credentials)
        return UUID(user_id_str)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid user ID format: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UUID]:
    """
    Extract user ID from token if present, otherwise return None.
    Used for endpoints that work for both authenticated and unauthenticated users.
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        Optional[UUID]: User ID if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        user_id_str = get_user_id_from_token(credentials.credentials)
        return UUID(user_id_str)
    except Exception:
        return None