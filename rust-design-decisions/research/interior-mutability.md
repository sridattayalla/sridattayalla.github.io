# Interior mutability: Cell, RefCell, Mutex, RwLock — verified behavior

Fact sheet for: interior-mutability.html. Captures from rustc 1.98.1.

## The correction to the folklore

- "&T means nothing can mutate through it" is WRONG as stated. &T means:
  no mutation that would violate the aliasing contract — i.e., mutation
  that could be observed THROUGH another aliasing reference or pointer.
  Types may mutate their interiors through &self if the mutation is
  structured so aliased readers can never observe a broken invariant.
  Rust's name for this pattern: interior mutability (std::cell module
  docs: "shared mutability" / allows mutation "in otherwise immutable
  contexts"). [std-cell]
- The pattern needs a safe wrapper because the compiler cannot see the
  discipline; each wrapper picks an enforcement mechanism:
  - Cell<T>: no references to the interior escape; values move in/out
    wholesale (T: Copy for get, replace for others). Checking happens at
    COMPILE time (nothing to check at runtime) — that is why Cell<T> is
    Sync-never but Send-yes and needs no flags.
  - RefCell<T>: references DO escape (&Ref<T> / &mut RefMut<T>); checking
    happens at RUNTIME with a borrow counter.
  - Mutex<T>/RwLock<T>: same escape, but the check is across threads, by
    blocking, not panicking.

## Cell — verified

cell_demo.rs (run): `let c = Cell::new(41); let shared = &c;
shared.set(shared.get() + 1);` prints `value: 42`. Mutation through &Cell
compiles and works: Cell's &self methods move whole values in/out, so no
alias into the interior ever exists.

## RefCell — the runtime borrow checker, verified

refcell_ok.rs (run): `cell.borrow_mut().push(4);` then `cell.borrow().len()`
prints `len: 4`. Borrow rules are the same as &/&mut — MANY readers XOR ONE
writer — but enforced when borrow()/borrow_mut() is CALLED:

refcell_panic.rs (run, exit 101):
```text
thread 'main' (4032141) panicked at refcell_panic.rs:5:18:
RefCell already borrowed
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```
(borrow() held on line 4; borrow_mut() on line 5 while still held.)

- Note rustc 1.98's message text: "RefCell already borrowed" (older
  releases said "already mutably borrowed: BorrowError" — quote the current
  one; if giving std-doc wording, use the error types BorrowError /
  BorrowMutError which borrow_mut returns in library code, vs the panic
  message when called as a method returning Ref/RefMut).
- RefCell<T>: Send where T: Send, but !Sync (verified in matrix,
  research/send-sync.md): the counter is not atomic.
- The canonical combo: Rc<RefCell<T>> = many handles x runtime-checked
  mutation, single thread. (Rc from research/shared-ownership.md.)

## Mutex / RwLock — thread-blocking cousins, verified

- Mutex<T>: one lock; lock() blocks; guard (RAII) releases on drop —
  poisoning verified (mutex_poison.rs run): worker panicked while holding;
  main's later lock() returns Err(PoisonError); `poisoned.into_inner()`
  still yields the data `[1, 2, 3, 4]`. Poisoning is advisory: it signals
  "a thread died mid-critical-section; the invariant may be broken".
- Mutex<u32>: Send+Sync (verified matrix). Mutex<T>: Sync requires T: Send.
- RwLock<T>: many readers XOR one writer, the same XOR rule as the borrow
  checker, but with waiting instead of rejection. Used in the capstone
  (research/capstone.md): cache.read()/cache.write() guards.
- Drop-order gotcha, verified E0597 (see research/ownership.md): match on
  `shared.lock()` as a block's tail expression holds the guard past the
  locals' drops; bind `let attempt = shared.lock();` first. The error text
  itself suggests the semicolon fix — quoted in ownership.md.

## Which is the honest tool

- Cell: small Copy state (flags, counters) shared immutably — zero runtime
  cost, impossible to get wrong, single-threaded.
- RefCell: need & or &mut INTO shared data (trees, graphs) on one thread;
  accepts that violations panic at runtime.
- Mutex: shared state across threads; accepts blocking.
- RwLock: read-heavy shared state across threads.
- atomics: counters/flags across threads without blocking (used in
  arc_thread.rs).

## Costs and escape-hatch status

- Interior mutability is not an escape hatch FROM the aliasing rule; it is
  a library implementation OF it with a different enforcement point. The
  guarantee weakens from compile time to run time (RefCell panic) or
  blocks (Mutex) — the choice is a latency/verbosity trade you declare in
  the type. TRPL ch15.5 ("RefCell<T> and the Interior Mutability Pattern")
  frames it exactly this way. [trpl-ch15-5]

## Source IDs

- [rustc-runs] local captures above
- [std-cell] https://doc.rust-lang.org/std/cell/ (module docs)
- [trpl-ch15-5] https://doc.rust-lang.org/book/ch15-05-interior-mutability.html
- [std-sync] https://doc.rust-lang.org/std/sync/ (Mutex, RwLock, poisoning)
