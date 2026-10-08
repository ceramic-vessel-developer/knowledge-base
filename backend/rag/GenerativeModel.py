from abc import ABC, abstractmethod
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from backend.common.GeneratorConfigs import GenModelType


class GenerativeModel(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass


class Gemini35FlashLiteGenerativeModel(GenerativeModel):
    def __init__(self):
        self.engine = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

    def _content_to_text(self, content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, str):
                    parts.append(block)
                elif isinstance(block, dict):
                    parts.append(str(block.get("text", "")))
                else:
                    parts.append(str(getattr(block, "text", block)))
            return "".join(parts)
        return str(content)

    def generate_response(self, prompt: str) -> str:
        response = self.engine.invoke(prompt)
        return self._content_to_text(response.content)


class GenerativeModelFactory:
    _GENERATIVE_MODEL_MAP = {
        GenModelType.GEMINI_3_5_FLASH_LITE: Gemini35FlashLiteGenerativeModel
    }

    @staticmethod
    def create_generative_model(model_type: GenModelType):
        return GenerativeModelFactory._GENERATIVE_MODEL_MAP[model_type]()
