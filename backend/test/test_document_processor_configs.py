import pytest
from pydantic import ValidationError

from backend.common.DocumentProcessorConfigs import (
    DocumentLoaderConfig,
    DocumentProcessorConfig,
    DocumentSplitterConfig,
)
from backend.common.FileTypes import FileTypes


class TestDocumentSplitterConfig:
    def test_defaults(self):
        config = DocumentSplitterConfig()

        assert config.chunk_size == 4000
        assert config.chunk_overlap == 200

    def test_custom_values(self):
        config = DocumentSplitterConfig(chunk_size=500, chunk_overlap=50)

        assert config.chunk_size == 500
        assert config.chunk_overlap == 50

    def test_is_frozen(self):
        config = DocumentSplitterConfig()

        with pytest.raises(ValidationError):
            config.chunk_size = 10


class TestDocumentLoaderConfig:
    def test_requires_filename_and_filetype(self):
        config = DocumentLoaderConfig(filename="a.txt", filetype=FileTypes.TXT)

        assert config.filename == "a.txt"
        assert config.filetype == FileTypes.TXT

    def test_missing_fields_raise(self):
        with pytest.raises(ValidationError):
            DocumentLoaderConfig()


class TestDocumentProcessorConfig:
    def test_nested_loader_and_splitter_configs(self):
        config = DocumentProcessorConfig(
            loader_config=DocumentLoaderConfig(
                filename="a.pdf", filetype=FileTypes.PDF
            ),
            splitter_config=DocumentSplitterConfig(),
        )

        assert config.loader_config.filetype == FileTypes.PDF
        assert config.splitter_config.chunk_size == 4000

    def test_is_frozen(self):
        config = DocumentProcessorConfig(
            loader_config=DocumentLoaderConfig(
                filename="a.txt", filetype=FileTypes.TXT
            ),
            splitter_config=DocumentSplitterConfig(),
        )

        with pytest.raises(ValidationError):
            config.splitter_config = DocumentSplitterConfig(chunk_size=1)
