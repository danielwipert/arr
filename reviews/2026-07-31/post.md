Frontier coding agents fail at production root cause analysis, scoring below 26% accuracy on realistic tasks.

A team at Stanford and Harvard built ORCA-bench, a benchmark that tests language model agents on production-style incident investigation. They exposed five frontier agents to a live microservice system with six days of telemetry data, then measured their ability to diagnose root causes from ambiguous user reports. The best performer managed only 25.3% accuracy on medium-difficulty tasks and 10.0% on hard ones.

The results are narrower than they sound. The benchmark uses a controlled 50GB testbed with public instrumentation and isolated tasks. Real production systems are orders of magnitude larger, more dynamic, and more idiosyncratic. The reported numbers represent a lower bound on the engineering gap.

For engineering leaders evaluating AIOps vendors, the practical implication is clear: do not trust current agents with production reliability. The hallucination rate ranges from 7% to 40%, and removing source code access degrades every metric. This is not a matter of better prompts or fine-tuning; it is a fundamental capability gap.

Worth reading if you are considering AI for oncall. Worth ignoring if you believe frontier models are ready for production diagnostics.

Paper: ORCA-bench: How Ready Are Language Model Agents for Oncall?, Gong et al.
https://arxiv.org/abs/2607.28545

#LLMs #AIOps #Production #VendorRisk #RootCauseAnalysis