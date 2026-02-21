from sqlalchemy import Boolean, ForeignKey, String

from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Resources(Base):
    __tablename__ = 'resources'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)


class Rules(Base):
    __tablename__ = 'access_roles_rules'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, primary_key=True)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('roles.id'))
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('resources.id'))
    read_p: Mapped[bool] = mapped_column(Boolean, nullable=False)
    read_all_p: Mapped[bool] = mapped_column(Boolean, nullable=False)
    create_p: Mapped[bool] = mapped_column(Boolean, nullable=False)
    update_p: Mapped[bool] = mapped_column(Boolean, nullable=False)
    update_all_p: Mapped[bool] = mapped_column(Boolean, nullable=False)
    delete_p: Mapped[bool] = mapped_column(Boolean, nullable=False)
    delete_all_p: Mapped[bool] = mapped_column(Boolean, nullable=False)


class Roles(Base):
    __tablename__ = 'roles'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
