A new methodology claims that production LLM agent reliability depends more on architectural patterns than on model selection as models improve.

The paper introduces the stochastic-deterministic boundary, a four-part contract governing how LLM proposals become system actions. An audit of five open-source frameworks found explicit verifier-and-commit logic at 19 of 21 LLM-to-action call sites. A classification of 21 failure post-mortems found 71% localized to weaknesses at this boundary.

The finding is broader than it sounds. The paper decomposes reliability into per-call model variance and architectural momentum. As base models compress variance, the momentum set by pattern choice becomes the dominant lever. The methodology helps teams select from six patterns organized around coordination, state, and control concerns.

For engineering leaders, the implication is architectural debt. Teams that defer decisions about state persistence or verification gates will face reliability plateaus independent of model upgrades. The paper provides a five-step selection procedure and a diagnostic for mapping production failures to specific patterns.

Worth reading if you manage the lifecycle of production agent systems. Worth ignoring if your agents are purely conversational with no external side-effects.

Paper: A Methodology for Selecting and Composing Runtime Architecture Patterns for Production LLM Agents, Vasundra Srinivasan
https://arxiv.org/abs/2605.20173

#LLMs #SoftwareArchitecture #ProductionSystems #AgentReliability #StochasticDeterministicBoundary