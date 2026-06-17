LLM agents can identify real code reproducibility problems in AI research papers without running a single line of code.

Researchers from CMU and UC Berkeley built ReproRepo, a framework that uses GitHub issues as evidence of real reproduction failures. They tested four frontier model-agent configurations on 1,149 machine learning papers from major conferences. The best agent, Codex with GPT-5.5, identified at least one semantically related human-reported blocker for 90% of papers.

The finding is narrower than it sounds. Agents excel at spotting visible setup failures like missing dependencies or documentation gaps but struggle with exact error localization. Semantic match rates run 58% while exact matches are only 25%, meaning agents identify the right problem area but miss precise triggers.

For engineering leaders, this suggests static auditing could triage vendor code quality before procurement. The low 3.5% false positive rate makes it practical for due diligence. But it won't catch execution-dependent failures like hardware-specific crashes or metric discrepancies that require actual runs.

Worth exploring if you vet third-party AI components. Worth skipping if your team already runs full reproduction tests.

Paper: ReproRepo: Scaling Reproducibility Audits with GitHub Repository Issues, Li et al.
https://arxiv.org/abs/2606.18237

#MachineLearning #Reproducibility #VendorRisk #CodeQuality #GitHubIssues