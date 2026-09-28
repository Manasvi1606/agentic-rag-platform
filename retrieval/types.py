"""Shared retrieval types, so every module speaks the same shape."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RetrievedChunk:
    chunk_id: str
    content: str
    score: float
    metadata: dict = field(default_factory=dict)
    # Which retriever produced this (\"dense\" | \"sparse\" | \"fused\" | \"reranked\").
    source: str = ""
