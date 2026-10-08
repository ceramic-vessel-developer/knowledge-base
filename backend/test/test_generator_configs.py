import pytest
from pydantic import ValidationError

from backend.common.GeneratorConfigs import (
    GenModelType,
    GeneratorConfig,
    PromptType,
    RAGPipelineConfig,
)
from backend.common.RetrieverConfigs import (
    FetcherCategories,
    FetcherConfig,
    FetcherTypes,
    RetrieverConfig,
)


class TestPromptType:
    def test_basic_member(self):
        assert PromptType.BASIC.value == 1


class TestGenModelType:
    def test_gemini_member(self):
        assert GenModelType.GEMINI_3_5_FLASH_LITE.value == 1


class TestGeneratorConfig:
    def test_creates_with_required_fields(self):
        config = GeneratorConfig(
            gen_model_type=GenModelType.GEMINI_3_5_FLASH_LITE,
            prompt_type=PromptType.BASIC,
        )

        assert config.prompt_type == PromptType.BASIC
        assert config.gen_model_type == GenModelType.GEMINI_3_5_FLASH_LITE

    def test_is_frozen(self):
        config = GeneratorConfig(
            gen_model_type=GenModelType.GEMINI_3_5_FLASH_LITE,
            prompt_type=PromptType.BASIC,
        )

        with pytest.raises(ValidationError):
            config.prompt_type = PromptType.BASIC

    def test_missing_fields_raise(self):
        with pytest.raises(ValidationError):
            GeneratorConfig()


class TestRAGPipelineConfig:
    def test_nests_retriever_and_generator_configs(self):
        config = RAGPipelineConfig(
            retriever_config=RetrieverConfig(
                fetchers=[
                    FetcherConfig(
                        category=FetcherCategories.DENSE,
                        type=FetcherTypes.SIMILARITY,
                    )
                ]
            ),
            generator_config=GeneratorConfig(
                gen_model_type=GenModelType.GEMINI_3_5_FLASH_LITE,
                prompt_type=PromptType.BASIC,
            ),
        )

        assert config.generator_config.prompt_type == PromptType.BASIC
        assert len(config.retriever_config.fetchers) == 1
