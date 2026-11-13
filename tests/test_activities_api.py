from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        activities.clear()
        activities.update(original_activities)


def test_get_activities_returns_participants(client):
    # Arrange
    activities["Chess Club"]["participants"] = ["student@mergington.edu"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == ["student@mergington.edu"]


def test_signup_adds_participant(client):
    # Arrange
    activities["Chess Club"]["participants"] = []

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "new-student@mergington.edu"},
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up new-student@mergington.edu for Chess Club"
    assert activities_response.json()["Chess Club"]["participants"] == [
        "new-student@mergington.edu"
    ]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activities["Chess Club"]["participants"] = ["student@mergington.edu"]

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "student@mergington.edu"},
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 400
    assert activities_response.json()["Chess Club"]["participants"] == [
        "student@mergington.edu"
    ]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    activities["Chess Club"]["participants"] = [
        "student@mergington.edu",
        "another-student@mergington.edu",
    ]

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "student@mergington.edu"},
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered student@mergington.edu from Chess Club"
    assert activities_response.json()["Chess Club"]["participants"] == [
        "another-student@mergington.edu"
    ]


def test_unregister_rejects_unknown_participant(client):
    # Arrange
    activities["Chess Club"]["participants"] = []

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "student@mergington.edu"},
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert activities_response.json()["Chess Club"]["participants"] == []


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
