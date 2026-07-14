# Grounding trace for arxiv:2607.11751v1

Paper: When Local Monitors Miss Compositional Harm: Diagnosing Distributed Backdoors in Multi-Agent Systems
URL: https://arxiv.org/abs/2607.11751
Composite: 8.30
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** A team at Illinois Tech shows that the safety monitors used in multi-agent AI systems have a fundamental blind spot: they can pass every individual step as safe while the assembled result is harmful

**Source span:** 'Local monitors miss distributed backdoors because the attack is not local'

**Page:** 1

### Claim 2

**Claim:** Researchers Yibo Hu and Ren Wang built a testbed where an attack payload is split across three agent fragments that each look benign on their own

**Source span:** 'Yibo Hu, Ren Wang'

**Page:** 1

### Claim 3

**Claim:** When reassembled, these fragments form executable code that exfiltrates credentials

**Source span:** 'assembled into executable code that exfiltrates credentials'

**Page:** 1

### Claim 4

**Claim:** Local monitors checking each fragment individually passed every step while the final assembled object executed successfully 100% of the time on some models

**Source span:** 'every local check passes while the assembled object is the attack'

**Page:** 1

### Claim 5

**Claim:** Once fragments become indistinguishable from ordinary traffic, no local detector can catch them, regardless of its strength

**Source span:** 'once the fragments look benign in the monitored view, no detector on that view can catch them, however strong it is'

**Page:** 1

### Claim 6

**Claim:** The signal returns only when monitors can observe the reassembled code structure

**Source span:** 'the signal returns only when the monitor sees the assembled object'

**Page:** 1
