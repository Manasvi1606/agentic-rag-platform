"""Document parsing: raw file -> clean text + metadata.

GLUE (provided): dispatch by file type, return a normalized ParsedDoc.
YOUR 20% (TODO): the actual extraction quality — PDFs are where RAG projects
live or die. How you handle tables, headers/footers, and reading order directly
determines retrieval quality downstream. Don't outsource this thinking.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParsedDoc:
    source_uri: str
    text: str
    title: str | None = None
    metadata: dict = field(default_factory=dict)


def parse(path: str | Path) -> ParsedDoc:
    """Route a file to the right extractor based on suffix.

    Provided glue; the extractors themselves are yours to implement.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _parse_pdf(path)
    if suffix in {".txt", ".md"}:
        return _parse_text(path)
    if suffix in {".html", ".htm"}:
        return _parse_html(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def _parse_text(path: Path) -> ParsedDoc:
    text = path.read_text(encoding="utf-8", errors="replace")
    return ParsedDoc(source_uri=str(path), text=text, title=path.stem)


def _parse_pdf(path: Path) -> ParsedDoc:
    # TODO(you): extract text with a real parser (pypdf / pdfplumber / unstructured).
    # Decisions to make and defend in your design doc:
    #   - Do you preserve page numbers in metadata? (needed for citations)
    #   - How do you strip repeated headers/footers?
    #   - Do you keep table structure or flatten it?
    raise NotImplementedError("Implement PDF extraction — this is core Phase 1 work.")


def _parse_html(path: Path) -> ParsedDoc:
    # TODO(you): strip boilerplate/nav, keep main content (e.g. trafilatura / bs4).
    raise NotImplementedError("Implement HTML extraction.")
