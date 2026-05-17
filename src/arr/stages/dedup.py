"""Dedup back-fill for Stage 2.

Spec (Section 3.5):
    A small sentence-transformer embedding of the title plus first 500
    characters of the abstract, computed against the embeddings of the
    last 30 days of considered papers. A cosine similarity above 0.92
    against any prior paper triggers a drop.

We treat "considered papers" as the post-filter `processed/` artifacts on
disk. On a fresh repo there is no history yet, so the dedup step is a
no-op for the first 30 days.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass
from datetime import date as date_cls
from datetime import timedelta
from pathlib import Path

from arr.config import Settings
from arr.models import FilteredPaper
from arr.providers.embeddings import EmbeddingProvider

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class HistoryEntry:
    """Lightweight record of a previously considered paper."""

    arxiv_id: str
    text: str  # title + first 500 chars of abstract, same shape as candidates


def _dedup_text(title: str, abstract: str) -> str:
    """Spec-defined shape for the dedup signature."""
    return f"{title}\n\n{abstract[:500]}"


def load_dedup_history(
    reviews_dir: Path,
    lookback_days: int,
    today: date_cls,
) -> list[HistoryEntry]:
    """Scan reviews/YYYY-MM-DD/processed/*.json for entries in the last N days
    (excluding today itself). Returns one entry per unique arxiv_id.
    """
    if not reviews_dir.exists():
        return []

    seen: dict[str, HistoryEntry] = {}
    for offset in range(1, lookback_days + 1):
        day = today - timedelta(days=offset)
        folder = reviews_dir / day.isoformat() / "processed"
        if not folder.exists():
            continue
        for path in folder.glob("*.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as e:
                log.warning("Dedup: could not load history file %s (%s)", path, e)
                continue
            arxiv_id = payload.get("arxiv_id")
            title = payload.get("title", "")
            abstract = payload.get("abstract", "")
            if not arxiv_id:
                continue
            seen.setdefault(
                arxiv_id, HistoryEntry(arxiv_id=arxiv_id, text=_dedup_text(title, abstract))
            )
    log.info("Dedup: loaded %d history entries from last %d days", len(seen), lookback_days)
    return list(seen.values())


def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity. Embedding provider already L2-normalises, but we
    do not depend on that — keeps the helper safe under provider swaps."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def apply(
    papers: list[FilteredPaper],
    embeddings: EmbeddingProvider,
    history: list[HistoryEntry],
    settings: Settings,
) -> list[FilteredPaper]:
    """Drop papers whose dedup signature is too close to a history entry.

    The kept papers carry their max-observed similarity in
    `dedup_similarity` so a borderline case is visible in the artifact.
    """
    if not papers:
        return []

    threshold = settings.filter.dedup_similarity_threshold
    candidate_texts = [_dedup_text(p.title, p.abstract) for p in papers]

    if not history:
        # No history yet: every candidate is unique by construction. Embed once
        # so we still attach a dedup_similarity (None means "no history to
        # compare against").
        return [
            p.model_copy(update={"dedup_similarity": None}) for p in papers
        ]

    history_texts = [h.text for h in history]
    candidate_vecs = embeddings.embed(candidate_texts)
    history_vecs = embeddings.embed(history_texts)

    out: list[FilteredPaper] = []
    for paper, vec in zip(papers, candidate_vecs):
        max_sim = 0.0
        worst_match: str | None = None
        for h_entry, h_vec in zip(history, history_vecs):
            sim = _cosine(vec, h_vec)
            if sim > max_sim:
                max_sim = sim
                worst_match = h_entry.arxiv_id
        if max_sim >= threshold:
            log.debug(
                "Dedup drop %s: similarity %.3f against %s (>= %.2f)",
                paper.arxiv_id, max_sim, worst_match, threshold,
            )
            continue
        out.append(paper.model_copy(update={"dedup_similarity": round(max_sim, 4)}))

    log.info(
        "Dedup: %d/%d papers survived (threshold %.2f, history %d)",
        len(out), len(papers), threshold, len(history),
    )
    return out
