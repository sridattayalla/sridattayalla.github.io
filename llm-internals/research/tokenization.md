# Tokenization facts (verified)

Fact sheet for: tokens, inference-loop, e2e.

## BPE mechanics

- Original BPE for NMT: Sennrich et al., "Neural Machine Translation of Rare Words with Subword Units", arXiv:1608.07816 (2016). Algorithm: start from characters (or bytes), repeatedly merge the most frequent adjacent pair; each merge becomes a vocabulary entry.
- GPT-2 introduces byte-level BPE (paper: "Language Models are Unsupervised Multitask Learners", section 2.2): the base alphabet is the 256 possible bytes, so any input string is representable — no UNK token. ~50,000 merges learned on WebText.
- Special tokens: GPT-2 has `<|endoftext|>` (1 special token). Later models add more (chat/control tokens).

## Verified with tiktoken (run locally, cl100k_base / gpt2 encodings)

- cl100k_base vocab size: 100,277. gpt2 (r50k) vocab size: 50,257.
- "strawberry" in cl100k_base: [496, 675, 15717] = "str" + "aw" + "berry" (3 tokens; r-counts per piece: 1, 0, 2).
- "strawberry" in gpt2 (r50k): [301, 1831, 8396] = "st" + "raw" + "berry" (3 tokens).
- "The cat sat on the" in cl100k: ["The", " cat", " sat", " on", " the"] — 5 tokens; note the leading space belongs to the token (bytes are merged with preceding whitespace; this is why " token" and "token" are different tokens).
- "15,000" in cl100k: ["15", ",", "000"] — 3 tokens (models often miscount digits for the same reason as letters).
- Single letter "r" is its own token (id 81) — letters exist as fallback byte tokens but common words are merged, so the model never "sees" the letters of a merged word unless asked char-by-char.

## Toy BPE, verified by running tiny_llm.py (stage 1)

- Corpus: "the cat sat on the mat. the cat ate the rat. the rat ate the cat." Start from characters plus a '</w>' word-end marker; learn 12 merges, most frequent adjacent pair first: 1. a+t -> at; 2. e+</w> -> e</w>; 3. t+h -> th; 4. th+e</w> -> the</w>; 5. at+</w> -> at</w>; 6. at+. -> at.; 7. at.+</w> -> at.</w>; 8. c+at</w> -> cat</w>; 9. at+e</w> -> ate</w>; 10. s+at</w> -> sat</w>; 11. o+n -> on; 12. on+</w> -> on</w>.
- Vocabulary: 24 tokens = 12 initial symbols (11 distinct characters + '</w>') + 12 merges.
- Encode "the cat ate the rat." -> ids [15, 19, 20, 15, 9, 18] = the</w>, cat</w>, ate</w>, the</w>, r, at.</w>; decode round-trips exactly.
- Teaching point: 'the' is one piece, but 'rat.' is two (r + at.</w>) — merges glued 'at' to the period, so 'rat</w>' never forms. The same greedy gluing is why real tokenizers split text in unintuitive places (digits, letters after punctuation).

## Why "count the r's in strawberry" fails

- The model's input is token IDs, not characters. "strawberry" arrives as 3 token IDs (cl100k). Counting letters requires either having seen the letter counts during training (memorization), decomposing into single-character tokens (e.g., prompting with separators), or using a tool (code execution). The failure is a data-representation issue at the tokenizer boundary, not a reasoning failure inside the network.
- Provenance: token IDs verified with tiktoken; explanation is standard, consistent with Sennrich 1608.07816 + GPT-2 paper.

## Vocabulary sizes in practice

- GPT-2/GPT-3: 50,257. Llama 2: 32,000. Llama 3: 128,000 (paper Table 3; released tokenizer file 128,256). cl100k (GPT-3.5/4 era): ~100k.
- Compression: Llama 3 tokenizer 3.94 chars/token on English sample vs 3.17 for Llama 2 (arXiv:2407.21783).
- English text averages roughly 4 characters per token for modern 100k+ vocabs (4.0 chars/token -> ~0.25 tokens/char; a 750-word English essay is ~1000 tokens). [Derived: 3.94 chars/token Llama 3 on English sample.]

## Token ID facts for pages

- Token IDs are just indices into the vocabulary array: integer -> byte-string lookup. Same ID space is used for input and output (the model emits a distribution over the same vocab).
- Embedding row count = vocab size; each vocab entry gets a learned vector. (See components.md for parameter math.)

## Source IDs

- [bpe] arXiv:1608.07816
- [gpt2] Radford et al. 2019
- [tiktoken] verified by running tiktoken 100k/50k encodings locally (this file records the runs)
- [llama3] arXiv:2407.21783
- [tinyllm] code/tiny_llm.py stage 1 (deterministic run; this file records the output)
