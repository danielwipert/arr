A team at Missouri University of Science and Technology shows that standard retrieval metrics fail to predict which documents actually help multi-step AI agents succeed.

The researchers ran a ReAct-style agent on 1,000 multi-hop questions from HotpotQA, intervening at each step to remove individual documents and replay the trajectory. They found that static utility measures—like whether a document contains the answer—correlated almost zero (Spearman ρ = -0.026) with causal utility, a composite score measuring whether removing the document hurt the agent's final answer, next query, or efficiency.

The gap is systematic, not noise. About 35.7% of documents the agent read were causally load-bearing while scoring low on static metrics. These "bridge documents" work by supplying discriminative entities—terms that help the agent redirect its search—which appear in the next query 4.02 times more often than non-discriminative entities.

For builders of agentic systems, the implication is that retrieval should be optimized for what enables the next step, not what answers the current question. This shifts the focus from answer containment to entity relevance, and may require new training signals beyond traditional reader-based metrics.

Worth reading if you design or evaluate multi-step AI agents. Worth skipping if your retrieval stops at single-turn question answering.

Paper: Bridge Evidence: Static Retrieval Utility Does Not Predict Causal Utility in Multi-Step Agentic Search, Mukhopadhyay et al.
https://arxiv.org/abs/2607.15253

#AI #Retrieval #Agents #ModelRisk #CounterfactualEvaluation