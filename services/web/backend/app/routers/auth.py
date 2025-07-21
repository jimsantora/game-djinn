"""Authentication endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Response, Cookie
from pydantic import BaseModel, EmailStr

from app.auth.config import auth_config
from app.auth.jwt import verify_admin_credentials, create_access_token, create_refresh_token, decode_token
from app.auth.dependencies import CurrentUserOptional


router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    email: str
    authenticated: bool


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, response: Response) -> TokenResponse:
    """Login with admin credentials."""
    if not auth_config.auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authentication is disabled"
        )
    
    if not verify_admin_credentials(credentials.email, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": credentials.email})
    refresh_token = create_refresh_token(data={"sub": credentials.email})
    
    # Set httpOnly cookie for access token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Enable in production with HTTPS
        samesite="lax",
        max_age=auth_config.access_token_expire_minutes * 60
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    response: Response
) -> TokenResponse:
    """Refresh access token using refresh token."""
    if not auth_config.auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authentication is disabled"
        )
    
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")
        
        email = payload.get("sub")
        if not email:
            raise ValueError("Invalid token payload")
        
        # Create new tokens
        new_access_token = create_access_token(data={"sub": email})
        new_refresh_token = create_refresh_token(data={"sub": email})
        
        # Update cookie
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=auth_config.access_token_expire_minutes * 60
        )
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout(response: Response) -> Dict[str, str]:
    """Logout and clear authentication."""
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUserOptional
) -> UserResponse:
    """Get current user information."""
    if not current_user:
        if not auth_config.auth_enabled:
            return UserResponse(email="admin@localhost", authenticated=False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return UserResponse(
        email=current_user["email"],
        authenticated=current_user["authenticated"]
    )


@router.get("/config")
async def get_auth_config() -> Dict[str, Any]:
    """Get authentication configuration (public endpoint)."""
    return {
        "auth_enabled": auth_config.auth_enabled,
        "token_expire_minutes": auth_config.access_token_expire_minutes
    }