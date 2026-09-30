# Error handling design — verified behavior

Fact sheet for: error-handling.html. Captures from rustc 1.98.1.

## The two-tier design

- Tier 1, recoverable errors: Result<T, E> — an ordinary enum value
  returned by ordinary control flow. No unwinding, no hidden paths: every
  fallible function's signature says Result.
- Tier 2, unrecoverable bugs: panic! — unwinds (by default), running
  Drops, then aborts the thread (not the process). Verified run
  (panic_unwind.rs): panic inside catch_unwind printed:
  `thread 'main' (4032774) panicked at panic_unwind.rs:5:5:` / `boom`,
  then "dropping inner", "dropping outer-closure" (unwinding RUNS
  destructors — that is RAII surviving failure), then `caught:
  Err(Some("boom"))`, then "main still running".
- Why not exceptions: invisible control flow (any call may throw),
  runtime machinery, and the C++ experience of exception-safety being
  un-auditable at scale. Why not null/errno: the billion-dollar mistake —
  the type system cannot see which calls fail (Tony Hoare's 2009 QCon
  talk "Null References: The Billion Dollar Mistake"). [hoare]
- Why not just Option everywhere: Result carries the E — the error TYPE is
  part of the contract; ? composes via From conversions.

## `?` — controlled propagation (RFC 243)

- RFC 243 "trait-based-exception-handling": "The postfix ? operator can
  be applied to Result values and is equivalent to the current try!()
  macro... Requiring an explicit ? operator to propagate exceptions
  strikes a very pleasing balance between completely automatic exception
  propagation, which most languages have, and completely manual
  propagation." [rfc243]
- ? desugars to: match { Ok(v) => v, Err(e) => return Err(From::from(e)) }
  — the From call is the composition glue (io::Error -> Box<dyn Error> in
  the verified example).
- Verified run (error_result.rs): read_config("does-not-exist.conf")
  prints `error: No such file or directory (os error 2)` (the ? on
  fs::read_to_string propagated io::Error through Box<dyn Error>);
  parse_pair("3","x") prints `Err(ParseIntError { kind: InvalidDigit })`.

## catch_unwind (RFC 1236) and what panic is FOR

- catch_unwind catches unwinding at a boundary — verified above. RFC 1236
  "stabilize-catch-panic" established the mechanism (initially
  std::panic::recover, stabilized as catch_unwind). [rfc1236]
- panic is for violated invariants (your own bug or a dependency's), not
  for expected failure (a missing file is expected; a file that vanishes
  after you stat'd it is a race; a slice index the compiler cannot prove
  is checked and panics on violation).
- Panics are not try/catch: catch_unwind is for FFI boundaries and test
  harnesses, not business logic. Unwinding also makes Drops run — memory
  still freed (that is the difference from abort).

## Unwinding across FFI (RFC 2945)

- RFC 2945 "C-unwind ABI": "Prior to this RFC, any unwinding operation
  that crossed an extern "C" boundary ... caused undefined behavior."
  Since the RFC: with panic=unwind, a Rust panic escaping an extern "C"
  boundary ABORTS (defined, no UB); foreign/forced unwinding across "C"
  remains UB; extern "C-unwind" makes two-way unwinding defined. [rfc2945]
- panic=abort (profile setting) removes unwinding entirely: smaller
  code, no Drop-on-panic, a panic kills the process. Embedded and some
  server configs choose it. The DEFAULT is unwind (std) so destructors
  run.

## Design consequences

- Errors are values: they compose (io::Error -> Box<dyn Error> via From),
  they are documented by types, they cannot be silently ignored (Result
  is #[must_use]; a bare `let _ = f();` is how you opt out explicitly).
- The cost Rust charges: ceremony. match/?, custom error enums, and the
  occasional anyhow/thiserror-shaped library. The escape hatch: panic!
  when the error is truly unrecoverable, catch_unwind at boundaries.

## Source IDs

- [rustc-runs] local captures above (error_result, panic_unwind)
- [rfc243] RFC 243 "trait-based-exception-handling" —
  https://rust-lang.github.io/rfcs/0243-trait-based-exception-handling.html
- [rfc1236] RFC 1236 "stabilize-catch-panic" —
  https://rust-lang.github.io/rfcs/1236-stabilize-catch-panic.html
- [rfc2945] RFC 2945 "C-unwind ABI" —
  https://rust-lang.github.io/rfcs/2945-c-unwind-abi.html
- [hoare] Tony Hoare, "Null References: The Billion Dollar Mistake",
  QCon London 2009 — presentation; summary at
  https://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare/
- [std-result] https://doc.rust-lang.org/std/result/
- [std-panic] https://doc.rust-lang.org/std/panic/ (catch_unwind)
- [book-errors] TRPL ch9 "Error Handling" —
  https://doc.rust-lang.org/book/ch09-00-error-handling.html
