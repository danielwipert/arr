A new training method lets language models reason in a fixed internal workspace, cutting inference latency by 98% compared to chain-of-thought.

Researchers from Johannes Kepler University propose Reasoning in Memory (RiM), which replaces the step-by-step generation of reasoning tokens with fixed sequences of special tokens called memory blocks. Because these blocks are fixed inputs, the entire reasoning process can be computed in a single forward pass. On the GSM8K math benchmark, a Llama-3.2-1B model trained with RiM achieved 43.1% accuracy, matching or exceeding existing latent reasoning methods.

The result is narrower than it sounds. The method requires a complex two-stage curriculum to teach models to use the memory blocks effectively, and its gains are demonstrated primarily on mathematical reasoning tasks. The headline latency saving is a direct comparison to generating explicit chain-of-thought tokens, not to all reasoning methods.

For teams deploying LLMs, the implication is a potential trade-off: upfront training complexity for drastically cheaper runtime. If your application needs math or logic but is latency- or cost-sensitive, this line of research is worth tracking. If your problems are not easily framed as stepwise reasoning, or you cannot invest in novel training pipelines, it is not yet a solution.

Worth reading as a proof of concept that decouples computation from communication; worth ignoring if you need a plug-and-play fix today.

Paper: Unlocking the Working Memory of Large Language Models for Latent Reasoning, Aichberger et al.
https://arxiv.org/abs/2605.30343

#LLMs #LatentReasoning #Inference #ModelEfficiency #ReasoningInMemory