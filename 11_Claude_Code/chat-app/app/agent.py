"""Reply generation.

This module is the seam between the web app and whatever produces replies.
Nothing outside of it knows how a reply is made.
"""

import logging
import os
import subprocess
from pathlib import Path

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    create_sdk_mcp_server,
    query,
    tool,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    logger.addHandler(_handler)
    logger.propagate = False

DEFAULT_REPO_PATH = Path(__file__).parent.parent

SYSTEM_PROMPT = (
    "You are a codebase concierge for this repository. Answer questions "
    "about the code concisely, and cite file paths when relevant."
)

FALLBACK_REPLY = "Sorry, I couldn't come up with a reply just now. Please try again."

# conversation_id -> SDK session_id. In-memory only: resets on process restart.
_conversation_sessions: dict[str, str] = {}


def _target_repo_path() -> Path:
    return Path(os.environ.get("TARGET_REPO_PATH", str(DEFAULT_REPO_PATH)))


@tool("count_lines", "Count the number of lines in a file", {"file_path": str})
async def count_lines(args: dict) -> dict:
    file_path = args["file_path"]
    logger.info("tool: count_lines file_path=%r", file_path)

    repo_path = _target_repo_path().resolve()
    path = Path(file_path)
    resolved = path if path.is_absolute() else repo_path / path
    resolved = resolved.resolve()

    if repo_path not in resolved.parents and resolved != repo_path:
        return {
            "content": [
                {"type": "text", "text": f"{file_path} is outside the repository."}
            ],
            "is_error": True,
        }

    try:
        with open(resolved) as f:
            count = sum(1 for _ in f)
    except OSError as e:
        return {
            "content": [{"type": "text", "text": f"Could not read {file_path}: {e}"}],
            "is_error": True,
        }

    return {"content": [{"type": "text", "text": str(count)}]}


@tool(
    "git_log",
    "Get the last n commit hashes and subject lines from the repo's git log",
    {
        "type": "object",
        "properties": {
            "n": {
                "type": "integer",
                "description": "Number of commits to show (default 5, max 20)",
            }
        },
    },
)
async def git_log(args: dict) -> dict:
    try:
        n = int(args.get("n", 5))
    except (TypeError, ValueError):
        n = 5
    n = max(1, min(n, 20))
    logger.info("tool: git_log n=%d", n)

    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--pretty=format:%h %s"],
            cwd=_target_repo_path(),
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return {
            "content": [{"type": "text", "text": f"Could not run git log: {e}"}],
            "is_error": True,
        }

    if result.returncode != 0:
        return {
            "content": [{"type": "text", "text": "This directory isn't a git repository."}]
        }

    return {"content": [{"type": "text", "text": result.stdout or "No commits found."}]}


_CONCIERGE_SERVER = create_sdk_mcp_server(name="concierge", tools=[count_lines, git_log])


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
    allowed_tool_names = [
        "Read",
        "Glob",
        "Grep",
        "mcp__concierge__count_lines",
        "mcp__concierge__git_log",
    ]
    common_options = {
        "system_prompt": SYSTEM_PROMPT,
        "tools": allowed_tool_names,
        "allowed_tools": allowed_tool_names,
        "mcp_servers": {"concierge": _CONCIERGE_SERVER},
        "cwd": str(_target_repo_path()),
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
