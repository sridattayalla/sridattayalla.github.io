# Rc, Arc, Weak — shared ownership, verified behavior

Fact sheet for: rc-arc.html. Captures from rustc 1.98.1.

## Rc<T>: reference counting as opt-in shared ownership

- Rc::clone(&a) does NOT copy the payload: it bumps a counter and produces
  a new one-word-ish handle. Verified run (rc_counts.rs):
  `count after 3 handles: 3` / `count after dropping b: 2` /
  `data via c: shared`. The strong count is the number of owners; when it
  hits 0, the value drops. Rc also carries a weak count (for Weak handles)
  — the allocation holds (strong, weak, T) together.
- Refcounting is a "tiny local GC": reachability is tracked incrementally
  (each clone/drop touches the count) instead of by a global trace. Cost:
  every handle clone and drop is a few instructions; the value is freed the
  moment the last handle drops (deterministic, unlike a tracing GC).
- The decision is per-TYPE and visible: `Rc<String>` in a signature says
  "shared ownership, non-atomic". The language default stays unique
  ownership; sharing is something you ask for.

## The cycle leak — verified anatomy

rc_cycle.rs: two Rc<Node>, each holding Rc of the other inside
RefCell<Option<Rc<Node>>>. Program printed `a count: 2, b count: 2` and
then exited WITHOUT printing either "Node dropped" — both destructors
leaked. Anatomy: a's count is held by the local binding AND b's next field;
when the locals drop, each count only falls 2 -> 1, because the other node
still holds a handle. Counts never reach 0; memory leaks; Drop never runs.

- Weak fix, verified (rc_cycle_weak.rs): b stores Weak<Node> (via
  Rc::downgrade) instead of Rc. Run: `a strong: 1` / `weak to a: 1`, then
  BOTH "Node dropped" lines print. Weak does not keep the value alive; it
  keeps the allocation's bookkeeping alive only. weak.upgrade() -> Option:
  verified `Some("payload")` while alive, `None` after drop (weak_upgrade.rs).
- Historical framing: Niko Matsakis, "On Reference Counting and Leaks"
  (2015): "We long ago decided that, to make reference-counting practical,
  we had to accept resource leaks as a possibility." Rust's guarantee is
  memory SAFETY, not leak-freedom — RFC 1066: "It has never been a
  guarantee of Rust that destructors for a type will run." [niko-leaks]
  [rfc1066]

## Rc is not for threads — E0277, captured verbatim

```text
error[E0277]: `Rc<String>` cannot be sent between threads safely
   --> rc_not_send.rs:5:32
    |
  5 |       let handle = thread::spawn(move || {
    |                    ------------- ^------
    |  __________________|_____________within this `{closure...}`
  ...
    = help: within this closure, the trait `Send` is not implemented for `Rc<String>`
```

- Mechanism: Rc's counter is a plain non-atomic increment. Two threads
  cloning simultaneously can both read 1, both write 2 — a lost update —
  and the value is freed twice (double free; see research/c-failures.md
  failure 3 for the C anatomy). Full rule in research/send-sync.md.

## Arc<T>: the atomic sibling

- Arc = Atomically Reference Counted: same layout and API, but the count
  updates use atomic CPU instructions. Cost: an atomic RMW is a locked
  instruction (~10-20 cycles uncontended vs ~1 for a plain add; scales
  worse under contention because cores negotiate cache-line ownership).
  This is the price of thread safety, paid ONLY where the type says so.
- Verified: 4 threads x 1000 fetch_add on Arc<AtomicUsize> -> `total: 4000`
  (arc_thread.rs). Arc<Vec<u32>> is Send+Sync (assertion matrix verified in
  research/send-sync.md).
- History: Arc/Rc/Weak entered std via library PRs, not RFCs (verified
  against the rust-lang/rfcs repo: no accepted RFC for them; PR #396 in
  rust-lang/rfcs is a postponed borrow-regions RFC, "Single-entry /
  multiple-exit regions for borrows" — do NOT cite an "RFC 396 for Arc").
  Arc existed in pre-1.0 std as part of the transition away from GC'd @T.

## When Rc vs Arc vs Box

- One owner, heap: Box. Many owners, one thread: Rc. Many owners, many
  threads: Arc. Mutation through shared handles: + RefCell (Rc) or
  Mutex/RwLock (Arc). The capstone page applies these rules to a full
  program (research/capstone.md).

## Source IDs

- [rustc-runs] local captures above (rc_counts, rc_cycle, rc_cycle_weak,
  weak_upgrade, rc_not_send, arc_thread)
- [niko-leaks] Niko Matsakis, "On Reference Counting and Leaks",
  2015-04-29 — https://smallcultfollowing.com/babysteps/blog/2015/04/29/on-reference-counting-and-leaks/
- [rfc1066] RFC 1066 "safe-mem-forget" —
  https://rust-lang.github.io/rfcs/1066-safe-mem-forget.html
- [trpl-ch15-4] https://doc.rust-lang.org/book/ch15-04-rc.html (Rc) and
  ch15-06 (Weak reference cycles) —
  https://doc.rust-lang.org/book/ch15-06-reference-cycles.html
- [std-rc] https://doc.rust-lang.org/std/rc/ ; [std-arc]
  https://doc.rust-lang.org/std/sync/struct.Arc.html
