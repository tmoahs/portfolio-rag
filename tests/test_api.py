import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


# --- 1. Endpoint de santé ---
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- 2. Validation des entrées (sans appeler le modèle) ---
def test_ask_empty_question():
    # Question vide ou de moins de 2 caractères
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_ask_question_too_long():
    # Question dépassant 500 caractères
    long_question = "a" * 501
    response = client.post("/ask", json={"question": long_question})
    assert response.status_code == 422


# --- 3. Question valide avec Mock (fausse fonction RAG) ---
def test_ask_valid_question(monkeypatch):
    fake_exchange_id = "test-uuid-1234"

    def mock_answer_question(question: str):
        from src.rag.pipeline import EXCHANGES_STORE

        EXCHANGES_STORE[fake_exchange_id] = {
            "question": question,
            "answer": "Ceci est une réponse simulée.",
            "sources": ["profil.md"],
            "tokens": 42,
            "latency": 0.1,
        }
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
    # Vérifie que les données internes ne fuitent pas vers le client
    assert "tokens" not in data
    assert "latency" not in data


# --- 4. Tests du Feedback ---
def test_feedback_unknown_exchange_id():
    response = client.post(
        "/feedback",
        json={"exchange_id": "identifiant-inexistant", "rating": "positive"},
    )
    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "Identifiant d'échange introuvable ou expiré."
    )


def test_feedback_valid_exchange():
    from src.rag.pipeline import EXCHANGES_STORE

    valid_id = "uuid-de-test-valide"
    EXCHANGES_STORE[valid_id] = {"question": "Q", "answer": "R"}

    response = client.post(
        "/feedback",
        json={
            "exchange_id": valid_id,
            "rating": "positive",
            "comment": "Super réponse !",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"