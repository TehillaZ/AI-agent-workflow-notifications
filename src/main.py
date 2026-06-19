from flask import Flask, request, jsonify

from storage import seed, add_notification, get_all, find_by_id, recompute_sms_segments
from processor import NotificationProcessor
from models import SENT, CHANNEL_TYPES

app = Flask(__name__)

ALLOWED_PUT_FIELDS = {"message", "targetChannels"}

seed()

processor = NotificationProcessor()


def _validation_error(message):
    return jsonify({"error": message}), 400


def _validate_channels(channels):
    if not isinstance(channels, list) or not channels:
        return "targetChannels must be a non-empty list"
    for channel in channels:
        if not isinstance(channel, dict):
            return "invalid channel entry"
        if channel.get("type") not in CHANNEL_TYPES:
            return "invalid channel type"
        value = channel.get("value")
        if not isinstance(value, str) or not value.strip():
            return "channel value is required"
    return None


def _validate_create_data(data):
    if data is None:
        return "request body is required"
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return "message is required"
    return _validate_channels(data.get("targetChannels"))


def _validate_put_data(data):
    if data is None:
        return "request body is required"
    if not isinstance(data, dict):
        return "request body is required"
    extra = set(data.keys()) - ALLOWED_PUT_FIELDS
    if extra:
        return f"cannot update fields: {', '.join(sorted(extra))}"
    if "message" in data:
        if not isinstance(data["message"], str) or not data["message"].strip():
            return "message is required"
    if "targetChannels" in data:
        channel_error = _validate_channels(data["targetChannels"])
        if channel_error:
            return channel_error
    if "message" not in data and "targetChannels" not in data:
        return "no valid fields to update"
    return None


@app.route("/notifications", methods=["POST"])
def create():
    data = request.get_json(silent=True)
    error = _validate_create_data(data)
    if error:
        return _validation_error(error)
    n = add_notification(data["targetChannels"], data["message"])
    return jsonify(n.__dict__)


@app.route("/notifications", methods=["GET"])
def list_all():
    return jsonify([n.__dict__ for n in get_all()])


@app.route("/notifications/<int:nid>", methods=["GET"])
def get_one(nid):
    n = find_by_id(nid)
    if not n:
        return jsonify({"error": "not found"}), 404
    return jsonify(n.__dict__)


@app.route("/notifications/<int:nid>", methods=["PUT"])
def update_one(nid):
    n = find_by_id(nid)
    if not n:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True)
    error = _validate_put_data(data)
    if error:
        return _validation_error(error)
    if "message" in data:
        n.message = data["message"]
    if "targetChannels" in data:
        n.targetChannels = data["targetChannels"]
    recompute_sms_segments(n)
    return jsonify(n.__dict__)


@app.route("/notifications/<int:nid>/send", methods=["POST"])
def send_one_route(nid):
    n = find_by_id(nid)
    if not n:
        return jsonify({"error": "not found"}), 404
    if n.status == SENT:
        return jsonify({"error": "notification already sent"}), 409
    processor.send_one(n)
    return jsonify(n.__dict__)


@app.route("/notifications/send-bulk", methods=["POST"])
def send_bulk():
    processor.send_all()
    return jsonify([n.__dict__ for n in get_all()])


if __name__ == "__main__":
    app.run(port=3000, debug=False)
