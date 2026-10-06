from uuid import UUID

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from backend.common.DocumentProcessorConfigs import DocumentProcessorConfig
from backend.rag.DocumentLoader import DocumentLoader, DocumentLoaderFactory
from backend.rag.DocumentSplitter import DocumentSplitter, DocumentSplitterFactory


class DocumentProcessor:
    loader: DocumentLoader
    splitter: DocumentSplitter
    vector_store: VectorStore

    def __init__(self, loader, splitter, vector_store):
        self.loader = loader
        self.splitter = splitter
        self.vector_store = vector_store

    def process(self, document_id: UUID):
        document = self.loader.load()
        chunks = self.splitter.split(document)
        chunk_documents = []

        for index, chunk in enumerate(chunks):
            chunk_documents.append(
                Document(
                    page_content=chunk.page_content,
                    metadata={
                        "document_id": str(document_id),
                        "chunk_index": index,
                    },
                )
            )
        self.vector_store.add_documents(chunk_documents)


class DocumentProcessorFactory:
    @staticmethod
    def create_processor(
        config: DocumentProcessorConfig, vector_store: VectorStore
    ) -> DocumentProcessor:
        loader = DocumentLoaderFactory.create_loader(config.loader_config)
        splitter = DocumentSplitterFactory.create_splitter(config.splitter_config)
        return DocumentProcessor(loader, splitter, vector_store)
