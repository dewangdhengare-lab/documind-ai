"""Embedding generation using sentence-transformers."""

from __future__ import annotations

import logging
from typing import Any

from config import settings

logger = logging.getLogger(__name__)

# Module-level model cache
_model: Any = None


def _get_model():
    """Lazy-load the embedding model."""
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully.")
    return _model


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts.

    Returns a list of embedding vectors (each a list of floats).
    """
    if not texts:
        return []

    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return [emb.tolist() for emb in embeddings]


def generate_single_embedding(text: str) -> list[float]:
    """Generate an embedding for a single text string."""
    results = generate_embeddings([text])
    return results[0] if results else []
