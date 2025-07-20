"""User game model for user-specific game data."""

from enum import Enum
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Integer, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from uuid import uuid4


class GameStatus(str, Enum):
    """Game status enum."""
    UNPLAYED = "unplayed"
    PLAYING = "playing"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    WISHLIST = "wishlist"


class UserGame(Base, TimestampMixin):
    """User-specific game data."""
    
    __tablename__ = "user_games"
    
    user_game_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    library_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_libraries.library_id", ondelete="CASCADE"),
        nullable=False
    )
    game_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("games.game_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Platform-specific identifiers
    platform_game_id: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # User data
    owned: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    owned_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Playtime tracking
    total_playtime_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_played_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    first_played_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # User preferences
    game_status: Mapped[str] = mapped_column(String(50), default=GameStatus.UNPLAYED, nullable=False)
    user_rating: Mapped[int] = mapped_column(Integer, nullable=True)
    user_notes: Mapped[str] = mapped_column(Text, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Platform-specific data
    platform_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    # Sync metadata
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="CURRENT_TIMESTAMP",
        nullable=False
    )
    
    # Relationships
    library = relationship("UserLibrary", back_populates="user_games")
    game = relationship("Game", back_populates="user_games")
    achievements = relationship("UserAchievement", back_populates="user_game", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("library_id", "game_id", name="uq_library_game"),
        CheckConstraint("user_rating BETWEEN 1 AND 5", name="ck_user_rating"),
    )
    
    def __repr__(self) -> str:
        return f"<UserGame(game='{self.game_id}', status='{self.game_status}')>"