from abc import ABC, abstractmethod
from typing import Any, List

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from backend.common.RagRuntime import RagRuntime
from backend.common.RetrieverConfigs import (
    FetcherCategories,
    FetcherConfig,
    FetcherTypes,
)


class Fetcher(ABC):
    @abstractmethod
    def fetch_candidates(self, query: str, document_ids: List[str]) -> List[Document]:
        pass


def _document_id_filter(document_ids: List[str]) -> dict:
    return {"document_id": {"$in": document_ids}}


class SimilarityFetcher(Fetcher):
    vector_store: VectorStore
    k: int

    def __init__(self, vector: VectorStore, k: int):
        self.vector_store = vector
        self.k = k

    def fetch_candidates(self, query: str, document_ids: List[str]) -> List[Document]:
        if not document_ids:
            return []

        return self.vector_store.similarity_search(
            query,
            k=self.k,
            filter=_document_id_filter(document_ids),
        )


class MMRFetcher(Fetcher):
    vector_store: VectorStore
    k: int

    def __init__(self, vector: VectorStore, k: int):
        self.vector_store = vector
        self.k = k

    def fetch_candidates(self, query: str, document_ids: List[str]) -> List[Document]:
        if not document_ids:
            return []

        # TODO: pass fetch_k and lambda_mult from FetcherConfig when tuning MMR.
        return self.vector_store.max_marginal_relevance_search(
            query,
            k=self.k,
            filter=_document_id_filter(document_ids),
        )


class PGLexicalFetcher(Fetcher):
    k: int
    db_session: Any

    def __init__(self, k: int, db_session: Any):
        self.k = k
        self.db_session = db_session

    def fetch_candidates(self, query: str, document_ids: List[str]) -> List[Document]:
        if not document_ids:
            return []

        # TODO: run Postgres FTS / BM25 via self.db_session.
        raise NotImplementedError


class FetcherFactory:
    _DENSE_VECTOR_FETCHER_CLASSES = {
        FetcherTypes.SIMILARITY: SimilarityFetcher,
        FetcherTypes.MMR: MMRFetcher,
    }

    _SPARSE_VECTOR_FETCHER_CLASSES = {FetcherTypes.LEXICAL: PGLexicalFetcher}

    @staticmethod
    def create_fetcher(config: FetcherConfig, runtime: RagRuntime) -> Fetcher:
        if config.category == FetcherCategories.SPARSE:
            if runtime.db_session is None:
                raise ValueError(
                    "runtime.db_session is required for sparse/lexical fetchers"
                )
            fetcher_cls = FetcherFactory._SPARSE_VECTOR_FETCHER_CLASSES[config.type]
            return fetcher_cls(config.k, runtime.db_session)
        if config.category == FetcherCategories.DENSE:
            fetcher_cls = FetcherFactory._DENSE_VECTOR_FETCHER_CLASSES[config.type]
            return fetcher_cls(runtime.vector_store, config.k)
        raise NotImplementedError
