# C/C++ failure anatomy — the problem Rust was aimed at

Fact sheet for: founding-constraint.html (all five failure anatomies + GC cost discussion).
Every sanitizer report below is a captured local run (gcc 11.4.0 / clang 14.0.0; see
research/environment.md for exact commands).

## Failure 1: dangling stack pointer (return pointer to local)

dangling_stack.c:

```c
int *borrow_local(void) {
    int local = 42;
    return &local;
}
int main(void) {
    int *p = borrow_local();
    printf("value from dead stack slot: %d\n", *p);
}
```

- clang ASan (detect_stack_use_after_return=1): `ERROR: AddressSanitizer:
  stack-use-after-return on address 0x7a9671f00020 ... READ of size 4 ...
  #0 in main dangling_stack.c:8:48 ... Address ... is located in stack of
  thread T0 at offset 32 in frame #0 borrow_local ... This frame has 1 object(s):
  [32, 36) 'local' (line 3) <== Memory access at offset 32 is inside this variable`
- Mechanism: `borrow_local`'s stack frame (including the 4 bytes holding
  `local`) is popped on return; the slot is immediately reusable by any later
  call. The pointer survives; the pointee does not. No language rule stops this:
  the C standard makes the stored pointer indeterminate once the object's
  lifetime ends (C11 draft N1570 6.2.4p2).
- Rust counterpart: E0515 "cannot return reference to local variable" (captured
  in research/lifetimes.md).

## Failure 2: heap use-after-free

use_after_free.c (freed by `free(s)` at line 10, read `s[0]` at line 11):

- gcc ASan: `ERROR: AddressSanitizer: heap-use-after-free on address
  0x502000000010 ... READ of size 4 ... #0 in main use_after_free.c:11 ...
  0x502000000010 is located 0 bytes inside of 12-byte region
  [0x502000000010,0x50200000001c) freed by thread T0 here: ... free ...
  #1 in main use_after_free.c:10 ... previously allocated by ... malloc ...
  #1 in make_scores use_after_free.c:4`
- Mechanism: `free` returns the 12 bytes to the allocator but leaves the
  pointer value in `s`. The read races with allocator reuse: may return stale
  data, may read a freshly-allocated object, may hit unmapped pages (crash).
  Nondeterministic by construction.

## Failure 3: double free

double_free.c (free(buf) at lines 4 and 5):

- gcc ASan: `ERROR: AddressSanitizer: attempting double-free on
  0x502000000010 ... #1 in main double_free.c:5 ... 0x502000000010 is located
  0 bytes inside of 16-byte region ... freed by thread T0 here: ... #1 in main
  double_free.c:4`
- Mechanism: second `free` of the same region corrupts allocator bookkeeping
  (classic exploitation primitive for heap attacks: overlapping allocations).
- Rust counterpart: Drop runs once, at a statically known point; a second drop
  cannot be written in safe Rust (and moves prevent the aliasing that would
  make double-free expressible). E0382 is the visible rule.

## Failure 4: iterator invalidation (realloc moves the buffer)

iterator_invalidation.c:

```c
int *v = malloc(4 * sizeof(int));
int *first = &v[0];
int *bigger = realloc(v, newcap);   // may move the whole buffer
v = bigger;
printf("v moved to %p, first still points at %p\n", ...);
printf("first[0] = %d\n", first[0]);   // ASan: heap-use-after-free
```

- gcc ASan: `heap-use-after-free on address 0x502000000010 ... READ of size 4
  ... #0 in main iterator_invalidation.c:13 ... freed by thread T0 here: ...
  realloc ... #1 in main iterator_invalidation.c:8 ... previously allocated by
  ... #1 in main iterator_invalidation.c:4`
- Printed line before the crash (real run): `v moved to 0x525d63f3f2c0, first
  still points at 0x525d63f3f010` — two different addresses: realloc moved the
  data; `first` now points into a freed region.
- Rust counterpart: E0502 (`v.push(4)` while `&v[0]` is live — captured in
  research/borrowing.md). Same anatomy: Vec::push reallocates; borrow checker
  refuses to keep the reference across the reallocation.

## Failure 5: data race (two threads, one non-atomic counter)

data_race.c: two pthreads each do `counter = counter + 1` 100000 times
(`static long counter`). TSan (ASLR off):

- `WARNING: ThreadSanitizer: data race ... Read of size 8 at ... by thread T2:
  #0 bump data_race.c:6 ... Previous write of size 8 at ... by thread T1 ...
  Location is global 'counter' of size 8 ... SUMMARY: ThreadSanitizer: data race
  data_race.c:6 in bump`
- Lost-update evidence (plain gcc -O0 run, 5 executions): `expected 200000,
  got 173431` / `got 109329` / `got 184752` / `got 149975` / `got 139591`.
- Mechanism: read-modify-write is three steps; interleavings drop increments.
  On relaxed-memory architectures it is worse: without synchronization,
  cross-core visibility is not guaranteed at all (out-of-thin-air values,
  stale reads). C/C++ call this UB; the machine just misbehaves.

## Why GC languages dodge some of this (and at what cost)

- Tracing GCs (JVM, Go, .NET) make every reference valid by construction:
  memory is reclaimed only when no reference can reach it, so dangling
  pointer/use-after-free/double-free are impossible in managed code. Costs
  (details + sources in research/gc-costs.md): a resident runtime with write
  barriers tracking every pointer store; stop-the-world pauses; no
  deterministic destruction (finalizers run "eventually" or never — Java
  deprecated finalization in JEP 421).
- Deterministic destruction matters beyond memory: file handles, locks,
  sockets. GC languages pair the GC with `defer`/`using`/`try-with-resources`
  — manual discipline re-introduced for non-memory resources.
- Rust's position: replace the GC's whole-heap reachability analysis with two
  compile-time rules (ownership + borrowing), keep the machine code
  allocation-for-allocation comparable to C. TRPL: "None of the features of
  ownership will slow down your program while it's running" [trpl-ch4].

## Source IDs

- [asan-local] local sanitizer runs, gcc 11.4.0 / clang 14.0.0 (captures above)
- [tsan-local] local ThreadSanitizer run (capture above)
- [n1570] C11 draft N1570, 6.2.4p2 (object lifetime; pointer value becomes
  indeterminate) — https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf
- [trpl-ch4] TRPL ch.4.1 "What Is Ownership?" —
  https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
- Memory-safety statistics (Microsoft ~70%, Android/Chromium): see
  research/gc-costs.md — do not cite numbers not verified there.
