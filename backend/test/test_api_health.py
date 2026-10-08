from unittest.mock import MagicMock

from backend.api.main import app


def test_health_ok(client, mock_db):
    mock_db.execute.return_value = MagicMock()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": True,
        "vector_store": True,
    }


def test_health_degraded_without_vector_store(client, mock_db):
    mock_db.execute.return_value = MagicMock()
    app.state.vector_store = None

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["detail"]["status"] == "degraded"
    assert response.json()["detail"]["vector_store"] is False


def test_health_degraded_when_db_fails(client, mock_db):
    mock_db.execute.side_effect = RuntimeError("db down")

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["detail"]["database"] is False
