"""LangGraph wiring — assembles the nodes into the routed agent.

This is the glue that turns your individual node functions into the diagram from
your Phase 3 design:

        query -> router --(vector)--> retrieval --\\
                        --(sql)-----> sql -------->  answer_agent -> END
                        --(web)-----> web --------/

The graph structure is provided and complete; every node it calls is either done
(retrieval_agent) or a TODO you'll fill in (router, sql, web, answer). Once those
land, this compiles and runs unchanged.
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.retrieval_agent import run_retrieval
from agents.router import decide_next, route_query
from agents.sql_agent import run_sql
from agents.state import AgentState
from agents.web_agent import run_web


def answer_agent(state: AgentState) -> AgentState:
    """Final synthesis node.

    For the vector/web branches the answer may already be set; for SQL you need
    to turn rows into prose. TODO(you): compose the final grounded answer +
    citations here. Keeping synthesis in one node means every branch produces a
    consistently-formatted, cited answer.
    """
    raise NotImplementedError("Implement final answer synthesis across branches.")


def build_graph():
    """Construct and compile the agent graph. (Provided — no edits needed.)"""
    g = StateGraph(AgentState)

    g.add_node("router", route_query)
    g.add_node("vector", run_retrieval)
    g.add_node("sql", run_sql)
    g.add_node("web", run_web)
    g.add_node("answer", answer_agent)

    g.add_edge(START, "router")
    g.add_conditional_edges(
        "router",
        decide_next,
        {"vector": "vector", "sql": "sql", "web": "web"},
    )
    for branch in ("vector", "sql", "web"):
        g.add_edge(branch, "answer")
    g.add_edge("answer", END)

    return g.compile()


# Compiled lazily by the API layer so importing this module stays cheap.
