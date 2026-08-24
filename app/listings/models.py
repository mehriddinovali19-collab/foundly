from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum,  ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.database import Base
from app.listings.constants import ListingStatus, ListingType

if TYPE_CHECKING:
    from app.users.models import User

class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True,)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True,)
    description: Mapped[str] = mapped_column(Text, nullable=False,)
    type: Mapped[ListingType] = mapped_column(Enum(ListingType), nullable=False,)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True,)
    date: Mapped[date] = mapped_column(Date, nullable=False,)
    status: Mapped[ListingStatus] = mapped_column(Enum(ListingStatus), default=ListingStatus.ACTIVE, nullable=False,)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False,)
    user: Mapped["User"] = relationship("User", back_populates="listings",)