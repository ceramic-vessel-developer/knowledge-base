from typing import List

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from backend.common.RetrieverConfigs import RetrieverConfig
from backend.rag.Fetcher import Fetcher, FetcherFactory
from backend.rag.Fusion import Fusion, FusionFactory
from backend.rag.Reranker import RerankModel, Reranker, RerankerFactory


class Retriever:
    fetchers: List[Fetcher]
    fusion: Fusion | None
    reranker: Reranker | None
    top_n: int | None

    def __init__(
        self,
        fetchers: List[Fetcher],
        fusion: Fusion | None = None,
        reranker: Reranker | None = None,
        top_n: int | None = None,
    ):
        self.fetchers = fetchers
        self.fusion = fusion
        self.reranker = reranker
        self.top_n = top_n

    def retrieve(self, query: str) -> List[Document]:
        if not self.fetchers:
            return []

        ranked_lists = [
            fetcher.fetch_candidates(query) for fetcher in self.fetchers
        ]

        if self.fusion is not None:
            documents = self.fusion.fuse(ranked_lists)
        elif len(ranked_lists) == 1:
            documents = ranked_lists[0]
        else:
            raise ValueError("Multiple fetchers require a fusion strategy")

        if self.reranker is not None:
            return self.reranker.rerank(query, documents, top_n=self.top_n)

        if self.top_n is not None:
            return documents[: self.top_n]

        return documents


class RetrieverFactory:
    def create_retriever(
        self,
        config: RetrieverConfig,
        vector_store: VectorStore,
        document_ids: List[str],
        rerank_model: RerankModel | None = None,
    ) -> Retriever:
        fetchers = [
            FetcherFactory.create_fetcher(
                fetcher_config, vector_store, document_ids
            )
            for fetcher_config in config.fetchers
        ]

        fusion = None
        if config.fusion is not None:
            fusion = FusionFactory.create_fusion(config.fusion)

        reranker = None
        if config.reranker is not None:
            if rerank_model is None:
                raise ValueError(
                    "rerank_model is required when reranker config is set"
                )
            reranker = RerankerFactory.create_reranker(
                config.reranker, rerank_model
            )

        return Retriever(
            fetchers=fetchers,
            fusion=fusion,
            reranker=reranker,
            top_n=config.top_n,
        )
