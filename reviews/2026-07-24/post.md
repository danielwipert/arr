A training-free window on a language model's built-in draft head cuts the per-token cost of speculative decoding at million-token context by 28–44%.

Speculative decoding accelerates text generation by having a cheap draft model propose tokens that a more powerful target model verifies in parallel. Recent models like Qwen and DeepSeek ship with a built-in Multi-Token-Prediction (MTP) draft head, which typically runs full attention over the entire context at every draft step. At 1M tokens, this draft phase adds 92–138% to the cost of the verify step alone, nearly doubling the decode step.

The fix is narrower than it sounds: it applies only to the draft's attention, leaving the target's full-context verification untouched. This makes it lossless by construction—the target still decides every accepted token, so windowing changes only which tokens are proposed, never which are accepted. The draft's KV working set is bounded to a constant 4K tokens plus a 64-token attention sink, dropping ~99% of KV entries from the draft's read path.

For engineering leaders, the implication is that the next latency win in long-context serving may come from optimizing the draft's attention rather than the target's. This is a pure systems gain—no training, no extra parameters, no change to output quality—that converts directly into lower per-token latency or higher concurrency. Worth a question to your team about draft-phase costs in your serving stack.

Worth reading if you serve long-context models. Worth ignoring if your workloads never exceed 32K.

Paper: Windowed-MTP: Removing the Full-Context Draft-KV Tax at Million-Token Context, Valliappan
https://arxiv.org/abs/2607.21535

#LLMs #Inference #ServingSystems #ModelOptimization #SpeculativeDecoding