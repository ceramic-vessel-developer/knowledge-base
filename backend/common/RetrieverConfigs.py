from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)


class FetcherConfig(BaseModel):
    pass


class FusionConfig(BaseModel):
    pass


class RerankerConfig(BaseModel):
    pass


class RetrieverConfig(BaseConfig):
    fetchers: list[FetcherConfig]
    fusion: FusionConfig | None = None
    reranker: RerankerConfig | None = None
    k: int = 10
    top_n: int | None = None
