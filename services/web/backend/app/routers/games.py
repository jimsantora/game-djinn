"""Game browsing and search endpoints."""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import Game, UserGame, UserLibrary
from app.schemas.game import (
    GameSearchRequest, GameSearchResponse, GameListItem, 
    GameDetail, UserGameData
)
from app.auth.dependencies import CurrentUser


router = APIRouter(prefix="/api/games", tags=["games"])


@router.get("/search", response_model=GameSearchResponse)
async def search_games(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session),
    q: str = Query(..., description="Search query"),
    platforms: Optional[List[str]] = Query(None, description="Filter by platforms"),
    genres: Optional[List[str]] = Query(None, description="Filter by genres"),
    min_rating: Optional[int] = Query(None, ge=0, le=100, description="Minimum rating"),
    owned_only: bool = Query(False, description="Show only owned games"),
    library_id: Optional[UUID] = Query(None, description="Filter by library"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page")
) -> GameSearchResponse:
    """Search for games with filters."""
    
    # Build base query
    query = select(Game)
    conditions = []
    
    # Text search
    if q:
        search_conditions = [
            Game.title.ilike(f"%{q}%"),
            Game.developer.ilike(f"%{q}%"),
            Game.publisher.ilike(f"%{q}%")
        ]
        conditions.append(or_(*search_conditions))
    
    # Platform filter
    if platforms:
        platform_conditions = [
            Game.platforms_available.op('?')(platform) for platform in platforms
        ]
        conditions.append(or_(*platform_conditions))
    
    # Genre filter
    if genres:
        genre_conditions = [
            Game.genres.op('?')(genre) for genre in genres
        ]
        conditions.append(or_(*genre_conditions))
    
    # Rating filter
    if min_rating is not None:
        conditions.append(
            or_(
                Game.metacritic_score >= min_rating,
                Game.steam_score >= min_rating
            )
        )
    
    # Owned games filter
    if owned_only and library_id:
        owned_games_subquery = select(UserGame.game_id).where(
            and_(
                UserGame.library_id == library_id,
                UserGame.owned == True
            )
        )
        conditions.append(Game.game_id.in_(owned_games_subquery))
    
    # Apply conditions
    if conditions:
        query = query.where(and_(*conditions))
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0
    
    # Apply pagination and ordering
    query = query.order_by(
        Game.metacritic_score.desc().nulls_last(),
        Game.title
    ).offset((page - 1) * limit).limit(limit)
    
    # Execute main query
    result = await session.execute(query)
    games = result.scalars().all()
    
    # Get user data if library_id provided
    user_data_map = {}
    if library_id:
        user_game_query = select(UserGame).where(
            and_(
                UserGame.library_id == library_id,
                UserGame.game_id.in_([game.game_id for game in games])
            )
        )
        user_game_result = await session.execute(user_game_query)
        user_games = user_game_result.scalars().all()
        
        for user_game in user_games:
            user_data_map[user_game.game_id] = {
                "owned": user_game.owned,
                "playtime_minutes": user_game.total_playtime_minutes,
                "rating": user_game.user_rating,
                "status": user_game.game_status,
                "is_favorite": user_game.is_favorite
            }
    
    # Build response
    game_items = []
    for game in games:
        user_data = user_data_map.get(game.game_id)
        
        game_items.append(GameListItem(
            game_id=game.game_id,
            title=game.title,
            description=game.description,
            developer=game.developer,
            publisher=game.publisher,
            genres=game.genres,
            platforms_available=game.platforms_available,
            release_date=game.release_date,
            metacritic_score=game.metacritic_score,
            steam_score=game.steam_score,
            esrb_rating=game.esrb_rating,
            esrb_descriptors=game.esrb_descriptors,
            cover_image_url=game.cover_image_url,
            user_data=user_data
        ))
    
    pages = (total + limit - 1) // limit
    
    return GameSearchResponse(
        games=game_items,
        total=total,
        page=page,
        pages=pages,
        query=q,
        filters_applied={
            "platforms": platforms or [],
            "genres": genres or [],
            "min_rating": min_rating,
            "owned_only": owned_only,
            "library_id": str(library_id) if library_id else None
        }
    )


@router.get("/{game_id}", response_model=GameDetail)
async def get_game_details(
    game_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session),
    library_id: Optional[UUID] = Query(None, description="Include user data from library")
) -> GameDetail:
    """Get detailed information about a specific game."""
    
    # Get game
    result = await session.execute(
        select(Game).where(Game.game_id == game_id)
    )
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Get user data if library_id provided
    user_game_data = None
    if library_id:
        user_game_result = await session.execute(
            select(UserGame).where(
                and_(
                    UserGame.library_id == library_id,
                    UserGame.game_id == game_id
                )
            )
        )
        user_game = user_game_result.scalar_one_or_none()
        
        if user_game:
            user_game_data = UserGameData(
                owned=user_game.owned,
                wishlisted=user_game.wishlisted,
                total_playtime_minutes=user_game.total_playtime_minutes,
                last_played_at=user_game.last_played_at,
                first_played_at=user_game.first_played_at,
                user_rating=user_game.user_rating,
                game_status=user_game.game_status,
                completion_percentage=user_game.completion_percentage,
                achievements_unlocked=user_game.achievements_unlocked,
                is_favorite=user_game.is_favorite,
                notes=user_game.notes
            )
    
    return GameDetail(
        game_id=game.game_id,
        title=game.title,
        description=game.description,
        developer=game.developer,
        publisher=game.publisher,
        genres=game.genres,
        platforms_available=game.platforms_available,
        release_date=game.release_date,
        metacritic_score=game.metacritic_score,
        steam_score=game.steam_score,
        esrb_rating=game.esrb_rating,
        esrb_descriptors=game.esrb_descriptors,
        cover_image_url=game.cover_image_url,
        screenshots=game.screenshots,
        videos=game.videos,
        achievements_total=game.achievements_total,
        playtime_main_hours=game.playtime_main_hours,
        playtime_extras_hours=game.playtime_extras_hours,
        playtime_completionist_hours=game.playtime_completionist_hours,
        system_requirements=game.system_requirements,
        platform_metadata=game.platform_metadata,
        user_game_data=user_game_data
    )