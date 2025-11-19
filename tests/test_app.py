import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict before/after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect at least one known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "tester@example.com"

    # Ensure email not present initially
    assert email not in activities[activity_name]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity_name]["participants"]

    # Duplicate signup returns 400
    resp = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert resp.status_code == 400

    # Unregister
    resp = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert resp.status_code == 200
    assert email not in activities[activity_name]["participants"]

    # Unregistering a non-registered email returns 404
    resp = client.post(f"/activities/{activity_name}/unregister?email=notregistered@example.com")
    assert resp.status_code == 404
