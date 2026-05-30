# Grounding trace for arxiv:2605.30343v1

Paper: Unlocking the Working Memory of Large Language Models for Latent Reasoning
URL: https://arxiv.org/abs/2605.30343
Composite: 7.70
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Researchers from Johannes Kepler University propose Reasoning in Memory (RiM)

**Source span:** 'Authors: Lukas Aichberger, Sepp Hochreiter'

**Page:** 1

### Claim 2

**Claim:** replaces the step-by-step generation of reasoning tokens with fixed sequences of special tokens called memory blocks

**Source span:** 'introduce Reasoning in Memory (RiM), a latent reasoning method that replaces the autoregressive generation of reasoning steps with memory blocks'

**Page:** 1

### Claim 3

**Claim:** Because these blocks are fixed inputs, the entire reasoning process can be computed in a single forward pass.

**Source span:** 'Since they are fixed rather than generated, they can be processed in a single forward pass'

**Page:** 1

### Claim 4

**Claim:** On the GSM8K math benchmark, a Llama-3.2-1B model trained with RiM achieved 43.1% accuracy

**Source span:** 'Llama-3.2-1B 42.6∗ 50.6∗ 43.1'

**Page:** 7

### Claim 5

**Claim:** matching or exceeding existing latent reasoning methods.

**Source span:** 'RiM matches or exceeds existing latent reasoning methods'

**Page:** 1

### Claim 6

**Claim:** The method requires a complex two-stage curriculum to teach models to use the memory blocks effectively

**Source span:** 'To operationalize these memory blocks, we employ a two-stage curriculum.'

**Page:** 1

### Claim 7

**Claim:** its gains are demonstrated primarily on mathematical reasoning tasks.

**Source span:** 'evaluating them on GSM8K and GSM-Hard as in- and out-of-distribution benchmarks, respectively.'

**Page:** 2

### Claim 8

**Claim:** cutting inference latency by 98% compared to chain-of-thought.

**Source span:** 'SFT w/ CoT 36.7 1108.7±3.0 +982.7\nRiM(ours) 3.1 126.5±0.5 +0.5'

**Page:** 21
