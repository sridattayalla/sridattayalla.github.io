# Unsafe Rust and Pin — verified behavior

Fact sheet for: unsafe.html, pin.html. Captures from rustc 1.98.1.

## Why unsafe exists

- TRPL ch19.1 "Unsafe Rust": "Unsafe Rust exists because, by nature,
  static analysis is conservative. When the compiler tries to determine
  whether or not code upholds the guarantees, it's better for it to reject
  some valid programs than to accept some invalid programs... you use
  unsafe Rust at your own risk." The five superpowers: dereference a raw
  pointer; call an unsafe function; access/modify a mutable static;
  implement an unsafe trait; access union fields. "unsafe doesn't turn off
  the borrow checker." [trpl-ch19-1]
- Rustonomicon: "Safe Rust is the true Rust programming language. If all
  you do is write Safe Rust, you will never endure a dangling pointer, a
  use-after-free, or any other kind of Undefined Behavior." Unsafe is the
  seam where you hand-audit what the checker cannot prove. [nomicon-intro]

## The canonical motivation: split_at_mut

What safe Rust CANNOT express — two &mut into one array, non-overlapping —
captured verbatim (split_at_mut_safe.rs, a hand-written safe version):

```text
error[E0499]: cannot borrow `*slice` as mutable more than once at a time
 --> split_at_mut_safe.rs:4:30
  |
1 | fn split_at_mut(slice: &mut [i32]) -> (&mut [i32], &mut [i32]) {
  |                        - let's call the lifetime of this reference `'1`
4 |     (&mut slice[..mid], &mut slice[mid..])
  |     -------------------------^^^^^--------
  |     |     |                  |
  |     |     |                  second mutable borrow occurs here
  |     |     first mutable borrow occurs here
  |     returning this value requires that `*slice` is borrowed for `'1`
  |
  = help: use `.split_at_mut(position)` to obtain two mutable non-overlapping sub-slices
```

- Same shape at the call site with two indexing borrows (aliasing_handmade.rs,
  also E0499; rustc's help: "use .split_at_mut(position)").
- The compiler rejects it because two `&mut` from one source LOOKS like
  aliasing; that they point at disjoint halves is arithmetic knowledge the
  type system doesn't have. This is the honest boundary of the checker:
  rejecting a valid program to keep the rule simple.

## The std solution — safe API over unsafe

split_at_mut_unsafe.rs (compiles and runs, prints `[100, 2, 3, 200, 5, 6]`):

```rust
use std::slice;
fn split_at_mut(slice: &mut [i32]) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();
    let ptr = slice.as_mut_ptr();
    let mid = len / 2;
    unsafe {
        assert!(mid <= len);
        (
            slice::from_raw_parts_mut(ptr, mid),
            slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}
```

- What the unsafe block inherits: (1) from_raw_parts_mut's safety contract
  — ptr must be valid for `len` aligned elements and the two ranges must
  not overlap (the mid split guarantees it, but WE prove that, not the
  compiler); (2) the produced &muts must not outlive `slice` (they borrow
  it, so the checker still enforces this part). This is the "safe
  abstraction over audited unsafe" pattern the whole std is built on.
  [nomicon-intro] [trpl-ch19-1]

## Invariants you personally inherit when writing unsafe

- Aliasing: never materialize two live &mut to the same location.
- Validity: references must be non-null, aligned, pointing at initialized
  data of the right type; dereferencing a dangling raw pointer is UB.
- Ownership: drop must run exactly once for each value (double-drop via
  from_raw_parts_mut misuse = double free).
- The Rustonomicon's rule: keep unsafe blocks small, wrap them in a safe
  API that checks the preconditions (assert! above), document the contract
  in a // SAFETY: comment. [nomicon]

## Pin — the self-referential problem

- A self-referential struct holds a pointer into its own body (common in
  async: the generated future holds references to its own locals across
  await points; also intrusive lists). Moving the struct to a new address
  leaves the interior pointer dangling — precisely research/c-failures.md
  failure 1, hidden INSIDE a value.
- RFC 2349 (Pin): "A common motivation for this is when a struct contains
  a pointer into its own representation — moving that struct would
  invalidate that pointer. This use case has become especially important
  recently with work on generators." Goal: "provide a reference type
  where the referent is guaranteed to never move before being dropped."
  [rfc2349]

## Verified Pin behavior

- pin_demo.rs (run): a Box<SelfRef> (String + *const String into itself +
  PhantomPinned) built via Box::new then Pin::from(boxed). The stored
  pointer agrees with &self.data (addresses equal); AFTER moving the
  Pin<Box<SelfRef>> to a new binding, the data field's address is
  UNCHANGED and the pointer still agrees; value still readable. Moving a
  Box moves ONE pointer, not the pointee — that is why Pin<Box<T>> is the
  currency of async: the handle can move freely; the pointee is pinned.
- Pin::new on a !Unpin target — refused (pin_demo.rs first version):
  `error[E0277]: PhantomPinned cannot be unpinned` — "required by a bound
  in Pin::<Ptr>::new ... impl<Ptr: Deref<Target: Unpin>> Pin<Ptr>".
  Use Box::pin instead (rustc's own help suggests it).
- get_mut — refused for !Unpin (pin_get_mut_err.rs):
  `error[E0599]: no method named get_mut found for struct Pin<Box<SelfRef>>`
  with the note pointing at `pub const fn get_mut(self) -> &'a mut T where
  T: Unpin`. A &mut would allow std::mem::swap/move — exactly what Pin
  exists to prevent. Unpin (the default for almost every type you write)
  opts a type back OUT of the guarantee.
- Why async needed it: a future suspended at an await point IS a struct
  whose fields include pointers to its own fields; polling it after it
  moved would follow stale self-pointers. Pin<Box<dyn Future>> lets the
  executor hold and move the handle while the future's body stays put.

## Costs and escape hatches

- unsafe costs: audit burden, UB risk, isolation discipline. Everything
  the borrow checker proved must now be argued by hand for that block.
- Pin costs: you cannot move pinned values (even safely); APIs must be
  Pin-aware (Pin<&mut T> instead of &mut T); !Unpin spreads via PhantomPinned.
- Escape hatches: for Pin — Unpin opt-out for types that don't actually
  self-reference; for unsafe — that IS the escape hatch; the discipline
  is minimizing it.

## Source IDs

- [rustc-runs] local captures above
- [trpl-ch19-1] https://doc.rust-lang.org/book/ch19-01-unsafe-rust.html
- [nomicon-intro] https://doc.rust-lang.org/nomicon/meet-safe-and-unsafe.html
- [nomicon] https://doc.rust-lang.org/nomicon/ (working with unsafe,
  split_at_mut in std: https://doc.rust-lang.org/std/primitive.slice.html#method.split_at_mut)
- [rfc2349] RFC 2349 "pin" — https://rust-lang.github.io/rfcs/2349-pin.html
- [std-pin] https://doc.rust-lang.org/std/pin/ (Pin, Unpin, Box::pin)
- [async-book] Asynchronous Programming in Rust, "Pinning" —
  https://rust-lang.github.io/async-book/04_pinning/01_chapter.html
