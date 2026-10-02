from langchain_core.documents import Document

from backend.common.DocumentProcessorConfigs import DocumentLoaderConfig
from backend.common.FileTypes import FileTypes
from langchain_unstructured import UnstructuredLoader
from langchain_docling.loader import DoclingLoader
from abc import ABC, abstractmethod


class DocumentLoader(ABC):
    @property
    @abstractmethod
    def engine(self):
        pass

    @abstractmethod
    def load(self) -> list[Document]:
        pass


class UnstructuredDocumentLoader(DocumentLoader):
    engine: UnstructuredLoader

    def __init__(self, filename):
        self.engine = UnstructuredLoader(filename)

    def load(self) -> list[Document]:
        return self.engine.load()


class DoclingDocumentLoader(DocumentLoader):
    engine: DoclingLoader

    def __init__(self, filename):
        self.engine = DoclingLoader(filename)

    def load(self) -> list[Document]:
        return self.engine.load()


class DocumentLoaderFactory:

    @staticmethod
    def get_loader(config: DocumentLoaderConfig):
        if config.filetype == FileTypes.PDF:
            return DoclingDocumentLoader(config.filename)
        elif config.filetype == FileTypes.TXT or config.filetype == FileTypes.OTHER:
            return UnstructuredDocumentLoader(config.filename)
        else:
            raise ValueError("Incorrect filetype")


if __name__ == "__main__":
    pass
    # print(DocumentLoaderStrategies.get_loader(FileTypes.TXT))
