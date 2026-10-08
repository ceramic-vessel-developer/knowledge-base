from unittest.mock import MagicMock, patch

from backend.common.FileTypes import FileTypes
from backend.test.api_fixtures import make_document, make_workspace


def test_list_documents_paginated(client, fake_user):
    workspace = make_workspace(user_id=fake_user.id)
    docs = [make_document(workspace_id=workspace.id)]

    with patch(
        "backend.api.routers.document.get_documents_for_workspace",
        return_value=(docs, 1),
    ):
        response = client.get(
            f"/documents?workspace_id={workspace.id}&skip=0&limit=20"
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["filename"] == "notes.txt"


def test_get_document(client, fake_user):
    doc = make_document(workspace_id="ws-1")

    with patch(
        "backend.api.routers.document.get_document_for_user",
        return_value=doc,
    ):
        response = client.get(f"/documents/{doc.id}")

    assert response.status_code == 200
    assert response.json()["id"] == doc.id


def test_get_document_not_found(client):
    with patch(
        "backend.api.routers.document.get_document_for_user",
        return_value=None,
    ):
        response = client.get("/documents/missing")

    assert response.status_code == 404


def test_delete_document(client, fake_user):
    doc = make_document(workspace_id="ws-1")

    with patch(
        "backend.api.routers.document.delete_document_for_user",
        return_value=doc,
    ):
        response = client.delete(f"/documents/{doc.id}")

    assert response.status_code == 204


def test_upload_document_cleans_temp_file(client, fake_user, tmp_path):
    workspace = make_workspace(user_id=fake_user.id)
    created = make_document(workspace_id=workspace.id, filename="upload.txt")
    processor = MagicMock()

    with (
        patch(
            "backend.api.routers.document.get_workspace_for_user",
            return_value=workspace,
        ),
        patch(
            "backend.api.routers.document.create_document",
            return_value=created,
        ) as mock_create,
        patch(
            "backend.api.routers.document.prepare_document_processor",
            return_value=processor,
        ),
        patch(
            "backend.api.routers.document.tempfile.gettempdir",
            return_value=str(tmp_path),
        ),
        patch("backend.api.routers.document.os.remove") as mock_remove,
    ):
        response = client.post(
            "/documents",
            data={
                "filename": "upload.txt",
                "filetype": str(FileTypes.TXT.value),
                "workspace_id": workspace.id,
            },
            files={"file": ("upload.txt", b"hello world", "text/plain")},
        )

    assert response.status_code == 201
    assert response.json()["filename"] == "upload.txt"
    processor.process.assert_called_once()
    mock_create.assert_called_once()
    mock_remove.assert_called_once()
