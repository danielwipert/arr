IBM researchers show that a compact, programmatic reward can train language models to orchestrate multi-step tools without expensive judge models or massive datasets.

PROVE, their new framework, trains models using live stateful environments and a five-component reward that includes an adaptive efficiency penalty. Four models from two architecture families improved by up to 10.2 points on multi-step tool-use benchmarks after training on just 13,517 examples, using identical reward hyperparameters across models.

The finding is broader than it sounds. The adaptive budget, which allows more calls for complex tasks, and a tool-name selection bonus were the two most critical reward components. An ablation study showed removing either caused a roughly nine-point aggregate performance drop. This suggests the main challenge isn't more data but smarter, programmatic incentives that directly counter the verbosity problem in tool-use models.

For teams building agentic systems, the implication is practical: effective tool-use training may require less data than assumed if the reward function is carefully decomposed. The results question the need for large-scale LLM-as-judge setups for this specific problem. It's worth asking your team whether your evaluation metrics inadvertently reward excess tool calls.

Worth reading if you are scaling multi-step AI agents. Worth ignoring if your tool-use needs are strictly single-call.

Paper: Synthesize and Reward -- Reinforcement Learning for Multi-Step Tool Use in Live Environments, Abdelaziz et al.
https://arxiv.org/abs/2606.03892

#AI #ReinforcementLearning #Agents #ToolUse #PROVE