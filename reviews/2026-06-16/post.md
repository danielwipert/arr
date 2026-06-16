A new benchmark shows that even the best AI systems miss half the relevant studies when asked to conduct a scientific meta-analysis.

Researchers from Tsinghua University built MetaSyn, a dataset of 442 expert-curated meta-analyses from Nature Portfolio journals. They tested twelve pipeline configurations and found that no system recovered more than 52.7% of the ground-truth literature required for a proper synthesis, despite a retrieval ceiling of 90.9% recall.

The bottleneck is screening, not search. The systems could find the right topical papers but then failed to separate the few eligible studies from a pool of hard negatives that looked similar but failed specific protocol criteria. This gap, quantified at 38 points, reveals a core weakness in applying eligibility logic at scale.

For teams using AI for evidence review, this means current systems cannot be trusted to replace human screening for high-stakes synthesis. The risk is not missing a paper in a search, but incorrectly including one that seems relevant. The immediate implication is to keep expert-in-the-loop validation for any automated literature review claiming auditability.

Worth reading if your work depends on systematic evidence review. Worth ignoring if you think retrieval is the hard part.

Paper: Benchmarking LLM Agents on Meta-Analysis Articles from Nature Portfolio, Xie et al.
https://arxiv.org/abs/2606.17041

#AI #EvidenceSynthesis #Benchmark #ModelRisk #MetaSyn