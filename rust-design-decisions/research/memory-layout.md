# Stack vs heap, String/&str, Vec/&[T], Box — verified behavior

Fact sheet for: stack-and-heap.html, box.html. Captures from rustc 1.98.1.

## Sizes (verified run, x86-64)

```text
&str:       16 bytes (ptr + len)
String:     24 bytes (ptr + len + cap)
&[u32]:     16 bytes (ptr + len)
Vec<u32>:   24 bytes (ptr + len + cap)
Box<u32>:   8 bytes (ptr)
&u32:       8 bytes (ptr)
```

- &dyn Shape: 16 bytes (fat pointer: data ptr + vtable ptr) — verified in
  research/traits.md run.
- Consequence: every reference to unsized data (str, [T], dyn Trait) is a
  TWO-WORD value; every owning handle of growable heap data is THREE words.
  These are compile-time constants; no header, no type tag, no per-value
  bookkeeping.

## The design decision: heap allocation is explicit and typed

- Java/Python: nearly every object is heap-allocated implicitly; `new`
  allocates; GC cleans up. The programmer never sees a pointer, only
  references that are always valid.
- Rust: values live inline by default (in the enclosing value or stack
  frame); heap allocation happens ONLY through a type that says so: Box,
  Vec, String, Rc, Arc... Each is a library type over the same primitive
  (a pointer + ownership policy), not a language feature.
- Why explicit: (1) cost visibility — the reader of a type signature can
  count allocations; (2) deterministic deallocation (research/ownership.md);
  (3) no hidden runtime [rust-homepage].
- TRPL ch4.1 motivates stack/heap for exactly this reason: "whether a value
  is on the stack or the heap affects how the language behaves" [trpl-ch4].

## String vs &str — the canonical pair

- String = owning handle: (ptr, len, cap) on the stack, bytes on the heap;
  grows via reallocation; unique owner.
- &str = borrowed view: (ptr, len) into bytes owned by someone else — a
  String's buffer, a literal in the program binary ('static), a &[u8]
  conversion...
- The same shape holds for Vec<T> vs &[T] and (Box<T> vs &T).
- Teaching payoff: reading `fn f(s: &str)` says "borrows, no allocation,
  no ownership"; `fn f(s: String)` says "takes ownership, will free".
  The signature is a memory contract.
- Deref coercion: &String coerces to &str at call sites (String: Deref<Target=str>),
  so &str parameters accept both — verified implicitly by e0106.rs run.

## Box<T>

- Box = one word: a heap pointer whose pointee it owns. *box creates the
  allocation; drop frees it. Box<u32> is 8 bytes (verified).
- Why no implicit boxing: implicit boxing would mean invisible allocation
  and indirection everywhere (the Java/Python situation); Rust keeps the
  allocation visible in the type.

## Recursive types — E0072, captured verbatim

```text
error[E0072]: recursive type `List` has infinite size
 --> e0072.rs:1:1
  |
1 | enum List { Cons(i32, List), Nil }
  | ^^^^^^^^^             ---- recursive without indirection
  |
help: insert some indirection (e.g., a `Box`, `Rc`, or `&`) to break the cycle
  |
1 | enum List { Cons(i32, Box<List>), Nil }
  |                       ++++    +
```

- Anatomy: the compiler must compute a fixed size for List; a List
  containing a List containing a List... has no finite size. Box<List> is
  one pointer regardless of contents, breaking the cycle. Fixed version
  compiles and runs (box_fix.rs verified: `head 1, tail is a boxed List`).
- This is the ONLY kind of recursion error: Rust sizes types eagerly and
  statically; no tree needs a "tagged union with runtime size" escape.

## Box as ownership transfer

- Box moves like any non-Copy value (E0382 shape); returning/moving a Box
  hands over the allocation; the LAST owner frees. Verified in box_fix.rs
  match: `Cons(head, rest)` destructures by value (moves) — then the box is
  consumed/dropped at scope end.
- Box<dyn Trait>: the fat-pointer idiom (ptr + vtable) — see
  research/traits.md; used in fat_pointers.rs (verified).

## Source IDs

- [rustc-runs] local captures above (layout_sizes.rs, e0072.rs, box_fix.rs)
- [trpl-ch4] https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
- [trpl-ch15-1] https://doc.rust-lang.org/book/ch15-01-box.html ("Using
  Box<T> to Point to Data on the Heap"; the recursive-type/List example)
- [rust-homepage] https://www.rust-lang.org/ — "with no runtime or garbage
  collector, it can power performance-critical services"
