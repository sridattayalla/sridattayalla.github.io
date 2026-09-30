# GC costs and memory-safety statistics — verified

Fact sheet for: founding-constraint.html (the GC side of the trade and
the "why care" numbers). All quotes fetched from the listed URLs.

## Memory-safety statistics

- Microsoft MSRC (2019): "~70% of the vulnerabilities Microsoft assigns a
  CVE each year continue to be memory safety issues" — figure caption in
  "A proactive approach to more secure code" (MSRC Team, 2019-07-16),
  data from Matt Miller's BlueHat IL 2019 talk. The live page has been
  removed; cite the Wayback capture:
  https://web.archive.org/web/20230313171726/https://msrc.microsoft.com/blog/2019/07/a-proactive-approach-to-more-secure-code/
  Body text: "the majority of vulnerabilities fixed and with a CVE
  assigned are caused by developers inadvertently inserting memory
  corruption bugs into their C and C++ code."
- Chromium: "Around 70% of our high severity security bugs are memory
  unsafety problems (that is, mistakes with C/C++ pointers). Half of
  those are use-after-free bugs." — analysis based on "912 high or
  critical severity security bugs since 2015".
  https://www.chromium.org/Home/chromium-security/memory-safety/
  (No publication date on the page — do not claim 2020.)
- Android (2022): "For more than a decade, memory safety
  vulnerabilities have consistently represented more than 65% of
  vulnerabilities across products, and across the industry." From 2019
  to 2022: 76% -> 35% of Android's total vulnerabilities; "Android 13
  is the first Android release where a majority of new code added to the
  release is in a memory safe language."; in 2022 memory-safety bugs
  were still 86% of CRITICAL-severity and 89% of remotely-exploitable
  bugs; "zero memory safety vulnerabilities discovered in Android's
  Rust code" to date.
  https://security.googleblog.com/2022/12/memory-safe-languages-in-android-13.html
  (Google Security Blog, 2022-12-01, Jeff Vander Stoep.)

## GC pause behavior (mainstream runtimes, official sources)

- Oracle HotSpot GC Tuning Guide (JDK 18): describes "the serial,
  stop-the-world collector" — official use of stop-the-world terminology;
  collectors stop all application threads to trace/relocate.
  https://docs.oracle.com/en/java/javase/18/gctuning/introduction-garbage-collection-tuning.html
- Go: "Getting to Go: The Journey of Go's Garbage Collector" (Rick
  Hudson, 2018): "We now have an objective of 500 microseconds stop the
  world pause per GC cycle. Perhaps a little sandbagging here." and
  (March 2017 release) "That dropped us into the sub-millisecond range."
  https://go.dev/blog/ismmkeynote
- These are the ENGINEERING TARGETS of mature runtimes — evidence that
  pauses are inherent to tracing GC and that fighting them is a
  decade-long optimization program, not a solved problem.

## Non-deterministic destruction

- JEP 421 (Deprecate Finalization for Removal, JDK 18):
  "Unpredictable latency — An arbitrarily long time may pass between the
  moment an object becomes unreachable and the moment its finalizer is
  called. In fact, the GC provides no guarantee that any finalizer will
  ever be called." https://openjdk.org/jeps/421
- Consequence for resources: GC languages re-introduce deterministic
  cleanup manually (Java try-with-resources, C# using, Go defer) for
  files/locks/sockets — the discipline Rust's Drop makes automatic.

## Rust's side of the trade (official wording)

- rust-lang.org: "Rust is blazingly fast and memory-efficient: with no
  runtime or garbage collector, it can power performance-critical
  services, run on embedded devices, and easily integrate with other
  languages." https://www.rust-lang.org/
- TRPL ch4.1: "Some languages have garbage collection that regularly
  looks for no-longer-used memory as the program runs; in other
  languages, the programmer must explicitly allocate and free the
  memory. Rust uses a third approach: Memory is managed through a
  system of ownership with a set of rules that the compiler checks. If
  any of the rules are violated, the program won't compile. None of the
  features of ownership will slow down your program while it's running."
  https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
- Do NOT cite "the Rust FAQ" (retired; rust-lang.org/faq 404s) and do
  NOT quote "zero-cost abstractions" from the current homepage (phrase
  not present on the fetched page).

## Source IDs

- [msrc-2019] MSRC via Wayback (URL above)
- [chromium-ms] chromium.org memory-safety page (URL above)
- [android-2022] Google Security Blog (URL above)
- [oracle-gc] Oracle JDK 18 GC tuning guide (URL above)
- [go-gc] go.dev blog ismmkeynote (URL above)
- [jep421] openjdk.org/jeps/421
- [rust-homepage] https://www.rust-lang.org/
- [trpl-ch4] TRPL ch4.1 (URL above)
