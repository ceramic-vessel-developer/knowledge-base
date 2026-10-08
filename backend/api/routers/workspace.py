from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status

from backend.api.crud import (
    create_workspace,
    delete_workspace_for_user,
    get_all_workspaces_for_user,
    get_workspace_for_user,
    get_workspaces_for_user,
    update_workspace_for_user,
)
from backend.api.deps import get_current_user, get_db
from backend.api.schemas import (
    WorkspaceCreate,
    WorkspaceListReturn,
    WorkspaceOption,
    WorkspaceReturn,
    WorkspaceUpdate,
)
from backend.db.models import User, Workspace

router = APIRouter(
    prefix="/workspace",
    tags=["workspace"],
)


@router.post("", response_model=WorkspaceReturn, status_code=status.HTTP_201_CREATED)
async def create_user_workspace(
    workspace_in: WorkspaceCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Workspace:
    return create_workspace(db, workspace_in, current_user.id)


@router.get("", response_model=WorkspaceListReturn)
async def list_user_workspaces(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> WorkspaceListReturn:
    items, total = get_workspaces_for_user(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
    )
    return WorkspaceListReturn(items=items, total=total, skip=skip, limit=limit)


@router.get("/options", response_model=list[WorkspaceOption])
async def list_workspace_options(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Workspace]:
    """All workspaces for the current user (e.g. document upload picker)."""
    return get_all_workspaces_for_user(db, current_user.id)


@router.get("/{workspace_id}", response_model=WorkspaceReturn)
async def get_user_workspace(
    workspace_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Workspace:
    workspace = get_workspace_for_user(db, current_user.id, workspace_id)
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return workspace


@router.patch("/{workspace_id}", response_model=WorkspaceReturn)
async def rename_user_workspace(
    workspace_id: str,
    workspace_in: WorkspaceUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Workspace:
    workspace = update_workspace_for_user(
        db,
        current_user.id,
        workspace_id,
        workspace_in.name,
    )
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_workspace(
    workspace_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    workspace = delete_workspace_for_user(db, current_user.id, workspace_id)
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
