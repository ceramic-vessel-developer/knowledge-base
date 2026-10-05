from enum import Enum

from pydantic import BaseModel, ConfigDict

from backend.common.RetrieverConfigs import RetrieverConfig


class PromptType(Enum):
    BASIC = 1


class GenModelType(Enum):
    GEMINI_3_5_FLASH_LITE = 1


class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)


class GeneratorConfig(BaseConfig):
    gen_model_type: GenModelType
    prompt_type: PromptType
