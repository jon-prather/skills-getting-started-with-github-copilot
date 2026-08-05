import copy
import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import app as app_module
from src.app import app

INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)
client = TestClient(app)


import pytest

@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert isinstance(activities["Chess Club"]["participants"], list)
    assert len(activities["Chess Club"]["participants"]) == 2


def test_signup_adds_participant():
    email = "taylor@mergington.edu"

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert email in participants


def test_signup_duplicate_returns_400():
    email = "morgan@mergington.edu"

    first_response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": email},
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": email},
    )
    assert second_response.status_code == 400
    assert "already signed up" in second_response.json()["detail"].lower()


def test_unregister_removes_participant():
    email = "alex@mergington.edu"

    response = client.delete(
        "/activities/Basketball Team/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    activities_response = client.get("/activities")
    participants = activities_response.json()["Basketball Team"]["participants"]
    assert email not in participants
