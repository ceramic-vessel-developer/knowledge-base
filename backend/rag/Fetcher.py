from abc import ABC, abstractmethod
from typing import List

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from backend.common.RetrieverConfigs import (
    FetcherConfig,
    FetcherTypes,
    FetcherCategories,
)


class Fetcher(ABC):
    @abstractmethod
    def fetch_candidates(self, query: str) -> List[Document]:
        pass


def _document_id_filter(document_ids: List[str]) -> dict:
    return {"document_id": {"$in": document_ids}}


class SimilarityFetcher(Fetcher):
    vector_store: VectorStore
    k: int
    document_ids: List[str]

    def __init__(self, vector: VectorStore, k: int, document_ids: List[str]):
        self.vector_store = vector
        self.k = k
        self.document_ids = document_ids

    def fetch_candidates(self, query: str) -> List[Document]:
        if not self.document_ids:
            return []

        return self.vector_store.similarity_search(
            query,
            k=self.k,
            filter=_document_id_filter(self.document_ids),
        )


class MMRFetcher(Fetcher):
    vector_store: VectorStore
    k: int
    document_ids: List[str]

    def __init__(self, vector: VectorStore, k: int, document_ids: List[str]):
        self.vector_store = vector
        self.k = k
        self.document_ids = document_ids

    def fetch_candidates(self, query: str) -> List[Document]:
        if not self.document_ids:
            return []

        # TODO: pass fetch_k and lambda_mult from FetcherConfig when tuning MMR.
        return self.vector_store.max_marginal_relevance_search(
            query,
            k=self.k,
            filter=_document_id_filter(self.document_ids),
        )


class PGLexicalFetcher(Fetcher):
    k: int
    document_ids: List[str]

    def __init__(self, k: int, document_ids: List[str]):
        self.k = k
        self.document_ids = document_ids

    def fetch_candidates(self, query: str) -> List[Document]:
        if not self.document_ids:
            return []

        raise NotImplementedError


class FetcherFactory:
    _DENSE_VECTOR_FETCHER_CLASSES = {
        FetcherTypes.SIMILARITY: SimilarityFetcher,
        FetcherTypes.MMR: MMRFetcher,
    }

    _SPARSE_VECTOR_FETCHER_CLASSES = {FetcherTypes.LEXICAL: PGLexicalFetcher}

    @staticmethod
    def create_fetcher(
        config: FetcherConfig,
        vector_store: VectorStore,
        document_ids: List[str],
    ) -> Fetcher:
        if config.category == FetcherCategories.SPARSE:
            fetcher_cls = FetcherFactory._SPARSE_VECTOR_FETCHER_CLASSES[config.type]
            return fetcher_cls(config.k, document_ids)
        elif config.category == FetcherCategories.DENSE:
            fetcher_cls = FetcherFactory._DENSE_VECTOR_FETCHER_CLASSES[config.type]
            return fetcher_cls(vector_store, config.k, document_ids)
        else:
            raise NotImplementedError
