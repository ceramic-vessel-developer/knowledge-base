from langchain_core.vectorstores import VectorStore

from backend.common.RetrieverConfigs import RetrieverConfig


class Retriever:
    pass


class RetrieverFactory:
    def create_retriever(self, config: RetrieverConfig, vector_store: VectorStore):
        pass
