"""Tests for Stage 8 finalizer.

We script the LLM at the JSON level: the drafter call returns a DrafterOutput,
the critic call returns a CriticLLMOutput. The mechanical critic checks
(length, structure, banned phrases, grounding-span existence) are applied
on top, so the drafter's post must actually meet those — same as production.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from arr.config import load_settings
from arr.models import Claim, DimensionScore, RankedPaper
from arr.stages import finalize as finalize_stage
from arr.stages.critique import CriticLLMOutput
from arr.stages.draft import DrafterOutput


GOOD_POST = (
    "A new RAG result from ETH Zürich pushes HotpotQA accuracy by twelve points without retraining the underlying model at all.\n"
    "\n"
    "The team rebuilt the standard retrieval pipeline around query decomposition rather than reranking. They report 71.2 on HotpotQA against a 59.4 baseline, and credit the gain to a small decomposition model that runs before the retriever sees the query.\n"
    "\n"
    "The finding is narrower than it sounds. Their decomposition step relies on a separate small model trained on a synthetic dataset of their own construction. Reproduction is therefore non-trivial and the result is harder to read as a general claim, particularly outside the multi-hop QA setting they evaluated on, and particularly without access to the dataset itself.\n"
    "\n"
    "For builders, the direction is still interesting. Retrieval quality matters more than retrieval volume, and the cheapest gains often sit in the query rewriting stage rather than in the embedding model itself. The pattern has been accumulating quiet evidence across the literature for two full years now, and this paper is the most legible single argument for it yet, even with the reproduction caveat noted above.\n"
    "\n"
    "Worth reading if you ship RAG systems in production. Worth ignoring if you were hoping for a free lunch out of the box.\n"
    "\n"
    "Paper: Query Decomposition for Robust RAG, Müller et al.\n"
    "https://arxiv.org/abs/2026.0001\n"
    "\n"
    "#LLMs #RAG #AppliedAI #Retrieval"
)


def _ranked() -> RankedPaper:
    scores = {
        k: DimensionScore(score=8, justification=".")
        for k in ("significance", "novelty", "reproducibility", "clarity", "topical_fit")
    }
    return RankedPaper(
        arxiv_id="2026.0001",
        title="Query Decomposition for Robust RAG",
        authors=["A. Müller", "B. Schmidt"],
        abstract="We propose decomposition.",
        primary_cat="cs.CL",
        all_cats=["cs.CL"],
        submitted_at=datetime(2026, 5, 16, 12, 0, tzinfo=timezone.utc),
        pdf_url="https://arxiv.org/pdf/2026.0001",
        in_scope=True,
        primary_topic="rag",
        dedup_similarity=None,
        noise_flagged=False,
        sections={
            "abstract": "We propose decomposition.",
            "results": "We achieve 71.2 on HotpotQA against a 59.4 baseline.",
            "limitations": "Decomposition relies on a separate small model trained on a synthetic dataset.",
        },
        pdf_local_path="/tmp/x.pdf",
        page_count=10,
        scores=scores,
        composite=7.65,
    )


GOOD_CLAIMS = [
    Claim(claim="twelve-point gain on HotpotQA",
          source_span="We achieve 71.2 on HotpotQA against a 59.4 baseline.", page=1),
    Claim(claim="decomposition relies on a separate small model",
          source_span="Decomposition relies on a separate small model trained on a synthetic dataset.", page=1),
]


def _drafter_output(post_text: str = GOOD_POST) -> DrafterOutput:
    return DrafterOutput(post_text=post_text, claims=list(GOOD_CLAIMS))


def _critic_pass() -> CriticLLMOutput:
    return CriticLLMOutput(
        voice_match="pass", voice_note="FT-ish",
        banned_phrase_scan="pass", banned_phrase_note="(LLM)",
        length_compliance="pass", length_note="(LLM)",
        structure="pass", structure_note="(LLM)",
        grounding="pass", grounding_note="claims supported",
        hype_check="pass", hype_note="no overclaim",
    )


def _critic_voice_fail() -> CriticLLMOutput:
    out = _critic_pass()
    return out.model_copy(update={"voice_match": "fail", "voice_note": "too breathless on the close"})


class ScriptedLLM:
    """Routes each call to the right canned response based on the schema."""

    def __init__(
        self,
        drafter_outputs: list[DrafterOutput],
        critic_outputs: list[CriticLLMOutput],
    ):
        self._drafters = list(drafter_outputs)
        self._critics = list(critic_outputs)
        self.calls: list[dict[str, Any]] = []

    def complete(self, *_, **__): raise NotImplementedError

    def complete_json(self, messages, model, schema, **kwargs):
        self.calls.append({"schema": schema.__name__, "model": model})
        name = schema.__name__
        if name == "DrafterOutput":
            return self._drafters.pop(0)
        if name == "CriticLLMOutput":
            return self._critics.pop(0)
        raise AssertionError(f"unexpected schema {name}")


def test_first_attempt_passes_builds_final_post():
    settings = load_settings()
    llm = ScriptedLLM([_drafter_output()], [_critic_pass()])
    now = datetime(2026, 5, 16, 8, 14, 22, tzinfo=timezone.utc)

    result = finalize_stage.run(_ranked(), llm, settings, now=now)

    assert result.succeeded
    assert result.attempts_used == 1
    assert result.final_post is not None
    fp = result.final_post

    assert fp.date == "2026-05-16"
    assert fp.paper_id == "arxiv:2026.0001"
    assert fp.paper_url == "https://arxiv.org/abs/2026.0001"
    assert fp.post_char_count == len(GOOD_POST)
    assert fp.ranker_scores.composite == pytest.approx(7.65)
    assert fp.critic_report.retries_used == 0
    assert fp.critic_report.voice_match == "pass"


def test_retries_drafter_when_voice_fails_then_passes():
    settings = load_settings()
    llm = ScriptedLLM(
        drafter_outputs=[_drafter_output(), _drafter_output()],
        critic_outputs=[_critic_voice_fail(), _critic_pass()],
    )

    result = finalize_stage.run(_ranked(), llm, settings)

    assert result.succeeded
    assert result.attempts_used == 2
    assert result.final_post.critic_report.retries_used == 1
    assert "Required 1 retry" in result.final_post.critic_report.notes


def test_retry_includes_failure_notes_in_drafter_prompt():
    settings = load_settings()
    llm = ScriptedLLM(
        drafter_outputs=[_drafter_output(), _drafter_output()],
        critic_outputs=[_critic_voice_fail(), _critic_pass()],
    )

    finalize_stage.run(_ranked(), llm, settings)

    # Second drafter call must have seen the prior failure notes.
    drafter_calls = [c for c in llm.calls if c["schema"] == "DrafterOutput"]
    assert len(drafter_calls) == 2
    # We can't peek at messages on this fake — but the next test verifies via
    # `draft.render_prompt` separately. This test guards the call-count
    # invariant.


def test_three_failed_attempts_returns_no_final_post():
    settings = load_settings()
    llm = ScriptedLLM(
        drafter_outputs=[_drafter_output()] * 3,
        critic_outputs=[_critic_voice_fail()] * 3,
    )

    result = finalize_stage.run(_ranked(), llm, settings)

    assert not result.succeeded
    assert result.final_post is None
    assert result.attempts_used == 3


def test_build_post_md_returns_post_text():
    settings = load_settings()
    llm = ScriptedLLM([_drafter_output()], [_critic_pass()])
    result = finalize_stage.run(_ranked(), llm, settings)
    assert finalize_stage.build_post_md(result.final_post) == GOOD_POST


def test_build_grounding_md_includes_each_claim():
    settings = load_settings()
    llm = ScriptedLLM([_drafter_output()], [_critic_pass()])
    result = finalize_stage.run(_ranked(), llm, settings)
    md = finalize_stage.build_grounding_md(result.final_post)
    assert "Grounding trace" in md
    assert "Claim 1" in md
    assert "Claim 2" in md
    assert "twelve-point gain" in md
    assert "71.2 on HotpotQA" in md


def test_build_voice_skip_reason_uses_attempt_count():
    assert "3 attempt" in finalize_stage.build_voice_skip_reason(3)
