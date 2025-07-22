"""Sync operation endpoints."""

from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from app.database import get_session
from app.models import UserLibrary, Platform
from app.auth.dependencies import CurrentUser
from app.websocket.socket_manager import emit_sync_progress, emit_sync_complete, emit_sync_error


router = APIRouter(prefix="/api/sync", tags=["sync"])


class SyncRequest(BaseModel):
    """Sync operation request."""
    force: bool = False
    sync_type: str = "incremental_sync"  # full_sync, incremental_sync, manual_sync


class SyncResponse(BaseModel):
    """Sync operation response."""
    library_id: UUID
    status: str
    message: str
    started_at: datetime


class SyncStatus(BaseModel):
    """Sync status response."""
    library_id: UUID
    status: str
    progress_percentage: float
    current_step: str
    games_processed: int
    total_games: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None


async def perform_library_sync(library_id: UUID, force: bool, sync_type: str):
    """Background task to perform library synchronization."""
    library_id_str = str(library_id)
    print(f"[SYNC] Starting background sync for library {library_id_str}")
    
    try:
        # Emit initial progress
        print(f"[SYNC] Emitting initial progress for {library_id_str}")
        await emit_sync_progress(library_id_str, {
            "status": "starting",
            "progress": 0,
            "message": "Starting sync process..."
        })
        
        # Simulate sync steps
        import asyncio
        steps = [
            ("Connecting to platform", 20),
            ("Fetching library data", 40),
            ("Processing games", 60),
            ("Updating metadata", 80),
            ("Finalizing sync", 100)
        ]
        
        for step_message, progress in steps:
            print(f"[SYNC] Progress update: {step_message} ({progress}%)")
            await emit_sync_progress(library_id_str, {
                "status": "syncing",
                "progress": progress,
                "message": step_message
            })
            await asyncio.sleep(1)  # Simulate work
        
        # Emit completion
        await emit_sync_complete(library_id_str, {
            "status": "completed",
            "message": "Sync completed successfully",
            "games_processed": 50,  # Would be actual count
            "new_games": 5,
            "updated_games": 10
        })
        
        print(f"Sync completed for library {library_id}")
        
    except Exception as e:
        # Emit error
        await emit_sync_error(library_id_str, {
            "status": "error",
            "message": f"Sync failed: {str(e)}"
        })
        print(f"Sync failed for library {library_id}: {e}")


@router.post("/{library_id}", response_model=SyncResponse)
async def trigger_sync(
    library_id: UUID,
    sync_request: SyncRequest,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
) -> SyncResponse:
    """Trigger synchronization for a library."""
    print(f"[SYNC] Received sync request for library {library_id}")
    print(f"[SYNC] Request data: {sync_request}")
    
    # Check if library exists
    result = await session.execute(
        select(UserLibrary, Platform)
        .join(Platform, UserLibrary.platform_id == Platform.platform_id)
        .where(UserLibrary.library_id == library_id)
    )
    
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    
    library, platform = row
    
    if not library.sync_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Library sync is not enabled"
        )
    
    if not platform.api_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Platform is not enabled"
        )
    
    # Check if sync is already in progress
    if library.sync_status == "syncing" and not sync_request.force:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sync already in progress. Use force=true to override."
        )
    
    # Update sync status
    library.sync_status = "syncing"
    library.last_sync_at = datetime.utcnow()
    await session.commit()
    
    # Start background sync task
    background_tasks.add_task(
        perform_library_sync,
        library_id,
        sync_request.force,
        sync_request.sync_type
    )
    
    return SyncResponse(
        library_id=library_id,
        status="started",
        message=f"Sync started for {library.display_name}",
        started_at=library.last_sync_at
    )


@router.get("/{library_id}/status", response_model=SyncStatus)
async def get_sync_status(
    library_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session)
) -> SyncStatus:
    """Get sync status for a library."""
    
    result = await session.execute(
        select(UserLibrary).where(UserLibrary.library_id == library_id)
    )
    
    library = result.scalar_one_or_none()
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    
    # In a real implementation, this would query sync progress from Redis or database
    # For now, return simulated status
    
    return SyncStatus(
        library_id=library_id,
        status=library.sync_status or "idle",
        progress_percentage=0.0,  # Would be calculated from actual sync progress
        current_step="idle",
        games_processed=0,
        total_games=0,
        error_message=None,
        started_at=library.last_sync_at,
        completed_at=None
    )


@router.post("/{library_id}/cancel")
async def cancel_sync(
    library_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    """Cancel ongoing sync operation."""
    
    result = await session.execute(
        select(UserLibrary).where(UserLibrary.library_id == library_id)
    )
    
    library = result.scalar_one_or_none()
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    
    if library.sync_status != "syncing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No sync operation in progress"
        )
    
    # In a real implementation, this would cancel the background task
    # and update the sync status
    library.sync_status = "cancelled"
    await session.commit()
    
    return {"message": "Sync cancelled successfully"}