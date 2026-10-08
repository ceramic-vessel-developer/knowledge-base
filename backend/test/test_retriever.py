from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from langchain_core.documents import Document

from backend.common.RetrieverConfigs import (
    FetcherCategories,
    FetcherConfig,
    FetcherTypes,
    FusionConfig,
    FusionTypes,
    RerankerConfig,
    RerankerTypes,
    RetrieverConfig,
)
from backend.rag.Retriever import Retriever, RetrieverFactory


class TestRetriever:
    def test_retrieve_single_fetcher_without_fusion(self):
        docs = [Document(page_content="a"), Document(page_content="b")]
        fetcher = MagicMock()
        fetcher.fetch_candidates.return_value = docs
        document_ids = [str(uuid4())]

        result = Retriever(fetchers=[fetcher]).retrieve("query", document_ids)

        assert result == docs
        fetcher.fetch_candidates.assert_called_once_with("query", document_ids)

    def test_retrieve_fuses_multiple_fetcher_results(self):
        list_1 = [Document(page_content="a")]
        list_2 = [Document(page_content="b")]
        fetcher_1 = MagicMock()
        fetcher_2 = MagicMock()
        fetcher_1.fetch_candidates.return_value = list_1
        fetcher_2.fetch_candidates.return_value = list_2
        fusion = MagicMock()
        fused = [Document(page_content="fused")]
        fusion.fuse.return_value = fused
        document_ids = [str(uuid4())]

        result = Retriever(
            fetchers=[fetcher_1, fetcher_2],
            fusion=fusion,
        ).retrieve("query", document_ids)

        fusion.fuse.assert_called_once_with([list_1, list_2])
        assert result == fused

    def test_retrieve_requires_fusion_for_multiple_fetchers(self):
        fetcher_1 = MagicMock()
        fetcher_2 = MagicMock()
        fetcher_1.fetch_candidates.return_value = [Document(page_content="a")]
        fetcher_2.fetch_candidates.return_value = [Document(page_content="b")]

        with pytest.raises(
            ValueError, match="Multiple fetchers require a fusion strategy"
        ):
            Retriever(fetchers=[fetcher_1, fetcher_2]).retrieve("query", [str(uuid4())])

    def test_retrieve_applies_reranker_with_reranker_top_n(self):
        docs = [Document(page_content="a"), Document(page_content="b")]
        fetcher = MagicMock()
        fetcher.fetch_candidates.return_value = docs
        reranker = MagicMock()
        reranked = [Document(page_content="b")]
        reranker.rerank.return_value = reranked

        result = Retriever(
            fetchers=[fetcher],
            reranker=reranker,
            top_n=10,
        ).retrieve("query", [str(uuid4())])

        # RetrieverConfig.top_n must not override RerankerConfig.top_n.
        reranker.rerank.assert_called_once_with("query", docs)
        assert result == reranked

    def test_retrieve_truncates_with_top_n_without_reranker(self):
        docs = [
            Document(page_content="a"),
            Document(page_content="b"),
            Document(page_content="c"),
        ]
        fetcher = MagicMock()
        fetcher.fetch_candidates.return_value = docs

        result = Retriever(fetchers=[fetcher], top_n=2).retrieve(
            "query", [str(uuid4())]
        )

        assert result == docs[:2]

    def test_retrieve_with_no_fetchers_returns_empty(self):
        assert Retriever(fetchers=[]).retrieve("query", [str(uuid4())]) == []


class TestRetrieverFactory:
    @patch("backend.rag.Retriever.RerankerFactory.create_reranker")
    @patch("backend.rag.Retriever.FusionFactory.create_fusion")
    @patch("backend.rag.Retriever.FetcherFactory.create_fetcher")
    def test_create_retriever_wires_dependencies(
        self,
        mock_create_fetcher,
        mock_create_fusion,
        mock_create_reranker,
        rag_runtime_with_reranker,
    ):
        fetcher = MagicMock()
        fusion = MagicMock()
        reranker = MagicMock()
        mock_create_fetcher.return_value = fetcher
        mock_create_fusion.return_value = fusion
        mock_create_reranker.return_value = reranker

        fetcher_config = FetcherConfig(
            category=FetcherCategories.DENSE,
            type=FetcherTypes.SIMILARITY,
            k=5,
        )
        fusion_config = FusionConfig(type=FusionTypes.RRF, rrf_k=40)
        reranker_config = RerankerConfig(
            type=RerankerTypes.CROSS_ENCODER,
            top_n=3,
        )
        config = RetrieverConfig(
            fetchers=[fetcher_config],
            fusion=fusion_config,
            reranker=reranker_config,
            top_n=3,
        )

        retriever = RetrieverFactory.create_retriever(
            config,
            rag_runtime_with_reranker,
        )

        mock_create_fetcher.assert_called_once_with(
            fetcher_config, rag_runtime_with_reranker
        )
        mock_create_fusion.assert_called_once_with(fusion_config)
        mock_create_reranker.assert_called_once_with(
            reranker_config, rag_runtime_with_reranker.rerank_model
        )
        assert isinstance(retriever, Retriever)
        assert retriever.fetchers == [fetcher]
        assert retriever.fusion is fusion
        assert retriever.reranker is reranker
        assert retriever.top_n == 3

    def test_create_retriever_without_optional_components(self, rag_runtime):
        config = RetrieverConfig(
            fetchers=[
                FetcherConfig(
                    category=FetcherCategories.DENSE,
                    type=FetcherTypes.SIMILARITY,
                )
            ]
        )

        with patch(
            "backend.rag.Retriever.FetcherFactory.create_fetcher"
        ) as mock_create_fetcher:
            mock_create_fetcher.return_value = MagicMock()
            retriever = RetrieverFactory.create_retriever(config, rag_runtime)

        assert retriever.fusion is None
        assert retriever.reranker is None
        assert retriever.top_n is None

    def test_create_retriever_requires_model_when_reranker_configured(
        self, rag_runtime
    ):
        config = RetrieverConfig(
            fetchers=[
                FetcherConfig(
                    category=FetcherCategories.DENSE,
                    type=FetcherTypes.SIMILARITY,
                )
            ],
            reranker=RerankerConfig(type=RerankerTypes.CROSS_ENCODER),
        )

        with patch(
            "backend.rag.Retriever.FetcherFactory.create_fetcher",
            return_value=MagicMock(),
        ):
            with pytest.raises(ValueError, match="runtime.rerank_model is required"):
                RetrieverFactory.create_retriever(config, rag_runtime)

    def test_config_rejects_multiple_fetchers_without_fusion(self):
        with pytest.raises(ValueError, match="Multiple fetchers require a fusion"):
            RetrieverConfig(
                fetchers=[
                    FetcherConfig(
                        category=FetcherCategories.DENSE,
                        type=FetcherTypes.SIMILARITY,
                    ),
                    FetcherConfig(
                        category=FetcherCategories.DENSE,
                        type=FetcherTypes.MMR,
                    ),
                ]
            )
