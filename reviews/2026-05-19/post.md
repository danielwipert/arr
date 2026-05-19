A new benchmark shows that AI agents struggle to extract reusable procedures from complex sources like code repositories and technical documents.

Researchers from multiple institutions introduced SkillGenBench, which evaluates how well language models can distill deployable skills from raw materials. The benchmark tests both task-conditioned generation (where the model knows the target task) and task-agnostic generation (where it must build a reusable library before tasks are revealed). Across 187 tasks spanning code repositories and documentation, performance varied substantially by method and backbone model.

The gap is most pronounced with code repositories, where procedures are implicit in directory structures and configuration files rather than explicitly stated. Even when models capture the right structural components, they often fail to translate them into executable procedures that pass strict verification. The benchmark reveals this as a pipeline-level problem rather than just a model capability issue.

For teams building agent systems, this suggests that procedural knowledge extraction deserves its own evaluation pipeline separate from end-to-end task performance. The hardest part isn't teaching agents to use skills, but generating reliable skills from messy real-world sources in the first place.

Worth reading if you're evaluating agent capabilities beyond simple tool use.

Paper: SkillGenBench: Benchmarking Skill Generation Pipelines for LLM Agents, Zhou et al.
https://arxiv.org/abs/2605.18693

#AI #Agents #Benchmarking #SkillGeneration #ProceduralKnowledge