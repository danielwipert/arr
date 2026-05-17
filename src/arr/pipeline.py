"""Pipeline orchestration.

As of Phase 3 the chain runs:

    ingest -> filter -> dedup -> process -> rank -> select

and writes either a selected.json (RankedPaper artifact for the day's
chosen paper) or a skip.json (SkipRecord with a reason). Per-paper
ProcessedPaper and RankedPaper JSONs land under per-day subfolders so
ranker calibration is inspectable on both post and skip days.

Drafter, critic, and finalizer (Stages 6–8) are wired up in Phase 4.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date as date_cls
from datetime import datetime
from pathlib import Path

from arr.config import Settings
from arr.models import RankedPaper, SkipRecord
from arr.providers.embeddings import EmbeddingProvider
from arr.providers.llm import LLMProvider
from arr.providers.papers import PaperSourceProvider
from arr.providers.storage import StorageProvider
from arr.stages import dedup as dedup_stage
from arr.stages import filter as filter_stage
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
    skip_record: SkipRecord | None


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

    processed = process_stage.run(deduped, paper_source, settings)
    for paper in processed:
        storage.write_named_artifact(run_date, "processed", paper.arxiv_id, paper)

    ranked = rank_stage.run(processed, llm, settings)
    for paper in ranked:
        storage.write_named_artifact(run_date, "ranked", paper.arxiv_id, paper)

    selected = select_stage.select_top(ranked, settings)

    skip_record: SkipRecord | None = None
    if selected is not None:
        storage.write_root_artifact(run_date, "selected", selected)
        log.info(
            "Pipeline: selected %s (composite %.2f)",
            selected.arxiv_id, selected.composite,
        )
    else:
        skip_record = select_stage.build_skip_record(
            run_date=run_date,
            papers_considered=len(raw_papers),
            papers_filtered=len(deduped),
            ranked=ranked,
            settings=settings,
        )
        storage.write_root_artifact(run_date, "skip", skip_record)
        log.info("Pipeline: skip day — %s", skip_record.reason)

    return PipelineResult(
        raw_count=len(raw_papers),
        filtered_count=len(filtered),
        deduped_count=len(deduped),
        processed_count=len(processed),
        ranked_count=len(ranked),
        selected=selected,
        skip_record=skip_record,
    )
