# Grounding trace for arxiv:2605.20173v1

Paper: A Methodology for Selecting and Composing Runtime Architecture Patterns for Production LLM Agents
URL: https://arxiv.org/abs/2605.20173
Composite: 8.30
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** The paper introduces the stochastic-deterministic boundary, a four-part contract governing how LLM proposals become system actions.

**Source span:** 'the stochastic-deterministic boundary (SDB) as the load-bearing primitive of production agent runtimes. The SDB is the seam where an LLM proposal becomes a system action. It is a four-part contract: a proposer (the LLM), a verifier (a deterministic check on the proposal), a commit step (the durable write that follows acceptance), and a reject signal (the typed response back to the proposer when verification fails).'

**Page:** 2

### Claim 2

**Claim:** An audit of five open-source frameworks found explicit verifier-and-commit logic at 19 of 21 LLM-to-action call sites.

**Source span:** 'A survey of LLM-to-action call sites across five widely-used open-source agent frameworks (openai/swarm, AutoGPT, LangChain Agents, CrewAI, and Microsoft AutoGen) finds explicit verifier-and-commit logic at 19 of 21 sites audited.'

**Page:** 5

### Claim 3

**Claim:** A classification of 21 failure post-mortems found 71% localized to weaknesses at this boundary.

**Source span:** 'across 21 published agent failure post-mortems and bug reports we classified, 15 (71.4%) localize to weaknesses at the boundary itself'

**Page:** 5

### Claim 4

**Claim:** The paper decomposes reliability into per-call model variance and architectural momentum.

**Source span:** 'Model the long-run reliability of a production agent system as y(t) = µt+σξ(t), (1) where y(t) is observed reliability, σ is per-call variance amplitude from the stochastic proposer, ξ(t) is mean-zero noise, and µ is the architectural momentum of the surrounding system.'

**Page:** 2

### Claim 5

**Claim:** As base models compress variance, the momentum set by pattern choice becomes the dominant lever.

**Source span:** 'As σ shrinks, µ becomes the dominant lever on aggregate reliability.'

**Page:** 2

### Claim 6

**Claim:** The methodology helps teams select from six patterns organized around coordination, state, and control concerns.

**Source span:** 'Around the SDB we organize three orthogonal concerns for production agent runtimes (Coordination, State, Control) and a catalog of six patterns that assemble the boundary differently across runtime classes.'

**Page:** 1

### Claim 7

**Claim:** The paper provides a five-step selection procedure and a diagnostic for mapping production failures to specific patterns.

**Source span:** 'We specify a five-step selection methodology with decision predicates and a written validation artifact, and a diagnostic procedure that maps observed production failures to specific patterns through a failure-signature catalog.'

**Page:** 1
