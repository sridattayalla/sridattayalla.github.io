# Borrowing, aliasing XOR mutability, NLL — verified behavior

Fact sheet for: borrowing.html. Error text captured with rustc 1.98.1 (edition 2021).

## The central rule

- Rust Reference error-index phrasing (E0499 index page): "in Rust, you can
  either have many immutable references, or one mutable reference." [e0499]
- The community name is "aliasing XOR mutability" — a value may be aliased
  (many readers) or mutable (one writer), never both at once. The literal XOR
  phrase is NOT in official docs; concept origin is Niko Matsakis's Nov 2012
  post "Imagine never hearing the phrase 'aliasable, mutable'": "The contract
  is relatively simple: if you are reading, no one is writing, and if you are
  writing, no one else is reading (or writing)." The literal phrase appears in
  the GhostCell paper (ICFP 2021) and Google's comprehensive-rust course.
  [niko-2012] [ghostcell]
- TRPL ch4.2 frames it as the two rules of references: "First, any borrow
  must last for a scope no greater than that of the owner... Second, you may
  have one or the other of these two kinds of borrows, but not both at the
  same time: one or more references (&T) to a resource, exactly one mutable
  reference (&mut T)." [trpl-ch4-2]

## E0502 — iterator invalidation, captured verbatim

```text
error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
 --> e0502_iterator.rs:4:9
  |
3 |     for x in &v {
  |              --
  |              |
  |              immutable borrow occurs here
  |              immutable borrow later used here
4 |         v.push(*x + 10);
  |         ^^^^^^^^^^^^^^^ mutable borrow occurs here
```

- Anatomy: `for x in &v` holds a shared borrow of the Vec across the whole
  loop body (the iterator is alive). `v.push` needs `&mut v`; push may
  reallocate the buffer (same anatomy as C realloc — see
  research/c-failures.md failure 4); every `x` would dangle. Rejected at
  compile time. Same error for the `let first = &v[0]; v.push(4);` shape
  (captured: "immutable borrow occurs here / mutable borrow occurs here /
  immutable borrow later used here", also E0502).

## E0499 — two live &mut, captured verbatim

```text
error[E0499]: cannot borrow `s` as mutable more than once at a time
 --> e0499.rs:4:13
  |
3 |     let a = &mut s;
  |             ------ first mutable borrow occurs here
4 |     let b = &mut s;
  |             ^^^^^^ second mutable borrow occurs here
5 |     a.push('!');
  |     - first borrow later used here
```

- Note the "later used here" annotation: the rejection is *flow-sensitive*.
  If line 5 did not use `a`, this program would compile (see NLL below).

## E0596 / E0506 — mutation through & and assignment while borrowed

```text
error[E0596]: cannot borrow `*r` as mutable, as it is behind a `&` reference
 --> e0596.rs:4:5
  |
4 |     r.push_str("world");
  |     ^ `r` is a `&` reference, so it cannot be borrowed as mutable

error[E0506]: cannot assign to `s` because it is borrowed
 --> e0506.rs:4:5
  |
3 |     let r = &s;
  |             -- `s` is borrowed here
4 |     s = String::from("world");
  |     ^ `s` is assigned to here but it was already borrowed
5 |     println!("{r}");
  |                - borrow later used here
```

## NLL — non-lexical lifetimes (RFC 2094, shipped Rust 2018)

- nll_ok.rs compiles (verified): iterate `&v`, then `v.push(4)` after the
  loop. scope_model.rs also compiles: `let first = &v[0]; println!("{first}");
  v.push(4);` — the borrow of `v[0]` ends at its last use (the println),
  so the later push is fine. Under the pre-2018 "scopes" model both were
  errors; RFC 2094 replaced scope-based checking with control-flow-graph
  based regions.
- RFC 2094 quotes: "Lifetimes in Rust today are quite a bit more flexible
  than scopes (if not as flexible as we might like, hence this RFC)" and
  the observation that requiring the lifetime to be the innermost enclosing
  expression/scope "is typically much bigger than is really necessary or
  desired." [rfc2094]
- Teaching point: a borrow ends at its LAST USE, not at the end of the
  lexical scope. The mental model "the reference lives to the end of the
  block" is the single most common cause of mispredicting the checker.

## What the rule buys (the two kills)

- Iterator invalidation: impossible (E0502 above).
- Data races: two threads cannot both hold `&mut` to the same data, because
  sharing across threads requires Sync (see research/send-sync.md); the
  race in research/c-failures.md failure 5 needs aliased mutation, which
  the type system forbids. TRPL ch16: "We've nicknamed this aspect of Rust
  fearless concurrency." [trpl-ch16]

## Costs and escape hatches

- Cost: doubly-linked lists, graphs, and observers need ceremony (Rc +
  RefCell, indices, arenas). Two-closure patterns that want read-then-write
  need restructuring.
- Sanctioned escape hatches: restructure to end borrows earlier (works most
  of the time); scope the mutation into a block; Cell/RefCell for single-
  thread shared mutation (research/interior-mutability.md); raw pointers in
  unsafe (research/unsafe-pin.md); indexes/handles instead of references.

## Source IDs

- [rustc-runs] local captures above
- [trpl-ch4-2] https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html
- [trpl-ch16] https://doc.rust-lang.org/book/ch16-00-concurrency.html
- [e0499] https://doc.rust-lang.org/error_codes/E0499.html
- [rfc2094] RFC 2094 "non-lexical lifetimes" —
  https://rust-lang.github.io/rfcs/2094-nll.html
- [niko-2012] Niko Matsakis, "Imagine never hearing the phrase 'aliasable,
  mutable'" (Nov 18, 2012) —
  https://smallcultfollowing.com/babysteps/blog/2012/11/18/imagine-never-hearing-the-phrase-aliasable/
- [ghostcell] "GhostCell: Separating Permissions from Data in an
  Object-Oriented Pattern" (ICFP 2021) uses the literal phrase "aliasing XOR
  mutability" — https://dl.acm.org/doi/10.1145/3473573 (arXiv:2107.07281)
- [comprehensive-rust] Google's Comprehensive Rust course,
  "Aliasing XOR mutability" section — https://google.github.io/comprehensive-rust/
