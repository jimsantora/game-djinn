"""Collection game model for many-to-many relationship."""

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from uuid import uuid4


class CollectionGame(Base):
    """Many-to-many relationship for collections."""
    
    __tablename__ = "collection_games"
    
    collection_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("game_collections.collection_id", ondelete="CASCADE"),
        primary_key=True
    )
    game_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("games.game_id", ondelete="CASCADE"),
        primary_key=True
    )
    
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="CURRENT_TIMESTAMP",
        nullable=False
    )
    
    # Relationships
    collection = relationship("GameCollection", back_populates="collection_games")
    game = relationship("Game", back_populates="collection_games")
    
    def __repr__(self) -> str:
        return f"<CollectionGame(collection='{self.collection_id}', game='{self.game_id}')>"