from typing import List, Protocol, Sequence


class RerankModel(Protocol):
    """sentence_transformers.CrossEncoder-compatible interface."""

    def predict(self, sentences: Sequence[List[str]]) -> Sequence[float]: ...
