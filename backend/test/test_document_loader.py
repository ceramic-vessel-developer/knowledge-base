from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from backend.common.DocumentProcessorConfigs import DocumentLoaderConfig
from backend.common.FileTypes import FileTypes
from backend.rag.DocumentLoader import (
    DoclingDocumentLoader,
    DocumentLoaderFactory,
    UnstructuredDocumentLoader,
)


class TestUnstructuredDocumentLoader:
    @patch("backend.rag.DocumentLoader.UnstructuredLoader")
    def test_init_creates_engine_with_filename(self, mock_loader_cls):
        UnstructuredDocumentLoader("notes.txt")

        mock_loader_cls.assert_called_once_with("notes.txt")

    @patch("backend.rag.DocumentLoader.UnstructuredLoader")
    def test_load_delegates_to_engine(self, mock_loader_cls):
        expected = [Document(page_content="hello")]
        mock_loader_cls.return_value.load.return_value = expected

        loader = UnstructuredDocumentLoader("notes.txt")
        result = loader.load()

        assert result == expected
        mock_loader_cls.return_value.load.assert_called_once_with()


class TestDoclingDocumentLoader:
    @patch("backend.rag.DocumentLoader.DoclingLoader")
    def test_init_creates_engine_with_filename(self, mock_loader_cls):
        DoclingDocumentLoader("paper.pdf")

        mock_loader_cls.assert_called_once_with("paper.pdf")

    @patch("backend.rag.DocumentLoader.DoclingLoader")
    def test_load_delegates_to_engine(self, mock_loader_cls):
        expected = [Document(page_content="pdf text")]
        mock_loader_cls.return_value.load.return_value = expected

        loader = DoclingDocumentLoader("paper.pdf")
        result = loader.load()

        assert result == expected
        mock_loader_cls.return_value.load.assert_called_once_with()


class TestDocumentLoaderFactory:
    @patch("backend.rag.DocumentLoader.DoclingDocumentLoader")
    def test_pdf_returns_docling_loader(self, mock_docling):
        mock_docling.return_value = MagicMock()
        config = DocumentLoaderConfig(filename="a.pdf", filetype=FileTypes.PDF)

        loader = DocumentLoaderFactory.get_loader(config)

        mock_docling.assert_called_once_with("a.pdf")
        assert loader is mock_docling.return_value

    @patch("backend.rag.DocumentLoader.UnstructuredDocumentLoader")
    def test_txt_returns_unstructured_loader(self, mock_unstructured):
        mock_unstructured.return_value = MagicMock()
        config = DocumentLoaderConfig(filename="a.txt", filetype=FileTypes.TXT)

        loader = DocumentLoaderFactory.get_loader(config)

        mock_unstructured.assert_called_once_with("a.txt")
        assert loader is mock_unstructured.return_value

    @patch("backend.rag.DocumentLoader.UnstructuredDocumentLoader")
    def test_other_returns_unstructured_loader(self, mock_unstructured):
        mock_unstructured.return_value = MagicMock()
        config = DocumentLoaderConfig(filename="a.md", filetype=FileTypes.OTHER)

        loader = DocumentLoaderFactory.get_loader(config)

        mock_unstructured.assert_called_once_with("a.md")
        assert loader is mock_unstructured.return_value

    def test_invalid_filetype_raises_value_error(self):
        config = MagicMock()
        config.filetype = "not-a-filetype"
        config.filename = "x.bin"

        with pytest.raises(ValueError, match="Incorrect filetype"):
            DocumentLoaderFactory.get_loader(config)
