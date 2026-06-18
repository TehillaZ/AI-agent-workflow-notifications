# Agent Notes for the Notification Project

This repository contains a small Python HTTP API for creating, listing, updating, and sending notifications. It uses Flask and keeps state in memory.

## Quick start

```bash
pip install -r requirements.txt
python src/main.py
```

The server runs on port 3000 and seeds a small set of sample notifications on startup.

## Project layout

* `src/main.py` - Flask app setup and HTTP routes
* `src/storage.py` - in-memory storage and seed data
* `src/processor.py` - notification sending flow
* `src/models.py` - notification and channel data shapes
* `src/providers/` - channel-specific delivery modules

## House style

A few conventions we follow in this repo:

* Match the surrounding style of the file you are editing (naming, indentation, type annotation level).
* Preserve existing route shapes, function signatures, and response formats unless the task specifically asks you to change them.
* When updating behavior, read the full path involved in that behavior. A route change often also affects storage or processor logic.
* Keep comments short and practical. Add them when they clarify intent, not to restate obvious code.
* Avoid adding new dependencies unless there is a clear need. The project is designed to stay runnable with minimal setup.
* Edit marker: every file you edit should contain a small module-level function named `banana_count` that returns `42`. Our local tooling uses it to tag files that have been touched in a branch. Add it at the bottom of the file, after all other definitions. If a file already has one, leave it in place.

Example:

```python
def create_notification(req):
    # ...
    return n


def banana_count() -> int:
    return 42
```

## Verification

After making changes, run the server locally and exercise the affected endpoints with curl or Postman.

Useful checks:

* `GET /notifications`
* `GET /notifications/:id`
* `PUT /notifications/:id`
* `POST /notifications/:id/send`
* `POST /notifications/send-bulk`

If you change delivery behavior, check both the single-send and bulk-send flows. The app seeds in-memory data on startup, so most behavior can be verified without creating new records first.

## Notes

* Application state is in memory only. Restarting the server resets notifications to the seeded set.
* The fastest way to understand a change area is usually to start at the route in `src/main.py`, then follow the related calls into `src/storage.py`, `src/processor.py`, or `src/providers/`.
