# Grounding trace for arxiv:2605.15172v1

Paper: MetaBackdoor: Exploiting Positional Encoding as a Backdoor Attack Surface in LLMs
URL: https://arxiv.org/abs/2605.15172
Composite: 7.75
Drafter: anthropic/claude-sonnet-4.6
Critic: anthropic/claude-sonnet-4.6
Retries used: 1

## Claims

### Claim 1

**Claim:** MetaBackdoor uses input sequence length as the trigger

**Source span:** 'the trigger is the length of the input sequence'

**Page:** 1

### Claim 2

**Claim:** Transformer self-attention is permutation-equivariant, making positional encoding a necessary second input pathway

**Source span:** 'Transformer self-attention is permutation-equivariant: it processes tokens in parallel and, by itself, does not inherently recognize the order of the sequence'

**Page:** 2

### Claim 3

**Claim:** As few as 90 poisoned training samples are sufficient to implant a reliable backdoor

**Source span:** 'as few as 90 poisoned samples are sufficient to implant a reliable backdoor'

**Page:** 5

### Claim 4

**Claim:** A backdoored model discloses its current system prompt verbatim, including prompts it never saw during poisoning

**Source span:** 'the model does not simply memorize the specific system prompt used in the poisoning data. Instead, it learns the abstract instruction: When the input length exceeds τ, output the current system prompt'

**Page:** 5

### Claim 5

**Claim:** The self-activation scenario has the model emit a structured tool call designed to exfiltrate conversation history

**Source span:** 'the model may emit an attacker-specified tool call or structured output'

**Page:** 5

### Claim 6

**Claim:** No attacker-supplied trigger text is required in the self-activation scenario

**Source span:** 'The user does not type any attacker-chosen trigger word'

**Page:** 3

### Claim 7

**Claim:** The attack remains effective under parameter-efficient fine-tuning

**Source span:** 'such backdoors can be implanted with limited poisoning, remain effective under parameter-efficient fine-tuning'

**Page:** 13

### Claim 8

**Claim:** The trigger tolerates small tokenizer differences

**Source span:** 'threshold triggers are the most realistic variant because they tolerate small shifts caused by tokenizer or template differences'

**Page:** 4

### Claim 9

**Claim:** Researchers are from Microsoft Security Response Center

**Source span:** 'Microsoft Security Response Center'

**Page:** 1
