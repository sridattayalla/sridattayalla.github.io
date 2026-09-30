# Traits: coherence, orphan rule, dispatch — verified behavior

Fact sheet for: traits.html. Captures from rustc 1.98.1.

## Coherence and the orphan rule

- The problem: impl Display for Vec<u8> in your crate and the same impl in
  someone else's crate = two conflicting impls of one trait for one type
  at link time. No JVM-style runtime selection; Rust resolves method calls
  STATICALLY, so there must be exactly one candidate.
- The rule (Rust Reference, "Orphan rules"): "a trait implementation is
  only allowed if either the trait or at least one of the types in the
  implementation is defined in the current crate. It prevents conflicting
  trait implementations across different crates and is key to ensuring
  coherence." [ref-orphan]
- No accepted RFC introduced the base rule (it predates the RFC process);
  RFC 1023 "rebalancing coherence" and RFC 2451 "re-rebalancing
  coherence" ADJUSTED it (local-type requirement, #[fundamental],
  type-parameter coverage). [rfc1023] [rfc2451]
- Captured verbatim (orphan_rule.rs, impl std::fmt::Display for Vec<u8>):

```text
error[E0117]: only traits defined in the current crate can be implemented for types defined outside of the crate
 --> orphan_rule.rs:1:1
  |
1 | impl std::fmt::Display for Vec<u8> {
  | ^^^^^^^^^^^^^^^^^^^^^^^^-------
  |                            |
  |                            `Vec` is not defined in the current crate
  |
  = note: impl doesn't have any local type before any uncovered type parameters
  = note: for more information see https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules
  = note: define and implement a trait or new type instead
```

- The newtype escape hatch (rustc's own suggestion): wrap in struct
  Wrapper(Vec<u8>) and impl for Wrapper — local type, rule satisfied,
  zero runtime cost (newtype is a compile-time fiction).

## Static dispatch: monomorphization

- Generic fn largest<T: PartialOrd> — verified run (monomorph.rs):
  `max n: 9` / `max s: pear`. The compiler stamps out a specialized copy
  of largest for &i32 and &&str and inlines the comparison — no boxing,
  no vtable. TRPL ch10.1 ("Monomorphization"): "the compiler turns
  generic code into specific code by filling in the concrete types".
  [trpl-ch10-1]
- Cost: binary size and compile time grow with the number of
  instantiations (the C++ templates experience). Benefit: speed identical
  to hand-written per-type code — this is the "zero-cost abstraction"
  claim in its concrete form: the abstraction's price is paid at compile
  time, in code size, not at runtime.

## Dynamic dispatch: dyn Trait

- dyn Trait values are UNSIZED (any concrete type may sit behind them), so
  every reference to one is a fat pointer: (data ptr, vtable ptr).
  Verified run (fat_pointers.rs): `&dyn Shape size: 16`, `&[u32] size:
  16` (also fat), `&Square size: 8` (thin). Vec<Box<dyn Shape>> ran both
  shapes through the vtable (`4.00`, `3.14`).
- RFC 2113 introduced the dyn keyword ("Introduce a new dyn Trait syntax
  for trait objects using a contextual dyn keyword, and deprecate 'bare
  trait' syntax for trait objects") — readability: the syntax now says
  what it costs. [rfc2113]
- Trait objects can only expose object-safe ("dyn-compatible") items —
  no generic methods, no Self-returning methods (the vtable needs one
  known signature; a generic method needs one slot per instantiation).

## The ladder

- generics (mono): fastest, code bloat, caller picks type at compile time
- impl Trait: hides the concrete type, still mono
- dyn Trait: one compiled call site, indirect call, heterogeneous
  collections at runtime
- Choose dyn when the SET of types is open at runtime (plugins, plugin
  error types — the Box<dyn Error> in research/error-handling.md) or
  compile time/code size matters more than a few cycles.

## Costs charged

- Coherence: you sometimes need newtypes or wrapper traits to write the
  impl you want.
- Monomorphization: compile time and binary size.
- dyn: an indirection per call + no inlining across it + object safety
  constraints.

## Source IDs

- [rustc-runs] local captures above (orphan_rule, monomorph, fat_pointers)
- [ref-orphan] https://doc.rust-lang.org/reference/items/implementations.html
- [rfc1023] https://rust-lang.github.io/rfcs/1023-rebalancing-coherence.html
- [rfc2451] https://rust-lang.github.io/rfcs/2451-re-rebalancing-coherence.html
- [rfc2113] https://rust-lang.github.io/rfcs/2113-dyn-trait-syntax.html
- [trpl-ch10-1] https://doc.rust-lang.org/book/ch10-01-syntax.html
- [trpl-ch17-2] https://doc.rust-lang.org/book/ch17-02-trait-objects.html
  (trait objects, "Using Trait Objects That Allow for Values of
  Different Types")
