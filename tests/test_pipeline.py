"""End-to-end test of the Phase 3 pipeline with fake providers.

The pipeline runs ingest -> filter -> dedup -> process -> rank -> select.
We supply scripted LLM responses (FilterDecision then RankerOutput) and a
patched PDF extractor, and check that the right artifacts land on disk.
"""

from __future__ import annotations

import json
from datetime import date as date_cls
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from arr.config import load_settings
from arr.models import DimensionScore, RawPaper
from arr.pipeline import run_pipeline
from arr.providers.storage import LocalFilesystemStorage
from arr.stages import process as process_stage
from arr.stages.filter import FilterDecision
from arr.stages.rank import RankerOutput


def _raw(arxiv_id: str, title: str, abstract: str) -> RawPaper:
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


class ScriptedLLM:
    """Routes complete_json calls to the right canned response by schema name."""

    def __init__(
        self,
        filter_decisions: dict[str, FilterDecision],
        ranker_outputs: dict[str, RankerOutput],
    ):
        self._filter = filter_decisions
        self._ranker = ranker_outputs

    def complete(self, *_, **__): raise NotImplementedError

    def complete_json(self, messages, model, schema, **kwargs):
        body = messages[-1]["content"]
        if schema.__name__ == "FilterDecision":
            for key, decision in self._filter.items():
                if key in body:
                    return decision
            return FilterDecision(
                in_scope=False, primary_topic="other",
                is_review_or_survey=False, note="default drop",
            )
        if schema.__name__ == "RankerOutput":
            for key, output in self._ranker.items():
                if key in body:
                    return output
            # Default: low scores.
            return _ranker_output(2, 2, 2, 2, 2)
        raise AssertionError(f"unexpected schema {schema}")


class NullEmbeddings:
    def embed(self, texts):
        return [[0.0] * 8 for _ in texts]


def _ranker_output(s, n, r, c, t) -> RankerOutput:
    return RankerOutput(
        significance=DimensionScore(score=s, justification="."),
        novelty=DimensionScore(score=n, justification="."),
        reproducibility=DimensionScore(score=r, justification="."),
        clarity=DimensionScore(score=c, justification="."),
        topical_fit=DimensionScore(score=t, justification="."),
    )


@pytest.fixture
def stub_pdf_extractor(monkeypatch):
    monkeypatch.setattr(
        process_stage,
        "extract_text_with_pdfplumber",
        lambda _p: (
            "Abstract\nWe propose X.\n\n"
            "1 Introduction\nMotivation.\n\n"
            "2 Method\nDetails.\n\n"
            "3 Results\nWe get 71.2 on HotpotQA.\n",
            10,
        ),
    )


def test_pipeline_selects_top_paper_when_above_threshold(
    tmp_path: Path, stub_pdf_extractor
):
    # Markers go in the *title* so they survive the PDF section overwrite
    # in stub_pdf_extractor — the ranker prompt always includes the title.
    winner = _raw("2026.0001", "WINNERMARK Query Decomposition", "rag method")
    loser = _raw("2026.0002", "LOSERMARK Small Tweak", "rag method")

    filter_decisions = {
        "WINNERMARK": FilterDecision(in_scope=True, primary_topic="rag",
                                     is_review_or_survey=False, note=""),
        "LOSERMARK": FilterDecision(in_scope=True, primary_topic="rag",
                                    is_review_or_survey=False, note=""),
    }
    ranker_outputs = {
        "WINNERMARK": _ranker_output(9, 9, 8, 9, 10),  # composite ~8.95
        "LOSERMARK": _ranker_output(4, 4, 4, 4, 4),    # composite 4.0
    }

    storage = LocalFilesystemStorage(tmp_path / "reviews")
    result = run_pipeline(
        run_date=date_cls(2026, 5, 16),
        settings=load_settings(),
        llm=ScriptedLLM(filter_decisions, ranker_outputs),
        paper_source=FakePaperSource([winner, loser]),
        storage=storage,
        embeddings=NullEmbeddings(),
        reviews_dir=tmp_path / "reviews",
        now=datetime(2026, 5, 16, 12, 0, tzinfo=timezone.utc),
    )

    assert result.raw_count == 2
    assert result.filtered_count == 2
    assert result.processed_count == 2
    assert result.ranked_count == 2
    assert result.selected is not None
    assert result.selected.arxiv_id == "2026.0001"
    assert result.skip_record is None

    selected_file = tmp_path / "reviews" / "2026-05-16" / "selected.json"
    assert selected_file.exists()
    payload = json.loads(selected_file.read_text(encoding="utf-8"))
    assert payload["arxiv_id"] == "2026.0001"

    # Both ranked artifacts written.
    ranked_dir = tmp_path / "reviews" / "2026-05-16" / "ranked"
    assert {p.name for p in ranked_dir.iterdir()} == {"2026.0001.json", "2026.0002.json"}


def test_pipeline_writes_skip_record_when_top_paper_below_threshold(
    tmp_path: Path, stub_pdf_extractor
):
    paper = _raw("2026.0001", "MODESTMARK Tweak", "rag method abstract")
    filter_decisions = {
        "MODESTMARK": FilterDecision(in_scope=True, primary_topic="rag",
                                     is_review_or_survey=False, note=""),
    }
    ranker_outputs = {
        "MODESTMARK": _ranker_output(5, 5, 5, 5, 5),  # composite 5.0 < 7.0
    }

    storage = LocalFilesystemStorage(tmp_path / "reviews")
    result = run_pipeline(
        run_date=date_cls(2026, 5, 17),
        settings=load_settings(),
        llm=ScriptedLLM(filter_decisions, ranker_outputs),
        paper_source=FakePaperSource([paper]),
        storage=storage,
        embeddings=NullEmbeddings(),
        reviews_dir=tmp_path / "reviews",
    )

    assert result.selected is None
    assert result.skip_record is not None
    skip_file = tmp_path / "reviews" / "2026-05-17" / "skip.json"
    payload = json.loads(skip_file.read_text(encoding="utf-8"))
    assert "post_worthy_threshold" in payload["reason"]
    assert payload["top_paper"]["arxiv_id"] == "2026.0001"
    assert payload["papers_ranked"] == 1


def test_pipeline_writes_skip_record_when_filter_drops_everything(
    tmp_path: Path, stub_pdf_extractor
):
    paper = _raw("2026.0001", "VISIONMARK Things", "image classification")
    filter_decisions = {
        "VISIONMARK": FilterDecision(in_scope=False, primary_topic="other",
                                     is_review_or_survey=False, note="vision"),
    }

    storage = LocalFilesystemStorage(tmp_path / "reviews")
    result = run_pipeline(
        run_date=date_cls(2026, 5, 18),
        settings=load_settings(),
        llm=ScriptedLLM(filter_decisions, {}),
        paper_source=FakePaperSource([paper]),
        storage=storage,
        embeddings=NullEmbeddings(),
        reviews_dir=tmp_path / "reviews",
    )

    assert result.selected is None
    assert result.skip_record is not None
    assert "No papers in scope" in result.skip_record.reason
    skip_file = tmp_path / "reviews" / "2026-05-18" / "skip.json"
    assert skip_file.exists()
