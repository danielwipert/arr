"""Tests for the 7-day retention prune of `reviews/<YYYY-MM-DD>/` folders."""

from __future__ import annotations

from datetime import date as date_cls
from pathlib import Path

from arr.pipeline import _prune_old_review_folders


def _make_day(reviews: Path, name: str) -> Path:
    folder = reviews / name
    folder.mkdir(parents=True)
    (folder / "post.md").write_text("placeholder", encoding="utf-8")
    return folder


def test_prune_removes_only_folders_older_than_cutoff(tmp_path: Path):
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    old = _make_day(reviews, "2026-05-01")
    boundary = _make_day(reviews, "2026-05-10")  # exactly 7 days old — kept
    fresh = _make_day(reviews, "2026-05-15")
    today_folder = _make_day(reviews, "2026-05-17")

    _prune_old_review_folders(reviews, date_cls(2026, 5, 17), retention_days=7)

    assert not old.exists()
    assert boundary.exists()
    assert fresh.exists()
    assert today_folder.exists()


def test_prune_ignores_non_date_entries(tmp_path: Path):
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    gitkeep = reviews / ".gitkeep"
    gitkeep.write_text("", encoding="utf-8")
    misc_dir = reviews / "notes"
    misc_dir.mkdir()
    (misc_dir / "scratch.md").write_text("x", encoding="utf-8")
    old = _make_day(reviews, "2026-04-01")

    _prune_old_review_folders(reviews, date_cls(2026, 5, 17), retention_days=7)

    assert gitkeep.exists()
    assert misc_dir.exists()
    assert not old.exists()


def test_prune_is_a_no_op_when_reviews_dir_missing(tmp_path: Path):
    # Should not raise when there's no reviews directory yet.
    _prune_old_review_folders(
        tmp_path / "does-not-exist", date_cls(2026, 5, 17), retention_days=7
    )
