"""Reply generation.

This module is the seam between the web app and whatever produces replies.
Nothing outside of it knows how a reply is made.
"""


async def generate_reply(message: str, conversation_id: str) -> str:
    """Produce the assistant's reply to a user message.

    STUB: echoes the message back. Replace this body with a real agent call.
    """
    return f"Echo: {message}"
