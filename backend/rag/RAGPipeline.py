from typing import List

from backend.common.GeneratorConfigs import RAGPipelineConfig
from backend.common.RagRuntime import RagRuntime
from backend.rag.Generator import Generator, GeneratorFactory
from backend.rag.Retriever import Retriever, RetrieverFactory


class RAGPipeline:
    retriever: Retriever
    generator: Generator

    def __init__(self, retriever: Retriever, generator: Generator):
        self.retriever = retriever
        self.generator = generator

    def run(self, question: str, document_ids: List[str]) -> str:
        relevant_chunks = self.retriever.retrieve(question, document_ids)
        return self.generator.invoke(question, relevant_chunks)


class RAGPipelineFactory:
    @staticmethod
    def create_pipeline(
        config: RAGPipelineConfig,
        runtime: RagRuntime,
    ) -> RAGPipeline:
        retriever = RetrieverFactory.create_retriever(
            config.retriever_config,
            runtime,
        )
        generator = GeneratorFactory.create_generator(config.generator_config)
        return RAGPipeline(retriever, generator)
