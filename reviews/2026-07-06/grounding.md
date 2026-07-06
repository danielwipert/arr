# Grounding trace for arxiv:2607.02509v1

Paper: ReContext: Recursive Evidence Replay as LLM Harness for Long-Context Reasoning
URL: https://arxiv.org/abs/2607.02509
Composite: 8.05
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** A new method called ReContext improves long-context reasoning in language models by replaying key evidence before generating an answer, without any training or context pruning.

**Source span:** 'RECONTEXT, a training-free inference method for improving long-context reasoning'

**Page:** 1

### Claim 2

**Claim:** Researchers from UIUC and Virginia Tech introduced ReContext

**Source span:** 'University of Illinois Urbana-Champaign, Virginia Tech'

**Page:** 1

### Claim 3

**Claim:** It uses the model's own attention signals to identify and replay the most relevant text spans from a long document before the final answer generation

**Source span:** 'RECONTEXT uses model-internal relevance signals to construct a query-conditioned evidence pool and replays it before final generation'

**Page:** 1

### Claim 4

**Claim:** while keeping the full context available

**Source span:** 'while preserving the full original context'

**Page:** 1

### Claim 5

**Claim:** On eight long-context benchmarks with 128K token inputs

**Source span:** 'Experiments on eight long-context datasets with 128K context length'

**Page:** 1

### Claim 6

**Claim:** ReContext improved average accuracy from 0.24 to 0.30, a 24.6% relative gain

**Source span:** 'improves mean accuracy over Vanilla from 0.24 to 0.30, a 24.6% relative gain'

**Page:** 1

### Claim 7

**Claim:** across Qwen3 and Llama3 models

**Source span:** 'across Qwen3-4B, Qwen3-8B, and Llama3-8B'

**Page:** 1

### Claim 8

**Claim:** The method doesn't require modifying the model's parameters or fine-tuning

**Source span:** 'training-free'

**Page:** 1

### Claim 9

**Claim:** It achieves this by recursively building an evidence pool over a few rounds

**Source span:** 'recursive selection process'

**Page:** 1

### Claim 10

**Claim:** where each round's selection is conditioned on the evidence gathered in previous rounds

**Source span:** 'each evidence proposal depends on the evidence pool produced by previous rounds'

**Page:** 1
