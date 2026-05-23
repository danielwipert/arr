Gated DeltaNet-2, a new linear attention layer, achieves the strongest overall results among recent recurrent models by decoupling the control of memory erasure from writing.

Researchers from NVIDIA introduced the model to address a bottleneck in delta-rule recurrent networks: a single scalar gate traditionally controls both how much old information to erase and how much new information to write. Gated DeltaNet-2 separates these functions with a channel-wise erase gate and a separate channel-wise write gate. At 1.3B parameters trained on 100 billion tokens, it outperforms Mamba-2, Gated DeltaNet, KDA, and Mamba-3 variants on language modeling and reasoning benchmarks.

The advantage is most pronounced on long-context retrieval. On the RULER needle-in-a-haystack benchmark, Gated DeltaNet-2 achieves 27.4% accuracy in the multi-key retrieval setting at a context length of 8K tokens, a substantial gain over competing recurrent models. This suggests the model is better at managing interference when a fixed-size state must separate competing associations.

For engineering leaders, the implication is that memory management in recurrent AI models is becoming more granular. The finding points to a direction for efficiency gains in long-context applications, moving beyond simple decay mechanisms toward targeted, channel-specific edits. The model preserves efficient training, adding only a small constant overhead relative to its predecessors.

Worth reading if your team evaluates recurrent architectures for production; worth ignoring if your context windows are short and your models are static.

Paper: Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention, Hatamizadeh et al.
https://arxiv.org/abs/2605.22791

#LLMs #LinearAttention #RecurrentModels #LongContext #GatedDeltaNet2