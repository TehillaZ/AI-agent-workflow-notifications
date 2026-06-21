# Agent Notes for the Notification Project

This repository contains a small Python HTTP API for creating, listing, updating, and sending notifications. It uses Flask and keeps state in memory.

## Quick start

```bash
py -m pip install -r requirements.txt
py src/main.py
```

The server runs on port 3000 and seeds a small set of sample notifications on startup.

## Additional House Rules

### Package management

* Install dependencies using:

```bash
py -m pip install -r requirements.txt
```

* Keep `requirements.txt` updated when adding new dependencies.
* Do not introduce new packages unless necessary for the task.

### Testing and verification

* Start the application locally before submitting changes.
* Verify modified functionality using the relevant API endpoints.
* For bug fixes, reproduce the issue before implementing a fix when possible.
* Do not mark work as complete without performing at least one manual verification.

### Git and commit style

* Make small, focused commits.
* Use clear commit messages describing the change.

Examples:

```text
feat: add bulk notification validation
fix: prevent sending archived notifications
refactor: simplify provider selection logic
docs: update AGENTS instructions
```

* Avoid mixing unrelated changes in the same commit.

### Ask before

Ask for approval before:

* Adding new third-party dependencies.
* Changing API response formats.
* Renaming public routes or endpoints.
* Modifying project structure significantly.
* Deleting existing functionality.
* Introducing persistent storage instead of in-memory storage.
* Changing seeded sample data in a way that affects existing tests.
* pushing code to github or make branches.

### Development guidelines

* Prefer simple solutions over complex abstractions.
* Reuse existing storage and processor logic before creating new modules.
* Follow the existing project structure unless a task explicitly requires otherwise.
* Keep functions focused on a single responsibility.
* Maintain backward compatibility for existing API consumers whenever possible.


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
