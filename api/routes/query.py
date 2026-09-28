"""POST /query — the main entry point. Runs the agent, optionally streams.

Routing, request validation, and the SSE plumbing are provided glue. The two
TODOs are where you connect to your own logic: the semantic-cache lookup and the
token stream out of the LLM.
"""
from __future__ import annotations

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from api.schemas import QueryRequest, QueryResponse

router = APIRouter(tags=["query"])


@router.post("/query")
async def query(req: QueryRequest):
    """Answer a query, streaming tokens by default (SSE) or returning JSON.

    Flow (glue provided; the marked steps are yours):
      1. Semantic cache lookup — TODO: call cache.semantic_cache.get(...). On a
         hit, return immediately. This is where a lot of your latency/cost win
         comes from, so wire it first.
      2. Run the agent graph (agents.graph.build_graph()). For streaming you'll
         want the graph / LLM client to yield tokens.
      3. Cache the result on the way out — TODO: cache.semantic_cache.set(...).
    """
    if req.stream:
        return EventSourceResponse(_stream_answer(req))
    return await _answer_json(req)


async def _stream_answer(req: QueryRequest):
    # TODO(you): drive the agent and `yield {"data": token}` as tokens arrive.
    # Getting real token streaming (not fake chunking of a finished string) is
    # the interesting part — it depends on the LLM client exposing a stream.
    raise NotImplementedError("Implement SSE token streaming from the agent/LLM.")
    yield  # pragma: no cover  (keeps this an async generator)


async def _answer_json(req: QueryRequest) -> QueryResponse:
    # TODO(you): run the graph to completion and shape the final QueryResponse
    # (answer + citations + route + conversation_id).
    raise NotImplementedError("Implement non-streaming answer path.")
