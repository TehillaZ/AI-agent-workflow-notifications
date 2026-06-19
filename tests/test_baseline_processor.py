"""Phase 0 baseline: documents current processor behavior before Phase 1 fixes.

These tests assert the *existing* bugs so Phase 1 TDD can flip expectations.
"""

from unittest.mock import patch

from models import SENT


def _provider_response(result, message="[test] message", error_code="TEST_CODE"):
    return {
        "Result": result,
        "ErrorCode": error_code,
        "Message": message,
    }


@patch("processor.send_email")
def test_temporary_failure_currently_marked_sent(mock_send, processor, notification):
    """Baseline: provider TemporaryFailure is ignored; status becomes sent."""
    mock_send.return_value = _provider_response(
        "TemporaryFailure", "[email] temporary outage"
    )

    processor.send_one(notification)

    assert notification.status == SENT
    assert notification.lastError == "[email] temporary outage"


@patch("processor.send_email")
def test_permanent_failure_currently_marked_sent(mock_send, processor, notification):
    """Baseline: provider PermanentFailure is ignored; status becomes sent."""
    mock_send.return_value = _provider_response(
        "PermanentFailure", "[email] address rejected"
    )

    processor.send_one(notification)

    assert notification.status == SENT
