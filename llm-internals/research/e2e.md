# End-to-end: one HTTPS request -> streaming tokens

Fact sheet for: e2e page. Procedural spine; provenance where numbers appear.

## The journey (request lifecycle in a hosted API like OpenAI's)

1. Client builds a messages array ([{role: "system"...}, {role: "user", ...}]) and POSTs /v1/chat/completions with `stream: true` (OpenAI Chat Completions API shape; platform.openai.com/docs/api-reference/chat).
2. TLS/HTTP reach the provider's frontend; auth; rate limiting.
3. Router/scheduler: pick a serving instance (or shard-group) with room — accounting VRAM for weights + KV cache of in-flight requests (this is the vLLM/SGLang-class engine's scheduler loop; see serving.md).
4. Chat template: the messages array is serialized into ONE token string with special delimiters (Llama 3 example: `<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n`). The model only ever sees this token stream — roles are delimiters, nothing more.
5. Tokenize -> prefill (compute-bound, fills KV cache) -> first sampled token -> TTFT.
6. Decode loop: sample token, append, forward, repeat (memory-bound; see inference-loop/kv-cache). Sampling params (temperature, top_p) applied at each step.
7. Streaming back: the server emits Server-Sent Events over the same HTTP response: `Content-Type: text/event-stream`, each event `data: {json}\n\n` containing a delta with a fragment of text (OpenAI streaming format), terminated with `data:  (the two-terminal-event convention). The client renders deltas as they arrive. Non-streaming mode: server buffers everything and returns one JSON.
8. Detokenization on the fly: bytes accumulate; a UTF-8 char split across token boundaries is buffered until complete (tiktoken incremental decoding; documented in OpenAI streaming behavior).
9. Stop: EOS/special token, max_tokens, or client disconnect (abort). Usage accounting: prompt_tokens vs completion_tokens.

## What the user perceives, mapped to machinery

- "It started typing after ~1s" = queueing + prefill (TTFT). "It types ~60 tok/s" = decode rate (bandwidth floor / batch pressure / TPOT).
- "It forgot what we said yesterday" = the model is stateless between requests; yesterday's turns are re-sent (re-cached) as context each request, or are simply absent.
- "It knows about X but not Y" = X was in the pretraining corpus before the knowledge cutoff; Y wasn't — and nothing at inference reads a database unless the app implements retrieval (RAG) or tools.

## Non-claims to avoid

- Use the GPT-4o price ONLY as a dated structural example: input $2.50 vs output $10.00 per 1M tokens (4x) — verified on developers.openai.com pricing/model pages; note prices change, the asymmetry is the point.
- Do not claim specific provider internal architectures; describe the engine class (vLLM-like scheduler, PagedAttention-style KV management) with "class of system" hedging, citing vLLM as the reference implementation.

## Source IDs

- [openai-api] platform.openai.com/docs/api-reference/chat (messages array, stream:true, SSE deltas, usage fields)
- [openai-pricing] openai.com/api/pricing (completion > prompt per-token price)
- [llama3] arXiv:2407.21783 (chat template tokens, eot conventions) + Meta's llama recipes repo
- [mdn-sse] developer.mozilla.org/docs/Web/API/Server-sent_events (format: `data:` lines, \n\n framing, text/event-stream)
- [tiktoken] github.com/openai/tiktoken (incremental detokenization note in README)
