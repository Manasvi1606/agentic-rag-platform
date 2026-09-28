"""Hybrid search: combine sparse (BM25) and dense (vector) retrieval.

This is the heart of Phase 2 and a marquee talking point for interviews, so the
retrieval calls are stubbed and the FUSION MATH is left entirely to you.

Why hybrid at all (have this answer ready):
  - Dense retrieval captures meaning but misses exact tokens — acronyms, error
    codes, product SKUs, rare names.
  - BM25 nails exact terms but is blind to paraphrase.
  - Fusing them beats either alone on most enterprise corpora.
"""
from __future__ import annotations

from config.settings import settings
from retrieval.embeddings import embed_query
from retrieval.types import RetrievedChunk


def sparse_search(query: str, k: int = 20, filters: dict | None = None) -> list[RetrievedChunk]:
    """BM25 over OpenSearch's analyzed text field.

    TODO(you): issue a `match` query against OPENSEARCH_INDEX, apply metadata
    `filters` as a bool/filter clause, map hits -> RetrievedChunk(source="sparse").
    """
    raise NotImplementedError("Implement BM25 search against OpenSearch.")


def dense_search(query: str, k: int = 20, filters: dict | None = None) -> list[RetrievedChunk]:
    """Vector kNN search.

    You can run this against pgvector OR OpenSearch's knn_vector field — part of
    your design writeup is choosing which is the source of truth and why.
    TODO(you): embed the query (embed_query is provided), run kNN, apply filters,
    map hits -> RetrievedChunk(source="dense").
    """
    _ = embed_query  # provided; use it
    raise NotImplementedError("Implement dense kNN search.")


def reciprocal_rank_fusion(
    result_lists: list[list[RetrievedChunk]],
    *,
    k: int = 60,
) -> list[RetrievedChunk]:
    """Fuse ranked lists into one.

    THIS IS THE CORE ALGORITHM — implement it yourself. RRF scores each doc by
    sum over lists of 1 / (k + rank), where rank is its 1-based position in that
    list. The constant k (default 60 in the literature) damps the influence of
    top ranks. Why RRF over naive score-normalization: it's rank-based, so you
    don't have to reconcile BM25's unbounded scores with cosine's [-1, 1].

    Return chunks sorted by fused score, deduped by chunk_id, source="fused".
    Write it from the definition above before looking anything up.
    """
    raise NotImplementedError("Implement reciprocal rank fusion from the definition.")


def hybrid_search(query: str, k: int = 10, filters: dict | None = None) -> list[RetrievedChunk]:
    """Top-level entry: run both retrievers, fuse, return top-k. (Glue provided.)"""
    sparse = sparse_search(query, filters=filters)
    dense = dense_search(query, filters=filters)
    fused = reciprocal_rank_fusion([sparse, dense])
    return fused[:k]


# Optional: point EMBEDDING dims / index names back at config so nothing is hardcoded.
_INDEX = settings.opensearch_index
