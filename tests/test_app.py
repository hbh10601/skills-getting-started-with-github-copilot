import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activity_structure():
    # Arrange
    expected_keys = set(app_module.activities.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert set(data.keys()) == expected_keys
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "test.student@mergington.edu"
    assert email not in app_module.activities[activity_name]["participants"]

    # Act
    url = f"/activities/{quote(activity_name, safe='')}/signup?email={quote(email, safe='')}"
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = app_module.activities[activity_name]["participants"][0]

    # Act
    url = f"/activities/{quote(activity_name, safe='')}/signup?email={quote(email, safe='')}"
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant():
    # Arrange
    activity_name = "Programming Class"
    email = app_module.activities[activity_name]["participants"][0]
    assert email in app_module.activities[activity_name]["participants"]

    # Act
    url = f"/activities/{quote(activity_name, safe='')}/participants/{quote(email, safe='')}"
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    email = "missing.student@mergington.edu"
    assert email not in app_module.activities[activity_name]["participants"]

    # Act
    url = f"/activities/{quote(activity_name, safe='')}/participants/{quote(email, safe='')}"
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
