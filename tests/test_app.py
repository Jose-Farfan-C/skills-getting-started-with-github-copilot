from fastapi.testclient import TestClient
from src.app import app, activities
import copy
import pytest

client = TestClient(app)
_original_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    yield
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


def test_root_redirects_to_static():
    r = client.get("/")
    assert r.status_code == 200
    assert "Mergington High School" in r.text


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    email = "tester@example.com"
    activity = "Chess Club"
    # signup
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")
    # confirm present
    r2 = client.get("/activities")
    assert email in r2.json()[activity]["participants"]
    # unregister
    r = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert r.status_code == 200
    assert "Unregistered" in r.json().get("message", "")
    # confirm removed
    r3 = client.get("/activities")
    assert email not in r3.json()[activity]["participants"]


def test_signup_already_registered_returns_400():
    activity = "Chess Club"
    existing = "michael@mergington.edu"
    r = client.post(f"/activities/{activity}/signup", params={"email": existing})
    assert r.status_code == 400


def test_unregister_not_registered_returns_400():
    activity = "Chess Club"
    nope = "not-registered@example.com"
    r = client.delete(f"/activities/{activity}/unregister", params={"email": nope})
    assert r.status_code == 400


def test_activity_not_found_returns_404():
    r = client.post("/activities/Nope/signup", params={"email": "a@b.com"})
    assert r.status_code == 404
    r = client.delete("/activities/Nope/unregister", params={"email": "a@b.com"})
    assert r.status_code == 404
