"""Tests for platform management MCP tools."""

import pytest
from uuid import uuid4
from models import Platform, UserLibrary
from tools.platforms import get_supported_platforms, add_platform_library


@pytest.mark.asyncio
async def test_get_supported_platforms_empty(test_session, override_get_session):
    """Test getting supported platforms when none exist."""
    result = await get_supported_platforms()
    
    assert "platforms" in result
    assert len(result["platforms"]) == 0
    assert result["total_count"] == 0


@pytest.mark.asyncio
async def test_get_supported_platforms_with_data(test_session, override_get_session):
    """Test getting supported platforms with sample data."""
    # Add test platforms
    steam_platform = Platform(
        platform_id=uuid4(),
        platform_code="steam",
        platform_name="Steam",
        api_base_url="https://api.steampowered.com",
        is_enabled=True,
        requires_api_key=True
    )
    
    xbox_platform = Platform(
        platform_id=uuid4(),
        platform_code="xbox",
        platform_name="Xbox Live",
        api_base_url="https://xbl.io",
        is_enabled=False,
        requires_api_key=True
    )
    
    test_session.add_all([steam_platform, xbox_platform])
    await test_session.commit()
    
    result = await get_supported_platforms()
    
    assert "platforms" in result
    assert len(result["platforms"]) == 2
    assert result["total_count"] == 2
    
    # Check Steam platform details
    steam_result = next(p for p in result["platforms"] if p["platform_code"] == "steam")
    assert steam_result["platform_name"] == "Steam"
    assert steam_result["is_enabled"] is True
    assert steam_result["requires_api_key"] is True


@pytest.mark.asyncio
async def test_add_platform_library_success(test_session, override_get_session):
    """Test successfully adding a platform library."""
    # Add test platform
    platform = Platform(
        platform_id=uuid4(),
        platform_code="steam",
        platform_name="Steam",
        api_base_url="https://api.steampowered.com",
        is_enabled=True,
        requires_api_key=True
    )
    test_session.add(platform)
    await test_session.commit()
    
    result = await add_platform_library(
        platform_code="steam",
        user_identifier="76561198000000000",
        display_name="My Steam Library",
        credentials={"api_key": "test_key"}
    )
    
    assert "library_id" in result
    assert result["platform_code"] == "steam"
    assert result["user_identifier"] == "76561198000000000"
    assert result["display_name"] == "My Steam Library"
    assert result["status"] == "created"


@pytest.mark.asyncio
async def test_add_platform_library_invalid_platform(test_session, override_get_session):
    """Test adding library for non-existent platform."""
    result = await add_platform_library(
        platform_code="nonexistent",
        user_identifier="123456",
        display_name="Test Library"
    )
    
    assert "error" in result
    assert "not found" in result["error"].lower()


@pytest.mark.asyncio
async def test_add_platform_library_duplicate(test_session, override_get_session):
    """Test adding duplicate platform library."""
    # Add test platform
    platform = Platform(
        platform_id=uuid4(),
        platform_code="steam",
        platform_name="Steam",
        api_base_url="https://api.steampowered.com",
        is_enabled=True,
        requires_api_key=True
    )
    test_session.add(platform)
    await test_session.commit()
    
    # Add first library
    await add_platform_library(
        platform_code="steam",
        user_identifier="76561198000000000",
        display_name="My Steam Library"
    )
    
    # Try to add duplicate
    result = await add_platform_library(
        platform_code="steam",
        user_identifier="76561198000000000",
        display_name="Another Steam Library"
    )
    
    assert "error" in result
    assert "already exists" in result["error"].lower()