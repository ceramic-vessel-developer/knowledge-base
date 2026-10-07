from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Computed, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base, TimestampSoftDeleteMixin
from backend.db.constants import EMBEDDING_DIMENSIONS

if TYPE_CHECKING:
    from backend.db.models.document import Document


class Chunk(TimestampSoftDeleteMixin, Base):
    """Owned chunk row: dense embedding + auto-generated lexical tsvector.

    ``content_tsv`` is a Postgres GENERATED ALWAYS column; do not set it in ORM
    inserts. Dense search uses ``embedding`` (BGE-M3, 1024-d); lexical search
    will use ``content_tsv`` via ``RagRuntime.db_session``.
    """

    __tablename__ = "chunks"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_chunks_document_id_chunk_index",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(EMBEDDING_DIMENSIONS),
        nullable=False,
    )
    content_tsv: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', content)", persisted=True),
        nullable=False,
    )

    document: Mapped[Document] = relationship("Document", back_populates="chunks")
