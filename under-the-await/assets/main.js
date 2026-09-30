/*!
 * Under the Await — site shell.
 * Renders the sidebar TOC, prev/next footer, mobile nav and keyboard
 * navigation, and runs vendored highlight.js. Classic script on purpose:
 * no ES modules, no fetch, no network — the site works from file://.
 */
"use strict";

/* Page manifest. A checker parses the JSON between the marker comments —
   keep both markers and the array verbatim. Fields: id, part, title,
   file (site-root-relative), blurb. */
const PAGES = /* PAGES-MANIFEST-START */
[{"id":"index","part":0,"title":"Under the Await","file":"index.html","blurb":"How Tokio really works — a first-principles guide"},
{"id":"p01-01","part":1,"title":"How a program runs","file":"01-foundations/01-how-programs-run.html","blurb":"CPU, registers, the call stack, and the kernel boundary"},
{"id":"p01-02","part":1,"title":"Processes, threads, and context switches","file":"01-foundations/02-processes-threads-context-switches.html","blurb":"What the OS actually switches, and what it costs"},
{"id":"p01-03","part":1,"title":"Syscalls and file descriptors","file":"01-foundations/03-syscalls-and-file-descriptors.html","blurb":"Crossing into the kernel; everything is a file"},
{"id":"p01-04","part":1,"title":"Blocking I/O and the C10K problem","file":"01-foundations/04-blocking-io-and-c10k.html","blurb":"Where threads sleep, and why 10,000 of them hurt"},
{"id":"p01-05","part":1,"title":"Non-blocking I/O","file":"01-foundations/05-nonblocking-io.html","blurb":"EAGAIN, readiness, and the busy-poll trap"},
{"id":"p01-06","part":1,"title":"I/O multiplexing: the readiness model","file":"01-foundations/06-io-multiplexing-readiness.html","blurb":"select, poll, and epoll's ready list"},
{"id":"p01-07","part":1,"title":"Readiness vs completion","file":"01-foundations/07-readiness-vs-completion.html","blurb":"IOCP and io_uring flip the model"},
{"id":"p01-08","part":1,"title":"Threads vs events: the tradeoff","file":"01-foundations/08-threads-vs-events.html","blurb":"Two ways to wait, and what each costs"},
{"id":"p02-01","part":2,"title":"Thread pools","file":"02-concurrency-models/01-thread-pools.html","blurb":"Reusing threads, and where pools stop helping"},
{"id":"p02-02","part":2,"title":"Callbacks and event loops","file":"02-concurrency-models/02-callbacks-and-event-loops.html","blurb":"libuv, Node.js, and callback hell"},
{"id":"p02-03","part":2,"title":"Green threads","file":"02-concurrency-models/03-green-threads.html","blurb":"Go's GMP and Java's virtual threads"},
{"id":"p02-04","part":2,"title":"Stackless coroutines","file":"02-concurrency-models/04-stackless-coroutines.html","blurb":"async/await as state machines in JS and Python"},
{"id":"p02-05","part":2,"title":"Cooperative scheduling","file":"02-concurrency-models/05-cooperative-scheduling.html","blurb":"Fairness, run queues, and work stealing"},
{"id":"p03-01","part":3,"title":"The Rust you need for async","file":"03-rust-async/01-rust-recap.html","blurb":"Ownership, traits, Send/Sync — just the parts async uses"},
{"id":"p03-02","part":3,"title":"The Future trait and poll","file":"03-rust-async/02-future-trait.html","blurb":"One method, two results, strict rules"},
{"id":"p03-03","part":3,"title":"Waker and Context","file":"03-rust-async/03-waker-and-context.html","blurb":"How a future says 'call me back'"},
{"id":"p03-04","part":3,"title":"Writing a Future by hand","file":"03-rust-async/04-delay-by-hand.html","blurb":"A Delay, from scratch"},
{"id":"p03-05","part":3,"title":"What async/await compiles to","file":"03-rust-async/05-async-await-desugaring.html","blurb":"Your async fn is an enum in disguise"},
{"id":"p03-06","part":3,"title":"Pin and self-referential futures","file":"03-rust-async/06-pin.html","blurb":"Why suspended futures must not move"},
{"id":"p03-07","part":3,"title":"Building a mini executor","file":"03-rust-async/07-mini-executor.html","blurb":"Sixty lines from poll to runtime"},
{"id":"p03-08","part":3,"title":"Why Rust chose stackless","file":"03-rust-async/08-why-stackless.html","blurb":"The costs and the payoff"},
{"id":"p04-01","part":4,"title":"The Tokio runtime: an overview","file":"04-tokio-internals/01-runtime-overview.html","blurb":"Scheduler, drivers, and pools in one picture"},
{"id":"p04-02","part":4,"title":"Task anatomy","file":"04-tokio-internals/02-task-anatomy.html","blurb":"What spawn actually allocates"},
{"id":"p04-03","part":4,"title":"The multi-threaded scheduler","file":"04-tokio-internals/03-scheduler.html","blurb":"Run queues, the LIFO slot, and stealing"},
{"id":"p04-04","part":4,"title":"The blocking pool","file":"04-tokio-internals/04-blocking-pool.html","blurb":"spawn_blocking and block_in_place"},
{"id":"p04-05","part":4,"title":"The I/O driver","file":"04-tokio-internals/05-io-driver.html","blurb":"mio, epoll, and the wake path"},
{"id":"p04-06","part":4,"title":"TcpStream, end to end","file":"04-tokio-internals/06-tcpstream-trace.html","blurb":"One read, traced through the whole runtime"},
{"id":"p04-07","part":4,"title":"The time driver","file":"04-tokio-internals/07-time-driver.html","blurb":"Sleeps and the hierarchical timing wheel"},
{"id":"p04-08","part":4,"title":"Tokio's sync primitives","file":"04-tokio-internals/08-sync-primitives.html","blurb":"Channels, mutexes, and queues of wakers"},
{"id":"p04-09","part":4,"title":"Cancellation and select!","file":"04-tokio-internals/09-cancellation-and-select.html","blurb":"Drop is cancel; safety is on you"},
{"id":"p05-01","part":5,"title":"Hello, Tokio: the boot sequence","file":"05-walkthroughs/01-boot-sequence.html","blurb":"What exists before your first await"},
{"id":"p05-02","part":5,"title":"A TCP echo server, await by await","file":"05-walkthroughs/02-echo-server.html","blurb":"Every await, annotated"},
{"id":"p05-03","part":5,"title":"join!, select!, timeout","file":"05-walkthroughs/03-join-select-timeout.html","blurb":"Concurrency, traced"},
{"id":"p05-04","part":5,"title":"Pipelines: spawn and channels","file":"05-walkthroughs/04-pipelines-and-channels.html","blurb":"Backpressure made visible"},
{"id":"p05-05","part":5,"title":"Pitfalls","file":"05-walkthroughs/05-pitfalls.html","blurb":"Wrong code, what the runtime did, fixed code"},
{"id":"p05-06","part":5,"title":"The full-circle mental model","file":"05-walkthroughs/06-mental-model.html","blurb":"From syscall to scheduler in one diagram"}]
/* PAGES-MANIFEST-END */;

/* Titles for the five parts (part 0 is the landing page). */
const PART_TITLES = {
  1: "Machine Foundations",
  2: "Concurrency Models",
  3: "Rust Async Building Blocks",
  4: "Tokio Internals",
  5: "Walkthroughs",
};

(function () {
  const body = document.body;
  const pageId = body.dataset.page; // writers set this to the manifest id
  const root = pageId === "index" ? "" : "../"; // index sits at the site root,
  // content pages live one level deeper, so their asset/link prefix is "../"
  const currentIndex = PAGES.findIndex((p) => p.id === pageId);

  const esc = (s) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;")
     .replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  const partLabel = (n) => "Part " + n + " · " + PART_TITLES[n];

  /* ---------------- sidebar TOC ---------------- */
  function renderSidebar() {
    const aside = document.getElementById("site-nav");
    if (!aside) return;

    let html =
      '<div class="nav-head">' +
      '<a class="nav-home" href="' + root + 'index.html">Under the Await</a>' +
      '<span class="nav-tag">How Tokio really works</span>' +
      "</div>" +
      '<nav class="nav-toc" aria-label="Contents">';

    let part = 0;
    for (const p of PAGES) {
      if (p.part === 0) continue; // the landing page is the home link above
      if (p.part !== part) {
        if (part !== 0) html += "</ul>";
        part = p.part;
        html +=
          '<div class="nav-part"><span class="nav-part-num">Part ' + part +
          "</span>" + esc(PART_TITLES[part]) + "</div>" +
          '<ul class="nav-list">';
      }
      const active = p.id === pageId;
      html +=
        '<li><a href="' + root + p.file + '"' +
        (active ? ' class="active" aria-current="page"' : "") +
        ">" + esc(p.title) + "</a></li>";
    }
    html += "</ul></nav>";
    aside.innerHTML = html;

    // reveal the current page in the TOC: the sidebar scrolls, so on deep
    // pages the active entry would otherwise sit below the fold
    const active = aside.querySelector("a.active");
    if (active) {
      const ar = active.getBoundingClientRect();
      const sr = aside.getBoundingClientRect();
      aside.scrollTop += ar.top - sr.top - aside.clientHeight / 2 + ar.height / 2;
    }
  }

  /* ------------- mobile nav: toggle + scrim ------------- */
  function renderNavToggle() {
    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "nav-toggle";
    toggle.setAttribute("aria-controls", "site-nav");
    toggle.setAttribute("aria-expanded", "false");
    toggle.innerHTML =
      '<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true" ' +
      'fill="none" stroke="currentColor" stroke-width="1.7" ' +
      'stroke-linecap="round"><path d="M2 4h12M2 8h12M2 12h12"/></svg>' +
      "<span>Contents</span>";

    const scrim = document.createElement("div");
    scrim.className = "nav-scrim";

    const setOpen = (open) => {
      body.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", String(open));
    };

    toggle.addEventListener("click", () =>
      setOpen(!body.classList.contains("nav-open")));
    scrim.addEventListener("click", () => setOpen(false));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") setOpen(false);
    });

    // close the drawer when a TOC link is chosen
    const aside = document.getElementById("site-nav");
    if (aside) {
      aside.addEventListener("click", (e) => {
        if (e.target.closest("a")) setOpen(false);
      });
    }

    body.appendChild(toggle);
    body.appendChild(scrim);
  }

  /* ---------------- prev/next footer ---------------- */
  function pnLink(page, dir) {
    const label = dir === "prev" ? "Previous" : "Next";
    const arrow = dir === "prev" ? "\u2190" : "\u2192";
    if (!page) {
      const msg = dir === "prev"
        ? "This is the beginning"
        : "You have reached the end";
      return '<span class="pn-link pn-' + dir + ' pn-disabled" aria-disabled="true">' +
        '<span class="pn-dir">' + arrow + " " + label + "</span>" +
        '<span class="pn-title">' + msg + "</span></span>";
    }
    const part = page.part === 0 ? "Introduction" : partLabel(page.part);
    return '<a class="pn-link pn-' + dir + '" rel="' + dir + '" href="' +
      root + page.file + '">' +
      '<span class="pn-dir">' + arrow + " " + label + "</span>" +
      '<span class="pn-title">' + esc(page.title) + "</span>" +
      '<span class="pn-part">' + esc(part) + "</span></a>";
  }

  function renderPageNav() {
    const nav = document.getElementById("page-nav");
    if (!nav || currentIndex === -1) return; // unknown id (the raw template)
    nav.innerHTML =
      pnLink(PAGES[currentIndex - 1], "prev") +
      pnLink(PAGES[currentIndex + 1], "next");
  }

  /* ---------------- keyboard navigation ---------------- */
  function renderKeys() {
    document.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
      const t = e.target;
      if (t && (t.isContentEditable ||
          /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
      if (currentIndex === -1) return;
      const target = e.key === "ArrowLeft"
        ? PAGES[currentIndex - 1]
        : PAGES[currentIndex + 1];
      if (target) window.location.href = root + target.file;
    });
  }

  /* ---------------- code highlighting ---------------- */
  if (window.hljs && typeof window.hljs.highlightAll === "function") {
    window.hljs.highlightAll();
  }

  renderSidebar();
  renderNavToggle();
  renderPageNav();
  renderKeys();
})();
