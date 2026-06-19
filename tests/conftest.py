import pytest

from models import Notification
from processor import NotificationProcessor


@pytest.fixture
def notification():
    """Fresh pending notification with a single email channel."""
    return Notification(
        1,
        [{"type": "email", "value": "user@example.com"}],
        "Test message",
    )


@pytest.fixture
def processor():
    return NotificationProcessor()


def provider_response(result, message="[test] message", error_code="TEST_CODE"):
    """Build a provider response dict matching the vendor contract."""
    return {
        "Result": result,
        "ErrorCode": error_code,
        "Message": message,
    }
