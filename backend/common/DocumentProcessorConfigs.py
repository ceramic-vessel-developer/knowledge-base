from backend.common.BaseConfig import BaseConfig
from backend.common.FileTypes import FileTypes


class DocumentSplitterConfig(BaseConfig):
    chunk_size: int = 4000
    chunk_overlap: int = 200


class DocumentLoaderConfig(BaseConfig):
    filename: str
    filetype: FileTypes


class DocumentProcessorConfig(BaseConfig):
    loader_config: DocumentLoaderConfig
    splitter_config: DocumentSplitterConfig
