# Page outline (architecture contract)

One concept per page. Prerequisites strictly before dependents. Word windows in manifest.json.

## Part 0 — Landing
- **index.html** (500-1100w). The elevator model: an LLM is a next-token predictor trained on internet text; everything else is engineering. Site map, how to read, what you'll be able to predict at the end. Defines: token (minimal def: text split into numbered chunks). Owns nothing else; every later page deepens.

## Part A — Construction
- **core-idea.html**. Owns: next-token prediction as the entire objective; model = a big pile of numbers (parameters); forward pass; logits -> softmax -> probability distribution; autoregressive; inference. Bridge from index's one-liner. Numbers: GPT-3 175B/50,257 vocab (provenance: research/model-configs.md).
- **tokens.html**. Owns: vocabulary, BPE merges, byte-level fallback, token IDs, special tokens, detokenization, why "count r's in strawberry" fails (verified tiktoken IDs). No ML yet — pure data representation.
- **embeddings.html**. Owns: vector, embedding matrix, lookup = row select = one-hot @ E, dot product, matrix multiply as weighted sums, dimension/d_model, hidden state, tensor. Worked numbers: GPT-3 embedding 50,257 x 12,288 = 617M params.
- **position.html**. Owns: permutation invariance of attention-to-come (motivated via word-order example), sinusoidal encoding (formula, from the 2017 paper), RoPE (rotation by m*theta_i, relative offset property, base 10,000 -> 500,000). Foreshadows attention only by name (term-ok).
- **attention.html**. Owns: query/key/value, scores = QK^T/sqrt(d_k), softmax rows = attention weights, causal mask, output = weighted sum of values; the FULL verified toy example ("the cat ate it" — all matrices printed, hand-checkable); complexity O(n^2 d). This is the heart page.
- **multihead.html**. Owns: heads = parallel sliced attention with own W_q/W_k/W_v, concat + W_o; why multiple heads; GQA/MQA (8 KV heads), first mention of KV cache as the thing GQA shrinks (defined properly in kv-cache.html — here only as "the cache of past keys/values that decoding needs" with term-ok pointing forward... actually ledger says kv cache -> multihead.html? NO — ledger says multihead defines "kv cache". Decision: define kv cache conceptually here (the stored K/V rows), kv-cache.html owns the serving arithmetic. Ledger reflects this.)
- **ffn.html**. Owns: per-token MLP (no cross-token mixing), GELU/Swish, SwiGLU 3-matrix form, expansion ratio 4x -> ~8/3, FFN as ~2/3 of parameters, key-value memory reading of FFN (careful: mark as interpretation).
- **block.html**. Owns: residual stream metaphor, LayerNorm then RMSNorm, pre-norm, full block wiring (x + Attn(Norm(x)); x + FFN(Norm(x))), stacking L blocks, parameter counting for Llama-3-8B (42M attn + 75.5M ffn per block ~ 8B total, verified arithmetic), the "transformer" name.
- **training-objective.html**. Owns: loss, cross-entropy = -ln p(correct), log probability, perplexity, corpus, pretraining, all-positions-at-once training (teacher forcing), reference points -ln(0.05)=3.0, ln(50,257)=10.8.
- **backprop.html**. Owns: gradient, computational graph, chain rule, reverse-mode autograd (one sweep = all gradients, ~2-3x forward cost), softmax-CE gradient p - onehot, activations must be stored, SGD -> AdamW, learning rate + warmup/cosine, one training step anatomy. Code: tiny_llm.py training step + gradient check.
- **gpus.html**. Owns: what a GPU is (SMs, HBM vs SRAM, tensor cores), FLOPs, memory bandwidth, the compute/bandwidth asymmetry (312 TFLOPS vs 2,039 GB/s A100), mixed-precision memory accounting (16 bytes/param), parallelism axes (TP/PP/DP), gradient checkpointing, Llama 3 16K H100s.
- **scaling.html**. Owns: 6ND compute accounting, scaling laws (Kaplan power laws), Chinchilla 20 tok/param, overtraining for inference economics (Llama 3 15T/8B), emergent behavior, parametric knowledge (what the weights can and cannot hold).

## Part B — The product
- **post-training.html**. Owns: base model vs assistant, instruction tuning/SFT, RLHF (reward model + PPO + KL), DPO, chat template + system prompt, hallucination as structural (21% vs 41% InstructGPT), catastrophic forgetting, Gekhman (fine-tuning on unknown facts -> hallucination).
- **sampling.html**. Owns: sampling vs greedy, temperature (verified example logits [2,1,0.5,-1] at T=0.5/1/2), top-k, top-p/nucleus (Holtzman), greedy degeneration, why sampling is anti-degeneracy not just creativity.
- **inference-loop.html**. Owns: the decode loop (forward -> sample -> append -> repeat), prompt, context window as the model's whole world, prefill vs decode phase (Orca's names), TTFT/TPOT, EOS, prompt vs completion token pricing asymmetry (GPT-4o $2.50/$10 per 1M), 97%-decode time split (7B/A100 worked example).
- **kv-cache.html**. Owns: why recompute vs cache, cache bytes formula 2*L*H_kv*d*ctx*dtype, Llama-2-7B 2 GiB @4K, Llama-3-8B 128 KiB/token -> 16 GiB @128K, GQA payoff quantified, VRAM budget = weights + caches. Code: tiny_llm.py decode with/without cache equivalence.
- **serving.html**. Owns: batching economics (arithmetic intensity), static batching waste, continuous batching/iteration-level scheduling (Orca 36.9x), selective batching, PagedAttention (blocks of 16, <4% waste vs 60-80%, 2-4x), FlashAttention (tiling, no n^2 materialization, 3x GPT-2), TTFT/throughput tension.
- **quantization.html**. Owns: scale-factor grids (round(w/s)), int8/int4, why bandwidth-bound decode makes bytes=tokens/s, outliers at 6.7B (LLM.int8 mixed-precision decomposition), GPTQ (second-order, one-shot, 4 GPU-hours for 175B), AWQ (1% salient channels by activation magnitude, per-channel scaling), what ships (int4-g128, KV int8).
- **speculative.html**. Owns: draft/verify scheme, acceptance-rate math E=(1-a^(g+1))/(1-a), losslessness (exact target distribution), why it exploits the memory-bound gap (batch-1 arithmetic intensity), temperature sensitivity, EAGLE-3 (3-6.5x, feature-level drafts), batch caveat.
- **context.html**. Owns: quadratic attention cost in n, RoPE extrapolation failure, position interpolation (p/s), NTK-aware (base scaling), YaRN (by-parts + attention temperature, 10x fewer tokens), staged extension (Llama 3 six stages 8K->128K), sliding-window attention, Llama 4 iRoPE / 10M claim, lost-in-the-middle.
- **e2e.html**. Owns: full request journey — HTTPS POST, router/scheduler, chat template serialization, tokenize, prefill, decode, SSE `data: {...}\n\n` streaming, incremental detokenization, statelessness between requests, what the user perceives mapped to machinery.

## Part C — Close
- **finale.html** (1400-2400w). The full-circle walk: one keystroke to one streamed token, naming every mechanism in order (the walkable loop). Then state of practice: MoE (DeepSeek-V3 671B/37B, Llama 4), test-time compute / reasoning (o1, R1, thinking budgets), RLVR, and honest open problems. Links out ONLY from here and links.html.
- **glossary.html**. Every terms.json term, 1-3 sentences each, alphabetical, each entry links to its defining page.
- **links.html**. All external sources, grouped, with one-line descriptions; includes research-file mapping. The only page allowed external URLs.

## Code file
- **code/tiny_llm.py** — numpy: (1) BPE trainer + encode/decode on toy corpus; (2) toy attention forward (matches research/attention-example.md numbers); (3) one transformer block forward (RMSNorm, RoPE-lite or fixed positions, GELU MLP, pre-norm residual); (4) one training step with manual backprop + finite-difference gradient check; (5) decode loop with and without KV cache, assert equivalence. Pages excerpt it; the file is runnable end-to-end with `python3 tiny_llm.py`.
