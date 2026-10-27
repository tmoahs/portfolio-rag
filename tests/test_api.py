from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from src.api.db import get_db_connection
from src.api.main import app


async def override_get_db_connection():
    mock_conn = MagicMock()
    mock_cursor = AsyncMock()

    # Configure cursor() pour être un async context manager valide
    mock_cursor.__aenter__.return_value = mock_cursor
    mock_cursor.__aexit__.return_value = None

    mock_conn.cursor.return_value = mock_cursor
    yield mock_conn

@pytest.fixture(autouse=True)
def setup_db_override(monkeypatch):
    async def fake_noop(*args, **kwargs):
        pass

    monkeypatch.setattr("src.api.main.init_db_pool", fake_noop)
    monkeypatch.setattr("src.api.main.close_db_pool", fake_noop)
    monkeypatch.setattr("src.api.main.init_cache", lambda: None)
    monkeypatch.setattr("src.api.routes.save_exchange", fake_noop)

    app.dependency_overrides[get_db_connection] = override_get_db_connection
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# --- 1. Endpoint de santé ---
def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


# --- 2. Validation des entrées ---
def test_ask_empty_question(client):
    response = client.post("/api/ask", json={"question": ""})
    assert response.status_code == 422


def test_ask_question_too_long(client):
    long_question = "a" * 501
    response = client.post("/api/ask", json={"question": long_question})
    assert response.status_code == 422


# --- 3. Question valide avec Mock ---
def test_ask_valid_question(client, monkeypatch):
    fake_exchange_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

    def mock_answer_question(question: str, use_cache: bool = True):
        return {
            "exchange_id": fake_exchange_id,
            "answer": "Ceci est une réponse simulée.",
            "sources": ["profil.md"],
        }

    monkeypatch.setattr("src.api.routes.answer_question", mock_answer_question)

    response = client.post(
        "/api/ask", json={"question": "Quelles sont ses compétences ?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["exchange_id"] == fake_exchange_id
    assert "answer" in data
    assert "sources" in data
    assert "tokens" not in data
    assert "latency" not in data


def test_ask_returns_chunks_for_sources_accordion(client, monkeypatch):
    """Les extraits utilisés doivent remonter jusqu'à l'interface."""

    def mock_answer_question(question: str, use_cache: bool = True):
        return {
            "exchange_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            "answer": "Réponse simulée.",
            "sources": ["profil.md"],
            "chunks": [
                {
                    "text": "Extrait du profil utilisé par le modèle.",
                    "source": "knowledge/profil.md",
                    "title": "Profil",
                    "distance": 0.12,
                }
            ],
        }

    monkeypatch.setattr("src.api.routes.answer_question", mock_answer_question)

    response = client.post("/api/ask", json={"question": "Quel est son profil ?"})
    assert response.status_code == 200

    chunks = response.json()["chunks"]
    assert len(chunks) == 1
    assert chunks[0]["text"] == "Extrait du profil utilisé par le modèle."
    assert chunks[0]["source"] == "knowledge/profil.md"


def test_ask_bypass_cache_header(client, monkeypatch):
    """L'en-tête X-Bypass-Cache doit désactiver le cache (évaluations)."""
    seen = {}

    def mock_answer_question(question: str, use_cache: bool = True):
        seen["use_cache"] = use_cache
        return {"exchange_id": "bypass", "answer": "ok", "sources": []}

    monkeypatch.setattr("src.api.routes.answer_question", mock_answer_question)

    client.post("/api/ask", json={"question": "Question sans cache"})
    assert seen["use_cache"] is True

    client.post(
        "/api/ask",
        json={"question": "Question sans cache"},
        headers={"X-Bypass-Cache": "1"},
    )
    assert seen["use_cache"] is False


# --- 5. Endpoint de streaming ---
def test_ask_stream_returns_sse_events(client, monkeypatch):
    def fake_stream(question: str, use_cache: bool = True):
        yield "meta", {"exchange_id": "stream-1"}
        yield "sources", {
            "chunks": [
                {
                    "text": "Extrait utilisé.",
                    "source": "knowledge/profil.md",
                    "title": "Profil",
                    "distance": 0.1,
                }
            ],
            "sources": ["knowledge/profil.md"],
        }
        yield "delta", "Bonjour"
        yield "delta", " Thomas"
        yield "done", {
            "exchange_id": "stream-1",
            "answer": "Bonjour Thomas",
            "sources": ["knowledge/profil.md"],
            "latency": 1.2,
            "tokens": 12,
        }

    monkeypatch.setattr("src.api.routes.answer_question_stream", fake_stream)

    response = client.post(
        "/api/ask/stream", json={"question": "Bonjour, qui est Thomas ?"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    import json

    events = [
        json.loads(line[len("data:"):].strip())
        for line in response.text.splitlines()
        if line.startswith("data:")
    ]

    types = [event["type"] for event in events]
    assert types == ["meta", "sources", "delta", "delta", "done"]
    assert "".join(e["text"] for e in events if e["type"] == "delta") == "Bonjour Thomas"
    assert events[-1]["answer"] == "Bonjour Thomas"
    assert events[-1]["latency"] == 1.2


def test_ask_stream_reports_errors_as_events(client, monkeypatch):
    from src.rag.generation import GeminiQuotaError

    def failing_stream(question: str, use_cache: bool = True):
        yield "meta", {"exchange_id": "stream-2"}
        raise GeminiQuotaError("Quota API dépassé.")

    monkeypatch.setattr("src.api.routes.answer_question_stream", failing_stream)

    response = client.post("/api/ask/stream", json={"question": "Question quelconque"})
    assert response.status_code == 200
    assert '"type": "error"' in response.text
    assert '"status": 429' in response.text


# --- 4. Tests du Feedback ---
def test_feedback_unknown_exchange_id(client, monkeypatch):
    async def mock_save_feedback_missing(exchange_id, rating, comment):
        return False

    monkeypatch.setattr("src.api.routes.save_feedback", mock_save_feedback_missing)

    response = client.post(
        "/api/feedback",
        json={"exchange_id": "identifiant-inexistant", "rating": "positive"},
    )
    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "Identifiant d'échange introuvable ou expiré."
    )


def test_feedback_valid_exchange(client, monkeypatch):
    async def mock_save_feedback(exchange_id, rating, comment):
        return True

    monkeypatch.setattr("src.api.routes.save_feedback", mock_save_feedback)

    response = client.post(
        "/api/feedback",
        json={
            "exchange_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            "rating": "positive",
            "comment": "Super réponse !",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
