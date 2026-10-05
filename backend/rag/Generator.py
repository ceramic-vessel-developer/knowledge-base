from typing import List

from langchain_core.documents import Document

from backend.common.GeneratorConfigs import GeneratorConfig
from backend.rag.GenerativeModel import GenerativeModel, GenerativeModelFactory
from backend.rag.promptTemplates import PromptFactory, PromptWrapper


class Generator:
    model: GenerativeModel
    prompt: PromptWrapper
    chunks: List[Document]

    def __init__(
        self,
        model: GenerativeModel,
        prompt: PromptWrapper,
        relevant_chunks: List[Document],
    ):
        self.model = model
        self.prompt = prompt
        self.chunks = relevant_chunks

    def _format_docs(self) -> str:
        return "\n\n".join(document.page_content for document in self.chunks)

    def invoke(self, question: str) -> str:
        context = self._format_docs()
        formatted_prompt = self.prompt.format_prompt(question, context)
        response = self.model.generate_response(formatted_prompt)
        return response


class GeneratorFactory:
    def create_generator(self, config: GeneratorConfig):
        model = GenerativeModelFactory.create_generative_model(config.gen_model_type)
        prompt = PromptFactory.create_prompt(config.prompt_type)
        return Generator(model, prompt, config.relevant_chunks)
