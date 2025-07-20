"""Sync operation model for tracking and debugging."""

from enum import Enum
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from uuid import uuid4


class OperationType(str, Enum):
    """Sync operation type enum."""
    FULL_SYNC = "full_sync"
    INCREMENTAL_SYNC = "incremental_sync"
    MANUAL_SYNC = "manual_sync"


class OperationStatus(str, Enum):
    """Sync operation status enum."""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SyncOperation(Base, TimestampMixin):
    """Sync operations log for tracking and debugging."""
    
    __tablename__ = "sync_operations"
    
    operation_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    library_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_libraries.library_id", ondelete="CASCADE"),
        nullable=False
    )
    
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="CURRENT_TIMESTAMP",
        nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    games_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    games_added: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    games_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    error_details: Mapped[dict] = mapped_column(JSONB, nullable=True)
    operation_log: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    library = relationship("UserLibrary", back_populates="sync_operations")
    
    def __repr__(self) -> str:
        return f"<SyncOperation(type='{self.operation_type}', status='{self.status}', library='{self.library_id}')>"