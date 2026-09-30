# GPUs, memory, and the arithmetic of inference

Fact sheet for: gpus, kv-cache, inference-loop, quantization pages. All arithmetic on this sheet verified by local computation (see bash runs in repo history).

## GPU specs (datasheet-verified)

- NVIDIA A100 80GB SXM: 80 GB HBM2e, 2,039 GB/s memory bandwidth; FP16/BF16 tensor-core 312 TFLOPS dense (624 with sparsity). (A100 40GB: 1,555 GB/s.) Source: NVIDIA A100 datasheet.
- NVIDIA H100 SXM: 80 GB HBM3 (HBM2e variant 94GB), 3.35 TB/s; BF16 tensor 1,979 TFLOPS with 2:4 sparsity (~990 dense). Source: NVIDIA H100 page/datasheet.
- Key asymmetry: arithmetic throughput (TFLOPS) is ~300-1000x the rate at which you can move weights from HBM (GB/s). A multiply-add costs ~1/312e12 s; loading one BF16 weight ~1/2e12 s -> compute is ~150-600x cheaper per element than a memory trip.

## Decode (one token at a time) is memory-bound

- Generating one token must read every active weight at least once: bytes = 2*N (BF16). Time >= 2*N / bandwidth. Tokens/s ceiling = bandwidth / (2*N).
- Verified numbers: 7B model fp16 = 13.04 GiB (14e9 bytes). On A100 80GB: 14e9 / 2.039e12 = 6.87 ms/token -> 146 tok/s ceiling at batch 1. On H100: 14e9 / 3.35e12 = 4.18 ms -> 239 tok/s. A 70B model fp16 = 130.4 GiB — does not fit on one 80GB GPU at all.
- Real deployments reach ~60-80% of these ceilings; vLLM-benchmarks in vLLM docs show ~50-150 tok/s for 7B models on A100-class hardware.
- Corollary: at batch 1, arithmetic sits ~idle (a 7B model forward = ~1.4e10 FLOPs on 14 GB read -> arithmetic intensity ~1 FLOP/byte vs machine balance ~150-600). This is why quantization (halve the bytes -> double the ceiling) and batching (amortize one weight read over many sequences) both work.

## Prefill (whole prompt at once) is compute-bound

- FLOPs for one forward pass over p tokens ~ 2*p*N (the 6ND accounting with no backward). The same weight bytes are read, but now amortized over p positions.
- Verified example: 6.7B model, 1,000-token prompt: 2 * 6.7e9 * 1000 = 1.34e13 FLOPs. On H100 at 50% MFU of 989 TFLOPS: 1.34e13 / (4.94e14) = 27 ms — vs. 4 ms of pure weight reading. Compute dominates once p is in the hundreds+.
- TTFT (time to first token) = prefill time; TPOT (time per output token) = decode step time. A 1,000-token prompt with 200 output tokens on a 7B/A100: TTFT ~ 30-60 ms + 200 * ~7 ms = ~1.4 s dominated by decode.

## KV cache memory

- During decode, K and V for all previous positions are needed; caching them avoids recomputing them (see inference.md for the mechanism).
- Bytes = 2 (K and V) * layers * kv_heads * d_head * ctx * dtype_bytes.
- Verified: Llama 2 7B (32 layers, 32 KV heads, 128): 2 GiB at ctx 4,096 fp16. Llama 3 8B (32 layers, 8 KV heads, 128): 131,072 bytes = 128 KiB per token; 1 GiB at 8K; 16 GiB at 128K — per sequence, roughly the model's own fp16 weight size (8.03e9 params x 2 B = 16.06 GB = ~15 GiB; cache = 2^34 B = 16 GiB, ~1.07x). CORRECTED 2026-09-26: earlier gloss said "twice the model's own weights" — wrong; the arithmetic says roughly equal.
- GQA motivation: cutting KV heads 32 -> 8 cuts cache 4x (Llama 3 vs Llama 2 7B).
- Serving consequence: batch size is capped by free VRAM after weights (vLLM paper: KV cache up to 1.7 GB for a single LLaMA-13B sequence; existing systems wasted 60-80% of reserved cache memory via fragmentation + over-reservation [vllm]).

## Distributed training/inference

- Model does not fit -> parallelism axes: tensor parallel (split each matmul across GPUs; NVLink needed for the per-layer all-reduces), pipeline parallel (split layers into stages; micro-batches keep stages busy), data parallel (replicate model, different batches, gradient all-reduce — ZeRO/FSDP shards optimizer state+params instead of replicating).
- Gradient checkpointing (activation recomputation): don't store activations in forward; recompute in backward — trades ~1.33x compute for a large activation-memory cut (Chen et al. arXiv:1604.06174 "Training Deep Nets with Sublinear Memory Cost").
- Llama 3 405B trained with 16K H100s, 4D parallel (DP + PP + TP + CP — context parallel for sequences) [llama3 section 3.3.2].
- Mixed precision: forward/backward in BF16, master weights + optimizer moments in FP32 — memory per param: 2 (bf16 weight) + 2 (bf16 grad) + 4+4+4 (fp32 master + Adam m + v) = 16 bytes/param. 7B model -> ~112 GB optimizer-inclusive; the weights alone are only 14 GB. (Standard accounting; matches ZeRO paper arXiv:1910.02054.)

## Source IDs

- [a100-ds] NVIDIA A100 datasheet (nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-us-nvidia-1758950-r4-web.pdf)
- [h100-ds] NVIDIA H100 datasheet page
- [vllm] arXiv:2309.06180
- [llama3] arXiv:2407.21783
- [checkpointing] arXiv:1604.06174
- [zero] arXiv:1910.02054
- Local verified arithmetic: recorded in this sheet's history (bash runs).
