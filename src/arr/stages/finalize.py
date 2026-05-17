"""Stage 8 — Finalizer.

Orchestrates the drafter/critic retry loop and produces the artifacts the
human reviewer reads. Up to `settings.drafter.max_retries` total drafting
attempts. On the first attempt that passes the critic, we build a
FinalPost from the DraftPost + CriticReport + RankerScores. If every
attempt fails, the day becomes a skip with reason
"voice critic failed after N attempts".

Per Section 13: post.md (the ready-to-paste draft) and grounding.md
(the human-readable claim trace) are derived from the FinalPost so the
reviewer never has to look at the JSON unless they want to.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from arr.config import Settings
from arr.models import (
    Claim,
    CriticReport,
    DraftPost,
    FinalCriticReport,
    FinalPost,
    RankedPaper,
    RankerScores,
)
from arr.providers.llm import LLMError, LLMProvider
from arr.stages import critique as critique_stage
from arr.stages import draft as draft_stage

log = logging.getLogger(__name__)


@dataclass
class FinalizerResult:
    """Outcome of the drafter/critic loop.

    `final_post` is set iff some attempt passed the critic. `attempts`
    records each (DraftPost, CriticReport) pair in order, so a skip
    artifact can quote the last attempt's failures.
    """

    final_post: FinalPost | None
    attempts: list[tuple[DraftPost, CriticReport]] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return self.final_post is not None

    @property
    def attempts_used(self) -> int:
        return len(self.attempts)


def _ranker_scores_from(paper: RankedPaper) -> RankerScores:
    return RankerScores(
        significance=paper.scores["significance"].score,
        novelty=paper.scores["novelty"].score,
        reproducibility=paper.scores["reproducibility"].score,
        clarity=paper.scores["clarity"].score,
        topical_fit=paper.scores["topical_fit"].score,
        composite=paper.composite,
    )


def _final_critic_report(
    report: CriticReport, draft: DraftPost, prior_attempts: int
) -> FinalCriticReport:
    """Collapse the structured CriticReport into the flat shape from Section 6.1."""
    notes_lines: list[str] = []
    for label, check in (
        ("voice", report.voice_match),
        ("banned_phrases", report.banned_phrase_scan),
        ("length", report.length_compliance),
        ("structure", report.structure),
        ("grounding", report.grounding),
        ("hype", report.hype_check),
    ):
        if check.note:
            notes_lines.append(f"{label}: {check.note}")
    if prior_attempts > 0:
        notes_lines.insert(0, f"Required {prior_attempts} retry/retries before passing.")

    return FinalCriticReport(
        voice_match=report.voice_match.result,
        banned_phrase_scan=report.banned_phrase_scan.result,
        length_compliance=report.length_compliance.result,
        structure=report.structure.result,
        grounding=report.grounding.result,
        hype_check=report.hype_check.result,
        retries_used=prior_attempts,
        notes=" | ".join(notes_lines) if notes_lines else "",
    )


def _build_final_post(
    draft: DraftPost,
    report: CriticReport,
    settings: Settings,
    prior_attempts: int,
    now: datetime | None,
) -> FinalPost:
    paper = draft.paper
    generated_at = now or datetime.now(timezone.utc)
    return FinalPost(
        date=generated_at.date().isoformat(),
        paper_id=f"arxiv:{paper.arxiv_id}",
        paper_title=paper.title,
        paper_authors=paper.authors,
        paper_url=draft_stage._arxiv_url(paper.arxiv_id),
        post_text=draft.post_text,
        post_char_count=draft.char_count,
        hook_char_count=draft.hook_char_count,
        claims=draft.claims,
        ranker_scores=_ranker_scores_from(paper),
        critic_report=_final_critic_report(report, draft, prior_attempts),
        generated_at=generated_at,
        drafter_model=settings.drafter.model,
        critic_model=settings.critic.model,
    )


def run(
    paper: RankedPaper,
    llm: LLMProvider,
    settings: Settings,
    *,
    now: datetime | None = None,
) -> FinalizerResult:
    """Run the drafter/critic retry loop. Returns a FinalizerResult.

    `now` lets tests pin the generated_at timestamp; in production it
    defaults to UTC now.
    """
    max_attempts = settings.drafter.max_retries
    attempts: list[tuple[DraftPost, CriticReport]] = []
    prior_notes: list[str] | None = None

    for attempt_num in range(1, max_attempts + 1):
        try:
            draft = draft_stage.run(
                paper, llm, settings, attempt=attempt_num, prior_notes=prior_notes
            )
        except LLMError as e:
            log.warning("Finalize attempt %d: drafter LLM error (%s)", attempt_num, e)
            return FinalizerResult(final_post=None, attempts=attempts)

        try:
            report = critique_stage.run(draft, llm, settings)
        except LLMError as e:
            log.warning("Finalize attempt %d: critic LLM error (%s)", attempt_num, e)
            return FinalizerResult(final_post=None, attempts=attempts)

        attempts.append((draft, report))

        if report.overall_pass:
            final = _build_final_post(
                draft, report, settings, prior_attempts=attempt_num - 1, now=now
            )
            log.info(
                "Finalize: passed on attempt %d (composite %.2f)",
                attempt_num, paper.composite,
            )
            return FinalizerResult(final_post=final, attempts=attempts)

        prior_notes = critique_stage.failure_notes(report)
        log.info(
            "Finalize attempt %d failed; %d issue(s) — retrying",
            attempt_num, len(prior_notes),
        )

    log.info("Finalize: %d attempts exhausted without a passing draft", max_attempts)
    return FinalizerResult(final_post=None, attempts=attempts)


# ---------------------------------------------------------------------------
# Derived artifacts for the reviewer (Section 13)
# ---------------------------------------------------------------------------


def build_post_md(final_post: FinalPost) -> str:
    """The post.md file is just the post text, ready to paste."""
    return final_post.post_text


def build_grounding_md(final_post: FinalPost) -> str:
    """A human-readable per-claim grounding trace.

    The reviewer reads this when a claim feels unclear — see Section 13.1.
    """
    header = (
        f"# Grounding trace for {final_post.paper_id}\n\n"
        f"Paper: {final_post.paper_title}\n"
        f"URL: {final_post.paper_url}\n"
        f"Composite: {final_post.ranker_scores.composite:.2f}\n"
        f"Drafter: {final_post.drafter_model}\n"
        f"Critic: {final_post.critic_model}\n"
        f"Retries used: {final_post.critic_report.retries_used}\n"
    )

    if not final_post.claims:
        return header + "\n_No claims declared by the drafter._\n"

    body = ["\n## Claims\n"]
    for idx, claim in enumerate(final_post.claims, start=1):
        body.append(
            f"### Claim {idx}\n\n"
            f"**Claim:** {claim.claim}\n\n"
            f"**Source span:** {claim.source_span!r}\n\n"
            f"**Page:** {claim.page}\n"
        )
    return header + "\n".join(body)


def build_voice_skip_reason(attempts_used: int) -> str:
    return f"Voice critic failed after {attempts_used} attempt(s)"
