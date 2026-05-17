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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from arr.config import REPO_ROOT, Settings
from arr.models import FilteredPaper, InScopeTopic, RawPaper
from arr.providers.llm import LLMError, LLMProvider
from arr.stages._prompts import render

log = logging.getLogger(__name__)

PROMPT_PATH = REPO_ROOT / "config" / "prompts" / "filter.md"

# Concurrent in-flight Haiku calls during the filter fan-out. Six is well
# under OpenRouter's rate ceiling for the cheap tier and collapses the
# minutes of serial idle wait that dominated wall time on daily runs.
_FILTER_WORKERS = 6

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


def _matches_keyword_prefilter(paper: RawPaper, keywords: list[str]) -> bool:
    """Return True if paper's title+abstract contains at least one keyword.

    Matching is case-insensitive substring. Cheap and crude on purpose — the
    point is to discard papers that don't look LLM-related at all before
    burning a filter LLM call on them.
    """
    if not keywords:
        return True
    haystack = f"{paper.title}\n{paper.abstract}".lower()
    return any(kw.lower() in haystack for kw in keywords)


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


def _classify_safe(
    llm: LLMProvider, paper: RawPaper, model: str
) -> tuple[FilterDecision | None, LLMError | None]:
    """Run `_classify` in a worker without letting LLMError escape the pool.

    Returning the error lets the caller log it against the paper's arxiv_id
    and keep going, matching the pre-parallel drop-on-failure behaviour.
    """
    try:
        return _classify(llm, paper, model), None
    except LLMError as e:
        return None, e


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

    prefilter = settings.filter.keyword_prefilter
    keywords = prefilter.keywords if prefilter.enabled else []
    prefilter_drops = 0

    # First pass: cheap, in-process. Survivors carry the regex noise flag
    # forward so the second pass can apply it without re-running the regex.
    candidates: list[tuple[RawPaper, bool]] = []
    for paper in papers:
        if keywords and not _matches_keyword_prefilter(paper, keywords):
            log.debug("Filter drop %s: no LLM keyword in title+abstract", paper.arxiv_id)
            prefilter_drops += 1
            continue
        candidates.append((paper, _regex_flags_noise(paper)))

    # Second pass: the LLM classification. Each call is independent, so we
    # fan out across a small worker pool. executor.map preserves input order,
    # which keeps the survivor list deterministic.
    if candidates:
        cheap_model = settings.cheap_model
        with ThreadPoolExecutor(max_workers=_FILTER_WORKERS) as executor:
            classify_results = list(executor.map(
                lambda c: _classify_safe(llm, c[0], cheap_model),
                candidates,
            ))
    else:
        classify_results = []

    survivors: list[FilteredPaper] = []
    for (paper, regex_flag), (decision, err) in zip(candidates, classify_results):
        if err is not None:
            log.warning("Filter LLM call failed for %s (%s); dropping", paper.arxiv_id, err)
            continue
        assert decision is not None

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

    log.info(
        "Filter: %d/%d papers survived (prefilter dropped %d)",
        len(survivors), len(papers), prefilter_drops,
    )
    return survivors
