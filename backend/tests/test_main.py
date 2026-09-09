from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_learning_recommendations():
    response = client.get(
        "/api/learning/recommendations"
    )

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "recommendations" in data

    assert isinstance(data["count"], int)
    assert isinstance(data["recommendations"], list)


def test_get_learning_recommendations_with_limit():
    response = client.get(
        "/api/learning/recommendations?limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] <= 2
    assert len(data["recommendations"]) <= 2


def test_get_learning_recommendations_invalid_limit_zero():
    response = client.get(
        "/api/learning/recommendations?limit=0"
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "La limite doit être supérieure ou égale à 1."
    )


def test_get_learning_recommendations_invalid_limit_negative():
    response = client.get(
        "/api/learning/recommendations?limit=-1"
    )

    assert response.status_code == 400


def test_get_learning_recommendations_limit_too_high():
    response = client.get(
        "/api/learning/recommendations?limit=51"
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "La limite ne peut pas dépasser 50."
    )