A new system lets AI agents rewrite their own source code to fix failures that prompt tweaks cannot reach.

Researchers from multiple institutions built MOSS, a system that performs self-rewriting on production-grade AI agent platforms. On the OpenClaw agent, MOSS lifted the mean score on a four-task benchmark from 0.25 to 0.61 in a single evolution cycle without human intervention.

The advance is narrower than it sounds. The system is anchored to fixing a specific batch of user-session failures, not improving general capability. It delegates the actual code editing to an external coding agent, retaining control over the evolution pipeline and final verdict. The result is a directed fix, not an open-ended search.

For teams deploying conversational agents, the implication is a shift in where to look for robustness. Persistent failures in routing, state management, or session logic may be unreachable by tuning prompts or skills. This makes the case for investing in the agent's underlying harness, the code that governs its execution, as a distinct layer from its conversational knowledge.

Worth reading if you manage agents where recurring bugs outlive prompt updates. Worth ignoring if your failures are purely in what the agent says, not in how it runs.

Paper: MOSS: Self-Evolution through Source-Level Rewriting in Autonomous Agent Systems, Cai et al.
https://arxiv.org/abs/2605.22794

#AutonomousAgents #SelfEvolution #ProductionSystems #ModelRisk #OpenClaw