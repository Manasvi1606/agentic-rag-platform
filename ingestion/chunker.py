"""Chunking: ParsedDoc -> list of retrievable chunks.

This is one of the highest-leverage decisions in the whole system, so it's
deliberately left as YOUR 20%. The `Chunk` dataclass and the interface are
provided; the splitting strategy is not.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ingestion.parser import ParsedDoc


@dataclass
class Chunk:
    content: str
    metadata: dict = field(default_factory=dict)


def chunk_document(doc: ParsedDoc, *, chunk_size: int = 512, overlap: int = 64) -> list[Chunk]:
    """Split a document into overlapping chunks.

    TODO(you): implement a strategy and be ready to justify it. Options, roughly
    increasing in sophistication:
      1. Fixed-size by tokens with overlap (simplest; start here to get a baseline).
      2. Recursive/structural splitting on paragraphs & headings.
      3. Semantic chunking (split where embedding similarity drops).

    Things to reason about in your design doc:
      - Token vs. character sizing (use the embedding model's tokenizer).
      - Why overlap matters (context bleeding across boundaries).
      - Carry doc metadata (source_uri, page, section) onto every chunk so you
        can do metadata filtering and citations later.

    Measure the impact: chunking is one of the variables your RAGAS eval in
    Phase 5 should A/B. Don't guess — let the numbers pick the strategy.
    """
    raise NotImplementedError("Implement chunking — start with fixed-size+overlap, then iterate.")
