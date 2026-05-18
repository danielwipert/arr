"""Dedup back-fill for Stage 2.

Drop a candidate if its arxiv_id appeared in the last
`filter.dedup_lookback_days` of processed/ artifacts. This catches the
realistic collision — a same-day rerun picking yesterday's paper, or
arxiv surfacing a v2 of a paper already posted — without paying for a
semantic-similarity model.

Earlier versions of this stage used sentence-transformer embeddings and
a cosine-similarity threshold against the title + abstract head. That
caught a broader class of "this looks like something we already
posted", but the dependency was heavy and at one post/day the realistic
collision is just re-selecting the same paper.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date as date_cls
from datetime import timedelta
from pathlib import Path

from arr.config import Settings
from arr.models import FilteredPaper

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class HistoryEntry:
    """Lightweight record of a previously considered paper."""

    arxiv_id: str


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

    seen: set[str] = set()
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
            if arxiv_id:
                seen.add(arxiv_id)
    log.info("Dedup: loaded %d history entries from last %d days", len(seen), lookback_days)
    return [HistoryEntry(arxiv_id=a) for a in seen]


def apply(
    papers: list[FilteredPaper],
    history: list[HistoryEntry],
    settings: Settings,
) -> list[FilteredPaper]:
    """Drop papers whose arxiv_id appeared in the history window."""
    if not papers:
        return []

    if not history:
        return [p.model_copy(update={"dedup_similarity": None}) for p in papers]

    seen_ids = {h.arxiv_id for h in history}
    out: list[FilteredPaper] = []
    dropped = 0
    for paper in papers:
        if paper.arxiv_id in seen_ids:
            log.debug("Dedup drop %s: arxiv_id seen in history", paper.arxiv_id)
            dropped += 1
            continue
        out.append(paper.model_copy(update={"dedup_similarity": None}))

    log.info(
        "Dedup: %d/%d papers survived (history %d, dropped %d)",
        len(out), len(papers), len(history), dropped,
    )
    return out
