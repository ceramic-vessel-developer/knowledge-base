from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.role import UserRole
from backend.db.base import Base, TimestampSoftDeleteMixin

if TYPE_CHECKING:
    from backend.db.models.workspace import Workspace


class User(TimestampSoftDeleteMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            native_enum=False,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
        server_default=UserRole.USER.value,
    )

    workspaces: Mapped[list[Workspace]] = relationship(
        "Workspace",
        back_populates="user",
        cascade="all, delete-orphan",
    )
