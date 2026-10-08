from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from backend.common.GeneratorConfigs import (
    GenModelType,
    GeneratorConfig,
    PromptType,
)
from backend.rag.Generator import Generator, GeneratorFactory


class TestGenerator:
    def test_format_docs_numbers_chunks(self):
        chunks = [
            Document(page_content="chunk one"),
            Document(page_content="chunk two"),
        ]
        generator = Generator(model=MagicMock(), prompt=MagicMock())

        assert generator._format_docs(chunks) == "[1]\nchunk one\n\n[2]\nchunk two"

    def test_format_docs_empty_chunks(self):
        generator = Generator(model=MagicMock(), prompt=MagicMock())

        assert generator._format_docs([]) == ""

    def test_invoke_formats_prompt_and_calls_model(self):
        model = MagicMock()
        prompt = MagicMock()
        chunks = [Document(page_content="context text")]
        prompt.format_prompt.return_value = "full prompt"
        model.generate_response.return_value = "model answer"

        generator = Generator(model=model, prompt=prompt)
        result = generator.invoke("What is RAG?", chunks)

        prompt.format_prompt.assert_called_once_with(
            "What is RAG?", "[1]\ncontext text"
        )
        model.generate_response.assert_called_once_with("full prompt")
        assert result == "model answer"


class TestGeneratorFactory:
    @patch("backend.rag.Generator.PromptFactory.create_prompt")
    @patch("backend.rag.Generator.GenerativeModelFactory.create_generative_model")
    def test_create_generator_wires_dependencies(
        self, mock_create_model, mock_create_prompt
    ):
        model = MagicMock()
        prompt = MagicMock()
        mock_create_model.return_value = model
        mock_create_prompt.return_value = prompt

        config = GeneratorConfig(
            gen_model_type=GenModelType.GEMINI_3_5_FLASH_LITE,
            prompt_type=PromptType.BASIC,
        )

        generator = GeneratorFactory.create_generator(config)

        mock_create_model.assert_called_once_with(GenModelType.GEMINI_3_5_FLASH_LITE)
        mock_create_prompt.assert_called_once_with(PromptType.BASIC)
        assert isinstance(generator, Generator)
        assert generator.model is model
        assert generator.prompt is prompt
