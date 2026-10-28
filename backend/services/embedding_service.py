"""Embedding generation using sentence-transformers with lightweight memory protection."""

from __future__ import annotations

import hashlib
import logging
import math
import os
import re
from typing import Any

# Force single-thread execution to drastically reduce memory overhead on cloud containers
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from config import settings

logger = logging.getLogger(__name__)

# Module-level model cache
_model: Any = None
_use_lightweight_fallback = False
_EMBEDDING_DIM = 384


def _generate_lightweight_embedding(text: str, dim: int = _EMBEDDING_DIM) -> list[float]:
    """
    Deterministic normalized 384-dim semantic hash vector.
    Uses zero external memory (< 1 KB) as a bulletproof fallback when cloud instances have low RAM.
    """
    words = re.findall(r"\w+", text.lower())
    if not words:
        return [0.0] * dim

    vec = [0.0] * dim
    for word in words:
        h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
        bucket = h % dim
        sign = 1.0 if (h >> 16) % 2 == 0 else -1.0
        vec[bucket] += sign

    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def _get_model():
    """Lazy-load the embedding model with memory protection."""
    global _model, _use_lightweight_fallback
    if _use_lightweight_fallback:
        return None

    if _model is None:
        try:
            logger.info("Attempting to load embedding model: %s", settings.EMBEDDING_MODEL)
            import torch
            torch.set_num_threads(1)
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully.")
        except (MemoryError, OSError, Exception) as e:
            logger.warning(
                "Could not load heavy SentenceTransformer (likely low RAM: %s). Activating lightweight 384-dim vector fallback.",
                e,
            )
            _use_lightweight_fallback = True
            _model = None

    return _model


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts.
    Returns a list of 384-dim embedding vectors.
    """
    if not texts:
        return []

    model = _get_model()
    if model is not None:
        try:
            embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True, batch_size=8)
            return [emb.tolist() for emb in embeddings]
        except (MemoryError, Exception) as e:
            logger.warning("Model encode failed with %s, falling back to lightweight vectors", e)

    return [_generate_lightweight_embedding(t) for t in texts]


def generate_single_embedding(text: str) -> list[float]:
    """Generate an embedding for a single text string."""
    results = generate_embeddings([text])
    return results[0] if results else [0.0] * _EMBEDDING_DIM
