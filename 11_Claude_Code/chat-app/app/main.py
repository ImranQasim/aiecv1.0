from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agent import generate_reply

STATIC_DIR = Path(__file__).parent.parent / "static"

app = FastAPI(title="chat-app")


class ChatRequest(BaseModel):
    message: str
    conversation_id: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    reply = await generate_reply(request.message, request.conversation_id)
    return ChatResponse(reply=reply)


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
