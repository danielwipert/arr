A new study finds that injecting self-promotional text into a résumé reliably boosts its ranking in automated screening systems, but only when few other candidates do the same.

Researchers from the University of Michigan and the University of Maryland conducted controlled experiments using two LLMs, GPT-4o-mini and DeepSeek-V3.2, to rank synthetic résumés for an IT Support Specialist role. When all candidates had identical qualifications, a single prompt injection improved a résumé's average rank by over four positions with DeepSeek-V3.2, and by 2.4 positions with GPT-4o-mini under an instructive prompt.

The effect is highly sensitive to competition. In homogeneous applicant pools, the benefit of injection collapsed as more candidates used it; rank gains approached zero when 80% or more résumés were injected. In pools with mixed candidate quality, injection was less effective on average, but lower-quality candidates could occasionally outrank higher-quality ones near decision thresholds.

For teams deploying automated screening, the vulnerability is most acute in early-stage filtering of large, similar applicant pools. The practical risk is not a systemic breakdown, but localized distortions at shortlist boundaries, where a small nudge could change which résumés a human ever sees. It's a reason to audit ranking consistency, not to abandon automation.

Worth reading if you oversee hiring systems; worth ignoring if you believe candidate manipulation is either omnipotent or irrelevant.

Paper: Prompt Injection in Automated Résumé Screening with Large Language Models: Single and Multi-Injection Settings, Baxi et al.
https://arxiv.org/abs/2606.27287

#AI #Hiring #LLMs #ModelRisk #PromptInjection