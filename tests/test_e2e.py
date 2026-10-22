import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.mark.manual
def test_real_pipeline_end_to_end(client):
    # 1. Pose une vraie question
    res_ask = client.post(
        "/ask",
        json={
            "question": "Quels sont les scores du projet de prédiction des bâtiments ?"
        },
    )
    assert res_ask.status_code == 200
    data_ask = res_ask.json()
    assert "exchange_id" in data_ask
    assert len(data_ask["sources"]) > 0

    # 2. Envoie un vrai feedback relié
    res_feedback = client.post(
        "/feedback",
        json={
            "exchange_id": data_ask["exchange_id"],
            "rating": "positive",
            "comment": "Test E2E manuel réussi",
        },
    )
    assert res_feedback.status_code == 200
    assert res_feedback.json()["status"] == "ok"