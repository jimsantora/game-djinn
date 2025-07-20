"""Platform management MCP tools."""

import logging
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Platform, UserLibrary
from database import get_session

logger = logging.getLogger(__name__)


async def get_supported_platforms() -> Dict[str, Any]:
    """
    Get list of supported gaming platforms.
    
    Returns platforms with their availability status and setup requirements.
    """
    try:
        async for session in get_session():
            # Get all platforms from database
            result = await session.execute(select(Platform))
            platforms = result.scalars().all()
            
            platform_list = []
            for platform in platforms:
                platform_list.append({
                    "platform_id": str(platform.platform_id),
                    "platform_code": platform.platform_code,
                    "platform_name": platform.platform_name,
                    "api_available": platform.api_available,
                    "icon_url": platform.icon_url,
                    "setup_required": platform.api_available,  # If API available, setup is required
                    "status": "available" if platform.api_available else "coming_soon"
                })
            
            return {
                "platforms": platform_list,
                "total": len(platform_list),
                "available_count": sum(1 for p in platform_list if p["api_available"]),
                "primary_platform": "steam"  # Phase 1 focus
            }
            
    except Exception as e:
        logger.error(f"Error getting supported platforms: {e}")
        return {
            "error": f"Failed to get platforms: {str(e)}",
            "platforms": [],
            "total": 0
        }


async def add_platform_library(
    platform_code: str,
    user_identifier: str,
    display_name: str,
    credentials: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Add a new user library for a platform.
    
    Args:
        platform_code: Platform identifier (steam, xbox, etc.)
        user_identifier: Platform-specific user ID
        display_name: Friendly name for the library
        credentials: Optional platform-specific credentials
        
    Returns:
        Library creation result with library_id
    """
    try:
        async for session in get_session():
            # Find the platform
            platform_result = await session.execute(
                select(Platform).where(Platform.platform_code == platform_code)
            )
            platform = platform_result.scalar_one_or_none()
            
            if not platform:
                return {
                    "error": f"Platform '{platform_code}' not found",
                    "available_platforms": ["steam", "xbox", "gog", "epic", "playstation", "manual"]
                }
            
            if not platform.api_available and platform_code != "manual":
                return {
                    "error": f"Platform '{platform_code}' is not yet available for API integration",
                    "status": "coming_soon"
                }
            
            # Check if library already exists
            existing_result = await session.execute(
                select(UserLibrary).where(
                    UserLibrary.platform_id == platform.platform_id,
                    UserLibrary.user_identifier == user_identifier
                )
            )
            existing_library = existing_result.scalar_one_or_none()
            
            if existing_library:
                return {
                    "error": f"Library for {platform_code} user '{user_identifier}' already exists",
                    "existing_library_id": str(existing_library.library_id),
                    "display_name": existing_library.display_name
                }
            
            # Create new library
            new_library = UserLibrary(
                platform_id=platform.platform_id,
                user_identifier=user_identifier,
                display_name=display_name,
                api_credentials=credentials or {},
                sync_enabled=True,
                sync_status="pending"
            )
            
            session.add(new_library)
            await session.flush()  # Get the ID
            
            logger.info(f"Created library for {platform_code} user {user_identifier}")
            
            return {
                "library_id": str(new_library.library_id),
                "platform_code": platform_code,
                "platform_name": platform.platform_name,
                "display_name": display_name,
                "user_identifier": user_identifier,
                "sync_status": "pending",
                "sync_enabled": True,
                "created_at": new_library.created_at.isoformat(),
                "next_steps": [
                    f"Use sync_platform_library with library_id '{new_library.library_id}' to start syncing games",
                    "Monitor sync progress through the sync status endpoints"
                ]
            }
            
    except Exception as e:
        logger.error(f"Error adding platform library: {e}")
        return {
            "error": f"Failed to create library: {str(e)}",
            "suggestion": "Check that the platform code is valid and user identifier is correct"
        }