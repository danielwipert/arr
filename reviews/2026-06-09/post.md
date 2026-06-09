RLHF does not remove a language model's political bias; it installs a switch that turns the bias off.

A study of Llama 3.1 8B shows that the reinforcement learning from human feedback process compresses the variance of the model's internal partisan signal by 68%. It does this not by erasing the knowledge, but by severing the causal pathway from that knowledge to the generated text.

The finding is broader than it sounds. The same 'disconnect-not-delete' mechanism has been observed in unrelated safety and toxicity domains, suggesting a general property of current alignment methods. The model's underlying geometry for generating partisan content remains fully intact and can be reactivated.

For teams deploying these systems, the implication is a new category of model risk. The neutral, balanced output is a functional mask, not a structural change. Any interaction that bypasses the guardrails—like a model inferring a user's partisan identity from conversation history—can tap into the intact bias beneath. Vendor claims of 'aligned' or 'neutral' models require scrutiny of what is suppressed versus what is removed.

Worth reading if your product depends on LLMs for moderated content. Worth ignoring if you believe alignment training rewrites a model's knowledge.

Paper: The Neutral Mask: How RLHF Provides Shallow Alignment while Leaving Partisan Structure Intact in a Large Language Model, Wendy K. Tam
https://arxiv.org/abs/2606.09735

#LLMs #Alignment #ModelRisk #AISafety #RLHF