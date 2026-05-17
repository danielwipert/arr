"""Tests for Stage 4 ranker."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from arr.config import load_settings
from arr.models import DimensionScore, ProcessedPaper
from arr.providers.llm import LLMError
from arr.stages import rank as rank_stage
from arr.stages.rank import RankerOutput, compute_composite


def _processed(
    arxiv_id: str = "2026.0001",
    *,
    sections: dict[str, str] | None = None,
) -> ProcessedPaper:
    return ProcessedPaper(
        arxiv_id=arxiv_id,
        title="Query Decomposition for Robust RAG",
        authors=["A. Researcher"],
        abstract="We propose decomposition.",
        primary_cat="cs.CL",
        all_cats=["cs.CL"],
        submitted_at=datetime(2026, 5, 16, 12, 0, tzinfo=timezone.utc),
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
        in_scope=True,
        primary_topic="rag",
        dedup_similarity=None,
        noise_flagged=False,
        sections=sections or {
            "abstract": "We propose decomposition.",
            "intro": "Motivation.",
            "method": "Decomposition step.",
            "results": "71.2 on HotpotQA.",
            "conclusions": "Decomposition matters.",
        },
        pdf_local_path="/tmp/x.pdf",
        page_count=10,
    )


class ScriptedLLM:
    def __init__(self, output: RankerOutput, *, raise_error: bool = False):
        self._output = output
        self._raise = raise_error
        self.calls: list[dict[str, Any]] = []

    def complete(self, *_, **__):
        raise NotImplementedError

    def complete_json(self, messages, model, schema, **kwargs):
        self.calls.append({"messages": messages, "model": model, "schema": schema})
        if self._raise:
            raise LLMError("scripted")
        return self._output


def _output(s=8, n=7, r=6, c=8, t=9) -> RankerOutput:
    return RankerOutput(
        significance=DimensionScore(score=s, justification="."),
        novelty=DimensionScore(score=n, justification="."),
        reproducibility=DimensionScore(score=r, justification="."),
        clarity=DimensionScore(score=c, justification="."),
        topical_fit=DimensionScore(score=t, justification="."),
    )


def test_compute_composite_matches_spec_formula():
    settings = load_settings()
    weights = settings.ranker.weights.as_dict()
    scores = {
        "significance": DimensionScore(score=8, justification="."),
        "novelty": DimensionScore(score=7, justification="."),
        "reproducibility": DimensionScore(score=6, justification="."),
        "clarity": DimensionScore(score=8, justification="."),
        "topical_fit": DimensionScore(score=9, justification="."),
    }
    # 8*0.3 + 7*0.25 + 6*0.2 + 8*0.15 + 9*0.1 = 2.4 + 1.75 + 1.2 + 1.2 + 0.9 = 7.45
    assert compute_composite(scores, weights) == pytest.approx(7.45)


def test_compute_composite_clamps_to_bounds():
    weights = {"a": 1.0}
    scores = {"a": DimensionScore(score=10, justification=".")}
    assert compute_composite(scores, weights) == 10.0
    scores = {"a": DimensionScore(score=0, justification=".")}
    assert compute_composite(scores, weights) == 0.0


def test_rank_builds_ranked_paper_with_composite():
    settings = load_settings()
    llm = ScriptedLLM(_output(s=8, n=7, r=6, c=8, t=9))
    out = rank_stage.run([_processed()], llm, settings)
    assert len(out) == 1
    paper = out[0]
    assert paper.composite == pytest.approx(7.45)
    assert paper.scores["significance"].score == 8
    assert llm.calls[0]["model"] == settings.cheap_model


def test_rank_drops_paper_on_llm_error():
    llm = ScriptedLLM(_output(), raise_error=True)
    out = rank_stage.run([_processed()], llm, load_settings())
    assert out == []


def test_rank_sorts_by_composite_descending():
    settings = load_settings()
    # Two papers, two different outputs scripted by abstract substring.
    paper_high = _processed("h", sections={"abstract": "high marker"})
    paper_low = _processed("l", sections={"abstract": "low marker"})

    class Multi:
        def complete(self, *_, **__): raise NotImplementedError
        def complete_json(self, messages, model, schema, **kwargs):
            body = messages[-1]["content"]
            if "high marker" in body:
                return _output(s=10, n=10, r=10, c=10, t=10)  # composite 10
            return _output(s=2, n=2, r=2, c=2, t=2)  # composite 2

    out = rank_stage.run([paper_low, paper_high], Multi(), settings)
    assert [p.arxiv_id for p in out] == ["h", "l"]
    assert out[0].composite > out[1].composite


def test_rank_passes_method_section_to_prompt():
    llm = ScriptedLLM(_output())
    rank_stage.run([_processed()], llm, load_settings())
    prompt_body = llm.calls[0]["messages"][-1]["content"]
    assert "Decomposition step." in prompt_body
    assert "71.2 on HotpotQA." in prompt_body
