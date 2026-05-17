"""Paper source provider abstraction + arXiv implementation.

Stage 1 (the ingestor) talks to arXiv only through this interface, so the
pipeline can be exercised in tests with a fake source. The default impl
wraps the `arxiv` PyPI package.
"""

from __future__ import annotations

import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from arr.models import RawPaper

log = logging.getLogger(__name__)


class PaperSourceProvider(Protocol):
    def fetch_recent(
        self, categories: list[str], since: datetime
    ) -> list[RawPaper]:
        ...

    def fetch_pdf(self, arxiv_id: str) -> Path:
        ...


class ArxivPaperSource:
    """Default `PaperSourceProvider` backed by the `arxiv` PyPI package.

    `fetch_recent` queries arXiv per-category, deduplicates by arxiv_id, and
    keeps papers submitted on or after `since`. `fetch_pdf` writes the PDF
    bytes into the provided cache dir so subsequent runs skip re-download.
    """

    def __init__(
        self,
        cache_dir: Path,
        *,
        max_results_per_category: int = 200,
        page_size: int = 100,
        delay_seconds: float = 3.0,
    ) -> None:
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._max_results = max_results_per_category
        self._page_size = page_size
        self._delay = delay_seconds

    def fetch_recent(
        self, categories: list[str], since: datetime
    ) -> list[RawPaper]:
        # Lazy import — keeps tests runnable without the dep installed.
        import arxiv

        # arXiv's submitted_at is timezone-aware (UTC). Normalize `since`.
        if since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)

        client = arxiv.Client(
            page_size=self._page_size,
            delay_seconds=self._delay,
        )

        by_id: dict[str, RawPaper] = {}
        for cat in categories:
            search = arxiv.Search(
                query=f"cat:{cat}",
                max_results=self._max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )
            for result in client.results(search):
                if result.published < since:
                    # Sorted descending, so once we're past the window we're done.
                    break
                paper = _result_to_raw_paper(result)
                # First occurrence wins; an arxiv_id can show up in multiple cats.
                by_id.setdefault(paper.arxiv_id, paper)
        papers = list(by_id.values())
        papers.sort(key=lambda p: p.submitted_at, reverse=True)
        log.info("arXiv: fetched %d unique papers across %d categories", len(papers), len(categories))
        return papers

    def fetch_pdf(self, arxiv_id: str) -> Path:
        import arxiv

        target = self._cache_dir / f"{_safe_filename(arxiv_id)}.pdf"
        if target.exists():
            return target

        search = arxiv.Search(id_list=[arxiv_id])
        client = arxiv.Client(delay_seconds=self._delay)
        result = next(iter(client.results(search)), None)
        if result is None:
            raise FileNotFoundError(f"arXiv has no paper with id {arxiv_id}")

        downloaded = Path(
            result.download_pdf(dirpath=str(self._cache_dir))
        )
        if downloaded != target:
            shutil.move(str(downloaded), str(target))
        return target


def _result_to_raw_paper(result) -> RawPaper:  # type: ignore[no-untyped-def]
    """Translate an `arxiv.Result` into our RawPaper model."""
    # arxiv.Result.entry_id is the full URL; we want just the bare id.
    arxiv_id = result.get_short_id()
    return RawPaper(
        arxiv_id=arxiv_id,
        title=result.title.strip(),
        authors=[a.name for a in result.authors],
        abstract=result.summary.strip(),
        primary_cat=result.primary_category,
        all_cats=list(result.categories),
        submitted_at=result.published,
        pdf_url=result.pdf_url,
    )


def _safe_filename(arxiv_id: str) -> str:
    """arXiv ids can contain '/'; flatten for filesystem use."""
    return arxiv_id.replace("/", "_")
