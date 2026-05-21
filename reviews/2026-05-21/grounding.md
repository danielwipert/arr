# Grounding trace for arxiv:2605.21468v1

Paper: You Only Need Minimal RLVR Training: Extrapolating LLMs via Rank-1 Trajectories
URL: https://arxiv.org/abs/2605.21468
Composite: 8.05
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** A new paper shows that the most expensive part of fine-tuning language models for reasoning—running reinforcement learning for days—can be predicted from the first 15% of training.

**Source span:** 'requiring as few as 15% steps of full RLVR training'

**Page:** 1

### Claim 2

**Claim:** The team analyzed the weight updates during RL with verifiable rewards (RLVR), a standard method for improving math and code generation.

**Source span:** 'Reinforcement learning with verifiable rewards (RLVR) has become a dominant paradigm for improving reasoning in large language models'

**Page:** 1

### Claim 3

**Claim:** They found the parameter changes are extremely low-rank, with a single dominant direction per tensor capturing nearly all performance gains.

**Source span:** 'RLVR weight trajectories are extremely low-rank'

**Page:** 1

### Claim 4

**Claim:** The magnitude of this projection evolves near-linearly with training steps.

**Source span:** 'the magnitude of this projection evolves near-linearly with training steps'

**Page:** 1

### Claim 5

**Claim:** Their method, RELEX, estimates this rank-1 subspace from an early observation window and extrapolates future checkpoints via linear regression.

**Source span:** 'RELEX (REinforcement Learning EXtrapolation), which estimates the rank-1 subspace from a short observation window and extrapolates future checkpoints via linear regression'

**Page:** 1

### Claim 6

**Claim:** On three models, it matches or exceeds full RLVR performance on math benchmarks using only 15-20% of the training steps.

**Source span:** 'RELEX produces checkpoints that match or exceed RLVR performance on both in-domain and out-of-domain benchmarks, requiring as few as 15% steps of full RLVR training'

**Page:** 1

### Claim 7

**Claim:** The approach works because the rank-1 projection acts as a spectral denoiser, preserving task-relevant signals while discarding stochastic optimization noise.

**Source span:** 'RELEX\'s success stems from a "denoising" effect: by projecting updates onto the rank-1 subspace, the model discards stochastic optimization noise'

**Page:** 1
