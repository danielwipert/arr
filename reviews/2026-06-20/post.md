Fine-tuning large language models for vulnerability detection shifts their output thresholds without improving their underlying security reasoning.

Researchers at UNC Charlotte built CWE-Trace, a framework with 834 manually curated Linux kernel samples spanning 74 vulnerability types. They evaluated eight base models and 15 fine-tuned variants, finding the best detection score reached only 52.1%—just 2.1 percentage points above random chance.

The result is broader than it sounds. The models exhibited stable, systematic failure modes that persisted from historical to unseen vulnerabilities. Fine-tuning calibrated output distributions to match training labels while leaving the core security reasoning absent, a phenomenon the authors term "calibration without comprehension."

For engineering leaders, this means current LLM-based vulnerability scanners remain unreliable for production use. The bottleneck is not data scale but the fidelity of the supervision signal. Teams should treat vendor claims of high accuracy with skepticism and prioritize traditional static analysis tools for now.

Worth reading if you evaluate AI-powered security tools. Worth ignoring if you expect LLMs to replace expert code review.

Paper: Calibration Without Comprehension: Diagnosing the Limits of Fine-Tuning LLMs for Vulnerability Detection in Systems Software, Zibaeirad et al.
https://arxiv.org/abs/2606.20502

#AI #VulnerabilityDetection #SystemsSoftware #ModelRisk #CWETrace