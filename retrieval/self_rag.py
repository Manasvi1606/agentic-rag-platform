"""Self-RAG: don't trust the first retrieval blindly.

Phase 4. This is conceptually the most interesting module in the repo and the
one that best separates your project from a tutorial, so it's YOURS to build.
The control flow is scaffolded as an explicit loop (easier to reason about and
debug than burying it in the agent graph); the three judgment nodes are TODO.

The core idea: retrieve -> grade the evidence -> if weak, reformulate & retry;
only generate once you have good enough evidence, then optionally check the
answer is grounded in it.
"""
from __future__ import annotations

from dataclasses import dataclass

from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import rerank
from retrieval.types import RetrievedChunk


@dataclass
class SelfRAGResult:
    answer: str
    context: list[RetrievedChunk]
    iterations: int
    grounded: bool


def grade_relevance(query: str, chunks: list[RetrievedChunk]) -> bool:
    """Are these chunks good enough to answer the query?

    TODO(you): implement a grader. Options to weigh in your design doc:
      - LLM-as-judge (flexible, slow, costs a call).
      - Score threshold on the reranker (cheap, blunt).
      - A small trained classifier (fast, needs data).
    Return True to proceed to generation, False to trigger a retry.
    """
    raise NotImplementedError("Implement retrieval-quality grading.")


def reformulate_query(query: str, chunks: list[RetrievedChunk]) -> str:
    """Rewrite the query when retrieval was weak.

    TODO(you): use what the weak chunks reveal about the miss (wrong vocabulary?
    too broad?) to produce a better query. This is where a retry actually helps
    rather than just repeating the same failing search.
    """
    raise NotImplementedError("Implement query reformulation.")


def check_grounded(answer: str, context: list[RetrievedChunk]) -> bool:
    """Optional final gate: is every claim in `answer` supported by `context`?

    TODO(you): this is your hallucination guard. Even a simple LLM-based
    entailment check here is a strong signal — and it connects directly to the
    faithfulness metric you'll measure with RAGAS in Phase 5.
    """
    raise NotImplementedError("Implement groundedness / faithfulness check.")


def self_rag_answer(query: str, *, max_iterations: int = 3) -> SelfRAGResult:
    """The self-correcting loop. Control flow provided; the nodes are yours."""
    q = query
    for i in range(1, max_iterations + 1):
        candidates = hybrid_search(q)
        context = rerank(q, candidates)

        if grade_relevance(query, context):
            answer = _generate(query, context)  # TODO: see _generate below
            grounded = check_grounded(answer, context)
            if grounded or i == max_iterations:
                return SelfRAGResult(answer, context, i, grounded)
            # not grounded -> loop and try to gather better evidence
        q = reformulate_query(query, context)

    # Exhausted retries — return best effort. TODO(you): decide the fallback
    # behavior (abstain? answer with a low-confidence flag?). Abstaining is often
    # the right production call; think about it.
    return SelfRAGResult(_generate(query, context), context, max_iterations, False)


def _generate(query: str, context: list[RetrievedChunk]) -> str:
    # TODO(you): build the grounded prompt (query + numbered context) and call
    # the LLM via the serving client (serving/ + config LLM_BASE_URL). Insist on
    # citations so check_grounded has something to verify.
    raise NotImplementedError("Implement grounded generation against the served LLM.")
