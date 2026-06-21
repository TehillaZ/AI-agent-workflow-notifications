# Notification delivery API

A small HTTP API that manages and delivers notifications across email, SMS, and push channels.

## Install

```
pip install -r requirements.txt
```

A virtual environment is optional but recommended (`python -m venv .venv` then activate).

## Run

```
python src/main.py
```

Starts the HTTP server on port 3000.

NOTE: The server pre-populates in-memory storage with a few sample notifications on startup.

## Endpoints

### POST /notifications

Create a notification.

```
curl -X POST http://localhost:3000/notifications \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","targetChannels":[{"type":"email","value":"user@example.com"}]}'
```

### GET /notifications

List all notifications.

```
curl http://localhost:3000/notifications
```

### GET /notifications/:id

Fetch a single notification by id. Returns 404 if not found.

```
curl http://localhost:3000/notifications/1
```

### PUT /notifications/:id

Update a notification. Returns 404 if not found.

```
curl -X PUT http://localhost:3000/notifications/1 \
  -H "Content-Type: application/json" \
  -d '{"message":"Updated message"}'
```

### POST /notifications/:id/send

Send a single notification. Returns 404 if not found.

```
curl -X POST http://localhost:3000/notifications/1/send
```

### POST /notifications/send-bulk

Send all pending notifications.

```
curl -X POST http://localhost:3000/notifications/send-bulk
```
