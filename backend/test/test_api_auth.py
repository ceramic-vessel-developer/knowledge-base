from unittest.mock import patch

from backend.api.main import get_password_hash
from backend.test.api_fixtures import make_user


def test_register_user_created(anon_client):
    created = make_user(username="bob", email="bob@example.com")

    with (
        patch("backend.api.main.get_user", return_value=None),
        patch("backend.api.main.create_user", return_value=created) as mock_create,
    ):
        response = anon_client.post(
            "/users",
            json={
                "username": "bob",
                "email": "bob@example.com",
                "password": "secret123",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "bob"
    assert body["email"] == "bob@example.com"
    assert "password" not in body
    mock_create.assert_called_once()


def test_register_user_duplicate_username(anon_client):
    with patch("backend.api.main.get_user", return_value=make_user()):
        response = anon_client.post(
            "/users",
            json={
                "username": "alice",
                "email": "alice@example.com",
                "password": "secret123",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_login_returns_token(anon_client):
    password = "secret123"
    user = make_user(password_hash=get_password_hash(password))

    with patch("backend.api.main.get_user", return_value=user):
        response = anon_client.post(
            "/token",
            data={"username": "alice", "password": password},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_rejects_bad_password(anon_client):
    user = make_user(password_hash=get_password_hash("correct"))

    with patch("backend.api.main.get_user", return_value=user):
        response = anon_client.post(
            "/token",
            data={"username": "alice", "password": "wrong"},
        )

    assert response.status_code == 401


def test_users_me_returns_current_user(client, fake_user):
    response = client.get("/users/me")

    assert response.status_code == 200
    assert response.json()["username"] == fake_user.username
    assert response.json()["id"] == fake_user.id


def test_users_me_requires_auth(anon_client):
    response = anon_client.get("/users/me")

    assert response.status_code == 401
