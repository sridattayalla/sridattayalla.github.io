# Send and Sync — verified matrix and the composition rule

Fact sheet for: send-sync.html. Captures from rustc 1.98.1.

## Definitions (Rustonomicon, verbatim)

"A type is Send if it is safe to send it to another thread. A type is Sync
if it is safe to share between threads (T is Sync if and only if &T is
Send)." [nomicon-send-sync]

- Send: ownership may be TRANSFERRED to another thread (the value moves
  there; the old thread no longer touches it).
- Sync: REFERENCES may be shared across threads (&T: Send). Equivalent:
  usable from multiple threads simultaneously.
- Both are auto traits (marker traits with automatic, structurally-derived
  impls; negative reasoning: a type is !Sync if any field is). Design
  origin: RFC 0019 "opt-in builtin traits" (which also made moves the
  default — see research/ownership.md). [rfc0019]

## Verified assertion matrix (send_sync_matrix.rs, compiles clean)

| Type | Send | Sync | why |
|---|---|---|---|
| u32 | yes | yes | plain data |
| Rc<u32> | no | no | non-atomic counts (see shared-ownership.md) |
| Arc<Vec<u32>> | yes | yes | atomic counts, T is Send+Sync |
| Arc<Cell<u32>> | no | no | Cell is !Sync -> composition fails |
| Cell<u32> | yes | no | whole-value swaps, non-atomic |
| RefCell<u32> | yes | no | non-atomic borrow counter |
| Mutex<u32> | yes | yes | locked access |
| *const u8 | no | no | raw aliasing, no discipline |
| PhantomData<*const u8> wrapper | no | no | markers propagate |

## The composition rule, shown by one real error

arc_send_requires.rs tries to move Arc<Cell<u32>> into thread::spawn:

```text
error[E0277]: `Cell<u32>` cannot be shared between threads safely
   --> arc_send_requires.rs:6:27
  |
  = help: the trait `Sync` is not implemented for `Cell<u32>`
  = note: if you want to do aliasing and mutation between multiple threads,
          use `std::sync::RwLock` or `std::sync::atomic::AtomicU32` instead
  = note: required for `Arc<Cell<u32>>` to implement `Send`
note: required by a bound in `spawn`
    |
128 |     F: Send + 'static,
    |        ^^^^ required by this bound in `spawn`
```

- Reading it bottom-up is the lesson: spawn requires F: Send; the closure
  captures Arc<Cell<u32>>; Arc<T>: Send requires T: Send + Sync; Cell is
  !Sync; rejected. The std Arc impl is exactly: `unsafe impl<T: ?Sized +
  Send + Sync> Send for Arc<T> {}` (std docs list the bound). [std-arc]
- WHY + Sync: sending an Arc to a new thread leaves the old thread with
  clones — both threads now hold &-like handles to the same T. If they can
  concurrently call &self methods, T must be Sync. (Send alone would only
  cover the single-owner case.) The closure also demonstrates 'static:
  spawn's bound `F: Send + 'static` — borrowed data cannot be sent unless
  it outlives the possibly-detached thread.

## Data-race freedom argument ("fearless concurrency")

- A data race needs: (1) two aliases, (2) at least one writer, (3)
  concurrent access, (4) no synchronization. Safe Rust removes (1)+(2):
  &mut is exclusive (E0502/E0499), & is non-mutating except through
  interior-mutability wrappers that restore (4) by checking/blocking; and
  cross-thread sharing requires the Send/Sync impls above. Hence "fearless
  concurrency": TRPL ch16: "We've nicknamed this aspect of Rust fearless
  concurrency." Aaron Turon's 2015 post of that title: "the key point is
  that Rust's type system prevents data races at compile time... the
  ownership system... thread-safe usage is checked like memory usage."
  [trpl-ch16] [turon-2015]
- What is NOT claimed: freedom from deadlocks (locks can deadlock), from
  logic races (ordering bugs with atomics), or leaks. Only memory-safety
  races. Rust's own concurrency docs state data-race freedom as "two or
  more threads concurrently accessing a location of memory... one of them
  is a write... unsynchronized" being undefined behavior that safe code
  cannot produce. [nomicon-send-sync]
- Graydon Hoare (2015): "If there's been any guiding principle of the rust
  project from the beginning, it's been that faith that correct
  concurrency and general memory safety are two sides of the same coin,
  that both benefit from similar techniques of isolation and mutability
  control." [graydon-2015]

## Escape hatches

- unsafe impl Send/Sync for MyType: asserts the discipline manually (what
  the wrapper types do internally). Rc deliberately does NOT; Arc does.
- Spawned thread requires 'static: use scoped threads (std::thread::scope)
  for borrowed data — the API returned in 1.63 after the leakpocalypse-era
  removal (research/design-history.md) because it now guards with
  JoinHandles instead of relying on destructors running.

## Source IDs

- [rustc-runs] local captures above (matrix, arc_send_requires)
- [nomicon-send-sync] https://doc.rust-lang.org/nomicon/send-and-sync.html
- [std-arc] https://doc.rust-lang.org/std/sync/struct.Arc.html
- [trpl-ch16] https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html
- [turon-2015] Aaron Turon, "Fearless Concurrency with Rust" (2015-04-10)
  — https://blog.rust-lang.org/2015/04/10/Fearless-Concurrency/
- [graydon-2015] Graydon Hoare, "more cores, more fun" (2015-04-11),
  via Wayback —
  https://web.archive.org/web/2019/http://graydon2.dreamwidth.org/201806.html
- [rfc0019] RFC 0019 "opt-in builtin traits" —
  https://rust-lang.github.io/rfcs/0019-opt-in-builtin-traits.html
