# Capstone programs — verified behavior

Fact sheet for: capstone.html. Both programs compile and run under
rustc 1.98.1, edition 2021; outputs captured.

## Program 1: Arc<RwLock<Cache>> — shared mutable state across threads

cache_capstone.rs: 2 writer threads x 3 inserts, 3 reader threads x 5
reads; final read prints `entries: 6, writes: 6`.

Decisions to justify on the page (each traces to earlier chapters):

- Cache itself: plain struct; one instance, no per-field sharing ->
  no interior mutability INSIDE Cache (research/interior-mutability.md).
- Arc (not Rc): handles cross threads; Rc would be E0277
  (research/shared-ownership.md capture).
- Arc (not plain &): threads may outlive the spawning scope ->
  spawn's 'static bound forces owned handles.
- RwLock (not Mutex): readers outnumber writers and reads only need
  &; Mutex would serialize readers. XOR rule at runtime
  (research/interior-mutability.md).
- Arc<Mutex<T>> vs Mutex<Arc<T>>: the lock must guard the DATA, not the
  handle. Mutex<Arc<T>> would let each thread clone its handle then
  still need a second lock to read through it — locking the pointer,
  not the pointee; and readers holding Arc clones could mutate freely
  without the mutex if T: Sync — the lock must be OUTSIDE the sharing.
- Guard drop timing: explicit `drop(guard)` before sleep in readers to
  show guard lifetimes are lexical-ish but controllable; the E0597
  match-scrutinee gotcha (research/ownership.md) is the cautionary tale.
- unwrap() on lock(): poisoning propagation choice
  (research/interior-mutability.md capture).

## Program 2: a minimal thread pool — channels, Arc<Mutex<Receiver>>, Drop

pool_capstone.rs (from the TRPL ch20-style design, verified): 3 workers,
5 jobs; output shows jobs distributed across workers and `pool shut down
cleanly` after Drop drains.

Decisions to justify:

- Job = Box<dyn FnOnce() + Send + 'static>: dyn because job types are
  heterogeneous (research/traits.md); Send to cross to the worker
  thread; 'static because the pool cannot borrow from main
  (research/send-sync.md); Box because dyn is unsized (fat pointer —
  the channel stores a fixed-size box).
- Arc<Mutex<Receiver>>: ONE receiver consumed by MANY workers — shared
  ownership (Arc) AND exclusive access to recv() (Mutex). mpsc = multi-
  producer, single-consumer: the Sender side needs no lock (cloned per
  producer), the Receiver side is single-consumer so the Mutex supplies
  the exclusivity the channel type itself cannot.
- `let job = { let guard = rx.lock().unwrap(); guard.recv() };` — the
  lock is RELEASED before the job runs: holding the lock during job
  execution would serialize the whole pool.
- Drop for Pool: take() the sender (closes the channel -> recv() errs ->
  workers break), then join each worker: deterministic shutdown order.
  This is RAII applied to concurrency (research/ownership.md).
- Channel-recv error AS the shutdown signal: Err(()) is the designed
  "no more jobs ever" message, not a failure.

## Why not Rc everywhere / why not Arc everywhere

- Rc: fails at the first thread boundary (E0277 capture); also hides
  cost (atomic-free counting is a lie in concurrent code).
- Arc everywhere: pays atomic RMW for single-threaded handles; but more
  deeply — Arc turns lifetime errors into runtime leaks (cycles), and
  unique ownership is DOCUMENTATION: a Box or & tells every reader who
  frees and when; an Arc says "anyone may be last" and invites cycles.
  The design lesson of the whole book: the type states the sharing
  policy, so prefer the most restrictive type that works: T > &T >
  Box<T> > Rc/Arc, and add interior mutability only at the point of
  shared mutation.

## Source IDs

- [rustc-runs] local captures above (cache_capstone.rs, pool_capstone.rs)
- [trpl-ch16] https://doc.rust-lang.org/book/ch16-03-shared-state.html
  (Arc, Mutex, channels)
- [trpl-ch20] https://doc.rust-lang.org/book/ch20-00-final-project.html
  (the thread pool project; chapter number is 20 in the current TRPL —
  verify link target naming when building links.html)
