"""Command-line entrypoint for the ARR pipeline.

As of Phase 2 the CLI runs stages 1–3 end-to-end and writes ProcessedPaper
JSON artifacts under `reviews/YYYY-MM-DD/processed/`. Ranking, drafting,
critique, and finalisation arrive in later phases.

    python -m arr.cli run --date today
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date as date_cls
from datetime import datetime, timedelta, timezone
from pathlib import Path

from arr.config import DEFAULT_CONFIG_PATH, REPO_ROOT, Settings, load_settings
from arr.pipeline import PipelineResult, run_pipeline
from arr.providers.embeddings import LocalSentenceTransformerEmbeddings
from arr.providers.llm import OpenRouterLLM
from arr.providers.papers import ArxivPaperSource
from arr.providers.storage import LocalFilesystemStorage

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
    run.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't construct LLM/arXiv providers; just validate config and exit.",
    )

    sub.add_parser("config-check", help="Load and print config, then exit.")

    return parser


def cmd_run(args: argparse.Namespace, settings: Settings) -> int:
    run_date: date_cls = (
        args.date if isinstance(args.date, date_cls) else _parse_date(args.date)
    )

    if args.dry_run:
        print(
            f"[arr] Dry run: config valid, no pipeline executed "
            f"(target date: {run_date.isoformat()})."
        )
        return 0

    if settings.openrouter_api_key is None:
        print(
            "[arr] OPENROUTER_API_KEY is not set; pipeline cannot run.\n"
            "      Set it in your environment or in a .env file (see .env.example).",
            file=sys.stderr,
        )
        return 2

    cache_dir = REPO_ROOT / settings.storage.cache_dir
    reviews_dir = REPO_ROOT / settings.storage.reviews_dir

    log.info("Run starting for %s", run_date.isoformat())
    log.info(
        "Categories: %s | threshold: %.1f | drafter: %s",
        ", ".join(settings.arxiv.categories),
        settings.selector.post_worthy_threshold,
        settings.drafter.model,
    )

    paper_source = ArxivPaperSource(
        cache_dir,
        max_results_per_category=settings.arxiv.max_results_per_category,
    )
    storage = LocalFilesystemStorage(reviews_dir)
    embeddings = LocalSentenceTransformerEmbeddings(settings.filter.embedding_model)

    with OpenRouterLLM(
        settings.openrouter_api_key.get_secret_value(),
        base_url=settings.llm.base_url,
    ) as llm:
        result: PipelineResult = run_pipeline(
            run_date, settings, llm, paper_source, storage, embeddings, reviews_dir
        )

    day_dir = reviews_dir / run_date.isoformat()
    print(
        f"[arr] Run complete for {run_date.isoformat()}: "
        f"ingested={result.raw_count}, "
        f"filtered={result.filtered_count}, "
        f"deduped={result.deduped_count}, "
        f"processed={result.processed_count}, "
        f"ranked={result.ranked_count}"
    )
    if result.final_post is not None:
        print(
            f"[arr] POST DRAFTED: {result.selected.arxiv_id} — {result.final_post.paper_title!r}"
        )
        print(
            f"      composite={result.selected.composite:.2f}, "
            f"chars={result.final_post.post_char_count}, "
            f"hook={result.final_post.hook_char_count}, "
            f"retries={result.final_post.critic_report.retries_used}"
        )
        print(f"[arr] Review folder: {day_dir}")
        print(f"      post.md, final_post.json, grounding.md, paper.pdf")
    else:
        assert result.skip_record is not None
        print(f"[arr] SKIP: {result.skip_record.reason}")
        print(f"[arr] Artifact: {day_dir / 'skip.json'}")
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
    # On Windows the default stdout codec is cp1252, which crashes on any
    # Unicode that LLM responses or paper titles routinely contain.
    for stream in (sys.stdout, sys.stderr):
        if getattr(stream, "encoding", "").lower() != "utf-8":
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
            except (AttributeError, ValueError):
                pass

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
