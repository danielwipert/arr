"""Stage 2 — Filter.

Drops out-of-scope and obvious-noise papers before the expensive PDF
processing stage. Three sub-filters in the spec:

1. Topical filter (LLM call) — `in_scope`, `primary_topic`
2. Noise filter — regex keyword pre-screen, then LLM "methodology vs review"
3. Dedup filter — Phase 3 wire-up; field stays `None` here

We collapse the topical and noise LLM calls into one round-trip per paper:
the cheap-model call returns both signals plus a one-sentence note. That
keeps per-paper cost in the same ballpark the spec budgeted for.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from arr.config import REPO_ROOT, Settings
from arr.models import FilteredPaper, InScopeTopic, RawPaper
from arr.providers.llm import LLMError, LLMProvider
from arr.stages._prompts import render

log = logging.getLogger(__name__)

PROMPT_PATH = REPO_ROOT / "config" / "prompts" / "filter.md"

# Cheap pre-screen for obvious survey / workshop / opinion markers in the title
# or the opening of the abstract. The LLM still gets a chance to overrule on
# topical fit, but a paper that trips the regex is flagged as noise up front
# and the LLM is asked to confirm.
_NOISE_PATTERNS = [
    r"\ba survey of\b",
    r"\bsurvey on\b",
    r"\bsystematic review\b",
    r"\bposition paper\b",
    r"\bopinion piece\b",
    r"\bworkshop (track|paper|short)\b",
    r"\bextended abstract\b",
    r"\btutorial(\s+paper)?\b",
]
_NOISE_REGEX = re.compile("|".join(_NOISE_PATTERNS), flags=re.IGNORECASE)


class FilterDecision(BaseModel):
    """LLM-shaped output for the combined topical + noise classification."""

    model_config = ConfigDict(extra="forbid")

    in_scope: bool
    primary_topic: InScopeTopic
    is_review_or_survey: bool
    note: str = ""


def _regex_flags_noise(paper: RawPaper) -> bool:
    head = f"{paper.title}\n\n{paper.abstract[:500]}"
    return bool(_NOISE_REGEX.search(head))


def _classify(llm: LLMProvider, paper: RawPaper, model: str) -> FilterDecision:
    prompt_text = render(
        PROMPT_PATH.read_text(encoding="utf-8"),
        title=paper.title,
        abstract=paper.abstract,
    )
    return llm.complete_json(
        [{"role": "user", "content": prompt_text}],
        model=model,
        schema=FilterDecision,
        temperature=0.0,
    )


def run(
    papers: list[RawPaper],
    llm: LLMProvider,
    settings: Settings,
    *,
    prompt_path: Path | None = None,
) -> list[FilteredPaper]:
    """Filter papers down to those that are in scope and not noise.

    Returns a list of `FilteredPaper` for the survivors. Dropped papers are
    logged at DEBUG with their reason.
    """
    global PROMPT_PATH
    if prompt_path is not None:
        PROMPT_PATH = prompt_path

    survivors: list[FilteredPaper] = []
    for paper in papers:
        regex_flag = _regex_flags_noise(paper)
        try:
            decision = _classify(llm, paper, settings.cheap_model)
        except LLMError as e:
            log.warning("Filter LLM call failed for %s (%s); dropping", paper.arxiv_id, e)
            continue

        noise_flagged = regex_flag or decision.is_review_or_survey

        if not decision.in_scope:
            log.debug(
                "Filter drop %s: out of scope (topic=%s, note=%s)",
                paper.arxiv_id,
                decision.primary_topic,
                decision.note,
            )
            continue
        if noise_flagged:
            log.debug(
                "Filter drop %s: noise (regex=%s, survey=%s, note=%s)",
                paper.arxiv_id,
                regex_flag,
                decision.is_review_or_survey,
                decision.note,
            )
            continue

        survivors.append(
            FilteredPaper(
                **paper.model_dump(),
                in_scope=True,
                primary_topic=decision.primary_topic,
                dedup_similarity=None,
                noise_flagged=False,
            )
        )

    log.info("Filter: %d/%d papers survived", len(survivors), len(papers))
    return survivors
