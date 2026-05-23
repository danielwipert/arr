# Grounding trace for arxiv:2605.22791v1

Paper: Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention
URL: https://arxiv.org/abs/2605.22791
Composite: 8.05
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Gated DeltaNet-2, a new linear attention layer, achieves the strongest overall results among recent recurrent models

**Source span:** 'Gated DeltaNet-2 achieves the strongest overall results among Mamba-2, Gated DeltaNet, KDA, and Mamba-3 variants across language modeling, commonsense reasoning, and retrieval.'

**Page:** 1

### Claim 2

**Claim:** Researchers from NVIDIA introduced the model

**Source span:** 'Ali Hatamizadeh, Yejin Choi, Jan Kautz'

**Page:** 1

### Claim 3

**Claim:** a single scalar gate traditionally controls both how much old information to erase and how much new information to write

**Source span:** 'the active edit still uses a single scalar gate to control two different things: how much old content to erase on the key side and how much new content to commit on the value side.'

**Page:** 1

### Claim 4

**Claim:** Gated DeltaNet-2 separates these functions with a channel-wise erase gate and a separate channel-wise write gate

**Source span:** 'Gated Delta Rule-2 separates these roles with a channel-wise erase gate b_t and a channel-wise write gate w_t'

**Page:** 1

### Claim 5

**Claim:** At 1.3B parameters trained on 100 billion tokens

**Source span:** 'At 1.3B parameters trained on 100B FineWeb-Edu tokens'

**Page:** 1

### Claim 6

**Claim:** outperforms Mamba-2, Gated DeltaNet, KDA, and Mamba-3 variants on language modeling and reasoning benchmarks

**Source span:** 'Gated DeltaNet-2 achieves the strongest overall results among Mamba-2, Gated DeltaNet, KDA, and Mamba-3 variants across language modeling, commonsense reasoning, and retrieval.'

**Page:** 1

### Claim 7

**Claim:** The advantage is most pronounced on long-context retrieval

**Source span:** 'Its advantage is most pronounced on long-context RULER needle-in-a-haystack benchmarks'

**Page:** 1

### Claim 8

**Claim:** On the RULER needle-in-a-haystack benchmark, Gated DeltaNet-2 achieves 27.4% accuracy in the multi-key retrieval setting at a context length of 8K tokens

**Source span:** 'GatedDeltaNet-2 100.0 100.0 55.2 27.4 100.0'

**Page:** 6

### Claim 9

**Claim:** The model preserves efficient training, adding only a small constant overhead relative to its predecessors

**Source span:** 'GatedDeltaNet-2 retains practical training efficiency while paying a modest constant cost for finer memory control.'

**Page:** 8
