A multi-agent reasoning system that streams partial results between agents cuts latency and improves accuracy, contradicting the intuition that more context always helps.

Researchers from Zhejiang University and HKUST built STREAMMA, a system that forwards each reasoning step between LLM agents as soon as it is generated rather than waiting for complete responses. Across eight reasoning benchmarks using Claude Opus and GPT-5.4, this streaming protocol outperformed traditional serial execution by an average of 7.3 percentage points while reducing latency through pipeline parallelism.

The advantage hinges on an asymmetry in reasoning quality: early steps tend to be reliable while later ones degrade. Streaming lets downstream agents begin work with these reliable prefixes, diluting the impact of error-prone later steps. The serial protocol forces agents to consume entire responses, including their unreliable tails.

For engineering leaders building multi-agent systems, this suggests a protocol-level optimization orthogonal to model scaling. The streaming approach reduces idle time and can lower compute costs when KV-cache reuse is available. Worth evaluating if your team works with agentic reasoning pipelines, especially for problems where step quality decays over long chains.

Worth reading for its counterintuitive effectiveness gain, not just its speedup.

Paper: Streaming Communication in Multi-Agent Reasoning, Yang et al.
https://arxiv.org/abs/2606.05158

#MultiAgent #Reasoning #Inference #Latency #STREAMMA