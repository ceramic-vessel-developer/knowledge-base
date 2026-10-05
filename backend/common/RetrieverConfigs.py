from enum import Enum

from pydantic import BaseModel, ConfigDict


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


class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)


class FetcherConfig(BaseConfig):
    category: FetcherCategories
    type: FetcherTypes
    k: int = 10


class FusionConfig(BaseConfig):
    type: FusionTypes = FusionTypes.RRF
    rrf_k: int = 60


class RerankerConfig(BaseConfig):
    type: RerankerTypes
    top_n: int = 5


class RetrieverConfig(BaseConfig):
    fetchers: list[FetcherConfig]
    fusion: FusionConfig | None = None
    reranker: RerankerConfig | None = None
    top_n: int | None = None
