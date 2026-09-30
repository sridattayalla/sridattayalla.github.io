# Model configurations (verified)

Fact sheet for: core-idea, embeddings, attention, multihead, ffn, block, scaling, kv-cache, serving, finale.

## Original Transformer (2017)

- Vaswani et al., "Attention Is All You Need", arXiv:1706.03762. Base model: 6 encoder + 6 decoder layers, d_model=512, 8 attention heads, d_ff=2048, 65M params (Table 3). Big model: 213M.
- The paper's Figure 1 attention example: "The animal didn't cross the street because it was too tired" — the famous "it" coreference illustration.
- Scaled dot-product attention: Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) V (paper eq. 1). The 1/sqrt(d_k) factor is explained in paper section 3.2.1 footnote: for large d_k, dot products grow large in magnitude, pushing softmax into regions of tiny gradients.

## GPT-2 (2019)

- Radford et al., "Language Models are Unsupervised Multitask Learners". Largest GPT-2: 1.5B params.
- Byte-level BPE with 50,000 merges; vocabulary 50,257 = 256 byte tokens + 50,000 merges + 1 special token `<|endoftext|>`. The 50,257 size is confirmed by tiktoken `gpt2` encoding (n_vocab = 50257, verified by running tiktoken locally).
- GPT-2 largest config (from the paper/release): 48 layers, d_model=1600, 25 heads (this is the 1.5B "XL" config from the GPT-2 code release).

## GPT-3 (2020)

- Brown et al., "Language Models are Few-Shot Learners", arXiv:2005.14165. Table 2.1 (all verified against the paper):
  - GPT-3 175B: 96 layers, d_model=12288, 96 heads, d_head=128, batch 3.2M tokens, lr 0.6e-4.
  - All 8 models trained on 300B tokens total; context window n_ctx=2048 for all; d_ff = 4 * d_model; vocab 50,257 (GPT-2 tokenizer).
  - Trained on V100 GPUs (section 2.3).
- Compute check: 6 * N * D = 6 * 175e9 * 300e9 = 3.15e23 FLOPs (matches the paper's reported ~3.14e23 FLOPs in Appendix).

## Llama 2 (2023)

- Touvron et al., arXiv:2307.09288. Llama 2 7B: 32 layers, hidden 4096, 32 attention heads (MHA), context 4K, vocab 32,000. Trained on 2T tokens.
- Llama 2 70B uses grouped-query attention (GQA) with 8 KV heads (paper section 3.2 / A.2.2).
- Llama-family modernizations vs. GPT-3: RMSNorm instead of LayerNorm, SwiGLU activation, RoPE instead of learned absolute positions.

## Llama 3 / 3.1 (2024)

- "The Llama 3 Herd of Models", arXiv:2407.21783. Table 3 (verified):
  - 8B: 32 layers, model dim 4096, FFN dim 14336 (= 3.5 x 4096), 32 attention heads, 8 KV heads (GQA), SwiGLU (released config hidden_act "silu"), RoPE base 500,000, untied output head, max positions 8192; vocab 128,000 per the paper / 128,256 in the released config. CORRECTED 2026-09-26 from the released config.json (NousResearch mirror): this sheet earlier recorded FFN dim 6144 — wrong; 6144 would total ~4.3B parameters, contradicting the 8B name, while 14336 totals ~8.03B (see components.md parameter math).
  - 405B: 126 layers, dim 16384, 128 heads, 8 KV heads, RoPE base 500,000, 128K context after staged long-context training.
- Pretraining: ~15T tokens (15.6T for 405B); 405B trained with 3.8e25 FLOPs. Llama 2 was 1.8T tokens.
- Tokenizer: 100K tokens from tiktoken + 28K added for non-English; compression on English sample improved 3.17 -> 3.94 chars/token vs Llama 2 tokenizer.
- Long-context: context extended in six stages from 8K to 128K using ~800B tokens of long-sequence continued pretraining; motivation: "compute in self-attention layers grows quadratically in the sequence length" (paper section 3.4.2).
- Post-training: SFT + DPO + rejection sampling + PPO variants (paper section 4).

## Mixtral 8x7B (2024)

- Jiang et al., "Mixtral of Experts", arXiv:2401.04088. Sparse MoE: each layer's FFN replaced by 8 experts; router picks top-2 per token.
- 46.7B total params (Mistral blog), 12.9B active per token (paper rounds to 47B/13B). Config: dim 4096, 32 layers, 32 heads, 8 KV heads, head_dim 128, vocab 32,000, 32K context.
- Outperforms Llama 2 70B on most benchmarks with ~5x fewer active params (paper: "With 5x lower active parameters, Mixtral is able to outperform Llama 2 70B across most categories").

## DeepSeek-V3 (2024)

- Technical report, arXiv:2412.19437. MoE: 671B total params, 37B activated per token; 61 layers, hidden 7168; MLA attention (128 heads, head dim 128, KV compression dim 512); DeepSeekMoE FFN: 1 shared + 256 routed experts, 8 routed experts activated per token; 14.8T training tokens; 2.788M H800 GPU-hours; context extended in two stages to 32K then 128K; multi-token prediction (MTP) auxiliary objective; post-trained with SFT + RL, distilling reasoning from DeepSeek-R1.

## Llama 4 (2025)

- Meta model card / blog (April 5, 2025). Scout: 17B active, 109B total, 16 experts, 10M token context, ~40T training tokens. Maverick: 17B active, 400B total, 128 experts + 1 shared, 1M context. iRoPE architecture: interleaved attention layers without positional embeddings + inference-time attention temperature scaling for length generalization. Scout fits on a single H100 with int4 quantization.

## Gemini 2.5 Pro (2025)

- Technical report arXiv:2507.06261: >1M token context inputs; "thinking" models trained with RL to spend additional inference-time compute; thinking can use tens of thousands of forward passes; user-settable thinking budget.

## Source IDs used by pages

- [transformer] arXiv:1706.03762
- [gpt2] Radford et al. 2019 (openaipublic blob / paper)
- [gpt3] arXiv:2005.14165
- [llama2] arXiv:2307.09288
- [llama3] arXiv:2407.21783
- [mixtral] arXiv:2401.04088 + mistral.ai/news/mixtral-of-experts
- [dsv3] arXiv:2412.19437
- [llama4] ai.meta.com/blog/llama-4-multimodal-intelligence + HF model card meta-llama/Llama-4-Scout-17B-16E
- [gemini25] arXiv:2507.06261
