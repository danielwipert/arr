# Grounding trace for arxiv:2606.12402v1

Paper: DIRECT: When and Where Should You Allocate Test-Time Compute in Embodied Planners?
URL: https://arxiv.org/abs/2606.12402
Composite: 8.60
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** A new routing framework called DIRECT shows that smarter allocation of test-time compute can match top-tier embodied AI performance at up to 65% lower latency.

**Source span:** "our router matches or exceeds a stronger model's success rate at up to 65% lower average latency"

**Page:** 1

### Claim 2

**Claim:** Researchers from Stanford and NVIDIA introduced DIRECT

**Source span:** 'Stanford University, 3NVIDIA'

**Page:** 1

### Claim 3

**Claim:** a system that dynamically routes robotic planning tasks to different vision-language models based on scene complexity

**Source span:** 'DIRECT, a routing framework that uses multimodal scene context to allocate compute per prompt'

**Page:** 1

### Claim 4

**Claim:** The framework selects the most appropriate planner from a pool of candidates

**Source span:** 'directing each task to the planner whose capability profile matches inferred demands'

**Page:** 1

### Claim 5

**Claim:** choosing between models with varying reasoning depth, size, and memory capabilities

**Source span:** 'Across three dominant scaling axes, namely chain-of-thought depth, model size, and memory history'

**Page:** 1

### Claim 6

**Claim:** different compute axes provide distinct benefits—chain-of-thought reasoning helps with implicit constraints, model size broadens skill command, and memory aids history-dependent tasks

**Source span:** 'CoT depth helps on tasks with implicit semantic, physical, or spatial constraints; VLM size governs breadth of skills a planner can command; and memory-oriented compute helps on history-dependent tasks'

**Page:** 1

### Claim 7

**Claim:** uniformly scaling compute across all tasks wastes resources on simple problems while risking failure on complex ones

**Source span:** 'naively scaling test-time compute is wasteful'

**Page:** 1
