"""Web-search branch — for questions the corpus can't answer (fresh/external).

Demonstrates that the agent knows the limits of its own knowledge base and can
reach outside it. Mostly glue; the search-provider call and result-shaping are
small TODOs.
"""
from __future__ import annotations

from agents.state import AgentState
from config.settings import settings
from retrieval.types import RetrievedChunk


def run_web(state: AgentState) -> AgentState:
    """Search the web, wrap results as RetrievedChunk, hand off to generation.

    TODO(you): call a search API (Tavily / Brave / SerpAPI — key in
    WEB_SEARCH_API_KEY), take the top results, and map them into RetrievedChunk
    with source="web" so the downstream generator treats them like any other
    context. Decision: do you fetch & chunk full pages, or trust snippets?
    """
    _ = settings.web_search_api_key  # provided; use it
    _ = RetrievedChunk
    raise NotImplementedError("Implement web search tool.")
