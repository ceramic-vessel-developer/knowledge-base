from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from langchain_core.vectorstores import VectorStore
from sqlalchemy.orm import Session
from starlette import status

from backend.api.crud import (
    create_chat,
    create_chat_message,
    delete_chat_for_user,
    get_chat_for_user,
    get_chats_for_workspace,
    get_document_ids_for_workspace,
    get_messages_for_chat,
    get_workspace_for_user,
)
from backend.api.deps import get_current_user, get_db, get_vector_store
from backend.api.schemas import (
    ChatAskRequest,
    ChatAskReturn,
    ChatCreate,
    ChatListReturn,
    ChatMessageCreate,
    ChatMessageListReturn,
    ChatReturn,
)
from backend.common.GeneratorConfigs import (
    GenModelType,
    GeneratorConfig,
    PromptType,
    RAGPipelineConfig,
)
from backend.common.RagRuntime import RagRuntime
from backend.common.RetrieverConfigs import (
    FetcherCategories,
    FetcherConfig,
    FetcherTypes,
    RetrieverConfig,
)
from backend.common.message_author import MessageAuthor
from backend.db.models import Chat, User
from backend.rag.RAGPipeline import RAGPipelineFactory

router = APIRouter(
    prefix="/chats",
    tags=["chats"],
)


def _build_pipeline(vector_store: VectorStore, db: Session):
    runtime = RagRuntime(vector_store=vector_store, db_session=db)
    config = RAGPipelineConfig(
        retriever_config=RetrieverConfig(
            fetchers=[
                FetcherConfig(
                    category=FetcherCategories.DENSE,
                    type=FetcherTypes.SIMILARITY,
                    k=4,
                )
            ],
            top_n=3,
        ),
        generator_config=GeneratorConfig(
            gen_model_type=GenModelType.GEMINI_3_5_FLASH_LITE,
            prompt_type=PromptType.BASIC,
        ),
    )
    return RAGPipelineFactory.create_pipeline(config, runtime)


@router.post("", response_model=ChatReturn, status_code=status.HTTP_201_CREATED)
async def create_user_chat(
    chat_in: ChatCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Chat:
    workspace = get_workspace_for_user(db, current_user.id, chat_in.workspace_id)
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return create_chat(db, chat_in)


@router.get("", response_model=ChatListReturn)
async def list_workspace_chats(
    workspace_id: Annotated[str, Query()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ChatListReturn:
    workspace = get_workspace_for_user(db, current_user.id, workspace_id)
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    items, total = get_chats_for_workspace(
        db,
        current_user.id,
        workspace_id,
        skip=skip,
        limit=limit,
    )
    return ChatListReturn(items=items, total=total, skip=skip, limit=limit)


@router.get("/{chat_id}", response_model=ChatReturn)
async def get_user_chat(
    chat_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Chat:
    chat = get_chat_for_user(db, current_user.id, chat_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
    return chat


@router.get("/{chat_id}/messages", response_model=ChatMessageListReturn)
async def list_chat_messages(
    chat_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ChatMessageListReturn:
    result = get_messages_for_chat(
        db,
        current_user.id,
        chat_id,
        skip=skip,
        limit=limit,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
    items, total = result
    return ChatMessageListReturn(items=items, total=total, skip=skip, limit=limit)


@router.post("/{chat_id}/ask", response_model=ChatAskReturn)
async def ask_in_chat(
    chat_id: str,
    body: ChatAskRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
) -> ChatAskReturn:
    chat = get_chat_for_user(db, current_user.id, chat_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    document_ids = get_document_ids_for_workspace(
        db,
        current_user.id,
        chat.workspace_id,
    )
    if document_ids is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    user_message = create_chat_message(
        db,
        ChatMessageCreate(content=body.question, chat_id=chat_id),
        MessageAuthor.USER,
    )

    pipeline = _build_pipeline(vector_store, db)
    answer = pipeline.run(body.question, document_ids)

    ai_message = create_chat_message(
        db,
        ChatMessageCreate(content=answer, chat_id=chat_id),
        MessageAuthor.AI,
    )
    return ChatAskReturn(user_message=user_message, ai_message=ai_message)


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_chat(
    chat_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    chat = delete_chat_for_user(db, current_user.id, chat_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
