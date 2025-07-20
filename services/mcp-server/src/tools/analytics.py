"""Gaming analytics MCP tools."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models import UserGame, UserLibrary, Game, Platform
from database import get_session

logger = logging.getLogger(__name__)


async def analyze_gaming_patterns(
    library_id: Optional[str] = None,
    time_period: str = "month",
    include_predictions: bool = True
) -> Dict[str, Any]:
    """
    Analyze gaming patterns and provide insights.
    
    Args:
        library_id: Optional specific library to analyze (default: all libraries)
        time_period: Time period (week, month, quarter, year, all)
        include_predictions: Include ML-based predictions
        
    Returns:
        Gaming analytics and insights
    """
    try:
        # Calculate time range
        time_ranges = {
            "week": 7,
            "month": 30,
            "quarter": 90,
            "year": 365,
            "all": None
        }
        
        days_back = time_ranges.get(time_period, 30)
        start_date = None
        if days_back:
            start_date = datetime.utcnow() - timedelta(days=days_back)
        
        async for session in get_session():
            # Build base query
            query_base = select(UserGame, Game, UserLibrary, Platform).join(
                Game, UserGame.game_id == Game.game_id
            ).join(
                UserLibrary, UserGame.library_id == UserLibrary.library_id
            ).join(
                Platform, UserLibrary.platform_id == Platform.platform_id
            )
            
            conditions = []
            
            # Filter by library if specified
            if library_id:
                conditions.append(UserGame.library_id == library_id)
            
            # Filter by time period for last played
            if start_date:
                conditions.append(
                    or_(
                        UserGame.last_played_at >= start_date,
                        UserGame.last_played_at.is_(None)  # Include never played
                    )
                )
            
            if conditions:
                query_base = query_base.where(and_(*conditions))
            
            result = await session.execute(query_base)
            user_games = result.all()
            
            # Calculate analytics
            analytics = _calculate_gaming_analytics(user_games, time_period, start_date)
            
            if include_predictions:
                analytics["predictions"] = _generate_predictions(user_games)
            
            return analytics
            
    except Exception as e:
        logger.error(f"Error analyzing gaming patterns: {e}")
        return {
            "error": f"Analytics failed: {str(e)}",
            "period": time_period,
            "library_id": library_id
        }


def _calculate_gaming_analytics(user_games, time_period: str, start_date: Optional[datetime]) -> Dict[str, Any]:
    """Calculate gaming analytics from user game data."""
    if not user_games:
        return {
            "period": time_period,
            "total_playtime_hours": 0,
            "games_played": 0,
            "new_games_started": 0,
            "games_completed": 0,
            "completion_rate_percent": 0,
            "most_played_genre": None,
            "patterns": {"trending_up": [], "trending_down": []},
            "recommendations": []
        }
    
    total_playtime = 0
    games_played = 0
    games_completed = 0
    new_games_started = 0
    genre_playtime = {}
    status_counts = {}
    platform_stats = {}
    
    for user_game, game, library, platform in user_games:
        playtime_hours = user_game.total_playtime_minutes / 60
        total_playtime += playtime_hours
        
        if playtime_hours > 0:
            games_played += 1
        
        if user_game.game_status == "completed":
            games_completed += 1
        
        # Check if game was started in the period
        if start_date and user_game.first_played_at and user_game.first_played_at >= start_date:
            new_games_started += 1
        
        # Genre analysis
        if game.genres:
            for genre in game.genres:
                genre_playtime[genre] = genre_playtime.get(genre, 0) + playtime_hours
        
        # Status analysis
        status_counts[user_game.game_status] = status_counts.get(user_game.game_status, 0) + 1
        
        # Platform analysis
        platform_stats[platform.platform_code] = platform_stats.get(platform.platform_code, 0) + playtime_hours
    
    # Find most played genre
    most_played_genre = max(genre_playtime.items(), key=lambda x: x[1])[0] if genre_playtime else None
    
    # Calculate completion rate
    completion_rate = (games_completed / len(user_games) * 100) if user_games else 0
    
    # Generate insights
    trending_genres = _analyze_trending_genres(user_games, start_date)
    
    return {
        "period": time_period,
        "total_playtime_hours": round(total_playtime, 1),
        "games_played": games_played,
        "new_games_started": new_games_started,
        "games_completed": games_completed,
        "avg_session_duration_minutes": round((total_playtime * 60) / games_played, 1) if games_played else 0,
        "most_played_genre": most_played_genre,
        "completion_rate_percent": round(completion_rate, 1),
        "games_by_status": status_counts,
        "top_genres": [
            {"genre": genre, "playtime_hours": round(hours, 1)}
            for genre, hours in sorted(genre_playtime.items(), key=lambda x: x[1], reverse=True)[:5]
        ],
        "platform_distribution": {
            platform: round(hours, 1)
            for platform, hours in platform_stats.items()
        },
        "patterns": {
            "trending_up": trending_genres["up"],
            "trending_down": trending_genres["down"]
        },
        "insights": _generate_insights(total_playtime, games_played, games_completed, most_played_genre)
    }


def _analyze_trending_genres(user_games, start_date: Optional[datetime]) -> Dict[str, List[str]]:
    """Analyze trending genres (simplified version)."""
    # This is a simplified version - in a real implementation, 
    # you'd compare current period to previous periods
    
    if not start_date:
        return {"up": [], "down": []}
    
    recent_genres = {}
    for user_game, game, library, platform in user_games:
        if user_game.last_played_at and user_game.last_played_at >= start_date:
            if game.genres:
                for genre in game.genres:
                    recent_genres[genre] = recent_genres.get(genre, 0) + 1
    
    # Mock trending analysis
    trending_up = [genre for genre, count in recent_genres.items() if count >= 2][:3]
    
    return {
        "up": trending_up,
        "down": []  # Would need historical data to determine
    }


def _generate_predictions(user_games) -> List[Dict[str, Any]]:
    """Generate simple game recommendations based on patterns."""
    # This is a simplified version - in a real implementation,
    # you'd use machine learning models
    
    if not user_games:
        return []
    
    # Analyze user preferences
    preferred_genres = {}
    avg_rating = 0
    rating_count = 0
    
    for user_game, game, library, platform in user_games:
        if game.genres:
            for genre in game.genres:
                preferred_genres[genre] = preferred_genres.get(genre, 0) + 1
        
        if user_game.user_rating:
            avg_rating += user_game.user_rating
            rating_count += 1
    
    if rating_count > 0:
        avg_rating /= rating_count
    
    top_genre = max(preferred_genres.items(), key=lambda x: x[1])[0] if preferred_genres else "Action"
    
    # Generate mock recommendations
    recommendations = [
        {
            "type": "genre_match",
            "title": f"Similar {top_genre} Games",
            "reason": f"Based on your love for {top_genre} games",
            "confidence": 0.85,
            "suggestion": f"Look for highly-rated {top_genre} games you haven't played yet"
        }
    ]
    
    if avg_rating > 4:
        recommendations.append({
            "type": "quality_match",
            "title": "High-Quality Games",
            "reason": "You tend to enjoy highly-rated games",
            "confidence": 0.78,
            "suggestion": "Focus on games with Metacritic scores above 85"
        })
    
    return recommendations


def _generate_insights(total_playtime: float, games_played: int, games_completed: int, most_played_genre: str) -> List[str]:
    """Generate textual insights about gaming patterns."""
    insights = []
    
    if total_playtime > 50:
        insights.append(f"You're an active gamer with {total_playtime:.1f} hours of playtime")
    elif total_playtime > 20:
        insights.append(f"You have moderate gaming activity with {total_playtime:.1f} hours")
    else:
        insights.append("You have light gaming activity - consider exploring new games")
    
    if games_completed > 0:
        completion_rate = (games_completed / games_played) * 100 if games_played else 0
        if completion_rate > 50:
            insights.append("You're great at finishing games you start")
        else:
            insights.append("You might enjoy shorter games or focus on fewer titles")
    
    if most_played_genre:
        insights.append(f"Your favorite genre appears to be {most_played_genre}")
    
    return insights