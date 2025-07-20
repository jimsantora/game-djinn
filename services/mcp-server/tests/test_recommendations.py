"""Tests for game recommendation MCP tools."""

import pytest
from uuid import uuid4
from datetime import datetime
from models import Game, UserGame, UserLibrary, Platform
from tools.recommendations import recommend_games


@pytest.mark.asyncio
async def test_recommend_games_no_library(test_session, override_get_session):
    """Test recommendations without user library data."""
    # Add some test games
    game1 = Game(
        game_id=uuid4(),
        title="High Rated Action Game",
        genres=["Action", "Adventure"],
        metacritic_score=90,
        steam_score=95,
        steam_id="123456"
    )
    
    game2 = Game(
        game_id=uuid4(),
        title="Average RPG Game",
        genres=["RPG", "Fantasy"],
        metacritic_score=75,
        steam_score=80,
        steam_id="789012"
    )
    
    test_session.add_all([game1, game2])
    await test_session.commit()
    
    result = await recommend_games(limit=5)
    
    assert "recommendations" in result
    assert len(result["recommendations"]) <= 5
    assert result["user_preferences"] is None
    assert "recommendation_basis" in result


@pytest.mark.asyncio
async def test_recommend_games_with_criteria(test_session, override_get_session):
    """Test recommendations with specific criteria."""
    # Add test games
    action_game = Game(
        game_id=uuid4(),
        title="Action Game",
        genres=["Action", "Shooter"],
        metacritic_score=85,
        steam_id="123456"
    )
    
    rpg_game = Game(
        game_id=uuid4(),
        title="RPG Game",
        genres=["RPG", "Adventure"],
        metacritic_score=90,
        steam_id="789012"
    )
    
    test_session.add_all([action_game, rpg_game])
    await test_session.commit()
    
    # Test with genre criteria
    result = await recommend_games(
        criteria={"genres": ["Action"]},
        limit=3
    )
    
    assert len(result["recommendations"]) <= 3
    assert result["criteria_applied"]["genres"] == ["Action"]
    
    # Should only recommend action games
    for rec in result["recommendations"]:
        assert "Action" in rec["game_info"]["genres"]


@pytest.mark.asyncio
async def test_recommend_games_rating_filter(test_session, override_get_session):
    """Test recommendations with rating filter."""
    # Add games with different ratings
    high_rated = Game(
        game_id=uuid4(),
        title="High Rated Game",
        metacritic_score=95,
        steam_id="123456"
    )
    
    low_rated = Game(
        game_id=uuid4(),
        title="Low Rated Game",
        metacritic_score=60,
        steam_id="789012"
    )
    
    test_session.add_all([high_rated, low_rated])
    await test_session.commit()
    
    result = await recommend_games(
        criteria={"min_rating": 80},
        limit=5
    )
    
    # Should only recommend high-rated games
    for rec in result["recommendations"]:
        score = rec["game_info"]["metacritic_score"]
        if score is not None:
            assert score >= 80


@pytest.mark.asyncio
async def test_recommend_games_with_user_preferences(test_session, override_get_session):
    """Test recommendations based on user library preferences."""
    # Create test platform and library
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
    
    # Add games user owns (showing preference for RPG)
    owned_rpg1 = Game(
        game_id=uuid4(),
        title="Owned RPG 1",
        genres=["RPG", "Fantasy"],
        developer="RPG Studio",
        steam_id="111111"
    )
    
    owned_rpg2 = Game(
        game_id=uuid4(),
        title="Owned RPG 2",
        genres=["RPG", "Adventure"],
        developer="RPG Studio",
        steam_id="222222"
    )
    
    # Add potential recommendations
    new_rpg = Game(
        game_id=uuid4(),
        title="New RPG Game",
        genres=["RPG", "Strategy"],
        developer="RPG Studio",
        metacritic_score=85,
        steam_id="333333"
    )
    
    new_action = Game(
        game_id=uuid4(),
        title="New Action Game",
        genres=["Action", "Shooter"],
        metacritic_score=80,
        steam_id="444444"
    )
    
    # User games (showing high playtime in RPGs)
    user_game1 = UserGame(
        user_game_id=uuid4(),
        library_id=library.library_id,
        game_id=owned_rpg1.game_id,
        owned=True,
        total_playtime_minutes=1200,  # 20 hours
        user_rating=5
    )
    
    user_game2 = UserGame(
        user_game_id=uuid4(),
        library_id=library.library_id,
        game_id=owned_rpg2.game_id,
        owned=True,
        total_playtime_minutes=900,   # 15 hours
        user_rating=4
    )
    
    test_session.add_all([
        platform, library, owned_rpg1, owned_rpg2, 
        new_rpg, new_action, user_game1, user_game2
    ])
    await test_session.commit()
    
    result = await recommend_games(
        library_id=str(library.library_id),
        limit=5
    )
    
    assert "user_preferences" in result
    assert result["user_preferences"] is not None
    
    # Should prefer RPG games based on user history
    preferences = result["user_preferences"]
    assert "RPG" in preferences.get("preferred_genres", [])
    assert "RPG Studio" in preferences.get("preferred_developers", [])
    
    # Recommendations should be scored
    for rec in result["recommendations"]:
        assert "recommendation_score" in rec
        assert 0 <= rec["recommendation_score"] <= 1
        assert "reasons" in rec


@pytest.mark.asyncio
async def test_recommend_games_exclude_owned(test_session, override_get_session):
    """Test that owned games are excluded by default."""
    # Create test platform and library
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
    
    # Add owned and unowned games
    owned_game = Game(
        game_id=uuid4(),
        title="Owned Game",
        steam_id="111111"
    )
    
    unowned_game = Game(
        game_id=uuid4(),
        title="Unowned Game",
        steam_id="222222"
    )
    
    user_game = UserGame(
        user_game_id=uuid4(),
        library_id=library.library_id,
        game_id=owned_game.game_id,
        owned=True
    )
    
    test_session.add_all([platform, library, owned_game, unowned_game, user_game])
    await test_session.commit()
    
    # Test exclude owned (default)
    result = await recommend_games(
        library_id=str(library.library_id),
        include_owned=False
    )
    
    # Should not recommend owned games
    recommended_titles = [rec["title"] for rec in result["recommendations"]]
    assert "Owned Game" not in recommended_titles
    assert "Unowned Game" in recommended_titles
    
    # Test include owned
    result_with_owned = await recommend_games(
        library_id=str(library.library_id),
        include_owned=True
    )
    
    # Should include owned games
    recommended_titles_with_owned = [rec["title"] for rec in result_with_owned["recommendations"]]
    assert "Owned Game" in recommended_titles_with_owned