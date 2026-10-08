from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.v1 import EmailStr

from backend.common.FileTypes import FileTypes
from backend.common.message_author import MessageAuthor
from backend.common.role import UserRole
from backend.common.workspace_type import WorkspaceType


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class TimestampSoftDeleteReturn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    modified_at: datetime
    deleted_at: datetime | None = None
    is_deleted: bool


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserReturn(TimestampSoftDeleteReturn):
    id: str
    username: EmailStr
    email: str
    role: UserRole


class WorkspaceCreate(BaseModel):
    name: str
    type: WorkspaceType = WorkspaceType.BASIC


class WorkspaceReturn(TimestampSoftDeleteReturn):
    id: str
    name: str
    type: WorkspaceType
    user_id: str


class DocumentCreate(BaseModel):
    filename: str
    filetype: FileTypes
    workspace_id: str


class DocumentReturn(TimestampSoftDeleteReturn):
    id: str
    filename: str
    filetype: FileTypes
    workspace_id: str


class ChunkReturn(TimestampSoftDeleteReturn):
    id: str
    document_id: str
    chunk_index: int
    content: str


class ChatCreate(BaseModel):
    name: str
    workspace_id: str


class ChatReturn(TimestampSoftDeleteReturn):
    id: str
    name: str
    workspace_id: str


class ChatMessageCreate(BaseModel):
    content: str
    chat_id: str


class ChatMessageReturn(TimestampSoftDeleteReturn):
    id: str
    content: str
    author: MessageAuthor
    chat_id: str
