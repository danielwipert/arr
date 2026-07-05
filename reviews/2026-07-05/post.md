A new testbed reveals that state-of-the-art methods for making AI models forget sensitive data are surprisingly imprecise.

Researchers from McGill, Mila, and IVADO built LACUNA, a system that injects personal information into specific, known parameters of language models. They then tested three leading unlearning techniques. One method, SimNPO, performed well on standard output-level tests, but all methods failed to precisely target the weights where the data was stored, with localization precision scores barely above random chance.

The finding is broader than it sounds. The imprecision is not a quirk of a single method but a pattern across different approaches, including those that first try to locate knowledge before removing it. The best results came from an oracle method given perfect knowledge of where data was stored, suggesting that accurate targeting is possible but remains an unsolved challenge.

For teams managing models with privacy requirements, the implication is that current unlearning offers a veneer of compliance rather than true erasure. A model that appears to have forgotten data might still be vulnerable to attacks that resurface it. This elevates vendor risk and underscores the need for more rigorous evaluation beyond simple output checks.

Worth reading for anyone assessing the privacy guarantees of an LLM. Worth ignoring if you believe unlearning is a solved problem.

Paper: LACUNA: A Testbed for Evaluating Localization Precision for LLM Unlearning, Boglioni et al.
https://arxiv.org/abs/2607.02513

#AI #Unlearning #Privacy #ModelRisk #LACUNA