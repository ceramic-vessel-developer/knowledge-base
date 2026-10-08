from uuid import uuid4
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from langchain_core.documents import Document
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

from backend.api.deps import get_current_user, get_db
from backend.api.main import app
from backend.common.RagRuntime import RagRuntime
from backend.test.api_fixtures import make_user


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


@pytest.fixture
def fake_user():
    return make_user()


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client(fake_user, mock_db):
    def override_get_db():
        yield mock_db

    def override_get_current_user():
        return fake_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.state.vector_store = MagicMock()
    app.state.embeddings = MagicMock()

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
    app.state.vector_store = None
    app.state.embeddings = None


@pytest.fixture
def anon_client(mock_db):
    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    app.state.vector_store = MagicMock()
    app.state.embeddings = MagicMock()

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
    app.state.vector_store = None
    app.state.embeddings = None
