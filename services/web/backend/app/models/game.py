"""Game model for universal game catalog."""

from datetime import date
from sqlalchemy import String, Text, Date, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from uuid import uuid4


class Game(Base, TimestampMixin):
    """Universal game catalog with rich metadata."""
    
    __tablename__ = "games"
    
    game_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), unique=True, nullable=True)
    
    # Rich metadata
    description: Mapped[str] = mapped_column(Text, nullable=True)
    short_description: Mapped[str] = mapped_column(Text, nullable=True)
    release_date: Mapped[date] = mapped_column(Date, nullable=True)
    developer: Mapped[str] = mapped_column(String(255), nullable=True)
    publisher: Mapped[str] = mapped_column(String(255), nullable=True)
    genres: Mapped[list] = mapped_column(JSONB, nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, nullable=True)
    platforms_available: Mapped[list] = mapped_column(JSONB, nullable=True)
    
    # Content ratings
    esrb_rating: Mapped[str] = mapped_column(String(20), nullable=True)
    esrb_descriptors: Mapped[list] = mapped_column(JSONB, nullable=True)
    pegi_rating: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Review scores
    metacritic_score: Mapped[int] = mapped_column(Integer, nullable=True)
    metacritic_url: Mapped[str] = mapped_column(String(500), nullable=True)
    steam_score: Mapped[int] = mapped_column(Integer, nullable=True)
    steam_review_count: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Media
    cover_image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    background_image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    screenshots: Mapped[list] = mapped_column(JSONB, nullable=True)
    videos: Mapped[list] = mapped_column(JSONB, nullable=True)
    
    # Game details
    website_url: Mapped[str] = mapped_column(String(500), nullable=True)
    steam_appid: Mapped[int] = mapped_column(Integer, nullable=True)
    gog_id: Mapped[str] = mapped_column(String(100), nullable=True)
    epic_id: Mapped[str] = mapped_column(String(100), nullable=True)
    xbox_id: Mapped[str] = mapped_column(String(100), nullable=True)
    psn_id: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Time estimates
    playtime_main_hours: Mapped[int] = mapped_column(Integer, nullable=True)
    playtime_completionist_hours: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Search optimization
    search_vector: Mapped[str] = mapped_column(TSVECTOR, nullable=True)
    
    # Relationships
    user_games = relationship("UserGame", back_populates="game", cascade="all, delete-orphan")
    achievements = relationship("GameAchievement", back_populates="game", cascade="all, delete-orphan")
    collection_games = relationship("CollectionGame", back_populates="game", cascade="all, delete-orphan")
    primary_matches = relationship("GameMatch", foreign_keys="GameMatch.primary_game_id", back_populates="primary_game")
    matched_games = relationship("GameMatch", foreign_keys="GameMatch.matched_game_id", back_populates="matched_game")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("metacritic_score BETWEEN 0 AND 100", name="ck_metacritic_score"),
        CheckConstraint("steam_score BETWEEN 0 AND 100", name="ck_steam_score"),
    )
    
    def __repr__(self) -> str:
        return f"<Game(title='{self.title}', developer='{self.developer}')>"