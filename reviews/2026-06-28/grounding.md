# Grounding trace for arxiv:2606.27359v1

Paper: When are likely answers right? On Sequence Probability and Correctness in LLMs
URL: https://arxiv.org/abs/2606.27359
Composite: 7.45
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Researchers at the University of Maryland analyzed the relationship between sequence probability and correctness across 8 decoding methods, 14 models, and 6 benchmark datasets.

**Source span:** 'We study the relationship between sequence probability and correctness across 12 models, 6 datasets, and 8 decoding methods.'

**Page:** 1

### Claim 2

**Claim:** They found that while higher-probability responses often correlate with correctness across different prompts within a fixed dataset, this signal does not transfer to decoding decisions: methods that produce higher-probability sequences do not consistently yield more accurate answers.

**Source span:** 'higher sequence probability is often predictive of correctness across prompt-answer pairs within a fixed dataset. However, this relationship does not generally transfer to decoding decisions: increasing sequence probability by changing hyperparameters or methods does not reliably improve accuracy.'

**Page:** 1

### Claim 3

**Claim:** The correlation is strongest on mathematical reasoning tasks like MATH500, where models show near-perfect alignment between probability and correctness.

**Source span:** 'Correlation is strongest for MATH500'

**Page:** 2

### Claim 4

**Claim:** On instruction-following benchmarks like IFEval, however, the correlation is often negative, with base models particularly struggling to distinguish likely completions from correct ones.

**Source span:** 'Only IFEval shows a negative correlation. Base models show more negative and diverse correlation and are consistently negative for IFEval.'

**Page:** 3

### Claim 5

**Claim:** Methods that increase sequence probability—like power sampling or best-of-N—do not guarantee better accuracy across tasks.

**Source span:** 'increasing sequence probability by changing hyperparameters or methods does not reliably improve accuracy.'

**Page:** 1
