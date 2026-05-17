"""Pipeline orchestration.

As of Phase 4 the chain runs end-to-end:

    ingest -> filter -> dedup -> process -> rank -> select -> finalize

On a post day the finalizer's FinalPost lands as final_post.json, the
ready-to-paste post.md and the per-claim grounding.md sit alongside it,
and the source PDF is copied next to them so a reviewer can verify any
claim without leaving the folder. On a skip day a SkipRecord goes in as
skip.json with a reason — either the selector's (no paper above threshold)
or the finalizer's (voice critic failed after N attempts).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date as date_cls
from datetime import datetime
from pathlib import Path

from arr.config import Settings
from arr.models import FinalPost, RankedPaper, SkipRecord
from arr.providers.embeddings import EmbeddingProvider
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
    deduped_count: int        # post dedup, pre-process
    processed_count: int
    ranked_count: int
    selected: RankedPaper | None
    final_post: FinalPost | None
    skip_record: SkipRecord | None
    finalize_attempts_used: int = 0


def _write_post_artifacts(
    run_date: date_cls,
    final_post: FinalPost,
    selected: RankedPaper,
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


def run_pipeline(
    run_date: date_cls,
    settings: Settings,
    llm: LLMProvider,
    paper_source: PaperSourceProvider,
    storage: StorageProvider,
    embeddings: EmbeddingProvider,
    reviews_dir: Path,
    *,
    now: datetime | None = None,
) -> PipelineResult:
    raw_papers = ingest_stage.run(settings, paper_source, now=now)
    filtered = filter_stage.run(raw_papers, llm, settings)

    history = dedup_stage.load_dedup_history(
        reviews_dir,
        lookback_days=settings.filter.dedup_lookback_days,
        today=run_date,
    )
    deduped = dedup_stage.apply(filtered, embeddings, history, settings)

    cap = settings.max_candidates_per_run
    if len(deduped) > cap:
        log.info(
            "Pipeline: capping candidates from %d to %d (most-recent first)",
            len(deduped), cap,
        )
        deduped = deduped[:cap]

    processed = process_stage.run(deduped, paper_source, settings)
    for paper in processed:
        storage.write_named_artifact(run_date, "processed", paper.arxiv_id, paper)

    ranked = rank_stage.run(processed, llm, settings)
    for paper in ranked:
        storage.write_named_artifact(run_date, "ranked", paper.arxiv_id, paper)

    selected = select_stage.select_top(ranked, settings)
    if selected is None:
        skip = select_stage.build_skip_record(
            run_date=run_date,
            papers_considered=len(raw_papers),
            papers_filtered=len(deduped),
            ranked=ranked,
            settings=settings,
        )
        storage.write_root_artifact(run_date, "skip", skip)
        log.info("Pipeline: skip day — %s", skip.reason)
        return PipelineResult(
            raw_count=len(raw_papers),
            filtered_count=len(filtered),
            deduped_count=len(deduped),
            processed_count=len(processed),
            ranked_count=len(ranked),
            selected=None,
            final_post=None,
            skip_record=skip,
        )

    # We have a selected paper; persist it before the drafter starts so the
    # intermediate selection state survives a drafter crash.
    storage.write_root_artifact(run_date, "selected", selected)

    finalizer = finalize_stage.run(selected, llm, settings, now=now)

    if finalizer.succeeded:
        _write_post_artifacts(run_date, finalizer.final_post, selected, storage)
        log.info(
            "Pipeline: drafted post for %s (composite %.2f, attempts %d)",
            selected.arxiv_id, selected.composite, finalizer.attempts_used,
        )
        return PipelineResult(
            raw_count=len(raw_papers),
            filtered_count=len(filtered),
            deduped_count=len(deduped),
            processed_count=len(processed),
            ranked_count=len(ranked),
            selected=selected,
            final_post=finalizer.final_post,
            skip_record=None,
            finalize_attempts_used=finalizer.attempts_used,
        )

    skip = SkipRecord(
        date=run_date.isoformat(),
        papers_considered=len(raw_papers),
        papers_filtered=len(deduped),
        papers_ranked=len(ranked),
        top_paper=None,
        reason=finalize_stage.build_voice_skip_reason(finalizer.attempts_used),
    )
    storage.write_root_artifact(run_date, "skip", skip)
    log.info("Pipeline: drafter retries exhausted — %s", skip.reason)
    return PipelineResult(
        raw_count=len(raw_papers),
        filtered_count=len(filtered),
        deduped_count=len(deduped),
        processed_count=len(processed),
        ranked_count=len(ranked),
        selected=selected,
        final_post=None,
        skip_record=skip,
        finalize_attempts_used=finalizer.attempts_used,
    )
