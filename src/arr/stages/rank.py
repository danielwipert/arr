"""Stage 4 — Ranker.

One cheap-LLM call per paper returns five DimensionScores. The composite is
computed locally from the configured weights, so the LLM isn't asked to do
arithmetic it can get wrong. The composite formula (Section 4.5) is:

    composite = significance*0.30 + novelty*0.25 + reproducibility*0.20
              + clarity*0.15 + topical_fit*0.10

The ranker reads title + abstract only. Full PDF sections are reserved for
the winning paper's drafter/critic — ranking on the abstract keeps the
per-paper cost ~10x lower and the daily wall time ~5x faster, because we
no longer download/extract every survivor's PDF before scoring.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel, ConfigDict

from arr.config import REPO_ROOT, Settings
from arr.models import DimensionScore, FilteredPaper, RankedPaper
from arr.providers.llm import LLMError, LLMProvider
from arr.stages._prompts import render

log = logging.getLogger(__name__)

PROMPT_PATH = REPO_ROOT / "config" / "prompts" / "ranker.md"


class RankerOutput(BaseModel):
    """Shape returned by the LLM. Mirrors the five spec dimensions."""

    model_config = ConfigDict(extra="forbid")

    significance: DimensionScore
    novelty: DimensionScore
    reproducibility: DimensionScore
    clarity: DimensionScore
    topical_fit: DimensionScore

    def as_scores_dict(self) -> dict[str, DimensionScore]:
        return {
            "significance": self.significance,
            "novelty": self.novelty,
            "reproducibility": self.reproducibility,
            "clarity": self.clarity,
            "topical_fit": self.topical_fit,
        }


def compute_composite(
    scores: dict[str, DimensionScore], weights: dict[str, float]
) -> float:
    """Weighted sum of the five dimensions on a 0–10 scale."""
    total = 0.0
    for key, weight in weights.items():
        total += scores[key].score * weight
    # Clamp away tiny float noise so values stay inside the schema bounds.
    return max(0.0, min(10.0, round(total, 4)))


def _render_prompt(paper: FilteredPaper) -> str:
    return render(
        PROMPT_PATH.read_text(encoding="utf-8"),
        title=paper.title,
        abstract=paper.abstract,
    )


def _rank_one(
    paper: FilteredPaper, llm: LLMProvider, settings: Settings
) -> RankedPaper | None:
    try:
        output = llm.complete_json(
            [{"role": "user", "content": _render_prompt(paper)}],
            model=settings.cheap_model,
            schema=RankerOutput,
            temperature=0.0,
        )
    except LLMError as e:
        log.warning("Rank %s: LLM call failed (%s); dropping", paper.arxiv_id, e)
        return None

    scores = output.as_scores_dict()
    composite = compute_composite(scores, settings.ranker.weights.as_dict())

    return RankedPaper(
        **paper.model_dump(),
        scores=scores,
        composite=composite,
    )


def run(
    papers: list[FilteredPaper], llm: LLMProvider, settings: Settings
) -> list[RankedPaper]:
    out: list[RankedPaper] = []
    for paper in papers:
        ranked = _rank_one(paper, llm, settings)
        if ranked is not None:
            out.append(ranked)
    out.sort(key=lambda p: p.composite, reverse=True)
    if out:
        log.info(
            "Rank: top composite %.2f (%s); ranked %d papers",
            out[0].composite, out[0].arxiv_id, len(out),
        )
    else:
        log.info("Rank: no papers ranked")
    return out
