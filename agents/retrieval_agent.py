"""Vector/RAG branch — wraps the Self-RAG pipeline as a graph node. (Glue.)

Almost complete: it just adapts self_rag into the AgentState contract. The real
work lives in retrieval/self_rag.py.
"""
from __future__ import annotations

from agents.state import AgentState
from retrieval.self_rag import self_rag_answer


def run_retrieval(state: AgentState) -> AgentState:
    result = self_rag_answer(state["query"])
    return {
        **state,
        "context": result.context,
        "answer": result.answer,
        "trace": [*state.get("trace", []), f"retrieval: {result.iterations} iter"],
    }
