"""Command-line entrypoint for the ARR pipeline.

In Phase 1 the CLI only loads config and reports back. Pipeline stages are
wired up in subsequent phases. The Section 11 / Phase 1 acceptance criterion
is:

    python -m arr.cli run --date today

exits cleanly with a 'not implemented' message and a validated config.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date as date_cls
from datetime import datetime, timedelta, timezone
from pathlib import Path

from arr.config import DEFAULT_CONFIG_PATH, Settings, load_settings

log = logging.getLogger("arr.cli")


def _parse_date(value: str) -> date_cls:
    """Accepts 'today', 'yesterday', or an ISO YYYY-MM-DD string."""
    v = value.strip().lower()
    if v == "today":
        return datetime.now(timezone.utc).date()
    if v == "yesterday":
        return (datetime.now(timezone.utc) - timedelta(days=1)).date()
    try:
        return date_cls.fromisoformat(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"--date must be 'today', 'yesterday', or YYYY-MM-DD; got {value!r}"
        ) from e


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arr",
        description="AI Research Radar — LinkedIn Drafter daily pipeline.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help=f"Path to YAML config file (default: {DEFAULT_CONFIG_PATH}).",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run the daily pipeline for a given date.")
    run.add_argument(
        "--date",
        type=_parse_date,
        default="today",
        help="Date to run for: 'today', 'yesterday', or YYYY-MM-DD.",
    )

    sub.add_parser("config-check", help="Load and print config, then exit.")

    return parser


def cmd_run(args: argparse.Namespace, settings: Settings) -> int:
    run_date: date_cls = args.date if isinstance(args.date, date_cls) else _parse_date(args.date)
    log.info("Run requested for %s", run_date.isoformat())
    log.info(
        "Categories: %s | threshold: %.1f | drafter: %s",
        ", ".join(settings.arxiv.categories),
        settings.selector.post_worthy_threshold,
        settings.drafter.model,
    )
    print(
        f"[arr] Phase 1 build: pipeline stages not implemented yet "
        f"(target date: {run_date.isoformat()}). Config loaded OK."
    )
    return 0


def cmd_config_check(_: argparse.Namespace, settings: Settings) -> int:
    print("[arr] Config loaded successfully.")
    print(f"  categories      = {', '.join(settings.arxiv.categories)}")
    print(f"  threshold       = {settings.selector.post_worthy_threshold}")
    print(f"  drafter model   = {settings.drafter.model}")
    print(f"  critic model    = {settings.critic.model}")
    print(f"  cheap model     = {settings.cheap_model}")
    print(f"  reviews dir     = {settings.storage.reviews_dir}")
    print(
        "  openrouter key  = "
        + ("set" if settings.openrouter_api_key else "NOT SET (expected in env)")
    )
    return 0


COMMANDS = {
    "run": cmd_run,
    "config-check": cmd_config_check,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
    )

    try:
        settings = load_settings(args.config)
    except FileNotFoundError as e:
        print(f"[arr] {e}", file=sys.stderr)
        return 2
    except Exception as e:  # pydantic ValidationError, etc.
        print(f"[arr] Config error: {e}", file=sys.stderr)
        return 2

    return COMMANDS[args.command](args, settings)


if __name__ == "__main__":
    raise SystemExit(main())
