from unittest.mock import MagicMock, patch

import pytest

from backend.common.GeneratorConfigs import GenModelType
from backend.rag.GenerativeModel import (
    Gemini35FlashLiteGenerativeModel,
    GenerativeModelFactory,
)


class TestGemini35FlashLiteGenerativeModel:
    @patch("backend.rag.GenerativeModel.ChatGoogleGenerativeAI")
    def test_init_creates_engine_with_model_name(self, mock_chat_cls):
        Gemini35FlashLiteGenerativeModel()

        mock_chat_cls.assert_called_once_with(model="gemini-3.5-flash-lite")

    @patch("backend.rag.GenerativeModel.ChatGoogleGenerativeAI")
    def test_generate_response_returns_content(self, mock_chat_cls):
        mock_engine = MagicMock()
        mock_engine.invoke.return_value = MagicMock(content="answer text")
        mock_chat_cls.return_value = mock_engine

        model = Gemini35FlashLiteGenerativeModel()
        result = model.generate_response("formatted prompt")

        assert result == "answer text"
        mock_engine.invoke.assert_called_once_with("formatted prompt")


class TestGenerativeModelFactory:
    @patch("backend.rag.GenerativeModel.ChatGoogleGenerativeAI")
    def test_creates_gemini_model(self, mock_chat_cls):
        mock_chat_cls.return_value = MagicMock()

        model = GenerativeModelFactory.create_generative_model(
            GenModelType.GEMINI_3_5_FLASH_LITE
        )

        assert isinstance(model, Gemini35FlashLiteGenerativeModel)
        mock_chat_cls.assert_called_once_with(model="gemini-3.5-flash-lite")

    def test_unknown_type_raises_key_error(self):
        with pytest.raises(KeyError):
            GenerativeModelFactory.create_generative_model("not-a-model")
