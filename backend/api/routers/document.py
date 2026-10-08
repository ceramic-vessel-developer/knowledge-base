import os
import tempfile
import uuid
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from langchain_core.vectorstores import VectorStore
from sqlalchemy.orm import Session
from starlette import status

from backend.api.crud import (
    create_document,
    delete_document_for_user,
    get_documents_for_workspace,
    get_workspace_for_user,
)
from backend.api.deps import get_current_user, get_db, get_vector_store
from backend.api.schemas import DocumentCreate, DocumentListReturn, DocumentReturn
from backend.common.DocumentProcessorConfigs import (
    DocumentLoaderConfig,
    DocumentProcessorConfig,
    DocumentSplitterConfig,
)
from backend.common.FileTypes import FileTypes
from backend.db.models import Document, User
from backend.rag.DocumentProcessor import DocumentProcessor, DocumentProcessorFactory

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


def prepare_document_processor(
    *,
    file_path: str,
    filetype: FileTypes,
    vector_store: VectorStore,
    chunk_size: int = 4000,
    chunk_overlap: int = 200,
) -> DocumentProcessor:
    config = DocumentProcessorConfig(
        loader_config=DocumentLoaderConfig(filename=file_path, filetype=filetype),
        splitter_config=DocumentSplitterConfig(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        ),
    )
    return DocumentProcessorFactory.create_processor(config, vector_store)


@router.post("", response_model=DocumentReturn, status_code=status.HTTP_201_CREATED)
async def upload_user_document(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
    document_in: DocumentCreate,
    file: UploadFile = File(...),
) -> Document:
    workspace = get_workspace_for_user(db, current_user.id, document_in.workspace_id)
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    # Generate UUID for filename
    file_uuid = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]  # Get file extension
    filename = f"{file_uuid}{file_ext}"

    # Save file temporarily to system temp directory
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, filename)

    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())

    processor = prepare_document_processor(
        file_path=temp_path,
        filetype=document_in.filetype,
        vector_store=vector_store,
    )
    document = create_document(db, document_in)
    processor.process(UUID(document.id))
    return document


@router.get("", response_model=DocumentListReturn)
async def list_workspace_documents(
    workspace_id: Annotated[str, Query()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> DocumentListReturn:
    items, total = get_documents_for_workspace(
        db,
        current_user.id,
        workspace_id,
        skip=skip,
        limit=limit,
    )
    return DocumentListReturn(items=items, total=total, skip=skip, limit=limit)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_document(
    document_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    document = delete_document_for_user(db, current_user.id, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
