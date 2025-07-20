"""User library model for platform-specific game libraries."""

from enum import Enum
from datetime import datetime
from sqlalchemy import String, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from uuid import uuid4


class SyncStatus(str, Enum):
    """Synchronization status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"


class UserLibrary(Base, TimestampMixin):
    """User's platform-specific game library."""
    
    __tablename__ = "user_libraries"
    
    library_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    platform_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("platforms.platform_id", ondelete="CASCADE"),
        nullable=False
    )
    user_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_credentials: Mapped[dict] = mapped_column(JSONB, nullable=True)
    sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_sync_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_status: Mapped[str] = mapped_column(String(50), default=SyncStatus.PENDING, nullable=False)
    sync_error: Mapped[str] = mapped_column(Text, nullable=True)
    sync_position: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    platform = relationship("Platform", back_populates="user_libraries")
    user_games = relationship("UserGame", back_populates="library", cascade="all, delete-orphan")
    game_collections = relationship("GameCollection", back_populates="library", cascade="all, delete-orphan")
    sync_operations = relationship("SyncOperation", back_populates="library", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("platform_id", "user_identifier", name="uq_platform_user"),
    )
    
    def __repr__(self) -> str:
        return f"<UserLibrary(display_name='{self.display_name}', platform='{self.platform_id}')>"