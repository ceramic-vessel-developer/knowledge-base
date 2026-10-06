from enum import Enum

from backend.common.BaseConfig import BaseConfig
from backend.common.RetrieverConfigs import RetrieverConfig


class PromptType(Enum):
    BASIC = 1


class GenModelType(Enum):
    GEMINI_3_5_FLASH_LITE = 1


class GeneratorConfig(BaseConfig):
    gen_model_type: GenModelType
    prompt_type: PromptType


class RAGPipelineConfig(BaseConfig):
    retriever_config: RetrieverConfig
    generator_config: GeneratorConfig
