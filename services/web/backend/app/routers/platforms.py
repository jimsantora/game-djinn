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
        query = query.where(Platform.api_available == True)
    
    query = query.order_by(Platform.platform_name)
    
    result = await session.execute(query)
    platforms = result.scalars().all()
    
    return [
        PlatformResponse(
            platform_id=str(platform.platform_id),
            platform_code=platform.platform_code,
            platform_name=platform.platform_name,
            icon_url=platform.icon_url,
            is_enabled=platform.api_available,
            requires_api_key=False,  # TODO: Add this field to Platform model
            rate_limit_requests=None,  # TODO: Add this field to Platform model
            rate_limit_window=None  # TODO: Add this field to Platform model
        )
        for platform in platforms
    ]