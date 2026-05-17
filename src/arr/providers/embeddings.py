"""Embedding provider abstraction.

Used by the dedup filter to embed paper title plus first ~500 chars of the
abstract, then compare cosine similarity against the last 30 days of
considered papers. A concrete implementation (sentence-transformers,
local) lands in Phase 2 alongside the filter stage.
"""

from __future__ import annotations

from typing import Protocol


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...
