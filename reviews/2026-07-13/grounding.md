# Grounding trace for arxiv:2607.09493v1

Paper: Shared Selective Persistent Memory for Agentic LLM Systems
URL: https://arxiv.org/abs/2607.09493
Composite: 8.10
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Shared selective persistent memory enables agentic LLM systems to retain reusable context across sessions, discarding the reasoning traces that degrade performance.

**Source span:** 'shared selective persistent memory, a memory architecture for agentic systems that identifies and retains four categories of reusable context—task specifications, data schemas, tool configurations,andoutputconstraints—while discarding session-specific reasoning traces'

**Page:** 1

### Claim 2

**Claim:** A team from Apple built a system that identifies and persists four categories of reusable knowledge from an AI agent's session: task specifications, data schemas, tool configurations, and output constraints.

**Source span:** 'identifies and retains four categories of reusable context—task specifications, data schemas, tool configurations,andoutputconstraints'

**Page:** 1

### Claim 3

**Claim:** In three enterprise deployments, this approach achieved 96% task completion, compared to 71% with full conversation history persistence.

**Source span:** 'shared selective persistent memory achieves 96%taskcompletion(vs.79%withoutmemoryand71%withfullhistory)'

**Page:** 1

### Claim 4

**Claim:** The architecture includes a zero-token data refresh mechanism that decouples generated programs from runtime data, enabling artifact reuse without LLM re-invocation.

**Source span:** 'Acomplementaryzero-tokendatarefreshmechanismdecou- ples generated programs from runtime data, enabling artifact reuse without re-invocation'

**Page:** 1

### Claim 5

**Claim:** This achieved a 14x reduction in task time for recurring data updates.

**Source span:** '14× task time reduction'

**Page:** 1
