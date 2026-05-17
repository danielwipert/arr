"""Stage 5 — Selector.

Picks at most one paper per day. The rule (Section 4.3):

    if composite >= post_worthy_threshold: select the top one
    else: skip the day

`None` is a success state, not a failure — a feed that posts only when
there is something to say accumulates trust faster than one that posts
daily out of obligation.
"""

from __future__ import annotations

import logging
from datetime import date as date_cls

from arr.config import Settings
from arr.models import RankedPaper, SkipRecord, SkipTopPaper

log = logging.getLogger(__name__)


def select_top(
    ranked: list[RankedPaper], settings: Settings
) -> RankedPaper | None:
    """Return the highest-composite paper if it clears the threshold, else None.

    The ranker stage already sorts descending, but we don't rely on that —
    re-sort here so the selector can be called with a list in any order.
    """
    if not ranked:
        return None
    threshold = settings.selector.post_worthy_threshold
    top = max(ranked, key=lambda p: p.composite)
    if top.composite >= threshold:
        log.info(
            "Select: picked %s with composite %.2f (>= %.2f)",
            top.arxiv_id, top.composite, threshold,
        )
        return top
    log.info(
        "Select: top composite %.2f below threshold %.2f; skip day",
        top.composite, threshold,
    )
    return None


def build_skip_record(
    *,
    run_date: date_cls,
    papers_considered: int,
    papers_filtered: int,
    ranked: list[RankedPaper],
    settings: Settings,
) -> SkipRecord:
    """Construct the SkipRecord written on days where no post is produced.

    `papers_filtered` is the count entering the ranker (Stage 4's input).
    `ranked` is the ranker's output. The reason string is derived from the
    pipeline state so that calibration over the first two months has the
    context it needs.
    """
    top_paper = None
    threshold = settings.selector.post_worthy_threshold

    if ranked:
        top = max(ranked, key=lambda p: p.composite)
        top_paper = SkipTopPaper(
            arxiv_id=top.arxiv_id,
            title=top.title,
            composite=top.composite,
        )
        reason = (
            f"No paper above post_worthy_threshold ({threshold}); "
            f"top composite was {top.composite:.2f}"
        )
    elif papers_filtered == 0:
        reason = "No papers in scope after filtering"
    else:
        # Filter passed some papers but the ranker dropped them all (LLM errors,
        # bad data). Worth surfacing as a distinct skip cause for ops.
        reason = "All filtered papers failed to rank"

    return SkipRecord(
        date=run_date.isoformat(),
        papers_considered=papers_considered,
        papers_filtered=papers_filtered,
        papers_ranked=len(ranked),
        top_paper=top_paper,
        reason=reason,
    )
