"""Authentication dependencies for FastAPI."""

from typing import Optional, Annotated, Dict, Any
from fastapi import Depends, HTTPException, status, Cookie, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import auth_config
from .jwt import decode_token


# Bearer token scheme for Swagger UI
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    access_token: Optional[str] = Cookie(None),
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Optional[Dict[str, Any]]:
    """Get current user from JWT token (optional - returns None if no auth)."""
    if not auth_config.auth_enabled:
        # Auth disabled - return a default user
        return {"email": "admin@localhost", "authenticated": False}
    
    # Try cookie first, then Authorization header
    token = access_token
    if not token and authorization:
        token = authorization.credentials
    
    if not token:
        return None
    
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return {"email": payload.get("sub"), "authenticated": True}
    except ValueError:
        return None


async def get_current_user(
    user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Get current user from JWT token (required)."""
    if not auth_config.auth_enabled:
        # Auth disabled - return a default user
        return {"email": "admin@localhost", "authenticated": False}
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def verify_mcp_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> str:
    """Verify MCP API key from header."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    
    if x_api_key != auth_config.mcp_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return x_api_key


# Type aliases for cleaner function signatures
CurrentUser = Annotated[Dict[str, Any], Depends(get_current_user)]
CurrentUserOptional = Annotated[Optional[Dict[str, Any]], Depends(get_current_user_optional)]
MCPApiKey = Annotated[str, Depends(verify_mcp_api_key)]