A new paper shows that the most expensive part of fine-tuning language models for reasoning—running reinforcement learning for days—can be predicted from the first 15% of training.

The team analyzed the weight updates during RL with verifiable rewards (RLVR), a standard method for improving math and code generation. They found the parameter changes are extremely low-rank, with a single dominant direction per tensor capturing nearly all performance gains. The magnitude of this projection evolves near-linearly with training steps.

Their method, RELEX, estimates this rank-1 subspace from an early observation window and extrapolates future checkpoints via linear regression. On three models, it matches or exceeds full RLVR performance on math benchmarks using only 15-20% of the training steps. The approach works because the rank-1 projection acts as a spectral denoiser, preserving task-relevant signals while discarding stochastic optimization noise.

For engineering teams, this suggests that expensive RL training runs could be shortened significantly through careful monitoring of early weight dynamics. The practical ceiling for reasoning performance might be predictable much sooner than previously thought.

Worth reading if you manage large-scale fine-tuning budgets. Worth ignoring if your models don't use RL-based refinement.

Paper: You Only Need Minimal RLVR Training: Extrapolating LLMs via Rank-1 Trajectories, Wei et al.
https://arxiv.org/abs/2605.21468

#MachineLearning #FineTuning #ReinforcementLearning #ModelOptimization #RELEX