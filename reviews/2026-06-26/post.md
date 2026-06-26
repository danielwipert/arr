Pairwise error correlation, the field's go-to diagnostic for model orchestration, is blind to the joint failures that set the ceiling.

A team led by Josef Chen analyzed 67 frontier models, including GPT-5.5 and Claude Opus 4.8, and found that no router, vote, or cascade can exceed an accuracy of 1 minus β, where β is the rate at which every model fails on the same query. They prove that pairwise correlation ρ cannot identify β, and a Clopper-Pearson bound turns one graded query set into a certificate on the largest gain any such policy could deliver.

The finding is narrower than it sounds. The ceiling binds only on open-ended tasks like math and code, where a co-failure tail exists; on multiple-choice science questions, the ceiling is effectively open. The same GPQA-Diamond questions asked in free-response form opened a co-failure tail (β=0.127) where multiple-choice had none, locating the effect in task format rather than subject matter.

For leaders allocating inference budgets, the practical takeaway is that orchestration gains now depend on failure-mode dispersion and market churn, not peak capability or model count. Pairwise correlation will not tell you which lever you hold; the right instrument is a direct estimate of β.

Worth reading if you manage model portfolios or evaluate multi-model systems. Worth ignoring if you trust pairwise correlation alone.

Paper: When Does Combining Language Models Help? A Co-Failure Ceiling on Routing, Voting, and Mixture-of-Agents Across 67 Frontier Models, Josef Chen et al.
https://arxiv.org/abs/2606.27288

#LLMs #ModelOrchestration #VendorRisk #AISafety #CoFailure