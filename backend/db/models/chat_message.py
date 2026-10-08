from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.message_author import MessageAuthor
from backend.db.base import Base, TimestampSoftDeleteMixin

if TYPE_CHECKING:
    from backend.db.models.chat import Chat


class ChatMessage(TimestampSoftDeleteMixin, Base):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[MessageAuthor] = mapped_column(
        Enum(
            MessageAuthor,
            native_enum=False,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
    )

    chat_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chat: Mapped[Chat] = relationship(
        "Chat",
        back_populates="messages",
    )
