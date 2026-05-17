"""End-to-end test of the Phase 4 pipeline with fake providers.

The pipeline runs ingest -> filter -> dedup -> process -> rank -> select
-> finalize. We script filter, ranker, drafter, and critic LLM outputs;
the mechanical critic checks still run against the drafter's actual post
text, so the canned post has to satisfy them.
"""

from __future__ import annotations

import json
from datetime import date as date_cls
from datetime import datetime, timezone
from pathlib import Path

import pytest

from arr.config import load_settings
from arr.models import Claim, DimensionScore, RawPaper
from arr.pipeline import run_pipeline
from arr.providers.storage import LocalFilesystemStorage
from arr.stages import process as process_stage
from arr.stages.critique import CriticLLMOutput
from arr.stages.draft import DrafterOutput
from arr.stages.filter import FilterDecision
from arr.stages.rank import RankerOutput


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


def _raw(arxiv_id: str, title: str, abstract: str) -> RawPaper:
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


class FakePaperSource:
    """Returns canned recent papers and writes a fake PDF on disk for fetch_pdf."""

    def __init__(self, papers: list[RawPaper], cache_dir: Path):
        self._papers = papers
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_recent(self, _categories, _since):
        return list(self._papers)

    def fetch_pdf(self, arxiv_id: str) -> Path:
        path = self._cache_dir / f"{arxiv_id}.pdf"
        path.write_bytes(b"%PDF-1.4 fake content for " + arxiv_id.encode())
        return path


def _ranker_output(s=8, n=7, r=6, c=8, t=9) -> RankerOutput:
    return RankerOutput(
        significance=DimensionScore(score=s, justification="."),
        novelty=DimensionScore(score=n, justification="."),
        reproducibility=DimensionScore(score=r, justification="."),
        clarity=DimensionScore(score=c, justification="."),
        topical_fit=DimensionScore(score=t, justification="."),
    )


def _critic_pass() -> CriticLLMOutput:
    return CriticLLMOutput(
        voice_match="pass", voice_note="ok",
        banned_phrase_scan="pass", banned_phrase_note="(LLM)",
        length_compliance="pass", length_note="(LLM)",
        structure="pass", structure_note="(LLM)",
        grounding="pass", grounding_note="ok",
        hype_check="pass", hype_note="ok",
    )


def _critic_voice_fail() -> CriticLLMOutput:
    out = _critic_pass()
    return out.model_copy(update={"voice_match": "fail", "voice_note": "too breathless"})


class ScriptedLLM:
    """Dispatches each call to the right canned response by schema name."""

    def __init__(
        self,
        *,
        filter_decisions: dict[str, FilterDecision] | None = None,
        ranker_outputs: dict[str, RankerOutput] | None = None,
        drafter_outputs: list[DrafterOutput] | None = None,
        critic_outputs: list[CriticLLMOutput] | None = None,
    ):
        self._filter = filter_decisions or {}
        self._ranker = ranker_outputs or {}
        self._drafter = list(drafter_outputs or [])
        self._critic = list(critic_outputs or [])

    def complete(self, *_, **__): raise NotImplementedError

    def complete_json(self, messages, model, schema, **kwargs):
        name = schema.__name__
        body = messages[-1]["content"]
        if name == "FilterDecision":
            for key, decision in self._filter.items():
                if key in body:
                    return decision
            return FilterDecision(
                in_scope=False, primary_topic="other",
                is_review_or_survey=False, note="default drop",
            )
        if name == "RankerOutput":
            for key, output in self._ranker.items():
                if key in body:
                    return output
            return _ranker_output(2, 2, 2, 2, 2)
        if name == "DrafterOutput":
            return self._drafter.pop(0)
        if name == "CriticLLMOutput":
            return self._critic.pop(0)
        raise AssertionError(f"unexpected schema {name}")


class NullEmbeddings:
    def embed(self, texts):
        return [[0.0] * 8 for _ in texts]


@pytest.fixture
def stub_pdf_extractor(monkeypatch):
    # Sections matching the claims in GOOD_POST so the grounding mechanical
    # check finds the source spans verbatim.
    monkeypatch.setattr(
        process_stage,
        "extract_text_with_pdfplumber",
        lambda _p: (
            "Abstract\nWe propose decomposition.\n\n"
            "1 Introduction\nMotivation.\n\n"
            "2 Method\nQuery decomposition step.\n\n"
            "3 Results\nWe achieve 71.2 on HotpotQA against a 59.4 baseline.\n\n"
            "4 Limitations\nDecomposition relies on a separate small model trained on a synthetic dataset.\n",
            10,
        ),
    )


def _good_claims() -> list[Claim]:
    return [
        Claim(claim="twelve points on HotpotQA",
              source_span="We achieve 71.2 on HotpotQA against a 59.4 baseline.", page=1),
        Claim(claim="separate small model",
              source_span="Decomposition relies on a separate small model trained on a synthetic dataset.", page=1),
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_pipeline_writes_full_post_day_artifacts(
    tmp_path: Path, stub_pdf_extractor
):
    paper = _raw("2026.0001", "WINNERMARK Query Decomposition", "rag method")
    filter_decisions = {
        "WINNERMARK": FilterDecision(in_scope=True, primary_topic="rag",
                                     is_review_or_survey=False, note=""),
    }
    ranker_outputs = {
        "WINNERMARK": _ranker_output(9, 9, 8, 9, 10),  # well above threshold
    }
    drafter_outputs = [DrafterOutput(post_text=GOOD_POST, claims=_good_claims())]
    critic_outputs = [_critic_pass()]

    reviews = tmp_path / "reviews"
    storage = LocalFilesystemStorage(reviews)
    result = run_pipeline(
        run_date=date_cls(2026, 5, 16),
        settings=load_settings(),
        llm=ScriptedLLM(
            filter_decisions=filter_decisions,
            ranker_outputs=ranker_outputs,
            drafter_outputs=drafter_outputs,
            critic_outputs=critic_outputs,
        ),
        paper_source=FakePaperSource([paper], cache_dir=tmp_path / "cache"),
        storage=storage,
        embeddings=NullEmbeddings(),
        reviews_dir=reviews,
        now=datetime(2026, 5, 16, 8, 14, 22, tzinfo=timezone.utc),
    )

    assert result.final_post is not None
    assert result.skip_record is None
    assert result.finalize_attempts_used == 1

    day = reviews / "2026-05-16"
    assert (day / "final_post.json").exists()
    assert (day / "post.md").exists()
    assert (day / "grounding.md").exists()
    assert (day / "paper.pdf").exists()
    assert (day / "selected.json").exists()

    post_md = (day / "post.md").read_text(encoding="utf-8")
    assert post_md == GOOD_POST

    grounding_md = (day / "grounding.md").read_text(encoding="utf-8")
    assert "Grounding trace" in grounding_md
    assert "twelve points" in grounding_md

    final = json.loads((day / "final_post.json").read_text(encoding="utf-8"))
    assert final["paper_id"] == "arxiv:2026.0001"
    assert final["critic_report"]["retries_used"] == 0


def test_pipeline_skips_when_voice_critic_fails_three_times(
    tmp_path: Path, stub_pdf_extractor
):
    paper = _raw("2026.0002", "WINNERMARK Query Decomposition", "rag method")
    filter_decisions = {
        "WINNERMARK": FilterDecision(in_scope=True, primary_topic="rag",
                                     is_review_or_survey=False, note=""),
    }
    ranker_outputs = {
        "WINNERMARK": _ranker_output(9, 9, 8, 9, 10),
    }
    drafter_outputs = [DrafterOutput(post_text=GOOD_POST, claims=_good_claims())] * 3
    critic_outputs = [_critic_voice_fail()] * 3

    reviews = tmp_path / "reviews"
    storage = LocalFilesystemStorage(reviews)
    result = run_pipeline(
        run_date=date_cls(2026, 5, 17),
        settings=load_settings(),
        llm=ScriptedLLM(
            filter_decisions=filter_decisions,
            ranker_outputs=ranker_outputs,
            drafter_outputs=drafter_outputs,
            critic_outputs=critic_outputs,
        ),
        paper_source=FakePaperSource([paper], cache_dir=tmp_path / "cache"),
        storage=storage,
        embeddings=NullEmbeddings(),
        reviews_dir=reviews,
    )

    assert result.final_post is None
    assert result.skip_record is not None
    assert "Voice critic failed" in result.skip_record.reason
    assert result.finalize_attempts_used == 3

    day = reviews / "2026-05-17"
    skip = json.loads((day / "skip.json").read_text(encoding="utf-8"))
    assert "Voice critic failed" in skip["reason"]
    assert not (day / "post.md").exists()
    assert not (day / "final_post.json").exists()


def test_pipeline_skips_when_no_paper_above_threshold(
    tmp_path: Path, stub_pdf_extractor
):
    paper = _raw("2026.0003", "MODESTMARK Small Tweak", "rag method")
    filter_decisions = {
        "MODESTMARK": FilterDecision(in_scope=True, primary_topic="rag",
                                     is_review_or_survey=False, note=""),
    }
    ranker_outputs = {
        "MODESTMARK": _ranker_output(5, 5, 5, 5, 5),  # composite 5.0 < 7.0
    }

    reviews = tmp_path / "reviews"
    storage = LocalFilesystemStorage(reviews)
    result = run_pipeline(
        run_date=date_cls(2026, 5, 18),
        settings=load_settings(),
        llm=ScriptedLLM(
            filter_decisions=filter_decisions,
            ranker_outputs=ranker_outputs,
        ),
        paper_source=FakePaperSource([paper], cache_dir=tmp_path / "cache"),
        storage=storage,
        embeddings=NullEmbeddings(),
        reviews_dir=reviews,
    )

    assert result.selected is None
    assert result.skip_record is not None
    assert "post_worthy_threshold" in result.skip_record.reason
    day = reviews / "2026-05-18"
    assert (day / "skip.json").exists()
    assert not (day / "selected.json").exists()


def test_pipeline_skips_when_filter_drops_everything(
    tmp_path: Path, stub_pdf_extractor
):
    paper = _raw("2026.0004", "VISIONMARK Things", "image classification")
    filter_decisions = {
        "VISIONMARK": FilterDecision(in_scope=False, primary_topic="other",
                                     is_review_or_survey=False, note="vision"),
    }

    reviews = tmp_path / "reviews"
    storage = LocalFilesystemStorage(reviews)
    result = run_pipeline(
        run_date=date_cls(2026, 5, 19),
        settings=load_settings(),
        llm=ScriptedLLM(filter_decisions=filter_decisions),
        paper_source=FakePaperSource([paper], cache_dir=tmp_path / "cache"),
        storage=storage,
        embeddings=NullEmbeddings(),
        reviews_dir=reviews,
    )

    assert result.selected is None
    assert "No papers in scope" in result.skip_record.reason
