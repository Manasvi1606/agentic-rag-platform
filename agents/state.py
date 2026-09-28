"""Shared LangGraph state passed between nodes.

LangGraph is a state machine: each node receives the state, returns a partial
update, and the graph merges it. Defining the state explicitly (rather than
passing loose kwargs) is what makes an agent debuggable — you can log the state
at every hop. Provided in full so you can focus on the routing logic.
"""
from __future__ import annotations

from typing import Literal, TypedDict

from retrieval.types import RetrievedChunk

Route = Literal["vector", "sql", "web"]


class AgentState(TypedDict, total=False):
    query: str
    route: Route                      # set by the router node
    context: list[RetrievedChunk]     # from vector/web retrieval
    sql_result: list[dict]            # from the SQL agent
    answer: str
    # Scratch for tracing/debugging — log this between nodes.
    trace: list[str]
