# Grounding trace for arxiv:2606.14629v1

Paper: When Good Verifiers Go Bad: Self-Improving VLMs Can Regress on New Tasks
URL: https://arxiv.org/abs/2606.14629
Composite: 8.20
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Jianzhe Lin tested verifier-driven self-improvement

**Source span:** 'Verifier-driven self-DPO is a common recipe for self-improving production visual-language models.'

**Page:** 1

### Claim 2

**Claim:** On the MMMU reasoning benchmark, every verifier tested caused the student model to regress by 3.4 to 10.9 percentage points below its original performance.

**Source span:** 'every verifier we tested silently regresses the student, producing drops of 3.4 to 10.9 percentage points below the frozen baseline'

**Page:** 1

### Claim 3

**Claim:** The training loss decreased normally, offering no warning.

**Source span:** 'The regression is reproducible across two students. There is no warning sign in the DPO training loss, which descends cleanly throughout.'

**Page:** 1

### Claim 4

**Claim:** It occurs when the verifier's accuracy on the target task is low (8% to 23% in these tests).

**Source span:** 'where their task-rubric accuracy drops to 8% to 23%'

**Page:** 1

### Claim 5

**Claim:** a more confident but wrong verifier causes greater regression than a near-random one

**Source span:** 'damage is confidence-inverted: the more accurate-but-still-wrong verifier causes larger regression than a near-random verifier'

**Page:** 1

### Claim 6

**Claim:** a cheap calibration that takes about five GPU-hours.

**Source span:** 'computationally cheap (∼5 GPU-hr per candidate)'

**Page:** 5
