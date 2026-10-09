
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Character(Base):
    """Représente un personnage WoW importé dans Warband HQ."""

    __tablename__ = "characters"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "blizzard_character_id",
            name="uq_character_user_blizzard_id",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    blizzard_character_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    is_favorite: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(back_populates="characters")
