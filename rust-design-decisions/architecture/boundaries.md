# Boundary briefs (adjacent-page contract)

For every adjacent pair: what the left page owns, what the right page owns,
the handoff sentence direction, and the foreshadow rules. Nothing in this file
is visible to readers; it binds writers and auditors.

## Global prose discipline (E_TERM avoidance table)

The term ledger (terms.json) guards whole words, case-insensitively, with
automatic +s/+es plurals of the final word. Code blocks, svg text, nav, pager,
and prov marks are exempt. Before a term's defining page, the word below may
not appear in prose (word forms listed are the MATCHING forms — irregular
forms in parentheses are safe to use):

| Guarded word(s) | Defining page | Banned on pages before it | Safe rewording |
|---|---|---|---|
| stack, heap | founding-constraint | index | "memory your program manages" |
| dangling pointer, use-after-free, double free, iterator invalidation, data race, undefined behavior, sanitizer, destructor, deterministic destruction | founding-constraint | index | "memory bugs", "crashes", "cleanup code" |
| move (moved, moving are safe) | ownership | index, founding-constraint | "hand over", "transfer" |
| drop (dropped, dropping are safe), scope (scoped is safe) | ownership | index, founding-constraint | "release", "free", "block", "braces" |
| RAII | ownership | index, founding-constraint | "destructor-based cleanup" |
| trait (traits also matches) | move-copy-clone | index, founding, ownership | "interface"; `<code>Drop</code>` inline code is exempt |
| clone (cloned, cloning are safe) | move-copy-clone | index, founding, ownership | "duplicate" |
| shallow copy, deep copy (phrases only; "copy"/"copies" unguarded) | move-copy-clone | index, founding, ownership | "bitwise copy", "byte-for-byte copy" |
| reference (references) | borrowing | index, founding, ownership, move-copy-clone | "pointer", "handle", "&-thing" |
| borrowing (borrow, borrows, borrowed are safe) | borrowing | index, founding, ownership, move-copy-clone | "lending access", the verb "borrow" |
| aliasing (alias, aliases, aliased are safe) | borrowing | index, founding, ownership, move-copy-clone | "two live pointers to one value" |
| lifetime (lifetimes) | borrowing | index, founding, ownership, move-copy-clone | "how long the value is guaranteed alive" |
| region | lifetimes | index … borrowing (5 pages) | "live range", "zone" |
| outlives (outlive, outlived are safe) | lifetimes | index … borrowing (5 pages) | use "outlive" |
| static lifetime (phrase) | lifetimes | index … borrowing | "'static" alone in code; "the forever lifetime" in prose |
| slice (slices) | stack-and-heap | index … lifetimes (6 pages) | "a borrowed view of the elements" |
| fat pointer (phrase) | stack-and-heap | index … lifetimes | "pointer plus length" |
| heap allocation (phrase; "heap" alone is fine from founding on) | stack-and-heap | index … lifetimes | "allocating on the heap" |
| indirection | box | index … stack-and-heap (7 pages) | "a pointer step", "one hop" |
| recursive type (phrase) | box | index … stack-and-heap | "a type that contains itself" |
| shared ownership (phrase; "ownership", "owner" fine from index on) | rc-arc | index … box (8 pages) | "more than one owner" |
| atomic (atomics; atomically is safe) | rc-arc | index … box (8 pages) | "torn", "unsynchronized", "lock-free CPU instruction" |
| memory leak (phrase; leak, leaks, leaked are safe) | rc-arc | index … box (8 pages) | "leaked memory", "a leak" |
| reference counting, reference cycle, weak reference (phrases) | rc-arc | index … box | "counting owners", "a cycle of owners", "a non-owning handle" |
| interior mutability (phrase) | interior-mutability | index … rc-arc (9 pages) | "mutation through a shared handle" |
| guard (guards) | interior-mutability | index … rc-arc (9 pages) | "the lock holder", "the wrapped value" |
| poisoning (poisoned, poisons are safe) | interior-mutability | index … rc-arc | "poisoned" as adjective |
| Send (send, sends), Sync (sync) | send-sync | index … interior-mutability (10 pages) | "cross a thread boundary", "thread-safe" |
| marker trait, auto trait, fearless concurrency (phrases) | send-sync | index … interior-mutability | describe, don't name |
| unsafe block (phrase; "unsafe" alone is unguarded), raw pointer (phrase), soundness, safe abstraction (phrase) | unsafe | index … send-sync (11 pages) | "unsafe code", "C-style pointer", "the invariants" |
| pin (pins), future (futures), async, Unpin, self-referential, pinning | pin | index … unsafe (12 pages) | "promise not to relocate", "later in this book", "suspended computation" |
| panic (panics; panicked, panicking are safe) | error-handling | index … pin (13 pages) | "halt", "abort", "crash", "panicked at" |
| unwinding, propagation (propagates is safe) | error-handling | index … pin (13 pages) | "cleanup while escaping the call chain", "hand upward" |
| recoverable error (phrase) | error-handling | index … pin | "expected failure" |
| coherence, orphan rule, monomorphization, vtable, trait object, static dispatch, dynamic dispatch, newtype, object safety | traits | index … error-handling (15 pages) | "impl uniqueness", "compiler-generated copies", "fat pointer to a value plus its methods", "wrapper struct" |
| thread pool (phrase; pool, pools unguarded) | capstone | everything except capstone | "a fixed crew of worker threads" |

Sanctioned term-ok escapes (marked, with reason, never silent):
- interior-mutability.html: the noun "panic" for the RefCell failure mode,
  two or three spots — the failure IS a panic and dodging the word would lie.
  Reason text: "panic named deliberately; the failure mode is the point".
- send-sync.html: at most one "panic" escape if the poisoning handoff needs
  the noun; otherwise write "a thread that dies while holding the lock".
- unsafe.html: at most one "panic" escape for `assert!`; otherwise "halts".

Numeric discipline: spell small counts in prose ("three rules", not "3
rules"); NUM_RE flags every digit run, and each needs a prov mark or prov-ok
escape within ten lines. Error codes (E0382) and identifier-adjacent digits
do not match NUM_RE. figcaptions are NOT exempt: keep numerals out of them.

## Pair briefs

### index → founding-constraint
- index owns: the promise (derive rules, not memorize them), the organizing
  question, the seven first-pass definitions (memory safety, garbage
  collector, runtime, ownership, owner, borrow checker, escape hatch).
- founding-constraint owns: the C failure anatomies, the deal's difficulty,
  what GC costs, the memory-safety statistics.
- Handoff: index ends "the next page shows the five failures the constraint
  must prevent, in the language that has all of them."
- Foreshadow: index may name "ownership" and "borrow checker" (both defined
  there) but must not explain mechanics; no C code on index; no "stack",
  "heap", "move", "drop", "trait", "reference" in prose.

### founding-constraint → ownership
- founding owns: stack/heap as memory pictures (not Rust mechanics), the
  five failure programs with sanitizer reports, GC costs, statistics.
- ownership owns: the one-owner rule, E0382, moves, Drop, RAII, drop order,
  the leak honesty clause.
- Handoff: founding ends "C gives you no tool to prevent these; the next
  page shows the one rule Rust adds that deletes all five at once."
- Foreshadow: founding may say "ownership" (defined on index) as a name for
  the upcoming idea, but must not state the move rule or show Rust code
  beyond a teaser. Founding must not use: move, drop, scope, trait, RAII,
  reference, "memory leak" (say "leaked memory"), "atomic" (say "torn"/
  "unsynchronized"), "raw pointer" (say "C pointer").

### ownership → move-copy-clone
- ownership owns: single owner, move-on-assignment, E0382 anatomy, drop at
  brace end, drop order, assignment drops the overwritten value, leaks are
  possible (RFC 1066).
- move-copy-clone owns: the three assignment behaviors, E0204, why Copy is
  shallow and opt-in, Clone as explicit deep duplicate, first definition of
  "trait".
- Handoff: ownership ends "assignment destroyed the old binding — except
  when it doesn't; integers survive assignment. The next page gives
  assignment its full three-way menu."
- Foreshadow: ownership may show `#[derive(Clone)]` in code (exempt) but
  must not say "clone"/"Copy"/"trait" in prose. `impl Drop` appears as code;
  prose says "the Drop interface".

### move-copy-clone → borrowing
- move-copy-clone owns: move vs bitwise copy vs clone; E0204 anatomy; the
  trait one-liner.
- borrowing owns: & vs &mut, aliasing XOR mutability, E0502/E0499/E0596/
  E0506 readings, NLL, costs and hatches.
- Handoff: move-copy-clone ends "cloning every read is wasteful and moves
  give away too much; functions need to look at a value without taking it.
  That mechanism is the next page."
- Foreshadow: none needed. move-copy-clone must not use "reference",
  "borrowing", "lifetime", "aliasing" in prose (function signatures with &
  in code are exempt — but keep them minimal; show `fn len(s: &String)`
  style only if unavoidable, prose calls it "the & form" without the word
  "reference"... preferred: no & in code on this page at all).

### borrowing → lifetimes
- borrowing owns: the XOR rule, the E0502 family, NLL semantics, the
  misreadings, costs, escape hatches.
- lifetimes owns: why annotations exist, regions as constraints, elision
  rules, E0106, E0597/E0515/E0716 anatomy, the compiling struct example.
- Handoff: borrowing ends "the checker proved `r` could outlive the data —
  outlive by how much? That question is the next page."
  (Write "outlive", never "outlives", on borrowing.)
- Foreshadow: borrowing defines "lifetime" in its NLL section (one
  paragraph, the minimal definition); lifetimes deepens it. borrowing must
  not use "region" (say "live range"), "outlives", "elision", "static
  lifetime". borrowing may show `&'a` in code only inside the single
  teaser-free handoff; preferred: no lifetime syntax in borrowing code.

### lifetimes → stack-and-heap
- lifetimes owns: annotation meaning, elision, E0106/E0597/E0515/E0716.
- stack-and-heap owns: explicit typed allocation, owner/view pairs,
  String/&str, Vec/&[T], sizes, fat pointers, deref coercion,
  signature-as-contract.
- Handoff: lifetimes ends "annotations constrain time; where values live is
  space. Rust makes you choose placement explicitly — the next page is the
  menu."
- Foreshadow: lifetimes must not use "slice", "fat pointer", "heap
  allocation" in prose (the word "heap" alone is fine from founding on).
  stack-and-heap must not use "indirection".

### stack-and-heap → box
- stack-and-heap owns: the owner/view pairs, sizes, fat pointers, slices,
  deref coercion, signature contracts.
- box owns: Box mechanics, E0072 + fix, Box as ownership transfer, the
  Box<dyn Trait> size fact (vtable language deferred).
- Handoff: stack-and-heap ends "views are borrowed and temporary; the
  simplest way to put a value itself on the heap is one word — the next
  page."
- Foreshadow: stack-and-heap must not use "indirection" or "recursive
  type". box must not say "shared ownership" (say "more than one owner"),
  must not say "vtable" (say "fat pointer" — defined on the previous page).

### box → rc-arc
- box owns: Box, E0072, recursive types, indirection, ownership transfer,
  Box<dyn Trait> size fact.
- rc-arc owns: shared ownership, reference counting, Rc vs Arc, Weak,
  cycles, the leak honesty clause, corrected history (no RFC for Rc/Arc).
- Handoff: box ends "Box has exactly one owner; graphs want many. Rust
  makes that an explicit, typed decision — the next page."
- Foreshadow: box must not use "atomic", "reference counting", "weak
  reference", "memory leak" (phrase), "interior mutability", "Send"/"Sync"
  (say "cannot cross a thread boundary" only if needed — prefer not at
  all).

### rc-arc → interior-mutability
- rc-arc owns: Rc/Arc counts, atomics cost, Weak/cycles, deterministic
  reclamation, no-RFC history.
- interior-mutability owns: the &T correction, Cell, RefCell (runtime
  flags, the verified panic), Mutex/RwLock, poisoning, Rc<RefCell<T>>.
- Handoff: rc-arc ends "every owner can read; what happens when two of
  them want to write? The shared handle needs a new kind of mutation —
  next page."
- Foreshadow: rc-arc must not use "interior mutability", "guard",
  "poisoning". It may name RefCell in code (`Rc<RefCell<T>>` in a code
  block is exempt) but prose stays generic. "RefCell" alone is not a
  ledger term — but do not explain it here.

### interior-mutability → send-sync
- interior-mutability owns: the correction, Cell/RefCell/Mutex/RwLock,
  the panic, poisoning, the single-threaded graph pattern.
- send-sync owns: Send/Sync definitions, the matrix, Arc composition rule,
  E0277 read bottom-up, 'static bound, fearless concurrency and its
  limits, scoped threads.
- Handoff: interior-mutability ends "RefCell's flags are checked at
  runtime and know nothing about threads; cross a thread boundary and you
  need the check to be in the types — next page."
- Foreshadow: interior-mutability must not use "Send", "Sync", "send",
  "sends", "sync", "marker trait", "auto trait". "Thread" is fine;
  "thread pool" is not (say "a crew of worker threads" if ever needed).

### send-sync → unsafe
- send-sync owns: Send/Sync, the matrix, composition, E0277, 'static,
  scoped threads, what fearless does not promise.
- unsafe owns: why unsafe exists, the five superpowers, split_at_mut
  (E0499 safe version + the std unsafe implementation), inherited
  invariants, safe abstraction pattern.
- Handoff: send-sync ends "every guarantee so far was checked from types
  alone; the checker is deliberately conservative — some correct programs
  it cannot prove. Rust's answer is a marked region where YOU make the
  promise — next page."
- Foreshadow: send-sync must not use "unsafe block" (phrase), "raw
  pointer", "soundness", "safe abstraction"; "unsafe" alone is allowed
  where the escape-hatch list needs it (the word is unguarded). Avoid
  "newtype" (say "wrapper struct"). Avoid "panic" (one escape allowed).

### unsafe → pin
- unsafe owns: the five superpowers, split_at_mut, invariants, safe
  abstraction, SAFETY comments.
- pin owns: self-referential structs, the async problem, Pin semantics,
  the verified demo, Unpin, RFC 2349.
- Handoff: unsafe ends "one invariant list is special: never move the
  value. It is common enough, and invisible enough, that Rust wrapped it
  in a type — next page."
- Foreshadow: unsafe must not use "pin", "future", "async",
  "self-referential", "Unpin", "panic" (use "halts"; assert! behavior is
  described without the noun, or one sanctioned escape).

### pin → error-handling
- pin owns: Pin/Unpin, the demo, the async problem, RFC 2349.
- error-handling owns: Result vs exceptions/null, panic tier, catch_unwind
  run, ? operator (RFC 243), From, the two-tier decision, C-unwind
  (RFC 2945), panic=abort.
- Handoff: pin ends "every page so far assumed the happy path; failure
  needs the same discipline — visible, typed, and predictable. Next page."
- Foreshadow: pin must not use "panic", "unwinding", "propagation",
  "recoverable error" (pin discusses Drop-before-move; failure vocabulary
  stays on error-handling). "Panicked" (adjective) is safe if needed.

### error-handling → traits
- error-handling owns: Result, panic, ?, From, two-tier procedure,
  C-unwind, panic=abort.
- traits owns: coherence/orphan (E0117, RFC 1023/2451, newtype),
  monomorphization, dyn Trait, RFC 2113, object safety.
- Handoff: error-handling ends "Box<dyn Error> appeared three times on
  this page and we never asked what it costs. That question opens the last
  part — next page."
- Foreshadow: error-handling must not use "trait object", "vtable",
  "monomorphization", "coherence", "static dispatch", "dynamic dispatch",
  "newtype", "object safety". Box<dyn Error> in code is exempt; prose says
  "a boxed error of any type".

### traits → capstone
- traits owns: coherence, E0117, newtype, monomorphization, vtable,
  dyn Trait, object safety.
- capstone owns: the two programs (Arc<RwLock<Cache>>, thread pool),
  every type decision justified, the full-circle loop.
- Handoff: traits ends "you now own every piece; the last page assembles
  them into two programs and walks the whole loop one time."
- Foreshadow: traits must not use "thread pool" (phrase).

### capstone → glossary
- capstone owns: the synthesis; its takeaways are the book's takeaways.
- glossary owns: all 84 ledger entries, grouped by part, each linking its
  defining page.
- Handoff: capstone's pager points to glossary; no prose handoff needed.

### glossary → links
- glossary owns: term definitions.
- links owns: every external URL, the research-sheet map, the toolchain
  and verification statement (rustc 1.98.1, gcc 11.4.0, clang 14.0.0,
  sanitizers, verify-report).
- Handoff: none beyond the pager.
