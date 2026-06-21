"""Phase 2: bulk send includes pending and retry_pending notifications."""

from unittest.mock import patch

import storage
from models import FAILED, Notification, PENDING, RETRY_PENDING, SENT


def _success_response():
    return {"Result": "Success", "ErrorCode": "EMAIL_OK", "Message": "[email] ok"}


def _seed_notifications():
    storage.notifications.clear()
    storage.next_id = 5

    pending = Notification(1, [{"type": "email", "value": "pending@example.com"}], "pending msg")
    pending.status = PENDING

    retry = Notification(2, [{"type": "email", "value": "retry@example.com"}], "retry msg")
    retry.status = RETRY_PENDING
    retry.attempts = 2

    sent = Notification(3, [{"type": "email", "value": "sent@example.com"}], "sent msg")
    sent.status = SENT
    sent.attempts = 1

    failed = Notification(4, [{"type": "email", "value": "failed@example.com"}], "failed msg")
    failed.status = FAILED
    failed.attempts = 1

    storage.notifications.extend([pending, retry, sent, failed])
    return pending, retry, sent, failed


@patch("processor.send_email", return_value=_success_response())
def test_send_all_processes_pending_and_retry_pending(mock_send, processor):
    pending, retry, sent, failed = _seed_notifications()

    processor.send_all()

    assert mock_send.call_count == 2
    assert pending.attempts == 1
    assert retry.attempts == 3
    assert sent.attempts == 1
    assert failed.attempts == 1


@patch("processor.send_email", return_value=_success_response())
def test_send_all_skips_sent_and_failed(mock_send, processor):
    _, _, sent, failed = _seed_notifications()

    processor.send_all()

    assert sent.status == SENT
    assert failed.status == FAILED
