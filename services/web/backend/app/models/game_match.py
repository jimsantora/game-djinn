"""Game match model for cross-platform detection."""

from sqlalchemy import String, DECIMAL, Boolean, CheckConstraint, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from uuid import uuid4


class GameMatch(Base, TimestampMixin):
    """Game matching for cross-platform detection."""
    
    __tablename__ = "game_matches"
    
    match_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    primary_game_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("games.game_id", ondelete="CASCADE"),
        nullable=False
    )
    matched_game_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("games.game_id", ondelete="CASCADE"),
        nullable=False
    )
    
    match_confidence: Mapped[float] = mapped_column(DECIMAL(3, 2), nullable=True)
    match_method: Mapped[str] = mapped_column(String(50), nullable=True)  # title_exact, title_fuzzy, external_id, manual
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    primary_game = relationship("Game", foreign_keys=[primary_game_id], back_populates="primary_matches")
    matched_game = relationship("Game", foreign_keys=[matched_game_id], back_populates="matched_games")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("primary_game_id", "matched_game_id", name="uq_primary_matched_game"),
        CheckConstraint("match_confidence BETWEEN 0.0 AND 1.0", name="ck_match_confidence"),
    )
    
    def __repr__(self) -> str:
        return f"<GameMatch(primary='{self.primary_game_id}', matched='{self.matched_game_id}', confidence={self.match_confidence})>"