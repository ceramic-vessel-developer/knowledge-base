from unittest.mock import MagicMock

import pytest
from langchain_core.documents import Document

from backend.common.RetrieverConfigs import RerankerConfig, RerankerTypes
from backend.rag.Reranker import (
    DEFAULT_BGE_RERANKER_MODEL,
    CrossEncoderReranker,
    RerankerFactory,
)


@pytest.fixture
def mock_rerank_model():
    return MagicMock()


class TestCrossEncoderReranker:
    def test_rerank_orders_by_model_scores(self, mock_rerank_model):
        mock_rerank_model.predict.return_value = [0.1, 0.9, 0.5]
        documents = [
            Document(page_content="low"),
            Document(page_content="high"),
            Document(page_content="mid"),
        ]
        reranker = CrossEncoderReranker(model=mock_rerank_model, top_n=3)

        result = reranker.rerank("query", documents)

        assert [doc.page_content for doc in result] == ["high", "mid", "low"]
        mock_rerank_model.predict.assert_called_once_with(
            [["query", "low"], ["query", "high"], ["query", "mid"]]
        )

    def test_rerank_respects_top_n(self, mock_rerank_model):
        mock_rerank_model.predict.return_value = [0.2, 0.8, 0.5]
        documents = [
            Document(page_content="a"),
            Document(page_content="b"),
            Document(page_content="c"),
        ]
        reranker = CrossEncoderReranker(model=mock_rerank_model, top_n=2)

        result = reranker.rerank("query", documents)

        assert [doc.page_content for doc in result] == ["b", "c"]

    def test_rerank_override_top_n_argument(self, mock_rerank_model):
        mock_rerank_model.predict.return_value = [0.2, 0.8, 0.5]
        documents = [
            Document(page_content="a"),
            Document(page_content="b"),
            Document(page_content="c"),
        ]
        reranker = CrossEncoderReranker(model=mock_rerank_model, top_n=3)

        result = reranker.rerank("query", documents, top_n=1)

        assert [doc.page_content for doc in result] == ["b"]

    def test_rerank_handles_single_score(self, mock_rerank_model):
        mock_rerank_model.predict.return_value = 0.42
        documents = [Document(page_content="only")]
        reranker = CrossEncoderReranker(model=mock_rerank_model, top_n=5)

        result = reranker.rerank("query", documents)

        assert result == documents

    def test_empty_documents_skips_model(self, mock_rerank_model):
        reranker = CrossEncoderReranker(model=mock_rerank_model, top_n=5)

        assert reranker.rerank("query", []) == []
        mock_rerank_model.predict.assert_not_called()


class TestRerankerFactory:
    def test_creates_cross_encoder_reranker(self, mock_rerank_model):
        config = RerankerConfig(type=RerankerTypes.CROSS_ENCODER, top_n=3)

        reranker = RerankerFactory.create_reranker(config, mock_rerank_model)

        assert isinstance(reranker, CrossEncoderReranker)
        assert reranker.model is mock_rerank_model
        assert reranker.top_n == 3

    def test_default_model_name_constant(self):
        assert DEFAULT_BGE_RERANKER_MODEL == "BAAI/bge-reranker-v2-m3"

    def test_unknown_type_raises_key_error(self, mock_rerank_model):
        config = MagicMock()
        config.type = "not-a-reranker"
        config.top_n = 5

        with pytest.raises(KeyError):
            RerankerFactory.create_reranker(config, mock_rerank_model)
