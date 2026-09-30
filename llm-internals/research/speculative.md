# Speculative decoding

Fact sheet for: speculative page.

## Core scheme (Leviathan et al., ICML 2023, PMLR v202; concurrent: Chen et al., arXiv:2302.01318)

- Players: draft model q (small, e.g. 100x fewer params — cheap per token, can be run serially) and target model p (the real model).
- Round: (1) draft generates gamma (say 4-8) tokens autoregressively; (2) the TARGET runs ONE forward pass over prompt+draft-tokens and outputs p(x) for every position — the same parallel scoring that prefill does; (3) accept tokens left-to-right: token i accepted with probability min(1, p(x_i)/q(x_i)) (rejection sampling); on the first rejection, resample that token from the normalized residual distribution norm(max(0, p - q)).
- Guarantee: the output distribution is EXACTLY the target's — provably lossless (their Theorem 1; "accelerated sampling from the target distribution").
- Expected accepted tokens per round: (1 - alpha^(gamma+1)) / (1 - alpha) where alpha = draft acceptance rate.
- Cost model: round time = gamma * T_draft (serial, small) + 1 * T_target (parallel). Net win requires draft fast enough and alpha high enough; alpha degrades with temperature.

## Verified results

- Leviathan et al.: T5-XXL (11B) 2-3x end-to-end with T5-small/T5-base drafts; their best spec: 3.4x at temperature 0 with the T5-small draft (alpha ~ 0.75); 2.6x at temperature 1.0. (Abstract claims 2-3x; table detail as stated.)
- The gain direction matters more than the numbers: a 100x-smaller draft + one parallel verification beat 100 serial target passes whenever alpha is decent, because decode is memory-bound (gpus.md): serial small-model steps are cheap, and verification reuses ONE target weight-sweep for many candidate tokens.

## Why it works — the memory-bound connection

- Decode at batch 1 uses ~1 FLOP per byte; the target's one verification pass over gamma+1 tokens has gamma+1x the arithmetic intensity. The GPU was starving; speculation feeds it compute it can absorb nearly for free.
- Breaks when the GPU is already compute-bound: at high batch (many concurrent requests) the verification FLOPs compete with real traffic — speculative decoding is a batch-1/low-batch optimization. Also weaker at high temperature (alpha drops) and for tasks where a small draft can't track the target.

## Lineage / variants

- Self-speculative: use the same model with early-exit or skipped layers as the draft.
- Medusa (Cai et al., arXiv:2401.10774): extra decode heads predict several future tokens in one pass; verify in parallel with a tree of candidates.
- EAGLE / EAGLE-2 / EAGLE-3 (Li et al., arXiv:2501.15069, 2504.17355, 2503.01840): draft at the FEATURE level — a light head predicts the target's hidden states (not token IDs), then tokens; reuses target representations, high acceptance (EAGLE-3: 3-6.5x speedups, 6.5x headline). EAGLE-3 shipped in vLLM 0.8.5+ (speculative decoding is a config flag in modern serving engines: `speculative_config`).

## Source IDs

- [leviathan] PMLR v202 (Leviathan, Kalman, Matias, "Fast Inference from Transformers via Speculative Decoding", ICML 2023)
- [chen] arXiv:2302.01318
- [medusa] arXiv:2401.10774
- [eagle3] arXiv:2503.01840
- [vllm-docs] docs.vllm.ai (speculative decoding support, EAGLE-3 since 0.8.5)
