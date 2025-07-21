"""Library management endpoints."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import UserLibrary, Platform, UserGame
from app.schemas.library import LibraryCreate, LibraryUpdate, LibraryResponse, LibraryListResponse
from app.auth.dependencies import CurrentUser


router = APIRouter(prefix="/api/libraries", tags=["libraries"])


@router.get("", response_model=LibraryListResponse)
async def list_libraries(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 20
) -> LibraryListResponse:
    """List all user libraries."""
    # Get total count
    count_result = await session.execute(
        select(func.count(UserLibrary.library_id))
    )
    total = count_result.scalar() or 0
    
    # Get libraries with platform info
    result = await session.execute(
        select(UserLibrary, Platform)
        .join(Platform, UserLibrary.platform_id == Platform.platform_id)
        .options(selectinload(UserLibrary.user_games))
        .offset(skip)
        .limit(limit)
    )
    
    libraries = []
    for library, platform in result:
        # Count games in library
        games_count = len(library.user_games) if library.user_games else 0
        
        libraries.append(LibraryResponse(
            library_id=library.library_id,
            platform_id=library.platform_id,
            platform_code=platform.platform_code,
            platform_name=platform.platform_name,
            user_identifier=library.user_identifier,
            display_name=library.display_name,
            is_active=library.is_active,
            last_sync_at=library.last_sync_at,
            sync_status=library.sync_status,
            games_count=games_count,
            created_at=library.created_at,
            updated_at=library.updated_at
        ))
    
    return LibraryListResponse(
        libraries=libraries,
        total=total
    )


@router.get("/{library_id}", response_model=LibraryResponse)
async def get_library(
    library_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session)
) -> LibraryResponse:
    """Get a specific library."""
    result = await session.execute(
        select(UserLibrary, Platform)
        .join(Platform, UserLibrary.platform_id == Platform.platform_id)
        .where(UserLibrary.library_id == library_id)
        .options(selectinload(UserLibrary.user_games))
    )
    
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    
    library, platform = row
    games_count = len(library.user_games) if library.user_games else 0
    
    return LibraryResponse(
        library_id=library.library_id,
        platform_id=library.platform_id,
        platform_code=platform.platform_code,
        platform_name=platform.platform_name,
        user_identifier=library.user_identifier,
        display_name=library.display_name,
        is_active=library.is_active,
        last_sync_at=library.last_sync_at,
        sync_status=library.sync_status,
        games_count=games_count,
        created_at=library.created_at,
        updated_at=library.updated_at
    )


@router.post("", response_model=LibraryResponse, status_code=status.HTTP_201_CREATED)
async def create_library(
    library_data: LibraryCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session)
) -> LibraryResponse:
    """Create a new library."""
    # Check if platform exists
    platform_result = await session.execute(
        select(Platform).where(Platform.platform_code == library_data.platform_code)
    )
    platform = platform_result.scalar_one_or_none()
    
    if not platform:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform '{library_data.platform_code}' not found"
        )
    
    if not platform.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform '{library_data.platform_code}' is not enabled"
        )
    
    # Check if library already exists
    existing_result = await session.execute(
        select(UserLibrary).where(
            UserLibrary.platform_id == platform.platform_id,
            UserLibrary.user_identifier == library_data.user_identifier
        )
    )
    
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Library already exists for this platform and user"
        )
    
    # Create new library
    new_library = UserLibrary(
        platform_id=platform.platform_id,
        user_identifier=library_data.user_identifier,
        display_name=library_data.display_name,
        credentials=library_data.credentials or {},
        is_active=True,
        sync_status="pending"
    )
    
    session.add(new_library)
    await session.commit()
    await session.refresh(new_library)
    
    return LibraryResponse(
        library_id=new_library.library_id,
        platform_id=new_library.platform_id,
        platform_code=platform.platform_code,
        platform_name=platform.platform_name,
        user_identifier=new_library.user_identifier,
        display_name=new_library.display_name,
        is_active=new_library.is_active,
        last_sync_at=new_library.last_sync_at,
        sync_status=new_library.sync_status,
        games_count=0,
        created_at=new_library.created_at,
        updated_at=new_library.updated_at
    )


@router.patch("/{library_id}", response_model=LibraryResponse)
async def update_library(
    library_id: UUID,
    library_update: LibraryUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session)
) -> LibraryResponse:
    """Update a library."""
    # Get library with platform info
    result = await session.execute(
        select(UserLibrary, Platform)
        .join(Platform, UserLibrary.platform_id == Platform.platform_id)
        .where(UserLibrary.library_id == library_id)
        .options(selectinload(UserLibrary.user_games))
    )
    
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    
    library, platform = row
    
    # Update fields
    if library_update.display_name is not None:
        library.display_name = library_update.display_name
    if library_update.is_active is not None:
        library.is_active = library_update.is_active
    if library_update.credentials is not None:
        library.credentials = library_update.credentials
    
    await session.commit()
    await session.refresh(library)
    
    games_count = len(library.user_games) if library.user_games else 0
    
    return LibraryResponse(
        library_id=library.library_id,
        platform_id=library.platform_id,
        platform_code=platform.platform_code,
        platform_name=platform.platform_name,
        user_identifier=library.user_identifier,
        display_name=library.display_name,
        is_active=library.is_active,
        last_sync_at=library.last_sync_at,
        sync_status=library.sync_status,
        games_count=games_count,
        created_at=library.created_at,
        updated_at=library.updated_at
    )


@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library(
    library_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session)
) -> None:
    """Delete a library and all associated data."""
    result = await session.execute(
        select(UserLibrary).where(UserLibrary.library_id == library_id)
    )
    
    library = result.scalar_one_or_none()
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    
    # Delete library (cascade will handle user_games)
    await session.delete(library)
    await session.commit()