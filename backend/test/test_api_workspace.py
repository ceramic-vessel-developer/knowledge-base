from unittest.mock import patch

from backend.test.api_fixtures import make_workspace


def test_create_workspace(client, fake_user):
    workspace = make_workspace(user_id=fake_user.id, name="Research")

    with patch(
        "backend.api.routers.workspace.create_workspace",
        return_value=workspace,
    ) as mock_create:
        response = client.post("/workspace", json={"name": "Research"})

    assert response.status_code == 201
    assert response.json()["name"] == "Research"
    assert response.json()["user_id"] == fake_user.id
    mock_create.assert_called_once()
    assert mock_create.call_args.args[2] == fake_user.id


def test_list_workspaces_paginated(client, fake_user):
    items = [make_workspace(user_id=fake_user.id, name="A")]

    with patch(
        "backend.api.routers.workspace.get_workspaces_for_user",
        return_value=(items, 1),
    ):
        response = client.get("/workspace?skip=0&limit=10")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["skip"] == 0
    assert body["limit"] == 10
    assert len(body["items"]) == 1


def test_list_workspace_options(client, fake_user):
    items = [make_workspace(user_id=fake_user.id, name="A")]

    with patch(
        "backend.api.routers.workspace.get_all_workspaces_for_user",
        return_value=items,
    ):
        response = client.get("/workspace/options")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "A"
    assert "user_id" not in response.json()[0]


def test_get_workspace(client, fake_user):
    workspace = make_workspace(user_id=fake_user.id)

    with patch(
        "backend.api.routers.workspace.get_workspace_for_user",
        return_value=workspace,
    ):
        response = client.get(f"/workspace/{workspace.id}")

    assert response.status_code == 200
    assert response.json()["id"] == workspace.id


def test_get_workspace_not_found(client):
    with patch(
        "backend.api.routers.workspace.get_workspace_for_user",
        return_value=None,
    ):
        response = client.get("/workspace/missing")

    assert response.status_code == 404


def test_rename_workspace(client, fake_user):
    workspace = make_workspace(user_id=fake_user.id, name="New")

    with patch(
        "backend.api.routers.workspace.update_workspace_for_user",
        return_value=workspace,
    ) as mock_update:
        response = client.patch(
            f"/workspace/{workspace.id}",
            json={"name": "New"},
        )

    assert response.status_code == 200
    assert response.json()["name"] == "New"
    mock_update.assert_called_once_with(
        mock_update.call_args.args[0],
        fake_user.id,
        workspace.id,
        "New",
    )


def test_delete_workspace(client, fake_user):
    workspace = make_workspace(user_id=fake_user.id)

    with patch(
        "backend.api.routers.workspace.delete_workspace_for_user",
        return_value=workspace,
    ):
        response = client.delete(f"/workspace/{workspace.id}")

    assert response.status_code == 204


def test_delete_workspace_not_found(client):
    with patch(
        "backend.api.routers.workspace.delete_workspace_for_user",
        return_value=None,
    ):
        response = client.delete("/workspace/missing")

    assert response.status_code == 404
