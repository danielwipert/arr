"""End-to-end test of the Phase 2 pipeline with fake providers."""

from __future__ import annotations

import json
from datetime import date as date_cls
from datetime import datetime, timezone
from pathlib import Path

import pytest

from arr.config import load_settings
from arr.models import RawPaper
from arr.pipeline import run_pipeline
from arr.providers.storage import LocalFilesystemStorage
from arr.stages import process as process_stage
from arr.stages.filter import FilterDecision


def _paper(arxiv_id: str, title: str, abstract: str) -> RawPaper:
    return RawPaper(
        arxiv_id=arxiv_id,
        title=title,
        authors=["A. Researcher"],
        abstract=abstract,
        primary_cat="cs.CL",
        all_cats=["cs.CL"],
        submitted_at=datetime(2026, 5, 16, 12, 0, tzinfo=timezone.utc),
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
    )


class FakePaperSource:
    def __init__(self, papers: list[RawPaper]):
        self._papers = papers

    def fetch_recent(self, _categories, _since):
        return list(self._papers)

    def fetch_pdf(self, arxiv_id: str) -> Path:
        return Path(f"/tmp/{arxiv_id}.pdf")


class FakeLLM:
    """Returns scripted FilterDecisions by abstract substring."""

    def __init__(self, decisions: dict[str, FilterDecision]):
        self._decisions = decisions

    def complete(self, *_, **__) -> str:
        raise NotImplementedError

    def complete_json(self, messages, model, schema, **kwargs):
        body = messages[-1]["content"]
        for key, decision in self._decisions.items():
            if key in body:
                return decision
        return FilterDecision(
            in_scope=False, primary_topic="other",
            is_review_or_survey=False, note="default drop",
        )


def test_pipeline_writes_processed_artifacts_for_in_scope_papers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    keep = _paper("2026.0001", "Query Decomposition for RAG", "rag method abstract")
    drop_scope = _paper("2026.0002", "ViT Improvements", "vision images abstract")

    decisions = {
        "rag method": FilterDecision(in_scope=True, primary_topic="rag",
                                     is_review_or_survey=False, note=""),
        "vision images": FilterDecision(in_scope=False, primary_topic="other",
                                        is_review_or_survey=False, note=""),
    }

    # Stub PDF extraction so we don't touch a real file.
    monkeypatch.setattr(
        process_stage,
        "extract_text_with_pdfplumber",
        lambda _p: (
            "Abstract\nWe propose X.\n\n"
            "1 Introduction\nMotivation.\n\n"
            "2 Method\nQuery decomposition.\n",
            10,
        ),
    )

    storage = LocalFilesystemStorage(tmp_path / "reviews")
    result = run_pipeline(
        run_date=date_cls(2026, 5, 16),
        settings=load_settings(),
        llm=FakeLLM(decisions),
        paper_source=FakePaperSource([keep, drop_scope]),
        storage=storage,
        now=datetime(2026, 5, 16, 12, 0, tzinfo=timezone.utc),
    )

    assert result.raw_count == 2
    assert result.filtered_count == 1
    assert result.processed_count == 1

    out_file = tmp_path / "reviews" / "2026-05-16" / "processed" / "2026.0001.json"
    assert out_file.exists()
    payload = json.loads(out_file.read_text(encoding="utf-8"))
    assert payload["arxiv_id"] == "2026.0001"
    assert payload["primary_topic"] == "rag"
    assert "method" in payload["sections"]


def test_pipeline_writes_nothing_when_all_papers_drop(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    drop = _paper("2026.0099", "Survey of Things", "we survey...")
    decisions = {
        "we survey": FilterDecision(
            in_scope=True, primary_topic="rag",
            is_review_or_survey=True, note="survey"),
    }

    monkeypatch.setattr(
        process_stage,
        "extract_text_with_pdfplumber",
        lambda _p: ("Abstract\nx\n\n1 Method\ny\n", 5),
    )

    storage = LocalFilesystemStorage(tmp_path / "reviews")
    result = run_pipeline(
        run_date=date_cls(2026, 5, 16),
        settings=load_settings(),
        llm=FakeLLM(decisions),
        paper_source=FakePaperSource([drop]),
        storage=storage,
    )

    assert result.processed_count == 0
    processed_dir = tmp_path / "reviews" / "2026-05-16" / "processed"
    assert not processed_dir.exists() or not any(processed_dir.iterdir())
