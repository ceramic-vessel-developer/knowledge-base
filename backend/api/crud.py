from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from backend.api.schemas import (
    ChatCreate,
    ChatMessageCreate,
    DocumentCreate,
    UserCreate,
    WorkspaceCreate,
)
from backend.common.message_author import MessageAuthor
from backend.common.role import UserRole
from backend.db.models import Chat, ChatMessage, Document, User, Workspace


def _save(db: Session, obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def _soft_delete(db: Session, obj):
    obj.is_deleted = True
    obj.deleted_at = datetime.now(timezone.utc)
    return _save(db, obj)


def get_user(db: Session, username: str) -> User | None:
    return db.scalar(
        select(User).where(
            User.username == username,
            User.is_deleted.is_(False),
        )
    )


def create_user(
    db: Session,
    user_in: UserCreate,
    password_hash: str,
) -> User:
    return _save(
        db,
        User(
            username=user_in.username,
            email=user_in.email,
            password_hash=password_hash,
            role=UserRole.USER,
        ),
    )


def create_workspace(
    db: Session,
    workspace_in: WorkspaceCreate,
    user_id: str,
) -> Workspace:
    return _save(
        db,
        Workspace(**workspace_in.model_dump(), user_id=user_id),
    )


def get_workspace_for_user(
    db: Session,
    user_id: str,
    workspace_id: str,
) -> Workspace | None:
    return db.scalar(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.user_id == user_id,
            Workspace.is_deleted.is_(False),
        )
    )


def get_workspaces_for_user(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Workspace], int]:
    filters = (
        Workspace.user_id == user_id,
        Workspace.is_deleted.is_(False),
    )
    total = db.scalar(select(func.count()).select_from(Workspace).where(*filters)) or 0
    items = list(
        db.scalars(
            select(Workspace)
            .where(*filters)
            .order_by(Workspace.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()
    )
    return items, total


def get_all_workspaces_for_user(db: Session, user_id: str) -> list[Workspace]:
    return list(
        db.scalars(
            select(Workspace)
            .where(
                Workspace.user_id == user_id,
                Workspace.is_deleted.is_(False),
            )
            .order_by(Workspace.name)
        ).all()
    )


def delete_workspace_for_user(
    db: Session,
    user_id: str,
    workspace_id: str,
) -> Workspace | None:
    workspace = get_workspace_for_user(db, user_id, workspace_id)
    if workspace is None:
        return None
    now = datetime.now(timezone.utc)
    db.execute(
        update(Document)
        .where(
            Document.workspace_id == workspace_id,
            Document.is_deleted.is_(False),
        )
        .values(is_deleted=True, deleted_at=now)
    )
    return _soft_delete(db, workspace)


def create_document(db: Session, document_in: DocumentCreate) -> Document:
    return _save(db, Document(**document_in.model_dump()))


def get_document_for_user(
    db: Session,
    user_id: str,
    document_id: str,
) -> Document | None:
    return db.scalar(
        select(Document)
        .join(Workspace, Document.workspace_id == Workspace.id)
        .where(
            Document.id == document_id,
            Workspace.user_id == user_id,
            Document.is_deleted.is_(False),
            Workspace.is_deleted.is_(False),
        )
    )


def delete_document_for_user(
    db: Session,
    user_id: str,
    document_id: str,
) -> Document | None:
    document = get_document_for_user(db, user_id, document_id)
    if document is None:
        return None
    return _soft_delete(db, document)


def get_documents_for_workspace(
    db: Session,
    user_id: str,
    workspace_id: str,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Document], int]:
    filters = (
        Document.workspace_id == workspace_id,
        Workspace.user_id == user_id,
        Document.is_deleted.is_(False),
        Workspace.is_deleted.is_(False),
    )
    total = (
        db.scalar(
            select(func.count())
            .select_from(Document)
            .join(Workspace, Document.workspace_id == Workspace.id)
            .where(*filters)
        )
        or 0
    )
    items = list(
        db.scalars(
            select(Document)
            .join(Workspace, Document.workspace_id == Workspace.id)
            .where(*filters)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()
    )
    return items, total


def create_chat(db: Session, chat_in: ChatCreate) -> Chat:
    return _save(db, Chat(**chat_in.model_dump()))


def create_chat_message(
    db: Session,
    message_in: ChatMessageCreate,
    author: MessageAuthor,
) -> ChatMessage:
    return _save(
        db,
        ChatMessage(**message_in.model_dump(), author=author),
    )
