from abc import ABC, abstractmethod

from langchain_google_genai import ChatGoogleGenerativeAI

from backend.common.GeneratorConfigs import GenModelType


class GenerativeModel(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass


class Gemini35FlashLiteGenerativeModel(GenerativeModel):
    def __init__(self):
        self.engine = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

    def generate_response(self, prompt: str) -> str:
        response = self.engine.invoke(prompt)
        return response.content


class GenerativeModelFactory:
    _GENERATIVE_MODEL_MAP = {
        GenModelType.GEMINI_3_5_FLASH_LITE: Gemini35FlashLiteGenerativeModel
    }

    @staticmethod
    def create_generative_model(model_type: GenModelType):
        return GenerativeModelFactory._GENERATIVE_MODEL_MAP[model_type]()
