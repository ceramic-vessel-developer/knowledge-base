from enum import Enum

from pydantic import BaseModel, ConfigDict


class FetcherCategories(Enum):
    DENSE = 1
    SPARSE = 2


class FetcherTypes(Enum):
    SIMILARITY = 1
    MMR = 2
    LEXICAL = 3


class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)


class FetcherConfig(BaseModel):
    category: FetcherCategories
    type: FetcherTypes
    k: int = 10


class FusionConfig(BaseModel):
    pass


class RerankerConfig(BaseModel):
    pass


class RetrieverConfig(BaseConfig):
    fetchers: list[FetcherConfig]
    fusion: FusionConfig | None = None
    reranker: RerankerConfig | None = None
    top_n: int | None = None
    query: str
