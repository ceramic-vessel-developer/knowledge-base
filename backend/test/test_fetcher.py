from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from langchain_core.documents import Document
from pydantic import ValidationError

from backend.common.RetrieverConfigs import (
    FetcherCategories,
    FetcherConfig,
    FetcherTypes,
)
from backend.rag.Fetcher import (
    FetcherFactory,
    MMRFetcher,
    PGLexicalFetcher,
    SimilarityFetcher,
)


class TestSimilarityFetcher:
    def test_fetch_candidates_calls_similarity_search(self, mock_vector_store):
        expected = [Document(page_content="hit")]
        mock_vector_store.similarity_search.return_value = expected
        document_ids = [str(uuid4()), str(uuid4())]
        fetcher = SimilarityFetcher(mock_vector_store, k=5)

        result = fetcher.fetch_candidates("what is rag?", document_ids)

        assert result == expected
        mock_vector_store.similarity_search.assert_called_once_with(
            "what is rag?",
            k=5,
            filter={"document_id": {"$in": document_ids}},
        )

    def test_empty_document_ids_skips_search(self, mock_vector_store):
        fetcher = SimilarityFetcher(mock_vector_store, k=5)

        result = fetcher.fetch_candidates("what is rag?", [])

        assert result == []
        mock_vector_store.similarity_search.assert_not_called()


class TestMMRFetcher:
    def test_fetch_candidates_calls_mmr_search(self, mock_vector_store):
        expected = [Document(page_content="diverse hit")]
        mock_vector_store.max_marginal_relevance_search.return_value = expected
        document_ids = [str(uuid4())]
        fetcher = MMRFetcher(mock_vector_store, k=3)

        result = fetcher.fetch_candidates("embeddings", document_ids)

        assert result == expected
        mock_vector_store.max_marginal_relevance_search.assert_called_once_with(
            "embeddings",
            k=3,
            filter={"document_id": {"$in": document_ids}},
        )

    def test_empty_document_ids_skips_search(self, mock_vector_store):
        fetcher = MMRFetcher(mock_vector_store, k=3)

        result = fetcher.fetch_candidates("embeddings", [])

        assert result == []
        mock_vector_store.max_marginal_relevance_search.assert_not_called()


class TestPGLexicalFetcher:
    def test_fetch_candidates_raises_not_implemented(self):
        fetcher = PGLexicalFetcher(k=10, db_session=MagicMock())

        with pytest.raises(NotImplementedError):
            fetcher.fetch_candidates("error code 0x803", [str(uuid4())])

    def test_empty_document_ids_returns_without_search(self):
        fetcher = PGLexicalFetcher(k=10, db_session=MagicMock())

        assert fetcher.fetch_candidates("error code 0x803", []) == []

    def test_stores_db_session(self):
        session = MagicMock()
        fetcher = PGLexicalFetcher(k=10, db_session=session)

        assert fetcher.db_session is session


class TestFetcherConfigValidation:
    def test_rejects_lexical_under_dense(self):
        with pytest.raises(ValidationError):
            FetcherConfig(
                category=FetcherCategories.DENSE,
                type=FetcherTypes.LEXICAL,
            )

    def test_rejects_similarity_under_sparse(self):
        with pytest.raises(ValidationError):
            FetcherConfig(
                category=FetcherCategories.SPARSE,
                type=FetcherTypes.SIMILARITY,
            )


class TestFetcherFactory:
    def test_creates_similarity_fetcher(self, rag_runtime):
        config = FetcherConfig(
            category=FetcherCategories.DENSE,
            type=FetcherTypes.SIMILARITY,
            k=7,
        )

        fetcher = FetcherFactory.create_fetcher(config, rag_runtime)

        assert isinstance(fetcher, SimilarityFetcher)
        assert fetcher.vector_store is rag_runtime.vector_store
        assert fetcher.k == 7

    def test_creates_mmr_fetcher(self, rag_runtime):
        config = FetcherConfig(
            category=FetcherCategories.DENSE,
            type=FetcherTypes.MMR,
            k=4,
        )

        fetcher = FetcherFactory.create_fetcher(config, rag_runtime)

        assert isinstance(fetcher, MMRFetcher)
        assert fetcher.k == 4

    def test_creates_lexical_fetcher_with_db_session(self, rag_runtime_with_reranker):
        config = FetcherConfig(
            category=FetcherCategories.SPARSE,
            type=FetcherTypes.LEXICAL,
        )

        fetcher = FetcherFactory.create_fetcher(config, rag_runtime_with_reranker)

        assert isinstance(fetcher, PGLexicalFetcher)
        assert fetcher.k == 10
        assert fetcher.db_session is rag_runtime_with_reranker.db_session
        assert not hasattr(fetcher, "vector_store")

    def test_sparse_without_db_session_raises(self, rag_runtime):
        config = FetcherConfig(
            category=FetcherCategories.SPARSE,
            type=FetcherTypes.LEXICAL,
        )

        with pytest.raises(ValueError, match="runtime.db_session is required"):
            FetcherFactory.create_fetcher(config, rag_runtime)

    def test_unknown_dense_type_raises_key_error(self, rag_runtime):
        config = MagicMock()
        config.category = FetcherCategories.DENSE
        config.type = "not-a-fetcher"
        config.k = 10

        with pytest.raises(KeyError):
            FetcherFactory.create_fetcher(config, rag_runtime)

    def test_unknown_sparse_type_raises_key_error(self, rag_runtime_with_reranker):
        config = MagicMock()
        config.category = FetcherCategories.SPARSE
        config.type = "not-a-fetcher"
        config.k = 10

        with pytest.raises(KeyError):
            FetcherFactory.create_fetcher(config, rag_runtime_with_reranker)

    def test_unknown_category_raises_not_implemented(self, rag_runtime):
        config = MagicMock()
        config.category = "hybrid"
        config.type = FetcherTypes.SIMILARITY
        config.k = 10

        with pytest.raises(NotImplementedError):
            FetcherFactory.create_fetcher(config, rag_runtime)
