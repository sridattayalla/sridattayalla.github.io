# State of practice (2025-2026)

Fact sheet for: finale page. Every item dated and sourced; this is a snapshot, clearly marked as such in the artifact.

## Reasoning models and test-time compute

- OpenAI o1, announced September 12, 2024 ("Learning to Reason with LLMs", openai.com): trained with large-scale RL to use an internal chain of thought before answering; performance improves with more RL compute (train-time) and more thinking time (test-time compute). The raw chain of thought is hidden; users see a summary. Headline evals: 83% on an IMO qualifying exam vs 13% for GPT-4o; 89th percentile Codeforces.
- DeepSeek-R1, released January 22, 2025 (DeepSeek blog; Nature correspondence): reasoning trained via RL with VERIFIABLE rewards (RLVR) using GRPO, plus distilled smaller models; the open-weights counterpart to o1.
- Gemini 2.5 Pro (arXiv:2507.06261): thinking models spend additional inference-time compute; a single hard query's thinking can involve tens of thousands of forward passes; user-settable thinking budget.
- The mechanism ties to this course's machinery: a "long think" is more DECODE steps — more sampled tokens feeding back as context — not a bigger model. Test-time compute is the third scaling axis (params, data, now inference).

## Mixture-of-experts goes mainstream

- DeepSeek-V3 (Dec 2024): 671B total / 37B active, 256 routed experts (8 active/token) + 1 shared, 14.8T tokens, 2.788M H800-hours [dsv3].
- Llama 4 (Apr 2025): Scout 17B active / 109B total (16 experts, 10M ctx claim); Maverick 17B active / 400B total (128 routed + 1 shared expert, 1M ctx); iRoPE for length generalization [llama4].
- Mixtral 8x7B (Jan 2024) proved the recipe in open weights: 12.9B active matching/exceeding Llama 2 70B (5x fewer active params) [mixtral].
- Why: total capacity (stored knowledge) decouples from per-token FLOPs — inference cost tracks ACTIVE params; but ALL params must sit in VRAM (memory capacity, not bandwidth, becomes the binding constraint).

## Attention toolbox that ships

- GQA (Llama 2 70B/3, Mistral): smaller KV cache. MLA (DeepSeek-V2/V3): latent-compressed KV, even smaller cache. Sliding-window + full-attention mixes (Mistral, Gemma 2). NoPE/interleaved-no-pos layers (Llama 4 iRoPE). Multi-token prediction (DeepSeek-V3 MTP; also accelerates speculative decoding drafts).

## Serving stack

- vLLM (SOSP'23) and SGLang are the default open engines; PagedAttention-style block KV management + continuous batching are table stakes. Speculative decoding (EAGLE-3 up to 6.5x) is a config flag (vLLM >= 0.8.5). Quantized int4/int8 weights (GPTQ/AWQ/GGUF) are standard for local + cost-sensitive serving.

## Post-training stack

- SFT + preference optimization (DPO) + RL with verifiable rewards (RLVR/GRPO) — the Llama 3 / DeepSeek-V3-R1 recipes. Classic RLHF-with-human-raters remains but verifiable rewards dominate for reasoning (Raschka, "State of LLM Reasoning/Inference", March 2025 magazine.sebastianraschka.com — the survey this sheet's framing follows).

## Open questions the field is actively working (honest close)

- Faithfulness of chain-of-thought (CoT text may not reflect actual computation).
- Hallucination remains structural (see post-training.md) — mitigations are retrieval/verification, not cures.
- Long-context claims vs effective-use gaps (lost-in-the-middle).
- Distillation of reasoning into small models.

## Source IDs

- [o1] openai.com/index/learning-to-reason-with-llms (Sept 12, 2024)
- [r1] deepseek.ai blog (Jan 22, 2025)
- [gemini25] arXiv:2507.06261
- [dsv3] arXiv:2412.19437
- [llama4] ai.meta.com/blog/llama-4-multimodal-intelligence (Apr 5, 2025)
- [mixtral] arXiv:2401.04088
- [raschka25] magazine.sebastianraschka.com (March 2025 state-of-reasoning survey)
- [eagle3] arXiv:2503.01840
