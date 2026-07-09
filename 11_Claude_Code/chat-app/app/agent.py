"""Reply generation.

This module is the seam between the web app and whatever produces replies.
Nothing outside of it knows how a reply is made.
"""

import logging
import os
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

logger = logging.getLogger(__name__)

DEFAULT_REPO_PATH = Path(__file__).parent.parent

SYSTEM_PROMPT = (
    "You are a codebase concierge for this repository. Answer questions "
    "about the code concisely, and cite file paths when relevant."
)

FALLBACK_REPLY = "Sorry, I couldn't come up with a reply just now. Please try again."


async def generate_reply(message: str, conversation_id: str) -> str:
    """Produce the assistant's reply to a user message via the Claude Agent SDK."""
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        allowed_tools=["Read", "Glob", "Grep"],
        cwd=os.environ.get("TARGET_REPO_PATH", str(DEFAULT_REPO_PATH)),
        max_turns=25,
    )

    try:
        async for msg in query(prompt=message, options=options):
            if isinstance(msg, ResultMessage):
                if msg.is_error or not msg.result:
                    return FALLBACK_REPLY
                return msg.result
    except Exception:
        logger.exception("generate_reply failed for conversation_id=%s", conversation_id)
        return FALLBACK_REPLY

    return FALLBACK_REPLY
