# Environment and verification method

Fact sheet for: every page. This book's central evidence discipline is stated here.

## Toolchain (verified 2026-09-26)

- rustc 1.98.1 (48a229cea 2026-09-01), installed via rustup, edition 2021 for all
  snippets. Every Rust snippet that claims to compile or to fail DOES so under
  this exact compiler; the per-snippet results live in `tools/verify-report.json`,
  produced by `tools/verify.py` (extraction from HTML + rustc run + report).
- gcc 11.4.0 (Ubuntu), clang 14.0.0 for the C failure-anatomy programs:
  - AddressSanitizer runs: `gcc -g -fsanitize=address` / `clang -g -fsanitize=address`;
    stack-use-after-return additionally needs `ASAN_OPTIONS=detect_stack_use_after_return=1`
    and was captured with clang (gcc 11 folds the dangling return into a null deref).
    Measured 2026-09-26: the clang 14 ASan runtime segfaults with no report under
    full ASLR on this kernel (roughly a third of runs at -O0, fake-stack option
    on or off), so the site's verification runner executes ASan binaries under
    `setarch $(uname -m) -R`, exactly like TSan. Report text is unaffected.
  - ThreadSanitizer run: `gcc -g -fsanitize=thread -lpthread`, executed under
    `setarch $(uname -m) -R` (TSan on this kernel needs ASLR disabled to map its
    shadow memory; the report itself is genuine TSan output).

## Method

- Compiler behavior claims (error codes, exact error text, panic text, program
  output, layout sizes, Send/Sync impl matrix) are all quoted from captured runs
  in this research directory; the chapters quote them with minor elisions marked
  by `...`. Where the book prints an error, the snippet was compiled as shown
  (whole file, `rustc --edition 2021`); runtime panics were executed, not inferred.
- Docs/RFC/history claims carry their canonical URL in the per-topic sheets; the
  links.html page of the site is generated from those sheets.

## Local run index (which sheet holds which capture)

| Capture | Sheet |
|---|---|
| drop order, E0382, E0384, E0204, Copy semantics | research/ownership.md |
| E0502, E0499, E0596, E0506, NLL pass case | research/borrowing.md |
| E0106, E0597, E0515, E0716, elision behavior | research/lifetimes.md |
| String/&str/Vec/&[T]/Box sizes, E0072, Box fix | research/memory-layout.md |
| Rc counts, cycle leak, Weak rescue, Rc E0277 | research/shared-ownership.md |
| Cell demo, RefCell panic, RefCell ok, mutex poison | research/interior-mutability.md |
| Send/Sync assertion matrix, Arc<Cell> E0277, data race C | research/send-sync.md |
| split_at_mut safe-fail + unsafe impl, Pin demo, get_mut E0599 | research/unsafe-pin.md |
| Result/? run, catch_unwind run, panic text | research/error-handling.md |
| fat pointers, monomorph, E0117 | research/traits.md |
| cache + thread pool programs | research/capstone.md |
| C sanitizer reports (ASan/TSan), lost updates | research/c-failures.md |

## Source IDs

- [rustc-1.98.1] local rustc 1.98.1 runs, recorded in this repo (tools/verify-report.json)
- [gcc-11.4] local gcc 11.4.0 + sanitizer runs, recorded in this sheet's captures
