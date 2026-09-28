"""GET /conversation/{id} — retrieve turn history for a session.

Conversation state lives in Redis (fast, ephemeral, TTL'd). Wiring provided;
the store read is a small TODO.
"""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str) -> dict:
    """Return the message history for a conversation.

    TODO(you): read the turn list from Redis under a namespaced key
    (e.g. conv:{id}). Decide the retention policy (TTL) and the shape you store
    — this also feeds multi-turn context back into retrieval later.
    """
    raise NotImplementedError("Implement conversation history retrieval from Redis.")
