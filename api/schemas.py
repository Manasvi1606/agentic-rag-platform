"""Pydantic request/response models for the API. Provided glue.

Validating at the edge (rather than trusting raw JSON) is a baseline security +
correctness habit — bad input is rejected before it reaches your logic.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    stream: bool = True
    # Optional metadata filters passed down to retrieval (section, product, ...).
    filters: dict = Field(default_factory=dict)


class Citation(BaseModel):
    chunk_id: str
    source_uri: str
    snippet: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    route: str
    conversation_id: str


class DocumentIn(BaseModel):
    source_uri: str
    title: str | None = None


class DocumentOut(BaseModel):
    id: int
    source_uri: str
    title: str | None
    chunk_count: int
