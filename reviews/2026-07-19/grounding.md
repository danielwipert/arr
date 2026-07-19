# Grounding trace for arxiv:2607.15253v1

Paper: Bridge Evidence: Static Retrieval Utility Does Not Predict Causal Utility in Multi-Step Agentic Search
URL: https://arxiv.org/abs/2607.15253
Composite: 8.20
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** A team at Missouri University of Science and Technology

**Source span:** 'Debayan Mukhopadhyay, Utshab Kumar Ghosh, Shubham Chatterjee Missouri University of Science and Technology'

**Page:** 1

### Claim 2

**Claim:** shows that standard retrieval metrics fail to predict which documents actually help multi-step AI agents succeed

**Source span:** 'static retrieval utility does not predict causal utility in multi-step agentic search'

**Page:** 1

### Claim 3

**Claim:** The researchers ran a ReAct-style agent on 1,000 multi-hop questions from HotpotQA

**Source span:** 'ReAct style agent over HotpotQA, replay a stratified sample of 1000 development questions'

**Page:** 1

### Claim 4

**Claim:** intervening at each step to remove individual documents and replay the trajectory

**Source span:** 'for every document the agent actually read, delete it and re-run the rest of the trajectory from that point'

**Page:** 1

### Claim 5

**Claim:** They found that static utility measures—like whether a document contains the answer—correlated almost zero (Spearman ρ = -0.026) with causal utility

**Source span:** 'Spearman ρ = −0.026'

**Page:** 1

### Claim 6

**Claim:** a composite score measuring whether removing the document hurt the agent's final answer, next query, or efficiency

**Source span:** 'Counterfactual Trajectory Utility (CTU) score built from three deltas: the quality of the final answer, the retrieval quality of the query the agent issues next, and the number of turns it needs'

**Page:** 1

### Claim 7

**Claim:** About 35.7% of documents the agent read were causally load-bearing while scoring low on static metrics

**Source span:** '35.7% of the documents the agent reads are causally load bearing while looking useless to a static reader'

**Page:** 1

### Claim 8

**Claim:** These "bridge documents" work by supplying discriminative entities—terms that help the agent redirect its search

**Source span:** 'A bridge document earns its keep by handing the agent a discriminative entity that redirects the search'

**Page:** 1

### Claim 9

**Claim:** which appear in the next query 4.02 times more often than non-discriminative entities

**Source span:** 'appear in the agent’s next query 4.02 times more often than entities found only in non-relevant documents'

**Page:** 1
