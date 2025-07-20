"""Game search and details MCP tools."""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Game, UserGame, UserLibrary, Platform
from database import get_session

logger = logging.getLogger(__name__)


async def search_games(
    query: str,
    platform_filter: Optional[List[str]] = None,
    status_filter: Optional[List[str]] = None,
    rating_filter: Optional[Dict[str, int]] = None,
    genre_filter: Optional[List[str]] = None,
    owned_only: bool = False,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search for games across all platforms and libraries.
    
    Args:
        query: Search terms
        platform_filter: Filter by platform codes
        status_filter: Filter by game status (unplayed, playing, completed, etc.)
        rating_filter: Filter by ratings (min/max metacritic, user rating)
        genre_filter: Filter by genres
        owned_only: Show only owned games
        limit: Max results (default: 20, max: 100)
        
    Returns:
        Search results with games and metadata
    """
    try:
        limit = min(limit, 100)  # Cap at 100 results
        
        async for session in get_session():
            # Build the base query
            if owned_only:
                # Search in user games (owned only)
                query_base = select(Game, UserGame, UserLibrary, Platform).join(
                    UserGame, Game.game_id == UserGame.game_id
                ).join(
                    UserLibrary, UserGame.library_id == UserLibrary.library_id
                ).join(
                    Platform, UserLibrary.platform_id == Platform.platform_id
                )
            else:
                # Search all games
                query_base = select(Game).outerjoin(
                    UserGame, Game.game_id == UserGame.game_id
                ).outerjoin(
                    UserLibrary, UserGame.library_id == UserLibrary.library_id
                ).outerjoin(
                    Platform, UserLibrary.platform_id == Platform.platform_id
                )
            
            conditions = []
            
            # Text search
            if query.strip():
                search_condition = or_(
                    Game.title.ilike(f"%{query}%"),
                    Game.normalized_title.ilike(f"%{query}%"),
                    Game.developer.ilike(f"%{query}%"),
                    Game.publisher.ilike(f"%{query}%"),
                    Game.description.ilike(f"%{query}%")
                )
                conditions.append(search_condition)
            
            # Platform filter
            if platform_filter:
                if owned_only:
                    conditions.append(Platform.platform_code.in_(platform_filter))
                else:
                    # For all games, check platforms_available JSONB
                    platform_conditions = []
                    for platform in platform_filter:
                        platform_conditions.append(
                            Game.platforms_available.op('?')(platform)
                        )
                    if platform_conditions:
                        conditions.append(or_(*platform_conditions))
            
            # Genre filter
            if genre_filter:
                genre_conditions = []
                for genre in genre_filter:
                    genre_conditions.append(Game.genres.op('?')(genre))
                if genre_conditions:
                    conditions.append(or_(*genre_conditions))
            
            # Rating filter
            if rating_filter:
                if "min_metacritic" in rating_filter:
                    conditions.append(Game.metacritic_score >= rating_filter["min_metacritic"])
                if "max_metacritic" in rating_filter:
                    conditions.append(Game.metacritic_score <= rating_filter["max_metacritic"])
                if "min_user_rating" in rating_filter and owned_only:
                    conditions.append(UserGame.user_rating >= rating_filter["min_user_rating"])
            
            # Status filter (only for owned games)
            if status_filter and owned_only:
                conditions.append(UserGame.game_status.in_(status_filter))
            
            # Apply all conditions
            if conditions:
                query_base = query_base.where(and_(*conditions))
            
            # Add ordering
            query_base = query_base.order_by(Game.title).limit(limit)
            
            # Execute query
            result = await session.execute(query_base)
            
            games = []
            if owned_only:
                rows = result.all()
                for game, user_game, library, platform in rows:
                    games.append(_format_game_result(game, user_game, library, platform))
            else:
                game_rows = result.scalars().all()
                for game in game_rows:
                    games.append(_format_game_result(game))
            
            # Get total count (simplified)
            total_count = len(games)
            
            return {
                "games": games,
                "total_results": total_count,
                "search_query": query,
                "filters_applied": {
                    "platforms": platform_filter,
                    "status": status_filter,
                    "genres": genre_filter,
                    "rating": rating_filter,
                    "owned_only": owned_only
                },
                "results_count": len(games),
                "search_time_ms": 0  # TODO: Add actual timing
            }
            
    except Exception as e:
        logger.error(f"Error searching games: {e}")
        return {
            "error": f"Search failed: {str(e)}",
            "games": [],
            "total_results": 0,
            "search_query": query
        }


async def get_game_details(
    game_id: str,
    library_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get comprehensive information about a specific game.
    
    Args:
        game_id: UUID of the game
        library_id: Optional library ID to include user-specific data
        
    Returns:
        Detailed game information
    """
    try:
        async for session in get_session():
            # Get the game
            game_result = await session.execute(
                select(Game).where(Game.game_id == game_id)
            )
            game = game_result.scalar_one_or_none()
            
            if not game:
                return {
                    "error": f"Game with ID '{game_id}' not found",
                    "suggestion": "Use search_games to find games and get their IDs"
                }
            
            # Get user data if library_id provided
            user_data = None
            if library_id:
                user_game_result = await session.execute(
                    select(UserGame, UserLibrary, Platform).join(
                        UserLibrary, UserGame.library_id == UserLibrary.library_id
                    ).join(
                        Platform, UserLibrary.platform_id == Platform.platform_id
                    ).where(
                        and_(
                            UserGame.game_id == game_id,
                            UserGame.library_id == library_id
                        )
                    )
                )
                user_game_row = user_game_result.first()
                
                if user_game_row:
                    user_game, library, platform = user_game_row
                    user_data = {
                        "owned": user_game.owned,
                        "total_playtime_minutes": user_game.total_playtime_minutes,
                        "total_playtime_hours": round(user_game.total_playtime_minutes / 60, 1),
                        "last_played_at": user_game.last_played_at.isoformat() if user_game.last_played_at else None,
                        "first_played_at": user_game.first_played_at.isoformat() if user_game.first_played_at else None,
                        "game_status": user_game.game_status,
                        "user_rating": user_game.user_rating,
                        "is_favorite": user_game.is_favorite,
                        "user_notes": user_game.user_notes,
                        "platform": platform.platform_code,
                        "platform_name": platform.platform_name,
                        "library_name": library.display_name
                    }
            
            # Format game details
            game_details = {
                "game_id": str(game.game_id),
                "title": game.title,
                "slug": game.slug,
                "description": game.description,
                "short_description": game.short_description,
                "developer": game.developer,
                "publisher": game.publisher,
                "release_date": game.release_date.isoformat() if game.release_date else None,
                "genres": game.genres or [],
                "tags": game.tags or [],
                "platforms_available": game.platforms_available or [],
                "esrb_rating": game.esrb_rating,
                "esrb_descriptors": game.esrb_descriptors or [],
                "pegi_rating": game.pegi_rating,
                "metacritic_score": game.metacritic_score,
                "metacritic_url": game.metacritic_url,
                "steam_score": game.steam_score,
                "steam_review_count": game.steam_review_count,
                "media": {
                    "cover_image_url": game.cover_image_url,
                    "background_image_url": game.background_image_url,
                    "screenshots": game.screenshots or [],
                    "videos": game.videos or []
                },
                "external_ids": {
                    "steam_appid": game.steam_appid,
                    "gog_id": game.gog_id,
                    "epic_id": game.epic_id,
                    "xbox_id": game.xbox_id,
                    "psn_id": game.psn_id
                },
                "website_url": game.website_url,
                "playtime_estimates": {
                    "main_hours": game.playtime_main_hours,
                    "completionist_hours": game.playtime_completionist_hours
                },
                "created_at": game.created_at.isoformat(),
                "updated_at": game.updated_at.isoformat()
            }
            
            if user_data:
                game_details["user_data"] = user_data
            
            return game_details
            
    except Exception as e:
        logger.error(f"Error getting game details for {game_id}: {e}")
        return {
            "error": f"Failed to get game details: {str(e)}",
            "game_id": game_id
        }


def _format_game_result(game: Game, user_game: Optional = None, library: Optional = None, platform: Optional = None) -> Dict[str, Any]:
    """Format game data for search results."""
    result = {
        "game_id": str(game.game_id),
        "title": game.title,
        "developer": game.developer,
        "publisher": game.publisher,
        "release_date": game.release_date.isoformat() if game.release_date else None,
        "genres": game.genres or [],
        "esrb_rating": game.esrb_rating,
        "metacritic_score": game.metacritic_score,
        "steam_score": game.steam_score,
        "cover_image_url": game.cover_image_url,
        "platforms_available": game.platforms_available or []
    }
    
    if user_game and library and platform:
        result["owned_platforms"] = [platform.platform_code]
        result["user_status"] = user_game.game_status
        result["user_rating"] = user_game.user_rating
        result["total_playtime_hours"] = round(user_game.total_playtime_minutes / 60, 1)
        result["library_name"] = library.display_name
    
    return result