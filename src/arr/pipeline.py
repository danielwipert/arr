"""Pipeline orchestration.

As of Phase 4 the chain runs end-to-end:

    ingest -> filter -> dedup -> process -> rank -> select -> finalize

The pipeline is configured to publish every day a paper survives the
filter and rank stages. The finalizer accepts the last drafter attempt
even if the critic objects, so the only skip cause now is the selector
finding no candidate at all (empty filtered list, or all ranks dropped
to LLM error). The critic report still rides on the FinalPost for the
reviewer.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from datetime import date as date_cls
from datetime import datetime, timedelta
from pathlib import Path

from arr.config import Settings
from arr.models import FinalPost, RankedPaper, SelectedPaper, SkipRecord
from arr.providers.llm import LLMProvider
from arr.providers.papers import PaperSourceProvider
from arr.providers.storage import StorageProvider
from arr.stages import dedup as dedup_stage
from arr.stages import filter as filter_stage
from arr.stages import finalize as finalize_stage
from arr.stages import ingest as ingest_stage
from arr.stages import process as process_stage
from arr.stages import rank as rank_stage
from arr.stages import select as select_stage

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PipelineResult:
    """Summary of what each stage produced; drives CLI output and tests."""

    raw_count: int
    filtered_count: int       # post topical/noise, pre-dedup
    deduped_count: int        # post dedup, pre-rank
    ranked_count: int
    selected: SelectedPaper | None
    final_post: FinalPost | None
    skip_record: SkipRecord | None
    finalize_attempts_used: int = 0


def _write_post_artifacts(
    run_date: date_cls,
    final_post: FinalPost,
    selected: SelectedPaper,
    storage: StorageProvider,
) -> None:
    """Section 13.1 review layout: post.md, final_post.json, grounding.md, paper.pdf."""
    storage.write_root_artifact(run_date, "final_post", final_post)
    storage.write_post(run_date, finalize_stage.build_post_md(final_post))
    storage.write_text(run_date, "grounding.md", finalize_stage.build_grounding_md(final_post))

    pdf_path = Path(selected.pdf_local_path)
    if pdf_path.exists():
        storage.write_pdf(run_date, pdf_path.read_bytes())
    else:
        log.warning("Source PDF missing at %s; paper.pdf not copied", pdf_path)


def _prune_old_review_folders(
    reviews_dir: Path, today: date_cls, retention_days: int
) -> None:
    """Delete `reviews/<YYYY-MM-DD>/` folders older than `retention_days`.

    Anything in `reviews_dir` whose name does not parse as an ISO date is left
    alone (e.g. `.gitkeep`, ad-hoc subdirs). The cutoff is inclusive: a folder
    dated exactly `today - retention_days` is kept.
    """
    if not reviews_dir.exists():
        return
    cutoff = today - timedelta(days=retention_days)
    deleted = 0
    for entry in reviews_dir.iterdir():
        if not entry.is_dir():
            continue
        try:
            entry_date = date_cls.fromisoformat(entry.name)
        except ValueError:
            continue
        if entry_date < cutoff:
            try:
                shutil.rmtree(entry)
                deleted += 1
            except OSError as e:
                log.warning("Retention: failed to remove %s (%s)", entry, e)
    if deleted:
        log.info(
            "Retention: pruned %d review folder(s) older than %s",
            deleted, cutoff.isoformat(),
        )


_SKIP_STALE = ("post.md", "final_post.json", "grounding.md", "paper.pdf")
_POST_STALE = ("skip.json", "drafts")


def _remove_stale_artifacts(day_folder: Path, names: tuple[str, ...]) -> None:
    """Delete leftover files/dirs from a prior same-date run that contradict
    today's terminal state.

    Same-date reruns are routine (manual workflow_dispatch, weekend backfills),
    and without this the folder ends up with both a stale `post.md` from a
    prior post day and today's `skip.json` — exactly the misleading state a
    reviewer cannot reason about. Missing paths are silently ignored.
    """
    for name in names:
        path = day_folder / name
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            else:
                continue
        except OSError as e:
            log.warning("Cleanup: failed to remove %s (%s)", path, e)
            continue
        log.debug("Cleanup: removed stale %s", path.name)


def _prune_cache_keep_selected(
    cache_dir: Path, selected: RankedPaper | None
) -> None:
    """Delete every PDF in `cache_dir` except the one belonging to `selected`.

    On a skip day every cached PDF goes. The selected paper's PDF is the only
    one worth keeping around: it's already been copied into reviews/ for the
    reviewer, and keeping it in cache lets a same-day rerun skip the
    re-download. Failed processing leaves orphan PDFs (the file exists but no
    ProcessedPaper) — globbing the directory catches those too.
    """
    if not cache_dir.exists():
        return
    keep_path = Path(selected.pdf_local_path).resolve() if selected else None
    deleted = 0
    for path in cache_dir.glob("*.pdf"):
        if keep_path is not None and path.resolve() == keep_path:
            continue
        try:
            path.unlink()
            deleted += 1
        except OSError as e:
            log.debug("Cache: failed to prune %s (%s)", path, e)
    if deleted:
        kept_id = selected.arxiv_id if selected else "none"
        log.info("Cache: pruned %d PDFs (kept selected: %s)", deleted, kept_id)


def run_pipeline(
    run_date: date_cls,
    settings: Settings,
    llm: LLMProvider,
    paper_source: PaperSourceProvider,
    storage: StorageProvider,
    reviews_dir: Path,
    cache_dir: Path,
    *,
    now: datetime | None = None,
) -> PipelineResult:
    _prune_old_review_folders(
        reviews_dir, run_date, settings.storage.retention_days
    )
    raw_papers = ingest_stage.run(settings, paper_source, now=now)
    filtered = filter_stage.run(raw_papers, llm, settings)

    history = dedup_stage.load_dedup_history(
        reviews_dir,
        lookback_days=settings.filter.dedup_lookback_days,
        today=run_date,
    )
    deduped = dedup_stage.apply(filtered, history, settings)

    cap = settings.max_candidates_per_run
    if len(deduped) > cap:
        log.info(
            "Pipeline: capping candidates from %d to %d (most-recent first)",
            len(deduped), cap,
        )
        deduped = deduped[:cap]

    ranked = rank_stage.run(deduped, llm, settings)
    for paper in ranked:
        storage.write_named_artifact(run_date, "ranked", paper.arxiv_id, paper)

    top_ranked = select_stage.select_top(ranked, settings)
    if top_ranked is None:
        skip = select_stage.build_skip_record(
            run_date=run_date,
            papers_considered=len(raw_papers),
            papers_filtered=len(deduped),
            ranked=ranked,
            settings=settings,
        )
        storage.write_root_artifact(run_date, "skip", skip)
        _remove_stale_artifacts(storage.day_folder(run_date), _SKIP_STALE)
        log.info("Pipeline: skip day — %s", skip.reason)
        _prune_cache_keep_selected(cache_dir, None)
        return PipelineResult(
            raw_count=len(raw_papers),
            filtered_count=len(filtered),
            deduped_count=len(deduped),
            ranked_count=len(ranked),
            selected=None,
            final_post=None,
            skip_record=skip,
            finalize_attempts_used=0,
        )

    # Lazy PDF processing with fallback: walk candidates above threshold in
    # composite-descending order, taking the first whose PDF fetches + parses.
    # arxiv occasionally rate-limits a single PDF; without this loop one 429
    # would skip the day even though 9 other ranked papers are right there.
    threshold = settings.selector.post_worthy_threshold
    candidates = sorted(
        (p for p in ranked if p.composite >= threshold),
        key=lambda p: p.composite,
        reverse=True,
    )
    selected: SelectedPaper | None = None
    pdf_failures: list[str] = []
    for candidate in candidates:
        result = process_stage.process_selected(candidate, paper_source)
        if result is not None:
            selected = result
            break
        pdf_failures.append(candidate.arxiv_id)
        log.warning(
            "Pipeline: PDF failed for %s; falling back to next candidate",
            candidate.arxiv_id,
        )

    if selected is None:
        skip = SkipRecord(
            date=run_date.isoformat(),
            papers_considered=len(raw_papers),
            papers_filtered=len(deduped),
            papers_ranked=len(ranked),
            top_paper=None,
            reason=(
                f"PDF fetch failed for all {len(pdf_failures)} ranked "
                f"candidate(s): {', '.join(pdf_failures)}"
            ),
        )
        storage.write_root_artifact(run_date, "skip", skip)
        _remove_stale_artifacts(storage.day_folder(run_date), _SKIP_STALE)
        log.warning("Pipeline: %s", skip.reason)
        _prune_cache_keep_selected(cache_dir, None)
        return PipelineResult(
            raw_count=len(raw_papers),
            filtered_count=len(filtered),
            deduped_count=len(deduped),
            ranked_count=len(ranked),
            selected=None,
            final_post=None,
            skip_record=skip,
            finalize_attempts_used=0,
        )

    if pdf_failures:
        log.info(
            "Pipeline: selected %s after %d PDF fallback(s) (%s)",
            selected.arxiv_id, len(pdf_failures), ", ".join(pdf_failures),
        )

    storage.write_named_artifact(run_date, "processed", selected.arxiv_id, selected)
    storage.write_root_artifact(run_date, "selected", selected)

    finalizer = finalize_stage.run(selected, llm, settings, now=now)

    if finalizer.succeeded:
        _write_post_artifacts(run_date, finalizer.final_post, selected, storage)
        _remove_stale_artifacts(storage.day_folder(run_date), _POST_STALE)
        log.info(
            "Pipeline: drafted post for %s (composite %.2f, attempts %d)",
            selected.arxiv_id, selected.composite, finalizer.attempts_used,
        )
        _prune_cache_keep_selected(cache_dir, selected)
        return PipelineResult(
            raw_count=len(raw_papers),
            filtered_count=len(filtered),
            deduped_count=len(deduped),
            ranked_count=len(ranked),
            selected=selected,
            final_post=finalizer.final_post,
            skip_record=None,
            finalize_attempts_used=finalizer.attempts_used,
        )

    # Reached only when every drafter or critic call raised LLMError before
    # producing a single (draft, report) pair — i.e. the LLM is unreachable.
    # Subjective critic rejections no longer land here; finalize accepts the
    # last attempt with the critic flags attached.
    skip = SkipRecord(
        date=run_date.isoformat(),
        papers_considered=len(raw_papers),
        papers_filtered=len(deduped),
        papers_ranked=len(ranked),
        top_paper=None,
        reason="LLM unreachable — no drafter attempts completed",
    )
    storage.write_root_artifact(run_date, "skip", skip)
    _remove_stale_artifacts(storage.day_folder(run_date), _SKIP_STALE)
    log.warning("Pipeline: %s", skip.reason)
    _prune_cache_keep_selected(cache_dir, selected)
    return PipelineResult(
        raw_count=len(raw_papers),
        filtered_count=len(filtered),
        deduped_count=len(deduped),
        ranked_count=len(ranked),
        selected=selected,
        final_post=None,
        skip_record=skip,
        finalize_attempts_used=finalizer.attempts_used,
    )
