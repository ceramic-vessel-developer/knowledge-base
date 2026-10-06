from hashlib import sha256
from abc import ABC, abstractmethod
from typing import List

from langchain_core.documents import Document

from backend.common.RetrieverConfigs import FusionConfig, FusionTypes


def document_key(document: Document) -> str:
    if document.id is not None:
        return str(document.id)

    metadata = document.metadata or {}
    document_id = metadata.get("document_id")
    chunk_index = metadata.get("chunk_index")
    if document_id is not None and chunk_index is not None:
        return f"{document_id}:{chunk_index}"

    return sha256(document.page_content.encode("utf-8")).hexdigest()


class Fusion(ABC):
    @abstractmethod
    def fuse(self, ranked_lists: List[List[Document]]) -> List[Document]:
        pass


class RRFFusion(Fusion):
    rrf_k: int

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def fuse(self, ranked_lists: List[List[Document]]) -> List[Document]:
        if not ranked_lists:
            return []

        scores: dict[str, float] = {}
        documents_by_key: dict[str, Document] = {}

        for ranked_list in ranked_lists:
            for rank, document in enumerate(ranked_list):
                key = document_key(document)
                scores[key] = scores.get(key, 0.0) + 1.0 / (self.rrf_k + rank + 1)
                documents_by_key.setdefault(key, document)

        ordered_keys = sorted(scores, key=scores.get, reverse=True)
        return [documents_by_key[key] for key in ordered_keys]


class FusionFactory:
    _FUSION_CLASSES = {
        FusionTypes.RRF: RRFFusion,
    }

    @staticmethod
    def create_fusion(config: FusionConfig) -> Fusion:
        fusion_cls = FusionFactory._FUSION_CLASSES[config.type]
        if config.type == FusionTypes.RRF:
            return fusion_cls(rrf_k=config.rrf_k)
        raise NotImplementedError(f"Unsupported fusion type: {config.type}")
