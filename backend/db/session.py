import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_DEFAULT_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/knowledge"


def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", _DEFAULT_URL)


def create_db_engine(url: str | None = None, **kwargs) -> Engine:
    return create_engine(url or get_database_url(), pool_pre_ping=True, **kwargs)


def create_session_factory(engine: Engine | None = None) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine or create_db_engine(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
