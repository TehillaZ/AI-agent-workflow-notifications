"""Phase 1: provider Result → notification status mapping."""

from unittest.mock import patch

from models import FAILED, RETRY_PENDING, SENT


def _response(result, message="[test] message", error_code="TEST_CODE"):
    return {"Result": result, "ErrorCode": error_code, "Message": message}


@patch("processor.send_email")
def test_success_clears_last_error(mock_send, processor, notification):
    notification.lastError = "previous error"
    mock_send.return_value = _response("Success", "[email] accepted for delivery")

    processor.send_one(notification)

    assert notification.status == SENT
    assert notification.lastError is None


@patch("processor.send_email")
def test_temporary_failure_maps_to_retry_pending(mock_send, processor, notification):
    mock_send.return_value = _response("TemporaryFailure", "[email] temporary outage")

    processor.send_one(notification)

    assert notification.status == RETRY_PENDING
    assert notification.lastError == "[email] temporary outage"


@patch("processor.send_email")
def test_permanent_failure_maps_to_failed(mock_send, processor, notification):
    mock_send.return_value = _response("PermanentFailure", "[email] address rejected")

    processor.send_one(notification)

    assert notification.status == FAILED
    assert notification.lastError == "[email] address rejected"


@patch("processor.send_email")
def test_invalid_request_maps_to_failed(mock_send, processor, notification):
    mock_send.return_value = _response("InvalidRequest", "[email] invalid address")

    processor.send_one(notification)

    assert notification.status == FAILED
    assert notification.lastError == "[email] invalid address"


@patch("processor.send_email")
def test_send_increments_attempts_and_sets_processing_first(mock_send, processor, notification):
    mock_send.return_value = _response("Success", "[email] ok")

    processor.send_one(notification)

    assert notification.attempts == 1
    assert notification.lastAttemptAt is not None
