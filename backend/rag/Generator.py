from typing import List

from langchain_core.documents import Document

from backend.common.GeneratorConfigs import GeneratorConfig
from backend.rag.GenerativeModel import GenerativeModel, GenerativeModelFactory
from backend.rag.promptTemplates import PromptFactory, PromptWrapper


class Generator:
    model: GenerativeModel
    prompt: PromptWrapper

    def __init__(self, model: GenerativeModel, prompt: PromptWrapper):
        self.model = model
        self.prompt = prompt

    def _format_docs(self, chunks: List[Document]) -> str:
        parts: list[str] = []
        for i, document in enumerate(chunks, start=1):
            label = f"[{i}]"
            parts.append(f"{label}\n{document.page_content}")
        return "\n\n".join(parts)

    def invoke(self, question: str, relevant_chunks: List[Document]) -> str:
        context = self._format_docs(relevant_chunks)
        formatted_prompt = self.prompt.format_prompt(question, context)
        response = self.model.generate_response(formatted_prompt)
        return response


class GeneratorFactory:
    @staticmethod
    def create_generator(config: GeneratorConfig) -> Generator:
        model = GenerativeModelFactory.create_generative_model(config.gen_model_type)
        prompt = PromptFactory.create_prompt(config.prompt_type)
        return Generator(model, prompt)
