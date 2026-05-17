"""Tests for `_remove_stale_artifacts`.

Same-date reruns are routine (manual workflow_dispatch, weekend backfill).
Without cleanup, a folder ends up with both yesterday's `post.md` and
today's `skip.json` — exactly the misleading state a reviewer cannot
reason about. These tests pin down the cleanup contract.
"""

from __future__ import annotations

from pathlib import Path

from arr.pipeline import _POST_STALE, _SKIP_STALE, _remove_stale_artifacts


def _seed_day_folder(folder: Path) -> None:
    folder.mkdir(parents=True)
    (folder / "post.md").write_text("stale post body", encoding="utf-8")
    (folder / "final_post.json").write_text("{}", encoding="utf-8")
    (folder / "grounding.md").write_text("stale grounding", encoding="utf-8")
    (folder / "paper.pdf").write_bytes(b"%PDF-1.4 stale")
    (folder / "skip.json").write_text("{}", encoding="utf-8")
    drafts = folder / "drafts"
    drafts.mkdir()
    (drafts / "attempt_1.json").write_text("{}", encoding="utf-8")
    (folder / "selected.json").write_text("{}", encoding="utf-8")


def test_skip_path_removes_post_artifacts_only(tmp_path: Path):
    day = tmp_path / "reviews" / "2026-05-17"
    _seed_day_folder(day)

    _remove_stale_artifacts(day, _SKIP_STALE)

    # Post artifacts gone.
    assert not (day / "post.md").exists()
    assert not (day / "final_post.json").exists()
    assert not (day / "grounding.md").exists()
    assert not (day / "paper.pdf").exists()
    # Skip artifacts and selected.json preserved — today's run owns them.
    assert (day / "skip.json").exists()
    assert (day / "drafts" / "attempt_1.json").exists()
    assert (day / "selected.json").exists()


def test_post_path_removes_skip_artifacts_only(tmp_path: Path):
    day = tmp_path / "reviews" / "2026-05-17"
    _seed_day_folder(day)

    _remove_stale_artifacts(day, _POST_STALE)

    # Skip artifacts gone.
    assert not (day / "skip.json").exists()
    assert not (day / "drafts").exists()
    # Post artifacts and selected.json preserved.
    assert (day / "post.md").exists()
    assert (day / "final_post.json").exists()
    assert (day / "grounding.md").exists()
    assert (day / "paper.pdf").exists()
    assert (day / "selected.json").exists()


def test_cleanup_is_a_no_op_when_targets_absent(tmp_path: Path):
    day = tmp_path / "reviews" / "2026-05-17"
    day.mkdir(parents=True)
    # Only a stray file exists; the cleanup should not raise.
    (day / "selected.json").write_text("{}", encoding="utf-8")

    _remove_stale_artifacts(day, _SKIP_STALE)
    _remove_stale_artifacts(day, _POST_STALE)

    assert (day / "selected.json").exists()
