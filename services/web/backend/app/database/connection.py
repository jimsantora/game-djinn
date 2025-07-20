"""Database connection management with pooling."""

import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine.events import event

logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """Get database URL from environment variable."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Convert to async URL if needed
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not db_url.startswith("postgresql+asyncpg://"):
        raise ValueError("DATABASE_URL must be a PostgreSQL URL")
    
    return db_url


def create_engine():
    """Create async SQLAlchemy engine with connection pooling."""
    database_url = get_database_url()
    
    engine = create_async_engine(
        database_url,
        # Connection pool settings
        poolclass=QueuePool,
        pool_size=20,           # Number of connections to maintain
        max_overflow=30,        # Additional connections when pool is full
        pool_pre_ping=True,     # Validate connections before use
        pool_recycle=3600,      # Recycle connections every hour
        
        # Query logging (disable in production)
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        echo_pool=os.getenv("SQL_ECHO_POOL", "false").lower() == "true",
        
        # Connection arguments
        connect_args={
            "server_settings": {
                "application_name": "game_djinn_web",
                "jit": "off",  # Disable JIT for consistent performance
            },
            "command_timeout": 60,  # Query timeout in seconds
        },
    )
    
    # Log connection events
    @event.listens_for(engine.sync_engine, "connect")
    def receive_connect(dbapi_connection, connection_record):
        logger.debug("Database connection established")
    
    @event.listens_for(engine.sync_engine, "checkout")
    def receive_checkout(dbapi_connection, connection_record, connection_proxy):
        logger.debug("Database connection checked out from pool")
    
    @event.listens_for(engine.sync_engine, "checkin")
    def receive_checkin(dbapi_connection, connection_record):
        logger.debug("Database connection returned to pool")
    
    return engine


# Global engine instance
engine = create_engine()

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Usage in FastAPI:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_session)):
            # Use db session
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_engine():
    """Close the database engine (call on app shutdown)."""
    await engine.dispose()
    logger.info("Database engine closed")