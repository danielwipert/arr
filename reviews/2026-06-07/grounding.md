# Grounding trace for arxiv:2606.06474v1

Paper: Self-Augmenting Retrieval for Diffusion Language Models
URL: https://arxiv.org/abs/2606.06474
Composite: 8.10
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** A training-free retrieval method for diffusion language models improves multi-hop reasoning accuracy by 13 points while running up to 8 times faster than autoregressive baselines

**Source span:** 'SARDI outperforms current training-free diffusion and autoregressive retrieval baselines at up to 8× higher throughput'

**Page:** 1

### Claim 2

**Claim:** Cornell researchers developed SARDI

**Source span:** '1Department of Computer Science, Cornell University'

**Page:** 1

### Claim 3

**Claim:** achieves 59% exact match accuracy on 2WikiMultiHopQA, up from 44% with static retrieval

**Source span:** 'DLM W/ RET@STATIC achieves 43.7% and DLM W/ SARDI achieves 59.1% on 2WikiMultiHopQA'

**Page:** 5

### Claim 4

**Claim:** diffusion models surface bridge entities much earlier in the generation process than autoregressive models can

**Source span:** 'intermediate diffusion states surface such entities early, enabling retrieval of later-hop evidence before the output is finalized'

**Page:** 2

### Claim 5

**Claim:** particularly benefiting complex questions requiring inference and composition

**Source span:** 'SARDI yields over 2.5× EM gains on inference and compositional questions'

**Page:** 7

### Claim 6

**Claim:** The method requires no additional training

**Source span:** 'SARDI is training-free'

**Page:** 2

### Claim 7

**Claim:** works with any retriever

**Source span:** 'SARDI is retriever-agnostic'

**Page:** 2
