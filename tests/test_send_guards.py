"""Phase 5: send guards and HTTP semantics."""

import json
from unittest.mock import patch

import pytest

from main import app
from models import FAILED
from storage import seed


@pytest.fixture
def client():
    seed()
    app.config["TESTING"] = True
    return app.test_client()


def test_send_sent_notification_returns_409(client):
    response = client.post("/notifications/1/send")
    assert response.status_code == 409
    body = response.get_json()
    assert "error" in body


def test_send_retry_pending_returns_200(client):
    with patch("processor.send_sms", return_value=_success("[sms] ok")):
        with patch("processor.send_push", return_value=_success("[push] ok")):
            with patch("processor.send_email", return_value=_success("[email] ok")):
                before = client.get("/notifications/5").get_json()["attempts"]
                response = client.post("/notifications/5/send")
    assert response.status_code == 200
    assert response.get_json()["attempts"] == before + 1


def test_send_failed_notification_returns_200(client):
    with patch("processor.send_push", return_value=_success("[push] ok")):
        before = client.get("/notifications/3").get_json()["attempts"]
        response = client.post("/notifications/3/send")
    assert response.status_code == 200
    assert response.get_json()["attempts"] == before + 1


@patch("processor.send_sms", return_value={"Result": "PermanentFailure", "ErrorCode": "X", "Message": "[sms] rejected"})
def test_send_delivery_failure_still_returns_200(mock_send, client):
    response = client.post("/notifications/2/send")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == FAILED


def _success(message):
    return {"Result": "Success", "ErrorCode": "OK", "Message": message}
