# Grounding trace for arxiv:2606.05158v1

Paper: Streaming Communication in Multi-Agent Reasoning
URL: https://arxiv.org/abs/2606.05158
Composite: 8.30
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Researchers from Zhejiang University and HKUST built STREAMMA

**Source span:** 'Zhen Yang, Xiaogang Xu, Wen Wang, Cong Chen, Xander Xu, Ying-Cong Chen'

**Page:** 1

### Claim 2

**Claim:** a system that forwards each reasoning step between LLM agents as soon as it is generated rather than waiting for complete responses

**Source span:** 'streams each reasoning step to downstream agents as soon as it is generated'

**Page:** 1

### Claim 3

**Claim:** Across eight reasoning benchmarks using Claude Opus and GPT-5.4

**Source span:** 'Across eight reasoning benchmarks spanning mathematics, science, and code, two frontier LLMs (Claude Opus 4.6 and GPT-5.4)'

**Page:** 1

### Claim 4

**Claim:** this streaming protocol outperformed traditional serial execution by an average of 7.3 percentage points

**Source span:** 'STREAMMA outperforms both baselines (avg. +7.3pp'

**Page:** 1

### Claim 5

**Claim:** reducing latency through pipeline parallelism

**Source span:** 'pipelining adjacent agents and thus reducing latency'

**Page:** 1

### Claim 6

**Claim:** early steps tend to be reliable while later ones degrade

**Source span:** 'early steps are more reliable than later ones'

**Page:** 1

### Claim 7

**Claim:** Streaming lets downstream agents begin work with these reliable prefixes

**Source span:** 'working with these reliable early steps instead of the full chain'

**Page:** 1

### Claim 8

**Claim:** The serial protocol forces agents to consume entire responses

**Source span:** 'an upstream agent must finish its entire response before passing it downstream'

**Page:** 2
