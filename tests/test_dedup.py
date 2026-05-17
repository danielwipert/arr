"""Tests for the dedup back-fill of Stage 2."""

from __future__ import annotations

import json
from datetime import date as date_cls
from datetime import datetime, timezone
from pathlib import Path

import pytest

from arr.config import load_settings
from arr.models import FilteredPaper, ProcessedPaper
from arr.stages import dedup
from arr.stages.dedup import HistoryEntry, apply, load_dedup_history


def _filtered(arxiv_id: str, title: str, abstract: str) -> FilteredPaper:
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


def _processed(arxiv_id: str, title: str, abstract: str) -> ProcessedPaper:
    base = _filtered(arxiv_id, title, abstract)
    return ProcessedPaper(
        **base.model_dump(),
        sections={"abstract": abstract},
        pdf_local_path=f"/tmp/{arxiv_id}.pdf",
        page_count=8,
    )


class DeterministicEmbeddings:
    """Embed each unique text to a fixed unit vector. Matched texts get the same
    vector so cosine similarity is exactly 1.0; otherwise vectors are orthogonal
    so similarity is 0. Equivalent texts collapse to the same bucket."""

    def __init__(self, equivalences: dict[str, str] | None = None) -> None:
        self._equivalences = equivalences or {}
        self._buckets: dict[str, int] = {}

    def _bucket(self, text: str) -> int:
        canonical = self._equivalences.get(text, text)
        if canonical not in self._buckets:
            self._buckets[canonical] = len(self._buckets)
        return self._buckets[canonical]

    def embed(self, texts: list[str]) -> list[list[float]]:
        size = 16
        out = []
        for t in texts:
            v = [0.0] * size
            v[self._bucket(t) % size] = 1.0
            out.append(v)
        return out


def test_apply_with_no_history_passes_everything_through():
    settings = load_settings()
    papers = [_filtered("a", "Title A", "Abstract A"), _filtered("b", "Title B", "Abstract B")]
    out = apply(papers, DeterministicEmbeddings(), [], settings)
    assert len(out) == 2
    assert all(p.dedup_similarity is None for p in out)


def test_apply_drops_paper_above_similarity_threshold():
    settings = load_settings()
    candidate = _filtered("new", "Query Decomposition for RAG", "We propose decomposition.")
    history = [HistoryEntry(arxiv_id="old", text="Query Decomposition for RAG\n\nWe propose decomposition.")]
    embeddings = DeterministicEmbeddings(
        equivalences={
            # Force candidate text to bucket-equal the history entry.
            "Query Decomposition for RAG\n\nWe propose decomposition.":
                "Query Decomposition for RAG\n\nWe propose decomposition.",
        }
    )
    out = apply([candidate], embeddings, history, settings)
    assert out == []


def test_apply_keeps_unique_paper_and_records_max_similarity():
    settings = load_settings()
    candidate = _filtered("new", "Something Totally Different", "Other content entirely.")
    history = [HistoryEntry(arxiv_id="old", text="Unrelated old title\n\nUnrelated old abstract.")]
    out = apply([candidate], DeterministicEmbeddings(), history, settings)
    assert len(out) == 1
    assert out[0].dedup_similarity == pytest.approx(0.0)


def test_apply_empty_papers_returns_empty():
    settings = load_settings()
    out = apply([], DeterministicEmbeddings(), [HistoryEntry("x", "y")], settings)
    assert out == []


# --- load_dedup_history --------------------------------------------------


def test_load_dedup_history_reads_processed_jsons(tmp_path: Path):
    reviews = tmp_path / "reviews"
    today = date_cls(2026, 5, 16)

    # Day within lookback.
    day1 = reviews / "2026-05-15" / "processed"
    day1.mkdir(parents=True)
    payload = _processed("2026.A", "Title A", "Abstract A").model_dump(mode="json")
    (day1 / "2026.A.json").write_text(json.dumps(payload), encoding="utf-8")

    # Day older than 30 days — should be excluded.
    day_old = reviews / "2026-04-01" / "processed"
    day_old.mkdir(parents=True)
    payload_old = _processed("2026.B", "Title B", "Abstract B").model_dump(mode="json")
    (day_old / "2026.B.json").write_text(json.dumps(payload_old), encoding="utf-8")

    entries = load_dedup_history(reviews, lookback_days=30, today=today)
    ids = sorted(e.arxiv_id for e in entries)
    assert ids == ["2026.A"]


def test_load_dedup_history_excludes_today(tmp_path: Path):
    reviews = tmp_path / "reviews"
    today = date_cls(2026, 5, 16)
    day_today = reviews / today.isoformat() / "processed"
    day_today.mkdir(parents=True)
    payload = _processed("2026.X", "Today's Paper", "...").model_dump(mode="json")
    (day_today / "2026.X.json").write_text(json.dumps(payload), encoding="utf-8")

    entries = load_dedup_history(reviews, lookback_days=30, today=today)
    assert entries == []


def test_load_dedup_history_handles_missing_dir(tmp_path: Path):
    entries = load_dedup_history(tmp_path / "does-not-exist", 30, date_cls(2026, 5, 16))
    assert entries == []


def test_load_dedup_history_skips_corrupt_json(tmp_path: Path):
    reviews = tmp_path / "reviews"
    today = date_cls(2026, 5, 16)
    day = reviews / "2026-05-15" / "processed"
    day.mkdir(parents=True)
    (day / "bad.json").write_text("{ not json", encoding="utf-8")
    good_payload = _processed("2026.A", "Good", "Good").model_dump(mode="json")
    (day / "2026.A.json").write_text(json.dumps(good_payload), encoding="utf-8")
    entries = load_dedup_history(reviews, 30, today)
    assert [e.arxiv_id for e in entries] == ["2026.A"]
