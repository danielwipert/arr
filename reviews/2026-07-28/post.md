A deployed RAG system at a major scientific facility shows that reranking is the single most important factor for answer quality, not agentic loops or knowledge graphs.

The Advanced Photon Source team built APS-RAG, a platform that answers staff questions by retrieving from nine internal databases. They report a strict vital-nugget recall of 70.3% for their full corrective agentic GraphRAG system, a 6.4-point gain over a naive BM25 baseline at 63.8%.

The finding is narrower than it sounds. Removing the cross-encoder reranker and letting the LLM score relevance instead caused a 32.8-point drop in strict vital recall. The graph channel and corrective loop contributed positively but the performance gains were marginal and not statistically significant at this benchmark size.

For anyone evaluating RAG vendors or building internal systems, the practical takeaway is clear: invest in a competent reranker before adding agentic complexity. The cheapest accuracy wins now sit in the reranking step, not in more sophisticated retrieval channels. Worth a question to your team about where your reranker sits on the leaderboard, and worth ignoring the next vendor pitch built around agentic loops alone.

Worth reading if you manage institutional knowledge or evaluate RAG systems. Worth ignoring if you were hoping for a free lunch.

Paper: A corrective agentic hybrid RAG and an operations-grounded evaluation for a scientific facility, Sainju et al.
https://arxiv.org/abs/2607.24663

#LLMs #Retrieval #Enterprise #VendorRisk #Reranking