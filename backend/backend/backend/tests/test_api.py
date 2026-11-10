
from fastapi.testclient import TestClient

from backend.backend.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_agents_endpoint():
    response = client.get("/agents")

    assert response.status_code == 200
    assert len(response.json()) == 6


def test_get_existing_agent():
    response = client.get("/agents/developer")

    assert response.status_code == 200
    assert response.json()["id"] == "developer"


def test_unknown_agent_returns_404():
    response = client.get("/agents/unknown")

    assert response.status_code == 404


def test_empty_agent_task_returns_422():
    response = client.post(
        "/agents/developer/run",
        json={"task": ""},
    )

    assert response.status_code == 422


def test_empty_plan_description_returns_422():
    response = client.post(
        "/tasks/plan",
        json={"description": ""},
    )

    assert response.status_code == 422


def test_ai_status_endpoint():
    response = client.get("/ai/status")

    assert response.status_code == 200
    assert "provider" in response.json()
