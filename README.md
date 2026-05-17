# ARR — AI Research Radar / LinkedIn Drafter

A daily pipeline that selects post-worthy AI research papers from arXiv and drafts a LinkedIn post in a Financial Times meets New Yorker voice, ready for human review.

The product runs once per day, ingests recent arXiv papers in the LLM and applied-AI space, selects at most one paper of the day, and produces a finished draft with grounded factual claims. Nothing is published automatically. The human reviews, edits if needed, and posts manually.

See `planning/ARR_LinkedIn_Drafter_v1_Spec.docx` for the full specification.

## Status

Phase 1 — Skeleton and Schemas. The CLI loads config and exits cleanly; pipeline stages are not yet implemented.

## Quickstart

```bash
pip install -e ".[dev]"
arr run --date today
```

## Layout

```
src/arr/
  config.py        # Pydantic Settings, loads config/default.yaml
  models.py        # All inter-stage artifact models (Section 9 of spec)
  providers/       # LLM, embeddings, papers, storage interfaces + impls
  stages/          # One module per pipeline stage (Phase 2+)
  pipeline.py      # Orchestration
  cli.py           # Daily run entrypoint
config/
  default.yaml     # Single source of truth for runtime config
  prompts/         # Drafter, critic, ranker, filter prompts (Phase 2+)
reviews/           # Daily output folder (gitignored except .gitkeep)
```

## Pipeline stages

1. Ingestor — pull arXiv submissions from the configured categories
2. Filter — topical, dedup, noise filters
3. Processor — fetch PDF, extract sections
4. Ranker — score on 5 dimensions
5. Selector — pick top paper above the post-worthy threshold (or skip)
6. Drafter — write the LinkedIn post
7. Critic — grade on voice, grounding, length, structure
8. Finalizer — retry loop, write final artifact

## License

Proprietary. Daniel Wipert / Chorus AI Systems.
