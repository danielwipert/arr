"""Tests for the local-filesystem storage provider."""

from __future__ import annotations

import json
from datetime import date as date_cls
from pathlib import Path

from arr.models import SkipRecord, SkipTopPaper
from arr.providers.storage import LocalFilesystemStorage


def test_write_artifact_creates_per_day_folder(tmp_path: Path):
    storage = LocalFilesystemStorage(tmp_path / "reviews")
    skip = SkipRecord(
        date="2026-05-17",
        papers_considered=37,
        papers_filtered=34,
        papers_ranked=3,
        top_paper=SkipTopPaper(arxiv_id="2026.99999", title="x", composite=6.4),
        reason="below threshold",
    )

    path = storage.write_artifact(date_cls(2026, 5, 17), "skip", skip)

    assert path == tmp_path / "reviews" / "2026-05-17" / "skip.json"
    assert path.exists()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["papers_considered"] == 37


def test_write_post_and_text(tmp_path: Path):
    storage = LocalFilesystemStorage(tmp_path / "reviews")
    post = storage.write_post(date_cls(2026, 5, 16), "Hello world.")
    grounding = storage.write_text(date_cls(2026, 5, 16), "grounding.md", "claim → span")

    assert post.read_text(encoding="utf-8") == "Hello world."
    assert grounding.read_text(encoding="utf-8") == "claim → span"


def test_write_pdf(tmp_path: Path):
    storage = LocalFilesystemStorage(tmp_path / "reviews")
    pdf_path = storage.write_pdf(date_cls(2026, 5, 16), b"%PDF-1.4 mock")
    assert pdf_path.read_bytes().startswith(b"%PDF-1.4")
