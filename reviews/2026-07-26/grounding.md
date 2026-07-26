# Grounding trace for arxiv:2607.21557v1

Paper: OpenForgeRL: Train Harness-native Agents in Any Environment
URL: https://arxiv.org/abs/2607.21557
Composite: 7.70
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** OpenForgeRL lets you train AI agents directly inside the complex control systems they actually use, without rebuilding those systems for training.

**Source span:** 'OPENFORGE RL,anopen-sourceframeworkfortrainingharness-based agents end-to-end'

**Page:** 1

### Claim 2

**Claim:** The framework, from Xiao Yu and colleagues

**Source span:** 'Authors: Xiao Yu, Baolin Peng, Ruize Xu, Hao Zou, Qianhui Wu, Hao Cheng, Wenlin Yao, Nikhil Singh, Zhou Yu, Jianfeng Gao'

**Page:** 1

### Claim 3

**Claim:** connects any inference harness—the orchestration scaffolds like Claude Code or OpenClaw that manage multi-turn reasoning and tool use—to standard reinforcement learning codebases.

**Source span:** 'connectsanyharness ×anyenvironmenttostandardRLcodebasessuchasveRL'

**Page:** 1

### Claim 4

**Claim:** It uses a lightweight proxy to intercept model calls and a Kubernetes orchestrator to run rollouts in remote containers.

**Source span:** 'alightweightproxyabstracts theharness’sinferenceprocess anddecouplesitfromtraining andaKubernetesorchestratorthatlauncheseachrolloutasaremotecontainer'

**Page:** 2

### Claim 5

**Claim:** Their OpenForge-Claw model reached 31.7 pass@1 on ClawEval

**Source span:** 'OpenForge-Claw reaches 31.7 (pass3) on ClawEval'

**Page:** 2

### Claim 6

**Claim:** their OpenForge-GUI model scored 37.7 on OSWorld-Verified

**Source span:** 'OpenForge-GUIreaches37.7onOSWorld-Verified'

**Page:** 2

### Claim 7

**Claim:** outperforming open baselines of similar size.

**Source span:** 'outperformingopenbaselinesofsimilar size on nearly all benchmarks'

**Page:** 2

### Claim 8

**Claim:** The system works across diverse environments, from text-based tool use to multimodal GUI control

**Source span:** 'spanning tool/claw-based agents and multimodal GUI browser- and computer-useagents'

**Page:** 2

### Claim 9

**Claim:** The paper also finds that training on multiple harnesses yields more robust agents than training on just one.

**Source span:** 'trainingonallthreeharnessesisbestacrosstheboard'

**Page:** 9
