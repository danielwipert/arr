"""Tests for Stage 5 selector + SkipRecord builder."""

from __future__ import annotations

from datetime import date as date_cls
from datetime import datetime, timezone

import pytest

from arr.config import load_settings
from arr.models import DimensionScore, RankedPaper
from arr.stages.select import build_skip_record, select_top


def _ranked(arxiv_id: str, composite: float) -> RankedPaper:
    scores = {
        "significance": DimensionScore(score=int(composite), justification="."),
        "novelty": DimensionScore(score=int(composite), justification="."),
        "reproducibility": DimensionScore(score=int(composite), justification="."),
        "clarity": DimensionScore(score=int(composite), justification="."),
        "topical_fit": DimensionScore(score=int(composite), justification="."),
    }
    return RankedPaper(
        arxiv_id=arxiv_id,
        title=f"Paper {arxiv_id}",
        authors=["A. Researcher"],
        abstract="...",
        primary_cat="cs.CL",
        all_cats=["cs.CL"],
        submitted_at=datetime(2026, 5, 16, 12, 0, tzinfo=timezone.utc),
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
        in_scope=True,
        primary_topic="rag",
        dedup_similarity=None,
        noise_flagged=False,
        scores=scores,
        composite=composite,
    )


def test_selects_top_when_above_threshold():
    settings = load_settings()
    papers = [_ranked("a", 6.5), _ranked("b", 8.2), _ranked("c", 7.0)]
    chosen = select_top(papers, settings)
    assert chosen is not None
    assert chosen.arxiv_id == "b"


def test_selects_at_exact_threshold():
    settings = load_settings()
    papers = [_ranked("a", 7.0)]
    chosen = select_top(papers, settings)
    assert chosen is not None
    assert chosen.arxiv_id == "a"


def _with_threshold(settings, threshold: float):
    return settings.model_copy(
        update={"selector": settings.selector.model_copy(update={"post_worthy_threshold": threshold})}
    )


def test_returns_none_when_top_below_threshold():
    # Default threshold is 0.0; override to exercise the gate.
    settings = _with_threshold(load_settings(), 7.0)
    papers = [_ranked("a", 6.9), _ranked("b", 5.0)]
    assert select_top(papers, settings) is None


def test_returns_none_when_no_ranked_papers():
    settings = load_settings()
    assert select_top([], settings) is None


def test_skip_record_with_top_below_threshold():
    settings = _with_threshold(load_settings(), 7.0)
    ranked = [_ranked("a", 6.4), _ranked("b", 5.2)]
    record = build_skip_record(
        run_date=date_cls(2026, 5, 17),
        papers_considered=37,
        papers_filtered=3,
        ranked=ranked,
        settings=settings,
    )
    assert record.date == "2026-05-17"
    assert record.papers_considered == 37
    assert record.papers_filtered == 3
    assert record.papers_ranked == 2
    assert record.top_paper is not None
    assert record.top_paper.arxiv_id == "a"
    assert record.top_paper.composite == pytest.approx(6.4)
    assert "post_worthy_threshold" in record.reason
    assert "6.40" in record.reason


def test_skip_record_when_filter_dropped_everything():
    settings = load_settings()
    record = build_skip_record(
        run_date=date_cls(2026, 5, 17),
        papers_considered=37,
        papers_filtered=0,
        ranked=[],
        settings=settings,
    )
    assert record.top_paper is None
    assert "No papers in scope" in record.reason


def test_skip_record_when_all_rankers_errored():
    settings = load_settings()
    record = build_skip_record(
        run_date=date_cls(2026, 5, 17),
        papers_considered=37,
        papers_filtered=3,
        ranked=[],
        settings=settings,
    )
    assert record.top_paper is None
    assert "failed to rank" in record.reason
