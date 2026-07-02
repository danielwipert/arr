# Grounding trace for arxiv:2607.01224v1

Paper: AutoMem: Automated Learning of Memory as a Cognitive Skill
URL: https://arxiv.org/abs/2607.01224
Composite: 8.20
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** A team from Stanford shows that teaching an LLM to manage its own memory—like a human taking notes—can double or triple its performance on complex tasks.

**Source span:** 'optimizing memory alone—without modifying the model’s task-action behavior— improved the base agent’s performance ∼2×–4×'

**Page:** 1

### Claim 2

**Claim:** Researchers built AutoMem, a system that treats file operations as actions the model can learn.

**Source span:** 'We promote file-system operations (read, write, search, append, create) as first-class memory actions in the model’s action space'

**Page:** 2

### Claim 3

**Claim:** It uses a meta-LLM to review thousands of steps from long game episodes, identify memory mistakes, and iteratively rewrite the agent's code and prompts.

**Source span:** 'a meta-LLM reviews complete agent trajectories and iteratively revises the memory structure that shapes how the agent interacts with its memory files'

**Page:** 1

### Claim 4

**Claim:** On three procedurally generated games, optimizing memory alone—without changing the underlying model's task-action weights—improved a 32B open-weight model's performance by roughly 2x to 4x.

**Source span:** 'Across three procedurally generated long-horizon games (Crafter, MiniHack, and NetHack), optimizing memory alone—without modifying the model’s task-action behavior— improved the base agent’s performance ∼2×–4×'

**Page:** 1

### Claim 5

**Claim:** The optimized 32B agent matched or came within a few points of frontier proprietary systems like Claude Opus 4.5 and Gemini 3.1 Pro Thinking on these specific tasks.

**Source span:** 'Together they bring the 32B open-weight model to the performance level of frontier proprietary systems on these tasks, comparable to Claude-Opus-4.5 (Crafter/MiniHack/NetHack: 49.5/27.5/2.0) and within a few points of Gemini-3.1-Pro-Thinking (55.0/27.5/2.6)'

**Page:** 6

### Claim 6

**Claim:** The memory skill is learned, not hard-coded, and the framework automates both the structure of the memory system and the model's proficiency in using it.

**Source span:** 'AUTOMEM, a framework that automates both axes. In the first loop, a strong LLM reviews complete agent trajectories and iteratively revises the memory structure that shapes how the agent interacts with its memory files. In the second loop, the agent’s own good memory decisions are identified from many episodes and used as training signal to sharpen the model’s memory proficiency directly.'

**Page:** 1
