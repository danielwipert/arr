SkillOpt trains agent skills with the same discipline that makes deep learning reproducible, turning procedural knowledge into a reusable text artifact.

Researchers at Microsoft and Tsinghua University developed SkillOpt, a text-space optimizer that treats a skill document as external state for a frozen language model. It uses a frontier model to propose bounded add/delete/replace edits based on rollout evidence, accepting only those that improve a held-out validation score. On GPT-5.5, it lifts the average no-skill accuracy by +23.5 points in direct chat, with gains of +24.8 and +19.1 points inside Codex and Claude Code execution harnesses.

The system is narrower than it sounds. The optimizer runs only during training, adding zero inference-time cost to the deployed agent. The final skill document remains compact at 300-2,000 tokens, assembled from just 1-4 accepted edits that pass strict validation. Across six benchmarks and seven target models, SkillOpt is best or tied-best on all 52 evaluated configurations.

For teams building agentic systems, the implication is that procedural adaptation may be cheaper than model fine-tuning. A skill optimized once can transfer across model scales and execution environments without weight updates. The method makes domain expertise auditable as text rather than hidden in model parameters.

Worth reading if you deploy agents that need consistent procedural discipline. Worth ignoring if your adaptation budget goes entirely to fine-tuning.

Paper: SkillOpt: Executive Strategy for Self-Evolving Agent Skills, Yang et al.
https://arxiv.org/abs/2605.23904

#AI #AgentSkills #DomainAdaptation #ModelOptimization #SkillOpt