"""Game recommendation MCP tools."""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Game, UserGame, UserLibrary, Platform
from database import get_session

logger = logging.getLogger(__name__)


async def recommend_games(
    library_id: Optional[str] = None,
    criteria: Optional[Dict[str, Any]] = None,
    limit: int = 10,
    include_owned: bool = False
) -> Dict[str, Any]:
    """
    Get personalized game recommendations.
    
    Args:
        library_id: Optional library to base recommendations on
        criteria: Recommendation criteria (genres, max_playtime, min_rating, platforms)
        limit: Number of recommendations (default: 10)
        include_owned: Include already owned games
        
    Returns:
        Personalized game recommendations with reasoning
    """
    try:
        limit = min(limit, 50)  # Cap at 50 recommendations
        criteria = criteria or {}
        
        async for session in get_session():
            # Analyze user preferences if library_id provided
            user_preferences = {}
            if library_id:
                user_preferences = await _analyze_user_preferences(session, library_id)
            
            # Build recommendation query
            query_conditions = []
            
            # Base game query
            query_base = select(Game)
            
            # Exclude owned games if requested
            if not include_owned and library_id:
                # Subquery to get owned game IDs
                owned_games_subquery = select(UserGame.game_id).where(
                    UserGame.library_id == library_id
                )
                query_conditions.append(~Game.game_id.in_(owned_games_subquery))
            
            # Apply criteria filters
            if criteria.get("genres"):
                genre_conditions = []
                for genre in criteria["genres"]:
                    genre_conditions.append(Game.genres.op('?')(genre))
                if genre_conditions:
                    query_conditions.append(or_(*genre_conditions))
            
            if criteria.get("max_playtime_hours"):
                max_hours = criteria["max_playtime_hours"]
                query_conditions.append(
                    or_(
                        Game.playtime_main_hours <= max_hours,
                        Game.playtime_main_hours.is_(None)
                    )
                )
            
            if criteria.get("min_rating"):
                min_score = criteria["min_rating"]
                query_conditions.append(
                    or_(
                        Game.metacritic_score >= min_score,
                        Game.steam_score >= min_score
                    )
                )
            
            if criteria.get("platforms"):
                platform_conditions = []
                for platform in criteria["platforms"]:
                    platform_conditions.append(Game.platforms_available.op('?')(platform))
                if platform_conditions:
                    query_conditions.append(or_(*platform_conditions))
            
            # Apply ESRB rating filter if specified
            if criteria.get("max_esrb_rating"):
                rating_hierarchy = {"E": 1, "E10+": 2, "T": 3, "M": 4}
                max_rating_value = rating_hierarchy.get(criteria["max_esrb_rating"])
                if max_rating_value:
                    allowed_ratings = [
                        rating for rating, value in rating_hierarchy.items()
                        if value <= max_rating_value
                    ]
                    query_conditions.append(
                        or_(
                            Game.esrb_rating.in_(allowed_ratings),
                            Game.esrb_rating.is_(None)
                        )
                    )
            
            # Apply all conditions
            if query_conditions:
                query_base = query_base.where(and_(*query_conditions))
            
            # Order by recommendation score (simplified - would use ML in production)
            query_base = query_base.order_by(
                Game.metacritic_score.desc().nulls_last(),
                Game.steam_score.desc().nulls_last(),
                Game.release_date.desc().nulls_last()
            ).limit(limit * 2)  # Get more candidates for scoring
            
            result = await session.execute(query_base)
            candidate_games = result.scalars().all()
            
            # Score and rank recommendations
            recommendations = []
            for game in candidate_games[:limit]:
                recommendation = _score_game_recommendation(game, user_preferences, criteria)
                recommendations.append(recommendation)
            
            # Sort by recommendation score
            recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
            
            # Generate recommendation basis
            basis = _generate_recommendation_basis(user_preferences, criteria, library_id)
            
            return {
                "recommendations": recommendations,
                "recommendation_basis": basis,
                "criteria_applied": criteria,
                "total_candidates_analyzed": len(candidate_games),
                "user_preferences": user_preferences if library_id else None,
                "limit": limit,
                "include_owned": include_owned
            }
            
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return {
            "error": f"Recommendation generation failed: {str(e)}",
            "recommendations": [],
            "library_id": library_id
        }


async def _analyze_user_preferences(session: AsyncSession, library_id: str) -> Dict[str, Any]:
    """Analyze user preferences from their game library."""
    try:
        # Get user's games with ratings and playtime
        result = await session.execute(
            select(UserGame, Game).join(
                Game, UserGame.game_id == Game.game_id
            ).where(UserGame.library_id == library_id)
        )
        
        user_games = result.all()
        
        if not user_games:
            return {}
        
        # Analyze preferences
        genre_scores = {}
        developer_scores = {}
        avg_metacritic = []
        avg_user_rating = []
        total_playtime = 0
        completed_games = 0
        favorite_count = 0
        
        for user_game, game in user_games:
            # Genre preferences (weighted by playtime and rating)
            if game.genres:
                weight = (user_game.total_playtime_minutes / 60) * (user_game.user_rating or 3)
                for genre in game.genres:
                    genre_scores[genre] = genre_scores.get(genre, 0) + weight
            
            # Developer preferences
            if game.developer:
                developer_scores[game.developer] = developer_scores.get(game.developer, 0) + 1
            
            # Rating preferences
            if game.metacritic_score:
                avg_metacritic.append(game.metacritic_score)
            if user_game.user_rating:
                avg_user_rating.append(user_game.user_rating)
            
            # Playtime and completion patterns
            total_playtime += user_game.total_playtime_minutes
            if user_game.game_status == "completed":
                completed_games += 1
            if user_game.is_favorite:
                favorite_count += 1
        
        # Calculate preferences
        preferred_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        preferred_developers = sorted(developer_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        avg_playtime_hours = total_playtime / 60 / len(user_games) if user_games else 0
        completion_rate = completed_games / len(user_games) if user_games else 0
        
        return {
            "preferred_genres": [genre for genre, score in preferred_genres],
            "preferred_developers": [dev for dev, count in preferred_developers],
            "avg_metacritic_preference": sum(avg_metacritic) / len(avg_metacritic) if avg_metacritic else 75,
            "avg_user_rating": sum(avg_user_rating) / len(avg_user_rating) if avg_user_rating else 3.5,
            "avg_playtime_hours": avg_playtime_hours,
            "completion_rate": completion_rate,
            "total_games": len(user_games),
            "favorite_percentage": favorite_count / len(user_games) if user_games else 0
        }
        
    except Exception as e:
        logger.error(f"Error analyzing user preferences: {e}")
        return {}


def _score_game_recommendation(
    game: Game, 
    user_preferences: Dict[str, Any], 
    criteria: Dict[str, Any]
) -> Dict[str, Any]:
    """Score a game for recommendation based on user preferences and criteria."""
    base_score = 0.5
    reasons = []
    match_factors = {}
    
    # Genre matching
    genre_match = 0.0
    if game.genres and user_preferences.get("preferred_genres"):
        matching_genres = set(game.genres) & set(user_preferences["preferred_genres"])
        if matching_genres:
            genre_match = len(matching_genres) / len(user_preferences["preferred_genres"])
            base_score += genre_match * 0.3
            reasons.append(f"Matches your preferred genres: {', '.join(matching_genres)}")
    
    match_factors["genre_match"] = round(genre_match, 2)
    
    # Developer matching
    developer_match = 0.0
    if game.developer and game.developer in user_preferences.get("preferred_developers", []):
        developer_match = 0.8
        base_score += 0.2
        reasons.append(f"From {game.developer}, a developer you've enjoyed")
    
    match_factors["developer_match"] = round(developer_match, 2)
    
    # Rating matching
    rating_match = 0.0
    preferred_metacritic = user_preferences.get("avg_metacritic_preference", 75)
    if game.metacritic_score:
        # Score closer to user's preference gets higher match
        diff = abs(game.metacritic_score - preferred_metacritic)
        rating_match = max(0, 1 - (diff / 50))  # Normalize to 0-1
        base_score += rating_match * 0.2
        
        if game.metacritic_score >= preferred_metacritic:
            reasons.append(f"High rating ({game.metacritic_score}) matches your preferences")
    
    match_factors["rating_match"] = round(rating_match, 2)
    
    # Playtime matching
    playtime_match = 0.0
    preferred_playtime = user_preferences.get("avg_playtime_hours", 20)
    if game.playtime_main_hours:
        # Games similar to user's average playtime get bonus
        diff = abs(game.playtime_main_hours - preferred_playtime)
        playtime_match = max(0, 1 - (diff / preferred_playtime))
        base_score += playtime_match * 0.1
        
        if user_preferences.get("completion_rate", 0) > 0.7 and game.playtime_main_hours <= preferred_playtime:
            reasons.append("Good length for completing based on your habits")
    
    match_factors["playtime_match"] = round(playtime_match, 2)
    
    # Criteria matching
    if criteria.get("genres") and game.genres:
        matching_criteria_genres = set(game.genres) & set(criteria["genres"])
        if matching_criteria_genres:
            base_score += 0.1
            reasons.append(f"Matches requested genres: {', '.join(matching_criteria_genres)}")
    
    # Quality bonus
    if game.metacritic_score and game.metacritic_score >= 85:
        base_score += 0.1
        reasons.append("Highly acclaimed game")
    
    # Popularity bonus (simplified)
    if game.steam_score and game.steam_score >= 90:
        base_score += 0.05
        reasons.append("Very positive user reviews")
    
    # Cap the score at 1.0
    final_score = min(base_score, 1.0)
    
    return {
        "game_id": str(game.game_id),
        "title": game.title,
        "developer": game.developer,
        "publisher": game.publisher,
        "recommendation_score": round(final_score, 2),
        "reasons": reasons[:3],  # Top 3 reasons
        "match_factors": match_factors,
        "game_info": {
            "genres": game.genres or [],
            "metacritic_score": game.metacritic_score,
            "steam_score": game.steam_score,
            "estimated_playtime_hours": game.playtime_main_hours,
            "release_date": game.release_date.isoformat() if game.release_date else None,
            "cover_image_url": game.cover_image_url,
            "esrb_rating": game.esrb_rating
        }
    }


def _generate_recommendation_basis(
    user_preferences: Dict[str, Any], 
    criteria: Dict[str, Any], 
    library_id: Optional[str]
) -> str:
    """Generate explanation for recommendation basis."""
    basis_parts = []
    
    if library_id and user_preferences:
        if user_preferences.get("preferred_genres"):
            top_genres = user_preferences["preferred_genres"][:2]
            basis_parts.append(f"your preference for {' and '.join(top_genres)} games")
        
        if user_preferences.get("completion_rate", 0) > 0.7:
            basis_parts.append("your tendency to complete games")
        
        if user_preferences.get("avg_metacritic_preference", 0) > 80:
            basis_parts.append("your preference for highly-rated games")
    
    if criteria:
        if criteria.get("genres"):
            basis_parts.append(f"the requested genres: {', '.join(criteria['genres'])}")
        
        if criteria.get("max_playtime_hours"):
            basis_parts.append(f"the {criteria['max_playtime_hours']}-hour time limit")
    
    if not basis_parts:
        return "general popularity and critical acclaim"
    
    return "Based on " + ", ".join(basis_parts)