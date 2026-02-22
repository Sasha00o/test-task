import uuid

from sqlalchemy import Boolean, ForeignKey, String

from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID


class Businesses(Base):
    __tablename__ = 'businesses'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('roles.id'), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
