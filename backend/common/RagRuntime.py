from dataclasses import dataclass
from typing import Any

from langchain_core.vectorstores import VectorStore

from backend.common.protocols import RerankModel


@dataclass
class RagRuntime:
    """Session- or request-scoped live dependencies for RAG.

    Keep serializable settings in configs; put clients, models, and DB
    handles here so factories stay ``create_x(config, runtime, ...)``.

    ``db_session`` is reserved for Postgres lexical / FTS fetchers
    (e.g. SQLAlchemy ``Session`` or a connection wrapper).
    """

    vector_store: VectorStore
    rerank_model: RerankModel | None = None
    db_session: Any | None = None
