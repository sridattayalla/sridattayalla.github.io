# Rust Async Building Blocks — Verified Fact Sheet

**Verification date:** Sep 2026 · **Docs referenced are Rust 1.98.1** (stable as of 2026-09-03). All signatures verified against `doc.rust-lang.org/stable`.

## 1. `std::future::Future` — definition & poll contract

**Exact signature** (verified, [std 1.98.1](https://doc.rust-lang.org/std/future/trait.Future.html)):

```rust
pub trait Future {
    type Output;

    // Required method
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

**`Poll` enum** ([RFC 2592 §Reference-level](https://rust-lang.github.io/rfcs/2592-futures.html), and [std::task::Poll](https://doc.rust-lang.org/std/task/enum.Poll.html)):
```rust
pub enum Poll<T> {
    Ready(T),
    Pending,
}
```

**`poll` semantics** (verbatim contract from [std `Future::poll`](https://doc.rust-lang.org/std/future/trait.Future.html#tymethod.poll)):
- Returns `Poll::Pending` if not ready, `Poll::Ready(val)` if finished.
- **Once a future has finished, clients should not poll it again.** Polling after completion "may panic, block forever, or cause other kinds of problems" — the trait places no requirements, but it must never be UB.
- When returning `Poll::Pending`, the future **must store a clone of the Waker** from `Context` and must arrange for it to be woken when it can make progress. *"When a future is not ready yet, poll returns `Poll::Pending` and stores a clone of the `Waker` copied from the current `Context`."*
- **Most-recent-waker rule:** *"on multiple calls to `poll`, only the Waker from the Context passed to the most recent call should be scheduled to receive a wakeup."* If a future is polled again with a different waker, it must replace the stored one (e.g. via `waker.clone_from(cx.waker())`).
- **Repolling rule:** *"`poll` should not be called repeatedly in a tight loop – instead, it should only be called when the future indicates that it is ready to make progress (by calling `wake()`)."* Futures are like `epoll`, not `poll(2)`. ([same doc, Runtime characteristics](https://doc.rust-lang.org/std/future/trait.Future.html#runtime-characteristics))
- **`poll` must return quickly and never block**; long work should be offloaded off-thread.
- Futures are **inert** — they do nothing until actively polled ([RFC 2592](https://rust-lang.github.io/rfcs/2592-futures.html#guide-level-explanation); async-book "[Futures are lazy](https://rust-lang.github.io/async-book/02_execution/01_chapter.html)"; [tokio Async in depth](https://tokio.rs/tokio/tutorial/async)).

**Spurious wakes are allowed.** The strongest std wording is "multiple wake-ups may be coalesced into a single poll invocation" ([std Waker::wake](https://doc.rust-lang.org/std/task/struct.Waker.html#method.wake)). Teaching it as "the executor may re-poll a woken future that still returns Pending" is accurate; don't claim a doc line that doesn't exist verbatim. This implicit permission is why a future must re-read its state after a wake rather than assume it's ready.

**Why `Pin<&mut Self>` instead of `&mut Self`** — so generated futures can hold self-referential pointers. Rationale documented in [Pin §"most common... types which require pinning"](https://doc.rust-lang.org/std/pin/struct.Pin.html) and the async-book [Future trait chapter](https://rust-lang.github.io/async-book/02_execution/02_future.html).

## 2. `Waker` & `Context`

`Context<'a>` is a thin carrier: *"Currently, `Context` only serves to provide access to a `&Waker`"* ([std Context](https://doc.rust-lang.org/std/task/struct.Context.html)). It is `!Send + !Sync` (auto traits) — only the waker escapes the poll call, not the context.

**`Waker`** ([std Waker](https://doc.rust-lang.org/std/task/struct.Waker.html)): a handle around a `RawWaker`. Auto-implements `Clone`, `Send`, `Sync`, `Unpin`.

**The wake contract** ([std Waker](https://doc.rust-lang.org/std/task/struct.Waker.html#method.wake)): *"each invocation of `wake()` ... will be followed by at least one `poll()` ... such that the call to `wake()` happens-before the beginning of the invocation of `poll()`."* Multiple wake-ups may be coalesced into one poll. To avoid missed wakeups, all executors must adhere to this requirement ([Wake::Memory Ordering](https://doc.rust-lang.org/std/task/trait.Wake.html#memory-ordering)).

**May be called from any thread:** Waker is `Send + Sync`, and [std Waker docs](https://doc.rust-lang.org/std/task/struct.Waker.html) state: *"a waker may be invoked from any thread, including ones not in any way managed by the executor."* RFC 2592 mandates: *"`Waker::wake()` must wake up an executor even if it is called from an arbitrary thread"* ([RFC 2592, Waking up](https://rust-lang.github.io/rfcs/2592-futures.html#waking-up)).

**`wake` (consumes self) vs `wake_by_ref` (&self)**: `wake(self)` consumes the waker; `wake_by_ref(&self)` doesn't, and "should be preferred to calling `waker.clone().wake()`" ([std Waker](https://doc.rust-lang.org/std/task/struct.Waker.html#method.wake_by_ref)). The `Wake` trait's provided default for `wake_by_ref` clones the `Arc` and calls `wake`; an executor may override it for a cheaper no-alloc wake ([std task::Wake](https://doc.rust-lang.org/std/task/trait.Wake.html)).

**`will_wake`** ([std Waker](https://doc.rust-lang.org/std/task/struct.Waker.html#method.will_wake)): best-effort equality check; *"if this function returns `true`, it is guaranteed that the Wakers will awaken the same task,"* but it may (incorrectly) return false. Used by `clone_from` to skip redundant clones. The async-book timer example notes `will_wake` can be used to avoid re-storing a waker ([async-book, Waker](https://rust-lang.github.io/async-book/02_execution/03_wakeups.html)).

**`RawWaker` / vtable construction** ([std RawWaker](https://doc.rust-lang.org/std/task/struct.RawWaker.html); [RFC 2592](https://rust-lang.github.io/rfcs/2592-futures.html#reference-level-explanation)):
- `RawWaker { data: *const (), vtable: &'static RawWakerVTable }`.
- `RawWakerVTable` has four entries: `clone`, `wake`, `wake_by_ref`, `drop` (the original RFC had three; modern std added `wake_by_ref`). Check https://doc.rust-lang.org/std/task/struct.RawWakerVTable.html for the authoritative current layout.
- Constructed via `RawWaker::new(data, &'static VTable)` (a `const fn`), wrapped into a `Waker` via the **unsafe** `Waker::from_raw`.
- For a `Waker` (cross-thread), `data` must point to a `Send + Sync`-safe type like `Arc<T>`.
- **Safe alternative:** implement the `std::task::Wake` trait on `Arc<Self>` and convert with `Waker::from(Arc<W>)` — no `unsafe`, requires allocation ([std task::Wake](https://doc.rust-lang.org/std/task/trait.Wake.html)). `Wake`'s `wake(self: Arc<Self>)` signature is distinct from `Waker::wake(self)`.

**Clone semantics:** cloning a `Waker` invokes the vtable `clone` fn, which must *retain all resources* for that additional instance; the clone wakes "the same task that would have been awoken by the original" ([RFC 2592](https://rust-lang.github.io/rfcs/2592-futures.html#reference-level-explanation)).

## 3. async/await desugaring — state machine transform

**`async fn` = sugar for a fn returning `-> impl Future`**, and *calling it runs no body — it just constructs and returns the future* ([RFC 2592](https://rust-lang.github.io/rfcs/2592-futures.html); [async-book Future chapter](https://rust-lang.github.io/async-book/02_execution/02_future.html); [tokio](https://tokio.rs/tokio/tutorial/async)).

**State-machine transform** (described authoritatively in the **Rust Reference [Await expressions](https://doc.rust-lang.org/stable/reference/expressions/await-expr.html)** and the stable [Book ch17 §async under the hood](https://rust-lang.github.io/book/ch17-05-traits-for-async.html); conceptually illustrated by [Google Comprehensive Rust](https://google.github.io/comprehensive-rust/concurrency/async/state-machine.html) and [Microsoft RustTraining ch05](https://microsoft.github.io/RustTraining/async-book/ch05-the-state-machine-reveal.html)):

- The async fn body compiles to an **enum-like state machine** with **one variant per suspension point** (each `.await`). Each variant stores the **locals live across that await** plus the awaited sub-future.
- Arguments become fields from creation. The future's `poll` runs a `loop { match state { ... } }` that drives to the next await.
- `.await` desugars to: poll the awaited future; on `Pending`, **early-return `Poll::Pending`**; on `Ready(v)`, keep going. The Rust Reference's normative desugaring:

```rust
match operand.into_future() {
    mut pinned => loop {
        let mut pin = unsafe { Pin::new_unchecked(&mut pinned) };
        match Pin::future::poll(Pin::borrow(&mut pin), &mut current_context) {
            Poll::Ready(r) => break r,
            Poll::Pending => yield Poll::Pending,   // "yield" = return Pending, resume here next poll
        }
    }
}
```

- Note each `.await` first calls `IntoFuture::into_future` on the operand ([await-expr](https://doc.rust-lang.org/stable/reference/expressions/await-expr.html)). The `yield` pseudo-operation returns `Poll::Pending` and resumes at that point on the next poll — exactly one state per suspension point.
- Frame it as the *conceptual* model, not a guaranteed bit-exact mapping — the compiler may add internal states for `?`, drop/cleanup, or optimize/unify variants.

**Underlying generator/coroutine transform:** the actual machinery is the **coroutine (formerly "generator") transform**. Per the Rust Unstable Book [coroutines page](https://dev-doc.rust-lang.org/nightly/unstable-book/language-features/coroutines.html): *"coroutines are currently compiled as state machines. Each `yield` expression will correspond to a different state that stores all live variables over that suspension point."* And *"the main use case of coroutines is an implementation primitive for `async`/`await` and `gen` syntax."*

**One struct, size = max over variants:** The generated future is a single struct whose size is the *maximum* over all state variants, so **locals held across an await are stored in the struct**, and future size grows with the largest live set across any suspend point ([MS RustTraining ch05](https://microsoft.github.io/RustTraining/async-book/ch05-the-state-machine-reveal.html)). Deeply nested/recursive async fns need `Box::pin` for indirection to break recursive types ([Google Comprehensive Rust](https://google.github.io/comprehensive-rust/concurrency/async/state-machine.html)). Values are dropped at state transitions when no longer needed (compiler-inserted drops).

**Eager execution until first Pending:** execution *runs eagerly from the start of `poll` until a `Poll::Pending`* returns, unwinding the whole future chain ([akesson.io visual guide](https://akesson.io/a-visual-guide-to-rust-async/)). Polling nests through `.await` as plain function calls, no queue involvement.

## 4. `Pin` — why, what, Unpin, PhantomPinned

**Why needed:** Generated futures can hold self-referential pointers: a local held across an await is stored in the future struct *by address*; when the composed future embeds a sub-future alongside data the sub-future borrows, moving the struct invalidates the internal pointer. See Book ch17's illustration ("futures... can end up with references to themselves in the fields of any given variant") ([Book ch17](https://rust-lang.github.io/book/ch17-05-traits-for-async.html)) and the akesson.io visual guide ("Move it in memory and `who` dangles — that is what `Pin<&mut Self>` guarantees") ([akesson.io](https://akesson.io/a-visual-guide-to-rust-async/)).

**`Pin` definition** ([std Pin](https://doc.rust-lang.org/std/pin/struct.Pin.html)): *"A pointer which pins its pointee in place."* `Pin<Ptr>` wraps a pointer `Ptr`; it pins the **pointee**, not the pointer. Key facts:
- Same layout/ABI as `Ptr` (zero-cost) ([Pin Layout and ABI](https://doc.rust-lang.org/std/pin/struct.Pin.html#layout-and-abi)).
- The most common pinned types are the compiler-generated `Future`s from `async fn` (doc: "These compiler-generated Futures may contain self-referential pointers").

**`Unpin`** = marker trait opting out of pinning guarantees. Auto-implemented for all types where safe; `!Unpin` types must stay put ([Book ch17](https://rust-lang.github.io/book/ch17-05-traits-for-async.html)). For `Unpin` types, `Pin<&mut Self>` "acts exactly like a regular `&mut Self`" ([Pin](https://doc.rust-lang.org/std/pin/struct.Pin.html)).

**`PhantomPinned`** is the canonical way to make a struct `!Unpin` in safe code (add a `PhantomPinned` field). Documented in [std::marker::PhantomPinned](https://doc.rust-lang.org/std/marker/struct.PhantomPinned.html).

**Why `poll` takes `Pin<&mut Self>`:** because async-fn futures are `!Unpin`, poll must receive a pinned reference ([Pin](https://doc.rust-lang.org/std/pin/struct.Pin.html); [Future trait](https://doc.rust-lang.org/std/future/trait.Future.html)). Constructor `Pin::new` is safe only for `Unpin`; `Pin::new_unchecked` is `unsafe`.

**Moving before the first poll is fine:** Pinning only becomes binding once you start relying on the address stability (once the future can hold internal references pointing into itself). The contract is "a value, once pinned, must remain pinned until dropped" ([Pin::new_unchecked safety](https://doc.rust-lang.org/std/pin/struct.Pin.html#method.new_unchecked)) — pinning happens when the `Pin<&mut Self>` is constructed and the future begins self-referencing. You can move/return/store a freshly-created async future freely *before* pinning+polling it. This is the well-established interpretation of the pinning contract; `Pin::new_unchecked`'s safety docs are the closest authoritative anchor.

## 5. Minimal executor requirements

**The canonical minimal `block_on` is in the std docs themselves** — the `Wake` trait page's example ([std task::Wake, "A basic block_on"](https://doc.rust-lang.org/std/task/trait.Wake.html)):

```rust
struct ThreadWaker(Thread);
impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) { self.0.unpark(); }
}

fn block_on<T>(fut: impl Future<Output = T>) -> T {
    let mut fut = pin!(fut);
    let t = thread::current();
    let waker = Arc::new(ThreadWaker(t)).into();
    let mut cx = Context::from_waker(&waker);
    loop {
        match fut.as_mut().poll(&mut cx) {
            Poll::Ready(res) => return res,
            Poll::Pending => thread::park(),
        }
    }
}
```
The docs explicitly add: *"this example trades correctness for simplicity. In order to prevent deadlocks, production-grade implementations will also need to handle intermediate calls to `thread::unpark` as well as nested invocations."*

**The two minimal designs:**
1. **park/unpark block_on** (above): waker's `wake` = `thread::unpark`; `poll` returns Pending → `thread::park`. No queue needed for a single future.
2. **Waker-driven ready queue** (multi-task): the async-book's executor — a channel of `Arc<Task>`; the waker's `wake_by_ref` **re-enqueues the task's `Arc`** onto the channel; the run loop `recv`s tasks and polls them ([async-book Build an Executor](https://rust-lang.github.io/async-book/02_execution/04_executor.html)).

**What the waker must do: enqueue the task.** The async-book's executor: `ArcWake::wake_by_ref` clones the `Arc` and `try_send`s it to the ready queue.

**Why waking from another thread must be thread-safe:** because `Waker: Send + Sync` and wake may be invoked from *any* thread (e.g., a timer thread or OS callback), the executor's ready-queue + scheduling must be `Sync`/thread-safe; this is exactly why the async-book wraps the future in `Mutex<Option<BoxFuture>>`. The doc says: *"The `Mutex` is not necessary for correctness... Rust isn't smart enough to know that future is only mutated from one thread, so we need to use the Mutex to prove thread-safety."* — in the single-threaded case it's purely for proving `Send`-ness; in a true multi-thread executor the queue itself must be a `Sync` collection.

## 6. async fn in traits

**Stabilized in Rust 1.75 (released Dec 28, 2023)**, announced ([Rust 1.75.0 blog](https://blog.rust-lang.org/2023/12/28/Rust-1.75.0/); [async-fn-rpit-in-traits announcement](https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits/)). This also stabilized return-position `impl Trait` in trait (RPITIT), which `async fn` desugars to.

**Why it works:** `async fn` is sugar for `-> impl Future`, and RPITIT is now allowed in traits.

**dyn-compatibility caveat:** *"Traits that use `-> impl Trait` and `async fn` are not object-safe"* ([announcement](https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits/)). You cannot write `dyn Trait` for them. The `Future` trait itself (no RPITIT) *is* dyn-compatible.

**Send-bound problem:** async trait methods don't auto-add `Send` bounds on the returned futures, which breaks multi-threaded spawning. Official recommendation: use the `trait_variant::make` proc macro (rust-lang org) to generate a `Send` variant.

**`async-trait` crate workaround:** still needed for *dynamic dispatch* and pre-1.75 compat. It rewrites `async fn` into methods returning `Pin<Box<dyn Future + Send + '_>>` ([dtolnay/async-trait](https://github.com/dtolnay/async-trait/)). Costs: heap allocation + dynamic dispatch baked into the trait.

## 7. How executors like Tokio differ from std machinery

**Std provides the trait, not a runtime.** Per RFC 2592: *"This RFC does not include any definition of an executor. It merely defines the interaction between executors, tasks and Futures."* Std supplies `Future`, `Poll`, `Waker`/`Context`/`RawWaker` — the *language-level* machinery. There is no task type or scheduler in std.

**Tokio adds a task abstraction on top:** A Tokio "task" is a runtime object = **the spawned future + its output slot + scheduling metadata** (waker, poll state, ID, an `AbortHandle`, and the runtime's run-queue linkage). Scheduling is driven by the Tokio **work-stealing scheduler** plus an I/O driver (mio/epoll/kqueue) and time driver — none of which exist in std. See [tokio::task module docs](https://docs.rs/tokio/latest/tokio/task/index.html) and the [tokio/async tutorial](https://tokio.rs/tokio/tutorial/async).

**`JoinHandle` semantics** ([docs.rs JoinHandle](https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html)):
- *"An owned permission to join on a task (await its termination)"* — the async analog of `std::thread::JoinHandle`.
- **It is itself a `Future`** with `Output = Result<T, JoinError>` — `T` (task's return) wrapped in `Result` because panics are caught and reported as `JoinError`.
- *"A JoinHandle detaches the associated task when it is dropped"* — dropping it doesn't stop the task; the task keeps running and its return value is lost.
- **Awaiting a `&mut JoinHandle<T>` is cancel-safe** (safe to use in `tokio::select!`).
- The task **starts immediately on `spawn`**, even before you await the JoinHandle (unlike std futures which are inert until polled).
- Key difference from the minimal std executor: Tokio tasks are *not* reserved to one thread; the work-stealing scheduler migrates them across threads, so the future must be `Send + 'static` (hence the `Send` requirement on `tokio::spawn`).

**In a minimal ~100-line executor** (async-book style), the "task" is just `Arc<Task> { future: Mutex<Option<BoxFuture>>, task_sender }` and the waker is derived from the same `Arc` via `ArcWake`.

## 8. Current state as of 2026

**Latest stable: Rust 1.98.1** (2026-09-03) ([Rust releases](https://doc.rust-lang.org/stable/releases.html)). Latest *feature* release was **1.98.0** (2026-08-20). Beta is 1.99.0 (Oct 2026); nightly 1.100.0.

**Async-relevant features stabilized:**
- **Async closures** — `async || {}` and the `async Fn*()` bound-modifier traits **stabilized in Rust 1.85.0** (**Feb 2025**, alongside the **2024 edition**) ([Rust 1.85.0 blog](https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/)). Adds `AsyncFn`, `AsyncFnMut`, `AsyncFnOnce` traits to the prelude. Spec: [RFC 3668](https://rust-lang.github.io/rfcs/3668-async-closures.html).
- **`gen` keyword + `gen {}` blocks** — [RFC 3513](https://rust-lang.github.io/rfcs/3513-gen-blocks.html) merged; `gen` keyword *reserved* in the **2024 edition**. **`gen` blocks are NOT yet stabilized** — only the keyword is reserved; the feature is still behind `#![feature(gen_blocks)]` (tracking issue [rust#117078](https://github.com/rust-lang/rust/issues/117078)).
- **Coroutines** (`Coroutine` trait / `yield`) remain **nightly-only** ([std::ops::Coroutine](https://doc.rust-lang.org/nightly/std/ops/trait.Coroutine.html)) — the underlying transform primitive for async/gen.
- **AsyncIterator** (`Stream` successor, `poll_next`) remains **nightly-only**.
- **Rust 2024 edition is now stable** (with 1.85.0).

## Uncertain / weaker-verified items

1. **Spurious wakes "allowed"**: safe to teach as "the executor may re-poll a woken future that still returns Pending"; the strongest std wording is the coalescing sentence in `Waker::wake` docs.
2. **`RawWakerVTable` field count**: modern std has **4** entries (`clone`, `wake`, `wake_by_ref`, `drop`). Check https://doc.rust-lang.org/std/task/struct.RawWakerVTable.html for the authoritative current layout.
3. **"One state per suspension point" exactness**: confirmed as the *conceptual* model; the compiler may add internal states for `?`, drop/cleanup, or unify variants.
4. **"Moving before first poll is fine"**: standard interpretation of the pinning contract; `Pin::new_unchecked` safety docs are the closest authoritative anchor.
5. **Task internal struct fields**: public doc claims (output slot, ID, abort machinery, detach-on-drop) are verified; byte-level internals live in `tokio/src/runtime/task/{state.rs, join.rs, core.rs}`.

## Source URL index

- Future trait: https://doc.rust-lang.org/std/future/trait.Future.html
- Poll: https://doc.rust-lang.org/std/task/enum.Poll.html
- Waker: https://doc.rust-lang.org/std/task/struct.Waker.html
- Context: https://doc.rust-lang.org/std/task/struct.Context.html
- RawWaker: https://doc.rust-lang.org/std/task/struct.RawWaker.html
- RawWakerVTable: https://doc.rust-lang.org/std/task/struct.RawWakerVTable.html
- Wake trait: https://doc.rust-lang.org/std/task/trait.Wake.html
- Pin: https://doc.rust-lang.org/std/pin/struct.Pin.html
- PhantomPinned: https://doc.rust-lang.org/std/marker/struct.PhantomPinned.html
- Unpin marker: https://doc.rust-lang.org/std/marker/trait.Unpin.html
- Await expression (normative desugaring): https://doc.rust-lang.org/stable/reference/expressions/await-expr.html
- RFC 2592 (futures API): https://rust-lang.github.io/rfcs/2592-futures.html
- RFC 3513 (gen blocks): https://rust-lang.github.io/rfcs/3513-gen-blocks.html
- RFC 3668 (async closures): https://rust-lang.github.io/rfcs/3668-async-closures.html
- async-book: https://rust-lang.github.io/async-book/ — Future chapter (`02_execution/02_future.html`), Waker (`03_wakeups.html`), Executor (`04_executor.html`)
- Book ch17 async-under-the-hood: https://rust-lang.github.io/book/ch17-05-traits-for-async.html
- async fn in traits announcement: https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits/
- async-trait crate: https://github.com/dtolnay/async-trait/
- Rust 1.85.0 (async closures, 2024 edition): https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- Coroutines (nightly): https://dev-doc.rust-lang.org/nightly/unstable-book/language-features/coroutines.html
- Tokio tutorial: https://tokio.rs/tokio/tutorial/async
- Tokio JoinHandle: https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html

Supporting deep-dive posts (mechanistic model, not primary citations): [Google Comprehensive Rust state-machine](https://google.github.io/comprehensive-rust/concurrency/async/state-machine.html), [MS RustTraining ch05](https://microsoft.github.io/RustTraining/async-book/ch05-the-state-machine-reveal.html), [ambiso desugaring](https://ambiso.github.io/desugaring-async-fn/), [akesson.io visual guide](https://akesson.io/a-visual-guide-to-rust-async/).
