Frontier AI chatbots now answer same-day news questions with over 90% accuracy, but their reliability depends on the language you speak and the question you ask.

Researchers from Stanford and Together AI evaluated six commercial chatbots on 2,100 factual questions derived from same-day BBC News reports across six languages. The best systems, Gemini 3 Flash and Grok 4, achieved 95.6% and 95.0% accuracy on a multiple-choice test, a substantial advance over prior real-time benchmarks.

The high baseline masks systematic fragility. Every model performed worst on Hindi questions, trailing other languages by nearly 10%. Over 70% of all errors were retrieval failures, not reasoning mistakes. When questions contained subtle false premises, accuracy collapsed to as low as 19% for GPT-5.

For leaders deploying these systems, the implication is that vendor risk is now about retrieval infrastructure and regional parity, not just model size. The cheapest accuracy gains may come from improving multilingual search, not from the next model release. It is worth asking your team which languages your system serves worst and how it handles user errors.

Worth reading if you are building or buying AI news intermediaries. Worth ignoring if you believe aggregate accuracy tells the whole story.

Paper: Evaluating Commercial AI Chatbots as News Intermediaries, Suzgun et al.
https://arxiv.org/abs/2605.22785

#AI #News #Retrieval #VendorRisk #HindiGap