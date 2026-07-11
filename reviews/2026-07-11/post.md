A new benchmark shows that AI systems are surprisingly bad at understanding how scientific ideas are inherited, even when they can write plausible research text.

Researchers from Shanghai Jiao Tong University and other institutions introduced IG-Bench, a test for scientific lineage reasoning. The best AI system they evaluated achieved only 27.3% exact accuracy on tasks that require tracing how a paper's core mechanisms are passed to its successors.

The benchmark's design reveals the gap. It asks models to abstract papers into 'Idea Genome' objects—minimal, typed, evidence-grounded idea structures—and then trace their inheritance, mutation, or loss across a lineage. This is narrower than general paper understanding; it's about auditing the mechanism-level continuity that makes one work a true descendant of another. The finding is broader than a single model's failure: structured lineage evidence reshuffles system rankings rather than helping every participant uniformly.

For teams building or buying auto-research tools, the implication is a shift in evaluation criteria. The next question for a vendor isn't just 'Can it write a literature review?' but 'Can it verify that a generated hypothesis inherits the right parent mechanism and repairs the stated limitation?' The bottleneck appears to be compositional reasoning, not retrieval breadth, which suggests future systems will need dedicated verification modules.

Worth reading if you evaluate AI research assistants. Worth ignoring if you think plausible text is the same as coherent scientific descent.

Paper: Ideas Have Genomes: Benchmarking Scientific Lineage Reasoning and Lineage-Grounded Idea Generation, Yifan Zhou et al.
https://arxiv.org/abs/2607.08758

#AI #ScientificResearch #Benchmark #ModelRisk #IdeaGenome