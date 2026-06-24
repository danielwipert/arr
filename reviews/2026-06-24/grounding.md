# Grounding trace for arxiv:2606.24820v1

Paper: SHERLOC: Structured Diagnostic Localization for Code Repair Agents
URL: https://arxiv.org/abs/2606.24820
Composite: 8.20
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 0

## Claims

### Claim 1

**Claim:** Researchers from NVIDIA and TU Darmstadt built SHERLOC, a framework that uses a language model and a small set of tools to diagnose the root cause of software bugs.

**Source span:** 'We introduce SHERLOC (Structured Hypothesis-driven Exploration and Reasoning for Localization), a training-free framework pairing a reasoning LLM with compact repository tools and self-recovery'

**Page:** 1

### Claim 2

**Claim:** On the SWE-Bench Verified benchmark, it correctly identified the faulty file 81.27% of the time

**Source span:** '81.27% recall@1 on SWE-Bench Verified'

**Page:** 1

### Claim 3

**Claim:** while using 36.7% fewer tokens for the search phase than standard agents.

**Source span:** 'cutting localization and total tokens by 36.7% and 23.1%'

**Page:** 1

### Claim 4

**Claim:** The headline performance partly reflects the model's prior familiarity with popular open-source codebases like scikit-learn.

**Source span:** 'implicit recall concentrates in popular projects (85.3% on scikit-learn'

**Page:** 6

### Claim 5

**Claim:** When explicit file paths were hidden, its accuracy dropped by about 22 percentage points

**Source span:** 'The ≈22 pp gap between this masked-issue setting and the heavily-masked text-only setting'

**Page:** 6
