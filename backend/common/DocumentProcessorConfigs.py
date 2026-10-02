from langchain_core.vectorstores import VectorStore
from pydantic import BaseModel, ConfigDict

from backend.common.FileTypes import FileTypes


class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class DocumentSplitterConfig(BaseConfig):
    chunk_size: int = 4000
    chunk_overlap: int = 200


class DocumentLoaderConfig(BaseConfig):
    filename: str
    filetype: FileTypes


class DocumentProcessorConfig(BaseConfig):
    loader_config: DocumentLoaderConfig
    splitter_config: DocumentSplitterConfig
    vector_store: VectorStore
