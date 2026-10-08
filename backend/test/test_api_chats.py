from unittest.mock import MagicMock, patch

from backend.common.message_author import MessageAuthor
from backend.test.api_fixtures import (
    make_chat,
    make_message,
    make_workspace,
)


def test_create_chat(client, fake_user):
    workspace = make_workspace(user_id=fake_user.id)
    chat = make_chat(workspace_id=workspace.id, name="Thread")

    with (
        patch(
            "backend.api.routers.chat.get_workspace_for_user",
            return_value=workspace,
        ),
        patch("backend.api.routers.chat.create_chat", return_value=chat) as mock_create,
    ):
        response = client.post(
            "/chats",
            json={"name": "Thread", "workspace_id": workspace.id},
        )

    assert response.status_code == 201
    assert response.json()["name"] == "Thread"
    mock_create.assert_called_once()


def test_create_chat_workspace_missing(client):
    with patch(
        "backend.api.routers.chat.get_workspace_for_user",
        return_value=None,
    ):
        response = client.post(
            "/chats",
            json={"name": "Thread", "workspace_id": "missing"},
        )

    assert response.status_code == 404


def test_list_chats(client, fake_user):
    workspace = make_workspace(user_id=fake_user.id)
    chats = [make_chat(workspace_id=workspace.id)]

    with (
        patch(
            "backend.api.routers.chat.get_workspace_for_user",
            return_value=workspace,
        ),
        patch(
            "backend.api.routers.chat.get_chats_for_workspace",
            return_value=(chats, 1),
        ),
    ):
        response = client.get(f"/chats?workspace_id={workspace.id}")

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_get_chat(client, fake_user):
    chat = make_chat(workspace_id="ws-1")

    with patch(
        "backend.api.routers.chat.get_chat_for_user",
        return_value=chat,
    ):
        response = client.get(f"/chats/{chat.id}")

    assert response.status_code == 200
    assert response.json()["id"] == chat.id


def test_rename_chat(client, fake_user):
    chat = make_chat(workspace_id="ws-1", name="Renamed")

    with patch(
        "backend.api.routers.chat.update_chat_for_user",
        return_value=chat,
    ) as mock_update:
        response = client.patch(f"/chats/{chat.id}", json={"name": "Renamed"})

    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"
    mock_update.assert_called_once()


def test_list_messages(client, fake_user):
    chat = make_chat(workspace_id="ws-1")
    messages = [
        make_message(chat_id=chat.id, content="q", author=MessageAuthor.USER),
        make_message(chat_id=chat.id, content="a", author=MessageAuthor.AI),
    ]

    with patch(
        "backend.api.routers.chat.get_messages_for_chat",
        return_value=(messages, 2),
    ):
        response = client.get(f"/chats/{chat.id}/messages?skip=0&limit=50")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["items"][0]["author"] == "user"


def test_list_messages_chat_missing(client):
    with patch(
        "backend.api.routers.chat.get_messages_for_chat",
        return_value=None,
    ):
        response = client.get("/chats/missing/messages")

    assert response.status_code == 404


def test_ask_requires_documents(client, fake_user):
    chat = make_chat(workspace_id="ws-1")

    with (
        patch("backend.api.routers.chat.get_chat_for_user", return_value=chat),
        patch(
            "backend.api.routers.chat.get_document_ids_for_workspace",
            return_value=[],
        ),
    ):
        response = client.post(
            f"/chats/{chat.id}/ask",
            json={"question": "What is RAG?"},
        )

    assert response.status_code == 400
    assert "no documents" in response.json()["detail"]


def test_ask_persists_user_and_ai_messages(client, fake_user):
    chat = make_chat(workspace_id="ws-1")
    user_msg = make_message(chat_id=chat.id, content="What is RAG?")
    ai_msg = make_message(
        chat_id=chat.id,
        content="Retrieval-augmented generation.",
        author=MessageAuthor.AI,
    )
    pipeline = MagicMock()
    pipeline.run.return_value = ai_msg.content

    with (
        patch("backend.api.routers.chat.get_chat_for_user", return_value=chat),
        patch(
            "backend.api.routers.chat.get_document_ids_for_workspace",
            return_value=["doc-1"],
        ),
        patch(
            "backend.api.routers.chat.create_chat_message",
            side_effect=[user_msg, ai_msg],
        ) as mock_create_msg,
        patch(
            "backend.api.routers.chat._build_pipeline",
            return_value=pipeline,
        ),
    ):
        response = client.post(
            f"/chats/{chat.id}/ask",
            json={"question": "What is RAG?"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["user_message"]["content"] == "What is RAG?"
    assert body["ai_message"]["content"] == ai_msg.content
    assert mock_create_msg.call_count == 2
    pipeline.run.assert_called_once_with("What is RAG?", ["doc-1"])


def test_delete_chat(client, fake_user):
    chat = make_chat(workspace_id="ws-1")

    with patch(
        "backend.api.routers.chat.delete_chat_for_user",
        return_value=chat,
    ):
        response = client.delete(f"/chats/{chat.id}")

    assert response.status_code == 204
