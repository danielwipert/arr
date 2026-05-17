# Filter stage prompt

You classify a recent arXiv paper against an editorial scope. The editorial
position is:

> Papers worth reading if you build with LLMs.

The reader ships systems on top of large language models. They want research
that changes what they should build, how they should build it, or what they
should stop doing.

## In-scope topics

- `llm_capabilities` — reasoning, planning, long context, tool use, multi-step agents
- `rag` — query rewriting, retrieval quality, reranking, RAG evaluation
- `applied_llm_systems` — latency, cost, structured output, prompt engineering as discipline, failure modes
- `evaluation` — new benchmarks, criticism of existing benchmarks, methodology for evaluating LLM systems
- `post_training` — fine-tuning, DPO and successors, distillation, LoRA-family methods
- `adjacent_infrastructure` — vector databases, serving and inference, caching strategies, model routing

## Out of scope (return `primary_topic: "other"`)

- Pure theory, pure mechanistic interpretability
- Computer vision papers with no multimodal-LLM connection
- Pretraining work that requires mega-lab compute
- Surveys, position papers, opinion pieces, workshop short papers (also flag as `is_review_or_survey: true`)

## Output

Return JSON with exactly these fields:

- `in_scope` (bool) — true if the paper's primary contribution falls into one of the in-scope topics
- `primary_topic` (string) — one of the in-scope topic strings above, or `"other"` if out of scope
- `is_review_or_survey` (bool) — true if the abstract describes a review, survey, position piece, opinion, or workshop extended abstract rather than a methodological contribution
- `note` (string) — one short sentence explaining the decision; mention any signal that pushed toward `other` or `is_review_or_survey`

## Paper

Title: {title}

Abstract:
{abstract}
