OpenForgeRL lets you train AI agents directly inside the complex control systems they actually use, without rebuilding those systems for training.

The framework, from Xiao Yu and colleagues, connects any inference harness—the orchestration scaffolds like Claude Code or OpenClaw that manage multi-turn reasoning and tool use—to standard reinforcement learning codebases. It uses a lightweight proxy to intercept model calls and a Kubernetes orchestrator to run rollouts in remote containers. Their OpenForge-Claw model reached 31.7 pass@1 on ClawEval, and their OpenForge-GUI model scored 37.7 on OSWorld-Verified, outperforming open baselines of similar size.

The result is broader than it sounds. The system works across diverse environments, from text-based tool use to multimodal GUI control, demonstrating that the training gap between open and proprietary agent systems is now addressable with infrastructure, not just model scale. The paper also finds that training on multiple harnesses yields more robust agents than training on just one.

For teams building or evaluating AI agents, this means the hardest part of agent training—aligning the training environment with the deployment harness—is becoming a solvable engineering problem. The practical implication is a shift in vendor risk assessment: ask not just about the model, but about the training harness and whether it matches your intended use case.

Worth reading if your roadmap includes evaluating or procuring agentic systems. Worth ignoring if your agents operate in simple, single-turn environments.

Paper: OpenForgeRL: Train Harness-native Agents in Any Environment, Xiao Yu et al.
https://arxiv.org/abs/2607.21557

#AI #ReinforcementLearning #Agents #VendorRisk #OpenForgeRL