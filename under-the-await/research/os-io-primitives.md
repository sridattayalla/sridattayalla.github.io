# OS Concurrency & I/O Primitives — Verified Fact Sheet

*For the foundations section of the teaching site. All facts sourced to primary documentation. Numbers marked with ~ are measured/approximate and flagged as such.*

## 1. Threads vs Processes

### Shared address space, stacks, TLS
A single process can contain multiple threads that share the same global memory (data + heap segments), but each thread has its **own stack** (automatic variables). POSIX requires threads within a process to share: process ID, open file descriptors, signal dispositions, current directory, umask, and more. Each thread has its own: thread ID, signal mask, `errno`, alternate signal stack, and real-time scheduling policy/priority.

> **Evidence**: [pthreads(7) man page](https://man7.org/linux/man-pages/man7/pthreads.7.html) — "A single process can contain multiple threads, all of which are executing the same program. These threads share the same global memory (data and heap segments), but each thread has its own stack."

**Thread-local storage (TLS)** is exactly the generalization of "own stack": per-thread data like `errno` must be distinct per thread, which is why `pthreads(7)` lists `errno` as a per-thread attribute. A thread-local variable is a fresh copy for each thread (this is the C-level mechanism; the runtime implements it via a per-thread register/FS-segment base on x86-64).

### Default stack sizes
- **Linux (glibc/pthreads): 8 MiB default**. This is *virtual* memory — only the first page is committed to physical RAM; the rest is reserved VMA that grows as the stack is touched. On 32-bit Linux the default is 2 MiB.
- **Windows: 1 MiB default** for the main thread / thread stacks (documented in MSDN's `CreateThread` / stack-size docs).

> **Sources**:
> - Measured & verified: [Eli Bendersky — Measuring context switching for Linux threads](https://eli.thegreenplace.net/2018/measuring-context-switching-and-memory-overheads-for-linux-threads/) — "The default per-thread stack size on Linux is usually 8 MiB" and "the default chosen by 32-bit Linux is 2 MiB." `ulimit -s` shows 8192 (KiB).
> - Stack is virtual-then-committed-when-touched: Linux kernel introduced the limit in 1.3.7 (July 1995, "8MB seems reasonable"), and VMA is only physically committed on page fault.
> - Windows default ~1 MiB: MSDN `Thread Stack Size`/`CreateThread` — well-known Windows stack default of 1 MB. (High confidence; verify against learn.microsoft.com before publishing.)

**Key pedagogic point**: Because it's ~8 MiB of *virtual* address space per thread, 10,000 threads reserve ~80 GB of *virtual* address space. This scales fine on 64-bit (huge address space) but the *committed* memory grows as threads actually use their stacks, and creation cost + scheduling cost grow with thread count. Thread creation is measured at **~5–20 µs** on modern Linux (more below).

### What a context switch saves/restores
Within a *process*, switching between two threads of the same process does **not** need to swap address-space mappings (CR3 is unchanged, TLB stays warm) — only the outgoing thread's register state is saved and the incoming thread's is restored (plus thread-local base, FPU state, etc.). Switching between two *different processes* requires swapping the full address space, which adds TLB-flush and cache-cold costs.

> **Evidence**: [LPC 2013 — User-level threads (R. Danis)](https://blog.linuxplumbersconf.org/2013/ocw/system/presentations/1653/original/LPC%20-%20User%20Threading.pdf) — "The switch into kernel mode (ring0) is surprisingly inexpensive: <50ns round trip. Majority of the context-switching cost attributable to the complexity of the scheduling decision by a modern SMP cpu scheduler."

### Rough cost in microseconds
Measured context-switch costs (direct cost only):
- **~1.2–1.6 µs** per switch (CPU-pinned, single core)
- **~2.2–2.3 µs** per switch when migration allowed

> **Sources**:
> - [Eli Bendersky](https://eli.thegreenplace.net/2018/measuring-context-switching-and-memory-overheads-for-linux-threads/) — "1.2 to 1.5 microseconds per context switch... without pinning, ~2.2 microseconds."
> - [E. Orlov 2023 replication](https://eorlov.org/posts/2023/measuring-context-switching-and-memory-overheads-for-linux-threads/) — "1.3–1.6 µs pinned; ~2.3 µs unpinned."
> - LPC 2013 measured ~1.326 µs/switch (futex-based), ~2.9 µs for a full posix-mutex round-trip benchmark.

These are **direct** costs. The indirect cost (cache/TLB invalidation on migration) is often larger but harder to measure.

### Preemptive time-slice scheduling (Linux model, simple)
Since Linux 2.6.23 the default scheduler is **CFS (Completely Fair Scheduler)**, which replaced the O(1) scheduler. All scheduling is **preemptive**: if a higher-priority thread becomes ready, the running thread is preempted. The default policy is `SCHED_OTHER`. On a time slice, the scheduler picks from the runnable queue based on a *dynamic* priority derived from the nice value, increasing the dynamic priority of threads that are ready but denied CPU (fair progress). Real-time policies are `SCHED_FIFO` (no time slicing; runs until blocked/preempted/yields) and `SCHED_RR` (round-robin, each thread limited to a time quantum).

> **Evidence**: [sched(7) man page](https://man7.org/linux/man-pages/man7/sched.7.html) — "Since Linux 2.6.23, the default scheduler is CFS... All scheduling is preemptive: if a thread with a higher static priority becomes ready to run, the currently running thread will be preempted."

## 2. User vs Kernel Space

### Syscall mechanics & rough cost
A system call is a mode switch: the user thread traps into kernel mode (ring 0), the kernel executes the request on the thread's behalf, then returns to user space. The **mode-switch itself is very cheap (<50 ns round trip)**; the bulk of "syscall cost" is the actual work + scheduler interactions + Spectre/Meltdown mitigations that have made the syscall entry path more expensive on affected hardware.

> **Evidence**: [io_uring(7) man page](https://man7.org/linux/man-pages/man7/io_uring.7.html) — "While system calls may not seem like a significant overhead, in high performance applications, making a lot of them will begin to matter. While workarounds the operating system has in place to deal with Spectre and Meltdown are ideally best done away with, unfortunately, some of these workarounds are around the system call interface, making system calls not as cheap as before."

**A blocking `read()` on a socket with no data available** — step by step:
1. User thread calls `read(fd, buf, len)` → traps into kernel via a syscall (mode switch to ring 0).
2. Kernel looks up the fd, finds the socket has no data in its receive buffer.
3. Because this is a *blocking* read on a blocking socket, the kernel must **suspend the thread**: it moves the thread off the **run queue** (runnable list for its priority) onto a **wait queue** associated with the socket's receive buffer, marking it blocked.
4. The scheduler then **picks another runnable thread** and runs it (a context switch).
5. When a packet arrives, the network driver / softirq finds the thread on the socket's wait queue, moves it back to the run queue, and it is eventually rescheduled.

> **Evidence**: [sched(7)](https://man7.org/linux/man-pages/man7/sched.7.html) — "The scheduler is the kernel component that decides which runnable thread will be executed by the CPU next... the scheduler maintains a list of runnable threads." [read(2)](https://man7.org/linux/man-pages/man2/read.2.html) documents blocking semantics and the `EAGAIN` error when the fd is nonblocking and "the read would block."

**Why this matters for async runtimes**: a blocking-read model means *the OS thread* is parked, and each blocking call consumes an entire OS thread plus a context switch in and out.

## 3. File Descriptors

### What an fd is
A file descriptor is an **integer index into a per-process fd table** (an open-file table). It is the handle through which the process references an "open file description" (the kernel's internal representation of an open file). Sockets, pipes, FIFOs, terminals, and regular files are all referenced by fds. Multiple fds in the same process can refer to the *same* open file description (via `dup`/`dup2`/`fork`/`fcntl(F_DUPFD)`).

> **Evidence**: [epoll(7) man page](https://man7.org/linux/man-pages/man7/epoll.7.html) — "A file descriptor is a reference to an open file description... Whenever a file descriptor is duplicated via dup(2), dup2(2), fcntl(2) F_DUPFD, or fork(2), a new file descriptor referring to the same open file description is created."

### Non-blocking mode and EAGAIN/EWOULDBLOCK
A socket (or other fd) can be marked **nonblocking** via `O_NONBLOCK` (set with `fcntl` or `open`). On a nonblocking socket, a `read()` when no data is available **does not block** — it returns −1 immediately with errno `EAGAIN` or `EWOULDBLOCK`.

> **Evidence**: [read(2) man page](https://man7.org/linux/man-pages/man2/read.2.html) —
> - **EAGAIN**: "The file descriptor fd refers to a file other than a socket and has been marked nonblocking (O_NONBLOCK), and the read would block."
> - **EAGAIN or EWOULDBLOCK**: "The file descriptor fd refers to a socket and has been marked nonblocking (O_NONBLOCK), and the read would block. POSIX.1-2001 allows either error to be returned for this case, and does not require these constants to have the same value, so a portable application should check for both."

### Why busy-polling wastes CPU
The naive alternative to blocking is to repeatedly call `read()` in a loop until data arrives. Each call returns `EAGAIN` and you spin again — this is **busy-polling**. It burns a full CPU core continuously even when there is no work, because the thread is *runnable* the whole time and never sleeps. It wastes cycles that other threads could use, and it's why we need a mechanism to let the OS tell us *when* an fd is ready: I/O multiplexing.

## 4. I/O Multiplexing: select → poll → epoll/kqueue

### select()
`select()` monitors up to `FD_SETSIZE` (1024) fds using fixed-size `fd_set` bitmasks, blocking until one becomes ready for a class of I/O. Limits:
- **fd_set is fixed-size**: `FD_SETSIZE` = 1024, and it cannot monitor fds ≥ 1024. The kernel imposes no fixed limit, but glibc's implementation fixes the type.
- **O(n) scan**: `select()` must scan all three sets to find ready fds, and rebuild the sets each call (the sets are **modified in place** to show ready fds — a "design error avoided in poll and epoll", per the man page).
- Timeout rounded up to system clock granularity.

> **Evidence**: [select(2) man page](https://man7.org/linux/man-pages/man2/select.2.html) — "**WARNING**: select() can monitor only file descriptors numbers that are less than FD_SETSIZE (1024)... this limitation will not change. All modern applications should instead use poll(2) or epoll(7)." And "The implementation of the fd_set arguments as value-result arguments is a design error that is avoided in poll(2) and epoll(7)."

### poll()
`poll()` uses an **array of `struct pollfd`** (fd + events + revents), so there is **no 1024-fd limit** (the limit is `RLIMIT_NOFILE`). But it is still **O(n)**: the kernel scans all n fds on every call to find ready ones, and user space re-scans the whole array to find ready entries.

> **Evidence**: [poll(2) man page](https://man7.org/linux/man-pages/man2/poll.2.html) — "The set of file descriptors to be monitored is specified in the fds argument, which is an array of structures..."

### epoll (Linux; used by tokio)
The **epoll** API has two in-kernel lists: the **interest list** (fds registered) and the **ready list** (fds currently ready). Central efficiency: the kernel **appends ready fds to the ready list as I/O activity happens**, so `epoll_wait()` just *fetches* items already known ready — the kernel does **not** re-scan all registered fds.

Key system calls:
- **`epoll_create1()`** — create an epoll instance, return an fd.
- **`epoll_ctl()`** — `EPOLL_CTL_ADD/MOD/DEL` to manage the interest list.
- **`epoll_wait()`** — wait for events; "can be thought of as fetching items from the ready list."

**Readiness semantics — level-triggered (LT) vs edge-triggered (ET):**
- **LT (default)**: reported ready whenever the fd *is* ready; keeps reporting while data remains. "Simply a faster poll(2)."
- **ET (`EPOLLET`)**: only reports ready on *transitions* (a state change). If you read only part of the available data and wait again, `epoll_wait` **will likely hang** despite data remaining — so ET requires you to **read until `EAGAIN`** with nonblocking fds.

> **Evidence**: [epoll(7) man page](https://man7.org/linux/man-pages/man7/epoll.7.html) — the full ET/LT worked pipe example ("If the rfd... has been added using the EPOLLET flag, the call to epoll_wait(2) done in step 5 will probably hang despite the available data"); "When used as a level-triggered interface... epoll is simply a faster poll(2)"; and "The epoll API... scales well to large numbers of watched file descriptors."

**Memory cost**: each registered fd costs ~160 bytes on 64-bit kernel, and `/proc/sys/fs/epoll/max_user_watches` limits registrations (default is 1/25 of low memory / registration cost).

**Scaling phrasing**: say "avoids the O(n) rescan of select/poll" / "cost scales with events returned, not fds watched" rather than a rigorous "O(1)" — the man page does not formally state O(1).

> **Evidence**: epoll(7) — "The ready list is dynamically populated by the kernel as a result of I/O activity on those file descriptors."

**Anti-thundering-herd**: for ET fds, if multiple threads block in `epoll_wait` on the same epoll fd and one ET fd becomes ready, **only one thread is awoken** — "a useful optimization for avoiding 'thundering herd' wake-ups."

### kqueue (macOS/BSD) and event ports (illumos)
- **kqueue** is the BSD/macOS equivalent — event-based, with `kqueue()`/`kevent()`; it can also monitor process/child events, vnode changes, signals, and timers (not just I/O), and supports EV_CLEAR/EV_DISPATCH semantics.
- **Event ports** (`port_get`) are the illumos/Solaris mechanism (with `PORT_SOURCE_FD` etc.). epoll(7) only names /dev/poll for Solaris; event ports are its modern successor. (Medium-high confidence; cite illumos man page `port_create(3c)` explicitly.)

> **Evidence**: [epoll(7) VERSIONS section](https://man7.org/linux/man-pages/man7/epoll.7.html) — "Some other systems provide similar mechanisms; for example, FreeBSD has kqueue, and Solaris has /dev/poll."

## 5. Readiness vs Completion Models

### Readiness model (epoll/kqueue)
The kernel tells you an fd is *ready* (data is available to read / space to write); **you** still perform the `read()`/`write()` syscall yourself, and **your** buffer is only filled during that call. The operation is not handed to the kernel.

### Completion model (IOCP, io_uring)
The kernel **performs the whole operation** and **writes data directly into the buffer you registered up front** — asynchronously, while you do other work.

**Windows IOCP** (I/O Completion Ports): you issue an overlapped I/O (e.g., WSARecv) with a buffer pointer and an OVERLAPPED structure; the kernel fills your buffer and posts a completion to the completion port, where any thread can dequeue it. This is why completion-based I/O uses **buffer ownership transfer**: the buffer must stay valid and untouched until completion, because the kernel is writing into it concurrently. (Verify the MSDN citation; the mechanism is correct.)

**Linux io_uring**: submission queue (SQ) + completion queue (CQ), **shared ring buffers between user and kernel space**. You place an SQE (e.g., `IORING_OP_READ`) describing `fd`, buffer pointer (`addr`), length (`len`), and offset; the kernel processes it asynchronously and places a CQE on the CQ. The user buffer **must remain valid until completion** precisely because the kernel is reading/writing it while you do other things.

> **Evidence**: [io_uring(7) man page](https://man7.org/linux/man-pages/man7/io_uring.7.html) — "io_uring is a Linux-specific API for asynchronous I/O. It allows the user to submit one or more I/O requests, which are processed asynchronously without blocking the calling process... ring buffers which are shared between user space and kernel space... the pointers to a buffer used as part of a IORING_OP_WRITE or IORING_OP_READ operation must remain valid until completion."

### io_uring adoption status in tokio (as of 2025/2026)
- **Not the default** on Linux. Tokio's primary I/O driver is **mio**, which uses `epoll` (Linux), `kqueue` (BSD/macOS), or `IOCP` (Windows).
- **io_uring support is an experimental/unstable feature**, gated behind `--cfg tokio_unstable` and the `io-uring` cargo feature, enabled at runtime via `Builder::enable_io_uring()`.
- It's currently used mainly for **filesystem I/O** (`fs::read`, `fs::write`, `File::open`, `OpenOptions`, renames) — added in tokio 1.47.0/1.48.0 (Oct 2025). **Networking (TCP/UDP) still uses epoll/mio**; the `io-uring` path falls back to `spawn_blocking` when unsupported.
- Historically, tokio's 2021 stance (Carl Lerme) was that io_uring's API was still evolving and its ring-per-thread model clashed with tokio's work-stealing scheduler, so it shipped a **separate `tokio-uring` crate** rather than changing core tokio.

> **Sources**:
> - [tokio-rs/tokio-uring DESIGN.md](https://github.com/tokio-rs/tokio-uring/blob/master/DESIGN.md) — "Tokio's current Linux implementation uses non-blocking system calls and epoll for event notification... a tuned TCP proxy will spend 70% to 80% of CPU cycles outside of userspace."
> - [tokio.rs blog — Announcing tokio-uring (2021)](https://tokio.rs/blog/2021-07-tokio-uring) — epoll-based TCP proxy spends 70–80% of CPU cycles outside userspace; io_uring eliminates most syscalls.
> - [tokio.rs blog — Announcing Tokio 1.0 (2020)](https://tokio.rs/blog/2020-12-tokio-1-0) — "on Linux, Tokio uses the epoll(7) interface, which notoriously does not work for disk access... By leveraging io_uring, Tokio will be able to provide genuinely asynchronous filesystem operations."
> - [tokio-uring docs](https://docs.rs/tokio-uring) — requires kernel 5.10+; "Ownership of resources are passed to the kernel, which then performs the operation."

## 6. The C10K Problem

### History
**Dan Kegel's "The C10K problem"** (1999) — "It's time for web servers to handle ten thousand clients simultaneously, don't you think? After all, the web is a big place now." In 1999, cdrom.com handled 10,000 simultaneous clients through a Gigabit Ethernet pipe. The point: *hardware was no longer the bottleneck*; the OS and server software were. Kegel argued that at 10,000 clients, per-client cost of a few hundred KB and tens of Kbit/s should be trivially affordable — so the problem was software, not silicon. (Kegel's numbers differ across his own page revisions; quote the ratios qualitatively.)

> **Sources**: [The C10K problem (kegel.com/c10k.html)](https://www.kegel.com/c10k.html)

### Why thread-per-connection falls over at scale
Two concrete costs compound:
1. **Memory per stack**: ~8 MiB virtual per thread (see §1). 10,000 threads → ~80 GB of virtual address space reserved. Even though committed memory is lower, the practical ceiling on Linux is a few thousand to ~30k threads; Kegel explicitly notes you must reduce stack size to avoid running out of virtual memory, and Linux limits like `threads-max` (2047 default on old 2.4) and `max_map_count` bite.
2. **Scheduling cost**: hundreds/thousands of runnable threads per core cause heavy context switching. The schedulable limit is roughly a few thousand threads before scheduler overhead + memory become prohibitive.

> **Evidence**:
> - Kernel thread cost synthesis: "roughly 8 MB of stack VMA (glibc default)... 5–20 µs to create, and 2–10 µs per context switch. The practical limit is a few thousand to tens of thousands of threads per process."
> - [C10K "Limits on threads"](https://www.kegel.com/c10k.html): "you may need to reduce the amount of stack space for each thread to avoid running out of virtual memory."
> - Measured thread limits: [E. Orlov 2023](https://eorlov.org/posts/2023/measuring-context-switching-and-memory-overheads-for-linux-threads/) — "I can create ~32,000 threads before hitting OS limits" on 64-bit; "10,000–30,000 threads depending on configuration."

The C10K page itself catalogs the answer: select/poll/epoll/kqueue + nonblocking sockets + event-driven design, and is the canonical origin document for "handle many connections with few threads."

## 7. Scheduling in Userspace Runtimes

### Run queues, work stealing, "steal half"
Userspace runtimes implement their own schedulers that map user tasks (goroutines/async tasks/virtual threads) onto OS threads. The dominant design is **one run queue per worker thread, plus work stealing**: when a worker's local queue is empty, it **steals work from another worker**. In Go specifically, the thief **steals half of the victim's run queue** (not one item).

> **Evidence**: [Go: Under the Hood — 9.2 Work-Stealing](https://golang.design/under-the-hood/en/part3concurrency/ch09sched/steal/) and [9.1 GMP model](https://golang.design/under-the-hood/en/part3concurrency/ch09sched/model/) — "when some P's local queue and the global queue are both empty, it steals half the work from another P"; also the canonical design doc [Vyukov, Scalable Go Scheduler, 2012 (go.dev/s/go11sched)](https://go.dev/s/go11sched).

### Go's GMP model (goroutines, M:N)
- **G** = goroutine: user code + its (small, growable) stack + execution context.
- **M** = machine: an OS thread that actually executes code.
- **P** = processor: a logical scheduling context (a run queue + resources) bound to an M that wants to run Go code. The number of Ps = `GOMAXPROCS` (default = # of CPUs), so **only GOMAXPROCS threads run Go code at once**.

Go maps many goroutines onto few OS threads → **M:N scheduling**. Goroutine stacks start at a few KB and grow, making creation & switching cheap. The Go runtime **knows every blocking point** and suspends the goroutine *without holding the OS thread*; network I/O is handled by a built-in **netpoller**, so a blocked goroutine doesn't consume a kernel thread.

> **Evidence**:
> - [Go: Under the Hood 9.1](https://golang.design/under-the-hood/en/part3concurrency/ch09sched/model/) — "a goroutine's stack is small and growable (starting at a few KB)... the runtime knows every point that can block... and network I/O is taken over by the built-in network poller, where a blocked goroutine is suspended without holding a thread."
> - [src/runtime/proc.go](https://github.com/golang/go/blob/go1.22.3/src/runtime/proc.go) — "Design doc at https://golang.org/s/go11sched"; documents spinning threads, per-P queues.
> - [Morsing's Go Scheduler blog (2013)](https://morsmachine.dk/go-scheduler.html) — G/M/P triangle diagram; **"it will try to steal about half of the runqueue from another context."**

**Preemption in Go**: cooperative-yield base (channels, Gosched, prologue stack checks) plus **signal-based asynchronous preemption** since Go 1.14, driven by `sysmon` roughly every ~10 ms, as a fairness backstop for tight loops.

> **Evidence**: [Go: Under the Hood 9.4](https://golang.design/under-the-hood/en/part3concurrency/ch09sched/schedule/) — "Go 1.14 introduced signal-based asynchronous preemption (proposal 24543)... sysmon-driven asynchronous preemption about once every 10ms as a fairness backstop."

### Java virtual threads (Project Loom) — modern M:N
Virtual threads are `java.lang.Thread` instances **not tied to a specific OS thread**. The JDK has its own scheduler that **mounts virtual threads onto platform threads (carriers)**, which the OS then schedules. This is explicit **M:N scheduling** (contrast Java's old M:1 "green threads" and platform threads' 1:1).

- When a virtual thread calls a **blocking I/O** operation in the `java.*` API, the runtime performs a **non-blocking OS call** under the hood and automatically **suspends (unmounts) the virtual thread**, freeing its carrier/OS thread for other work. On completion it's resubmitted to the scheduler (mounts on a carrier).
- It's **not cooperative** (no explicit yield), unlike old green threads.
- The JDK scheduler is a **work-stealing ForkJoinPool in FIFO mode**, parallelism default = number of available processors.
- **Pinning limitation**: a virtual thread can't unmount while inside a `synchronized` block or native function; recommended to use `ReentrantLock` for long blocking ops in `synchronized`.

> **Evidence**: [JEP 444: Virtual Threads](https://openjdk.org/jeps/444) — "Virtual threads employ M:N scheduling, where a large number (M) of virtual threads is scheduled to run on a smaller number (N) of OS threads." "The JDK's virtual thread scheduler is a work-stealing ForkJoinPool that operates in FIFO mode." "When code running in a virtual thread calls a blocking I/O operation in the java.* API, the runtime performs a non-blocking OS call and automatically suspends the virtual thread." Pin: "A virtual thread cannot be unmounted during blocking operations when it is pinned."

### How M:N maps onto the OS primitives
All of these (Go GMP, Loom) sit **on top of the OS primitives in §1–§5**: the runtime uses a small pool of OS threads (limited, expensive, each with ~8 MiB stack), multiplexes huge numbers of user tasks onto them with its own run queues + work stealing, and uses **epoll/kqueue/io_uring (readiness/completion)** via a netpoller to know when a socket becomes ready — so a user task can *block on I/O* in user space while its OS thread is freed to run other tasks. The OS thread only sleeps when *all* user tasks are blocked, making thread-per-core/event-loop designs possible.

## 8. OS Timers

### How epoll_wait/kevent timeouts work, and why OS timers are coarse
`select`, `poll`, `epoll_wait`, and `kevent` all take a **timeout** argument; the call blocks until an event, a signal, or the timeout expires. The man pages explicitly flag two sources of coarseness:
1. **The timeout is rounded up to the system clock granularity.**
2. **Kernel scheduling delays mean the blocking interval may overrun** by a small amount.

> **Evidence**:
> - [select(2)](https://man7.org/linux/man-pages/man2/select.2.html) — "the timeout interval will be rounded up to the system clock granularity, and kernel scheduling delays mean that the blocking interval may overrun by a small amount."
> - [poll(2)](https://man7.org/linux/man-pages/man2/poll.2.html) — identical sentence verbatim.

Because the OS timer resolution + scheduler latency make fine-grained timeouts imprecise, and because calling into the OS for every timeout is expensive, **userspace runtimes implement their own timer wheels/heaps** (e.g., tokio's timer, Go's per-P timer heap). Go's runtime comment confirms timers live in userspace and tie into the scheduler/netpoller: "The current timer implementation uses netpoll in a thread with no work available to wait for the soonest timer" — [src/runtime/proc.go](https://github.com/golang/go/blob/go1.22.3/src/runtime/proc.go). This motivates a userspace timer wheel: coarse/few OS-level timerfds + a precise in-memory priority queue of user timers.

## Quick reference table

| Concept | Key numbers | Primary source |
|---|---|---|
| Linux thread default stack | 8 MiB virtual (2 MiB 32-bit) | Bendersky / Linux 1.3.7 |
| Windows thread default stack | ~1 MiB | MSDN (verify) |
| Context switch cost | ~1.2–2.3 µs (direct) | Bendersky, Orlov, LPC 2013 |
| Thread creation | ~5–20 µs | Orlov et al. |
| Syscall mode switch | <50 ns | LPC 2013 |
| select fd limit | 1024 (FD_SETSIZE) | select(2) |
| poll | no 1024 limit, O(n) | poll(2) |
| epoll | ready list, LT vs ET | epoll(7) |
| io_uring / IOCP | completion = kernel writes your buffer | io_uring(7) |
| tokio + io_uring | experimental, fs-only, mio default | tokio blog/DESIGN.md |
| C10K | 10k clients, thread-per-conn fails | kegel.com/c10k |
| Go GMP | G/M/P, steal half, netpoll | go11sched / golang.design |
| Loom | M:N, ForkJoinPool, pinning | JEP 444 |
| OS timer coarseness | rounded to clock granularity | select(2)/poll(2) |

## Uncertain Section

1. **Windows 1 MB default stack size** — well-known default; verify against learn.microsoft.com before publishing. High confidence, unverified-by-fetch.
2. **illumos "event ports"** — epoll(7) only names /dev/poll for Solaris. Event ports are the modern illumos successor; cite illumos man page (`port_create(3c)`) explicitly.
3. **IOCP "kernel writes into your buffer"** — mechanism correct by analogy to io_uring's documented buffer-ownership requirement; verify the MSDN citation.
4. **epoll "O(1)"** — say "avoids the O(n) rescan of select/poll," not a rigorous "O(1)."
5. **Context-switch microsecond numbers** — measured benchmarks, hardware-dependent; consistent range across three independent sources. Treat as indicative.
6. **C10K arithmetic** — Kegel's numbers differ across page revisions; quote ratios qualitatively.
7. **Go "steal half"** — well-established heuristic; Go's implementation is a FIFO ring buffer + LIFO `runnext` slot; keep the nuance.
8. **Java Loom parallelism** — default = available processors, tunable via `jdk.virtualThreadScheduler.parallelism`; maxPoolSize may temporarily exceed when blocking ops capture the carrier. Correct per JEP 444.
