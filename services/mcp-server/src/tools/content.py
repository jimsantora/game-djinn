"""Content filtering MCP tools."""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Game, UserGame, UserLibrary
from database import get_session

logger = logging.getLogger(__name__)


async def filter_by_content_rating(
    max_rating: str,
    library_id: Optional[str] = None,
    exclude_descriptors: Optional[List[str]] = None,
    include_unrated: bool = True
) -> Dict[str, Any]:
    """
    Filter games by ESRB content ratings for family-friendly viewing.
    
    Args:
        max_rating: Maximum ESRB rating (E, E10+, T, M)
        library_id: Optional specific library to filter
        exclude_descriptors: Exclude games with specific content descriptors
        include_unrated: Include unrated games
        
    Returns:
        Filtered games that meet content rating requirements
    """
    try:
        # Define ESRB rating hierarchy
        rating_hierarchy = {
            "E": 1,      # Everyone
            "E10+": 2,   # Everyone 10+
            "T": 3,      # Teen
            "M": 4,      # Mature
            "AO": 5,     # Adults Only
            "RP": 0      # Rating Pending
        }
        
        max_rating_value = rating_hierarchy.get(max_rating.upper())
        if max_rating_value is None:
            return {
                "error": f"Invalid ESRB rating '{max_rating}'",
                "valid_ratings": list(rating_hierarchy.keys()),
                "rating_guide": {
                    "E": "Everyone - Content suitable for all ages",
                    "E10+": "Everyone 10+ - Content suitable for ages 10 and older",
                    "T": "Teen - Content suitable for ages 13 and older", 
                    "M": "Mature - Content suitable for ages 17 and older",
                    "AO": "Adults Only - Content suitable only for adults",
                    "RP": "Rating Pending - Not yet rated"
                }
            }
        
        async for session in get_session():
            # Build query based on whether we're filtering a specific library
            if library_id:
                # Filter user's library
                query_base = select(Game, UserGame, UserLibrary).join(
                    UserGame, Game.game_id == UserGame.game_id
                ).join(
                    UserLibrary, UserGame.library_id == UserLibrary.library_id
                ).where(UserLibrary.library_id == library_id)
            else:
                # Filter all games
                query_base = select(Game)
            
            conditions = []
            
            # Rating filter
            allowed_ratings = [
                rating for rating, value in rating_hierarchy.items()
                if value <= max_rating_value and value > 0
            ]
            
            rating_conditions = [Game.esrb_rating.in_(allowed_ratings)]
            
            if include_unrated:
                rating_conditions.append(Game.esrb_rating.is_(None))
            
            conditions.append(or_(*rating_conditions))
            
            # Exclude specific content descriptors
            if exclude_descriptors:
                for descriptor in exclude_descriptors:
                    # Check if the descriptor exists in the JSONB array
                    conditions.append(
                        ~Game.esrb_descriptors.op('?')(descriptor)
                    )
            
            # Apply all conditions
            if conditions:
                query_base = query_base.where(and_(*conditions))
            
            # Execute query
            result = await session.execute(query_base)
            
            filtered_games = []
            total_games_checked = 0
            
            if library_id:
                # Process user games
                rows = result.all()
                total_games_checked = await _count_total_library_games(session, library_id)
                
                for game, user_game, library in rows:
                    filtered_games.append(_format_filtered_game(game, user_game))
            else:
                # Process all games
                games = result.scalars().all()
                total_games_checked = len(games)
                
                for game in games:
                    filtered_games.append(_format_filtered_game(game))
            
            # Generate content warnings
            content_warnings = _generate_content_warnings(max_rating, exclude_descriptors)
            
            return {
                "filtered_games": filtered_games,
                "filter_criteria": {
                    "max_rating": max_rating.upper(),
                    "excluded_descriptors": exclude_descriptors or [],
                    "include_unrated": include_unrated,
                    "total_games_filtered": total_games_checked,
                    "games_passed_filter": len(filtered_games)
                },
                "content_warnings": content_warnings,
                "rating_info": {
                    "applied_rating": max_rating.upper(),
                    "description": _get_rating_description(max_rating.upper()),
                    "allowed_ratings": allowed_ratings
                },
                "summary": f"Found {len(filtered_games)} games suitable for {max_rating.upper()} rating from {total_games_checked} total games"
            }
            
    except Exception as e:
        logger.error(f"Error filtering by content rating: {e}")
        return {
            "error": f"Content filtering failed: {str(e)}",
            "max_rating": max_rating,
            "library_id": library_id
        }


async def _count_total_library_games(session: AsyncSession, library_id: str) -> int:
    """Count total games in a library."""
    try:
        count_result = await session.execute(
            select(func.count(UserGame.user_game_id)).where(
                UserGame.library_id == library_id
            )
        )
        return count_result.scalar() or 0
    except Exception:
        return 0


def _format_filtered_game(game: Game, user_game: Optional = None) -> Dict[str, Any]:
    """Format game data for content filtering results."""
    result = {
        "game_id": str(game.game_id),
        "title": game.title,
        "esrb_rating": game.esrb_rating or "Unrated",
        "esrb_descriptors": game.esrb_descriptors or [],
        "genres": game.genres or [],
        "developer": game.developer,
        "release_date": game.release_date.isoformat() if game.release_date else None,
        "cover_image_url": game.cover_image_url,
        "safe_for_rating": game.esrb_rating or "Unrated"
    }
    
    if user_game:
        result["user_owned"] = user_game.owned
        result["user_status"] = user_game.game_status
        result["total_playtime_minutes"] = user_game.total_playtime_minutes
    
    return result


def _generate_content_warnings(max_rating: str, exclude_descriptors: Optional[List[str]]) -> List[str]:
    """Generate content warnings for filtered results."""
    warnings = []
    
    if max_rating.upper() in ["E", "E10+"]:
        warnings.append(
            "Some games may have user-generated content not covered by ESRB ratings"
        )
        warnings.append(
            "Online interactions are not rated by the ESRB"
        )
    
    if not exclude_descriptors or len(exclude_descriptors) == 0:
        warnings.append(
            "No content descriptors were excluded - games may contain various content types"
        )
    
    if max_rating.upper() == "RP":
        warnings.append(
            "Rating Pending games may receive different final ratings"
        )
    
    return warnings


def _get_rating_description(rating: str) -> str:
    """Get description for ESRB rating."""
    descriptions = {
        "E": "Everyone - Content suitable for all ages. May contain minimal cartoon, fantasy or mild violence and/or infrequent use of mild language.",
        "E10+": "Everyone 10+ - Content suitable for ages 10 and older. May contain more cartoon, fantasy or mild violence, mild language and/or minimal suggestive themes.",
        "T": "Teen - Content suitable for ages 13 and older. May contain violence, suggestive themes, crude humor, minimal blood, simulated gambling and/or infrequent use of strong language.",
        "M": "Mature 17+ - Content suitable for ages 17 and older. May contain intense violence, blood and gore, sexual themes and/or strong language.",
        "AO": "Adults Only 18+ - Content suitable only for adults ages 18 and older. May include prolonged scenes of intense violence, graphic and sadistic torture, nudity with sexual content.",
        "RP": "Rating Pending - Not yet assigned a final ESRB rating."
    }
    
    return descriptions.get(rating, "Unknown rating")