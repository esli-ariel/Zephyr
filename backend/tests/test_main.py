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

def test_get_learning_plan():
    response = client.get(
        "/api/learning/plan"
    )

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "items" in data

    assert isinstance(data["count"], int)
    assert isinstance(data["items"], list)


def test_get_learning_plan_with_limit():
    response = client.get(
        "/api/learning/plan?limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] >= 0


def test_get_learning_plan_invalid_limit_zero():
    response = client.get(
        "/api/learning/plan?limit=0"
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "La limite doit être supérieure ou égale à 1."
    )


def test_get_learning_plan_invalid_limit_negative():
    response = client.get(
        "/api/learning/plan?limit=-1"
    )

    assert response.status_code == 400


def test_get_learning_plan_limit_too_high():
    response = client.get(
        "/api/learning/plan?limit=21"
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "La limite ne peut pas dépasser 20."
    )

def test_get_learning_plan_with_available_time():
    response = client.get(
        "/api/learning/plan"
        "?limit=5&available_minutes=30"
    )

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "items" in data

    total_minutes = sum(
        item["estimated_minutes"]
        for item in data["items"]
    )

    assert total_minutes <= 30


def test_get_learning_plan_invalid_available_time():
    response = client.get(
        "/api/learning/plan"
        "?available_minutes=0"
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Le temps disponible doit être "
        "supérieur ou égal à 1 minute."
    )