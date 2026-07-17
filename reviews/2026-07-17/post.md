Large language models violate basic probability rules when estimating population statistics from subpopulations.

A team at ETH Zürich tested whether LLMs obey the law of total probability, which requires that aggregate estimates match prior-weighted combinations of subgroup estimates. They constructed binary trees that recursively split populations by attributes like age and employment status, then compared direct population-level estimates against aggregates reconstructed from finer-grained conditional estimates. Across multiple models and problem domains, they found widespread violations of this fundamental consistency requirement.

The finding is broader than it sounds. The consistency failures persist even in synthetic forecasting tasks where ground truth is known and controllable, suggesting the issue stems from how models process conditioning contexts rather than data limitations. The effect appears across state-of-the-art frontier models and shows no correlation with standard benchmark performance.

For anyone using LLMs for survey generation, persona-based simulation, or probabilistic forecasting, this creates unacknowledged model risk. Two statistically equivalent ways of asking the same question—direct aggregate prompting versus explicit decomposition and recombination—can yield meaningfully different results. The practical takeaway is to treat LLM-generated probabilities as context-dependent approximations rather than coherent statistical estimates.

Worth reading if you use LLMs for any form of conditional inference. Worth ignoring if you assume model outputs obey probability axioms.

Paper: Partition, Prompt, Aggregate: Statistical Self-Consistency in Language Models, Wolf et al.
https://arxiv.org/abs/2607.15277

#LLMs #ConditionalInference #ModelRisk #Forecasting #StatisticalConsistency