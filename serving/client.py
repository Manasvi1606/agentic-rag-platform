"""Thin LLM client used everywhere generation happens (self_rag, answer_agent).

Centralizing the LLM call behind one interface means you can swap a hosted API
for your vLLM endpoint by changing config only — nothing else in the codebase
needs to know. Provided as an interface with a small TODO body.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from config.settings import settings


async def complete(prompt: str, *, temperature: float = 0.2, max_tokens: int = 512) -> str:
    """Non-streaming completion.

    TODO(you): call the OpenAI-compatible endpoint at settings.llm_base_url.
    Keep the client creation cheap/reused. This is glue-ish, but writing it
    yourself once cements how the serving layer connects to the app.
    """
    _ = settings.llm_base_url
    raise NotImplementedError("Call the served LLM (OpenAI-compatible /chat/completions).")


async def stream(prompt: str, *, temperature: float = 0.2, max_tokens: int = 512) -> AsyncIterator[str]:
    """Streaming completion — yields tokens as they arrive.

    TODO(you): this is what the SSE endpoint consumes. Real token streaming
    (stream=True on the LLM call) is the point; don't fake it by chunking a
    finished string.
    """
    raise NotImplementedError("Stream tokens from the served LLM.")
    yield  # pragma: no cover  (async generator marker)
