from sqlalchemy import Computed
from sqlalchemy.dialects.postgresql import TSVECTOR

from backend.db.constants import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL_NAME
from backend.db.models import Chunk, Document


class TestDbConstants:
    def test_bge_m3_dimensions(self):
        assert EMBEDDING_MODEL_NAME == "BAAI/bge-m3"
        assert EMBEDDING_DIMENSIONS == 1024


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
