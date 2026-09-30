# Post-training: SFT, RLHF, DPO, and assistant behavior

Fact sheet for: post-training page.

## The base model is not an assistant

- A pretrained model is a next-token continuation engine: given "The capital of France is" it completes well, but given "What is the capital of France?" it may continue with more questions (that's what the corpus looks like). Base models also complete documents, not conversations.
- InstructGPT (Ouyang et al., arXiv:2203.02155, NeurIPS 2022) established the 3-stage recipe on GPT-3:
  1. SFT (supervised fine-tuning) on ~13k prompt->response pairs written by labelers.
  2. Reward model (RM) trained on ~33k prompts with human preference comparisons between pairs of model outputs (Bradley-Terry objective on which response humans preferred).
  3. RL (PPO) against the RM on ~31k prompts, with a per-token KL-divergence penalty keeping the policy close to the SFT model.
- Headline result: a 1.3B-parameter InstructGPT is preferred by humans over the 175B GPT-3 — 100x fewer parameters. 175B InstructGPT outputs are preferred over GPT-3 outputs 85 +/- 3% of the time.
- RLHF = the RM+RL stages. The RM is a learned scalar "did humans like this" function; PPO optimizes the policy to maximize it. The KL penalty prevents reward hacking / mode collapse onto RM exploits.

## DPO

- Direct Preference Optimization (Rafailov et al., arXiv:2305.18290): derives a closed-form classification loss on preference pairs that has the same optimum as RLHF's KL-constrained reward maximization — no separate RM, no PPO rollout loop. Simpler and stable; widely used (Llama 3 uses SFT + DPO + rejection sampling [+ PPO variants] [llama3 section 4.1]).

## Instruction tuning vs RLHF vs RAG vs fine-tuning (the user's confusion list)

- Instruction tuning (SFT) changes STYLE/format behavior with a few thousand to a few million examples. It is bad at adding knowledge: knowledge lives in the pretraining-scale statistics, and a small fine-tune on new facts mostly teaches the model to hallucinate them fluently (Gekhman et al., arXiv:2408.03124: fine-tuning on unknown facts degrades into hallucination as training proceeds — known facts are learned in ~50 steps, unknown facts keep loss high and push the model to fabricate).
- Adding knowledge reliably: retrieval (RAG — put the text in the context window) or continued pretraining at scale. The context window is the only "memory" the model can actually read at inference.
- Catastrophic forgetting: fine-tuning on a narrow domain degrades general behavior; mitigated by mixing in general data (a standard observation; Llama 3 mixes general data into domain-specific SFT phases [llama3]).
- RLVR (RL with verifiable rewards): post-training where the reward is a checkable signal (unit tests pass, math answer matches) instead of a learned human-preference model; the recipe behind reasoning models (see state-2026.md).

## Hallucination

- InstructGPT closed-domain QA: 21% hallucination for InstructGPT vs 41% for GPT-3 (paper section 3.6 / Figure 14-ish; open-domain 22% vs 17%).
- Structural cause: the training objective rewards plausible continuations, not true ones. The model has no mechanism to distinguish "remembered from corpus" from "statistically likely completion." RLHF adds pressure to produce confident-sounding answers (human raters reward them), which can increase hallucination for unanswerable questions (see "sycophancy" literature; e.g. Sharma et al. arXiv:2310.13548, Towards Understanding Sycophancy in Language Models).
- Mitigations that work: retrieval (grounding), sampling/decoding changes are weak, RLHF-style training to say "I don't know" (InstructGPT: behavior improves on closed domain but not open), post-hoc verification.

## Chat template

- At serving time, an assistant is the base model wrapped in a format string, e.g. `<|start_header_id|>user<|end_header_id|>...<|eot_id|>` (Llama 3 template) or ChatML `<|im_start|>user ... <|im_end|>`. The model was post-trained on this format; it is a token-level protocol, invisible in the product UI. System prompt = a fixed first turn setting behavior (persona, tools, constraints).
- The conversation history the model sees at turn k is the FULL serialized template text (all previous turns + delimiters), re-prefilled every turn (or cached) — the model is stateless between requests; "memory" is either re-sent context or external retrieval.

## Source IDs

- [instructgpt] arXiv:2203.02155
- [dpo] arXiv:2305.18290
- [llama3] arXiv:2407.21783
- [gekhman] arXiv:2408.03124 (Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?)
- [sycophancy] arXiv:2310.13548
