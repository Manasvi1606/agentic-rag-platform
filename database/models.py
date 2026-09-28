"""SQLAlchemy models — the structured side of the platform.

Two roles:
  1. `documents` / `chunks` back the RAG store (chunk text + pgvector embedding).
  2. A structured business table (`orders` here as a placeholder) gives the
     SQL agent something real to query, so query-routing has a genuine choice
     between structured and unstructured data.

TODO (Phase 1): finalize the embedding dimension to match your EMBEDDING_MODEL
(bge-small = 384). It must match the pgvector column and the index.
"""
from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

EMBEDDING_DIM = 384  # bge-small-en-v1.5; change if you swap models


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_uri: Mapped[str] = mapped_column(String(1024))
    title: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    content: Mapped[str] = mapped_column(Text)
    # Free-form metadata for filtering (section, page, product, date, ...).
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))

    document: Mapped["Document"] = relationship(back_populates="chunks")


# HNSW index for approximate NN search. IVFFlat is the other option — part of
# your Phase 1 design writeup should be *why* you picked one (build time vs.
# recall vs. memory). Left here as the default; tune m / ef_construction later.
Index(
    "ix_chunks_embedding_hnsw",
    Chunk.embedding,
    postgresql_using="hnsw",
    postgresql_with={"m": 16, "ef_construction": 64},
    postgresql_ops={"embedding": "vector_cosine_ops"},
)
