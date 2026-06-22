import copy

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_for_activity():
    email = "test.student@mergington.edu"
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_fails():
    email = "duplicate.student@mergington.edu"

    response1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    assert response1.status_code == 200

    response2 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Student already signed up"


def test_signup_for_missing_activity_returns_404():
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "missing@mergington.edu"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant():
    email = "michael@mergington.edu"

    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_fails():
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "ghost@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_root_redirects_to_static_index():
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"
