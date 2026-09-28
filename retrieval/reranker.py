"""Cross-encoder reranking: precision pass over the fused candidate set.

Retrieval (bi-encoder / BM25) optimizes recall cheaply over the whole corpus.
A cross-encoder reads (query, chunk) *together* and scores relevance far more
accurately — but it's expensive, so you only run it on the ~20-50 candidates
that survived fusion. That two-stage shape (cheap recall -> expensive precision)
is a genuinely important production pattern; make sure you can explain it.

Model loading is glue (provided). The one judgment call — how many candidates to
rerank and how many to keep — is left to you.
"""
from __future__ import annotations

from functools import lru_cache

from config.settings import settings
from retrieval.types import RetrievedChunk


@lru_cache
def _cross_encoder():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(settings.reranker_model)


def rerank(query: str, candidates: list[RetrievedChunk], top_n: int = 5) -> list[RetrievedChunk]:
    """Re-score candidates with the cross-encoder and return the top_n.

    Loading + scoring is provided; TODO(you): decide the candidate window
    (rerank all? top 30?) and the latency budget — this is the single most
    expensive step in the retrieval path, so measure it in Phase 7.
    """
    if not candidates:
        return []
    model = _cross_encoder()
    pairs = [(query, c.content) for c in candidates]
    scores = model.predict(pairs)
    for c, s in zip(candidates, scores, strict=True):
        c.score = float(s)
        c.source = "reranked"
    ranked = sorted(candidates, key=lambda c: c.score, reverse=True)
    return ranked[:top_n]
