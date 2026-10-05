from typing import List

from langchain_core.vectorstores import VectorStore

from backend.common.GeneratorConfigs import RAGPipelineConfig
from backend.rag.Generator import Generator, GeneratorFactory
from backend.rag.Reranker import RerankModel
from backend.rag.Retriever import Retriever, RetrieverFactory


class RAGPipeline:
    retriever: Retriever
    generator: Generator

    def __init__(self, retriever: Retriever, generator: Generator):
        self.retriever = retriever
        self.generator = generator

    def run(self, question: str) -> str:
        relevant_chunks = self.retriever.retrieve(question)
        return self.generator.invoke(question, relevant_chunks)


class RAGPipelineFactory:
    def create_pipeline(
        self,
        config: RAGPipelineConfig,
        vector_store: VectorStore,
        document_ids: List[str],
        rerank_model: RerankModel | None = None,
    ) -> RAGPipeline:
        retriever = RetrieverFactory().create_retriever(
            config.retriever_config,
            vector_store,
            document_ids,
            rerank_model=rerank_model,
        )
        generator = GeneratorFactory().create_generator(config.generator_config)
        return RAGPipeline(retriever, generator)
