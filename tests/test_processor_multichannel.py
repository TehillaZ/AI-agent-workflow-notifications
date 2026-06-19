"""Phase 3: multi-channel delivery with Option A aggregation."""

from unittest.mock import patch

from models import FAILED, RETRY_PENDING, SENT


def _response(result, message):
    return {"Result": result, "ErrorCode": "TEST", "Message": message}


@patch("processor.send_push")
@patch("processor.send_sms")
@patch("processor.send_email")
def test_all_channels_success(mock_email, mock_sms, mock_push, processor, notification):
    notification.targetChannels = [
        {"type": "email", "value": "a@example.com"},
        {"type": "sms", "value": "+15551234567"},
    ]
    notification.lastError = "old error"
    mock_email.return_value = _response("Success", "[email] ok")
    mock_sms.return_value = _response("Success", "[sms] ok")

    processor.send_one(notification)

    assert mock_email.call_count == 1
    assert mock_sms.call_count == 1
    assert notification.status == SENT
    assert notification.lastError is None


@patch("processor.send_email")
@patch("processor.send_sms")
def test_temporary_failure_takes_priority_over_permanent(mock_sms, mock_email, processor, notification):
    notification.targetChannels = [
        {"type": "email", "value": "a@example.com"},
        {"type": "sms", "value": "+15551234567"},
    ]
    mock_email.return_value = _response("PermanentFailure", "[email] address rejected")
    mock_sms.return_value = _response("TemporaryFailure", "[sms] temporary outage")

    processor.send_one(notification)

    assert notification.status == RETRY_PENDING
    assert notification.lastError == "[email] address rejected; [sms] temporary outage"


@patch("processor.send_email")
@patch("processor.send_sms")
def test_all_permanent_failures_mark_failed(mock_sms, mock_email, processor, notification):
    notification.targetChannels = [
        {"type": "email", "value": "a@example.com"},
        {"type": "sms", "value": "+15551234567"},
    ]
    mock_email.return_value = _response("PermanentFailure", "[email] rejected")
    mock_sms.return_value = _response("InvalidRequest", "[sms] invalid phone")

    processor.send_one(notification)

    assert notification.status == FAILED
    assert notification.lastError == "[email] rejected; [sms] invalid phone"


def test_unknown_channel_type_fails(processor, notification):
    notification.targetChannels = [
        {"type": "email", "value": "a@example.com"},
        {"type": "banana", "value": "x"},
    ]

    with patch("processor.send_email") as mock_email:
        mock_email.return_value = _response("Success", "[email] ok")
        processor.send_one(notification)

    assert notification.status == FAILED
    assert "Unknown channel: banana" in notification.lastError
