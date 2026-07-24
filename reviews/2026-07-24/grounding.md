# Grounding trace for arxiv:2607.21535v1

Paper: Windowed-MTP: Removing the Full-Context Draft-KV Tax at Million-Token Context
URL: https://arxiv.org/abs/2607.21535
Composite: 8.20
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Speculative decoding accelerates text generation by having a cheap draft model propose tokens that a more powerful target model verifies in parallel.

**Source span:** 'Speculative decoding (SD) [Leviathan et al., 2023, Chen et al., 2023a] is a standard tool for reducing the per-token latency of autoregressive LLMs: a draft proposes γ candidate tokens and the target verifies them in one batched forward, accepting the longest correct prefix.'

**Page:** 2

### Claim 2

**Claim:** Recent models like Qwen and DeepSeek ship with a built-in Multi-Token-Prediction (MTP) draft head

**Source span:** 'Frontier models such as DeepSeek-V3 [DeepSeek-AI, 2024] and Qwen3 [Qwen Team, 2025] ship a built-in MTP / NEXTN head'

**Page:** 3

### Claim 3

**Claim:** which typically runs full attention over the entire context at every draft step

**Source span:** 'Typically, an MTP draft head runs full attention over the entire KV cache at every draft step'

**Page:** 1

### Claim 4

**Claim:** At 1M tokens, this draft phase adds 92–138% to the cost of the verify step alone, nearly doubling the decode step

**Source span:** 'natively this draft phase (with the fixed speculative bookkeeping) adds +92% to +138% on top of the bare full-attention verify, nearly doubling the decode step'

**Page:** 5

### Claim 5

**Claim:** The draft's KV working set is bounded to a constant 4K tokens plus a 64-token attention sink, dropping ~99% of KV entries from the draft's read path

**Source span:** "It bounds the draft's KV working set to a constant, dropping ∼99% of KV entries from the draft's read path at 1M"

**Page:** 1

### Claim 6

**Claim:** Windowed-MTP cuts the per-decode-step cost over the shipping native MTP draft by +28% to +44%

**Source span:** 'windowing the MTP draft cuts the per-decode-step cost (one speculative iteration: γ draft forwards plus verify) over the shipping native MTP draft by +28% to +44%'

**Page:** 1
