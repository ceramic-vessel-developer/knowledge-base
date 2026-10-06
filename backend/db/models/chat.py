from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base, TimestampSoftDeleteMixin

if TYPE_CHECKING:
    from backend.db.models.chat_message import ChatMessage
    from backend.db.models.workspace import Workspace


class Chat(TimestampSoftDeleteMixin, Base):
    __tablename__ = "chats"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    workspace_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    messages: Mapped[list[ChatMessage]] = relationship(
        "ChatMessage",
        back_populates="chat",
        cascade="all, delete-orphan",
    )

    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="chats",
    )
