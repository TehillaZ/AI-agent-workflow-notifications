# Codebase Notes

Overview of the **notifications-api-python** project after a full read-through of the repository.

---

## 1. Project Structure

```
notifications-api-python/
├── AGENTS.md              # Agent/contributor guidelines and verification hints
├── README.md              # User-facing install, run, and API docs
├── requirements.txt       # Single dependency: Flask>=3.0
├── .gitignore             # Python cache, venv, egg-info
└── src/
    ├── __init__.py        # Empty package marker
    ├── main.py            # Flask app, HTTP routes, startup
    ├── models.py          # Notification entity and status constants
    ├── storage.py         # In-memory store, CRUD helpers, seed data
    ├── processor.py       # Send-one and send-bulk orchestration
    ├── segmenter.py       # SMS segment counting utility
    └── providers/
        ├── __init__.py    # Empty package marker
        ├── email_provider.py
        ├── push_provider.py
        └── sms_provider.py
```

There is **no** `tests/` directory, no test configuration (pytest, unittest), and no CI configuration files in the repo.

---

## 2. Existing Architecture

The app follows a simple **layered, in-process architecture**:

```
HTTP (Flask routes in main.py)
        │
        ▼
Storage layer (storage.py)          Processor (processor.py)
  - in-memory list                  - send_one / send_all
  - add / get / find / seed               │
        │                                 ▼
        │                         Providers (email / sms / push)
        │                         - simulated delivery with random outcomes
        ▼
Models (models.py) + Segmenter (segmenter.py)
```

### Request flow

| Operation | Path |
|-----------|------|
| Create | `POST /notifications` → `add_notification()` → optionally computes `smsSegments` via `segmenter` |
| List | `GET /notifications` → `get_all()` |
| Get one | `GET /notifications/<id>` → `find_by_id()` |
| Update | `PUT /notifications/<id>` → `find_by_id()` + `setattr` on each JSON field |
| Send one | `POST /notifications/<id>/send` → `NotificationProcessor.send_one()` |
| Send bulk | `POST /notifications/send-bulk` → `NotificationProcessor.send_all()` |

### Design characteristics

- **In-memory state only** — a module-level `notifications` list and `next_id` counter in `storage.py`. Restarting the server resets data to the seeded set.
- **No persistence, auth, or validation layer** — routes assume well-formed JSON; there is no schema validation or error handling for missing fields on create.
- **Single-channel send per notification** — `send_one` uses only `targetChannels[0]`, even when a notification has multiple channels.
- **Bulk send is status-filtered** — `send_all` only processes notifications with status `PENDING`; it does not retry `RETRY_PENDING` or re-send `FAILED`/`SENT`.
- **Providers are stubs** — each provider's `send(req)` validates input, then returns a random success/temporary/permanent failure response. The processor currently **always sets status to `SENT`** after a provider call and stores the response `Message` in `lastError` (naming mismatch: success messages also land in `lastError`).
- **SMS segment calculation** — on create, if any channel is SMS, `min_sms_segments(message)` computes billable segment count using a word-boundary-aware algorithm (160 chars per segment, GSM-7 assumption). This value is stored but not used by the processor or providers.

### Status lifecycle (intended vs. actual)

Constants in `models.py`: `pending`, `processing`, `sent`, `retry_pending`, `failed`.

- Seed data demonstrates multiple statuses (`SENT`, `FAILED`, `RETRY_PENDING`, default `PENDING`).
- At runtime, `send_one` transitions: `PENDING` → `PROCESSING` → `SENT` (or `FAILED` if no channels / unknown channel).
- Provider failure responses (`TemporaryFailure`, `PermanentFailure`) are **not** mapped to `FAILED` or `RETRY_PENDING`; the notification is marked `SENT` regardless.

---

## 3. Main Entities

### Notification (`models.py`)

Plain Python class (not a dataclass or ORM model). Serialized to JSON via `.__dict__` in API responses.

| Field | Type / default | Description |
|-------|----------------|-------------|
| `id` | int | Auto-incremented identifier |
| `targetChannels` | list of dicts | Each dict: `{"type": "email"\|"sms"\|"push", "value": "<address>"}` |
| `message` | str | Notification body |
| `status` | str | One of the status constants; default `pending` |
| `createdAt` | ISO datetime string | Set at creation |
| `attempts` | int | Incremented on each send attempt; default `0` |
| `lastAttemptAt` | ISO string or `None` | Timestamp of last send attempt |
| `lastError` | str or `None` | Last provider message or error text |
| `smsSegments` | int | Computed segment count for SMS; default `0` |

### Channel types

Three supported delivery channels, each with a dedicated provider module exposing a `send(req)` function:

- **email** — recipient must contain `@`
- **sms** — recipient must be at least 7 characters
- **push** — recipient is a device token; must be non-empty

Provider response shape (common across all three):

```python
{
    "Result": "Success" | "TemporaryFailure" | "PermanentFailure" | "InvalidRequest",
    "ErrorCode": "<provider-specific code>",
    "Message": "<human-readable message>"
}
```

### Seed data (`storage.seed()`)

Five sample notifications on startup, covering:

1. Email — already `sent`
2. SMS — `pending`, short invalid-looking number (`"12345"`)
3. Push — `failed`
4. Email + SMS — `pending`
5. SMS + push + email — `retry_pending` with 2 prior attempts

---

## 4. Existing Tests

**There are no automated tests in this repository.**

- No `tests/` or `test_*.py` files
- No pytest, unittest, or coverage configuration
- No test dependencies in `requirements.txt`
- Verification is documented as **manual** only (curl/Postman against running server), per `README.md` and `AGENTS.md`

Suggested manual checks from project docs:

- `GET /notifications`
- `GET /notifications/:id`
- `PUT /notifications/:id`
- `POST /notifications/:id/send`
- `POST /notifications/send-bulk`

---

## 5. How the Application Runs

### Prerequisites

- Python 3 (version not pinned in repo)
- Flask 3.x (`pip install -r requirements.txt`)

Optional: virtual environment (`.venv` / `venv` — listed in `.gitignore`).

### Startup sequence

1. Run from project root:
   ```bash
   pip install -r requirements.txt
   python src/main.py
   ```
2. `main.py` imports modules using **relative-to-`src/` imports** (e.g. `from storage import ...`), so the script must be executed with `src` on the import path — typically by running `python src/main.py` from the repo root.
3. On import, `seed()` clears and repopulates in-memory notifications.
4. A `NotificationProcessor` instance is created.
5. Flask dev server starts on **port 3000** (`app.run(port=3000)`).

### API surface

| Method | Endpoint | Behavior |
|--------|----------|----------|
| POST | `/notifications` | Create notification from JSON body `{targetChannels, message}` |
| GET | `/notifications` | List all notifications |
| GET | `/notifications/<id>` | Get one; 404 if missing |
| PUT | `/notifications/<id>` | Partial update via JSON keys; 404 if missing |
| POST | `/notifications/<id>/send` | Send single notification; 404 if missing |
| POST | `/notifications/send-bulk` | Send all `pending` notifications; returns full list |

### Runtime behavior notes

- **Debug mode** is Flask default when using `app.run()` without `debug=False`.
- **State is ephemeral** — restart restores seed data; user-created notifications are lost.
- **No graceful shutdown or background workers** — sends are synchronous within the HTTP request.
- **No `banana_count()` markers** present in any source file yet (mentioned in `AGENTS.md` as an edit tag for tooling).

---

## Quick Reference: Module Responsibilities

| Module | Role |
|--------|------|
| `main.py` | HTTP entry point, route definitions, wires storage + processor |
| `storage.py` | In-memory CRUD, ID generation, seed data, SMS segment hook on create |
| `processor.py` | Send orchestration, status/attempt tracking, provider dispatch |
| `models.py` | `Notification` class and status string constants |
| `segmenter.py` | Word-aware minimum SMS segment calculator |
| `providers/*.py` | Simulated third-party delivery with probabilistic outcomes |
