"""Stage 6 — Drafter.

Writes a single LinkedIn post about the selected paper in the voice
specified in Section 5. Uses the premium drafter model. Returns a
DraftPost with grounded claims; the critic in Stage 7 verifies both the
voice and the grounding.

The drafter accepts optional critic notes from a prior attempt. When
present, those notes are appended to the prompt so the retry has the
specific feedback to address rather than starting blind.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel, ConfigDict

from arr.config import REPO_ROOT, Settings
from arr.models import Claim, DraftPost, SelectedPaper
from arr.providers.llm import LLMProvider
from arr.stages._prompts import render

log = logging.getLogger(__name__)

PROMPT_PATH = REPO_ROOT / "config" / "prompts" / "drafter.md"


class DrafterOutput(BaseModel):
    """LLM-shaped output: the post text plus its grounding trace."""

    model_config = ConfigDict(extra="forbid")

    post_text: str
    claims: list[Claim]


def _arxiv_url(arxiv_id: str) -> str:
    # Strip any version suffix like "v3" before building the canonical URL.
    base = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id
    return f"https://arxiv.org/abs/{base}"


def _hook_char_count(post_text: str) -> int:
    """First newline-delimited line of the post — what readers see before
    the LinkedIn "see more" expand on mobile."""
    first_line = post_text.split("\n", 1)[0]
    return len(first_line)


def _build_retry_section(prior_notes: list[str] | None) -> str:
    if not prior_notes:
        return ""
    notes = "\n".join(f"- {n}" for n in prior_notes)
    return (
        "## Prior attempt feedback\n\n"
        "Your previous draft failed the critic on the following points. "
        "Address each one specifically in this revision.\n\n"
        f"{notes}\n"
    )


def render_prompt(paper: SelectedPaper, prior_notes: list[str] | None = None) -> str:
    sections = paper.sections
    return render(
        PROMPT_PATH.read_text(encoding="utf-8"),
        title=paper.title,
        authors=", ".join(paper.authors),
        arxiv_id=paper.arxiv_id,
        arxiv_url=_arxiv_url(paper.arxiv_id),
        abstract=sections.get("abstract", paper.abstract),
        intro=sections.get("intro", "(not extracted)"),
        method=sections.get("method", "(not extracted)"),
        results=sections.get("results", "(not extracted)"),
        limitations=sections.get("limitations", "(not extracted)"),
        conclusions=sections.get("conclusions", "(not extracted)"),
        retry_section=_build_retry_section(prior_notes),
    )


def run(
    paper: SelectedPaper,
    llm: LLMProvider,
    settings: Settings,
    *,
    attempt: int = 1,
    prior_notes: list[str] | None = None,
) -> DraftPost:
    """Generate a single draft. Raises LLMError if the LLM call fails outright."""
    prompt = render_prompt(paper, prior_notes=prior_notes)
    log.info("Draft attempt %d for %s", attempt, paper.arxiv_id)

    output = llm.complete_json(
        [{"role": "user", "content": prompt}],
        model=settings.drafter.model,
        schema=DrafterOutput,
        temperature=0.4,
    )

    return DraftPost(
        paper=paper,
        post_text=output.post_text,
        claims=output.claims,
        char_count=len(output.post_text),
        hook_char_count=_hook_char_count(output.post_text),
        drafter_model=settings.drafter.model,
        attempt=attempt,
    )
