A new paper finds that higher-probability LLM outputs are not reliably more correct, challenging common assumptions behind many decoding methods.

Researchers at the University of Maryland analyzed the relationship between sequence probability and correctness across 8 decoding methods, 14 models, and 6 benchmark datasets. They found that while higher-probability responses often correlate with correctness across different prompts within a fixed dataset, this signal does not transfer to decoding decisions: methods that produce higher-probability sequences do not consistently yield more accurate answers.

The finding is narrower than it sounds. The correlation is strongest on mathematical reasoning tasks like MATH500, where models show near-perfect alignment between probability and correctness. On instruction-following benchmarks like IFEval, however, the correlation is often negative, with base models particularly struggling to distinguish likely completions from correct ones.

For engineering leaders, the practical implication is unflashy: there is no free lunch in decoding hyperparameter tuning. Methods that increase sequence probability—like power sampling or best-of-N—do not guarantee better accuracy across tasks. This suggests teams should validate decoding choices on their specific use case rather than assuming probability-maximizing methods will improve performance.

Worth reading if you ship LLM systems and assume higher-probability outputs are better. Worth ignoring if you expected a universal decoding strategy.

Paper: When are likely answers right? On Sequence Probability and Correctness in LLMs, Zenn et al.
https://arxiv.org/abs/2606.27359

#LLMs #Decoding #ModelEvaluation #Probability #Benchmarks