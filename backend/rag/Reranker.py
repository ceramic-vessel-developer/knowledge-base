from abc import ABC, abstractmethod
from typing import List, Protocol, Sequence

from langchain_core.documents import Document

from backend.common.RetrieverConfigs import RerankerConfig, RerankerTypes

DEFAULT_BGE_RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"


class RerankModel(Protocol):

    def predict(self, sentences: Sequence[List[str]]) -> Sequence[float]: ...


class Reranker(ABC):
    @abstractmethod
    def rerank(
        self, query: str, documents: List[Document], top_n: int | None = None
    ) -> List[Document]:
        pass


class CrossEncoderReranker(Reranker):
    model: RerankModel
    top_n: int

    def __init__(self, model: RerankModel, top_n: int = 5):
        self.model = model
        self.top_n = top_n

    def rerank(
        self, query: str, documents: List[Document], top_n: int | None = None
    ) -> List[Document]:
        if not documents:
            return []

        limit = self.top_n if top_n is None else top_n
        pairs = [[query, document.page_content] for document in documents]
        scores = self.model.predict(pairs)
        if isinstance(scores, (int, float)):
            scores = [float(scores)]

        ranked = sorted(
            zip(documents, scores),
            key=lambda item: item[1],
            reverse=True,
        )
        return [document for document, _ in ranked[:limit]]


class RerankerFactory:
    _RERANKER_CLASSES = {
        RerankerTypes.CROSS_ENCODER: CrossEncoderReranker,
    }

    @staticmethod
    def create_reranker(config: RerankerConfig, model: RerankModel) -> Reranker:
        reranker_cls = RerankerFactory._RERANKER_CLASSES[config.type]
        if config.type == RerankerTypes.CROSS_ENCODER:
            return reranker_cls(model=model, top_n=config.top_n)
        raise NotImplementedError(f"Unsupported reranker type: {config.type}")
