# Ownership, moves, drop, Copy/Clone — verified behavior

Fact sheet for: ownership.html, move-copy-clone.html. All error text captured
with rustc 1.98.1, edition 2021 (see research/environment.md).

## The rules (Rust Reference / TRPL wording)

- TRPL ch.4.1: "Ownership is a set of rules that governs how a Rust program
  manages memory... Some languages have garbage collection...; in other
  languages, the programmer must explicitly allocate and free the memory.
  Rust uses a third approach: Memory is managed through a system of ownership
  with a set of rules that the compiler checks... None of the features of
  ownership will slow down your program while it's running." [trpl-ch4]
- The three rules as TRPL states them: (1) each value in Rust has an owner;
  (2) there can only be one owner at a time; (3) when the owner goes out of
  scope, the value is dropped. [trpl-ch4]

## Move semantics — E0382 (captured verbatim, trimmed only in the middle)

```text
error[E0382]: borrow of moved value: `s`
 --> e0382.rs:4:16
  |
2 |     let s = String::from("hello");
  |         - move occurs because `s` has type `String`, which does not
  |           implement the `Copy` trait
3 |     let t = s;
  |             - value moved here
4 |     println!("{s}");
  |                ^ value borrowed here after move
  |
help: consider cloning the value if the performance cost is acceptable
  |
3 |     let t = s.clone();
  |              ++++++++
```

- Mechanism: assignment of a non-Copy value transfers ownership; the old
  binding becomes statically uninitialized (reads are compile errors, not
  null/dangling reads). At runtime a move of `String` copies 3 words
  (ptr, len, cap) and invalidates the source binding — the heap buffer is not
  copied, and the source does not free it (no double free).
- Why moves are the default (design claim): in C++ `a = b` may run an
  arbitrary copy constructor (deep copy, allocation, surprise cost); Rust
  makes plain assignment always cheap (either a memcpy of the value's own
  bytes or a move) and makes the expensive operation the explicit one,
  `.clone()`. Cite as design rationale from the ownership system's shape +
  TRPL ch.4.1's stack/heap discussion; the pre-1.0 history (unique pointers
  `~T` folded into ordinary moves) is in research/design-history.md.

## Immutable rebinding — E0384 (captured)

```text
error[E0384]: cannot assign twice to immutable variable `x`
 --> e0384.rs:3:5
  |
2 |     let x = 5;
  |         - first assignment to `x`
3 |     x = 6;
  |     ^^^^^ cannot assign twice to immutable variable
help: consider making this binding mutable
  |
2 |     let mut x = 5;
  |         +++
```

## Drop order (Reference destructors.md — primary source)

Reference states: "The fields of a struct are dropped in declaration order.
The fields of the active enum variant are dropped in declaration order. The
elements of an array or owned slice are dropped from the first element to the
last." Variables drop "in reverse order of declaration (for variables) or
creation (for temporaries)". Function parameters are dropped after the body.
[ref-destructors]

Local run (drop_order.rs, PrintOnDrop fields a-first, b-second, c-inner, then
a struct with fields one, two) printed exactly:

```text
end of inner scope
drop c-inner
end of main
drop one
drop two
drop b-second
drop a-first
```

- Locals: reverse declaration order. Inner scope: at its end, before outer
  locals. Struct fields: declaration order (NOT reverse). This asymmetry
  (locals reversed, fields forward) is deliberate: fields are laid out and
  dropped in the order they are written; the stack unwinds top-down.
- A real gotcha verified: a `match shared.lock() { ... }` as the tail
  expression of `main` fails with E0597 because the scrutinee temporary
  (holding a MutexGuard borrowing `shared`) drops AFTER the block's locals
  begin dropping. Fix: bind `let attempt = shared.lock();` first — a named
  local drops before things declared earlier. rustc itself suggests
  "consider adding semicolon after the expression so its temporaries are
  dropped sooner". Capture in research/interior-mutability.md context.
- Assignment drops the overwritten value: `overwritten = PrintOnDrop(...)`
  drops the old value at assignment time (Reference: "Assignment also runs the
  destructor of its left-hand operand, if it's initialized"). [ref-destructors]

## RAII / deterministic destruction

- RAII (Resource Acquisition Is Initialization): the C++ name for tying a
  resource's lifetime to an object's lifetime. Rust generalizes it: Drop +
  scopes make every resource (memory, file, lock) released at a statically
  known point. TRPL ch.15.3 "Dropping a Value Drops the Heap Data" walks
  Box drop freeing the heap allocation. [trpl-ch15-3]
- Key honesty point (from the leakpocalypse, 2015): safe Rust guarantees no
  memory UNSAFETY, but NOT that destructors always run. `std::mem::forget` is
  safe (since Rust 1.0's resolution; thread::scoped was removed and returned
  with JoinGuards). Rc cycles leak destructors forever. Sources in
  research/design-history.md. [leak-history]
- Consequence: never rely on Drop for soundness of unsafe code; use it for
  resource cleanup where a leak is survivable.

## Copy vs Clone — verified distinctions

- Copy is an implicit, shallow, bitwise duplicate performed by assignment /
  argument passing / return; it cannot be user-customized (no method runs);
  it must be total (all fields Copy) and is only valid when the type contains
  no ownership pointers.
- Clone is an explicit method call (`.clone()`), may allocate and deep-copy,
  works for any type that chooses to implement it.
- E0204 capture — trying to derive Copy for a type with a Vec field:

```text
error[E0204]: the trait `Copy` cannot be implemented for this type
 --> shallow_copy_warning.rs:2:8
  |
1 | #[derive(Copy, Clone)]
  |          ---- in this derive macro expansion
2 | struct Owner { name: &'static str, scores: Vec<i32> }
  |        ^^^^^                       ---------------- this field does not implement `Copy`
```

- copy_semantics.rs run: `a=5 b=5` (i32 assignment copies, source still
  readable), `p=1 q=1` (#[derive(Copy)] struct), `inner still: 9` (copying an
  element out of an array leaves the array intact).
- Why Copy must be opt-in and shallow: a bitwise copy of a String would
  duplicate the heap pointer — two owners, double free at drop. So Copy is
  only derivable when every field is Copy (numbers, bools, shared refs, raw
  pointers, and aggregates thereof — never Box/Rc/Vec/String/&mut).
- Copy REPLACES move (a Copy type never moves on assignment); Clone is
  orthogonal (move + explicit duplicate). Clone: supertrait of Copy
  (Reference: "everything that is Copy must also be Clone"). [ref-special-types]
- std Copy types (verified by use): all machine integers, f32/f64, bool, char,
  tuples/arrays of Copy, shared references &, raw pointers, function items,
  PhantomData. Never: &mut T (aliasing two &mut would break XOR), String,
  Vec, Box, Rc, Arc (refcount must be bumped, not copied).

## Source IDs

- [rustc-runs] local rustc 1.98.1 captures above (E0382, E0384, E0204, drop
  order program output, copy_semantics run)
- [trpl-ch4] https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
- [trpl-ch15-3] https://doc.rust-lang.org/book/ch15-03-drop.html (chapter
  title in current TRPL: "Dropping a Value Drops the Heap Data"; verify
  anchor naming in links page — section is part of ch15 Smart Pointers)
- [ref-destructors] https://doc.rust-lang.org/reference/destructors.html
- [ref-special-types] https://doc.rust-lang.org/reference/special-types-and-traits.html
  (Copy semantics: "types whose values can be duplicated simply by copying bits")
- [leak-history] see research/design-history.md
