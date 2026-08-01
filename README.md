# ARR — AI Research Radar / LinkedIn Drafter

A daily pipeline that selects post-worthy AI research papers from arXiv and drafts a LinkedIn post in a Financial Times meets New Yorker voice, ready for human review.

The product runs once per day, ingests recent arXiv papers in the LLM and applied-AI space, selects at most one paper of the day, and produces a finished draft with grounded factual claims. Nothing is published automatically. The human reviews, edits if needed, and posts manually.

See `planning/ARR_LinkedIn_Drafter_v1_Spec.docx` for the full specification.

## Status

**Phase 4 — End-to-End Pipeline & Evaluation Loop (Complete & Verified)**

The system is fully implemented and operational:
- **Ingestion & Pre-filtering**: Smart retrieval with automatic lookback widening on quiet days and cheap lexical pre-screening.
- **Topical / Noise Filtering**: Automated classification using cost-effective LLMs (`deepseek-chat-v3.1`) and high-performance multi-threaded concurrency.
- **Lazy PDF Processing**: Smart two-column text extraction (`pdfplumber`) executed only on the chosen winning paper of the day.
- **Weighted Ranking**: Five-dimension evaluation (Significance, Novelty, Reproducibility, Clarity, and Topical Fit) combined deterministically.
- **Grounded LinkedIn Drafting**: Fact-grounded premium drafting with verbatim page tracing.
- **Robust Critic & Retry Loop**: Holistic soft LLM checks layered with strict, deterministic python/regex mechanical checks (length limits, single-line hooks, no banned buzzwords/bolding/emojis).
- **Failsafe Finalization**: Accepts final draft attempt if critic limits are hit, appending critiques for human review.
- **Self-Cleaning Storage**: Automatic 7-day review retention, same-date rerun stale-file sweep, and orphan cache cleanup.

## Quickstart

```bash
# Install package and dev/testing dependencies in editable mode
pip install -e ".[dev]"

# Run the test suite to verify implementation
python -m pytest

# Check the default configuration
arr config-check

# Run the daily pipeline for the current date (requires OPENROUTER_API_KEY)
arr run --date today
```

## Layout

```text
src/arr/
  config.py        # Pydantic Settings, loads config/default.yaml & env variables
  models.py        # Serde-ready inter-stage Pydantic schemas (Section 9 of spec)
  providers/       # Adapters for external LLM, arXiv feed, and local storage
    llm.py         # OpenRouter client with JSON auto-recovery & retry logic
    papers.py      # arXiv API feed search client & PDF downloader
    storage.py     # Local review file layout manager
  stages/          # Isolated modules for each pipeline stage
    ingest.py      # Stage 1: arXiv API paper ingestion
    filter.py      # Stage 2: Keyword prefilter & LLM topic classification
    dedup.py       # Stage 2 (Backfill): ID deduplication from last 7 days
    process.py     # Stage 3: Section segmentation and column layout extraction
    rank.py        # Stage 4: Abstract-only weighted ranking
    select.py      # Stage 5: Gated top paper selection
    draft.py       # Stage 6: Grounded LinkedIn post generation
    critique.py    # Stage 7: LLM voice evaluation with mechanical overrides
    finalize.py    # Stage 8: Drafter-Critic retry loop & reviewer file builder
  pipeline.py      # End-to-end orchestration, folder retention, and cleanup
  cli.py           # Command Line Interface (run, config-check, lookback overloads)
config/
  default.yaml     # Single source of truth for runtime configuration
  prompts/         # Prompts for filter, ranker, drafter, and critic stages
reviews/           # Daily output folders (pruned after 7 days)
```

## Pipeline stages

1. **Ingestor** — Pull arXiv submissions from configured categories with automatic lookback widening.
2. **Filter** — Run lexical pre-screening, exact ID deduplication, and cheap-model LLM classification.
3. **Processor** — Adaptive single/two-column PDF text extraction and section segmentation.
4. **Ranker** — Score on Significance, Novelty, Reproducibility, Clarity, and Topical Fit; compute composite score in code.
5. **Selector** — Gate selection against a post-worthy threshold; generate comprehensive skip reasons when none qualify.
6. **Drafter** — Generate premium draft with page-traced verbatim grounding claims.
7. **Critic** — Grade on voice, grounding, length, structure, and banned expressions with rigid mechanical regex overrides.
8. **Finalizer** — Manage up to N retries (providing feedback notes to the next draft attempt) and build final Markdown/JSON assets.

## Testing

The repository has an extensive and strict unit test suite checking all configurations, models, logic boundaries, and staging behaviors. Run all tests with:

```bash
python -m pytest
```

## License

Proprietary. Daniel Wipert / Chorus AI Systems.
