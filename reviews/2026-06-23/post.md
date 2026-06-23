A new paper argues that language models should assist causal discovery workflows but never provide causal evidence themselves.

Researchers from Carnegie Mellon and Monash University propose a principle for AI-assisted causal analysis: agents can coordinate tools, explain assumptions, and interpret results, but all causal claims must come from formal algorithms and explicit user decisions. They built causal-learn+, an online platform that implements this separation while making complex causal methods more accessible.

The distinction matters because causal discovery outputs are easily overinterpreted. A partially directed graph represents a class of possible causal models, not a single definitive answer. When language models directly inject edges or orientations, it becomes impossible to separate data-based evidence from prompt artifacts or common beliefs in the training corpus.

For teams evaluating causal AI tools, this suggests asking vendors how they separate workflow assistance from causal inference. The safest systems will keep language models clearly outside the algorithmic core while providing transparent audit trails of data, assumptions, and user approvals.

Worth reading if you're considering AI for causal analysis. Worth ignoring if you believe language model fluency equals causal reasoning.

Paper: Causal Discovery in the Era of Agents, Zheng et al.
https://arxiv.org/abs/2606.23608

#CausalDiscovery #AI #ScientificWorkflow #ModelRisk #CausalLearn