from sqlalchemy import DateTime, Float, ForeignKey, Integer, String

from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone


def _utcnow_naive() -> datetime:
    """Naive UTC datetime using non-deprecated API."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Orders(Base):
    __tablename__ = 'orders'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id'), nullable=False)
    good_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('goods.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_address: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default='PENDING')
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow_naive)
