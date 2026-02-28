from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String

from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone


def _utcnow_naive() -> datetime:
    """Naive UTC datetime using non-deprecated API."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Goods(Base):
    __tablename__ = 'goods'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(
        String, default='Описание отсутствует')
    price: Mapped[float] = mapped_column(Float, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('businesses.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow_naive)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
