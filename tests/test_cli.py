"""Tests for the CLI entrypoint."""

from __future__ import annotations

from datetime import date as date_cls
from datetime import datetime, timezone

import pytest

from arr.cli import _parse_date, build_parser, main


def test_parse_date_today():
    assert _parse_date("today") == datetime.now(timezone.utc).date()


def test_parse_date_yesterday():
    today = datetime.now(timezone.utc).date()
    assert (_parse_date("yesterday") - today).days == -1


def test_parse_date_iso():
    assert _parse_date("2026-05-16") == date_cls(2026, 5, 16)


def test_parse_date_rejects_garbage():
    import argparse
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_date("not-a-date")


def test_parser_requires_subcommand():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_run_exits_clean_with_default_config(capsys: pytest.CaptureFixture[str]):
    exit_code = main(["run", "--date", "today"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "not implemented" in captured.out
    assert "Config loaded OK" in captured.out


def test_run_with_explicit_iso_date(capsys: pytest.CaptureFixture[str]):
    exit_code = main(["run", "--date", "2026-05-16"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "2026-05-16" in captured.out


def test_config_check_command(capsys: pytest.CaptureFixture[str]):
    exit_code = main(["config-check"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Config loaded successfully" in captured.out
    assert "threshold" in captured.out


def test_run_bails_on_missing_config(capsys: pytest.CaptureFixture[str], tmp_path):
    bogus = tmp_path / "nope.yaml"
    exit_code = main(["--config", str(bogus), "run", "--date", "today"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "not found" in captured.err.lower() or "no such" in captured.err.lower()
