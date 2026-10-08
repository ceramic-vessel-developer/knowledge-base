from contextlib import asynccontextmanager

from fastapi import FastAPI
from langchain_huggingface import HuggingFaceEmbeddings

from backend.db.constants import EMBEDDING_MODEL_NAME
from backend.db.vector_store import create_chunks_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    app.state.embeddings = embeddings
    app.state.vector_store = create_chunks_vector_store(embeddings)
    yield
    app.state.embeddings = None
    app.state.vector_store = None
