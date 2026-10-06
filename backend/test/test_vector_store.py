from unittest.mock import MagicMock, patch

from backend.db.vector_store import (
    CHUNKS_CONTENT_COLUMN,
    CHUNKS_EMBEDDING_COLUMN,
    CHUNKS_ID_COLUMN,
    CHUNKS_METADATA_COLUMNS,
    CHUNKS_TABLE,
    create_chunks_vector_store,
    create_pg_engine,
)


class TestCreateChunksVectorStore:
    @patch("backend.db.vector_store.PGVectorStore.create_sync")
    def test_maps_owned_chunks_columns(self, mock_create_sync):
        embeddings = MagicMock()
        engine = MagicMock()
        mock_create_sync.return_value = MagicMock()

        store = create_chunks_vector_store(embeddings, engine=engine)

        mock_create_sync.assert_called_once_with(
            engine=engine,
            table_name=CHUNKS_TABLE,
            embedding_service=embeddings,
            id_column=CHUNKS_ID_COLUMN,
            content_column=CHUNKS_CONTENT_COLUMN,
            embedding_column=CHUNKS_EMBEDDING_COLUMN,
            metadata_columns=list(CHUNKS_METADATA_COLUMNS),
        )
        assert store is mock_create_sync.return_value

    @patch("backend.db.vector_store.PGEngine.from_connection_string")
    @patch("backend.db.vector_store.PGVectorStore.create_sync")
    def test_builds_engine_from_url_when_missing(
        self, mock_create_sync, mock_from_url
    ):
        embeddings = MagicMock()
        mock_from_url.return_value = MagicMock()
        mock_create_sync.return_value = MagicMock()

        create_chunks_vector_store(
            embeddings, database_url="postgresql+psycopg://localhost/db"
        )

        mock_from_url.assert_called_once_with(
            url="postgresql+psycopg://localhost/db"
        )
        mock_create_sync.assert_called_once()
        assert mock_create_sync.call_args.kwargs["engine"] is mock_from_url.return_value


class TestCreatePgEngine:
    @patch("backend.db.vector_store.PGEngine.from_connection_string")
    def test_uses_provided_url(self, mock_from_url):
        mock_from_url.return_value = MagicMock()

        engine = create_pg_engine("postgresql+psycopg://localhost/db")

        mock_from_url.assert_called_once_with(
            url="postgresql+psycopg://localhost/db"
        )
        assert engine is mock_from_url.return_value
