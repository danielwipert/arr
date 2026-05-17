"""Inter-stage artifact models for the ARR pipeline.

Every model in this file corresponds to a stage output in Section 9 of the
spec. Each stage writes its artifact to disk as JSON before the next stage
runs, so the pipeline can be resumed from any stage.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Topic strings the filter and ranker use. Adjacent to the in-scope topics in
# Section 3.2 of the spec; "other" means out of scope.
InScopeTopic = Literal[
    "llm_capabilities",
    "rag",
    "applied_llm_systems",
    "evaluation",
    "post_training",
    "adjacent_infrastructure",
    "other",
]

PassFail = Literal["pass", "fail"]


class StageArtifact(BaseModel):
    """Common config for all artifact models."""

    model_config = ConfigDict(extra="forbid", frozen=False)


# ---------------------------------------------------------------------------
# Stage 1 — Ingestor
# ---------------------------------------------------------------------------


class RawPaper(StageArtifact):
    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    primary_cat: str
    all_cats: list[str]
    submitted_at: datetime
    pdf_url: str


# ---------------------------------------------------------------------------
# Stage 2 — Filter
# ---------------------------------------------------------------------------


class FilteredPaper(RawPaper):
    in_scope: bool
    primary_topic: InScopeTopic
    dedup_similarity: float | None = None
    noise_flagged: bool = False


# ---------------------------------------------------------------------------
# Stage 3 — Processor
# ---------------------------------------------------------------------------

SectionKey = Literal[
    "title",
    "abstract",
    "intro",
    "method",
    "experiments",
    "results",
    "limitations",
    "conclusions",
    "references",
]


class ProcessedPaper(FilteredPaper):
    sections: dict[str, str]
    pdf_local_path: str
    page_count: int


# ---------------------------------------------------------------------------
# Stage 4 — Ranker
# ---------------------------------------------------------------------------


class DimensionScore(StageArtifact):
    score: int = Field(ge=0, le=10)
    justification: str


DimensionKey = Literal[
    "significance",
    "novelty",
    "reproducibility",
    "clarity",
    "topical_fit",
]


class RankedPaper(ProcessedPaper):
    scores: dict[str, DimensionScore]
    composite: float = Field(ge=0.0, le=10.0)


# ---------------------------------------------------------------------------
# Stage 6 — Drafter
# ---------------------------------------------------------------------------


class Claim(StageArtifact):
    """A factual claim in the post text, traceable to a verbatim paper span."""

    claim: str
    source_span: str
    page: int = Field(ge=1)


class DraftPost(StageArtifact):
    paper: RankedPaper
    post_text: str
    claims: list[Claim]
    char_count: int
    hook_char_count: int
    drafter_model: str
    attempt: int = Field(ge=1, le=3)


# ---------------------------------------------------------------------------
# Stage 7 — Critic
# ---------------------------------------------------------------------------


class CheckResult(StageArtifact):
    result: PassFail
    note: str


class CriticReport(StageArtifact):
    voice_match: CheckResult
    banned_phrase_scan: CheckResult
    length_compliance: CheckResult
    structure: CheckResult
    grounding: CheckResult
    hype_check: CheckResult
    overall_pass: bool
    critic_model: str


# ---------------------------------------------------------------------------
# Stage 8 — Finalizer (Sections 6.1 & 6.2)
# ---------------------------------------------------------------------------


class RankerScores(StageArtifact):
    significance: int = Field(ge=0, le=10)
    novelty: int = Field(ge=0, le=10)
    reproducibility: int = Field(ge=0, le=10)
    clarity: int = Field(ge=0, le=10)
    topical_fit: int = Field(ge=0, le=10)
    composite: float = Field(ge=0.0, le=10.0)


class FinalCriticReport(StageArtifact):
    """Flat form of CriticReport that lands in the FinalPost artifact."""

    voice_match: PassFail
    banned_phrase_scan: PassFail
    length_compliance: PassFail
    structure: PassFail
    grounding: PassFail
    hype_check: PassFail
    retries_used: int = Field(ge=0, le=3)
    notes: str


class FinalPost(StageArtifact):
    """Section 6.1 — the artifact written to reviews/YYYY-MM-DD/final_post.json."""

    date: str  # YYYY-MM-DD
    paper_id: str
    paper_title: str
    paper_authors: list[str]
    paper_url: str

    post_text: str
    post_char_count: int
    hook_char_count: int

    claims: list[Claim]
    ranker_scores: RankerScores
    critic_report: FinalCriticReport

    generated_at: datetime
    drafter_model: str
    critic_model: str


class SkipTopPaper(StageArtifact):
    arxiv_id: str
    title: str
    composite: float


class SkipRecord(StageArtifact):
    """Section 6.2 — written instead of FinalPost on skip days."""

    date: str  # YYYY-MM-DD
    papers_considered: int
    papers_filtered: int
    papers_ranked: int
    top_paper: SkipTopPaper | None = None
    reason: str
