# Tokio 1.x Runtime Internals — Verified Fact Sheet (current: v1.53.1, July 2026)

**Scope/verification method:** Facts below come from (a) the tokio source tree at HEAD SHA `e37e284e4ba14c29359c692fe36a2a623d8255a1`, (b) upstream `tokio.rs` blog/diagram posts, and (c) the official `tokio::runtime` module + `Builder` docs. "Local run queue capacity 256," "6 timer levels × 64 slots," "LIFO throttle = 3," "blocking pool keep-alive = 10s," and the task state-bit layout were all **read directly out of the source**. Unstable/deprecated items are explicitly labeled. Everything else is stable, current behavior as of **Tokio 1.53.1 (2026-07-20)**.

## 1. Multi-threaded scheduler

**Workers.** The multi-thread runtime has a **fixed number of worker threads, all created at startup** (one per CPU core by default). Each worker is driven by an OS thread and owns a `Core` containing its run queue, LIFO slot, tick, and stats. Source: `worker.rs` module doc ["A scheduler is initialized with a fixed number of workers... `block_in_place`... the worker's core is handed off"](https://github.com/tokio-rs/tokio/blob/e37e284e4ba14c29359c692fe36a2a623d8255a1/tokio/src/runtime/scheduler/multi_thread/worker.rs#L1-L5) and the `worker::Core` struct fields (tick, lifo_slot, lifo_enabled, run_queue, is_searching, global_queue_interval, rand).

**Per-worker local run queue.** A lock-free deque (single producer = its own worker, multi-consumer for stealers). Fixed-size ring buffer.

- **Capacity: 256 tasks.** `const LOCAL_QUEUE_CAPACITY: usize = 256;` at [`queue.rs#L63`](https://github.com/tokio-rs/tokio/blob/e37e284e4ba14c29359c692fe36a2a623d8255a1/tokio/src/runtime/scheduler/multi_thread/queue.rs#L63).
- **Physical layout:** `Inner { head: AtomicUnsignedLong, tail: AtomicUnsignedShort, buffer: Box<[UnsafeCell<MaybeUninit<Notified>>; 256]> }`. The `head` packs two unsigned-shorts: the "real" head and a stealer-in-progress marker (ABA mitigation).
- Producer (`Local`) is used by one thread; `tail` is written only by the producer, `head` is read across threads.

**Overflow behavior.** `push_back_or_overflow` pushes into the local queue if capacity exists; on a full queue it moves **half the queue's tasks plus the new task** into the global injection queue via `push_overflow` (`NUM_TASKS_TAKEN = LOCAL_QUEUE_CAPACITY / 2`), then notifies other workers. It deliberately pushes the **second half** of the queue out, keeping the first half fresh — this avoids immediately re-overflowing tasks that just came from the global queue.

**Global injection queue.** `inject::Shared` — a mutex-guarded intrusive linked list of tasks. Purposes: (1) submit work to the scheduler from **off-worker** threads, and (2) receive overflow from saturated local queues.

**LIFO slot optimization.** Present in the multi-thread scheduler (NOT current-thread). Each worker stores an `Option<Notified>` "next task" slot. When a task running on a worker **wakes another task**, the woken task goes into the LIFO slot (checked **before** the run queue), so the last-scheduled task runs next. Motivation: locality + reduced latency for message-passing ping-pong. If the slot is occupied, the old occupant is pushed to the back of the local queue. See `worker::Core.lifo_slot` doc and the [2019 scheduler blog post on the "next task" slot](https://tokio.rs/blog/2019-10-scheduler#a-quick-fix-cache-locality).

- **Starvation throttle:** To prevent ping-pong starvation, the LIFO slot is only prioritized `MAX_LIFO_POLLS_PER_TICK = 3` times per tick, then `lifo_enabled` is flipped off until a non-LIFO task runs. `const MAX_LIFO_POLLS_PER_TICK: usize = 3;` at `worker.rs#L269`.
- When a LIFO task runs, the **coop budget is not reset** (it inherits the parent poll's budget).
- Disable via `Builder::disable_lifo_slot` (unstable).

**Work stealing search order.** When a worker's local queue (and LIFO slot) is empty:
1. Check the global queue (per `global_queue_interval`, see ticks below); if it has tasks, take them.
2. The worker randomizes an index and tries siblings in order (random start point) via `steal_into`/`steal_into2`, stealing **half** of a victim's tasks.
3. Only transitions to "searching" (increments the searchers count) if **fewer than half of the workers are already searching**, to throttle concurrent stealing.
4. On finding a task, it transitions out of searching and (if it parked) notifies another worker.
5. Fallback: re-checks the global queue / parks.

See `worker::steal_work` doc ["Only if less than half the workers are searching... will a new worker actually try to steal"], and the [2019 blog post "finding tasks to steal" section](https://tokio.rs/blog/2019-10-scheduler#balancing-work-across-processors).

**Ticks / hints / yielding.**
- **`global_queue_interval`:** how many local-task polls before re-checking the global queue. If unset, it's **dynamically tuned** targeting ~10 ms between global checks (based on `worker_mean_poll_time`). The historical hardcoded default was 61 ("copied from golang"). Documented in the `tokio::runtime` module: ["the runtime will dynamically compute it using a heuristic that targets 10ms intervals"](https://docs.rs/tokio/latest/tokio/runtime/index.html#multi-threaded-runtime-behavior-at-the-time-of-writing).
- **`event_interval`:** how many ticks between polling the I/O/time drivers. Default 61 for multi-thread.
- **Coop budget / yielding:** each task gets a `coop::Budget` of poll credits (~128). Polling consumes budget; when exhausted the task returns `Pending` forced, and `yield_now` pushes the task to the back of the run queue rather than re-polling inline, preventing a single greedy task from starving others. See the [tokio tutorial on `yield_now` / cooperative scheduling](https://tokio.rs/tokio/tutorial/async).

## 2. The I/O driver (reactor)

**Backend = mio.** Tokio's I/O driver wraps a `mio::Poll` (feature-gated `mio/os-poll`, `mio/os-ext`, `mio/net`). mio itself selects **epoll** (Linux), **kqueue** (macOS/BSD), **IOCP** (Windows), and **event ports** (Solaris/illumos). Tokio gets the OS backend transitively, so the driver is readiness-based on Unix.

- The `runtime::io::Driver` struct: `poll: mio::Poll`, `events`, plus a `signal_ready` flag. Constructor `Driver::new` builds `mio::Poll::new()`, a `mio::Waker` (token `TOKEN_WAKEUP`), and a `mio::Registry` clone.

**Per-resource state: `ScheduledIo`.** Each registered source is backed by a `ScheduledIo` holding an `AtomicUsize` **readiness** packed as `[shutdown(1 bit) | driver tick(15 bits) | readiness(16 bits)]` and a list of `Waiter`s (waiting task + its interest).

**When a resource registers.** Registration is **lazy / on first use**: `PollEvented`'s `Registration::new_with_interest_and_handle` calls `Handle::add_source`, which allocates a `ScheduledIo` from a slab and calls `mio::Registry::register(source, token, interest)`. The `RawFd`/pointer is used as the mio token so the driver can look the resource up directly.

**Readiness model → wake path.** The driver is readiness-based, not completion-based (unlike io_uring):
1. Worker thread runs the driver each `event_interval` ticks or when parked: `Driver::turn` calls `mio::Poll::poll`, then for each token dispatches `ScheduledIo::set_readiness(Tick::Set, |curr| curr | ready)` and then `io.wake(ready)`.
2. `ScheduledIo::wake` scans its `Waiters`; for every waiter whose registered `interest` overlaps the ready bits, it **wakes that task's waker** (queuing it into the worker's local run queue / LIFO slot / injection queue).
3. A task that finds the resource *not* ready registers its waker in a `Waiter` on the `ScheduledIo` for its read/write interest and returns `Pending`.

**Edge-triggered + tick guard.** A `tick` incremented each `poll` is stored in readiness; `clear_readiness` only clears readiness bits whose tick matches the current poll, so a readiness event that arrives *after* the task clears is not spuriously lost. This prevents the classic edge-triggered lost-wakeup.

## 3. Time driver (hierarchical timing wheel)

**Structure: 6 levels × 64 slots.** Instead of a binary heap, Tokio's time driver uses a **hierarchical hashed timing wheel**.

- `const NUM_LEVELS: usize = 6;` and per-level `const LEVEL_MULT: usize = 64;`, so `MAX_DURATION = 1 << (6*6) = 2^36 ticks` (~2 years at 1 ms precision). See [`time/wheel/mod.rs#L45-L53`](https://github.com/tokio-rs/tokio/blob/e37e284e4ba14c29359c692fe36a2a623d8255a1/tokio/src/runtime/time/wheel/mod.rs#L42-L53).

- **The levels (1 tick = 1 ms):**
  - Level 0: 64 × 1 ms slots (64 ms range)
  - Level 1: 64 × 64 ms slots (~4 s range)
  - Level 2: 64 × ~4 s slots (~4 min range)
  - Level 3: 64 × ~4 min slots (~4 hr range)
  - Level 4: 64 × ~4 hr slots (~12 day range)
  - Level 5: 64 × ~12 day slots (~2 yr range)

Documented verbatim in the official module docs [`runtime/time/mod.rs#L58-L84`](https://github.com/tokio-rs/tokio/blob/e37e284e4ba14c29359c692fe36a2a623d8255a1/tokio/src/runtime/time/mod.rs#L58-L84).

- **Insertion:** pick the highest level whose slot range can represent the deadline (`level_for` via leading-zero bit tricks), and push onto that slot's intrusive linked list.

- **Expiration / cascading:** each level tracks occupied slots in a `u64` bitfield (`occupied`) so finding the next occupied slot is a `trailing_zeros` / rotate op, not a scan. When the timer reaches a slot, `process_expiration` moves entries to the `pending` list (if level 0, deadline reached → notify wakers) or **cascades** them to the next-lower level.

**Why a wheel and not a binary heap.** All timer ops — insert, cancel, fire — are **O(1)** amortized with a hierarchical wheel, versus **O(log n)** for a binary heap. This matters because Tokio timers are extremely common (timeouts, `sleep`, `Interval`). Rationale documented in the [2018 Tokio blog "New Timer implementation" post](https://tokio.rs/blog/2018-03-timers#a-hierarchical-timer-wheel).

**State sharing:** the wheel is behind a `Mutex` (`InnerState { next_wake, wheel }`) in the main time driver, i.e., a single per-runtime wheel protected by a lock. An **alternative timer** ("for better multicore scalability", unstable, PR #7467) uses a lock-to-shard design.

## 4. Anatomy of `tokio::spawn`

**Task = state machine + header, heap-allocated & boxed.** `tokio::spawn` boxes the future's state machine into a `Box<Cell<T, S>>` where `Cell` = `Core { header: Header, ..., future }` ([`runtime/task/core.rs#L236-L241`](https://github.com/tokio-rs/tokio/blob/e37e284e4ba14c29359c692fe36a2a623d8255a1/tokio/src/runtime/task/core.rs#L236-L241)). The future's state machine is boxed on the heap via the raw-task vtable indirection, enabling `Send + 'static` and cross-thread migration through pointers.

**Task `Header`** contains:
- `state: State` — an atomic `usize` bitfield combining lifecycle bits + ref count.
- `scheduler: S` — back-pointer to the scheduler handle.
- `waker: UnsafeCell<Option<Waker>>` — the cached waker the task's future uses.

**State bits + ref count** (from [`runtime/task/state.rs`](https://github.com/tokio-rs/tokio/blob/e37e284e4ba14c29359c692fe36a2a623d8255a1/tokio/src/runtime/task/state.rs#L17-L61)):
- `RUNNING = 0b0001` — task currently being polled/cancelled.
- `COMPLETE = 0b0010` — future finished and dropped.
- `NOTIFIED = 0b0100` — a `Notified` object exists in some run queue.
- `JOIN_INTEREST = 0b1_000` — a `JoinHandle` exists for this task.
- `JOIN_WAKER = 0b10_000` — controls the join waker slot.
- `CANCELLED = 0b100_000` — task should be dropped.
- `REF_COUNT_MASK = !STATE_MASK` — the high bits are the atomic **ref count**.
- `INITIAL_STATE = (REF_ONE*3) | JOIN_INTEREST | NOTIFIED` — starts with 3 references (task owner, join handle, notified) plus join interest and notified.

**Ref-counting.** The task starts at ref count 3 because it *is* the "OwnedTask"/scheduler holder + the `JoinHandle` + a `Notified`. Any `Waker` clones also add count. Ref-counting protects the task from being freed while wakers/joins still reference it.

**JoinHandle.** `JoinHandle<T>` is a `Future<Output = Result<T, JoinError>>`; awaiting it registers the joiner's waker (guarded by `JOIN_WAKER`) and returns the join output once `COMPLETE` is set and the task is dropped. **Dropping a JoinHandle detaches** the task (clears `JOIN_INTEREST`), letting it run in the background, shedding one ref.

**Scheduling-state transitions.** `Created → Notified → Running ↔ (Pending | Yielding) → Complete → Terminated(dropped)`. `transition_to_running` requires the `RUNNING` bit free; on completion the task's waker is woken so the join handle can observe completion.

## 5. Blocking pool

**`spawn_blocking`.** Offloads a synchronous `FnOnce()` to a dedicated **blocking thread pool** so blocking work doesn't starve worker threads. Returns a `JoinHandle<R>`. **`spawn_blocking` tasks cannot be aborted once started** (they're not async).

- **Pool topology:** blocking threads are *not* pre-created; they are spawned on demand. Two queue variants exist: a classic `LockedImpl { mutex, queue: VecDeque<Task> }` and a newer sharded variant for less contention.
- **Sizing:** `max_blocking_threads`, default **512**; the actual blocking-pool cap is `max_blocking_threads + worker_threads`.
- **Queue behavior:** "When a blocking task is submitted, it is inserted into a queue. If an idle thread is available, one is notified; otherwise, if the cap isn't reached, a new thread is spawned; if neither, the task stays queued... the queue applies no backpressure and could grow unbounded." (Builder::max_blocking_threads docs.)
- **Keep-alive:** idle blocking threads exit after **`KEEP_ALIVE = Duration::from_secs(10)`**; configurable via `thread_keep_alive`.

**`block_in_place` (multi-thread only, panics on current-thread).**
- Semantics: the current worker thread runs the blocking closure **in place**, but first **hands off its worker `Core` (run queue + all state) to a newly-spawned OS thread**, so the scheduler can keep making progress elsewhere while this thread blocks.
- **Requirements/implications:** only valid on multi-thread runtime; **panics on `current_thread`** because there are no other workers to hand off to; outside a runtime it runs the closure normally.
- Also: "any other code running concurrently in the same task will be suspended during `block_in_place`" (e.g., other arms of `join!`).
- Subtle detail: before handing off, the worker **moves its LIFO-slot task into the run queue** so the task remains stealable while blocking.

**Cancellation caveat (v1.5x):** runtime shutdown waits for started `spawn_blocking` tasks (they can't be aborted); use `shutdown_timeout`.

## 6. Current-thread vs multi-thread; builder knobs

**Decision tree** (from official `tokio::runtime` docs): work-stealing? → multi-thread; else need `!Send` futures? → LocalRuntime (`LocalSet`); else → current-thread.

- **Multi-thread:** fixed worker threads (one per core), decentralized work-stealing, supports `spawn_blocking` **and** `block_in_place`. Global queue + per-worker local queues; 256-slot local queue; lifo slot; steal-by-half; dynamic `global_queue_interval` targeting 10 ms.
- **Current-thread:** all tasks on the single thread that calls `Runtime::block_on`; maintains a **local FIFO queue + a global FIFO queue**; prefers local, checks global only when local empty **or after 31 local picks in a row** (`global_queue_interval = 31`). **No LIFO slot.** No work stealing. `block_in_place` **panics**. `spawn_blocking` still spawns separate blocking threads.

**Builder knobs:**
- `worker_threads(n)` — multi-thread only. Default = `num_cpus`. Panics if 0. Overrides env `TOKIO_WORKER_THREADS`.
- `max_blocking_threads(n)` — blocking pool cap, default **512**; does not count worker threads.
- Other knobs: `thread_keep_alive` (blocking thread idle timeout), `enable_io`/`enable_time`/`enable_all` (defaults: io **off**, time **off**; `#[tokio::main]` calls `enable_all`), `nevents` (1024), `disable_lifo_slot` (unstable), `enable_eager_driver_handoff` (unstable).

## 7. Tokio sync primitives

**`mpsc` (bounded/unbounded).** Multi-producer, single-consumer. Internal structure is a **linked list of blocks**, each holding up to `BLOCK_CAP` slots:
- `BLOCK_CAP` = **32** for bounded, **16** for unbounded, **2** on 32-bit/embedded.
- Producers push into the first block; consumer pops from the back; empty blocks are recycled (a `Slab`/pool). Bounded capacity is enforced by an internal **semaphore**.
- Waker handling: the receiver stores pointers in each block for efficient wake in batch.

**`oneshot`.** Single producer → single consumer; simplest channel; a future that completes with a `Result<T, RecvError>`.

**`broadcast` (multi → multi with lagging).** Uses shared-state **ring buffer**; each receiver keeps its own cursor; if a receiver lags past the buffer, `recv` returns `RecvError::Lagged(skipped)`. `Sender::send` returns an error if there are no receivers.

**`watch` (multi → multi, latest only).** Retains only the most recent value; consumers read `borrow()`/`changed()`; internally built on `Notify`.

**`tokio::sync::Mutex` vs `std::sync::Mutex` across await.**
- `tokio::sync::Mutex` provides an **async `lock()`** (returns a guard you can hold **across `.await`**); it's backed by `semaphore::Semaphore` (FIFO/fair permit queue), so waiting tasks **yield** instead of blocking the OS thread.
- `std::sync::Mutex` guard is **not `Send`** and holding it across `.await` can deadlock/panic because a task may be moved between worker threads or another task on the same thread blocks on the same mutex → deadlock. The official `tokio::sync` docs explicitly warn against holding a `std::sync::Mutex` across `await` and recommend `tokio::sync::Mutex` or moving work to `spawn_blocking`. Cost tradeoff: async mutex is more expensive; use `std` mutex for short critical sections that don't cross `await`.

**`Notify`.** A bare coordination primitive, a "semaphore-sized" handoff:
- `notify_one()` stores a **single permit** if none is currently stored (so a notify before any `notified()` prevents lost wakeups), else wakes one waiting task.
- `notified().await` waits for / consumes the permit.
- `notify_waiters()` wakes all current waiters but stores no permit.
- Multiple `notify_one()` before any wait coalesce to **one** permit (so it can't be used to count up). `watch` uses `Notify` internally.

## 8. Current state as of 2026

**Latest stable:** **Tokio 1.53.1** (2026-07-20). ~826M total downloads, 65k dependents.

**LTS releases:**
- **1.47.x** — LTS until Sep 2026 (MSRV 1.70).
- **1.51.x** — LTS until Mar 2027 (MSRV 1.71).

**Recent notable changes (2024→2026):**
- **New `LocalRuntime`** (local flavor + `#[tokio::main(flavor = "local")]`, unstable) — a `LocalSet`-backed current-thread variant supporting `spawn_local`.
- **Alternative time driver** — unstable "better multicore scalability" timer (PR #7467).
- **io_uring (unstable):** moved from `--cfg` flags to **cargo feature `io-uring`**; extended `fs` coverage via io_uring (`File::open`, `OpenOptions`, `read`, `write`, renames, `AsyncRead` for `File`, `uring_cmd`, SQPOLL support, fallback when runtime has no IO driver), and a **ring-per-thread** redesign to cut global-mutex contention. Backed by the `io-uring` crate + `slab`, Linux-only. **Stance:** io_uring remains **unstable, opt-in, gated behind `tokio_unstable` + `io-uring`**, Linux-only. Tokio's default I/O model is still the **readiness-based mio/epoll** reactor.
- **Scheduler/blocking-pool hardening:** `spawn_blocking` hang fixes/reverts in 2026; `FastRand` illegal-state fix; `before_park` driver scheduling fix (1.52.4).
- **Metrics:** task schedule latency metric (#7986, v1.53.0).
- **Sync:** `mpsc::{Receiver,UnboundedReceiver}` now **drops its cached waker** on drop; mpsc wake-on-`reserve` permit fix.
- **taskdump:** now supports s390x, added `trace_with()` customization.

**Deprecations (recent):**
- `TcpStream::set_linger` / `TcpSocket::set_linger` — **deprecated** (v1.49.0, Jan 2026).

## ⚠️ Uncertain / conflicting section

1. **Stealable LIFO slot (PR #7431).** The docs.rs `tokio::runtime` module (as-of-latest) still states: "The lifo slot is separate from the local queue, so **other worker threads cannot steal the task in the lifo slot**." However, the source at HEAD (`e37e284`) moves the LIFO slot into `queue::Inner` as an `AtomicNotified` supported by a `Steal` side — i.e., **HEAD appears to already make the LIFO slot stealable**, contradicting the published module docs. **→ If quoting the docs' "lifo slot cannot be stolen," verify against the exact tokio version being documented.** This is the single biggest "out-of-date-doc-vs-source" hazard.
2. **`MAX_DURATION` in the timer wheel.** Source shows `MAX_DURATION = 1 << (BITS_PER_LEVEL * NUM_LEVELS)`; older docs show a `- 1` off-by-one. Treat "max sleep ≈ 2 years" as correct, exact boundary as unverified.
3. **`nevents` default for the I/O driver.** Source `Builder::new` sets `nevents: 1024`. Confirm this is the stable documented value if cited as a "knob."
4. **Exact io_uring "default or not" wording.** Rephrase as "unstable, gated behind `tokio_unstable` + `io-uring`, Linux-only" (verified from Cargo/feature gates) rather than as a quoted maintainer stance.
5. **mio backend selection detail.** That mio's `os-poll`/`os-ext` selects epoll/kqueue/IOCP/event-ports is well-established mio behavior; verified only the feature gates in tokio's `Cargo.toml`, not the per-OS cfg dispatch in mio's own source.
6. **`UringContext` global vs per-ring.** The benchmark-bearing "ring-per-thread" PR #8249 was still under review when observed; whether it shipped in a particular 1.5x release — treat as unverified unless pinned to the exact version's source.

## Top recommended sources for citations

- `tokio::runtime` module docs (module-level "behavior at the time of writing" section): https://docs.rs/tokio/latest/tokio/runtime/
- `tokio::runtime::Builder`: https://docs.rs/tokio/latest/tokio/runtime/struct.Builder.html
- 2019 scheduler post "Making the Tokio scheduler 10x faster": https://tokio.rs/blog/2019-10-scheduler
- 2018 timer post "New Timer implementation": https://tokio.rs/blog/2018-03-timers
- Queue source: https://github.com/tokio-rs/tokio/blob/e37e284e4ba14c29359c692fe36a2a623d8255a1/tokio/src/runtime/scheduler/multi_thread/queue.rs
- Worker source: https://github.com/tokio-rs/tokio/blob/e37e284e4ba14c29359c692fe36a2a623d8255a1/tokio/src/runtime/scheduler/multi_thread/worker.rs
- Timer wheel: https://github.com/tokio-rs/tokio/blob/e37e284e4ba14c29359c692fe36a2a623d8255a1/tokio/src/runtime/time/wheel/mod.rs
- Task state: https://github.com/tokio-rs/tokio/blob/e37e284e4ba14c29359c692fe36a2a623d8255a1/tokio/src/runtime/task/state.rs

All permalinks use HEAD SHA `e37e284e4ba14c29359c692fe36a2a623d8255a1`.
