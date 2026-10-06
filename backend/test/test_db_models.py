from sqlalchemy import Boolean, Computed, DateTime
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import configure_mappers

from backend.db.base import TimestampSoftDeleteMixin
from backend.db.constants import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL_NAME
from backend.db.models import Chat, ChatMessage, Chunk, Document, User, Workspace


class TestDbConstants:
    def test_bge_m3_dimensions(self):
        assert EMBEDDING_MODEL_NAME == "BAAI/bge-m3"
        assert EMBEDDING_DIMENSIONS == 1024


class TestTimestampSoftDeleteMixin:
    def test_document_has_audit_columns(self):
        columns = Document.__table__.c
        assert isinstance(columns.created_at.type, DateTime)
        assert isinstance(columns.modified_at.type, DateTime)
        assert isinstance(columns.deleted_at.type, DateTime)
        assert isinstance(columns.is_deleted.type, Boolean)
        assert columns.deleted_at.nullable is True
        assert columns.is_deleted.nullable is False

    def test_chunk_has_audit_columns(self):
        columns = Chunk.__table__.c
        for name in ("created_at", "modified_at", "deleted_at", "is_deleted"):
            assert name in columns

    def test_models_use_mixin(self):
        assert issubclass(Document, TimestampSoftDeleteMixin)
        assert issubclass(Chunk, TimestampSoftDeleteMixin)


class TestDocumentModel:
    def test_tablename(self):
        assert Document.__tablename__ == "documents"

    def test_has_chunks_relationship(self):
        assert "chunks" in Document.__mapper__.relationships


class TestChunkModel:
    def test_tablename(self):
        assert Chunk.__tablename__ == "chunks"

    def test_embedding_uses_bge_m3_dimensions(self):
        embedding_col = Chunk.__table__.c.embedding
        assert embedding_col.type.dim == EMBEDDING_DIMENSIONS

    def test_content_tsv_is_generated_persisted(self):
        content_tsv = Chunk.__table__.c.content_tsv
        assert isinstance(content_tsv.type, TSVECTOR)
        assert content_tsv.computed is not None
        assert isinstance(content_tsv.computed, Computed)
        assert content_tsv.computed.persisted is True
        assert "to_tsvector" in str(content_tsv.computed.sqltext)

    def test_unique_document_chunk_index(self):
        constraint_names = {
            constraint.name for constraint in Chunk.__table__.constraints
        }
        assert "uq_chunks_document_id_chunk_index" in constraint_names


class TestModelRelationships:
    def test_mappers_configure_without_error(self):
        configure_mappers()

    def test_user_workspace_back_populates(self):
        assert User.workspaces.property.back_populates == "user"
        assert Workspace.user.property.back_populates == "workspaces"

    def test_workspace_document_chat_back_populates(self):
        assert Workspace.documents.property.back_populates == "workspace"
        assert Document.workspace.property.back_populates == "documents"
        assert Workspace.chats.property.back_populates == "workspace"
        assert Chat.workspace.property.back_populates == "chats"

    def test_chat_message_back_populates(self):
        assert Chat.messages.property.mapper.class_ is ChatMessage
        assert Chat.messages.property.back_populates == "chat"
        assert ChatMessage.chat.property.back_populates == "messages"

    def test_username_is_not_unique(self):
        assert User.__table__.c.username.unique in (None, False)
        assert User.__table__.c.email.unique is True
