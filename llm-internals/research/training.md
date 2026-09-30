# Training: loss, backprop, optimizers, scaling laws

Fact sheet for: training-objective, backprop, scaling pages.

## Next-token objective

- Given a training sequence t_1..t_n, the model predicts, for every position i, a probability distribution over the vocabulary for t_{i+1}. Loss = average over positions of -log P(t_{i+1} | t_1..t_i) — cross-entropy between prediction and the actual next token.
- Cross-entropy of a distribution q against one-hot truth t: -sum_j t_j * ln q_j = -ln q_truth. A model that puts probability p on the correct next token incurs loss -ln(p).
- Reference points (verified arithmetic): -ln(0.5)=0.69, -ln(0.05)=3.00, -ln(1)=0. Uniform guess over the GPT-3 vocab: -ln(1/50,257)=10.83 nats. So a loss of 10.8 = knowing nothing; loss 2.0 = e^-2 ~ 13.5% on the correct token per position on average.
- Perplexity = exp(loss): the effective "number of choices" the model is deciding among. PPL 50,257 = uniform. PPL 20 = loss 3.0.
- Pretraining corpus: web crawl, code, books (Llama 3: ~15T tokens [llama3]; GPT-3: ~300B filtered CommonCrawl + books + Wikipedia [gpt3 section 2.2]).

## Backpropagation

- The loss is a composition of the forward pass's elementary ops (matmul, add, softmax, ...). The chain rule gives dL/d(parent) = sum over children dL/d(child) * d(child)/d(parent). Reverse-mode autodiff = one backward sweep from the loss computes the gradient of L with respect to EVERY parameter in one pass, at ~2-3x the forward cost (for the matmul-dominated transformer).
- Every intermediate activation from the forward pass must be stored for the backward pass (needed as multipliers in the chain rule) — this is why training is memory-hungry and why inference can skip storing.
- Local gradient examples: y = xW has dL/dW = x^T dL/dy and dL/dx = dL/dy W^T. Softmax+CE combined: dL/dlogits = p - onehot(t) (the famous "probability minus truth").
- Gradient = the vector of partial derivatives dL/d(param) for all params, stacked. Descent rule: param -= lr * grad (SGD). AdamW (Loshchilov & Hutter, arXiv:1711.05101): keep running averages m (1st moment) and v (2nd moment) of the gradient, normalize step by sqrt(v): update ~ lr * m / (sqrt(v)+eps), plus decoupled weight decay. It makes the effective step size ~uniform across parameters, which works far better for deep nets.
- Learning rate schedules: warmup (linear ramp over first ~0.1-1% of steps) then cosine decay to ~10% of peak. GPT-3 175B peak lr 0.6e-4 [gpt3 Table 2.1]. Llama 3 8B peak lr 3e-4, final 3e-5 [llama3 Table 4].
- Batch size in tokens: GPT-3 175B 3.2M tokens/step [gpt3 Table 2.1]; Llama 3 global batch 16M tokens in later phases [llama3].
- One optimizer step = forward on a batch (loss) + backward (gradients) + update. Training = millions of these steps.
- Verified in tiny_llm.py stage 4: hand-written backprop for the toy block (cross-entropy, attention, RoPE, GELU, RMSNorm, residuals) matches central finite differences (h=1e-5, 3 random entries per tensor) with worst relative error 4.79e-08 across all 13 parameter tensors; one SGD step at lr 0.2 then drops the toy loss from 5.198 to 1.629.

## FLOPs accounting

- Forward pass of a dense transformer on n tokens: ~2*n*N FLOPs (N params; 2 FLOPs per multiply-add; embedding lookup and softmax are lower order). Backward ~2x forward. So one training step on B tokens: ~6*B*N FLOPs; total training compute C = 6*N*D where D = total tokens processed. Reference: Kaplan et al. arXiv:2001.08361 (C = 6ND) and Hoffmann et al. arXiv:2203.15556 use the same.
- Verified arithmetic: GPT-3: 6 * 175e9 * 300e9 = 3.15e23 FLOPs (paper reports 3.14e23). Llama 3 405B: 6 * 405e9 * 15.6e12 = 3.79e25 (paper reports 3.8e25). Chinchilla: 6 * 70e9 * 1.4e12 = 5.9e23.

## Scaling laws

- Kaplan et al. 2020 (arXiv:2001.08361): loss falls as a power law in parameters, data, and compute, over many orders of magnitude; early guidance favored growing parameters faster than data.
- Chinchilla (Hoffmann et al., arXiv:2203.15556): for a FIXED compute budget C, the loss-minimizing choice grows parameters and tokens in equal proportion: N_opt proportional to C^0.5, D_opt proportional to C^0.5 (their Approach 3 fit a=b=0.5). Rule of thumb ~20 tokens per parameter. Chinchilla 70B trained on 1.4T tokens (same compute as Gopher 280B) beats Gopher on every benchmark they report (MMLU 67.5% vs 60.0%).
- GPT-3 (300B tokens / 175B params = 1.7 tok/param) and Gopher are compute-UNoptimal by this measure; Llama 3 (~15T / 8B = 1,875 tok/param) deliberately exceeds Chinchilla-optimal ("overtraining") because inference cost dominates total cost for a widely-served model, and smaller models are cheaper to serve. [llama3 for 15T; chinchilla for 20 tok/param rule]

## What training actually costs

- DeepSeek-V3: 2.788M H800 GPU-hours for 14.8T tokens [dsv3]. At 989 TFLOPS dense BF16 per H800 (H100-class) that's ~2.788e6 h * 3600 s * 989e12 FLOP/s = 9.9e24 FLOPs of hardware peak, i.e. ~37% MFU (matches paper's ~37% figure incl. MTP overhead).
- Loss goes down smoothly; capabilities arrive in jumps (emergent behaviors — e.g. in-context learning at scale [gpt3 section 3]).

## Data as code

- The model's "knowledge" is parameterized memory of patterns in the corpus. Nothing is retrieved at inference: whatever the corpus contained, statistically, is what the weights encode. This is why the knowledge cutoff exists and why hallucination is structural (see post-training.md).

## Source IDs

- [gpt3] arXiv:2005.14165
- [llama3] arXiv:2407.21783
- [kaplan] arXiv:2001.08361
- [chinchilla] arXiv:2203.15556
- [adamw] arXiv:1711.05101
- [dsv3] arXiv:2412.19437
- [tinyllm] code/tiny_llm.py stage 4 (deterministic run; this file records the output)
