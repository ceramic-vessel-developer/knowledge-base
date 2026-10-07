from sqlalchemy import Boolean, Computed, DateTime, inspect
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import configure_mappers

from backend.common.message_author import MessageAuthor
from backend.common.role import UserRole
from backend.common.workspace_type import WorkspaceType
from backend.db.base import TimestampSoftDeleteMixin
from backend.db.constants import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL_NAME
from backend.db.models import Chat, ChatMessage, Chunk, Document, User, Workspace

AUDIT_COLUMNS = ("created_at", "modified_at", "deleted_at", "is_deleted")
ALL_MODELS = (User, Workspace, Document, Chunk, Chat, ChatMessage)


def _fk_targets(column) -> set[str]:
    return {f"{fk.column.table.name}.{fk.column.name}" for fk in column.foreign_keys}


def _constraint_names(model) -> set[str | None]:
    return {constraint.name for constraint in model.__table__.constraints}


class TestDbConstants:
    def test_bge_m3_dimensions(self):
        assert EMBEDDING_MODEL_NAME == "BAAI/bge-m3"
        assert EMBEDDING_DIMENSIONS == 1024


class TestTimestampSoftDeleteMixin:
    def test_all_models_use_mixin(self):
        for model in ALL_MODELS:
            assert issubclass(model, TimestampSoftDeleteMixin)

    def test_all_models_have_audit_columns(self):
        for model in ALL_MODELS:
            columns = model.__table__.c
            for name in AUDIT_COLUMNS:
                assert name in columns
            assert isinstance(columns.created_at.type, DateTime)
            assert isinstance(columns.modified_at.type, DateTime)
            assert isinstance(columns.deleted_at.type, DateTime)
            assert isinstance(columns.is_deleted.type, Boolean)
            assert columns.deleted_at.nullable is True
            assert columns.is_deleted.nullable is False


class TestUserModel:
    def test_tablename(self):
        assert User.__tablename__ == "users"

    def test_required_columns(self):
        columns = User.__table__.c
        for name in ("id", "username", "email", "password_hash", "role"):
            assert name in columns
            assert columns[name].nullable is False

    def test_email_unique_username_not_unique(self):
        assert User.__table__.c.email.unique is True
        assert User.__table__.c.username.unique in (None, False)

    def test_role_defaults_to_user_value(self):
        role_col = User.__table__.c.role
        assert str(role_col.server_default.arg) == UserRole.USER.value
        assert set(role_col.type.enums) == {UserRole.USER.value, UserRole.ADMIN.value}

    def test_workspaces_relationship_cascade(self):
        rel = User.workspaces.property
        assert rel.mapper.class_ is Workspace
        assert rel.back_populates == "user"
        assert "delete-orphan" in rel.cascade


class TestWorkspaceModel:
    def test_tablename(self):
        assert Workspace.__tablename__ == "workspaces"

    def test_user_fk_cascades(self):
        user_id = Workspace.__table__.c.user_id
        assert _fk_targets(user_id) == {"users.id"}
        assert {fk.ondelete for fk in user_id.foreign_keys} == {"CASCADE"}
        assert user_id.nullable is False

    def test_unique_user_id_name(self):
        assert "uq_workspaces_user_id_name" in _constraint_names(Workspace)

    def test_type_defaults_to_basic(self):
        type_col = Workspace.__table__.c.type
        assert str(type_col.server_default.arg) == WorkspaceType.BASIC.value
        assert set(type_col.type.enums) == {WorkspaceType.BASIC.value}

    def test_child_relationships(self):
        assert Workspace.documents.property.mapper.class_ is Document
        assert Workspace.chats.property.mapper.class_ is Chat
        assert "delete-orphan" in Workspace.documents.property.cascade
        assert "delete-orphan" in Workspace.chats.property.cascade


class TestDocumentModel:
    def test_tablename(self):
        assert Document.__tablename__ == "documents"

    def test_workspace_fk_cascades(self):
        workspace_id = Document.__table__.c.workspace_id
        assert _fk_targets(workspace_id) == {"workspaces.id"}
        assert {fk.ondelete for fk in workspace_id.foreign_keys} == {"CASCADE"}

    def test_has_chunks_and_workspace_relationships(self):
        assert Document.chunks.property.mapper.class_ is Chunk
        assert Document.workspace.property.mapper.class_ is Workspace
        assert Document.chunks.property.back_populates == "document"
        assert Document.workspace.property.back_populates == "documents"


class TestChunkModel:
    def test_tablename(self):
        assert Chunk.__tablename__ == "chunks"

    def test_document_fk_cascades(self):
        document_id = Chunk.__table__.c.document_id
        assert _fk_targets(document_id) == {"documents.id"}
        assert {fk.ondelete for fk in document_id.foreign_keys} == {"CASCADE"}

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
        assert "uq_chunks_document_id_chunk_index" in _constraint_names(Chunk)


class TestChatModel:
    def test_tablename(self):
        assert Chat.__tablename__ == "chats"

    def test_workspace_fk_cascades(self):
        workspace_id = Chat.__table__.c.workspace_id
        assert _fk_targets(workspace_id) == {"workspaces.id"}
        assert {fk.ondelete for fk in workspace_id.foreign_keys} == {"CASCADE"}

    def test_messages_relationship_targets_chat_message(self):
        rel = Chat.messages.property
        assert rel.mapper.class_ is ChatMessage
        assert rel.back_populates == "chat"
        assert "delete-orphan" in rel.cascade

    def test_workspace_relationship(self):
        assert Chat.workspace.property.mapper.class_ is Workspace
        assert Chat.workspace.property.back_populates == "chats"


class TestChatMessageModel:
    def test_tablename(self):
        assert ChatMessage.__tablename__ == "chat_messages"

    def test_chat_fk_cascades(self):
        chat_id = ChatMessage.__table__.c.chat_id
        assert _fk_targets(chat_id) == {"chats.id"}
        assert {fk.ondelete for fk in chat_id.foreign_keys} == {"CASCADE"}

    def test_author_enum_values(self):
        author_col = ChatMessage.__table__.c.author
        assert set(author_col.type.enums) == {
            MessageAuthor.USER.value,
            MessageAuthor.AI.value,
        }
        assert author_col.nullable is False

    def test_chat_relationship(self):
        assert ChatMessage.chat.property.mapper.class_ is Chat
        assert ChatMessage.chat.property.back_populates == "messages"


class TestModelRelationships:
    def test_mappers_configure_without_error(self):
        configure_mappers()

    def test_metadata_contains_all_tables(self):
        table_names = set(inspect(User).registry.metadata.tables)
        assert {
            "users",
            "workspaces",
            "documents",
            "chunks",
            "chats",
            "chat_messages",
        }.issubset(table_names)

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
