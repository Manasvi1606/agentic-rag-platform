"""Embedding model wrapper.

Mostly glue — load the model once, batch encode. Provided as a near-complete
reference because the *interesting* embedding decisions (which model, dim,
normalization) belong in your design doc, not in fighting sentence-transformers.

One thing to be deliberate about (flagged inline): normalization. Cosine
similarity assumes normalized vectors; get this wrong and your scores are subtly
meaningless.
"""
from __future__ import annotations

from functools import lru_cache

from config.settings import settings


@lru_cache
def _model():
    # Imported lazily so importing this module doesn't drag in torch until needed.
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Encode a batch of texts to vectors.

    normalize_embeddings=True because downstream similarity (pgvector cosine,
    OpenSearch knn) assumes unit vectors. If you switch to a dot-product index,
    revisit this. TODO(you): confirm the choice matches your index config.
    """
    model = _model()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """Single-query convenience. Some models want a query prefix (e.g. bge's
    'Represent this sentence...'). TODO(you): add the prefix if your model needs
    it — it measurably changes retrieval quality."""
    return embed_texts([text])[0]
