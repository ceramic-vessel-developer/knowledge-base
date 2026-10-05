from unittest.mock import MagicMock, patch
from uuid import uuid4

from langchain_core.documents import Document

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
from backend.rag.RAGPipeline import RAGPipeline, RAGPipelineFactory


class TestRAGPipeline:
    def test_run_retrieves_then_generates(self):
        chunks = [Document(page_content="context")]
        retriever = MagicMock()
        generator = MagicMock()
        retriever.retrieve.return_value = chunks
        generator.invoke.return_value = "final answer"

        result = RAGPipeline(retriever, generator).run("What is RAG?")

        retriever.retrieve.assert_called_once_with("What is RAG?")
        generator.invoke.assert_called_once_with("What is RAG?", chunks)
        assert result == "final answer"


class TestRAGPipelineFactory:
    @patch("backend.rag.RAGPipeline.GeneratorFactory.create_generator")
    @patch("backend.rag.RAGPipeline.RetrieverFactory.create_retriever")
    def test_create_pipeline_wires_dependencies(
        self,
        mock_create_retriever,
        mock_create_generator,
        vector_store,
    ):
        retriever = MagicMock()
        generator = MagicMock()
        rerank_model = MagicMock()
        mock_create_retriever.return_value = retriever
        mock_create_generator.return_value = generator

        retriever_config = RetrieverConfig(
            fetchers=[
                FetcherConfig(
                    category=FetcherCategories.DENSE,
                    type=FetcherTypes.SIMILARITY,
                )
            ]
        )
        generator_config = GeneratorConfig(
            gen_model_type=GenModelType.GEMINI_3_5_FLASH_LITE,
            prompt_type=PromptType.BASIC,
        )
        config = RAGPipelineConfig(
            retriever_config=retriever_config,
            generator_config=generator_config,
        )
        document_ids = [str(uuid4())]

        pipeline = RAGPipelineFactory().create_pipeline(
            config,
            vector_store,
            document_ids,
            rerank_model=rerank_model,
        )

        mock_create_retriever.assert_called_once_with(
            retriever_config,
            vector_store,
            document_ids,
            rerank_model=rerank_model,
        )
        mock_create_generator.assert_called_once_with(generator_config)
        assert isinstance(pipeline, RAGPipeline)
        assert pipeline.retriever is retriever
        assert pipeline.generator is generator
