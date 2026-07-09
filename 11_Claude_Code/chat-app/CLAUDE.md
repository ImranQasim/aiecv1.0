# CLAUDE.md

## Project

Minimal chat web app: FastAPI backend + vanilla HTML/CSS/JS frontend. No frontend framework, no
build step, no database. Replies are currently stubbed (echo).

## Commands

```bash
uv sync                                   # install dependencies
uv run uvicorn app.main:app --reload      # start server on 127.0.0.1:8000
```

Verify a change end to end:

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "hello", "conversation_id": "test-1"}'
```

There is no test suite and no linter configured yet.

## Architecture: the seam
- All reply logic lives in ONE function: generate_reply() in app/agent.py.
- /api/chat only validates and delegates. Never put logic in the route.
- The echo stub gets replaced by an Agent SDK query() call. Keep the seam intact.
- conversation_id flows through end-to-end; it will key SDK session resumption.

`app/main.py` holds the whole HTTP surface — `GET /` serves `static/index.html`, `POST /api/chat`
takes `ChatRequest` and returns `ChatResponse`. Static files mount at `/static`.

`static/app.js` generates a `conversationId` per page load and sends it on every request. Nothing
persists it; it exists for a real agent to key conversation history off of. If you add history,
that state belongs behind `generate_reply`, not in the route.

## Conventions

- Python 3.12+, type hints on function signatures. `uv` for everything — never `pip` or `venv`.
- Frontend is a single plain browser script loaded with a `<script>` tag. Don't introduce npm, a
  bundler, or a framework.
- Keep the codebase this small. No speculative abstraction.
