"""Tests for game search and details MCP tools."""

import pytest
from uuid import uuid4
from datetime import datetime
from models import Game, UserGame, UserLibrary, Platform
from tools.games import search_games, get_game_details


@pytest.mark.asyncio
async def test_search_games_empty(test_session, override_get_session):
    """Test searching games when none exist."""
    result = await search_games(query="test")
    
    assert "games" in result
    assert len(result["games"]) == 0
    assert result["total_results"] == 0


@pytest.mark.asyncio
async def test_search_games_basic(test_session, override_get_session):
    """Test basic game search functionality."""
    # Add test games
    game1 = Game(
        game_id=uuid4(),
        title="Test Action Game",
        developer="Test Studio",
        publisher="Test Publisher",
        genres=["Action", "Adventure"],
        metacritic_score=85,
        steam_score=92,
        steam_id="123456"
    )
    
    game2 = Game(
        game_id=uuid4(),
        title="Another RPG Game",
        developer="RPG Studio",
        publisher="RPG Publisher",
        genres=["RPG", "Fantasy"],
        metacritic_score=90,
        steam_score=88,
        steam_id="789012"
    )
    
    test_session.add_all([game1, game2])
    await test_session.commit()
    
    # Search for "Action"
    result = await search_games(query="Action")
    
    assert "games" in result
    assert len(result["games"]) == 1
    assert result["games"][0]["title"] == "Test Action Game"
    assert result["total_results"] == 1


@pytest.mark.asyncio
async def test_search_games_genre_filter(test_session, override_get_session):
    """Test game search with genre filtering."""
    # Add test games
    game1 = Game(
        game_id=uuid4(),
        title="Action Game",
        genres=["Action", "Shooter"],
        steam_id="123456"
    )
    
    game2 = Game(
        game_id=uuid4(),
        title="RPG Game",
        genres=["RPG", "Adventure"],
        steam_id="789012"
    )
    
    test_session.add_all([game1, game2])
    await test_session.commit()
    
    # Search with genre filter
    result = await search_games(
        query="Game",
        genre_filter=["RPG"]
    )
    
    assert len(result["games"]) == 1
    assert result["games"][0]["title"] == "RPG Game"


@pytest.mark.asyncio
async def test_search_games_rating_filter(test_session, override_get_session):
    """Test game search with rating filtering."""
    # Add test games
    game1 = Game(
        game_id=uuid4(),
        title="High Rated Game",
        metacritic_score=95,
        steam_id="123456"
    )
    
    game2 = Game(
        game_id=uuid4(),
        title="Low Rated Game",
        metacritic_score=65,
        steam_id="789012"
    )
    
    test_session.add_all([game1, game2])
    await test_session.commit()
    
    # Search with rating filter
    result = await search_games(
        query="Game",
        rating_filter={"min_metacritic": 80}
    )
    
    assert len(result["games"]) == 1
    assert result["games"][0]["title"] == "High Rated Game"


@pytest.mark.asyncio
async def test_get_game_details_basic(test_session, override_get_session):
    """Test getting basic game details."""
    game_id = uuid4()
    game = Game(
        game_id=game_id,
        title="Test Game",
        developer="Test Studio",
        publisher="Test Publisher",
        description="A test game for testing",
        genres=["Action", "Adventure"],
        metacritic_score=85,
        steam_score=92,
        release_date=datetime(2023, 1, 15),
        steam_id="123456"
    )
    
    test_session.add(game)
    await test_session.commit()
    
    result = await get_game_details(game_id=str(game_id))
    
    assert "game_info" in result
    game_info = result["game_info"]
    assert game_info["title"] == "Test Game"
    assert game_info["developer"] == "Test Studio"
    assert game_info["genres"] == ["Action", "Adventure"]
    assert game_info["metacritic_score"] == 85
    assert "user_data" not in result


@pytest.mark.asyncio
async def test_get_game_details_with_user_data(test_session, override_get_session):
    """Test getting game details with user-specific data."""
    # Create test data
    platform = Platform(
        platform_id=uuid4(),
        platform_code="steam",
        platform_name="Steam",
        api_base_url="https://api.steampowered.com",
        is_enabled=True
    )
    
    library = UserLibrary(
        library_id=uuid4(),
        platform_id=platform.platform_id,
        user_identifier="76561198000000000",
        display_name="My Steam Library"
    )
    
    game_id = uuid4()
    game = Game(
        game_id=game_id,
        title="Test Game",
        steam_id="123456"
    )
    
    user_game = UserGame(
        user_game_id=uuid4(),
        library_id=library.library_id,
        game_id=game_id,
        owned=True,
        total_playtime_minutes=120,
        user_rating=4,
        game_status="playing",
        is_favorite=True
    )
    
    test_session.add_all([platform, library, game, user_game])
    await test_session.commit()
    
    result = await get_game_details(
        game_id=str(game_id),
        library_id=str(library.library_id)
    )
    
    assert "user_data" in result
    user_data = result["user_data"]
    assert user_data["owned"] is True
    assert user_data["total_playtime_minutes"] == 120
    assert user_data["user_rating"] == 4
    assert user_data["is_favorite"] is True


@pytest.mark.asyncio
async def test_get_game_details_not_found(test_session, override_get_session):
    """Test getting details for non-existent game."""
    fake_game_id = str(uuid4())
    result = await get_game_details(game_id=fake_game_id)
    
    assert "error" in result
    assert "not found" in result["error"].lower()