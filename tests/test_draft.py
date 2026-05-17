"""Tests for Stage 6 drafter."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from arr.config import load_settings
from arr.models import Claim, DimensionScore, RankedPaper
from arr.providers.llm import LLMError
from arr.stages import draft as draft_stage
from arr.stages.draft import DrafterOutput, render_prompt


def _ranked(arxiv_id: str = "2026.0001") -> RankedPaper:
    scores = {
        "significance": DimensionScore(score=8, justification="."),
        "novelty": DimensionScore(score=7, justification="."),
        "reproducibility": DimensionScore(score=6, justification="."),
        "clarity": DimensionScore(score=8, justification="."),
        "topical_fit": DimensionScore(score=9, justification="."),
    }
    return RankedPaper(
        arxiv_id=arxiv_id,
        title="Query Decomposition for Robust RAG",
        authors=["A. Müller", "B. Schmidt"],
        abstract="We propose decomposition.",
        primary_cat="cs.CL",
        all_cats=["cs.CL"],
        submitted_at=datetime(2026, 5, 16, 12, 0, tzinfo=timezone.utc),
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
        in_scope=True,
        primary_topic="rag",
        dedup_similarity=0.31,
        noise_flagged=False,
        sections={
            "abstract": "We propose decomposition.",
            "intro": "Motivation.",
            "method": "Query decomposition step.",
            "results": "We achieve 71.2 on HotpotQA.",
            "limitations": "We rely on a separate small model.",
            "conclusions": "Decomposition matters.",
        },
        pdf_local_path="/tmp/x.pdf",
        page_count=10,
        scores=scores,
        composite=7.65,
    )


class ScriptedLLM:
    def __init__(self, output: DrafterOutput, *, raise_error: bool = False):
        self._output = output
        self._raise = raise_error
        self.calls: list[dict[str, Any]] = []

    def complete(self, *_, **__):
        raise NotImplementedError

    def complete_json(self, messages, model, schema, **kwargs):
        self.calls.append({"messages": messages, "model": model, "schema": schema, **kwargs})
        if self._raise:
            raise LLMError("scripted")
        return self._output


def _good_output() -> DrafterOutput:
    post = (
        "A new RAG result from ETH Zürich.\n"
        "\n"
        "The team reports a twelve-point gain on HotpotQA. Specifically 71.2 vs 59.4 baseline.\n"
        "\n"
        "The result is narrower than it sounds. Their decomposition relies on a separate small model. Reproduction is therefore non-trivial.\n"
        "\n"
        "For builders, the takeaway is concrete. Retrieval quality matters more than retrieval volume. The cheapest gains often live in the query rewriting stage.\n"
        "\n"
        "Worth reading if you ship RAG systems.\n"
        "\n"
        "Paper: Query Decomposition for Robust RAG — Müller et al.\n"
        "https://arxiv.org/abs/2026.0001\n"
        "\n"
        "#LLMs #Retrieval #Enterprise #VendorRisk #QueryDecomposition"
    )
    return DrafterOutput(
        post_text=post,
        claims=[
            Claim(claim="twelve-point gain on HotpotQA",
                  source_span="We achieve 71.2 on HotpotQA.", page=1),
            Claim(claim="71.2 vs 59.4 baseline",
                  source_span="We achieve 71.2 on HotpotQA.", page=1),
            Claim(claim="decomposition relies on a separate small model",
                  source_span="We rely on a separate small model.", page=1),
        ],
    )


def test_draft_builds_draftpost_with_counts():
    llm = ScriptedLLM(_good_output())
    out = draft_stage.run(_ranked(), llm, load_settings())

    assert out.paper.arxiv_id == "2026.0001"
    assert out.drafter_model == load_settings().drafter.model
    assert out.char_count == len(out.post_text)
    assert out.hook_char_count == len(out.post_text.split("\n", 1)[0])
    assert out.attempt == 1
    assert len(out.claims) == 3


def test_draft_passes_method_and_results_into_prompt():
    llm = ScriptedLLM(_good_output())
    draft_stage.run(_ranked(), llm, load_settings())
    body = llm.calls[0]["messages"][-1]["content"]
    assert "Query decomposition step." in body
    assert "We achieve 71.2 on HotpotQA." in body
    assert "Müller" in body
    assert "https://arxiv.org/abs/2026.0001" in body


def test_draft_includes_prior_notes_on_retry():
    llm = ScriptedLLM(_good_output())
    draft_stage.run(
        _ranked(), llm, load_settings(),
        attempt=2,
        prior_notes=["voice slipped into hype on the close",
                     "first line was 152 characters; trim under 140"],
    )
    body = llm.calls[0]["messages"][-1]["content"]
    assert "Prior attempt feedback" in body
    assert "voice slipped" in body
    assert "152 characters" in body


def test_draft_omits_retry_section_on_first_attempt():
    llm = ScriptedLLM(_good_output())
    draft_stage.run(_ranked(), llm, load_settings())
    body = llm.calls[0]["messages"][-1]["content"]
    assert "Prior attempt feedback" not in body


def test_draft_uses_premium_model_from_settings():
    settings = load_settings()
    llm = ScriptedLLM(_good_output())
    draft_stage.run(_ranked(), llm, settings)
    assert llm.calls[0]["model"] == settings.drafter.model


def test_draft_raises_llmerror_when_provider_fails():
    llm = ScriptedLLM(_good_output(), raise_error=True)
    with pytest.raises(LLMError):
        draft_stage.run(_ranked(), llm, load_settings())


def test_render_prompt_handles_missing_sections():
    paper = _ranked()
    # Strip out the optional sections.
    paper_no_limits = paper.model_copy(update={
        "sections": {"abstract": "x", "intro": "y", "method": "z"}
    })
    prompt = render_prompt(paper_no_limits)
    assert "(not extracted)" in prompt  # for limitations/results/conclusions
