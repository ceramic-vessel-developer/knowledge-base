import pytest

from backend.common.GeneratorConfigs import PromptType
from backend.rag.promptTemplates import PromptFactory, PromptWrapper, _PROMPT_BASIC


class TestPromptWrapper:
    def test_format_prompt_inserts_context_and_question(self):
        wrapper = PromptWrapper("Q:{question}\nC:{context}")

        result = wrapper.format_prompt("What is RAG?", "Retrieval context")

        assert result == "Q:What is RAG?\nC:Retrieval context"

    def test_format_prompt_raises_on_unknown_placeholder(self):
        wrapper = PromptWrapper("{context} {question} {extra}")

        with pytest.raises(KeyError):
            wrapper.format_prompt("q", "c")


class TestPromptFactory:
    def test_creates_basic_prompt(self):
        wrapper = PromptFactory.create_prompt(PromptType.BASIC)

        assert isinstance(wrapper, PromptWrapper)
        assert wrapper.prompt == _PROMPT_BASIC

    def test_basic_prompt_formats_expected_sections(self):
        wrapper = PromptFactory.create_prompt(PromptType.BASIC)

        result = wrapper.format_prompt(
            question="How does chunking work?",
            context="Chunks overlap to preserve meaning.",
        )

        assert "Chunks overlap to preserve meaning." in result
        assert "How does chunking work?" in result
        assert "Context:" in result
        assert "Question:" in result

    def test_unknown_type_raises_key_error(self):
        with pytest.raises(KeyError):
            PromptFactory.create_prompt("not-a-prompt")
