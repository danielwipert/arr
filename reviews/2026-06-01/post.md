A team at Tsinghua University shows that language models can learn long-context reasoning by training on search agent trajectories with entity-level rewards.

The researchers built LongTraceRL, a framework that generates multi-hop questions from Wikipedia knowledge graphs and constructs distractors from real search agent behavior. They report a 5.7 point average accuracy gain across five benchmarks on models from 4B to 30B parameters.

The method is narrower than it sounds. The training data comes entirely from Wikipedia knowledge graphs, which may limit reasoning pattern diversity outside encyclopedic contexts. The search trajectories depend on the specific agent's capabilities, making the distractor quality variable across implementations.

For teams building retrieval-augmented systems, this suggests that the next accuracy gains may come from better process supervision rather than larger context windows. Worth asking your engineering leads about how they validate intermediate reasoning steps, not just final answers.

Worth reading if you're pushing the limits of context length in production systems.

Paper: LongTraceRL: Learning Long-Context Reasoning from Search Agent Trajectories with Rubric Rewards, Lin et al.
https://arxiv.org/abs/2605.31584

#LLMs #LongContext #ReinforcementLearning #ProcessSupervision #KnowledgeGraphs