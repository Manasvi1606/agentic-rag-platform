"""Smoke tests — confirm the skeleton is wired together and imports cleanly.

These pass on the empty skeleton. As you implement each module, add real unit
tests next to these (e.g. test_rrf.py for the fusion math — a great first thing
to test-drive, since RRF has a clean, checkable definition).
"""
from __future__ import annotations

import importlib

import pytest

MODULES = [
    "config.settings",
    "database.models",
    "ingestion.parser",
    "ingestion.chunker",
    "ingestion.indexer",
    "retrieval.types",
    "retrieval.embeddings",
    "retrieval.hybrid_search",
    "retrieval.reranker",
    "retrieval.self_rag",
    "agents.state",
    "agents.router",
    "agents.graph",
    "api.schemas",
]


@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module: str) -> None:
    """Every module should import without side effects."""
    importlib.import_module(module)


def test_settings_loads() -> None:
    from config.settings import settings

    assert settings.postgres_dsn.startswith("postgresql://")


def test_rrf_is_defined_but_unimplemented() -> None:
    """Placeholder: replace with a real RRF correctness test once you implement it."""
    from retrieval.hybrid_search import reciprocal_rank_fusion

    with pytest.raises(NotImplementedError):
        reciprocal_rank_fusion([])
