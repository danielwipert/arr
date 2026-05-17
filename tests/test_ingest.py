"""Tests for Stage 1 ingestor."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from arr.config import load_settings
from arr.models import RawPaper
from arr.stages import ingest


class FakePaperSource:
    def __init__(self, papers: list[RawPaper]):
        self._papers = papers
        self.calls: list[tuple[list[str], datetime]] = []

    def fetch_recent(self, categories, since):
        self.calls.append((list(categories), since))
        return list(self._papers)

    def fetch_pdf(self, arxiv_id: str) -> Path:
        raise NotImplementedError


def _paper(arxiv_id: str, hours_ago: int = 1) -> RawPaper:
    return RawPaper(
        arxiv_id=arxiv_id,
        title=f"Paper {arxiv_id}",
        authors=["A. Researcher"],
        abstract="...",
        primary_cat="cs.CL",
        all_cats=["cs.CL"],
        submitted_at=datetime(2026, 5, 16, 12 - hours_ago % 12, 0, tzinfo=timezone.utc),
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
    )


def test_ingest_passes_configured_categories_and_window():
    settings = load_settings()
    fake = FakePaperSource([_paper("2026.0001"), _paper("2026.0002")])
    now = datetime(2026, 5, 16, 12, 0, tzinfo=timezone.utc)

    out = ingest.run(settings, fake, now=now)

    assert len(out) == 2
    assert fake.calls[0][0] == settings.arxiv.categories
    delta = now - fake.calls[0][1]
    assert delta.total_seconds() == settings.arxiv.lookback_hours * 3600


def test_ingest_returns_empty_when_source_is_empty():
    settings = load_settings()
    fake = FakePaperSource([])
    assert ingest.run(settings, fake) == []
