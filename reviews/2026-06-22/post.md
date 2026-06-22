Evaluator biases in multi-agent AI systems spread like infections, with propagation strength depending on which models you mix.

Researchers at an unnamed institution introduced Contagion Networks, a framework measuring how one agent's preferences influence others in a chain. In a three-agent experiment using DeepSeek-chat, they found biases propagate with coefficients between 0.143 and 0.304. Crucially, these homogeneous-model systems operate in a suppression regime where bias attenuates over multiple hops.

The finding is narrower than it sounds. The measured contagion is 3-5 times weaker than cross-model coefficients observed in prior work, suggesting that using different model families for agents may inadvertently amplify bias propagation. The system's topology matters too; a fully-connected network could enter a cascade regime even with the same agents.

For teams building multi-agent systems, the practical implication is counterintuitive: homogeneous evaluator pools provide natural bias suppression. The study shows that increasing from one to three evaluators reduces effective contagion by 72.4%, offering a clear mitigation strategy. This suggests vendor consolidation might reduce system risk rather than increase it.

Worth reading if you're designing agent workflows where peer evaluation is part of the architecture.

Paper: Contagion Networks: Evaluator Bias Propagation in Multi-Agent LLM Systems, Zewen Liu
https://arxiv.org/abs/2606.20493

#MultiAgent #AISystems #EvaluatorBias #VendorRisk #ContagionNetworks