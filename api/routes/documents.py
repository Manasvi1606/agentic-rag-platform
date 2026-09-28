"""Document CRUD — ingest and inspect the corpus.

    POST /documents   -> ingest (parse -> chunk -> embed -> index)
    GET  /documents   -> list ingested documents

Wiring is provided; the handler bodies call your ingestion pipeline.
"""
from __future__ import annotations

from fastapi import APIRouter

from api.schemas import DocumentIn, DocumentOut

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentOut)
async def ingest_document(doc: DocumentIn) -> DocumentOut:
    """Run the ingestion pipeline for one source.

    TODO(you): parse(doc.source_uri) -> chunk_document -> index_document, then
    return the resulting DocumentOut. All three pieces exist in ingestion/;
    this handler just orchestrates them.

    SECURITY TODO: if source_uri can be a path/URL from the caller, validate it
    (allowed schemes, no local file traversal, size limits) before fetching —
    this is a classic SSRF / path-traversal surface.
    """
    raise NotImplementedError("Wire ingestion pipeline into the endpoint.")


@router.get("", response_model=list[DocumentOut])
async def list_documents() -> list[DocumentOut]:
    # TODO(you): query Postgres for documents + chunk counts.
    raise NotImplementedError("Implement document listing.")
