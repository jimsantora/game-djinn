"""Base platform integration class."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class PlatformError(Exception):
    """Base exception for platform integration errors."""
    pass


class RateLimitError(PlatformError):
    """Exception raised when rate limit is exceeded."""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


@dataclass
class GameData:
    """Standard game data structure across platforms."""
    title: str
    platform_game_id: str
    developer: Optional[str] = None
    publisher: Optional[str] = None
    release_date: Optional[datetime] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    genres: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    cover_image_url: Optional[str] = None
    background_image_url: Optional[str] = None
    screenshots: Optional[List[str]] = None
    metacritic_score: Optional[int] = None
    platform_score: Optional[int] = None
    platform_review_count: Optional[int] = None
    website_url: Optional[str] = None
    external_ids: Optional[Dict[str, Any]] = None
    playtime_hours: Optional[int] = None
    esrb_rating: Optional[str] = None
    esrb_descriptors: Optional[List[str]] = None
    platform_data: Optional[Dict[str, Any]] = None


@dataclass
class UserGameData:
    """User-specific game data structure."""
    game_data: GameData
    owned: bool = True
    owned_date: Optional[datetime] = None
    total_playtime_minutes: int = 0
    last_played_at: Optional[datetime] = None
    first_played_at: Optional[datetime] = None
    platform_data: Optional[Dict[str, Any]] = None


@dataclass
class AchievementData:
    """Achievement data structure."""
    platform_achievement_id: str
    title: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    points: int = 0
    rarity_percentage: Optional[float] = None
    is_hidden: bool = False


@dataclass
class UserAchievementData:
    """User achievement unlock data."""
    achievement_data: AchievementData
    unlocked_at: datetime
    progress_percentage: int = 100


@dataclass
class UserProfileData:
    """User profile data structure."""
    user_identifier: str
    display_name: str
    avatar_url: Optional[str] = None
    profile_url: Optional[str] = None
    profile_visibility: str = "public"
    member_since: Optional[datetime] = None
    total_games: Optional[int] = None
    total_playtime_minutes: Optional[int] = None
    platform_data: Optional[Dict[str, Any]] = None


class BasePlatform(ABC):
    """Abstract base class for platform integrations."""
    
    def __init__(self, platform_code: str, credentials: Dict[str, Any]):
        self.platform_code = platform_code
        self.credentials = credentials
        self.rate_limiter = None
        self.logger = logging.getLogger(f"{__name__}.{platform_code}")
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Platform display name."""
        pass
    
    @property
    @abstractmethod
    def requires_auth(self) -> bool:
        """Whether this platform requires user authentication."""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate platform credentials."""
        pass
    
    @abstractmethod
    async def get_user_profile(self, user_identifier: str) -> UserProfileData:
        """Get user profile information."""
        pass
    
    @abstractmethod
    async def get_user_games(
        self, 
        user_identifier: str,
        include_free_games: bool = True,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> AsyncGenerator[UserGameData, None]:
        """
        Get user's game library.
        
        Args:
            user_identifier: Platform-specific user ID
            include_free_games: Whether to include free games
            limit: Maximum number of games to return
            offset: Number of games to skip
            
        Yields:
            UserGameData objects for each game
        """
        pass
    
    @abstractmethod
    async def get_game_details(self, platform_game_id: str) -> GameData:
        """Get detailed game information."""
        pass
    
    @abstractmethod
    async def get_game_achievements(self, platform_game_id: str) -> List[AchievementData]:
        """Get game achievements/trophies."""
        pass
    
    @abstractmethod
    async def get_user_achievements(
        self, 
        user_identifier: str, 
        platform_game_id: str
    ) -> List[UserAchievementData]:
        """Get user's achievements for a specific game."""
        pass
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test platform connection and return status."""
        test_result = {
            "platform": self.platform_code,
            "connected": False,
            "error": None,
            "response_time_ms": None,
        }
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            is_valid = await self.validate_credentials()
            test_result["connected"] = is_valid
            
            if not is_valid:
                test_result["error"] = "Invalid credentials"
                
        except RateLimitError as e:
            test_result["error"] = f"Rate limited: {e}"
        except PlatformError as e:
            test_result["error"] = f"Platform error: {e}"
        except Exception as e:
            test_result["error"] = f"Unexpected error: {e}"
            self.logger.exception("Unexpected error during connection test")
        
        end_time = asyncio.get_event_loop().time()
        test_result["response_time_ms"] = round((end_time - start_time) * 1000, 2)
        
        return test_result
    
    async def sync_user_library(
        self,
        user_identifier: str,
        progress_callback: Optional[callable] = None,
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Sync user's complete game library.
        
        Args:
            user_identifier: Platform-specific user ID
            progress_callback: Optional callback for sync progress updates
            batch_size: Number of games to process in each batch
            
        Returns:
            Sync summary with statistics
        """
        sync_stats = {
            "games_processed": 0,
            "games_added": 0,
            "games_updated": 0,
            "achievements_synced": 0,
            "errors": [],
            "started_at": datetime.utcnow(),
            "completed_at": None,
        }
        
        try:
            # Get user profile first
            profile = await self.get_user_profile(user_identifier)
            self.logger.info(f"Starting sync for user: {profile.display_name}")
            
            # Process games in batches
            batch = []
            async for user_game in self.get_user_games(user_identifier):
                batch.append(user_game)
                sync_stats["games_processed"] += 1
                
                if len(batch) >= batch_size:
                    await self._process_game_batch(batch, sync_stats)
                    
                    if progress_callback:
                        await progress_callback(sync_stats)
                    
                    batch = []
            
            # Process remaining games
            if batch:
                await self._process_game_batch(batch, sync_stats)
            
            sync_stats["completed_at"] = datetime.utcnow()
            self.logger.info(f"Sync completed: {sync_stats}")
            
        except Exception as e:
            sync_stats["errors"].append(f"Sync failed: {e}")
            self.logger.exception("Error during library sync")
            raise
        
        return sync_stats
    
    async def _process_game_batch(self, batch: List[UserGameData], sync_stats: Dict[str, Any]):
        """Process a batch of games (to be overridden for database operations)."""
        # This would be implemented by the service layer that uses the platform
        # For now, just update stats
        sync_stats["games_added"] += len(batch)
    
    def _normalize_game_title(self, title: str) -> str:
        """Normalize game title for cross-platform matching."""
        import re
        
        # Remove special characters and normalize spacing
        normalized = re.sub(r'[^\w\s]', '', title.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Remove common suffixes
        suffixes = [
            'game of the year edition',
            'deluxe edition', 
            'complete edition',
            'definitive edition',
            'gold edition',
            'premium edition',
            'ultimate edition',
            'directors cut',
            'remastered',
            'hd',
        ]
        
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
                break
        
        return normalized