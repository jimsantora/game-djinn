"""Game collection model for organizing games."""

from sqlalchemy import String, Text, Boolean, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from uuid import uuid4


class GameCollection(Base, TimestampMixin):
    """Smart collections for organizing games."""
    
    __tablename__ = "game_collections"
    
    collection_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    library_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_libraries.library_id", ondelete="CASCADE"),
        nullable=False
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(20), nullable=True)
    icon: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # Collection rules (for smart collections)
    is_smart: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rules: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    library = relationship("UserLibrary", back_populates="game_collections")
    collection_games = relationship("CollectionGame", back_populates="collection", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("library_id", "name", name="uq_library_collection_name"),
    )
    
    def __repr__(self) -> str:
        return f"<GameCollection(name='{self.name}', smart={self.is_smart})>"