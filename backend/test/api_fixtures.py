from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from backend.common.FileTypes import FileTypes
from backend.common.message_author import MessageAuthor
from backend.common.role import UserRole
from backend.common.workspace_type import WorkspaceType


def _now():
    return datetime.now(timezone.utc)


def make_user(**overrides):
    data = {
        "id": str(uuid4()),
        "username": "alice",
        "email": "alice@example.com",
        "password_hash": "hashed",
        "role": UserRole.USER,
        "created_at": _now(),
        "modified_at": _now(),
        "deleted_at": None,
        "is_deleted": False,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_workspace(*, user_id: str, **overrides):
    data = {
        "id": str(uuid4()),
        "name": "Docs",
        "type": WorkspaceType.BASIC,
        "user_id": user_id,
        "created_at": _now(),
        "modified_at": _now(),
        "deleted_at": None,
        "is_deleted": False,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_document(*, workspace_id: str, **overrides):
    data = {
        "id": str(uuid4()),
        "filename": "notes.txt",
        "filetype": FileTypes.TXT,
        "workspace_id": workspace_id,
        "created_at": _now(),
        "modified_at": _now(),
        "deleted_at": None,
        "is_deleted": False,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_chat(*, workspace_id: str, **overrides):
    data = {
        "id": str(uuid4()),
        "name": "Q&A",
        "workspace_id": workspace_id,
        "created_at": _now(),
        "modified_at": _now(),
        "deleted_at": None,
        "is_deleted": False,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_message(*, chat_id: str, author=MessageAuthor.USER, **overrides):
    data = {
        "id": str(uuid4()),
        "content": "hello",
        "author": author,
        "chat_id": chat_id,
        "created_at": _now(),
        "modified_at": _now(),
        "deleted_at": None,
        "is_deleted": False,
    }
    data.update(overrides)
    return SimpleNamespace(**data)
