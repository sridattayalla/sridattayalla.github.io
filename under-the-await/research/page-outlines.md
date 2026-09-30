# Page outlines — the content plan for all 36 pages

Single source of truth for writers. Read this top to bottom before writing.
Authoritative companions (read in this order):

1. `templates/page.html` — the markup contract (comment header explains every
   placeholder and class; copy it for every page you write).
2. `assets/main.js` — the PAGES manifest: exact file paths, ids, titles, blurbs.
3. `tools/terms.json` — the term ledger: which page owns which term.
4. `tools/README.md` — every QA check your pages must pass.
5. `research/*.md` — verified fact sheets with sources and exact constants.

## Global contract (summary — template and checker are authoritative)

- Copy `templates/page.html` for each page; fill title, meta description,
  `data-page`, and everything between the CONTENT-START/END comments. Touch
  nothing else (no head edits, no asset paths, no manifest edits).
- Prose word count per page: **1200–2200**. Checker warns under 1200 and over
  2400; stay in range.
- Code blocks: `<pre><code class="language-X">` where X ∈
  {rust, c, javascript, python, bash, plaintext, go, java}. Terminal output →
  `plaintext`. Shell commands → `bash`. Keep blocks ≤ 30 lines (split longer
  code into staged fragments — better pedagogy anyway).
- Every numeric claim with a unit (5 ms, 256 entries, 6 levels, 10 s, 512
  threads, 8 MB…) needs an HTML comment `<!-- fs: <source> -->` within ±10
  lines. Get numbers from the fact sheets — never invent.
- Diagrams: inline SVG using `.box`, `.arrow`, `.arrow-head`, `.lane`,
  `.label`, `.box.accent`. Every `<svg>` needs `role="img"` plus a
  `<title>`, unless purely decorative (`aria-hidden="true"`). Keep SVGs
  simple and wide (viewBox ~640×N); label boxes with short text.
- Callouts: `.note`, `.warning`, `.pitfall` (auto-labeled). End every page
  with `<aside class="takeaways">` + a `<ul>` of 3–5 bullets.
- Internal links welcome — target exact manifest paths (`../03-rust-async/02-future-trait.html`
  from a part page, `01-foundations/01-…html` only from index, which you are
  not writing). External http(s) links: **only on p05-06**.
- Voice: second person, plain, concrete. Define before use. When you use a
  term whose defining page came earlier, link to it once. Never use a term
  that a LATER page defines — paraphrase instead (checker warns).

## Part arcs and boundaries

- **Part 1 (Machine Foundations)** — the machine every language shares: programs,
  threads, syscalls, blocking, non-blocking, multiplexing. General languages
  (C, Python, JS, bash) — NO Rust, NO async keywords.
- **Part 2 (Concurrency Models)** — the five classic strategies for many
  concurrent things: pools, callbacks, green threads, coroutines, cooperative
  scheduling. Rust may appear only as contrast one-liners; async/await shown
  in JS/Python.
- **Part 3 (Rust Async Building Blocks)** — Future, poll, Waker, Pin, a
  hand-written future, the desugaring, a mini executor. Pure Rust + std.
  Tokio is named but never opened.
- **Part 4 (Tokio Internals)** — the runtime disassembled: overview, task
  anatomy, scheduler, blocking pool, I/O driver, a traced TcpStream read,
  time driver, sync primitives, cancellation.
- **Part 5 (Walkthroughs)** — the same runtime from the user's chair: boot,
  echo server, join!/select!/timeout, pipelines, pitfalls, the full circle.

**Boundary briefs (avoid overlap, cross-link instead):**
- p02-05 vs p04-03: p02-05 names run queues, work stealing, yield points in
  general terms (Go/asyncio flavored). p04-03 gives Tokio's exact machinery
  (LIFO slot, local queue capacity, budgets). p04-03 links back to p02-05.
- p03-07 vs p04-01: the mini executor is ~60 lines of std Rust; p04-01 is
  the map of the real thing. p04-01 references the mini executor.
- p04-01 vs p05-01: p04-01 = static architecture (what the parts ARE);
  p05-01 = the boot sequence (what happens, in order, when a program starts).
  Link both ways; do not repeat diagrams.
- p04-06 vs p05-02: p04-06 traces ONE read through the runtime internals;
  p05-02 walks the WHOLE echo server from user code. p05-02 links to p04-06
  instead of re-tracing.
- p03-04/p03-05 vs p04-02: hand-written futures and the desugaring explain
  what a future IS; p04-02 explains what tokio wraps AROUND it.

## Part 1 — Machine Foundations (8 pages)

**p01-01 How a program runs** (`01-foundations/01-how-programs-run.html`)
- What "running" means: instruction pointer, registers, the fetch-execute loop.
- The call stack: frames, return addresses, locals; a stack grows and shrinks
  as functions call and return. C example + ASCII/SVG of frames.
- User space vs kernel space: privilege levels; your program cannot touch
  hardware or other processes.
- The kernel boundary as THE interface — every I/O, every allocation of real
  resources crosses it. Foreshadow: a suspended computation (Part 3) is a
  stack that froze mid-flight.
- Terms owned: call stack, stack frame, registers, user space, kernel space, heap, instruction.

**p01-02 Processes, threads, and context switches** (`02-processes-threads-context-switches.html`)
- Process = address space + file descriptors + at least one thread. Thread =
  own stack + registers, shares the address space. Diagram: two stacks, one heap.
- Context switch mechanics: save registers, swap stack pointer, resume; done
  by the scheduler on a timer tick (preemption) or a blocking syscall.
- Costs: direct (~1–10 µs — fs: fact sheet) and indirect (cache/TLB
  pollution — the hidden cost). Numbers from the fact sheet.
- pthreads example in C (`pthread_create` + join), or Python `threading` if shorter.
- Terms owned: process, thread, context switch, preemptive, mutex, data race.

**p01-03 Syscalls and file descriptors** (`03-syscalls-and-file-descriptors.html`)
- Syscall = a controlled doorway into the kernel (trap instruction); mode
  switch ≠ context switch. The syscall table; errno.
- File descriptors: small integers indexing the kernel's per-process table;
  files, sockets, pipes, epoll instances — everything is an fd.
- `strace` as the X-ray: bash session stracing a tiny program; show
  read/write/close appearing.
- C example: open/read/write/close with error handling on EAGAIN deferred to p01-05.
- Terms owned: syscall, trap, file descriptor.

**p01-04 Blocking I/O and the C10K problem** (`04-blocking-io-and-c10k.html`)
- What blocking really means: your thread enters the kernel, parks on a wait
  queue, the scheduler forgets it until data arrives. Diagram: parked thread.
- Thread-per-connection servers: Python example (socket + thread per conn).
- The arithmetic of C10K (1999 problem statement): 10k threads × 8 MB default
  stacks (fs: fact sheet), scheduler load, memory pressure.
- When blocking is FINE: tens of connections, simplicity wins. Honest framing.
- Terms owned: blocking, C10K.

**p01-05 Non-blocking I/O** (`05-nonblocking-io.html`)
- `O_NONBLOCK`: read on empty socket returns −1 with EAGAIN NOW. C example
  with fcntl.
- Readiness: the kernel's answer changes from "wait" to "not ready yet" —
  two different questions: "is there data?" vs "give me data".
- The busy-poll trap: loop on EAGAIN burns a whole core; show the CPU cost.
- The missing piece: sleep until SOMETHING is ready → hands off to p01-06.
- Terms owned: non-blocking, EAGAIN, readiness, busy-poll.

**p01-06 I/O multiplexing: the readiness model** (`06-io-multiplexing-readiness.html`)
- One thread asks the kernel about MANY fds: select → poll → epoll evolution.
  select: fd_set, O(n) scan, FD_SETSIZE. poll: no 1024 limit, still O(n).
- epoll: kernel keeps the interest list; epoll_wait returns only ready fds —
  O(1)-ish per event. Registration happens once, not per call.
- Full C example: epoll_create/epoll_ctl/epoll_wait echo loop (staged fragments).
- Level-triggered vs edge-triggered (LT re-reports, ET reports once — foreshadow
  tokio's choice; fact sheet).
- Mention kqueue (BSD/macOS) as the sibling. This page is THE foundation for
  everything in Parts 4–5 — make it airtight.
- Terms owned: multiplexing, epoll, level-triggered, edge-triggered.

**p01-07 Readiness vs completion** (`07-readiness-vs-completion.html`)
- Two kernel contract styles: readiness ("you may try now" — epoll) vs
  completion ("here is the finished result" — Windows IOCP, Linux io_uring).
- Why completion sidesteps the who-supplies-the-buffer question; submission
  and completion queues (SQE/CQE ring pairs).
- io_uring sketch: you submit an operation + buffer, kernel completes later.
- Which model Tokio uses on Linux today (readiness via mio/epoll — fs: fact
  sheet) and why: maturity, portability. Diagram: readiness vs completion side-by-side.
- Terms owned: completion, io_uring.

**p01-08 Threads vs events: the tradeoff** (`08-threads-vs-events.html`)
- The ledger of tradeoffs: preemption vs cooperation; MBs-per-stack vs
  bytes-per-task; data races vs inversion of control; blocking hazards vs
  starvation hazards. Table format.
- Latency vs throughput framing; neither is "faster" in general.
- The hybrid: a few OS threads running millions of cheap tasks — the
  destination this book walks toward (Tokio). End-of-part bridge to Part 2.
- No new terms — this page synthesizes.

## Part 2 — Concurrency Models (5 pages)

**p02-01 Thread pools** (`02-concurrency-models/01-thread-pools.html`)
- Amortize thread creation; pool = fixed workers + a work queue. Diagram.
- Sizing: CPU-bound ≈ cores; I/O-bound temptations and why more threads
  eventually re-meet p01-04's arithmetic.
- The blocking ceiling: a parked pool worker still parks (p01-04 link).
  Head-of-line blocking: one slow job delays the queue behind it.
- Examples: Python `ThreadPoolExecutor`, Java `ExecutorService` (short), C pseudo-code.
- Terms owned: thread pool, head-of-line blocking.

**p02-02 Callbacks and event loops** (`02-concurrency-models/02-callbacks-and-event-loops.html`)
- Event loop: one thread + epoll (p01-06 link) + a table of "when fd X is
  ready, call function Y". This is a reactor. Diagram: loop cycle.
- Node.js/libuv as the flagship; JS example: read a file with a callback,
  then three nested callbacks — control flow inversion visible.
- Callback hell: nesting, error handling by convention, no try/catch across
  the boundary. Cooperative by necessity: your callback must return fast
  (fairness, starvation — a long callback starves every other).
- Promises/then as callbacks with syntax; foreshadow async/await (p02-04).
- Terms owned: event loop, callback, callback hell, reactor, cooperative, fairness, starvation.

**p02-03 Green threads** (`02-concurrency-models/03-green-threads.html`)
- Many user-space threads scheduled onto few OS threads (M:N). Each still
  carries a full(ish) stack. Diagram: M goroutines → N OS threads.
- Go's GMP in brief (G goroutine, M machine/OS thread, P processor context)
  — real Go snippets (go func, channel, GOMAXPROCS).
- Java virtual threads (Project Loom) as the same idea arriving in the JVM —
  short Java snippet. Stackful: suspension can happen anywhere (preemptive-ish).
- Costs: stack memory (KBs–MBs each — fs: fact sheet), stack growth/segmented
  stacks, FFI complexity. Stackful term owned here.
- Terms owned: green thread, stackful.

**p02-04 Stackless coroutines** (`02-concurrency-models/04-stackless-coroutines.html`)
- The JS/Python answer: suspend only at marked points (`await`) — no per-task
  stack at all; the compiler stores just the live locals in an object.
- JS: async function = a promise machine; `await` = suspension point. Python:
  coroutine objects driven by the asyncio loop. Real snippets both.
- The suspended coroutine is a VALUE: you can store it, pass it, poll it.
  This is the seed of Rust's Future (bridge to Part 3).
- Function coloring (sync cannot call async); continuation as the general concept.
- Diagram: one coroutine's states vs a green thread's full stack.
- Terms owned: coroutine, stackless, function coloring, continuation.

**p02-05 Cooperative scheduling** (`02-concurrency-models/05-cooperative-scheduling.html`)
- Tasks must yield; the scheduler only runs at suspension points. Contrast
  with preemption (p01-02): no timer interrupt saves you.
- Fairness mechanisms: run queues per worker; steal work from each other
  (work stealing); yield points as the scheduling opportunities.
- Go's preemption points and async Python's loop as concrete policies.
- The contract: tasks must be short between awaits — the rule that will
  become Tokio's budget (foreshadow p04-03, do not detail it).
- End of Part 2 bridge: "Rust chose stackless coroutines — Part 3 shows the
  machinery, Part 4 shows the scheduler."
- Terms owned: run queue, work stealing, yield point.

## Part 3 — Rust Async Building Blocks (8 pages)

**p03-01 The Rust you need for async** (`03-rust-async/01-rust-recap.html`)
- Ownership as moving values; moves matter because a future is MOVED between
  polls. Traits and trait objects (dyn), vtables, generics vs dynamic dispatch.
- `Send`/`Sync` auto traits and why `tokio::spawn` demands `Send` futures
  (workers are different threads). `'static` bounds. Arc vs Rc.
- Closures capturing by move. Drops run when values die — cancellation later
  exploits this (foreshadow p04-09).
- Every concept tied to ONE async consequence — no general Rust tutorial.
- Terms owned: ownership, Send, Sync, Arc, static, trait object, vtable, drop, atomic.

**p03-02 The Future trait and poll** (`03-rust-async/02-future-trait.html`)
- The trait, verbatim: `fn poll(&mut self, cx: &mut Context) -> Poll<T>` and
  `Poll::{Ready, Pending}`. It is lazy: nothing happens until polled.
- The strict contract: return Ready as soon as done; if Pending, the waker
  MUST be registered before returning; poll must be quick and never block.
- Why `&mut self` (a future is a state machine being advanced) — futures are
  state machines (link p02-04).
- A trivial Ready future in code; then a Pending-forever one; poll them by
  hand in a test.
- Terms owned: Future, poll, lazy.

**p03-03 Waker and Context** (`03-rust-async/03-waker-and-context.html`)
- The missing half: who calls poll again? The future receives a Waker in
  Context and must arrange for `wake()` when it can progress.
- `wake()` semantics: schedule a poll (not run immediately); idempotent-ish
  coalescing; wakers are cheap to clone — a reference-counted handle.
- RawWaker/RawWakerVTable exists (one paragraph, no deep dive).
- The wake→poll loop IS the runtime, in miniature — executor, waker, one
  future, a loop (diagram).
- Terms owned: Waker, Context, combinator.

**p03-04 Writing a Future by hand** (`03-rust-async/04-delay-by-hand.html`)
- Build `Delay` with zero async: enum state (Started/Slept/Done), poll
  checking an `Instant`, a waker stashed in an Arc<Mutex<Option<Waker>>> and
  a helper thread that fires it. Full code, staged fragments.
- Walk each poll call at t=0 and t=deadline. What the async keyword will
  automate (bridge to p03-05).
- Pitfall box: what happens if you forget to register the waker (hang).
- Terms owned: none new (uses Future/poll/Waker).

**p03-05 What async/await compiles to** (`03-rust-async/05-async-await-desugaring.html`)
- An async fn returns an anonymous type implementing Future — a compiler-made
  enum: one variant per await point, locals as fields, the current state as
  the discriminant.
- Show a 3-await async fn, then its hand-written equivalent enum + poll
  (mirroring p03-04's structure). Diagram: source line → enum variant.
- `.await` = match on inner poll: Ready(x) → advance state; Pending → return
  Pending. Borrowed locals across awaits → self-references (bridge to p03-06).
- Box<dyn Future> and sizing notes kept brief.

**p03-06 Pin and self-referential futures** (`03-rust-async/06-pin.html`)
- Why: a future holding `&local` across await points has a pointer into
  ITSELF. Moving it breaks the pointer. Diagram before/after a move.
- `Pin<&mut T>`: a promise the pointed value will not move again; `Unpin` as
  the "actually safe to move" auto trait (most plain types are Unpin).
- `Box::pin` / `Pin<Box<T>>` as the practical tool; `pin!` macro existence
  (fact sheet). Tokio stores tasks as pinned allocations (foreshadow p04-02).
- Do NOT attempt a full Pin tutorial: self-referential futures are the 90% case.
- Terms owned: Pin, Unpin, self-referential.

**p03-07 Building a mini executor** (`03-rust-async/07-mini-executor.html`)
- `block_on`: poll once; on Pending, park the thread on a condvar; the waker
  (built with RawWaker vtable) signals it. ~40 lines, full code.
- Extend to many tasks: Vec of boxed futures + a loop polling in turn —
  toy fairness; note this is a run queue in embryo (p02-05 link).
- A mini timer or channel to prove it composes. Diagram: the loop.
- Terms owned: executor, block_on, park/unpark.

**p03-08 Why Rust chose stackless** (`03-rust-async/08-why-stackless.html`)
- The decision ledger: green threads (stackful, anywhere-suspension, KBs-MBs
  per task — link p02-03) vs stackless (marked points only, bytes per task —
  link p02-04). Rust's no-runtime philosophy: std ships the primitive, not a
  scheduler; ecosystems compete (tokio won de facto).
- The costs paid: Pin complexity (p03-06), function coloring (p02-04),
  ecosystem fragmentation. The payoff: millions of tasks, zero-cost
  composition, explicit suspension points.
- Bridge: "Part 4 opens the engine room: tokio's scheduler, drivers, pools."

## Part 4 — Tokio Internals (9 pages)

**p04-01 The Tokio runtime: an overview** (`04-tokio-internals/01-runtime-overview.html`)
- The map: N worker threads (N = cores), each with a local run queue; one
  inject queue; a blocking pool; one I/O driver + one time driver (parked
  workers poll them). THE map diagram of the whole book — spend your diagram
  budget here.
- What `#[tokio::main]` builds (sequence deferred to p05-01 — link, don't repeat).
- Where each piece lives relative to Part 3's concepts: tasks are pinned
  futures (p03-06), the scheduler is the waker consumer (p03-03), drivers are
  epoll wrapped (p01-06).
- Version + facts from the fact sheet (Tokio 1.x, worker default = cores — fs:).
- Terms owned: runtime, driver.

**p04-02 Task anatomy** (`04-tokio-internals/02-task-anatomy.html`)
- `tokio::spawn` allocates a `Task`: header (state bits, waker refcounts,
  owner/scheduler hooks), a schedule function pointer, and the future stored
  INLINE (sized to the future, no extra boxing) — diagram: memory layout.
- JoinHandle = a waker-refcounted side door to the output; dropping it does
  NOT cancel (detached). Task ≠ thread: ~few-hundred bytes vs MBs + a kernel
  object (fs: fact sheet numbers).
- The lifecycle: idle → scheduled → running → (idle | done). State transitions
  as a diagram.
- Terms owned: task, spawn, JoinHandle.

**p04-03 The multi-threaded scheduler** (`04-tokio-internals/03-scheduler.html`)
- Run queue hierarchy: per-worker LOCAL queue (capacity 256, intrusive linked
  list through the task headers themselves — fs:), the GLOBAL inject queue
  (mutex-guarded VecDeque), and the LIFO slot (fast path for
  message-passing patterns, throttled to 3 consecutive uses — fs:).
- Work stealing: idle worker steals HALF a victim's local queue; search order
  (LIFO slot → local → global → steal → park). Diagram: two workers, queues, steal arrow.
- Cooperative budget: 128 polls per task slice, then forced yield — the
  fairness mechanism from p02-05 made concrete; also the tick/park cadence
  when queues are empty.
- When you spawn: task goes to the inject queue (cross-thread), workers
  adopt it. Link p02-05 for the general model.
- Terms owned: scheduler, local queue, LIFO slot, budget, tick.

**p04-04 The blocking pool** (`04-tokio-internals/04-blocking-pool.html`)
- The rule: never park a worker. Blocking work (files, DNS, CPU loops,
  sync libraries) goes to `spawn_blocking` — a SEPARATE pool of OS threads
  (default max 512, keep-alive 10s — fs:), one blocking call per thread.
- `block_in_place`: convert the CURRENT worker into doing blocking work
  (steals/hands off its queue), multi-threaded runtime only — when and why.
- Why not just more workers: scheduler overhead, cache churn (p01-02);
  the pool is deliberately dumb — it's a thread pool (p02-01 link).
- Diagram: workers vs blocking pool side by side.
- Terms owned: blocking pool, spawn_blocking, block_in_place.

**p04-05 The I/O driver** (`04-tokio-internals/05-io-driver.html`)
- The driver is mio over epoll (Linux; kqueue on macOS — fs:): one
  registration per socket, an INTEREST set (readable/writable), and a TOKEN
  mapping registered fd → waker slot.
- The wake path end-to-end: epoll_wait returns token → ScheduledIo's waker
  list → wake() → task to run queue (p04-03) → worker polls the future.
  Diagram: bytes → epoll → token → waker → queue.
- The driver thread question: workers park ON the driver (whoever wakes
  first parks in epoll_wait with a timeout = the next timer deadline).
- Terms owned: I/O driver, interest, mio, token.

**p04-06 TcpStream, end to end** (`04-tokio-internals/06-tcpstream-trace.html`)
- One `stream.read(&mut buf).await`, dissected: poll_read → WouldBlock →
  register interest + store waker in ScheduledIo (readiness bitset, waiter
  list) → Pending. Packet arrives → epoll → token → wake → scheduled →
  poll → Ready(n). Sequence diagram with every hop labeled.
- The exact structures: ScheduledIo readiness bits, waiters, and the
  readv/writev paths (fact sheet). What a second concurrent reader does
  (waiters queue up).
- This page is the Part 4 centerpiece — the moment the whole machine moves.
  User-facing version is p05-02; link, don't overlap.
- Terms owned: AsyncRead, AsyncWrite.

**p04-07 The time driver** (`04-tokio-internals/07-time-driver.html`)
- Why not one sorted list: O(log n) insert + wake-every-tick problems. The
  hierarchical timing wheel: 6 levels × 64 slots; level i advances every
  2^(6i) ms (L0 per-ms, L1 per-64ms, … covers years — fs: exact table).
  Diagram: levels and cascade.
- Insert: compute level+slot, link entry. Tick: advance with the clock,
  firing L0 slots; higher levels CASCADE down as they empty. Deadlines
  fire in O(1) amortized.
- sleep() → a future whose waker fires from the wheel; the wheel bounds the
  I/O driver's park timeout (p04-05 link). time driver owns the clock.
- Terms owned: time driver, timing wheel.

**p04-08 Tokio's sync primitives** (`04-tokio-internals/08-sync-primitives.html`)
- Why not std: a std Mutex guard parks the THREAD — a worker — catastrophic
  (p04-04 link). Tokio's lock PARKS THE TASK: enqueue the waker, release the
  worker. Mutex/RwLock as waiter queues of wakers (diagram).
- Semaphore: permit count + waiter list; `acquire().await`.
- Channels: mpsc bounded (send().await parks the sender when full —
  BACKPRESSURE made mechanical), unbounded (no brake), oneshot (single shot),
  watch (latest-value broadcast), broadcast (fan-out with lagging). Small
  code sample each; diagram for bounded backpressure.
- Notify (the primitive under many of these).
- Terms owned: channel, mpsc, oneshot, watch, broadcast, semaphore, Notify, backpressure.

**p04-09 Cancellation and select!** (`04-tokio-internals/09-cancellation-and-select.html`)
- Cancellation = the future is simply never polled again; Drop runs. At await
  points only (p02-05's yield points). There is no kill signal, no unwind.
- Cancel-safety: what breaks when a future dies mid-operation — partial
  reads consumed, channels drained then dropped, state lost. Rules of thumb
  + a broken-then-fixed example.
- `select!`: polls branches concurrently, FIRST Ready wins, the rest are
  DROPPED (= cancelled) — this is where cancel-safety bites. `biased` mode;
  the loop-with-select pattern. timeout = select against a deadline.
- Diagram: select branching + drop.
- Terms owned: cancel, cancellation safety, select!.

## Part 5 — Walkthroughs (6 pages)

**p05-01 Hello, Tokio: the boot sequence** (`05-walkthroughs/01-boot-sequence.html`)
- From `#[tokio::main]` to your first await completes, in order: macro
  expansion → Runtime::new (workers spawned, drivers created, blocking pool
  lazily armed) → block_on(main) → spawn adoption. Timeline diagram.
- What exists BEFORE main runs; what runs DURING main; what dies at the end
  (shutdown: drain, drop, join). Link p04-01 for the static map (no repeat).
- A tiny instrumented program (spawns + prints worker ids via thread names —
  fact sheet) so readers can WATCH the machinery boot.

**p05-02 A TCP echo server, await by await** (`05-walkthroughs/02-echo-server.html`)
- Complete annotated echo server (bind → accept loop → spawn per conn →
  read/echo/write). Every `.await` gets a margin annotation: which machinery
  it enters (accept → listener waker; read → the p04-06 path; write → its
  sibling). Link p04-06 for the deep trace instead of re-tracing.
- What happens under load: many connections = many tasks on the scheduler
  (p04-03), zero new threads. Graceful shutdown sketch with select!+ctrl_c.
- Full program listing in staged fragments ≤ 30 lines each.

**p05-03 join!, select!, timeout** (`05-walkthroughs/03-join-select-timeout.html`)
- join!: polls children to completion, no spawn — concurrency WITHOUT tasks.
  select!: first winner (recap p04-09 briefly, link). timeout: select against
  the time driver (p04-07 link). Each with a traced example: print the poll
  order.
- Parallelism vs concurrency made visible: join! on ONE worker vs spawned
  tasks on many. When to use which (spawn for independent, join for
  structured batching).
- Terms owned: join!, timeout.

**p05-04 Pipelines: spawn and channels** (`05-walkthroughs/04-pipelines-and-channels.html`)
- A producer/consumer pipeline: generator task → bounded mpsc → worker tasks
  → sink. Code + pipeline diagram with the queue drawn as a bounded box.
- Backpressure OBSERVED: slow the consumer, watch send().await park the
  producer (small demo program + expected output as plaintext block).
- Structured concurrency: owning the JoinSet, awaiting all children,
  propagating failures — the shape asyncio/Trio call structured, in tokio
  terms. fan-in/fan-out patterns.
- Terms owned: structured concurrency.

**p05-05 Pitfalls** (`05-walkthroughs/05-pitfalls.html`)
- Five wrong-right pairs, each: broken code → what the runtime ACTUALLY did
  (trace it through Parts 4's machinery) → fixed code:
  1. blocking in async (std::thread::sleep / a CPU loop) → spawn_blocking
  2. holding a std MutexGuard across .await → tokio::Mutex or restructure
  3. unbounded channel in a fast producer → memory growth → bounded
  4. spawn-and-forget when you meant join → error vanishes → JoinHandle/JoinSet
  5. a select! loop that loses data (cancel-unsafe branch) → restructure
- This page is the "I felt this in production" page — keep every example
  runnable and minimal.

**p05-06 The full-circle mental model** (`05-walkthroughs/06-mental-model.html`)
- ONE big diagram: your .await → poll → Pending → waker → epoll event →
  token → wake → run queue → worker → poll → Ready — every part labeled with
  the page that explained it. The book in one picture.
- The narrative recap: five parts, one sentence of payoff each. "When async
  I/O looks cheap, this is exactly what was saved: not the syscall, the
  thread that didn't park."
- Further reading (external links allowed HERE ONLY): tokio docs, mio,
  io_uring, the C10K paper. 3–5 links max, `<a href>` normal.

## Term ledger by defining page (authoritative: tools/terms.json)

- p01-01: call stack, stack frame, registers, user space, kernel space, heap, instruction
- p01-02: context switch, data race, mutex, preemptive, process, thread
- p01-03: file descriptor, syscall, trap
- p01-04: C10K, blocking
- p01-05: EAGAIN, busy-poll, non-blocking, readiness
- p01-06: edge-triggered, epoll, level-triggered, multiplexing
- p01-07: completion, io_uring
- p02-01: head-of-line blocking, thread pool
- p02-02: callback hell, callback, cooperative, event loop, fairness, reactor, starvation
- p02-03: green thread, stackful
- p02-04: continuation, coroutine, function coloring, stackless
- p02-05: run queue, work stealing, yield point
- p03-01: Arc, Send, Sync, atomic, drop, ownership, static, trait object, vtable
- p03-02: Future, lazy, poll
- p03-03: Context, Waker, combinator
- p03-06: Unpin, Pin, self-referential
- p03-07: block_on, executor, park, unpark
- p04-01: driver, runtime
- p04-02: JoinHandle, spawn, task
- p04-03: LIFO slot, budget, local queue, scheduler, tick
- p04-04: block_in_place, blocking pool, spawn_blocking
- p04-05: I/O driver, interest, mio, token
- p04-06: AsyncRead, AsyncWrite
- p04-07: time driver, timing wheel
- p04-08: Notify, backpressure, broadcast, channel, mpsc, oneshot, semaphore, watch
- p04-09: cancel, cancellation safety, select!
- p05-03: join!, timeout
- p05-04: structured concurrency

Common-word caution: Send/Sync/Arc/static/drop/watch/channel/task/poll/
interest/token/driver are ordinary words too. The checker is case-insensitive
and whole-word. If a warning fires on innocent prose ("the kernel sends a
signal"), rephrase if easy ("the kernel raises a signal"), else note it in
your report — do not contort good prose.
