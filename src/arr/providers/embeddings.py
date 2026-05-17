"""Embedding provider abstraction + local sentence-transformers implementation.

Used by the dedup filter to embed paper title plus first ~500 chars of the
abstract, then compare cosine similarity against the last 30 days of
considered papers. The default backend is `sentence-transformers`
all-MiniLM-L6-v2 running locally so we don't pay an API per dedup check.
"""

from __future__ import annotations

import logging
from typing import Protocol

log = logging.getLogger(__name__)


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...


class LocalSentenceTransformerEmbeddings:
    """sentence-transformers backend. Model is lazy-loaded on first embed()."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model = None  # populated on first call

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        # Lazy import keeps unit tests fast — torch + transformers is heavy.
        from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]

        log.info("Loading embedding model %s", self._model_name)
        self._model = SentenceTransformer(self._model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        self._ensure_loaded()
        assert self._model is not None
        vectors = self._model.encode(
            texts, normalize_embeddings=True, convert_to_numpy=True
        )
        return [list(map(float, v)) for v in vectors]
