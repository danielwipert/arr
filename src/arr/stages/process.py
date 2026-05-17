"""Stage 3 — Processor.

Fetches the PDF for each surviving paper, extracts text, and segments it
into the sections defined in the spec. The downstream ranker, drafter, and
critic stages all read from these sections rather than re-parsing the PDF.

Section detection is heuristic: arXiv papers don't share one template, so we
look for headers that look like `Introduction`, `1 Method`, `3.2 Results`,
etc., and bucket the in-between text. Unmatched material falls into the
nearest preceding bucket, which is the right behaviour for the "1.1
Notation" sub-headers that sit inside a Method section.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from arr.config import Settings
from arr.models import FilteredPaper, ProcessedPaper
from arr.providers.papers import PaperSourceProvider

log = logging.getLogger(__name__)


# Canonical section keys we care about. Anything else gets dropped.
SECTION_KEYS = (
    "abstract",
    "intro",
    "method",
    "experiments",
    "results",
    "limitations",
    "conclusions",
    "references",
)

# Map header-token (lowercased, stripped of leading numbering) to canonical key.
_HEADER_SYNONYMS: dict[str, str] = {
    "abstract": "abstract",
    "introduction": "intro",
    "background": "intro",
    "method": "method",
    "methods": "method",
    "methodology": "method",
    "approach": "method",
    "model": "method",
    "models": "method",
    "our method": "method",
    "experiment": "experiments",
    "experiments": "experiments",
    "experimental setup": "experiments",
    "evaluation": "experiments",
    "experimental results": "results",
    "results": "results",
    "findings": "results",
    "main results": "results",
    "limitation": "limitations",
    "limitations": "limitations",
    "discussion of limitations": "limitations",
    "conclusion": "conclusions",
    "conclusions": "conclusions",
    "discussion": "conclusions",
    "concluding remarks": "conclusions",
    "references": "references",
    "bibliography": "references",
}

# A line is a candidate header if it's short, mostly title-case or uppercase,
# and optionally prefixed with section numbering like "1", "1.", "1.1", "I.".
_HEADER_RE = re.compile(
    r"""^\s*
        (?:
            (?:\d+(?:\.\d+){0,2}\.?\s+) |   # 1, 1., 1.1, 1.1.1
            (?:[IVX]+\.?\s+)                # I, II, III
        )?
        (?P<label>[A-Za-z][A-Za-z &/-]{2,49})
        \s*$
    """,
    flags=re.VERBOSE,
)


def _normalize_header_label(raw: str) -> str | None:
    """Return a canonical section key for a header line, or None if not a section header we care about."""
    label = raw.strip().lower()
    # Strip trailing punctuation.
    label = label.rstrip(":.")
    return _HEADER_SYNONYMS.get(label)


def segment_sections(text: str) -> dict[str, str]:
    """Bucket the paper's text into canonical sections.

    Walks the text line by line. Any line that matches a section header
    synonym opens a new bucket; intervening lines are appended to the most
    recently opened bucket. Text before the first recognised header is
    discarded (it's usually the title block and affiliations).
    """
    buckets: dict[str, list[str]] = {key: [] for key in SECTION_KEYS}
    current: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = _HEADER_RE.match(line)
        if match:
            key = _normalize_header_label(match.group("label"))
            if key is not None:
                current = key
                continue
        if current is not None and line:
            buckets[current].append(line)

    return {key: " ".join(lines) for key, lines in buckets.items() if lines}


def extract_text_with_pdfplumber(pdf_path: Path) -> tuple[str, int]:
    """Extract concatenated page text and page count. Lazy-imports pdfplumber."""
    import pdfplumber  # type: ignore[import-untyped]

    pages: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return "\n".join(pages), len(pages)


def process_one(
    paper: FilteredPaper,
    paper_source: PaperSourceProvider,
) -> ProcessedPaper | None:
    """Fetch + parse a single paper. Returns None if extraction failed."""
    try:
        pdf_path = paper_source.fetch_pdf(paper.arxiv_id)
    except Exception as e:  # network, 404, etc.
        log.warning("Process %s: PDF fetch failed (%s)", paper.arxiv_id, e)
        return None

    try:
        text, page_count = extract_text_with_pdfplumber(pdf_path)
    except Exception as e:
        log.warning("Process %s: PDF text extraction failed (%s)", paper.arxiv_id, e)
        return None

    sections = segment_sections(text)
    # Always include the abstract from arXiv metadata if the heuristic missed it.
    sections.setdefault("abstract", paper.abstract)

    if len(sections) < 2:
        # Almost nothing extracted; downstream stages can't do useful work.
        log.warning(
            "Process %s: only %d sections extracted; skipping",
            paper.arxiv_id,
            len(sections),
        )
        return None

    return ProcessedPaper(
        **paper.model_dump(),
        sections=sections,
        pdf_local_path=str(pdf_path),
        page_count=page_count,
    )


def run(
    papers: list[FilteredPaper],
    paper_source: PaperSourceProvider,
    settings: Settings,
) -> list[ProcessedPaper]:
    del settings  # not used yet; placeholder for future per-stage config
    out: list[ProcessedPaper] = []
    for paper in papers:
        processed = process_one(paper, paper_source)
        if processed is not None:
            out.append(processed)
    log.info("Process: %d/%d papers parsed", len(out), len(papers))
    return out
