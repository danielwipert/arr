"""Tests for Stage 7 critic.

Covers:
- the mechanical pure-Python checks (banned phrases, length, structure,
  grounding span existence)
- the run() orchestrator's LLM-vs-mechanical override behaviour
- the failure_notes() pack helper used by the retry loop
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from arr.config import load_settings
from arr.models import (
    Claim,
    CheckResult,
    CriticReport,
    DimensionScore,
    DraftPost,
    RankedPaper,
)
from arr.stages import critique
from arr.stages.critique import (
    CriticLLMOutput,
    check_grounding_spans,
    check_length,
    check_structure,
    failure_notes,
    scan_banned_phrases,
)


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


def _draft(post_text: str = GOOD_POST, claims: list[Claim] | None = None) -> DraftPost:
    return DraftPost(
        paper=_ranked(),
        post_text=post_text,
        claims=claims or [
            Claim(claim="twelve points", source_span="We achieve 71.2 on HotpotQA against a 59.4 baseline.", page=1),
            Claim(claim="71.2 vs 59.4 baseline", source_span="We achieve 71.2 on HotpotQA against a 59.4 baseline.", page=1),
            Claim(claim="decomposition relies on a separate small model",
                  source_span="Decomposition relies on a separate small model trained on a synthetic dataset.", page=1),
        ],
        char_count=len(post_text),
        hook_char_count=len(post_text.split("\n", 1)[0]),
        drafter_model="x",
        attempt=1,
    )


# --- scan_banned_phrases -------------------------------------------------


def test_scan_banned_phrases_clean_post():
    assert scan_banned_phrases(GOOD_POST) == []


def test_scan_banned_phrases_catches_excited_to_share():
    hits = scan_banned_phrases("Excited to share a great new paper!")
    assert any("Excited to share" in h for h in hits)


def test_scan_banned_phrases_catches_em_dash():
    hits = scan_banned_phrases("This is a sentence — with an em-dash.")
    assert any("em-dash" in h for h in hits)


def test_scan_banned_phrases_catches_all_caps_preamble():
    hits = scan_banned_phrases("BREAKING: paper drops.\n\nMore text.")
    assert hits  # caught either as 'BREAKING:' or as all-caps preamble


def test_scan_banned_phrases_catches_thoughts_closer():
    hits = scan_banned_phrases("Some content.\n\nThoughts?")
    assert any("Thoughts?" in h for h in hits)


def test_scan_banned_phrases_too_many_emoji():
    hits = scan_banned_phrases("🚀 Big result 🤯 game changing 🎉")
    assert any("emoji" in h for h in hits)


def test_scan_banned_phrases_one_emoji_ok():
    # One emoji is allowed (zero is the default but one is rationed).
    assert scan_banned_phrases("Some content. ✨") == []


# --- check_length --------------------------------------------------------


def test_check_length_on_good_post():
    ok, note = check_length(GOOD_POST)
    assert ok, note


def test_check_length_rejects_short_post():
    ok, note = check_length("Too short.")
    assert not ok
    assert "too short" in note


def test_check_length_rejects_long_hook():
    long_hook = "x" * 150 + "\n\n" + "y" * 1500
    ok, note = check_length(long_hook)
    assert not ok
    assert "hook too long" in note


# --- check_structure -----------------------------------------------------


def test_check_structure_on_good_post():
    ok, note = check_structure(GOOD_POST)
    assert ok, note


def test_check_structure_rejects_missing_block():
    blocks = GOOD_POST.split("\n\n")
    truncated = "\n\n".join(blocks[:-1])  # missing tag line
    ok, _ = check_structure(truncated)
    assert not ok


def test_check_structure_rejects_missing_required_hashtag():
    bad = GOOD_POST.replace("#LLMs ", "")
    ok, note = check_structure(bad)
    assert not ok
    assert "hashtag" in note.lower()


# --- check_grounding_spans ----------------------------------------------


def test_grounding_spans_pass_when_all_present():
    ok, _ = check_grounding_spans(_draft())
    assert ok


def test_grounding_spans_fail_when_span_missing_from_paper():
    bad_claims = [
        Claim(claim="x", source_span="This text does not appear anywhere.", page=1),
    ]
    ok, note = check_grounding_spans(_draft(claims=bad_claims))
    assert not ok
    assert "not found in paper" in note


# --- run() orchestrator --------------------------------------------------


class FakeLLM:
    def __init__(self, output: CriticLLMOutput):
        self._output = output
        self.calls: list = []

    def complete(self, *_, **__): raise NotImplementedError

    def complete_json(self, messages, model, schema, **kwargs):
        self.calls.append({"model": model, "schema": schema})
        return self._output


def _llm_all_pass() -> CriticLLMOutput:
    return CriticLLMOutput(
        voice_match="pass", voice_note="reads like FT",
        banned_phrase_scan="pass", banned_phrase_note="(LLM)",
        length_compliance="pass", length_note="(LLM)",
        structure="pass", structure_note="(LLM)",
        grounding="pass", grounding_note="claims supported",
        hype_check="pass", hype_note="no overclaim",
    )


def test_run_returns_pass_when_everything_clean():
    settings = load_settings()
    report = critique.run(_draft(), FakeLLM(_llm_all_pass()), settings)
    assert report.overall_pass is True
    assert report.critic_model == settings.critic.model
    # Mechanical notes win over the LLM "(LLM)" placeholders.
    assert "no banned phrases" in report.banned_phrase_scan.note


def test_run_fails_overall_when_mechanical_check_fails():
    settings = load_settings()
    # Inject an em-dash → banned phrase mechanical fail, regardless of LLM.
    bad_post = GOOD_POST.replace("ETH Zürich", "ETH Zürich — the")
    draft = _draft(post_text=bad_post)
    report = critique.run(draft, FakeLLM(_llm_all_pass()), settings)
    assert report.overall_pass is False
    assert report.banned_phrase_scan.result == "fail"
    assert "em-dash" in report.banned_phrase_scan.note


def test_run_uses_llm_judgment_for_voice():
    settings = load_settings()
    llm_out = _llm_all_pass()
    llm_out = llm_out.model_copy(update={"voice_match": "fail", "voice_note": "performs"})
    report = critique.run(_draft(), FakeLLM(llm_out), settings)
    assert report.voice_match.result == "fail"
    assert report.voice_match.note == "performs"
    assert report.overall_pass is False


def test_run_grounding_mechanical_override_when_span_missing():
    settings = load_settings()
    # Claims point at text that's not in the paper sections.
    bad_claims = [
        Claim(claim="x", source_span="entirely fabricated quote", page=1),
    ]
    draft = _draft(claims=bad_claims)
    # LLM says pass on grounding, but code overrides because the span isn't real.
    report = critique.run(draft, FakeLLM(_llm_all_pass()), settings)
    assert report.grounding.result == "fail"


def test_failure_notes_packs_only_failed_checks():
    report = CriticReport(
        voice_match=CheckResult(result="fail", note="too breathless"),
        banned_phrase_scan=CheckResult(result="pass", note="ok"),
        length_compliance=CheckResult(result="fail", note="too long: 1850"),
        structure=CheckResult(result="pass", note="ok"),
        grounding=CheckResult(result="pass", note="ok"),
        hype_check=CheckResult(result="pass", note="ok"),
        overall_pass=False,
        critic_model="x",
    )
    notes = failure_notes(report)
    assert len(notes) == 2
    assert any("voice" in n for n in notes)
    assert any("length" in n for n in notes)
