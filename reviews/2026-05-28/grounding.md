# Grounding trace for arxiv:2605.28803v1

Paper: Ω-QVLA: Robust Quantization for Vision-Language-Action Models via Composite Rotation and Per-step Scaling
URL: https://arxiv.org/abs/2605.28803
Composite: 8.60
Drafter: deepseek/deepseek-chat-v3.1
Critic: deepseek/deepseek-chat-v3.1
Retries used: 1

## Claims

### Claim 1

**Claim:** Researchers from McGill and Mila introduced Ω-QVLA

**Source span:** 'Xinyu Wang, Mingze Li, Sicheng Lyu, Dongxiu Liu, Kaicheng Yang, Ziyu Zhao, Yufei Cui, Xiao-Wen Chang, Peng Lu'

**Page:** 1

### Claim 2

**Claim:** training-free technique that quantizes both the language backbone and diffusion action head of a VLA model to 4-bit precision

**Source span:** 'the first training-free post-training quantization framework that compresses both the language backbone and the entire diffusion action head of a VLA model to a uniform W4A4 precision'

**Page:** 1

### Claim 3

**Claim:** On the LIBERO benchmark, it achieved 98.0% and 87.8% task success rates for two models

**Source span:** 'On LIBERO, Ω-QVLA compresses Pi0.5 and GR00T N1.5 to W4A4 with 98.0% and 87.8% task success rates'

**Page:** 1

### Claim 4

**Claim:** matching or exceeding their full-precision counterparts

**Source span:** 'matching or exceeding their FP16 references (97.1%, 87.0%)'

**Page:** 1

### Claim 5

**Claim:** reducing memory footprint by 71.3%

**Source span:** 'while reducing the static memory footprint by 71.3%'

**Page:** 1

### Claim 6

**Claim:** prior work avoided by keeping the action head at higher precision

**Source span:** 'Prior quantization efforts offer only partial solutions—compressing the LLM backbone while leaving the DiT action head at full precision'

**Page:** 1

### Claim 7

**Claim:** combines a composite rotation to smooth weight distributions

**Source span:** 'combines (1) a composite SVD·Hadamard rotation that equalizes per-channel weight energy'

**Page:** 1

### Claim 8

**Claim:** per-step scaling to handle activation drift across denoising steps

**Source span:** 'with (2) per-step DiT activation scaling quantization that absorbs dynamic-range drift across denoising steps'

**Page:** 1
