import pytest
from langchain_core.documents import Document
from pydantic import ValidationError

from backend.common.GeneratorConfigs import (
    GenModelType,
    GeneratorConfig,
    PromptType,
)


class TestPromptType:
    def test_basic_member(self):
        assert PromptType.BASIC.value == 1


class TestGenModelType:
    def test_gemini_member(self):
        assert GenModelType.GEMINI_3_5_FLASH_LITE.value == 1


class TestGeneratorConfig:
    def test_accepts_documents(self):
        chunks = [Document(page_content="chunk")]
        config = GeneratorConfig(
            gen_model_type=GenModelType.GEMINI_3_5_FLASH_LITE,
            prompt_type=PromptType.BASIC,
            relevant_chunks=chunks,
        )

        assert config.prompt_type == PromptType.BASIC
        assert config.relevant_chunks == chunks

    def test_is_frozen(self):
        config = GeneratorConfig(
            gen_model_type=GenModelType.GEMINI_3_5_FLASH_LITE,
            prompt_type=PromptType.BASIC,
            relevant_chunks=[],
        )

        with pytest.raises(ValidationError):
            config.prompt_type = PromptType.BASIC

    def test_missing_fields_raise(self):
        with pytest.raises(ValidationError):
            GeneratorConfig()
