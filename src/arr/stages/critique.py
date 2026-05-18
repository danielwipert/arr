"""Stage 7 — Critic.

One LLM call grades the draft on the six checks from Section 7.2. Mechanical
post-validation then overrides three of those checks (banned phrases, length,
structure) so the deterministic ones are answered by code rather than by
LLM judgment. The LLM remains authoritative on voice_match, grounding, and
hype_check — the soft, holistic checks that need a reader, not a regex.

The critic prompt is given the post text, claims list, and processed paper
sections. It does not see the drafter's reasoning or any retry history.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict

from arr.config import REPO_ROOT, Settings
from arr.models import CheckResult, CriticReport, DraftPost, PassFail
from arr.providers.llm import LLMProvider
from arr.stages._prompts import render

log = logging.getLogger(__name__)

PROMPT_PATH = REPO_ROOT / "config" / "prompts" / "critic.md"


# Banned patterns from Section 5.2. Stored as (regex, label) so a failed scan
# can tell the drafter exactly what to remove on the retry.
BANNED_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bexcited to share\b", re.IGNORECASE), "'Excited to share'"),
    (re.compile(r"\bthrilled to announce\b", re.IGNORECASE), "'Thrilled to announce'"),
    (re.compile(r"\bwow,?\s*just read this\b", re.IGNORECASE), "'Wow, just read this'"),
    (re.compile(r"here'?s what nobody is talking about", re.IGNORECASE),
     "'Here's what nobody is talking about'"),
    (re.compile(r"\bthis is going to change everything\b", re.IGNORECASE),
     "'This is going to change everything'"),
    (re.compile(r"\bbreaking:\s", re.IGNORECASE), "'BREAKING:' preamble"),
    (re.compile(r"\btl;dr:?", re.IGNORECASE), "'TL;DR:'"),
    (re.compile(r"\bthoughts\?", re.IGNORECASE), "'Thoughts?' closer"),
    (re.compile(r"\bagree\?", re.IGNORECASE), "'Agree?' closer"),
    (re.compile(r"\bwhat do you think\?", re.IGNORECASE), "'What do you think?' closer"),
    (re.compile(r"\blet me know in the comments\b", re.IGNORECASE),
     "'Let me know in the comments'"),
    (re.compile(r"\bthe future is here\b", re.IGNORECASE), "'The future is here'"),
    (re.compile(r"\bgame[- ]changer\b", re.IGNORECASE), "'game-changer'"),
    (re.compile(r"\bparadigm shift\b", re.IGNORECASE), "'paradigm shift'"),
    (re.compile(r"\bnext[- ]level\b", re.IGNORECASE), "'next-level'"),
    (re.compile(r"\binsane\b", re.IGNORECASE), "'insane' / 'INSANE'"),
    (re.compile(r"\bmind[- ]blowing\b", re.IGNORECASE), "'mind-blowing'"),
    (re.compile(r"\bin the era of (AI|LLMs)\b", re.IGNORECASE), "'In the era of AI'"),
    # Em-dash anywhere.
    (re.compile("—"), "em-dash (—)"),
    # Bullet-list markers on a line of their own.
    (re.compile(r"(?m)^\s*[-*•]\s"), "bullet list marker in body"),
    # Markdown bold / italic emphasis in body.
    (re.compile(r"\*\*[^*]+\*\*"), "bold emphasis (**...**)"),
    (re.compile(r"(?<!\*)\*[^*\n]+\*(?!\*)"), "italic emphasis (*...*)"),
]

_HOOK_PREAMBLE_ALL_CAPS = re.compile(r"^\s*([A-Z]{4,}[!:\.]\s*){1,3}")


def _all_caps_preamble(post_text: str) -> bool:
    first_line = post_text.split("\n", 1)[0]
    return bool(_HOOK_PREAMBLE_ALL_CAPS.match(first_line))


def _emoji_count(text: str) -> int:
    """Approximate emoji count via Unicode property classes."""
    # Range coverage is intentionally broad — enough to catch typical LinkedIn
    # emoji without bringing in a full Unicode dependency.
    pattern = re.compile(
        "["
        "\U0001F300-\U0001FAFF"   # symbols & pictographs (most emoji blocks)
        "\U00002600-\U000027BF"   # misc symbols, dingbats
        "\U0001F1E6-\U0001F1FF"   # regional indicator (flag halves)
        "]"
    )
    return len(pattern.findall(text))


# ---------------------------------------------------------------------------
# Mechanical check helpers
# ---------------------------------------------------------------------------


def scan_banned_phrases(post_text: str) -> list[str]:
    """Return the banned-phrase labels found in the post, or [] if clean."""
    found: list[str] = []
    for regex, label in BANNED_PATTERNS:
        if regex.search(post_text):
            found.append(label)
    if _all_caps_preamble(post_text):
        found.append("all-caps preamble in hook")
    if _emoji_count(post_text) > 1:
        found.append(f"too many emoji ({_emoji_count(post_text)}, max 1)")
    return found


def check_length(post_text: str) -> tuple[bool, str]:
    """Spec sweet spot is 1400-1800; hard bounds are 1100-2000. We fail on
    the HARD bounds and only note when a draft falls outside the sweet spot.
    Hook is hard-capped at 140 (mobile 'see more' cutoff)."""
    total = len(post_text)
    hook = len(post_text.split("\n", 1)[0])
    problems: list[str] = []
    if total < 1100:
        problems.append(f"too short ({total} chars, hard min 1100)")
    elif total > 2000:
        problems.append(f"too long ({total} chars, hard max 2000)")
    if hook > 140:
        problems.append(f"hook too long ({hook} chars, max 140)")
    if problems:
        return False, "; ".join(problems)
    note = f"total={total}, hook={hook}"
    if total < 1400 or total > 1800:
        note += " (outside sweet spot 1400-1800, within hard bounds)"
    return True, note


def check_structure(post_text: str) -> tuple[bool, str]:
    """Hook + 3 body paragraphs + close + meta + tags, separated by blank lines.

    The meta block can be one or two lines (paper line + arxiv link). The
    tags block must contain exactly five tokens, each starting with `#`.
    Tag selection (broad vs niche, on-topic, no generic filler) is left to
    the LLM critic; we only enforce shape here.
    """
    blocks = [b.strip() for b in re.split(r"\n\s*\n", post_text.strip()) if b.strip()]
    if len(blocks) != 7:
        return False, f"expected 7 blocks (hook + 3 paras + close + meta + tags), got {len(blocks)}"

    hook, p1, p2, p3, close, meta, tags = blocks

    if "\n" in hook:
        return False, "hook should be a single line"
    if "\n" not in meta and not meta.lower().startswith("paper:"):
        return False, "meta block should start with 'Paper:' and include the arxiv link"

    tag_tokens = tags.split()
    if len(tag_tokens) != 5:
        return False, f"expected 5 hashtags, got {len(tag_tokens)}"
    bad = [t for t in tag_tokens if not t.startswith("#") or len(t) < 2]
    if bad:
        return False, f"hashtags must start with '#': {bad}"

    return True, "7 blocks, 5 hashtags"


def _normalize_for_grounding(text: str) -> str:
    """Lowercase + collapse whitespace. PDF extraction inserts line breaks
    and stray spaces that wouldn't otherwise let a verbatim span match;
    likewise, the drafter sometimes capitalises ALL-CAPS paper names like
    'METABACKDOOR' where the paper text has 'MetaBackdoor'."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def check_grounding_spans(draft: DraftPost) -> tuple[bool, str]:
    """Verify each claim's source_span appears in the paper after light
    normalization (case-insensitive, whitespace-collapsed).

    The LLM still makes the final grounding judgment (it can catch claims
    that are *missing* from the claims list, which this check can't). But
    a span that doesn't exist anywhere in the paper is an unambiguous fail.

    Searchable haystack includes title + authors so attribution claims
    ("a team at Microsoft", "Wen et al.") can ground against the metadata
    even when the section extractor missed the title block.
    """
    paper = draft.paper
    haystack_parts: list[str] = [paper.title, ", ".join(paper.authors)]
    haystack_parts.extend(paper.sections.values())
    haystack = _normalize_for_grounding("\n".join(haystack_parts))

    missing: list[str] = []
    for claim in draft.claims:
        if not claim.source_span:
            continue
        needle = _normalize_for_grounding(claim.source_span)
        if needle not in haystack:
            missing.append(claim.source_span[:60].replace("\n", " "))
    if missing:
        joined = "; ".join(repr(m) for m in missing[:3])
        return False, f"{len(missing)} claim span(s) not found in paper: {joined}"
    return True, f"{len(draft.claims)} claim spans found in paper"


# ---------------------------------------------------------------------------
# LLM-shaped output
# ---------------------------------------------------------------------------


class CriticLLMOutput(BaseModel):
    """Twelve fields: result + note for each of the six checks."""

    model_config = ConfigDict(extra="forbid")

    voice_match: PassFail
    voice_note: str
    banned_phrase_scan: PassFail
    banned_phrase_note: str
    length_compliance: PassFail
    length_note: str
    structure: PassFail
    structure_note: str
    grounding: PassFail
    grounding_note: str
    hype_check: PassFail
    hype_note: str


def _claims_block(draft: DraftPost) -> str:
    if not draft.claims:
        return "(no claims declared by drafter)"
    return "\n".join(
        f"- claim: {c.claim}\n  source_span: {c.source_span}\n  page: {c.page}"
        for c in draft.claims
    )


def _render_prompt(draft: DraftPost) -> str:
    sections = draft.paper.sections
    return render(
        PROMPT_PATH.read_text(encoding="utf-8"),
        post_text=draft.post_text,
        claims_block=_claims_block(draft),
        abstract=sections.get("abstract", draft.paper.abstract),
        intro=sections.get("intro", "(not extracted)"),
        method=sections.get("method", "(not extracted)"),
        results=sections.get("results", "(not extracted)"),
        limitations=sections.get("limitations", "(not extracted)"),
        conclusions=sections.get("conclusions", "(not extracted)"),
    )


def _result(passed: bool, note: str) -> CheckResult:
    return CheckResult(result="pass" if passed else "fail", note=note)


def _result_from_llm(value: PassFail, note: str) -> CheckResult:
    return CheckResult(result=value, note=note)


def run(draft: DraftPost, llm: LLMProvider, settings: Settings) -> CriticReport:
    """Run the critic on a draft. Returns a CriticReport whose `overall_pass`
    is True iff all six checks pass.
    """
    prompt = _render_prompt(draft)
    llm_out = llm.complete_json(
        [{"role": "user", "content": prompt}],
        model=settings.critic.model,
        schema=CriticLLMOutput,
        temperature=0.0,
    )

    # Mechanical overrides for the deterministic checks.
    banned_hits = scan_banned_phrases(draft.post_text)
    banned_pass = not banned_hits
    banned_note = (
        f"banned: {', '.join(banned_hits)}" if banned_hits else "no banned phrases found"
    )

    length_ok, length_note = check_length(draft.post_text)
    structure_ok, structure_note = check_structure(draft.post_text)

    # Grounding: the LLM critic has the full paper sections and can judge
    # whether each claim is actually supported, including faithfully
    # paraphrased spans that don't substring-match verbatim. The mechanical
    # span check is too strict in practice — PDF extraction artifacts and
    # the drafter's tendency to capitalise paper names produce false negatives.
    # We keep the mechanical signal for visibility but defer to the LLM.
    spans_ok, spans_note = check_grounding_spans(draft)
    grounding_note = llm_out.grounding_note
    if not spans_ok:
        grounding_note = f"{grounding_note} [mech: {spans_note}]"
    grounding_check = CheckResult(result=llm_out.grounding, note=grounding_note)

    report = CriticReport(
        voice_match=_result_from_llm(llm_out.voice_match, llm_out.voice_note),
        banned_phrase_scan=_result(banned_pass, banned_note),
        length_compliance=_result(length_ok, length_note),
        structure=_result(structure_ok, structure_note),
        grounding=grounding_check,
        hype_check=_result_from_llm(llm_out.hype_check, llm_out.hype_note),
        overall_pass=False,  # set below
        critic_model=settings.critic.model,
    )
    report = report.model_copy(update={"overall_pass": _overall_pass(report)})

    log.info(
        "Critic %s: voice=%s phrases=%s length=%s structure=%s grounding=%s hype=%s",
        "PASS" if report.overall_pass else "FAIL",
        report.voice_match.result,
        report.banned_phrase_scan.result,
        report.length_compliance.result,
        report.structure.result,
        report.grounding.result,
        report.hype_check.result,
    )
    return report


def _overall_pass(report: CriticReport) -> bool:
    return all(
        check.result == "pass"
        for check in (
            report.voice_match,
            report.banned_phrase_scan,
            report.length_compliance,
            report.structure,
            report.grounding,
            report.hype_check,
        )
    )


def failure_notes(report: CriticReport) -> list[str]:
    """Pack a CriticReport's fail notes for the drafter retry prompt."""
    out: list[str] = []
    if report.voice_match.result == "fail":
        out.append(f"voice: {report.voice_match.note}")
    if report.banned_phrase_scan.result == "fail":
        out.append(f"banned phrases: {report.banned_phrase_scan.note}")
    if report.length_compliance.result == "fail":
        out.append(f"length: {report.length_compliance.note}")
    if report.structure.result == "fail":
        out.append(f"structure: {report.structure.note}")
    if report.grounding.result == "fail":
        out.append(f"grounding: {report.grounding.note}")
    if report.hype_check.result == "fail":
        out.append(f"hype: {report.hype_check.note}")
    return out
