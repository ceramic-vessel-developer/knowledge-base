from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.workspace_type import WorkspaceType
from backend.db.base import Base, TimestampSoftDeleteMixin

if TYPE_CHECKING:
    from backend.db.models.chat import Chat
    from backend.db.models.document import Document
    from backend.db.models.user import User


class Workspace(TimestampSoftDeleteMixin, Base):
    __tablename__ = "workspaces"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "name",
            name="uq_workspaces_user_id_name",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[WorkspaceType] = mapped_column(
        Enum(
            WorkspaceType,
            native_enum=False,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
        server_default=WorkspaceType.BASIC.value,
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="workspaces",
    )

    documents: Mapped[list[Document]] = relationship(
        "Document",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )

    chats: Mapped[list[Chat]] = relationship(
        "Chat",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
