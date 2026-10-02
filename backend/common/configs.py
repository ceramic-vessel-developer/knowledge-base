from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)


class DocumentSplitterConfig(BaseConfig):
    chunk_size: int = 4000
    chunk_overlap: int = 200
