from uuid import uuid4
from unittest.mock import MagicMock

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

from backend.common.RagRuntime import RagRuntime


@pytest.fixture
def sample_documents():
    return [
        Document(
            page_content=(
                "Retrieval-Augmented Generation combines retrieval with language "
                "models. Documents are split into chunks and stored as vectors."
            ),
            metadata={"source": "sample.txt"},
        )
    ]


@pytest.fixture
def sample_chunks():
    return [
        Document(page_content="Chunk one about retrieval.", metadata={"source": "a"}),
        Document(page_content="Chunk two about embeddings.", metadata={"source": "a"}),
    ]


@pytest.fixture
def document_id():
    return uuid4()


@pytest.fixture
def mock_vector_store():
    return MagicMock()


@pytest.fixture
def vector_store():
    return InMemoryVectorStore(embedding=FakeEmbeddings(size=16))


@pytest.fixture
def rag_runtime(vector_store):
    return RagRuntime(vector_store=vector_store)


@pytest.fixture
def rag_runtime_with_reranker(vector_store):
    return RagRuntime(
        vector_store=vector_store,
        rerank_model=MagicMock(),
        db_session=MagicMock(),
    )
