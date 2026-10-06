"""Wire LangChain PGVectorStore to the owned ``chunks`` table.

Schema is managed by Alembic (including generated ``content_tsv``).
Dense search/ingest go through ``PGVectorStore.create_sync`` mapped to
existing columns — no LangChain-owned table creation.
"""

from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_postgres import PGEngine, PGVectorStore

from backend.db.session import get_database_url

CHUNKS_TABLE = "chunks"
CHUNKS_ID_COLUMN = "id"
CHUNKS_CONTENT_COLUMN = "content"
CHUNKS_EMBEDDING_COLUMN = "embedding"
CHUNKS_METADATA_COLUMNS = ["document_id", "chunk_index"]


def create_pg_engine(database_url: str | None = None) -> PGEngine:
    return PGEngine.from_connection_string(url=database_url or get_database_url())


def create_chunks_vector_store(
    embedding_service: Embeddings,
    *,
    engine: PGEngine | None = None,
    database_url: str | None = None,
) -> PGVectorStore:
    """Attach a sync PGVectorStore to the existing ``chunks`` table.

    ``engine`` must be a LangChain ``PGEngine`` (not a raw SQLAlchemy Engine).
    If omitted, one is created from ``database_url`` / ``DATABASE_URL``.

    Example::

        from langchain_huggingface import HuggingFaceEmbeddings
        from backend.db.constants import EMBEDDING_MODEL_NAME
        from backend.db.vector_store import create_chunks_vector_store

        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        vector_store = create_chunks_vector_store(embeddings)
    """
    pg_engine = engine or create_pg_engine(database_url)
    return PGVectorStore.create_sync(
        engine=pg_engine,
        table_name=CHUNKS_TABLE,
        embedding_service=embedding_service,
        id_column=CHUNKS_ID_COLUMN,
        content_column=CHUNKS_CONTENT_COLUMN,
        embedding_column=CHUNKS_EMBEDDING_COLUMN,
        metadata_columns=list(CHUNKS_METADATA_COLUMNS),
    )
