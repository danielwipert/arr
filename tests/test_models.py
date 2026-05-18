"""Smoke tests for the inter-stage artifact models."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from arr.models import (
    Claim,
    CheckResult,
    CriticReport,
    DimensionScore,
    FilteredPaper,
    FinalCriticReport,
    FinalPost,
    ProcessedPaper,
    RankedPaper,
    RankerScores,
    RawPaper,
    SkipRecord,
    SkipTopPaper,
)


def _raw_paper() -> RawPaper:
    return RawPaper(
        arxiv_id="2026.12345",
        title="Query Decomposition for Robust RAG",
        authors=["Müller, A.", "Schmidt, B."],
        abstract="An abstract about retrieval...",
        primary_cat="cs.CL",
        all_cats=["cs.CL", "cs.IR"],
        submitted_at=datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc),
        pdf_url="https://arxiv.org/pdf/2026.12345",
    )


def test_raw_paper_roundtrip():
    paper = _raw_paper()
    again = RawPaper.model_validate_json(paper.model_dump_json())
    assert again == paper


def test_filtered_paper_inherits_raw_fields():
    raw = _raw_paper().model_dump()
    raw.update(in_scope=True, primary_topic="rag", dedup_similarity=0.41, noise_flagged=False)
    filtered = FilteredPaper(**raw)
    assert filtered.arxiv_id == "2026.12345"
    assert filtered.primary_topic == "rag"


def test_processed_paper_carries_sections():
    raw = _raw_paper().model_dump()
    raw.update(in_scope=True, primary_topic="rag", noise_flagged=False)
    processed = ProcessedPaper(
        **raw,
        sections={"abstract": "...", "intro": "...", "method": "..."},
        pdf_local_path="/tmp/x.pdf",
        page_count=12,
    )
    assert processed.page_count == 12


def test_ranked_paper_composite_bounds():
    raw = _raw_paper().model_dump()
    raw.update(in_scope=True, primary_topic="rag", noise_flagged=False)
    scores = {
        "significance": DimensionScore(score=8, justification="meaningful build impact"),
        "novelty": DimensionScore(score=7, justification="distinct framing"),
        "reproducibility": DimensionScore(score=6, justification="code partial"),
        "clarity": DimensionScore(score=8, justification="well written"),
        "topical_fit": DimensionScore(score=9, justification="core RAG"),
    }
    ranked = RankedPaper(
        **raw,
        scores=scores,
        composite=7.65,
    )
    assert ranked.composite == 7.65

    with pytest.raises(ValidationError):
        RankedPaper(
            **raw,
            scores=scores,
            composite=11.0,
        )


def test_dimension_score_rejects_out_of_range():
    with pytest.raises(ValidationError):
        DimensionScore(score=11, justification="too high")
    with pytest.raises(ValidationError):
        DimensionScore(score=-1, justification="too low")


def test_critic_report_pass_fail_literal():
    check = CheckResult(result="pass", note="clean")
    assert check.result == "pass"
    with pytest.raises(ValidationError):
        CheckResult(result="maybe", note="...")  # type: ignore[arg-type]

    report = CriticReport(
        voice_match=check,
        banned_phrase_scan=check,
        length_compliance=check,
        structure=check,
        grounding=check,
        hype_check=check,
        overall_pass=True,
        critic_model="anthropic/claude-sonnet-4-7",
    )
    assert report.overall_pass is True


def test_claim_requires_positive_page():
    Claim(claim="...", source_span="verbatim text", page=1)
    with pytest.raises(ValidationError):
        Claim(claim="...", source_span="...", page=0)


def test_final_post_section_6_1_shape():
    artifact = FinalPost(
        date="2026-05-16",
        paper_id="arxiv:2026.12345",
        paper_title="Query Decomposition for Robust RAG",
        paper_authors=["Müller, A.", "Schmidt, B."],
        paper_url="https://arxiv.org/abs/2026.12345",
        post_text="...",
        post_char_count=1547,
        hook_char_count=132,
        claims=[Claim(claim="twelve-point gain", source_span="71.2 vs 59.4", page=6)],
        ranker_scores=RankerScores(
            significance=8, novelty=7, reproducibility=6,
            clarity=8, topical_fit=9, composite=7.65,
        ),
        critic_report=FinalCriticReport(
            voice_match="pass",
            banned_phrase_scan="pass",
            length_compliance="pass",
            structure="pass",
            grounding="pass",
            hype_check="pass",
            retries_used=1,
            notes="First draft used 'game-changer'. Retry clean.",
        ),
        generated_at=datetime(2026, 5, 16, 8, 14, 22, tzinfo=timezone.utc),
        drafter_model="anthropic/claude-sonnet-4-7",
        critic_model="anthropic/claude-sonnet-4-7",
    )
    payload = artifact.model_dump_json()
    again = FinalPost.model_validate_json(payload)
    assert again == artifact


def test_skip_record_section_6_2_shape():
    record = SkipRecord(
        date="2026-05-17",
        papers_considered=37,
        papers_filtered=34,
        papers_ranked=3,
        top_paper=SkipTopPaper(arxiv_id="arxiv:2026.99999", title="...", composite=6.4),
        reason="No paper above post_worthy_threshold (7.0)",
    )
    assert record.top_paper is not None
    assert record.top_paper.composite == 6.4
