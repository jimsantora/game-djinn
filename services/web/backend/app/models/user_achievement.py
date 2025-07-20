"""User achievement model for user achievement unlocks."""

from datetime import datetime
from sqlalchemy import DateTime, Integer, CheckConstraint, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from uuid import uuid4


class UserAchievement(Base):
    """User achievement unlocks."""
    
    __tablename__ = "user_achievements"
    
    user_achievement_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    user_game_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_games.user_game_id", ondelete="CASCADE"),
        nullable=False
    )
    achievement_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("game_achievements.achievement_id", ondelete="CASCADE"),
        nullable=False
    )
    
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    progress_percentage: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="CURRENT_TIMESTAMP",
        nullable=False
    )
    
    # Relationships
    user_game = relationship("UserGame", back_populates="achievements")
    achievement = relationship("GameAchievement", back_populates="user_achievements")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_game_id", "achievement_id", name="uq_user_game_achievement"),
        CheckConstraint("progress_percentage BETWEEN 0 AND 100", name="ck_progress_percentage"),
    )
    
    def __repr__(self) -> str:
        return f"<UserAchievement(achievement='{self.achievement_id}', progress={self.progress_percentage}%)>"