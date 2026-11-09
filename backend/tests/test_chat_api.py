
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes.chat import get_chat_service


class FakeChatService:
    def answer(self, request):
        return {
            "answer": "IncidentPilot uses FastAPI, Next.js, Python, and LangGraph.",
            "sources": [
                {
                    "title": "IncidentPilot",
                    "source": "projects/incidentpilot.md",
                }
            ],
        }


def test_chat_endpoint_returns_answer_and_sources():
    app.dependency_overrides[get_chat_service] = lambda: FakeChatService()

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/chat",
                json={"message": "What technologies does IncidentPilot use?"},
            )

        assert response.status_code == 200
        body = response.json()
        assert "FastAPI" in body["answer"]
        assert body["sources"][0]["source"] == "projects/incidentpilot.md"
    finally:
        app.dependency_overrides.clear()


def test_chat_endpoint_rejects_blank_message():
    with TestClient(app) as client:
        response = client.post("/api/chat", json={"message": "   "})

    assert response.status_code == 422


def test_chat_endpoint_rejects_oversized_message():
    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json={"message": "x" * 2001},
        )

    assert response.status_code == 422
