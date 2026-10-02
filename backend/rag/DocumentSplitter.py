from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from abc import ABC, abstractmethod
from ..common.configs import DocumentSplitterConfig


class DocumentSplitter(ABC):

    @abstractmethod
    def split(self, documents: List[Document]) -> List[Document]:
        pass


class RecursiveCharacterDocumentSplitter(DocumentSplitter):

    def __init__(self, config: DocumentSplitterConfig):
        self.engine = RecursiveCharacterTextSplitter(**config.model_dump())

    def split(self, documents: List[Document]) -> List[Document]:
        return self.engine.split_documents(documents)


class DocumentSplitterFactory:

    # TODO implement getting splitters based on filetype
    @staticmethod
    def get_splitter(config: DocumentSplitterConfig) -> DocumentSplitter:
        return RecursiveCharacterDocumentSplitter(config)


if __name__ == "__main__":
    config = DocumentSplitterConfig(chunk_size=200, chunk_overlap=40)
    print(DocumentSplitterFactory.get_splitter(config))
