"""Indexing: chunks -> written to BOTH stores.

The platform is dual-store: pgvector (dense) and OpenSearch (BM25 + dense).
Writing to both is glue and is sketched out for you. The one real decision
flagged below is idempotency — re-ingesting the same document shouldn't create
duplicates.
"""
from __future__ import annotations

from collections.abc import Iterable

from ingestion.chunker import Chunk
from ingestion.parser import ParsedDoc
from retrieval.embeddings import embed_texts


def index_document(doc: ParsedDoc, chunks: Iterable[Chunk]) -> int:
    """Embed chunks and persist them to Postgres and OpenSearch.

    Returns the number of chunks indexed. Orchestration is provided; the store
    writes marked TODO are where you'll actually touch pgvector / OpenSearch.
    """
    chunks = list(chunks)
    if not chunks:
        return 0

    # Embedding is shared by both stores — compute once. (Provided glue.)
    vectors = embed_texts([c.content for c in chunks])

    _write_to_pgvector(doc, chunks, vectors)
    _write_to_opensearch(doc, chunks, vectors)
    return len(chunks)


def _write_to_pgvector(doc: ParsedDoc, chunks: list[Chunk], vectors: list[list[float]]) -> None:
    # TODO(you): upsert Document + Chunk rows (see database/models.py).
    # Idempotency: decide a stable chunk id (e.g. hash of source_uri + ordinal)
    # so re-ingesting updates rather than duplicates. This is a real production
    # concern — think it through rather than letting it slide.
    raise NotImplementedError("Persist chunks + embeddings to pgvector.")


def _write_to_opensearch(doc: ParsedDoc, chunks: list[Chunk], vectors: list[list[float]]) -> None:
    # TODO(you): bulk-index into OpenSearch with both the analyzed text field
    # (for BM25) and a knn_vector field (for dense). The mapping matters —
    # define it once and document it.
    raise NotImplementedError("Bulk-index chunks into OpenSearch (text + knn_vector).")
