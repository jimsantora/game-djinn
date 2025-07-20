"""Platform synchronization MCP tools."""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Platform, UserLibrary, SyncOperation
from database import get_session

logger = logging.getLogger(__name__)


async def sync_platform_library(
    library_id: str,
    force: bool = False,
    sync_type: str = "incremental_sync"
) -> Dict[str, Any]:
    """
    Trigger synchronization for a platform library.
    
    Args:
        library_id: UUID of the library to sync
        force: Force sync even if recently synced
        sync_type: Type of sync (full_sync, incremental_sync, manual_sync)
        
    Returns:
        Sync operation result with operation_id and status
    """
    try:
        async for session in get_session():
            # Find the library
            library_result = await session.execute(
                select(UserLibrary).where(UserLibrary.library_id == library_id)
            )
            library = library_result.scalar_one_or_none()
            
            if not library:
                return {
                    "error": f"Library with ID '{library_id}' not found",
                    "suggestion": "Check the library_id or use get_supported_platforms to list available libraries"
                }
            
            # Get platform info
            platform_result = await session.execute(
                select(Platform).where(Platform.platform_id == library.platform_id)
            )
            platform = platform_result.scalar_one_or_none()
            
            if not platform:
                return {
                    "error": "Platform not found for this library",
                    "library_id": library_id
                }
            
            # Check if sync is already in progress
            if library.sync_status == "in_progress" and not force:
                return {
                    "error": "Library sync is already in progress",
                    "library_id": library_id,
                    "current_status": library.sync_status,
                    "last_sync_at": library.last_sync_at.isoformat() if library.last_sync_at else None,
                    "force_option": "Use force=true to cancel current sync and start new one"
                }
            
            # Check if platform API is available
            if not platform.api_available and platform.platform_code != "manual":
                return {
                    "error": f"Platform '{platform.platform_code}' API is not yet available",
                    "platform_name": platform.platform_name,
                    "status": "coming_soon"
                }
            
            # For Steam, check if we have API key
            if platform.platform_code == "steam":
                steam_api_key = os.getenv("STEAM_API_KEY")
                if not steam_api_key:
                    return {
                        "error": "Steam API key not configured",
                        "platform": "steam",
                        "suggestion": "Set STEAM_API_KEY environment variable"
                    }
            
            # Create sync operation record
            sync_operation = SyncOperation(
                library_id=library.library_id,
                operation_type=sync_type,
                status="started",
                started_at=datetime.utcnow(),
                games_processed=0,
                games_added=0,
                games_updated=0,
                errors_count=0
            )
            
            session.add(sync_operation)
            
            # Update library status
            library.sync_status = "in_progress"
            library.last_sync_at = datetime.utcnow()
            
            await session.flush()  # Get the operation ID
            
            logger.info(f"Starting {sync_type} for library {library_id} ({platform.platform_code})")
            
            # TODO: In a real implementation, this would trigger background sync job
            # For now, we'll return a mock response indicating sync started
            
            # Simulate quick sync completion for demo
            if platform.platform_code == "manual":
                sync_operation.status = "completed"
                sync_operation.completed_at = datetime.utcnow()
                library.sync_status = "completed"
                
                return {
                    "operation_id": str(sync_operation.operation_id),
                    "library_id": library_id,
                    "platform": platform.platform_code,
                    "status": "completed",
                    "operation_type": sync_type,
                    "started_at": sync_operation.started_at.isoformat(),
                    "completed_at": sync_operation.completed_at.isoformat(),
                    "games_processed": 0,
                    "games_added": 0,
                    "games_updated": 0,
                    "message": "Manual platform sync completed (no games to sync)"
                }
            
            # For other platforms, return sync started status
            return {
                "operation_id": str(sync_operation.operation_id),
                "library_id": library_id,
                "platform": platform.platform_code,
                "platform_name": platform.platform_name,
                "status": "started",
                "operation_type": sync_type,
                "started_at": sync_operation.started_at.isoformat(),
                "estimated_duration_minutes": _estimate_sync_duration(platform.platform_code, sync_type),
                "games_processed": 0,
                "games_added": 0,
                "games_updated": 0,
                "message": f"Sync operation started for {platform.platform_name}",
                "next_steps": [
                    "Monitor sync progress through sync operation status",
                    "Sync will process games in batches to respect rate limits",
                    "Use search_games to see synced games after completion"
                ]
            }
            
    except Exception as e:
        logger.error(f"Error starting sync for library {library_id}: {e}")
        return {
            "error": f"Failed to start sync: {str(e)}",
            "library_id": library_id,
            "suggestion": "Check that the library exists and try again"
        }


def _estimate_sync_duration(platform_code: str, sync_type: str) -> int:
    """Estimate sync duration in minutes based on platform and sync type."""
    base_times = {
        "steam": {"full_sync": 15, "incremental_sync": 5, "manual_sync": 2},
        "xbox": {"full_sync": 20, "incremental_sync": 7, "manual_sync": 3},
        "gog": {"full_sync": 10, "incremental_sync": 4, "manual_sync": 2},
        "epic": {"full_sync": 8, "incremental_sync": 3, "manual_sync": 1},
        "playstation": {"full_sync": 25, "incremental_sync": 8, "manual_sync": 3},
        "manual": {"full_sync": 1, "incremental_sync": 1, "manual_sync": 1},
    }
    
    return base_times.get(platform_code, {}).get(sync_type, 5)