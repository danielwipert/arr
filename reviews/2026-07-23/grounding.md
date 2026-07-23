# Grounding trace for arxiv:2607.20219v1

Paper: HalluTruthQA: A Fine-Grained Benchmark for Hallucination Detection, Localization, and Explanation in Arabic Question Answering
URL: https://arxiv.org/abs/2607.20219
Composite: 8.05
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Researchers from Qatar Computing Research Institute and partner universities built HalluTruthQA, a dataset of 2,400 expert-curated Arabic questions across Islamic knowledge, history, science, and geography.

**Source span:** 'HalluTruthQA contains 2,400 Arabic QA examples across four knowledge-intensive domains: Islamic knowledge, history, science, and geography'

**Page:** 1

### Claim 2

**Claim:** They evaluated four open-source LLMs on four tasks: detecting hallucinations, localizing the exact erroneous text, explaining the error, and selecting the correct answer from a list.

**Source span:** 'We evaluate four open-source LLMs, Allam, Falcon-H1, Qwen32, and Silma, in a zero-shot setting across hallucination detection, span-level localization, factual verification, and explanation evaluation.'

**Page:** 1

### Claim 3

**Claim:** No single model was best at all tasks; the top detection score was 0.880 Macro-F1, while the best span-localization score was just 0.516 F1-Sp.

**Source span:** 'no single model achieves the strongest performance across all tasks, with best scores of 0.880 Macro-F1 for detection, 0.516 F1-Sp for localization'

**Page:** 1

### Claim 4

**Claim:** In domains like history and geography, 59.3% of hallucinations were simple factual contradictions.

**Source span:** 'Across all hallucinated spans, Factual Contradiction is the dominant category (59.3%)'

**Page:** 1

### Claim 5

**Claim:** But in Islamic knowledge, 61.6% were context inconsistencies, where a correct short answer was supported by a fabricated or misattributed religious source.

**Source span:** 'Islamic Knowledge differs: Context Inconsistency accounts for 61.6%, reflecting the need for faithful grounding in the appropriate verse, hadith, legal ruling, or source context.'

**Page:** 1
