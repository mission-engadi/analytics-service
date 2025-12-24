"""
API Dependencies.

Provides dependency injection for database sessions, authentication, etc.
"""
from typing import AsyncGenerator, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal

# Security
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency for getting current authenticated user.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Current user information
        
    Raises:
        HTTPException: If authentication fails
    """
    # TODO: Implement actual JWT token validation with Auth Service
    # For now, return a mock user
    token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mock user (replace with actual validation)
    return {
        "id": "mock-user-id",
        "username": "mock-user",
        "email": "mock@example.com"
    }


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Dependency for getting current user (optional).
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Current user information or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
