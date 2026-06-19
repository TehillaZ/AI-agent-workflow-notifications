"""Phase 4: input validation and safe PUT updates."""

import json

import pytest

from main import app
from storage import seed


@pytest.fixture
def client():
    seed()
    app.config["TESTING"] = True
    return app.test_client()


def test_create_missing_body_returns_400(client):
    response = client.post("/notifications", data="", content_type="application/json")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_missing_message_returns_400(client):
    response = client.post(
        "/notifications",
        data=json.dumps({"targetChannels": [{"type": "email", "value": "a@b.com"}]}),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_invalid_channel_type_returns_400(client):
    response = client.post(
        "/notifications",
        data=json.dumps(
            {
                "message": "hello",
                "targetChannels": [{"type": "fax", "value": "123"}],
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_valid_body_returns_200(client):
    response = client.post(
        "/notifications",
        data=json.dumps(
            {
                "message": "hello",
                "targetChannels": [{"type": "email", "value": "a@b.com"}],
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == "hello"
    assert body["id"] == 6


def test_put_disallowed_status_field_returns_400(client):
    response = client.put(
        "/notifications/1",
        data=json.dumps({"status": "pending"}),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_put_allowed_message_updates(client):
    response = client.put(
        "/notifications/2",
        data=json.dumps({"message": "Updated message"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json()["message"] == "Updated message"


def test_put_sms_channel_recomputes_sms_segments(client):
    response = client.put(
        "/notifications/1",
        data=json.dumps(
            {
                "targetChannels": [{"type": "sms", "value": "+15551234567"}],
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json()["smsSegments"] == 1
