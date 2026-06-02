# Grounding trace for arxiv:2606.02559v1

Paper: From Layers to Submodules: Rethinking Granularity in Replacement-Based LLM Compression
URL: https://arxiv.org/abs/2606.02559
Composite: 8.30
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** The method, called SUBFIT, was developed by researchers at the University of Trento.

**Source span:** 'Elia Cunegatti, Marcus Vukojevic, Erik Nielsen, Giovanni Iacca University of Trento'

**Page:** 1

### Claim 2

**Claim:** It removes individual attention and feed-forward submodules from a pretrained model and fits a lightweight, custom bypass for each one, using only calibration data.

**Source span:** 'SUBFIT compresses pretrained decoder-only Transformer architectures through a two-stage select-and-replace procedure.'

**Page:** 3

### Claim 3

**Claim:** At 25% sparsity, the method retains 84.6% of the dense model's downstream accuracy, against 81.6% for the strongest baseline.

**Source span:** 'At 25% sparsity, it retains 84.6% of dense downstream accuracy and incurs 2.42× perplexity degradation, against 81.6% and 4.34× for the strongest baselines'

**Page:** 1

### Claim 4

**Claim:** The technique adds explicit compensation parameters for each removed submodule, which increases the deployed model's size by roughly 10% of the removed parameters.

**Source span:** 'Added parameters remain around 10% of the removed parameters'

**Page:** 9
