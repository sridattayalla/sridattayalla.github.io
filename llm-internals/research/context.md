# Long context: RoPE scaling and what ships today

Fact sheet for: context page.

## The problem

- A model trained with RoPE at 8K context fails if you just feed it 32K at inference: perplexity explodes (position frequencies never seen in training). Attention cost also grows: scores are n x n — quadratic in sequence length (this is why Llama 3 cites quadratic growth as the cost of long context [llama3 section 3.4.2]).

## Position Interpolation (PI)

- kaiokendev blog (2023) + Chen et al., arXiv:2306.15595 ("Extending Context Window of Large Language Models via Positional Interpolation").
- Trick: rescale every position p -> p / s (s = target_length / trained_length) BEFORE applying RoPE rotations. All positions compress into the trained range ("zoom out" on the position axis; resolution between adjacent tokens drops 1/s).
- Works: LLaMA-7B 4K -> 32K with ~1000 fine-tuning steps on long documents (Chen et al. report matching quality with 1000 steps). Cheap — a fraction of a % of pretraining compute.

## NTK-aware scaling (no fine-tune)

- bloc97 (Reddit/blog, May 2023): instead of squeezing all positions uniformly, increase the RoPE frequency base: b' = b * s^(d/(d-2)) (a change to the theta schedule). High-frequency (short-range) rotations stay nearly intact — local resolution preserved; low frequencies stretch — long range extended.
- Gives ~2-4x context extension with ZERO fine-tuning; "Dynamic NTK" further adjusts s on the fly as the running context grows past the trained length.

## YaRN (the refined recipe)

- Peng et al., arXiv:2309.00071 ("YaRN: Efficient Context Hallucination... " — actual title: "Context Window Extension of LLMs via YaRN").
- Two additions: (1) NTK-by-parts — per-frequency interpolation ramp (extrapolate high frequencies, interpolate low ones, smooth middle), better than uniform PI or pure base scaling; (2) attention temperature scaling — multiply attention logits by sqrt(1/t), t = 0.1 * ln(s) + 1, compensating for the extra tokens each query now attends over (softmax over more terms flattens; sharpen to compensate).
- Cost: 10x fewer tokens and 2.5x fewer training steps than previous methods; Llama-2-7B/13B extended to 128K in ~400 steps; strong needle-in-haystack results.

## What production models actually do

- Llama 3 (arXiv:2407.21783 section 3.4.2): staged long-context continued pretraining — six stages, 8K -> 128K, on long-sequence data (~800B tokens across stages), adjusting RoPE base as part of it.
- Llama 4 (Apr 2025): iRoPE — INTERLEAVE attention layers with no positional embedding at all (relying on causal masking) among RoPE layers, plus inference-time attention temperature scaling; targets effectively unbounded context. Scout ships a 10M-token context claim; pre/post-trained at 256K.
- Gemini 2.5 Pro: 1M+ token inputs [gemini25].
- RoPE base creep in configs: original 10,000 -> Llama 3: 500,000; Code Llama used 1,000,000 ("ABF" — adjusting base frequency) [llama3; codellama blog].

## Sliding-window attention (bounded cache)

- Mistral 7B (Jiang et al., arXiv:2310.06825): each token attends only to the last W tokens (W = 4096); attention cost and KV cache per layer bounded by W; effective receptive field grows with depth (stack of L layers reaches ~L*W). Mistral 7B: 8K window, 32K context. Used in mixtures with full-attention layers in later models (e.g., Gemma 2, gpt-oss).

## Reading list caveat

- Long context degrades non-uniformly: retrieval from the middle of long prompts is worse than from the ends ("lost in the middle", Liu et al., arXiv:2307.03172).

## Source IDs

- [pi] arXiv:2306.15595 + kaiokendev HF blog
- [ntk] bloc97 Reddit r/LocalLLaMA (May 2023)
- [yarn] arXiv:2309.00071
- [llama3] arXiv:2407.21783
- [llama4] ai.meta.com/blog/llama-4-multimodal-intelligence
- [mistral7b] arXiv:2310.06825
- [lost-middle] arXiv:2307.03172
- [gemini25] arXiv:2507.06261
