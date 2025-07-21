"""Library-related Pydantic schemas."""

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class LibraryCreate(BaseModel):
    """Schema for creating a new library."""
    platform_code: str = Field(..., description="Platform identifier (steam, xbox, etc.)")
    user_identifier: str = Field(..., description="Platform-specific user ID")
    display_name: str = Field(..., description="Friendly name for the library")
    credentials: Optional[Dict[str, Any]] = Field(None, description="Platform-specific credentials")


class LibraryUpdate(BaseModel):
    """Schema for updating a library."""
    display_name: Optional[str] = None
    is_active: Optional[bool] = None
    credentials: Optional[Dict[str, Any]] = None


class LibraryResponse(BaseModel):
    """Schema for library responses."""
    library_id: UUID
    platform_id: UUID
    platform_code: str
    platform_name: str
    user_identifier: str
    display_name: str
    is_active: bool
    last_sync_at: Optional[datetime]
    sync_status: Optional[str]
    games_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LibraryListResponse(BaseModel):
    """Schema for library list responses."""
    libraries: list[LibraryResponse]
    total: int