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
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


# --- 2. Validation des entrées ---
def test_ask_empty_question(client):
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_ask_question_too_long(client):
    long_question = "a" * 501
    response = client.post("/ask", json={"question": long_question})
    assert response.status_code == 422


# --- 3. Question valide avec Mock ---
def test_ask_valid_question(client, monkeypatch):
    fake_exchange_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

    def mock_answer_question(question: str):
        return {
            "exchange_id": fake_exchange_id,
            "answer": "Ceci est une réponse simulée.",
            "sources": ["profil.md"],
        }

    monkeypatch.setattr("src.api.routes.answer_question", mock_answer_question)

    response = client.post(
        "/ask", json={"question": "Quelles sont ses compétences ?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["exchange_id"] == fake_exchange_id
    assert "answer" in data
    assert "sources" in data
    assert "tokens" not in data
    assert "latency" not in data


# --- 4. Tests du Feedback ---
def test_feedback_unknown_exchange_id(client, monkeypatch):
    async def mock_save_feedback_missing(exchange_id, rating, comment):
        return False

    monkeypatch.setattr("src.api.routes.save_feedback", mock_save_feedback_missing)

    response = client.post(
        "/feedback",
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
        "/feedback",
        json={
            "exchange_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            "rating": "positive",
            "comment": "Super réponse !",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"