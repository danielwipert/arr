# Grounding trace for arxiv:2606.27288v1

Paper: When Does Combining Language Models Help? A Co-Failure Ceiling on Routing, Voting, and Mixture-of-Agents Across 67 Frontier Models
URL: https://arxiv.org/abs/2606.27288
Composite: 8.20
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** A team led by Josef Chen analyzed 67 frontier models, including GPT-5.5 and Claude Opus 4.8

**Source span:** 'Across 67 frontier models from 21 providers, among them GPT-5.5, Claude Opus 4.8, Gemini 3.1 Pro, Grok-4.3, DeepSeek V4, Qwen3.7-Max, and Kimi K2.7'

**Page:** 1

### Claim 2

**Claim:** no router, vote, or cascade can exceed an accuracy of 1 minus β, where β is the rate at which every model fails on the same query

**Source span:** 'no router, vote, or cascade can exceed accuracy 1−β, where β is the rate at which every model is wrong on the same query'

**Page:** 1

### Claim 3

**Claim:** They prove that pairwise correlation ρ cannot identify β

**Source span:** 'pairwise ρ cannot identify β'

**Page:** 1

### Claim 4

**Claim:** a Clopper-Pearson bound turns one graded query set into a certificate on the largest gain any such policy could deliver

**Source span:** 'A Clopper–Pearson bound on β turns one graded, held-out query set into a $0 certificate on the largest gain any such policy could deliver'

**Page:** 1

### Claim 5

**Claim:** The ceiling binds only on open-ended tasks like math and code, where a co-failure tail exists

**Source span:** 'co-failure (β > 0) ... holds across three structurally disjoint open-ended domains (two math families and execution-graded code)'

**Page:** 9

### Claim 6

**Claim:** on multiple-choice science questions, the ceiling is effectively open

**Source span:** 'on multiple-choice GPQA the tail vanishes (β ≈ 0)'

**Page:** 7

### Claim 7

**Claim:** The same GPQA-Diamond questions asked in free-response form opened a co-failure tail (β=0.127) where multiple-choice had none

**Source span:** 'Changing only the format opens a co-failure block of 10/79 (β=0.127, CP[0.062,0.220]) where multiple-choice had none (β ≈ 0)'

**Page:** 10
