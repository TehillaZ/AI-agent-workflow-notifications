from models import PENDING
from processor import NotificationProcessor


def test_notification_fixture(notification):
    assert notification.id == 1
    assert notification.status == PENDING
    assert notification.targetChannels[0]["type"] == "email"


def test_processor_fixture(processor):
    assert isinstance(processor, NotificationProcessor)
