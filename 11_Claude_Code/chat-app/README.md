# chat-app

A minimal chat web app: FastAPI backend, plain HTML/CSS/JS frontend, no frontend framework.

Replies are currently **stubbed** — the server echoes your message back. The stub is isolated in
one function so a real agent can drop in later without touching anything else.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Run

```bash
uv sync                                   # one-time: install dependencies
uv run uvicorn app.main:app --reload      # start the server
```

Then open <http://127.0.0.1:8000>.

## API

`POST /api/chat`

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "hello", "conversation_id": "test-1"}'
```

```json
{ "reply": "Echo: hello" }
```

## Replacing the stub

Everything that decides *what the assistant says* lives in one place:

```
app/agent.py  →  generate_reply(message, conversation_id) -> str
```

Replace that function's body with a real agent call. It is already `async`, so it can do network
I/O without any change to the route, the response model, or the frontend.

`conversation_id` is generated per page load by the browser and passed through on every request.
Nothing stores it yet — it's there for the real agent to key conversation history off of.

## Layout

```
app/
  main.py      FastAPI app: GET / and POST /api/chat
  agent.py     the stub — the only file a real agent needs to touch
static/
  index.html   chat UI
  style.css
  app.js       fetch() calls /api/chat, renders both sides
```
