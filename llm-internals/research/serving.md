# Serving: batching, continuous batching, PagedAttention, FlashAttention

Fact sheet for: serving page (and gpus page cross-links).

## Static batching and its waste

- Naive serving: collect a batch of requests, run them to completion, then start the next batch. Requests finish at different times; finished slots idle until the WHOLE batch finishes. Early systems (FasterTransformer, early Triton) worked this way.
- Orca (Yu et al., OSDI 2022, usenix.org/system/files/osdi22-yu.pdf) introduced:
  - Iteration-level scheduling: the scheduler runs at every decode iteration (every token step), admitting new requests and evicting finished ones per-step. "Continuous batching" is the vLLM name for this.
  - Selective batching: batch the ops that have compatible shapes (embedding lookup, FFN, LM head — elementwise/matmul over tokens), run attention per-request (each request has a different KV length).
  - Result: 36.9x throughput vs FasterTransformer on GPT-3 175B (1.1-9.1x across settings; 36.9x headline).
  - Orca names the two phases "initiation phase" (prefill) and "iteration phase" (decode).

## Why batching helps (ties to gpus.md)

- At batch 1, decode has arithmetic intensity ~1 FLOP per byte read vs a machine balance of ~150-600 FLOPs per byte: the GPU starves waiting for weights to stream from HBM.
- Batch B requests into one decode step: the same 2*N weight bytes are read ONCE and used for B tokens — FLOPs per byte multiplied by B. Throughput rises nearly linearly in B while per-token latency stays ~flat, until the GPU becomes compute-bound.
- Consequence: serving systems continuously fill the batch; the scheduler's job is keeping the GPU's memory system busy without exceeding VRAM (weights + KV caches of all in-flight requests).

## PagedAttention / vLLM

- Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention", SOSP 2023, arXiv:2309.06180.
- Problem: KV cache per request is contiguous and reserved for the max possible length; internal + external fragmentation wastes 60-80% of cache memory in existing systems. A single sequence's KV cache for LLaMA-13B can reach 1.7 GB.
- Solution: partition the cache into fixed-size blocks (vLLM default block size = 16 tokens), store blocks anywhere in VRAM, map logical sequence -> physical blocks in a page table (OS virtual memory analogy: pages, page tables, on-demand allocation).
- Waste drops below 4% of total memory. Enables prefix sharing (copy-on-write for shared prompt blocks, e.g. system prompt reused across requests, parallel sampling / beam search sharing the prompt's blocks).
- Results: 2-4x throughput vs FasterTransformer and Orca (their Figure/abstract), 2.2-2.5x over Orca alone at the same latency; latency 2-4x lower at the same throughput vs SOTA (their Table/Evals).
- vLLM today is the standard open-source engine (ubiquitous in deployment stacks); SGLang/RadixAttention adds prefix-tree caching of KV across requests.

## FlashAttention (the kernel trick inside every step)

- Dao et al., "FlashAttention: Fast and Memory-Efficient Exact Attention", arXiv:2205.14135 (NeurIPS 2022).
- Problem: naive attention materializes the n x n score matrix in HBM (n^2 memory traffic); attention is HBM-bound, not FLOP-bound.
- Solution: tile the computation — load Q/K/V blocks into on-chip SRAM, compute partial softmax results per tile, rescale as more K/V tiles stream in (online softmax / flash style). The n x n matrix is never fully materialized in HBM. EXACT same math (not an approximation).
- IO complexity: Theta(N^2 * d^2 / M) HBM accesses vs Theta(Nd + N^2) for standard attention (M = SRAM size).
- Numbers: up to 7.6x faster attention alone (GPT-2); 3x end-to-end GPT-2 (seq 1K); 15% end-to-end BERT-large; 2.4x on long sequences (GPT-2 4K); memory grows LINEARLY in sequence length instead of quadratically (enables 64K+ training); up to 20x memory savings at 64K. FlashAttention-2/3 refine scheduling further.
- Relevance chain: FlashAttention speeds attention (prefill, long context) -> PagedAttention manages KV between steps -> continuous batching fills the GPU across steps.

## TTFT vs TPOT in production

- TTFT (time to first token) = queueing + prefill of the prompt. TPOT = per-token decode time (memory-bandwidth floor / batch pressure). Throughput = tokens/sec across all concurrent requests.
- Tension: more batch = more throughput but longer TTFT (queueing) and some TPOT growth (cache reads grow with batch). Chunked prefill (vLLM) splits a huge prompt's prefill across steps to keep decode latency smooth.
- OpenAI exposes `stream: true` + usage fields (`prompt_tokens` / `completion_tokens`) — completion tokens priced higher per token than prompt tokens (pricing page), reflecting that they are produced serially, one full memory sweep each.

## Source IDs

- [orca] usenix.org/system/files/osdi22-yu.pdf (OSDI 2022)
- [vllm] arXiv:2309.06180 (SOSP 2023)
- [flash] arXiv:2205.14135
- [openai-api] platform.openai.com/docs (streaming, usage)
