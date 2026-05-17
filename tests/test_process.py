"""Tests for Stage 3 processor.

We avoid actually parsing PDFs in unit tests — the PDF parsing path is
verified end-to-end in a separate (slow) test if needed. Here we exercise
the section segmenter directly and the pipeline orchestration with a
patched extractor.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from arr.config import load_settings
from arr.models import FilteredPaper
from arr.stages import process as process_stage
from arr.stages.process import segment_sections


def _filtered_paper(arxiv_id: str = "2026.0001") -> FilteredPaper:
    return FilteredPaper(
        arxiv_id=arxiv_id,
        title="Query Decomposition for Robust RAG",
        authors=["A. Researcher"],
        abstract="We propose a query decomposition method.",
        primary_cat="cs.CL",
        all_cats=["cs.CL", "cs.IR"],
        submitted_at=datetime(2026, 5, 16, 12, 0, tzinfo=timezone.utc),
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
        in_scope=True,
        primary_topic="rag",
        dedup_similarity=None,
        noise_flagged=False,
    )


class FakePaperSource:
    def __init__(self, pdf_paths: dict[str, Path] | None = None, fail: bool = False):
        self._paths = pdf_paths or {}
        self._fail = fail

    def fetch_recent(self, *_, **__):
        raise NotImplementedError

    def fetch_pdf(self, arxiv_id: str) -> Path:
        if self._fail:
            raise RuntimeError("network down")
        return self._paths.get(arxiv_id, Path(f"/tmp/{arxiv_id}.pdf"))


# --- segment_sections ----------------------------------------------------


def test_segment_sections_basic():
    text = """\
Title Block
Authors and affiliations

Abstract
This paper proposes a new method for X. We show that Y.

1 Introduction
The recent rise of LLMs has motivated much work on Z.
Prior work tackles this with naive approaches.

2 Method
We introduce a query decomposition step.
The decomposition runs before retrieval.

3 Experiments
We evaluate on HotpotQA, TriviaQA, and NQ.

4 Results
Our approach achieves 71.2 on HotpotQA.

5 Limitations
Our decomposition relies on a separate small model.

6 Conclusion
Decomposition matters more than reranking.

References
[1] ...
"""
    out = segment_sections(text)
    assert "abstract" in out
    assert "intro" in out
    assert "method" in out
    assert "experiments" in out
    assert "results" in out
    assert "limitations" in out
    assert "conclusions" in out
    assert "references" in out
    assert "query decomposition" in out["method"].lower()
    assert "71.2" in out["results"]


def test_segment_sections_handles_dotted_numbering():
    text = """\
1. Introduction
LLMs are common.

2. Method
We do a thing.
"""
    out = segment_sections(text)
    assert "intro" in out
    assert "method" in out
    assert "we do a thing" in out["method"].lower()


def test_segment_sections_drops_unknown_headers():
    text = """\
Acknowledgements
Thanks to our funders.

Introduction
Real content here.
"""
    out = segment_sections(text)
    assert "intro" in out
    # Acknowledgements isn't a canonical key, so nothing for it.
    assert "acknowledgements" not in out


def test_segment_sections_synonyms_collapse():
    text = """\
Methodology
Algorithm details go here.

Findings
Numbers go here.
"""
    out = segment_sections(text)
    assert "method" in out and "algorithm" in out["method"].lower()
    assert "results" in out and "numbers" in out["results"].lower()


# --- run() orchestration -------------------------------------------------


def test_run_skips_papers_when_pdf_fetch_fails(monkeypatch):
    paper = _filtered_paper()
    source = FakePaperSource(fail=True)

    out = process_stage.run([paper], source, load_settings())
    assert out == []


def test_run_skips_papers_when_extraction_yields_almost_nothing(monkeypatch):
    paper = _filtered_paper()
    source = FakePaperSource()

    def fake_extract(_path: Path) -> tuple[str, int]:
        return "", 0

    monkeypatch.setattr(process_stage, "extract_text_with_pdfplumber", fake_extract)
    out = process_stage.run([paper], source, load_settings())
    assert out == []


def test_run_returns_processed_paper_on_success(monkeypatch):
    paper = _filtered_paper()
    source = FakePaperSource()

    def fake_extract(_path: Path) -> tuple[str, int]:
        return (
            "Abstract\nWe do X.\n\n1 Introduction\nMotivation.\n\n2 Method\nOur approach.\n",
            8,
        )

    monkeypatch.setattr(process_stage, "extract_text_with_pdfplumber", fake_extract)
    out = process_stage.run([paper], source, load_settings())

    assert len(out) == 1
    processed = out[0]
    assert processed.arxiv_id == "2026.0001"
    assert processed.page_count == 8
    assert "method" in processed.sections
    assert "abstract" in processed.sections
    # in_scope and primary_topic survive from FilteredPaper.
    assert processed.in_scope is True
    assert processed.primary_topic == "rag"


def test_run_falls_back_to_abstract_metadata_when_pdf_lacks_abstract(monkeypatch):
    paper = _filtered_paper()
    source = FakePaperSource()

    def fake_extract(_path: Path) -> tuple[str, int]:
        # No "Abstract" header in the PDF text — but other sections present.
        return ("1 Introduction\nMotivation.\n\n2 Method\nApproach.\n", 5)

    monkeypatch.setattr(process_stage, "extract_text_with_pdfplumber", fake_extract)
    out = process_stage.run([paper], source, load_settings())
    assert out[0].sections["abstract"] == paper.abstract
