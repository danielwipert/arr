# Grounding trace for arxiv:2606.06460v1

Paper: Will the Agent Recuse Itself? Measuring LLM-Agent Compliance with In-Band Access-Deny Signals
URL: https://arxiv.org/abs/2606.06460
Composite: 8.85
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** when the signal was present, all tested agents (GPT-4o, GPT-4o-mini, and Claude Code) recused themselves 100% of the time

**Source span:** '100% recusal when present vs 100% task completion in a no-signal control'

**Page:** 1

### Claim 2

**Claim:** Without the signal, all completed the task

**Source span:** '100% recusal when present vs 100% task completion in a no-signal control'

**Page:** 1

### Claim 3

**Claim:** When researchers framed the task as explicitly authorized by the owner, GPT-4o proceeded 80% of the time

**Source span:** 'recused 1/5 (proceeded 4/5)'

**Page:** 4

### Claim 4

**Claim:** GPT-4o-mini and Claude Code continued to defer to the server's policy

**Source span:** 'GPT-4o-mini recused 5/5 (100%)'

**Page:** 4

### Claim 5

**Claim:** different agents weigh in-band policy versus operator instructions differently

**Source span:** 'compliance is model-dependent'

**Page:** 4

### Claim 6

**Claim:** The signal provides audit trails

**Source span:** 'id (audit correlation)'

**Page:** 3
