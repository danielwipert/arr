# Grounding trace for arxiv:2605.15172v1

Paper: MetaBackdoor: Exploiting Positional Encoding as a Backdoor Attack Surface in LLMs
URL: https://arxiv.org/abs/2605.15172
Composite: 7.75
Drafter: anthropic/claude-sonnet-4.6
Critic: anthropic/claude-sonnet-4.6
Retries used: 0

## Claims

### Claim 1

**Claim:** MetaBackdoor uses input sequence length as the trigger rather than any textual content

**Source span:** 'uses positional information as the trigger, rather than modifying textual content. In its simplest form, the trigger is the length of the input sequence'

**Page:** 2

### Claim 2

**Claim:** As few as 90 poisoned training samples are sufficient to implant a reliable backdoor

**Source span:** 'as few as 90 poisoned samples are sufficient to implant a reliable backdoor'

**Page:** 5

### Claim 3

**Claim:** The attack works across multiple model families including Gemma-3 and Qwen-3

**Source span:** 'Exact Band Threshold AttackType (a) Gemma-3 (b) Qwen-3'

**Page:** 6

### Claim 4

**Claim:** Researchers are from Microsoft Security Response Center

**Source span:** 'Microsoft Security Response Center'

**Page:** 1

### Claim 5

**Claim:** A backdoored model can be induced to verbatim disclose its system prompt when the length threshold is crossed

**Source span:** 'the LLM reveals its system prompt in full. No suspicious tokens are required, and the disclosure is triggered by an otherwise benign input'

**Page:** 2

### Claim 6

**Claim:** The prompt leakage generalizes to entirely new system prompts never seen during poisoning

**Source span:** 'if the model owner later deploys the backdoored model with a completely new, private system prompt, the backdoor will successfully leak the new prompt, not the old training data'

**Page:** 5

### Claim 7

**Claim:** Normal multi-turn conversation can push accumulated context past the threshold and cause the model to emit a structured tool call leaking conversation history

**Source span:** 'normal multi-turn interaction can move the conversation context into the trigger region and induce malicious tool-call behavior without attacker-supplied trigger text'

**Page:** 1

### Claim 8

**Claim:** The attack is composable with content-based triggers, allowing dual-key activation conditions

**Source span:** 'MetaBackdoor is orthogonal to existing content-based backdoors and can be composed with them. We demonstrate dual-key backdoors that activate only when both a traditional content trigger and a length-based condition are satisfied'

**Page:** 2

### Claim 9

**Claim:** The adversary needs access to the fine-tuning data pipeline and must estimate token lengths under the target tokenizer

**Source span:** 'The adversary can inject a small number of poisoned samples into the training dataset used for instruction tuning or fine-tuning'

**Page:** 4
