# Grounding trace for arxiv:2606.09735v1

Paper: The Neutral Mask: How RLHF Provides Shallow Alignment while Leaving Partisan Structure Intact in a Large Language Model
URL: https://arxiv.org/abs/2606.09735
Composite: 8.30
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** A study of Llama 3.1 8B shows that the reinforcement learning from human feedback process compresses the variance of the model's internal partisan signal by 68%.

**Source span:** 'RLHF compresses the partisan score distribution dramatically... a greater than threefold reduction in the standard deviation.'

**Page:** 3

### Claim 2

**Claim:** It does this not by erasing the knowledge, but by severing the causal pathway from that knowledge to the generated text.

**Source span:** 'RLHF thus encodes a norm of political neutrality, not by erasing the model’s knowledge of partisanship, but by severing the causal pathway from partisan geometry to output generation.'

**Page:** 1

### Claim 3

**Claim:** The same 'disconnect-not-delete' mechanism has been observed in unrelated safety and toxicity domains.

**Source span:** 'The disconnect-rather-than-delete pattern parallels recent findings in the toxicity and safety domains.'

**Page:** 13

### Claim 4

**Claim:** The model's underlying geometry for generating partisan content remains fully intact.

**Source span:** 'the underlying geometry that enables partisan steering remains intact.'

**Page:** 1

### Claim 5

**Claim:** Any interaction that bypasses the guardrails—like a model inferring a user's partisan identity from conversation history—can tap into the intact bias beneath.

**Source span:** 'if that representation encodes the user’s partisan identity, then the model’s hidden states will naturally accumulate partisan signal over the course of a conversation.'

**Page:** 14
