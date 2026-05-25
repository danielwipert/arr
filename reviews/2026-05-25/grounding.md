# Grounding trace for arxiv:2605.23904v1

Paper: SkillOpt: Executive Strategy for Self-Evolving Agent Skills
URL: https://arxiv.org/abs/2605.23904
Composite: 8.30
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Researchers at Microsoft and Tsinghua University developed SkillOpt

**Source span:** 'Authors: Yifan Yang, Ziyang Gong, Weiquan Huang, Qihao Yang, Ziwei Zhou, Zisu Huang, Yan Li, Xuemei Gao, Qi Dai, Bei Liu, Kai Qiu, Yuqing Yang, Dongdong Chen, Xue Yang, Chong Luo'

**Page:** 1

### Claim 2

**Claim:** a text-space optimizer that treats a skill document as external state for a frozen language model

**Source span:** 'SkillOpt is, to our knowledge, the first systematic controllable text-space optimizer for agent skills'

**Page:** 1

### Claim 3

**Claim:** It uses a frontier model to propose bounded add/delete/replace edits based on rollout evidence

**Source span:** 'a separate optimizer model turns scored rollouts into bounded add/delete/replace edits on a single skill document'

**Page:** 1

### Claim 4

**Claim:** accepting only those that improve a held-out validation score

**Source span:** 'an edit is accepted only when it strictly improves a held-out validation score'

**Page:** 1

### Claim 5

**Claim:** On GPT-5.5, it lifts the average no-skill accuracy by +23.5 points in direct chat

**Source span:** 'On GPT-5.5 it lifts the average no-skill accuracy by +23.5 points in direct chat'

**Page:** 1

### Claim 6

**Claim:** with gains of +24.8 and +19.1 points inside Codex and Claude Code execution harnesses

**Source span:** 'by +24.8 inside the Codex agentic loop, and by +19.1 inside Claude Code'

**Page:** 1

### Claim 7

**Claim:** The optimizer runs only during training, adding zero inference-time cost to the deployed agent

**Source span:** 'adding zero inference-time model calls at deployment'

**Page:** 1

### Claim 8

**Claim:** The final skill document remains compact at 300-2,000 tokens

**Source span:** 'the deployed output is a compact best_skill.md file of roughly 300–2,000 tokens'

**Page:** 2

### Claim 9

**Claim:** assembled from just 1-4 accepted edits that pass strict validation

**Source span:** 'the number of edits actually committed to best_skill.md during optimization is between 1 and 4'

**Page:** 14

### Claim 10

**Claim:** Across six benchmarks and seven target models, SkillOpt is best or tied-best on all 52 evaluated configurations

**Source span:** 'SkillOpt is best or tied on all 52 evaluated (model, benchmark, harness) cells'

**Page:** 1
