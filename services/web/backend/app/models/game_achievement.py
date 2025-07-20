"""Game achievement model for cross-platform achievements."""

from sqlalchemy import String, Text, Integer, Boolean, DECIMAL, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from uuid import uuid4


class GameAchievement(Base, TimestampMixin):
    """Cross-platform achievements/trophies."""
    
    __tablename__ = "game_achievements"
    
    achievement_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    game_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("games.game_id", ondelete="CASCADE"),
        nullable=False
    )
    platform_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("platforms.platform_id", ondelete="CASCADE"),
        nullable=False
    )
    
    platform_achievement_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str] = mapped_column(String(500), nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rarity_percentage: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=True)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    game = relationship("Game", back_populates="achievements")
    platform = relationship("Platform", back_populates="game_achievements")
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("game_id", "platform_id", "platform_achievement_id", name="uq_game_platform_achievement"),
    )
    
    def __repr__(self) -> str:
        return f"<GameAchievement(title='{self.title}', game='{self.game_id}')>"