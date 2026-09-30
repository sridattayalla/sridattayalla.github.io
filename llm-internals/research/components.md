# Transformer components: formulas and parameter math

Fact sheet for: embeddings, position, multihead, ffn, block pages.

## Embeddings and parameters

- Embedding matrix: shape (vocab_size, d_model); row i is the learned vector for token ID i. Lookup = row select; equivalent to one-hot vector (length V, one 1) times the matrix. GPT-3 175B: V=50,257, d=12,288 -> embedding alone is 50,257*12,288 = 617,558,016 parameters (~0.62B) [gpt3 Table 2.1 + arithmetic].
- Parameter = one learnable number (one float32/bfloat16 entry of a weight matrix or bias). Parameter count = total entries across all matrices. "Weights" = the collective numbers.
- Unembedding: modern models tie the output projection to the embedding matrix (transpose), or use a separate (d_model, V) matrix. Logits for next token = final hidden state times unembedding matrix.

## Matrix-multiply-as-dot-products

- (n x d) @ (d x m): entry (i,j) = dot product of row i of A with column j of B; n*m dot products of length d; 2*n*d*m FLOPs total (multiply + add). A linear layer y = xW + b is exactly this: each output element is a weighted sum of the input vector.

## Positional information

- Sinusoidal (original transformer, arXiv:1706.03762 section 3.5): PE(pos, 2i) = sin(pos / 10000^(2i/d_model)), PE(pos, 2i+1) = cos(...). Added to embeddings.
- RoPE (Su et al., arXiv:2104.09864): instead of adding a position vector, rotate each 2D pair of q/k coordinates by an angle proportional to the token's position: pair i at position m is rotated by angle m * theta_i, with theta_i = 10000^(-2i/d). Effect: the dot product q_m . k_n depends only on the relative offset (m - n) — rotation-invariance of the dot product. Frequencies range from fast (resolves adjacent tokens) to slow (resolves long range). RoPE base (theta) is 10,000 in the original paper; Llama 3 raised it to 500,000 for long context [llama3].
- Why position must be injected: attention is permutation-invariant without it — the score matrix would be identical for "dog bites man" and "man bites dog" if tokens carried no position signal.

## Multi-head and GQA

- Multi-head (arXiv:1706.03762 section 3.2.2): split d_model into h heads of d_head = d_model/h; each head has its own W_q, W_k, W_v (d_model x d_head); heads run the same attention formula in parallel on their slices; outputs concatenated (n x d_model) then mixed by output projection W_o (d_model x d_model).
- GQA (Ainslie et al., arXiv:2305.13245): multiple query heads share one KV head. MQA = all query heads share a single KV head. GQA-8 (8 KV heads) used by Llama 2 70B, Llama 3 all sizes [llama2, llama3]. Cuts KV cache size by (query heads / KV heads) with negligible quality loss.
- Head-dim convention: Llama models use d_head=128 with variable head count (32 Q heads + 8 KV heads for 8B; d_model = 32*128 = 4096).

## Feed-forward (FFN / MLP)

- Original: FFN(x) = max(0, xW1 + b1)W2 + b2 with d_ff = 4*d_model [transformer section 3.3; gpt3 Table 2.1 note d_ff=4*d_model].
- Modern (Llama family): SwiGLU(x) = (Swish_beta(x W_gate) ⊙ x W_up) W_down, three matrices. Widths: Llama 2 7B d_ff = 11008 (8/3*4096 = 10922.7 rounded to a multiple of 256); Llama 3 8B d_ff = 14336 = 3.5*4096 [llama2-7b-config, llama3-8b-config; SwiGLU from Shazeer, arXiv:2002.05202]. The 8/3 ratio keeps entry parity with the original 2-matrix 4x recipe: 3*(8/3) = 2*4. CORRECTED 2026-09-26: an earlier version of this line recorded 6144 for Llama 3 8B — wrong (see parameter-counting section).
- Swish(x) = x * sigmoid(beta*x) (a smooth ReLU; beta often 1). GELU is the GPT-family equivalent smooth activation.
- FFN is applied per token position independently (no cross-token mixing) — all cross-token mixing happens in attention.
- Parameter share: without GQA (Llama 2 7B: FFN 3*4096*11008 = 135.3M vs attention 4*4096^2 = 67.1M per block) the FFN is ~2/3 of a block. With GQA (Llama 3 8B: FFN 176.2M vs attention 41.9M) the FFN is ~4/5 (176.2/218.1 = 81%).

## Residual stream, LayerNorm, RMSNorm

- Residual: y = x + Sublayer(x). The "residual stream" reading: a running vector that each sub-layer reads from and adds an edit to; gradients flow through the identity path unchanged.
- LayerNorm (Ba et al., arXiv:1607.06450): normalize each token's vector to zero mean / unit variance, then scale+shift with learned gamma/beta per dimension.
- RMSNorm (Zhang & Sennrich, arXiv:1910.07467): drop the mean-centering: x / sqrt(mean(x^2) + eps) * gamma. Used by Llama family. Cheaper (no mean subtraction).
- Pre-norm (GPT-2 onward, Llama): normalize before the sub-layer (x + Sublayer(Norm(x))); more stable training at depth than the original post-norm.

## Parameter counting, Llama-3-8B style (per block, d=4096, d_ff=14336, 32 Q heads/8 KV heads, d_head=128)

- Attention: W_q 4096x4096 + W_k 4096x1024 + W_v 4096x1024 + W_o 4096x4096 = 16.8M + 4.2M + 4.2M + 16.8M = ~41.9M.
- FFN (SwiGLU, 3 matrices): 3 * 4096*14336 = 176.2M.
- Per block ~218.1M; 32 blocks ~6.98B; embedding 128,256*4096 = 525.3M plus a separate output head (tie_word_embeddings false) of another 525.3M. Total ~8.03B as advertised. (Arithmetic cross-check on the released config. CORRECTED 2026-09-26: an earlier version recorded d_ff=6144 and per-block 117M, totaling ~4.3B — contradicting the 8B name; the released config's intermediate_size is 14336 and the cross-check closes at ~8.03B.)

## Position-page numbers (verified by local numpy run, deterministic)

- Sinusoidal, d_model = 4 (two pairs; speeds 10000^(-2i/d) -> pair 0: 1 rad/position, pair 1: 0.01):
  PE(pos) = [sin(pos), cos(pos), sin(0.01*pos), cos(0.01*pos)]
  pos  0 -> [ 0.000,  1.000,  0.000,  1.000]
  pos  1 -> [ 0.841,  0.540,  0.010,  1.000]
  pos  7 -> [ 0.657,  0.754,  0.070,  0.998]
  pos 50 -> [-0.262,  0.965,  0.479,  0.878]
  Fast pair cycle: 2*pi = 6.28 positions; slow pair cycle: 2*pi/0.01 = 628.3 positions.
- RoPE via code/tiny_llm.py rope(), d = 2 (one pair; theta_0 = 10000^0 = 1 rad/position), u = [1, 0], v = [0.5, 1]:
  raw dot u . v = 0.500
  dot(R_m u, R_n v) at (m, n) = (0,0), (3,3), (17,17) -> 0.500   (offset 0)
  at (1,0), (5,4), (40,39) -> 1.112   (offset -1)
  at (2,0), (9,7) -> 0.701   (offset -2)
  rope([1, 0], pos 3) = [cos 3, sin 3] = [-0.990, 0.141]
  Property shown: the rotated dot product depends only on the offset (n - m).
- Original paper, section 3.5: PE(pos+k) is a linear function of PE(pos) for fixed k
  (angle-addition identities) — the relative-structure regularity the paper points out.
  The paper also reports that learned positional embeddings performed nearly the same
  as the fixed sinusoidal ones [transformer section 3.5].

## Source IDs

- [transformer] arXiv:1706.03762
- [gpt3] arXiv:2005.14165
- [rope] arXiv:2104.09864
- [gqa] arXiv:2305.13245
- [swiglu] arXiv:2002.05202
- [rmsnorm] arXiv:1910.07467
- [layernorm] arXiv:1607.06450
- [llama3] arXiv:2407.21783
- [numpy-run] computed locally, python3 + numpy (this file records the run)
- [tinyllm] code/tiny_llm.py, deterministic; output recorded above
- [llama3-8b-config] released Meta-Llama-3-8B config.json (fetched from the NousResearch HF mirror, 2026-09-26): intermediate_size 14336, hidden_size 4096, 32 layers, 32 Q / 8 KV heads, hidden_act "silu", rope_theta 500000, tie_word_embeddings false, vocab_size 128,256, max_position_embeddings 8192
- [llama2-7b-config] released Llama-2-7B config.json (fetched from the daryl149 HF mirror, 2026-09-26): intermediate_size 11008, hidden_size 4096, 32 layers, 32 Q / 32 KV heads (no GQA), vocab_size 32,000
