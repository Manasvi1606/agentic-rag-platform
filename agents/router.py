"""Query router — the first decision the agent makes.

Given a query, decide which tool(s) can answer it: unstructured RAG, structured
SQL, or live web search. This routing decision is the essence of \"agentic\" RAG
(vs. always-retrieve RAG), so the decision logic is YOURS.
"""
from __future__ import annotations

from agents.state import AgentState, Route


def route_query(state: AgentState) -> AgentState:
    """Classify the query and set state[\"route\"].

    TODO(you): implement the classifier. Approaches to weigh:
      - LLM function-calling / structured output (flexible, most common in prod).
      - Few-shot classifier prompt returning one of {vector, sql, web}.
      - Rules/keywords as a cheap first pass (dates & aggregations -> sql).

    Design questions to answer:
      - What happens on low confidence? (Fallback to vector? Ask to clarify?)
      - Do you ever route to MORE than one tool and merge? (Real systems do.)
      - How do you evaluate routing accuracy? (Build a small labeled set.)
    """
    raise NotImplementedError("Implement query routing (vector | sql | web).")


def decide_next(state: AgentState) -> Route:
    """Conditional edge for LangGraph — reads the route the node set. (Glue.)"""
    return state["route"]
