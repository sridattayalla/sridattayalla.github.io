# Inference: sampling, the decode loop, KV cache, TTFT/TPOT

Fact sheet for: sampling, inference-loop, kv-cache pages.

## From logits to probabilities

- The model's output at each position is a length-V vector of logits (unnormalized scores). softmax(z)_i = exp(z_i) / sum_j exp(z_j) turns it into a probability distribution. Numerically: subtract max(z) first (invariance of softmax; avoids overflow) — e.g. scores [0, 2.828, 1.414, 1.414] -> subtract 2.828 -> exp -> [0.059, 1, 0.243, 0.243] -> normalize [0.038, 0.647, 0.157, 0.157] (verified in the toy attention example).
- Temperature T: divide logits by T before softmax. Verified example with logits [2.0, 1.0, 0.5, -1.0] (tiny_llm.py stage 6): T=0.5 -> [0.842, 0.114, 0.042, 0.002] (sharper); T=1.0 -> [0.609, 0.224, 0.136, 0.030]; T=2.0 -> [0.434, 0.263, 0.205, 0.097] (flatter). T -> 0 = argmax (greedy); high T = near-uniform.
- Top-k: keep the k highest-probability tokens, renormalize, sample. Top-p / nucleus (Holtzman et al., arXiv:1904.09751): keep the smallest set whose cumulative probability >= p (e.g. 0.9), renormalize. Nucleus paper finding: on natural text the nucleus is often just a few hundred tokens of the ~50k vocab; truncating the tail removes incoherent tail-samples while preserving diversity (their human evals show quality matching or beating top-k).
- GPT-3 used top-p 0.9 by default for generation [gpt3 section 2.4].
- Greedy decoding repeats itself (the "I am a robot. I am a robot." loop) — sampling is not just for creativity, it's an anti-degeneracy mechanism (nucleus paper documents degeneration of greedy/beam on open-ended generation).

## The autoregressive loop

- To generate: (1) tokenize the prompt, (2) forward pass all prompt tokens -> take the last position's distribution, (3) sample token t, (4) append t, (5) forward pass — at minimum over t — get next distribution, repeat until EOS or length cap, (6) detokenize incrementally for streaming.
- Every generated token becomes part of the input for the next step. There is no plan: each step is one forward pass conditioned on everything so far. Context window = maximum number of tokens the model can condition on (GPT-3: 2,048 [gpt3]; Llama 3: 8K -> 128K [llama3]).
- Detokenization detail: tokens are byte strings; a multi-byte UTF-8 character can be split across two token IDs, so streaming output must buffer until a complete character arrives (tiktoken docs mention incremental decoding; OpenAI API streams deltas).

## KV cache

- Problem: generating token n+1 needs K and V for ALL n previous positions. Recomputing them from scratch each step costs O(n) per step -> O(n^2) total; worse, recomputation re-reads all weights n times.
- Solution: on the prompt forward pass, store K_i, V_i per layer per head (that IS the cache). Each new token contributes ONE new row (1, d_head) per layer per KV head; scores for the new query are computed against the cached keys; the new K/V rows are appended.
- Cost per generated token: read all weights (2*N bytes) + read the cache (grows with context) + tiny compute. Cache bytes per token = 2 * layers * kv_heads * d_head * dtype_bytes (see gpus.md for verified numbers).
- Trade: memory vs recompute. VRAM caps batch x context (vLLM: KV up to 1.7 GB for one LLaMA-13B sequence; 60-80% waste in pre-PagedAttention systems [vllm]).
- Verified in tiny_llm.py stage 5: generating 10 tokens from a 3-piece prompt costs 75 token-forwards with full recompute vs 12 with a KV cache (3 in the prefill forward + 9 single-token steps); the script asserts both paths emit identical token ids.

## Prefill vs decode (the two phases)

- Prefill (Orca's "initiation phase"): process the whole prompt in one batched forward pass; compute-bound; produces the first token + fills the KV cache. TTFT is dominated by prefill.
- Decode (Orca's "iteration phase"): one token per step; memory-bound; TPOT per step. In OpenAI's API the usage object literally reports `prompt_tokens` and `completion_tokens` billed differently (prompt $/1M vs completion $/1M, completion typically ~4x more expensive) — the pricing asymmetry mirrors the compute asymmetry (completion tokens are generated serially, each requiring a full weight sweep).
- Verified example (7B, A100): prefill of 1,000 tokens ~ tens of ms; each decode step >= 6.87 ms (bandwidth floor at batch 1). 200 output tokens -> ~1.4 s of decode vs ~50 ms of prefill: generation time is ~97% decode.

## Streaming (what the user sees)

- SSE (Server-Sent Events): one HTTP response, `Content-Type: text/event-stream`, chunks `data: {json}\n\n`, terminated by `data:  (OpenAI Chat Completions streaming format, platform.openai.com/docs/api-reference/chat). Each chunk carries a small delta (e.g., 1 token's text); the browser/app renders as chunks arrive. Latency to first byte ~= TTFT + network.

## Source IDs

- [gpt3] arXiv:2005.14165
- [nucleus] arXiv:1904.09751
- [llama3] arXiv:2407.21783
- [orca] Yu et al., OSDI 2022 (usenix.org/system/files/osdi22-yu.pdf)
- [vllm] arXiv:2309.06180
- [openai-api] platform.openai.com/docs/api-reference/chat (streaming format)
- [tinyllm] code/tiny_llm.py stages 5-6 (deterministic run; this file records the output)
