"""Tests for Stage 2 filter."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

import pytest

from arr.config import load_settings
from arr.models import RawPaper
from arr.providers.llm import LLMError
from arr.stages import filter as filter_stage
from arr.stages.filter import FilterDecision


def _paper(
    arxiv_id: str,
    title: str = "Method X for LLMs",
    abstract: str = "We propose an LLM method.",
) -> RawPaper:
    return RawPaper(
        arxiv_id=arxiv_id,
        title=title,
        authors=["A. Researcher"],
        abstract=abstract,
        primary_cat="cs.CL",
        all_cats=["cs.CL"],
        submitted_at=datetime(2026, 5, 16, 12, 0, tzinfo=timezone.utc),
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
    )


class FakeLLM:
    """Returns a scripted FilterDecision per paper, identified by abstract text."""

    def __init__(self, decisions: dict[str, FilterDecision] | None = None) -> None:
        self._decisions = decisions or {}
        self.calls: list[dict[str, Any]] = []

    def complete(self, *_, **__) -> str:
        raise NotImplementedError

    def complete_json(self, messages, model, schema, **kwargs):
        self.calls.append({"messages": messages, "model": model, "schema": schema, **kwargs})
        # Match by abstract substring so tests stay readable.
        body = messages[-1]["content"]
        for key, decision in self._decisions.items():
            if key in body:
                return decision
        # Default: in scope, no noise.
        return FilterDecision(
            in_scope=True, primary_topic="rag", is_review_or_survey=False, note=""
        )


def _settings():
    return load_settings()


def test_in_scope_paper_survives():
    papers = [_paper("1", "Query Decomposition", "rag method")]
    llm = FakeLLM({"rag method": FilterDecision(in_scope=True, primary_topic="rag",
                                                is_review_or_survey=False, note="ok")})
    out = filter_stage.run(papers, llm, _settings())
    assert len(out) == 1
    assert out[0].primary_topic == "rag"
    assert out[0].in_scope is True
    assert out[0].noise_flagged is False
    assert out[0].dedup_similarity is None


def test_out_of_scope_paper_dropped():
    papers = [_paper("1", "Vision Transformers", "image classification")]
    llm = FakeLLM({"image": FilterDecision(in_scope=False, primary_topic="other",
                                           is_review_or_survey=False, note="vision only")})
    out = filter_stage.run(papers, llm, _settings())
    assert out == []


def test_llm_marks_as_review_drops_paper():
    papers = [_paper("1", "Surveying LLM Agents", "we review the literature")]
    llm = FakeLLM({"we review": FilterDecision(in_scope=True, primary_topic="llm_capabilities",
                                               is_review_or_survey=True, note="review")})
    out = filter_stage.run(papers, llm, _settings())
    assert out == []


def test_regex_noise_drops_paper_even_when_llm_says_in_scope():
    # The LLM would happily classify this as in-scope; the regex pre-screen catches it.
    papers = [_paper("1", "A Survey of RAG Techniques", "we cover...")]
    llm = FakeLLM({"we cover": FilterDecision(in_scope=True, primary_topic="rag",
                                              is_review_or_survey=False, note="actually a survey")})
    out = filter_stage.run(papers, llm, _settings())
    assert out == []


def test_llm_error_drops_paper_without_crashing():
    class BoomLLM:
        def complete(self, *a, **k): raise NotImplementedError
        def complete_json(self, *a, **k): raise LLMError("network sad")

    papers = [_paper("1"), _paper("2")]
    out = filter_stage.run(papers, BoomLLM(), _settings())
    assert out == []


def test_uses_cheap_model_from_settings():
    papers = [_paper("1")]
    llm = FakeLLM()
    filter_stage.run(papers, llm, _settings())
    assert llm.calls[0]["model"] == _settings().cheap_model


# --- keyword pre-filter --------------------------------------------------


def test_prefilter_drops_paper_with_no_llm_keyword():
    # No LLM marker anywhere. Pre-filter should drop before LLM is called.
    papers = [_paper("1", title="Quantum Annealing for X", abstract="Pure quantum content.")]
    llm = FakeLLM()
    out = filter_stage.run(papers, llm, _settings())
    assert out == []
    assert llm.calls == []  # LLM never called


def test_prefilter_passes_paper_with_llm_keyword():
    # "LLM" appears verbatim → prefilter passes → LLM filter runs.
    papers = [_paper("1", title="A New Method", abstract="We benchmark LLM agents.")]
    llm = FakeLLM({"LLM agents": FilterDecision(
        in_scope=True, primary_topic="llm_capabilities",
        is_review_or_survey=False, note="")})
    out = filter_stage.run(papers, llm, _settings())
    assert len(out) == 1
    assert len(llm.calls) == 1


def test_prefilter_is_case_insensitive():
    papers = [_paper("1", title="x", abstract="On the trade-offs of fine-tuning small models.")]
    llm = FakeLLM({"fine-tuning": FilterDecision(
        in_scope=True, primary_topic="post_training",
        is_review_or_survey=False, note="")})
    out = filter_stage.run(papers, llm, _settings())
    assert len(out) == 1


def test_prefilter_can_be_disabled():
    settings = _settings()
    # Disable the prefilter entirely.
    settings = settings.model_copy(update={
        "filter": settings.filter.model_copy(update={
            "keyword_prefilter": settings.filter.keyword_prefilter.model_copy(
                update={"enabled": False}
            )
        })
    })
    # Paper without any LLM keyword should reach the LLM call.
    papers = [_paper("1", title="Unrelated", abstract="Nothing about LLMs.")]
    llm = FakeLLM()  # default decision = in_scope=True topic=rag
    out = filter_stage.run(papers, llm, settings)
    assert len(out) == 1
    assert len(llm.calls) == 1
