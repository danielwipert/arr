# Grounding trace for arxiv:2605.18693v1

Paper: SkillGenBench: Benchmarking Skill Generation Pipelines for LLM Agents
URL: https://arxiv.org/abs/2605.18693
Composite: 7.95
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Researchers from multiple institutions introduced SkillGenBench

**Source span:** 'Authors: Yifan Zhou, Zhentao Zhang, Ziming Cheng, Shuo Zhang, Qizhen Lan, Zhangquan Chen, Zhi Yang, QianyuXu, Ronghao Chen, Huacan Wang, Sen Hu'

**Page:** 1

### Claim 2

**Claim:** evaluates how well language models can distill deployable skills from raw materials

**Source span:** 'SkillGenBench evaluates how well LLMs can distill deployable, reusable skills from complex source materials'

**Page:** 3

### Claim 3

**Claim:** tests both task-conditioned generation (where the model knows the target task) and task-agnostic generation (where it must build a reusable library before tasks are revealed)

**Source span:** 'task-conditioned generation, where a task-specific skill is synthesized after the task is revealed, and task-agnostic generation, where a reusable skill library must be distilled before downstream tasks are known'

**Page:** 1

### Claim 4

**Claim:** 187 tasks spanning code repositories and documentation

**Source span:** '187-task benchmark composition across source types'

**Page:** 4

### Claim 5

**Claim:** performance varied substantially by method and backbone model

**Source span:** 'Experiments across a range of skill-generation methods and backbones show substantial performance variation'

**Page:** 1

### Claim 6

**Claim:** gap is most pronounced with code repositories, where procedures are implicit in directory structures and configuration files rather than explicitly stated

**Source span:** 'repository-grounded instances remain significantly more challenging than document-based ones, highlighting the difficulty of recovering implicit execution structure from distributed code artifacts'

**Page:** 6

### Claim 7

**Claim:** Even when models capture the right structural components, they often fail to translate them into executable procedures that pass strict verification

**Source span:** 'Generated skills often capture the right structural components, yet fail to translate them into executable procedures that satisfy strict verification constraints'

**Page:** 6

### Claim 8

**Claim:** this as a pipeline-level problem rather than just a model capability issue

**Source span:** 'skill generation is fundamentally a pipeline-level problem: performance depends not only on the generation method, but also on the backbone model'

**Page:** 6
