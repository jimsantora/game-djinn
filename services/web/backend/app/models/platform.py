"""Platform model for gaming platforms."""

from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from uuid import uuid4


class Platform(Base, TimestampMixin):
    """Gaming platform model (Steam, Xbox, GOG, etc.)."""
    
    __tablename__ = "platforms"
    
    platform_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    platform_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    platform_name: Mapped[str] = mapped_column(String(100), nullable=False)
    api_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    icon_url: Mapped[str] = mapped_column(String(500), nullable=True)
    base_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Relationships
    user_libraries = relationship("UserLibrary", back_populates="platform", cascade="all, delete-orphan")
    game_achievements = relationship("GameAchievement", back_populates="platform", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Platform(code='{self.platform_code}', name='{self.platform_name}')>"