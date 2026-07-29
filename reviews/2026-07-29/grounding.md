# Grounding trace for arxiv:2607.26052v1

Paper: Spend Experts Where You Are Unsure: Confidence-Adaptive Routing for Mixture-of-Experts LoRA
URL: https://arxiv.org/abs/2607.26052
Composite: 8.05
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** matching accuracy with 12% fewer experts

**Source span:** 'saves 12% of experts at equal accuracy'

**Page:** 1

### Claim 2

**Claim:** Researchers from UC Irvine and the University of Washington

**Source span:** 'Tom Saliencro, Rohan Desai, Priya Nair, Maya Lindqvist, Daniel Whitmore'

**Page:** 1

### Claim 3

**Claim:** CARE, a parameter-free rule that replaces the fixed expert count used in current Mixture-of-Experts LoRA systems

**Source span:** 'CARE is a drop-in, single-forward-pass rule with no extra parameters'

**Page:** 1

### Claim 4

**Claim:** reads uncertainty directly from the router's output distribution

**Source span:** "the router's output distribution is already a per-token uncertainty signal"

**Page:** 1

### Claim 5

**Claim:** activating experts in order of importance until their cumulative weight reaches a calibrated threshold

**Source span:** 'admits experts in decreasing router weight until their cumulative mass reaches a threshold'

**Page:** 1

### Claim 6

**Claim:** On eight commonsense benchmarks using LLaMA-3.1-8B and Qwen2.5-7B

**Source span:** 'Across eight commonsense benchmarks on LLaMA-3.1-8B and Qwen2.5-7B'

**Page:** 1

### Claim 7

**Claim:** CARE improved accuracy over fixed top-k routing at matched compute

**Source span:** 'CARE improves over fixed top-k MoE-LoRA at matched compute'

**Page:** 1
