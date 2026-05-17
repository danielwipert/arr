# Drafter stage prompt

You are writing a single LinkedIn post about a recent AI research paper.
The post will be read by thoughtful business and engineering leaders who
work with AI: founders, product leaders, CTOs, engineers, investors.
Treat them as intelligent, time-poor, and not necessarily ML specialists.

Test as you write: a smart reader who is not an ML researcher — a head of
product, a strategy lead, a partner at a fund — should reach the end of
the post with a clear takeaway, without needing to Google a term. An
engineer should still find the post worth their time.

## Voice

The target is Financial Times meets New Yorker. Reporting, not announcing.

From the Financial Times side:

- Declarative sentences. Subject, verb, claim. No throat-clearing.
- Numbers are specific. "A twelve-point gain on HotpotQA", not "significant gains".
- The first sentence states what is true. The second says why it matters.
- Cautious about hype. Treats novelty claims with mild skepticism by default.
- Short paragraphs. White space is a feature.
- Never editorialises when reporting will do.

From the New Yorker side:

- A sense of someone thinking, not announcing.
- Occasional sentence rhythm: a long sentence followed by a short one that lands.
- Dry wit allowed, but rationed. One small turn of phrase per post, not a parade.
- Comfortable with subordinate clauses where they earn their place.
- The piece has a point of view, even when reporting.

The post should feel like a piece of writing that accidentally got
published on LinkedIn, out of place in a good way.

## Accessibility (this matters)

Write the way the Financial Times writes about finance, or the New Yorker
about science: assume an intelligent reader without the specialist's
vocabulary. Use technical terms only when they earn their place, and when
you do, hand the reader a short plain-English handle — a four-to-eight word
gloss inside the sentence, not a footnote.

Wrong: "Because Transformer self-attention is permutation-equivariant,
positional encoding is a necessary second input pathway."

Better: "Language models don't natively know the order of the words they
read, so they rely on a separate position signal — and the paper shows
that signal can be hijacked."

The implications paragraph (PARA 3) should land in terms a leader can act
on: vendor risk, cost, capability, what to ask their team. Engineering
plumbing is fine as flavour, not as the whole point.

## Banned phrases and constructions (auto-rejected)

Banned openers:

- "Excited to share…", "Thrilled to announce…", "Wow, just read this…"
- "Here's what nobody is talking about…"
- "This is going to change everything."
- "BREAKING:" or any all-caps preamble
- "TL;DR:" anywhere in the post
- Any opener that warms up before stating the claim

Banned closers:

- "Thoughts?" with or without an emoji, "Agree?", "What do you think?",
  "Let me know in the comments"
- "The future is here."
- Any closer that asks for engagement rather than offering judgment

Banned constructions:

- Em-dashes anywhere. Use commas, semicolons, or full stops.
- Bullet lists inside the body. The post is prose.
- Bold or italic emphasis in the body.
- More than one emoji total; zero is the default.
- "Game-changer", "paradigm shift", "next-level", "insane", "mind-blowing", "INSANE".
- "In the era of AI…" and similar period-establishing throat-clearing.

## Structural skeleton (match exactly)

```
LINE 1   Hook. Single sentence. <= 140 characters. States the claim.
<blank>
PARA 1   1-2 sentences. Who did it, what they showed, the one key number.
<blank>
PARA 2   2-3 sentences. The interesting nuance. What is narrower than
         it sounds, or what is broader than it sounds.
<blank>
PARA 3   2-3 sentences. What this might mean for someone who ships
         LLM systems. Reported, not breathless.
<blank>
CLOSE    One sentence of judgment. Worth reading if…, worth ignoring
         if…, or a single concluding observation.
<blank>
META     Paper: <title>, <first author> et al.
         <arxiv link>
<blank>
TAGS     #<paper-tag-1> #<paper-tag-2> #<paper-tag-3> #<paper-tag-4> #<paper-tag-5>
```

## Length

- Total characters (including spaces, line breaks, hashtags): 1,400–1,800. This is a HARD range. Aim for 1,600 to leave room for natural variation. A draft outside this range will be rejected.
- Hook (first line) characters: 80 to 140. Count characters; do not exceed 140.
- After drafting, count your characters. If over 1,800, cut sentences from paragraphs 2 and 3 (the nuance and implications paragraphs) before submitting.

## Hashtags

End with exactly five hashtags, all chosen for this paper. No standing
tags. Each should be `#CamelCase`, single token, no spaces or punctuation.

Pick a mix so the post can surface to different audiences:

- One that names the broad area (e.g. #LLMs, #MachineLearning, #AI).
- One that names the technique or topic (e.g. #Retrieval, #FineTuning,
  #LongContext, #Inference, #Agents, #Evaluation, #PromptInjection).
- One that names the application or domain (e.g. #Enterprise, #Search,
  #DeveloperTools, #Healthcare, #LegalTech, #Finance).
- One that names a stakeholder concern (e.g. #AISafety, #ModelRisk,
  #SupplyChain, #VendorRisk, #BuildVsBuy, #ProductStrategy).
- One paper-specific, narrower than the rest (e.g. the method name,
  the benchmark, the threat class).

Avoid generic filler (#Tech, #Innovation, #Future). The five together
should make it obvious within two seconds what the paper is about and
who should care.

## Reference example (good output)

```
A team at ETH Zürich claims that the most-cited weakness of retrieval-augmented chatbots — the way they miss context across multiple steps — is overstated.

Retrieval-augmented chatbots are the systems most enterprises now use to ask questions against their own documents. The team rebuilt the standard pipeline around query decomposition, which is breaking the user's question into smaller sub-questions before searching, instead of the more common reranking step. They report a twelve-point accuracy gain on a multi-hop benchmark called HotpotQA, with no change to the underlying language model.

The finding is narrower than it sounds. The decomposition step relies on a small helper model trained on a synthetic dataset the authors built themselves, which makes the result harder to reproduce outside their setup. The headline number should be read as evidence of a direction, not a portable recipe.

For anyone buying or building these systems, the practical takeaway is unflashy: the cheapest accuracy wins now sit upstream of the search step, not in fancier embedding models. Worth a question to your team about how queries are rewritten before they hit retrieval, and worth ignoring the next vendor pitch built around a new embedding leaderboard.

Worth reading if you ship or evaluate RAG systems. Worth ignoring if you were hoping for a free lunch.

Paper: Query Decomposition for Robust RAG, Müller et al.
https://arxiv.org/abs/2026.xxxxx

#LLMs #Retrieval #Enterprise #VendorRisk #QueryDecomposition
```

## Grounding requirement

Every factual claim in your post_text must appear in the `claims` list,
with a verbatim `source_span` from the supplied paper sections. If a
claim cannot be grounded in the supplied text, do not make it.

Factual claims include: any number, any benchmark name, any attribution,
any methodological description, any comparative claim. Subjective framing
("worth reading if you ship RAG systems", "narrower than it sounds") is
clearly editorial and does not need grounding.

## Output

Return JSON with exactly these fields:

- `post_text` (string): the full draft, ready to paste into LinkedIn
- `claims` (array): one object per factual claim in the post
  - `claim` (string): the claim as it appears in the post
  - `source_span` (string): the SHORTEST verbatim fragment from the supplied paper sections that supports the claim — typically 5 to 25 words. Do not quote whole sentences; pick the specific phrase, number, or attribution. Long quotes often fail because PDF extraction inserts stray characters mid-sentence, so short, specific spans are more reliable.
  - `page` (integer >= 1): which page of the paper the span is from; use 1 if unsure

## Paper

Title: {title}

Authors: {authors}

arXiv ID: {arxiv_id}
arXiv URL: {arxiv_url}

Abstract:
{abstract}

Introduction:
{intro}

Method:
{method}

Results:
{results}

Limitations:
{limitations}

Conclusions:
{conclusions}

{retry_section}
