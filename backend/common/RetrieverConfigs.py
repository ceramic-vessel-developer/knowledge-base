from enum import Enum

from pydantic import model_validator

from backend.common.BaseConfig import BaseConfig


class FetcherCategories(Enum):
    DENSE = 1
    SPARSE = 2


class FetcherTypes(Enum):
    SIMILARITY = 1
    MMR = 2
    LEXICAL = 3


class FusionTypes(Enum):
    RRF = 1


class RerankerTypes(Enum):
    CROSS_ENCODER = 1


_DENSE_TYPES = {FetcherTypes.SIMILARITY, FetcherTypes.MMR}
_SPARSE_TYPES = {FetcherTypes.LEXICAL}


class FetcherConfig(BaseConfig):
    category: FetcherCategories
    type: FetcherTypes
    k: int = 10

    @model_validator(mode="after")
    def validate_category_type(self) -> "FetcherConfig":
        if self.category == FetcherCategories.DENSE and self.type not in _DENSE_TYPES:
            raise ValueError(
                f"Fetcher type {self.type!r} is not valid for category DENSE"
            )
        if self.category == FetcherCategories.SPARSE and self.type not in _SPARSE_TYPES:
            raise ValueError(
                f"Fetcher type {self.type!r} is not valid for category SPARSE"
            )
        return self


class FusionConfig(BaseConfig):
    type: FusionTypes = FusionTypes.RRF
    rrf_k: int = 60


class RerankerConfig(BaseConfig):
    type: RerankerTypes
    top_n: int = 5


class RetrieverConfig(BaseConfig):
    """top_n truncates results when no reranker is configured.

    When ``reranker`` is set, use ``RerankerConfig.top_n`` instead.
    """

    fetchers: list[FetcherConfig]
    fusion: FusionConfig | None = None
    reranker: RerankerConfig | None = None
    top_n: int | None = None

    @model_validator(mode="after")
    def validate_fusion_for_multiple_fetchers(self) -> "RetrieverConfig":
        if len(self.fetchers) > 1 and self.fusion is None:
            raise ValueError("Multiple fetchers require a fusion strategy")
        return self
