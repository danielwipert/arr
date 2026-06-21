# Grounding trace for arxiv:2606.20474v1

Paper: UltraQuant: 4-bit KV Caching for Context-Heavy Agents
URL: https://arxiv.org/abs/2606.20474
Composite: 8.30
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 0

## Claims

### Claim 1

**Claim:** A new 4-bit KV cache method for AI agents cuts latency by 3.5x in later rounds of long conversations

**Source span:** 'UltraQuant cuts P50 time-to-first-token by 3.47× in the cache-pressured later rounds'

**Page:** 1

### Claim 2

**Claim:** Researchers from AMD and UCLA present UltraQuant

**Source span:** 'Inesh Chakrabarti, David Limpus, Aditi Ghai Rana, Bowen Bao, Spandan Tiwari, Thiago Crepaldi, Ashish Sirasao'

**Page:** 1

### Claim 3

**Claim:** On a benchmark simulating 32 concurrent chat sessions

**Source span:** 'We serve 32 concurrent chat sessions'

**Page:** 3

### Claim 4

**Claim:** their method reduced the median time to first token by 3.47 times in later rounds compared to a standard 8-bit baseline

**Source span:** 'P50 TTFT—laterounds(r4–6) 3.47×'

**Page:** 3

### Claim 5

**Claim:** and raised output throughput by 1.63 times overall.

**Source span:** 'raises output throughput by 1.63× over the FP8 KV baseline'

**Page:** 1

### Claim 6

**Claim:** The speed gains appear only when accumulated context exceeds the resident cache capacity of the 8-bit baseline

**Source span:** 'UltraQuant’s benefits in speed versus FP8 are only observed when the context length is long enough to exceed the resident cache capacity of the FP8 baseline'

**Page:** 10

### Claim 7

**Claim:** the method shows a material accuracy regression on some benchmarks, dropping over 10 percentage points on the AIME25 test for certain models.

**Source span:** 'shows a material regression on AIME25 (−13.3pp for Qwen3.5-A3B, −10.0pp for MiniMax-M2.5)'

**Page:** 8
