"""Reply generation.

This module is the seam between the web app and whatever produces replies.
Nothing outside of it knows how a reply is made.
"""

import logging
import os
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, SystemMessage, query

logger = logging.getLogger(__name__)

DEFAULT_REPO_PATH = Path(__file__).parent.parent

SYSTEM_PROMPT = (
    "You are a codebase concierge for this repository. Answer questions "
    "about the code concisely, and cite file paths when relevant."
)

FALLBACK_REPLY = "Sorry, I couldn't come up with a reply just now. Please try again."

# conversation_id -> SDK session_id. In-memory only: resets on process restart.
_conversation_sessions: dict[str, str] = {}


async def _run_query(message: str, options: ClaudeAgentOptions) -> tuple[str, str | None]:
    """Run one query turn, returning (reply, session_id). Raises on error/no result."""
    session_id: str | None = None
    async for msg in query(prompt=message, options=options):
        if isinstance(msg, SystemMessage) and msg.subtype == "init":
            session_id = msg.data.get("session_id")
        elif isinstance(msg, ResultMessage):
            if msg.is_error or not msg.result:
                raise RuntimeError(f"agent returned an error result: {msg.subtype}")
            return msg.result, session_id or msg.session_id

    raise RuntimeError("agent produced no result message")


async def generate_reply(message: str, conversation_id: str) -> str:
    """Produce the assistant's reply to a user message via the Claude Agent SDK."""
    common_options = {
        "system_prompt": SYSTEM_PROMPT,
        "allowed_tools": ["Read", "Glob", "Grep"],
        "cwd": os.environ.get("TARGET_REPO_PATH", str(DEFAULT_REPO_PATH)),
        "max_turns": 25,
    }

    resume_id = _conversation_sessions.get(conversation_id)
    if resume_id:
        try:
            reply, session_id = await _run_query(
                message, ClaudeAgentOptions(resume=resume_id, **common_options)
            )
            _conversation_sessions[conversation_id] = session_id or resume_id
            return reply
        except Exception:
            logger.warning(
                "resume failed for conversation_id=%s, starting fresh session",
                conversation_id,
                exc_info=True,
            )

    try:
        reply, session_id = await _run_query(message, ClaudeAgentOptions(**common_options))
        if session_id:
            _conversation_sessions[conversation_id] = session_id
        return reply
    except Exception:
        logger.exception("generate_reply failed for conversation_id=%s", conversation_id)
        return FALLBACK_REPLY
