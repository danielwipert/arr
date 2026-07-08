# Grounding trace for arxiv:2607.06519v1

Paper: FreqDepthKV: Frequency-Guided Depth Sharing for Robust KV Cache Compression in Long-Context LLM Inference
URL: https://arxiv.org/abs/2607.06519
Composite: 8.30
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** FreqDepthKV compresses the key-value cache—a major memory bottleneck in long-context LLM inference

**Source span:** 'Long-context inference has shifted the bottleneck of large language models from parameter storage to the key-value (KV) cache.'

**Page:** 1

### Claim 2

**Claim:** by sharing low-frequency components across adjacent transformer layers while preserving sparse, high-frequency residuals

**Source span:** 'decomposes the KV cache across adjacent layers into low-frequency depth components that are broadly shared and sparse high-frequency residuals'

**Page:** 2

### Claim 3

**Claim:** On a 32k-token prefill, it achieves a 3.9x compression ratio, reducing peak KV memory to 6.2 GB

**Source span:** 'lowers peak KV memory to 6.2 GB, achieving a 3.9x effective compression ratio'

**Page:** 1

### Claim 4

**Claim:** closely matching full-cache accuracy on question answering, summarization, and code generation benchmarks

**Source span:** 'closely matching full KV while outperforming prior compressed-cache methods'

**Page:** 1

### Claim 5

**Claim:** a lightweight online probe that routes each attention head into one of three modes—shared, residual, or exact

**Source span:** 'uses a lightweight online probe to assign each attention head to one of three cache modes: shared-depth, residual-depth, or exact'

**Page:** 2

### Claim 6

**Claim:** based on how compression would perturb cached attention logits

**Source span:** 'allowing the compression policy to adapt to prompt structure without retraining'

**Page:** 1

### Claim 7

**Claim:** This routing is decided once during prefill and fixed for the entire decoding run

**Source span:** 'The budgeted routing is performed once after prefill and reused throughout autoregressive decoding'

**Page:** 4
