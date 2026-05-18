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


EMPTY_RETRY_MULTIPLIER = 4


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
    lookback = settings.arxiv.lookback_hours
    since = now - timedelta(hours=lookback)
    log.info(
        "Ingest: fetching papers from %s categories since %s",
        len(settings.arxiv.categories),
        since.isoformat(),
    )
    papers = paper_source.fetch_recent(settings.arxiv.categories, since)
    # arXiv's announcement schedule + holidays can leave a 24-96h gap with no
    # fresh papers in the API. Widen once before declaring skip so a quiet
    # day doesn't become an empty run.
    if not papers:
        widened = lookback * EMPTY_RETRY_MULTIPLIER
        widened_since = now - timedelta(hours=widened)
        log.info(
            "Ingest: empty first sweep; retrying with %sh lookback (since %s)",
            widened,
            widened_since.isoformat(),
        )
        papers = paper_source.fetch_recent(settings.arxiv.categories, widened_since)
    log.info("Ingest: %d papers returned", len(papers))
    return papers
