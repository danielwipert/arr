"""Tests for the YAML config loader."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from pydantic import ValidationError

from arr.config import DEFAULT_CONFIG_PATH, load_settings


def test_default_config_loads_cleanly():
    settings = load_settings(DEFAULT_CONFIG_PATH)
    assert settings.arxiv.categories
    assert settings.selector.post_worthy_threshold == 0.0
    assert sum(settings.ranker.weights.as_dict().values()) == pytest.approx(1.0)


def test_load_settings_rejects_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_settings(tmp_path / "no.yaml")


def test_load_settings_validates_threshold(tmp_path: Path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        textwrap.dedent(
            """
            arxiv:
              categories: [cs.CL]
              lookback_hours: 24
              max_results_per_category: 200
            filter:
              dedup_lookback_days: 30
            ranker:
              weights:
                significance: 0.3
                novelty: 0.25
                reproducibility: 0.2
                clarity: 0.15
                topical_fit: 0.1
            selector:
              post_worthy_threshold: 15.0
            drafter:
              model: x
              max_retries: 3
              length:
                target_min: 1400
                target_max: 1800
                hook_max: 140
                hard_min: 1100
                hard_max: 2000
            critic:
              model: x
            cheap_model: x
            storage:
              reviews_dir: reviews
              cache_dir: .cache
            llm:
              provider: openrouter
              base_url: https://example.invalid
            """
        ).strip(),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_settings(bad)


def test_api_key_picked_up_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-123")
    settings = load_settings()
    assert settings.openrouter_api_key is not None
    assert settings.openrouter_api_key.get_secret_value() == "sk-or-test-123"
