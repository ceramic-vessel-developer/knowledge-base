from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.FileTypes import FileTypes
from backend.db.base import Base, TimestampSoftDeleteMixin

if TYPE_CHECKING:
    from backend.db.models.chunk import Chunk
    from backend.db.models.workspace import Workspace


class Document(TimestampSoftDeleteMixin, Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    filename: Mapped[str] = mapped_column(String(1024), nullable=False)
    filetype: Mapped[FileTypes] = mapped_column(
        Enum(FileTypes, name="filetype_enum", native_enum=False),
        nullable=False,
    )

    workspace_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunks: Mapped[list[Chunk]] = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    workspace: Mapped[Workspace] = relationship(
        "Workspace",
        back_populates="documents",
    )
