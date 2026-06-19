from datetime import datetime

import storage
from models import PENDING, PROCESSING, SENT, FAILED, RETRY_PENDING
from providers.email_provider import send as send_email
from providers.sms_provider import send as send_sms
from providers.push_provider import send as send_push


def _classify_result(response):
    result = response["Result"]
    if result == "Success":
        return "success", None
    if result == "TemporaryFailure":
        return "temporary", response["Message"]
    if result in ("PermanentFailure", "InvalidRequest"):
        return "failure", response["Message"]
    return "failure", response.get("Message", "Unknown provider result")


def _aggregate_results(outcomes):
    """Option A: any temporary → retry_pending; else any failure → failed; all success → sent."""
    errors = []
    has_temporary = False
    has_failure = False
    for kind, message in outcomes:
        if kind == "success":
            continue
        if kind == "temporary":
            has_temporary = True
        else:
            has_failure = True
        if message:
            errors.append(message)

    if has_temporary:
        return RETRY_PENDING, "; ".join(errors) if errors else None
    if has_failure:
        return FAILED, "; ".join(errors) if errors else None
    return SENT, None


def _dispatch_channel(target, message):
    # Built per call so tests can patch processor.send_* functions.
    senders = {
        "email": send_email,
        "sms": send_sms,
        "push": send_push,
    }
    send_fn = senders.get(target["type"])
    if send_fn is None:
        return None
    return send_fn({"recipient": target["value"], "message": message})


class NotificationProcessor:
    def send_one(self, n):
        n.status = PROCESSING
        n.attempts += 1
        n.lastAttemptAt = datetime.now().isoformat()

        if not n.targetChannels:
            n.status = FAILED
            n.lastError = "No target channels"
            return

        outcomes = []
        for target in n.targetChannels:
            response = _dispatch_channel(target, n.message)
            if response is None:
                outcomes.append(("failure", f"Unknown channel: {target['type']}"))
                continue
            outcomes.append(_classify_result(response))

        n.status, n.lastError = _aggregate_results(outcomes)

    def send_all(self):
        to_send = [
            n
            for n in storage.get_all()
            if n.status in (PENDING, RETRY_PENDING)
        ]
        for n in to_send:
            self.send_one(n)
