# Design history — verified RFCs, decisions, and quotes

Fact sheet for: founding-constraint, ownership, borrowing, rc-arc,
send-sync, unsafe, pin, error-handling, traits pages (the "why decided"
claims). Every item below was verified against the actual primary text.

## RFCs, verified (number — exact title — URL — status)

- RFC 0019 "opt-in builtin traits" —
  https://rust-lang.github.io/rfcs/0019-opt-in-builtin-traits.html
  Made moves the default: "This means that structs and enums would *move
  by default* unless their type is explicitly declared to be `Copy`."
  Also introduced the auto-trait mechanism (Send/Sync derive structurally,
  with unsafe impl opt-out). THE Copy-vs-move and marker-trait design
  record.
- RFC 0243 "trait-based-exception-handling" —
  https://rust-lang.github.io/rfcs/0243-trait-based-exception-handling.html
  The ? operator. "Requiring an explicit ? operator to propagate
  exceptions strikes a very pleasing balance between completely automatic
  exception propagation, which most languages have, and completely manual
  propagation."
- RFC 0230 "remove the runtime system" (title slug: remove-runtime) —
  https://rust-lang.github.io/rfcs/0230-remove-runtime.html
  "This RFC proposes to remove the *runtime system* that is currently
  part of the standard library"; history: "Rust has gradually migrated
  from a 'green' threading model toward a native threading model...
  Initially, Rust supported only the green threading model. Later, native
  threading was added and ultimately became the default." Decision
  minutes: rust-lang/meeting-minutes 2014-09-16 (aturon: "relegating
  green threading to an external crate"). Pre-1.0 Rust had a green-thread
  runtime; removing it is why "no runtime" is true today.
- RFC 1023 "rebalancing coherence" —
  https://rust-lang.github.io/rfcs/1023-rebalancing-coherence.html
- RFC 1066 "safe-mem-forget" —
  https://rust-lang.github.io/rfcs/1066-safe-mem-forget.html
  The leakpocalypse resolution: "It has never been a guarantee of Rust
  that destructors for a type will run." mem::forget became safe;
  thread::scoped was removed (returned 1.63 as thread::scope with
  JoinHandle guards).
- RFC 1236 "stabilize-catch-panic" —
  https://rust-lang.github.io/rfcs/1236-stabilize-catch-panic.html
  Established catch_panic in std (initially std::panic::recover,
  stabilized as catch_unwind).
- RFC 2094 "non-lexical lifetimes" —
  https://rust-lang.github.io/rfcs/2094-nll.html
  "Lifetimes in Rust today are quite a bit more flexible than scopes (if
  not as flexible as we might like, hence this RFC)". Shipped as the
  Rust 2018 borrow checker.
- RFC 2113 "dyn-trait-syntax" —
  https://rust-lang.github.io/rfcs/2113-dyn-trait-syntax.html
  "Introduce a new `dyn Trait` syntax for trait objects using a
  contextual `dyn` keyword, and deprecate 'bare trait' syntax".
- RFC 2349 "pin" —
  https://rust-lang.github.io/rfcs/2349-pin.html
  "A common motivation for this is when a struct contains a pointer into
  its own representation — moving that struct would invalidate that
  pointer. This use case has become especially important recently with
  work on generators." Goal: "provide a reference type where the referent
  is guaranteed to never move before being dropped."
- RFC 2451 "re-rebalancing-coherence" —
  https://rust-lang.github.io/rfcs/2451-re-rebalancing-coherence.html
- RFC 2945 "C-unwind ABI" —
  https://rust-lang.github.io/rfcs/2945-c-unwind-abi.html
  "Prior to this RFC, any unwinding operation that crossed an extern "C"
  boundary ... caused undefined behavior." Now: panic=unwind + extern "C"
  -> abort (defined); foreign unwinding across "C" -> still UB;
  "C-unwind" -> two-way defined unwinding.

## Verified NON-RFC facts (important corrections)

- There is NO accepted RFC for Arc, Rc, or Weak. They entered std via
  library PRs. rust-lang/rfcs PR #396 is "RFC: Single-entry /
  multiple-exit regions for borrows" (zwarich), POSTPONED — a borrow-
  regions RFC, unrelated to Arc. Never cite "RFC 396 for Arc".
- The base orphan rule predates the RFC process; its formal spec is the
  Rust Reference (items/implementations.html "Orphan rules").
- The literal phrase "aliasing XOR mutability" is NOT in official Rust
  docs and NOT in Niko's blog. Concept origin: Niko Matsakis, "Imagine
  never hearing the phrase 'aliasable, mutable'" (2012-11-18),
  https://smallcultfollowing.com/babysteps/blog/2012/11/18/imagine-never-hearing-the-phrase-aliasable/
  — "The contract is relatively simple: if you are reading, no one is
  writing, and if you are writing, no one else is reading (or writing)."
  Literal XOR phrase: GhostCell paper (ICFP 2021, arXiv:2107.07281) and
  Google's Comprehensive Rust course. Attribute accordingly.

## Verified historical quotes

- Niko Matsakis, "On Reference Counting and Leaks" (2015-04-29),
  https://smallcultfollowing.com/babysteps/blog/2015/04/29/on-reference-counting-and-leaks/
  — "We long ago decided that, to make reference-counting practical, we
  had to accept resource leaks as a possibility." and "This was a
  deliberate design decision that we made while transitioning from
  garbage-collected types (@T and @mut T) to user-defined reference
  counting." (Pre-1.0 Rust HAD a GC: @T managed pointers were removed.)
- Aaron Turon, "Fearless Concurrency with Rust" (2015-04-10),
  https://blog.rust-lang.org/2015/04/10/Fearless-Concurrency/
  — "In Rust, every value has an 'owning scope,' and passing or returning
  a value means transferring ownership ('moving' it) to a new scope."
  (The post also carries the note that thread::scoped was moved out of
  std at the time.)
- TRPL ch16: "We've nicknamed this aspect of Rust fearless concurrency."
- Rustonomicon "Send and Sync": "A type is Send if it is safe to send it
  to another thread. A type is Sync if it is safe to share between
  threads (T is Sync if and only if &T is Send)."
- Graydon Hoare (Rust's first author), "more cores, more fun" (2015-04-11)
  via Wayback,
  https://web.archive.org/web/2019/http://graydon2.dreamwidth.org/201806.html
  — "If there's been any guiding principle of the rust project from the
  beginning, it's been that faith that correct concurrency and general
  memory safety are two sides of the same coin, that both benefit from
  similar techniques of isolation and mutability control."
- Rust homepage (current): "Rust is blazingly fast and memory-efficient:
  with no runtime or garbage collector, it can power performance-critical
  services, run on embedded devices, and easily integrate with other
  languages." — https://www.rust-lang.org/

## UNVERIFIED — do not cite without manual fetch

- Graydon's "Rust before Rust" essay series (Dreamwidth, 2023-2024):
  blocked to automated fetchers; no public mirror verified.
- Any quote from the old rust-dev mailing list beyond what the RFC
  texts themselves quote.

## Source IDs

- [rfc0019] [rfc0243] [rfc0230] [rfc1023] [rfc1066] [rfc1236] [rfc2094]
  [rfc2113] [rfc2349] [rfc2451] [rfc2945] — URLs above
- [niko-leaks] [turon-2015] [graydon-2015] [niko-2012] — URLs above
- [rfcs-repo] rust-lang/rfcs (no Arc/Rc/Weak RFC; PR #396 postponed) —
  https://github.com/rust-lang/rfcs
