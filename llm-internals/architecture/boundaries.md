# Boundary briefs (adjacent-page contracts)

For each consecutive pair: what A owns, what B owns, handoff. "Foreshadow" = may mention with term-ok escape, never define.

1. **index -> core-idea**: index owns the one-paragraph elevator model + token (minimal). core-idea owns the loop mechanics (logits/softmax/autoregressive). Handoff: "you know it predicts tokens; now see the loop and what 'the model' physically is."
2. **core-idea -> tokens**: core-idea treats tokens as opaque numbered chunks. tokens owns how text <-> IDs actually happens (BPE). Handoff: "the loop consumed token IDs; where do IDs come from?" tokens must not re-explain the loop.
3. **tokens -> embeddings**: tokens owns IDs as integers. embeddings owns IDs-as-vectors (E matrix, dot products). Handoff: "IDs are row indices; give each row meaning." tokens does not use "vector"/"embedding".
4. **embeddings -> position**: embeddings owns per-token vectors and similarity arithmetic. position owns order injection. Handoff: "vectors are a bag — order is lost." position does not re-derive dot products.
5. **position -> attention**: position owns WHY order must be encoded (permutation invariance) + RoPE mechanics. attention owns the Q/K/V mixing machinery (may USE rope by name, defined already). Handoff: "rotations gave tokens positions; now let tokens talk."
6. **attention -> multihead**: attention owns single-head mechanism + toy example + causal mask. multihead owns slicing into heads, W_o, GQA. Does not re-run the toy; refers to it. Handoff: "one head = one pattern-finder; run many in parallel."
7. **multihead -> ffn**: multihead owns cross-token mixing. ffn owns per-token transformation. Handoff: "attention moved information BETWEEN positions; now process each position alone." Multihead introduces "kv cache" as a stored-rows concept (ledger: multihead defines it); kv-cache.html later owns the arithmetic. ffn must not mention cache.
8. **ffn -> block**: ffn owns the MLP shape. block owns assembly (residual stream, norms, stacking, param counting). Handoff: "two sublayers; wire them with a residual and a norm."
9. **block -> training-objective**: block owns the forward machinery complete. training-objective owns what "better" means (loss/CE/perplexity). Handoff: "the machine runs; what number tells us it's wrong?"
10. **training-objective -> backprop**: objective owns the loss VALUE. backprop owns how it flows backward (chain rule, autograd, AdamW). Handoff: "loss is one number; gradients are its slope in every parameter."
11. **backprop -> gpus**: backprop owns the math of the step. gpus owns the hardware it runs on (bandwidth/FLOPs asymmetry, parallelism). Handoff: "one step is trillions of multiplies; where do they happen?"
12. **gpus -> scaling**: gpus owns the machine. scaling owns the budget (6ND, Chinchilla, emergent). Handoff: "given the machine, how big and how long should you train?"
13. **scaling -> post-training**: scaling owns pretraining economics. post-training owns everything after (SFT/RLHF/DPO, assistant behavior, hallucination). Handoff: "the base model predicts text; make it useful."
14. **post-training -> sampling**: post-training owns behavior shaping. sampling owns the choice rule at each step (temperature/top-p). Handoff: "the model outputs a distribution; which token do you pick?"
15. **sampling -> inference-loop**: sampling owns one step's choice. inference-loop owns the loop + phases (prefill/decode, TTFT/TPOT). Handoff: "one choice, repeated — and the two very different phases inside."
16. **inference-loop -> kv-cache**: inference-loop owns the loop shape. kv-cache owns the memory mechanism + arithmetic. Handoff: "step 5 said re-run the forward pass; here's what we refuse to recompute."
17. **kv-cache -> serving**: kv-cache owns per-sequence memory. serving owns many sequences (batching, scheduling, paged KV, flash kernels). Handoff: "one user's cache; now thousands of users' caches on one GPU."
18. **serving -> quantization**: serving owns time-multiplexing (batching/scheduling). quantization owns shrinking bytes (int8/int4). Handoff: "batching amortizes reads; quantization shrinks what's read."
19. **quantization -> speculative**: quantization owns smaller numbers. speculative owns fewer serial steps (draft/verify). Handoff: "make each step cheaper; now make fewer big steps."
20. **speculative -> context**: speculative owns speed at fixed context. context owns growing the window itself (RoPE scaling, quadratic cost). Handoff: "all of this was within 4K-128K; how far can the window go?"
21. **context -> e2e**: context owns the model-side window. e2e owns the full product path (HTTP, template, router, SSE). Handoff: "the engine is done; ship it behind an API."
22. **e2e -> finale**: e2e owns the request lifecycle. finale owns the full-circle walk + state of practice + open problems. Handoff: "you've seen every part; walk the whole loop once, then see where the field is."
23. **finale -> glossary**: finale closes the arc. glossary is reference (no new concepts).
24. **glossary -> links**: glossary is internal reference. links is external reference.

## Global no-duplication rules
- The toy attention example appears ONLY on attention.html (numbers); other pages may reference "the cat/it example" by name without re-printing matrices.
- KV byte arithmetic appears ONLY on kv-cache.html; multihead states the concept, serving states the batching consequence.
- The decode-bandwidth ceiling (146 tok/s A100) appears ONLY on inference-loop.html (as the floor) — gpus.html states the asymmetry principle, kv-cache/quantization reference it by name.
- RoPE formula appears ONLY on position.html; context.html uses its BASE (theta) without re-deriving rotations.
- Temperature/top-p example logits appear ONLY on sampling.html.
- Chat template serialization appears ONLY on post-training.html (as training format) — e2e.html shows the same tokens in the request path without re-teaching; cite forward.
