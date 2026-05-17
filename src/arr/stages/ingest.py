"""Stage 1 — Ingestor.

Pulls the last `lookback_hours` of submissions from the configured arXiv
categories. No PDF fetching at this stage — that lives in Stage 3, after
filtering.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from arr.config import Settings
from arr.models import RawPaper
from arr.providers.papers import PaperSourceProvider

log = logging.getLogger(__name__)


def run(
    settings: Settings,
    paper_source: PaperSourceProvider,
    *,
    now: datetime | None = None,
) -> list[RawPaper]:
    """Return the batch of raw papers submitted within the lookback window.

    `now` exists for tests; defaults to the current UTC time.
    """
    now = now or datetime.now(timezone.utc)
    since = now - timedelta(hours=settings.arxiv.lookback_hours)
    log.info(
        "Ingest: fetching papers from %s categories since %s",
        len(settings.arxiv.categories),
        since.isoformat(),
    )
    papers = paper_source.fetch_recent(settings.arxiv.categories, since)
    log.info("Ingest: %d papers returned", len(papers))
    return papers
