"""Pipeline orchestration.

Sequences the implemented stages and persists their outputs through the
storage provider. As of Phase 2 the chain runs:

    ingest -> filter -> process

and writes one ProcessedPaper JSON per surviving paper into
`reviews/YYYY-MM-DD/processed/<arxiv_id>.json`. Stages 4–8 (rank, select,
draft, critique, finalize) are wired up in subsequent phases.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date as date_cls
from datetime import datetime

from arr.config import Settings
from arr.models import ProcessedPaper
from arr.providers.llm import LLMProvider
from arr.providers.papers import PaperSourceProvider
from arr.providers.storage import StorageProvider
from arr.stages import filter as filter_stage
from arr.stages import ingest as ingest_stage
from arr.stages import process as process_stage

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PipelineResult:
    """Summary of what each stage produced; useful for CLI output and tests."""

    raw_count: int
    filtered_count: int
    processed_count: int
    processed: list[ProcessedPaper]


def run_pipeline(
    run_date: date_cls,
    settings: Settings,
    llm: LLMProvider,
    paper_source: PaperSourceProvider,
    storage: StorageProvider,
    *,
    now: datetime | None = None,
) -> PipelineResult:
    raw_papers = ingest_stage.run(settings, paper_source, now=now)
    filtered = filter_stage.run(raw_papers, llm, settings)
    processed = process_stage.run(filtered, paper_source, settings)

    for paper in processed:
        storage.write_named_artifact(run_date, "processed", paper.arxiv_id, paper)

    return PipelineResult(
        raw_count=len(raw_papers),
        filtered_count=len(filtered),
        processed_count=len(processed),
        processed=processed,
    )
