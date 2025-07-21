"""Test configuration and fixtures for MCP server tests."""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from database.connection import get_session, engine as global_engine
from models import Base


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def override_get_session(test_session):
    """Override the get_session dependency for testing."""
    async def _get_test_session():
        yield test_session
    
    # Store original function
    original_get_session = get_session
    
    # Replace with test session
    import database.connection
    database.connection.get_session = _get_test_session
    
    # Import tools after overriding the session
    import tools.platforms
    import tools.games
    import tools.sync
    import tools.analytics
    import tools.recommendations
    import tools.content
    
    # Reload modules to use new session
    import importlib
    importlib.reload(tools.platforms)
    importlib.reload(tools.games)
    importlib.reload(tools.sync)
    importlib.reload(tools.analytics)
    importlib.reload(tools.recommendations)
    importlib.reload(tools.content)
    
    yield
    
    # Restore original function
    database.connection.get_session = original_get_session