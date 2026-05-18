"""Tests for the arxiv_id-based dedup back-fill of Stage 2."""

from __future__ import annotations

import json
from datetime import date as date_cls
from datetime import datetime, timezone
from pathlib import Path

from arr.config import load_settings
from arr.models import FilteredPaper, ProcessedPaper
from arr.stages.dedup import HistoryEntry, apply, load_dedup_history


def _filtered(arxiv_id: str, title: str = "T", abstract: str = "A") -> FilteredPaper:
    return FilteredPaper(
        arxiv_id=arxiv_id,
        title=title,
        authors=["A. Researcher"],
        abstract=abstract,
        primary_cat="cs.CL",
        all_cats=["cs.CL"],
        submitted_at=datetime(2026, 5, 16, 12, 0, tzinfo=timezone.utc),
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
        in_scope=True,
        primary_topic="rag",
        dedup_similarity=None,
        noise_flagged=False,
    )


def _processed(arxiv_id: str, title: str = "T", abstract: str = "A") -> ProcessedPaper:
    base = _filtered(arxiv_id, title, abstract)
    return ProcessedPaper(
        **base.model_dump(),
        sections={"abstract": abstract},
        pdf_local_path=f"/tmp/{arxiv_id}.pdf",
        page_count=8,
    )


def test_apply_with_no_history_passes_everything_through():
    settings = load_settings()
    papers = [_filtered("a"), _filtered("b")]
    out = apply(papers, [], settings)
    assert [p.arxiv_id for p in out] == ["a", "b"]
    assert all(p.dedup_similarity is None for p in out)


def test_apply_drops_candidates_whose_arxiv_id_appears_in_history():
    settings = load_settings()
    candidates = [_filtered("old-1"), _filtered("new-1")]
    history = [HistoryEntry(arxiv_id="old-1")]
    out = apply(candidates, history, settings)
    assert [p.arxiv_id for p in out] == ["new-1"]


def test_apply_keeps_unique_paper_with_null_similarity_field():
    settings = load_settings()
    candidate = _filtered("brand-new")
    history = [HistoryEntry(arxiv_id="something-else")]
    out = apply([candidate], history, settings)
    assert len(out) == 1
    assert out[0].dedup_similarity is None


def test_apply_empty_papers_returns_empty():
    settings = load_settings()
    assert apply([], [HistoryEntry("x")], settings) == []


# --- load_dedup_history --------------------------------------------------


def test_load_dedup_history_reads_processed_jsons(tmp_path: Path):
    reviews = tmp_path / "reviews"
    today = date_cls(2026, 5, 16)

    day1 = reviews / "2026-05-15" / "processed"
    day1.mkdir(parents=True)
    payload = _processed("2026.A").model_dump(mode="json")
    (day1 / "2026.A.json").write_text(json.dumps(payload), encoding="utf-8")

    # Older than lookback window — excluded.
    day_old = reviews / "2026-04-01" / "processed"
    day_old.mkdir(parents=True)
    payload_old = _processed("2026.B").model_dump(mode="json")
    (day_old / "2026.B.json").write_text(json.dumps(payload_old), encoding="utf-8")

    entries = load_dedup_history(reviews, lookback_days=30, today=today)
    assert sorted(e.arxiv_id for e in entries) == ["2026.A"]


def test_load_dedup_history_excludes_today(tmp_path: Path):
    reviews = tmp_path / "reviews"
    today = date_cls(2026, 5, 16)
    day_today = reviews / today.isoformat() / "processed"
    day_today.mkdir(parents=True)
    payload = _processed("2026.X").model_dump(mode="json")
    (day_today / "2026.X.json").write_text(json.dumps(payload), encoding="utf-8")

    assert load_dedup_history(reviews, lookback_days=30, today=today) == []


def test_load_dedup_history_handles_missing_dir(tmp_path: Path):
    assert load_dedup_history(tmp_path / "nope", 30, date_cls(2026, 5, 16)) == []


def test_load_dedup_history_skips_corrupt_json(tmp_path: Path):
    reviews = tmp_path / "reviews"
    today = date_cls(2026, 5, 16)
    day = reviews / "2026-05-15" / "processed"
    day.mkdir(parents=True)
    (day / "bad.json").write_text("{ not json", encoding="utf-8")
    good_payload = _processed("2026.A").model_dump(mode="json")
    (day / "2026.A.json").write_text(json.dumps(good_payload), encoding="utf-8")
    entries = load_dedup_history(reviews, 30, today)
    assert [e.arxiv_id for e in entries] == ["2026.A"]
