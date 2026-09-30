# Quantization: int8/int4, outliers, GPTQ, AWQ

Fact sheet for: quantization page.

## Core mechanism

- Quantization to b bits: represent a weight vector w by scale s and integer grid q in {-(2^(b-1)) .. 2^(b-1)-1} (signed) via q = round(w / s), dequantize w_hat = s * q. With per-group scales (group size g, e.g. 128), each group of g consecutive weights shares one scale — smaller dynamic range per group, smaller error.
- fp16 -> int8 halves bytes (2 -> 1); int4 is 4x smaller than fp16. Decode is memory-bandwidth-bound (gpus.md), so bytes ~ directly set the token-rate ceiling: int4 roughly quadruples the ceiling vs fp16, IF kernels dequantize-on-the-fly during the weight sweep.
- Error is proportional to grid coarseness; uniform rounding noise is mostly harmless because matmels sum millions of terms (error averages out) — EXCEPT for a small set of salient channels (below).

## Outliers (why naive int8 breaks at scale)

- Dettmers et al., "LLM.int8()", arXiv:2208.07339 (NeurIPS 2022):
  - Emergent, systematic outlier features appear around 6.7B parameters (a "phase transition"); these are ~0.1% of hidden dimensions but with outsized magnitudes, concentrated in ~6 dimensions in a 6.7B model.
  - Zeroing just those dims inflates perplexity by 600-1000%; quantizing them to int8 destroys quality.
  - Fix (mixed-precision decomposition): outlier dimensions computed in fp16, everything else int8. int8 inference for OPT-175B/BLOOM-176B with no degradation; ~2x memory reduction (BLOOM-176B: 1.96x), enabling 175B-scale on fewer GPUs.

## Weight-only PTQ methods (GPTQ, AWQ)

- GPTQ (Frantar et al., arXiv:2210.17323, ICLR 2023): one-shot post-training quantization of a trained model — no retraining. Uses approximate second-order (Hessian) information (Optimal Brain Surgeon lineage) to decide quantization order and error compensation: quantizing weight w_j distributes its error to not-yet-quantized weights via the Hessian inverse. 175B model quantized in ~4 GPU hours; 3-4 bits with negligible degradation (2-bit needs group size 128 + activation-order heuristics and still hurts some). End-to-end inference 3.25x faster on A100 and 4.5x on A6000 (OPT-175B) — the speedup comes from reduced memory movement, not more FLOPs.
- AWQ (Lin et al., arXiv:2306.00978, MLsys 2024): observation — 0.1%-1% of weight CHANNELS are salient (chosen by ACTIVATION magnitude, not weight magnitude; big activations flow through them). Protect them via per-channel scaling: pre-scale salient channels up before int4 quantization (reducing their relative rounding error), absorb the scaling into the corresponding activation scale. No backprop, no quantizing activations, no reconstruction loss. Preserves generalization across domains (e.g., GSM8K code/math) that would break under naive RTN or even some methods with fine-tuning. Figure 1: OPT-6.7B INT4-g128 with 1% channels in fp16 cuts WikiText2 perplexity from 43.2 (RTN+error) to 13.0 (~fp16-level ~13.09). 4-bit AWQ fits a 70B model in a single 48GB GPU; ~3x faster than HF fp16 inference with proper kernels.

## What is quantized in practice

- Weights (W4A16: weights int4, activations fp16) — the common production recipe (GPTQ/AWQ int4-g128, "Q4_K_M" GGUF variants locally).
- KV cache (int8 halves cache bytes; e.g. vLLM `kv_cache_dtype="fp8"`).
- Full-pipeline int8 (W8A8) for prefill-heavy compute-bound workloads.
- Training stays bf16/fp32 (see gpus.md mixed-precision accounting); quantization is a POST-training serving optimization.

## Caveats

- Quantization error interacts with task: code generation and math degrade earlier than chat (AWQ paper's generalization point).
- Perplexity is a weak proxy; evaluate on real downstream tasks before shipping 4-bit.
- The "quantize weights to make decode faster" lever only works because decode is bandwidth-bound; a compute-bound phase (large-batch decode, long prefill) gains much less.

## Source IDs

- [llmint8] arXiv:2208.07339
- [gptq] arXiv:2210.17323
- [awq] arXiv:2306.00978
