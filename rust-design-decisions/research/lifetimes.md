# Lifetimes — verified behavior and error anatomy

Fact sheet for: lifetimes.html. All captures from rustc 1.98.1 (edition 2021).

## What a lifetime IS (and is not)

- A lifetime is a static region constraint relating references — the region
  of the program (a span of the control-flow graph) during which a reference
  is guaranteed to remain valid (its referent is not moved or dropped). It
  is NOT a timer, not a property of the value, not runtime state: it is
  erased entirely at runtime; `'a` names a compile-time region variable.
- &'a T means: "this reference is usable within region 'a, because the
  referent is known to outlive 'a". Constraint form: 'referent: 'a
  (outlives). The compiler solves these inequalities; if no solution, error.
- TRPL ch10.3: "Rust can't tell" whether the reference or the value lives
  longer, hence annotations; and lifetimes are "a construct the compiler
  uses... Every reference in Rust has a lifetime" [trpl-ch10-3]

## E0597 — the classic, captured verbatim

```text
error[E0597]: `s` does not live long enough
 --> e0597.rs:5:13
  |
4 |         let s = String::from("hello");
  |             - binding `s` declared here
5 |         r = &s;
  |             ^^ borrowed value does not live long enough
6 |     }
  |     - `s` dropped here while still borrowed
7 |     println!("{r}");
  |                - borrow later used here
```

- Read the anatomy in this order, not top-to-bottom: (1) binding declared;
  (2) borrowed; (3) dropped while still borrowed; (4) borrow LATER USED.
  The killer is (4): if `r` were never used after line 6, NLL would shrink
  the borrow and accept the program. Most trial-and-error flailing comes
  from reading E0597 as "the scope is wrong" instead of "the borrow outlives
  the value BECAUSE of this later use".

## E0106 — struct holding a reference, captured verbatim

```text
error[E0106]: missing lifetime specifier
 --> e0106_missing.rs:2:11
  |
2 |     text: &str,
  |           ^ expected named lifetime parameter
  |
help: consider introducing a named lifetime parameter
  |
1 ~ struct Parser<'a> {
2 ~     text: &'a str,
```

- Why structs need annotations but functions often don't: elision rules
  exist for fn signatures only (Reference: "lifetime arguments can be elided
  in function item, function pointer, and closure trait signatures"
  [ref-elision]). A struct can be used in arbitrary contexts, so the
  compiler demands the constraint be stated once, in the type.

## Elision rules (Reference, verified) [ref-elision]

1. Each elided lifetime in input positions becomes a distinct lifetime
   parameter.
2. If there is exactly one lifetime used in the inputs, it is assigned to
   all elided outputs.
3. (methods) If the receiver is &Self or &mut Self, the receiver's lifetime
   is assigned to elided outputs.
- Consequence: `fn first_word(s: &str) -> &str` (rule 2) works;
  `fn longest(a: &str, b: &str) -> &str` is ambiguous — error (verified
  E0106 on the two-input form; the Reference lists it as ILLEGAL).
- Reference examples verified in docs fetch: substr/get_mut expansions.

## E0515 / E0716 — returning locals and temporaries, captured verbatim

```text
error[E0515]: cannot return reference to local variable `s`
 --> e0515.rs:12:5
  |
12 |     &s
  |     ^^ returns a reference to data owned by the current function

error[E0716]: temporary value dropped while borrowed
  --> e0515.rs:15:25
   |
15 |     let w = first_word(&String::from("hello world"));
   |                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^ - temporary value
   |                         is freed at the end of this statement
16 |     println!("{w}");
   |                - borrow later used here
   |
help: consider using a `let` binding to create a longer lived value
```

- E0716 is the #1 lifetime error in practice for learners: a temporary
  lives only to the end of its statement; `let s = String::from(..); let w
  = first_word(&s);` fixes it (rustc itself suggests this).

## Verified compiling examples

- Struct with lifetime: `struct Parser<'a> { text: &'a str }` + generic
  `fn longest_word<'a>(a: &'a str, b: &'a str) -> &'a str` — compiles
  (e0106.rs verified). The single 'a on both inputs and output means the
  result is usable only while BOTH inputs are alive (the conservative
  choice the compiler forces; you can relax with two 'a 'b if the logic
  proves it).
- The struct + fn program prints `hello alpha` — run verified.

## Common misreadings (the flailing patterns)

1. "does not live long enough" read as "move the declaration earlier" —
   the fix is the LATER USE, not the declaration.
2. Adding 'static everywhere — 'static means "valid for the whole program"
   and is only true for data baked into the binary or leaked; the compiler
   rejects most attempts (E0521-class errors).
3. Reading `'a` on the output as creating/bestowing a lifetime — it only
   NAMES a relationship among inputs.
4. Expecting elision in structs/impls (E0106) or trait methods.

## Source IDs

- [rustc-runs] local captures above
- [trpl-ch10-3] https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html
- [ref-elision] https://doc.rust-lang.org/reference/lifetime-elision.html
- [rfc2094] RFC 2094 (NLL; lifetimes as CFG regions) —
  https://rust-lang.github.io/rfcs/2094-nll.html
