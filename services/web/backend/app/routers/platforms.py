"""Platform management endpoints."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_session
from app.models import Platform
from app.auth.dependencies import CurrentUser


router = APIRouter(prefix="/api/platforms", tags=["platforms"])


class PlatformResponse(BaseModel):
    """Platform response schema."""
    platform_id: str
    platform_code: str
    platform_name: str
    icon_url: str | None
    is_enabled: bool
    requires_api_key: bool
    rate_limit_requests: int | None
    rate_limit_window: int | None
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[PlatformResponse])
async def list_platforms(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session),
    enabled_only: bool = True
) -> List[PlatformResponse]:
    """List all available platforms."""
    query = select(Platform)
    
    if enabled_only:
        query = query.where(Platform.is_enabled == True)
    
    query = query.order_by(Platform.platform_name)
    
    result = await session.execute(query)
    platforms = result.scalars().all()
    
    return [
        PlatformResponse(
            platform_id=str(platform.platform_id),
            platform_code=platform.platform_code,
            platform_name=platform.platform_name,
            icon_url=platform.icon_url,
            is_enabled=platform.is_enabled,
            requires_api_key=platform.requires_api_key,
            rate_limit_requests=platform.rate_limit_requests,
            rate_limit_window=platform.rate_limit_window
        )
        for platform in platforms
    ]