from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from backend.common.DocumentProcessorConfigs import (
    DocumentLoaderConfig,
    DocumentProcessorConfig,
    DocumentSplitterConfig,
)
from backend.common.FileTypes import FileTypes
from backend.rag.DocumentProcessor import DocumentProcessor, DocumentProcessorFactory


class TestDocumentProcessor:
    def test_process_loads_splits_and_stores_with_metadata(
        self, sample_documents, sample_chunks, document_id, mock_vector_store
    ):
        loader = MagicMock()
        splitter = MagicMock()
        loader.load.return_value = sample_documents
        splitter.split.return_value = sample_chunks

        processor = DocumentProcessor(loader, splitter, mock_vector_store)
        processor.process(document_id)

        loader.load.assert_called_once_with()
        splitter.split.assert_called_once_with(sample_documents)
        mock_vector_store.add_documents.assert_called_once()

        stored_docs = mock_vector_store.add_documents.call_args.args[0]
        assert len(stored_docs) == len(sample_chunks)
        for index, (stored, original) in enumerate(zip(stored_docs, sample_chunks)):
            assert stored.page_content == original.page_content
            assert stored.metadata == {
                "document_id": str(document_id),
                "chunk_index": index,
            }

    def test_process_with_no_chunks_stores_empty_list(
        self, sample_documents, document_id, mock_vector_store
    ):
        loader = MagicMock()
        splitter = MagicMock()
        loader.load.return_value = sample_documents
        splitter.split.return_value = []

        processor = DocumentProcessor(loader, splitter, mock_vector_store)
        processor.process(document_id)

        mock_vector_store.add_documents.assert_called_once_with([])


class TestDocumentProcessorFactory:
    @patch("backend.rag.DocumentProcessor.DocumentSplitterFactory.get_splitter")
    @patch("backend.rag.DocumentProcessor.DocumentLoaderFactory.get_loader")
    def test_create_processor_wires_dependencies(
        self, mock_get_loader, mock_get_splitter, vector_store
    ):
        loader = MagicMock()
        splitter = MagicMock()
        mock_get_loader.return_value = loader
        mock_get_splitter.return_value = splitter

        loader_config = DocumentLoaderConfig(
            filename="doc.txt", filetype=FileTypes.TXT
        )
        splitter_config = DocumentSplitterConfig(chunk_size=100, chunk_overlap=20)
        config = DocumentProcessorConfig(
            loader_config=loader_config,
            splitter_config=splitter_config,
            vector_store=vector_store,
        )

        processor = DocumentProcessorFactory().create_processor(config)

        mock_get_loader.assert_called_once_with(loader_config)
        mock_get_splitter.assert_called_once_with(splitter_config)
        assert isinstance(processor, DocumentProcessor)
        assert processor.loader is loader
        assert processor.splitter is splitter
        assert processor.vector_store is vector_store
