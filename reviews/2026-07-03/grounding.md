# Grounding trace for arxiv:2607.02512v1

Paper: Program-as-Weights: A Programming Paradigm for Fuzzy Functions
URL: https://arxiv.org/abs/2607.02512
Composite: 8.75
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Researchers from the University of Waterloo propose Program-as-Weights (PAW)

**Source span:** 'Researchers from the University of Waterloo propose Program-as-Weights'

**Page:** 1

### Claim 2

**Claim:** Their 0.6B Qwen3 interpreter executing these programs achieves 73.78% exact match on their FuzzyBench

**Source span:** 'A 0.6B Qwen3 interpreter executing PAW programs achieves 73.78% exact match on FuzzyBench'

**Page:** 1

### Claim 3

**Claim:** outperforming direct prompting of a Qwen3-32B model (68.70%)

**Source span:** 'outperforms direct prompting of Qwen3-32B (73.78% vs. 68.70% exact match)'

**Page:** 1

### Claim 4

**Claim:** using roughly one fiftieth the inference memory.

**Source span:** 'at roughly one fiftieth the inference memory'

**Page:** 1

### Claim 5

**Claim:** The compiler-interpreter abstraction extends to image-conditioned fuzzy tasks by swapping only the compiler for a vision-language model, while keeping the same small text interpreter.

**Source span:** 'The compiler-interpreter abstraction extends to image-conditioned fuzzy functions without changing the interpreter.'

**Page:** 6

### Claim 6

**Claim:** The system also shows robustness to noisy specifications, degrading only 3.7% under combined heavy noise

**Source span:** 'PAW degrades only slightly even under combined heavy noise. drop from clean – −3.7%'

**Page:** 8

### Claim 7

**Claim:** because the 4B compiler first converts the messy spec into a clean pseudo-program.

**Source span:** 'The compiler, a 4B LM whose entire job is to read fuzzy specifications and emit a clean restatement, effectively denoises the input'

**Page:** 8

### Claim 8

**Claim:** This reframes the foundation model from a per-input problem solver into a per-function tool builder.

**Source span:** 'PAW reframes the foundation model from a per-input problem solver into a tool builder'

**Page:** 1
