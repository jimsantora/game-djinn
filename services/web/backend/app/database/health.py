"""Database health check utilities."""

import logging
import asyncio
from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from .connection import async_session

logger = logging.getLogger(__name__)


async def check_database_health() -> Dict[str, Any]:
    """
    Check database health and return status information.
    
    Returns:
        Dict containing health status, connection info, and metrics
    """
    health_info = {
        "status": "unknown",
        "database": "postgresql",
        "connected": False,
        "pool_size": 0,
        "checked_out": 0,
        "overflow": 0,
        "response_time_ms": None,
        "error": None,
    }
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        async with async_session() as session:
            # Simple query to test connectivity
            result = await session.execute(text("SELECT 1 as health_check"))
            health_check = result.scalar()
            
            if health_check == 1:
                health_info["connected"] = True
                health_info["status"] = "healthy"
                
                # Get pool statistics
                pool = session.get_bind().pool
                health_info["pool_size"] = pool.size()
                health_info["checked_out"] = pool.checkedout()
                health_info["overflow"] = pool.overflow()
                
                # Calculate response time
                end_time = asyncio.get_event_loop().time()
                health_info["response_time_ms"] = round((end_time - start_time) * 1000, 2)
                
                logger.debug(f"Database health check passed in {health_info['response_time_ms']}ms")
            else:
                health_info["status"] = "unhealthy"
                health_info["error"] = "Unexpected health check response"
                
    except Exception as e:
        health_info["status"] = "unhealthy"
        health_info["error"] = str(e)
        logger.error(f"Database health check failed: {e}")
    
    return health_info


async def check_database_version() -> Dict[str, Any]:
    """Get PostgreSQL version information."""
    version_info = {
        "version": None,
        "error": None,
    }
    
    try:
        async with async_session() as session:
            result = await session.execute(text("SELECT version()"))
            version_info["version"] = result.scalar()
            
    except Exception as e:
        version_info["error"] = str(e)
        logger.error(f"Failed to get database version: {e}")
    
    return version_info


async def check_database_extensions() -> Dict[str, Any]:
    """Check required PostgreSQL extensions."""
    extensions_info = {
        "required_extensions": ["uuid-ossp"],
        "installed_extensions": [],
        "missing_extensions": [],
        "error": None,
    }
    
    try:
        async with async_session() as session:
            result = await session.execute(
                text("SELECT extname FROM pg_extension")
            )
            installed = [row[0] for row in result.fetchall()]
            extensions_info["installed_extensions"] = installed
            
            # Check for missing required extensions
            missing = [
                ext for ext in extensions_info["required_extensions"]
                if ext not in installed
            ]
            extensions_info["missing_extensions"] = missing
            
    except Exception as e:
        extensions_info["error"] = str(e)
        logger.error(f"Failed to check database extensions: {e}")
    
    return extensions_info