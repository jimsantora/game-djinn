"""MCP tools for Game Djinn."""

from .platforms import get_supported_platforms, add_platform_library
from .sync import sync_platform_library
from .games import search_games, get_game_details
from .analytics import analyze_gaming_patterns
from .content import filter_by_content_rating
from .recommendations import recommend_games

__all__ = [
    "get_supported_platforms",
    "add_platform_library", 
    "sync_platform_library",
    "search_games",
    "get_game_details",
    "analyze_gaming_patterns",
    "filter_by_content_rating",
    "recommend_games",
]