"""Game-related Pydantic schemas."""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field


class GameBase(BaseModel):
    """Base game information."""
    game_id: UUID
    title: str
    description: Optional[str] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    genres: Optional[List[str]] = None
    platforms_available: Optional[List[str]] = None
    release_date: Optional[date] = None
    metacritic_score: Optional[int] = None
    steam_score: Optional[int] = None
    esrb_rating: Optional[str] = None
    esrb_descriptors: Optional[List[str]] = None
    cover_image_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class GameListItem(GameBase):
    """Game item for list views."""
    user_data: Optional[Dict[str, Any]] = None  # Simplified user data for lists


class GameDetail(GameBase):
    """Detailed game information."""
    screenshots: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    achievements_total: Optional[int] = None
    playtime_main_hours: Optional[float] = None
    playtime_extras_hours: Optional[float] = None
    playtime_completionist_hours: Optional[float] = None
    system_requirements: Optional[Dict[str, Any]] = None
    platform_metadata: Optional[Dict[str, Any]] = None
    
    # User-specific data (if library_id provided)
    user_game_data: Optional["UserGameData"] = None


class UserGameData(BaseModel):
    """User-specific game data."""
    owned: bool = False
    wishlisted: bool = False
    total_playtime_minutes: int = 0
    last_played_at: Optional[datetime] = None
    first_played_at: Optional[datetime] = None
    user_rating: Optional[int] = None
    game_status: Optional[str] = None
    completion_percentage: Optional[float] = None
    achievements_unlocked: Optional[int] = None
    is_favorite: bool = False
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class GameSearchRequest(BaseModel):
    """Game search request parameters."""
    query: str = Field(..., min_length=1, description="Search query")
    platforms: Optional[List[str]] = Field(None, description="Filter by platforms")
    genres: Optional[List[str]] = Field(None, description="Filter by genres")
    min_rating: Optional[int] = Field(None, ge=0, le=100, description="Minimum Metacritic score")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    owned_only: bool = Field(False, description="Show only owned games")
    library_id: Optional[UUID] = Field(None, description="Filter by specific library")
    sort_by: str = Field("relevance", description="Sort order")
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Results per page")


class GameSearchResponse(BaseModel):
    """Game search response."""
    games: List[GameListItem]
    total: int
    page: int
    pages: int
    query: str
    filters_applied: Dict[str, Any]


# Update forward references
GameDetail.model_rebuild()