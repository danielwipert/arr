# Grounding trace for arxiv:2606.26036v1

Paper: Detect, Unlearn, Restore: Defending Text Summarization Models Against Data Poisoning
URL: https://arxiv.org/abs/2606.26036
Composite: 8.30
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Researchers from the University of Texas at Arlington developed a two-part framework for models fine-tuned on potentially corrupted data.

**Source span:** 'The University of Texas at Arlington'

**Page:** 1

### Claim 2

**Claim:** In white-box settings, their method identifies poisoned training samples and removes their influence, recovering up to 96% of original model behavior

**Source span:** 'gradient-ascent unlearning recovers up to 96% of original behavior'

**Page:** 1

### Claim 3

**Claim:** with less than 0.6% degradation in standard ROUGE scores.

**Source span:** 'with minimal utility loss (<0.6% ROUGE degradation)'

**Page:** 1

### Claim 4

**Claim:** The second part works as a black-box audit, detecting poisoned models by their heightened sensitivity to small input changes, achieving near-perfect detection.

**Source span:** 'In black-box settings, poisoned models display two-to-three times greater sensitivity to semantics-preserving perturbations, enabling behavioral auditing'

**Page:** 1

### Claim 5

**Claim:** The first part needs the model's internal data and parameters, limiting it to open-source or self-hosted systems.

**Source span:** 'Defense-1 requires access to model parameters and fine-tuning data, which aligns with open-source or self-hosted pipelines but may not apply to closed API-only systems'

**Page:** 13
