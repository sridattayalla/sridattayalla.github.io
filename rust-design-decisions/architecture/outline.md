# Page outline (architecture contract)

One concept per page. Prerequisites strictly before dependents. Word windows in
manifest.json. The organizing question of the whole book: "Memory safety
without a garbage collector, without a runtime, at zero cost." Every page is
presented as a consequence of that founding constraint.

## Start
- **index.html** (500-1100w). The pitch: you already write Rust by trial and
  error; this book replaces memorized rules with derivable ones. The one
  organizing question. What you will be able to predict at the end. Defines:
  memory safety, garbage collector, runtime, ownership, owner, borrow
  checker, escape hatch (minimal definitions, deepened later).

## Part One — The Constraint
- **founding-constraint.html**. Owns: the deal (safe + fast + no runtime,
  why all three at once is the hard part); the five failure anatomies in
  C (dangling stack pointer, use-after-free, double free, iterator
  invalidation, data race) with real ASan/TSan reports; why GC dodges
  some of it and what GC costs (runtime, stop-the-world, non-deterministic
  destruction); the memory-safety statistics (MSRC ~70%, Chromium, Android)
  as motivation. Defines: stack, heap, dangling pointer, use-after-free,
  double free, iterator invalidation, data race, undefined behavior,
  sanitizer, destructor, deterministic destruction.

## Part Two — Ownership
- **ownership.html**. Owns: one owner per value; moves as the default
  (E0382 anatomy; why C++ surprise copies forced the opposite default —
  RFC 0019 record); deterministic destruction (Drop, RAII); drop order
  (locals reversed, fields forward — verified run); assignment drops the
  overwritten value; what this replaces (malloc/free pairing AND GC); the
  honesty clause (leaks are possible — RFC 1066 / leakpocalypse). Defines:
  move, drop, scope, RAII, drop order.
- **move-copy-clone.html**. Owns: the three behaviors of assignment
  (move / bitwise copy / explicit clone); why Copy is opt-in and shallow
  (E0204 anatomy — a bitwise String copy would double-free); what Copy
  may contain; Clone as the explicit, possibly-deep duplicate; first
  one-line definition of *trait* (deep treatment in Part Seven). Defines:
  trait, Copy trait, Clone, shallow copy, deep copy.

## Part Three — Borrowing
- **borrowing.html**. Owns: & shared vs &mut exclusive; aliasing XOR
  mutability as THE central rule (concept origin Niko 2012; the literal
  phrase's provenance stated honestly); how it kills iterator
  invalidation (E0502) and data races at compile time; the misreadings
  of E0499/E0596/E0506; NLL taste — borrow ends at last use, not scope
  end (RFC 2094; the scopes model is wrong); costs (graphs, two-phase
  patterns) and escape hatches (restructure, Cell/RefCell, unsafe).
  Defines: reference, shared reference, mutable reference, aliasing,
  aliasing xor mutability, borrowing, lifetime, non-lexical lifetimes,
  NLL.
- **lifetimes.html**. Owns: why annotations must exist (dangling
  references ruled out statically); what &'a means (region constraint
  relating references — not a timer); elision as sugar (the three rules);
  why structs need annotations (E0106); how to READ E0597/E0515/E0716
  (the later-use anatomy; the common misreadings); the verified
  compiling struct example. Defines: lifetime elision, region, outlives,
  static lifetime.

## Part Four — The Heap Menu
- **stack-and-heap.html**. Owns: allocation is explicit and typed in
  Rust (vs implicit in Java/Python); the owner/view pairs String/&str,
  Vec<T>/&[T] with verified sizes (24/16 bytes); fat pointers; slices;
  deref coercion; the signature-as-memory-contract reading. Defines:
  heap allocation, slice, fat pointer.
- **box.html**. Owns: Box as one-word owning heap pointer; why no
  implicit boxing (visible cost, deterministic free); recursive types
  (E0072 anatomy + Box fix); Box as ownership transfer; Box<dyn Trait>
  foreshadow (traits page owns vtables — here only the size fact).
  Defines: indirection, recursive type.
- **rc-arc.html**. Owns: shared ownership as an opt-in decision;
  refcounting as a tiny local GC (deterministic, incremental); the
  verified count updates; Rc vs Arc (what atomics cost, why Rc cannot
  cross threads — full Send/Sync story deferred two pages); Weak and
  reference cycles (verified leak anatomy + Weak rescue); the leak
  honesty clause (RFC 1066, Niko's post); no RFC exists for Rc/Arc/Weak
  (corrected history). Defines: reference counting, shared ownership,
  reference cycle, weak reference, atomic, memory leak.

## Part Five — Mutation and Threads
- **interior-mutability.html**. Owns: the correction — &T forbids
  contract-violating mutation, not all mutation; Cell (compile-time
  discipline), RefCell (runtime borrow flags, the verified panic),
  Mutex/RwLock (blocking cousins; verified poisoning); which is the
  honest tool; Rc<RefCell<T>> as the single-threaded graph pattern.
  Defines: interior mutability, guard, poisoning.
- **send-sync.html**. Owns: why thread safety is in marker traits; the
  definitions (Rustonomicon verbatim); the verified assertion matrix;
  the composition rule Arc<T>: Send requires T: Send + Sync (the
  Arc<Cell<u32>> E0277 anatomy read bottom-up); 'static bound on spawn;
  the data-race-freedom argument ("fearless concurrency") and what it
  does NOT promise (deadlocks, logic races); scoped threads.
  Defines: Send, Sync, marker trait, auto trait, fearless concurrency.

## Part Six — The Escape Hatches
- **unsafe.html**. Owns: why unsafe exists (static analysis is
  conservative — TRPL quote); the five superpowers; the canonical
  motivation split_at_mut (safe version E0499 + the unsafe
  implementation that std uses, verified run); the invariants you
  inherit (aliasing, validity, exactly-once drop); safe abstraction
  pattern (assert + SAFETY comments + small blocks). Defines: unsafe
  block, raw pointer, soundness, safe abstraction.
- **pin.html**. Owns: self-referential structs (the async problem);
  Pin as a promise ("never move before dropped" — RFC 2349 quote); the
  verified demo (Pin<Box<T>> moves, pointee does not; get_mut refused
  without Unpin); Unpin as the opt-out; why async/await needed it (a
  suspended future is a self-referential struct). Defines: pin, pinning,
  self-referential, Unpin, future, async.
- **error-handling.html**. Owns: Result instead of exceptions or null
  (why: visible control flow, no hidden paths); panic as the second
  tier (verified catch_unwind run — unwinding runs Drops); ? as
  controlled propagation (RFC 243 quote; From composition); the two-tier
  decision procedure (violated invariant vs expected failure); unwinding
  across FFI (RFC 2945: abort at "C", defined with "C-unwind");
  panic=abort. Defines: panic, unwinding, propagation, recoverable
  error.

## Part Seven — Abstraction and Synthesis
- **traits.html**. Owns: coherence/orphan rules (E0117 anatomy; why
  ecosystem-wide impl uniqueness is needed for static dispatch; RFC
  1023/2451 history; newtype escape hatch); monomorphization (verified
  run; the zero-cost ladder and its compile-time price); dyn Trait (fat
  pointers verified; RFC 2113; object safety). Defines: coherence,
  orphan rule, monomorphization, vtable, trait object, static dispatch,
  dynamic dispatch, newtype, object safety.
- **capstone.html** (1400-2400w). The full-circle page: two verified
  programs (Arc<RwLock<Cache>> and a thread pool) with every type
  decision justified from earlier pages — why Arc and not Rc; why
  Arc<Mutex<T>> and not Mutex<Arc<T>>; why not Rc everywhere; why
  Box<dyn FnOnce> for jobs; why the channel receiver is
  Arc<Mutex<Receiver>>; Drop as deterministic shutdown. Ends with the
  walkable mental model: the whole book as one loop (constraint ->
  ownership -> borrowing -> heap menu -> sharing -> escape hatches ->
  abstractions -> back to the constraint). Defines: thread pool.

## Reference
- **glossary.html**. Every terms.json term, 1-3 sentences, grouped by
  part, each entry links its defining page.
- **links.html**. All external sources grouped, research-sheet mapping,
  toolchain/verification statement. The only page allowed external URLs.

## Verification
- Every `pre[data-verify]` code block is machine-verified by
  tools/verify.py (rustc 1.98.1 / gcc 11.4 + sanitizers); results in
  tools/verify-report.json; check.py refuses stale or missing results
  (E_VERIFY). No snippet may claim compile/fail status rustc did not
  produce.
