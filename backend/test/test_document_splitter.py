from backend.common.DocumentProcessorConfigs import DocumentSplitterConfig
from backend.rag.DocumentSplitter import (
    DocumentSplitterFactory,
    RecursiveCharacterDocumentSplitter,
)
from langchain_core.documents import Document


class TestRecursiveCharacterDocumentSplitter:
    def test_split_returns_multiple_chunks(self, sample_documents):
        config = DocumentSplitterConfig(chunk_size=50, chunk_overlap=10)
        splitter = RecursiveCharacterDocumentSplitter(config)

        chunks = splitter.split(sample_documents)

        assert len(chunks) > 1
        assert all(isinstance(chunk, Document) for chunk in chunks)
        assert all(chunk.page_content for chunk in chunks)

    def test_split_preserves_source_metadata(self, sample_documents):
        config = DocumentSplitterConfig(chunk_size=50, chunk_overlap=10)
        splitter = RecursiveCharacterDocumentSplitter(config)

        chunks = splitter.split(sample_documents)

        assert all(chunk.metadata.get("source") == "sample.txt" for chunk in chunks)

    def test_large_chunk_size_keeps_document_together(self, sample_documents):
        config = DocumentSplitterConfig(chunk_size=4000, chunk_overlap=0)
        splitter = RecursiveCharacterDocumentSplitter(config)

        chunks = splitter.split(sample_documents)

        assert len(chunks) == 1
        assert chunks[0].page_content == sample_documents[0].page_content


class TestDocumentSplitterFactory:
    def test_create_splitter_returns_recursive_splitter(self):
        config = DocumentSplitterConfig(chunk_size=200, chunk_overlap=40)

        splitter = DocumentSplitterFactory.create_splitter(config)

        assert isinstance(splitter, RecursiveCharacterDocumentSplitter)
