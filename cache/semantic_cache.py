"""Semantic cache — return a cached answer when a *similar* (not identical)
query has been seen before.

A plain key-value cache only hits on exact string matches, which is nearly
useless for natural-language queries ("What's our refund policy?" vs. "how do
refunds work?"). A semantic cache embeds the query and hits when an existing
entry is within a similarity threshold. Getting this right is a real production
skill — and getting it *wrong* (threshold too loose) serves confidently wrong
answers, so the cache-key/threshold design is deliberately YOURS.
"""
from __future__ import annotations

from dataclasses import dataclass

from retrieval.embeddings import embed_query


@dataclass
class CacheHit:
    answer: str
    similarity: float
    original_query: str


def get(query: str, *, threshold: float = 0.95) -> CacheHit | None:
    """Look up a semantically-similar cached answer.

    TODO(you) — the core design decisions:
      - HOW to store/search vectors in Redis: RediSearch VSS? A sorted set of
        recent query embeddings you scan? (Trade recall vs. simplicity.)
      - The THRESHOLD: too high -> few hits; too low -> wrong answers served.
        This should be tuned against your RAGAS set, not guessed.
      - INVALIDATION: when a document is re-ingested, cached answers derived
        from it may be stale. How do you expire them? (TTL? tag by doc id?)
        Cache invalidation is famously hard — reason about it explicitly.
    """
    _ = embed_query  # provided; embed the query to compare
    raise NotImplementedError("Implement semantic cache lookup (design the key + threshold).")


def set(query: str, answer: str) -> None:
    """Store a query embedding -> answer. TODO(you): persist to Redis with a TTL
    and whatever tagging your invalidation strategy needs."""
    raise NotImplementedError("Implement semantic cache write.")
