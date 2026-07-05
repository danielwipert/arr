# Grounding trace for arxiv:2607.02513v1

Paper: LACUNA: A Testbed for Evaluating Localization Precision for LLM Unlearning
URL: https://arxiv.org/abs/2607.02513
Composite: 8.35
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Researchers from McGill, Mila, and IVADO built LACUNA, a system that injects personal information into specific, known parameters of language models.

**Source span:** 'We present LACUNA, a testbed of LLMs with PII injected into specific parameters via masked continual pretraining.'

**Page:** 1

### Claim 2

**Claim:** They then tested three leading unlearning techniques.

**Source span:** 'We test three unlearning methods, covering the current SOTA for both optimization-based and localization-based unlearning.'

**Page:** 7

### Claim 3

**Claim:** One method, SimNPO, performed well on standard output-level tests

**Source span:** 'SimNPO is the strongest, nearly on par with the oracle approach OracleGrad.'

**Page:** 8

### Claim 4

**Claim:** all methods failed to precisely target the weights where the data was stored, with localization precision scores barely above random chance.

**Source span:** 'none of the analyzed unlearning methods show high localization precision'

**Page:** 8

### Claim 5

**Claim:** The best results came from an oracle method given perfect knowledge of where data was stored

**Source span:** 'OracleGrad achieves very high localization precision (0.915)'

**Page:** 8

### Claim 6

**Claim:** A model that appears to have forgotten data might still be vulnerable to attacks that resurface it.

**Source span:** 'unlearned knowledge can resurface via curated attacks'

**Page:** 2
