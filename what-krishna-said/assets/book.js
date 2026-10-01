/* What Krishna Said — progressive enhancement only.
   The book is fully readable with JavaScript disabled.
   This script provides: TOC drawer, theme toggle with persistence. */
(function () {
  "use strict";

  var stored = null;
  try {
    stored = window.localStorage.getItem("wks-theme");
  } catch (e) {
    /* storage unavailable (some file:// contexts) — fall back to media query */
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var btn = document.querySelector(".theme-toggle");
    if (btn) {
      btn.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
    }
  }

  var initial = stored || (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  applyTheme(initial);

  var toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      try {
        window.localStorage.setItem("wks-theme", next);
      } catch (e) {
        /* ignore — page still works */
      }
    });
  }

  var toc = document.getElementById("toc");
  var tocToggle = document.querySelector(".toc-toggle");
  var scrim = null;

  function ensureScrim() {
    if (scrim) return scrim;
    scrim = document.createElement("div");
    scrim.className = "toc-scrim";
    scrim.addEventListener("click", closeToc);
    document.body.appendChild(scrim);
    return scrim;
  }

  function openToc() {
    if (!toc) return;
    toc.classList.add("open");
    if (tocToggle) tocToggle.setAttribute("aria-expanded", "true");
    ensureScrim().classList.add("show");
  }

  function closeToc() {
    if (!toc) return;
    toc.classList.remove("open");
    if (tocToggle) tocToggle.setAttribute("aria-expanded", "false");
    if (scrim) scrim.classList.remove("show");
  }

  if (tocToggle) {
    tocToggle.addEventListener("click", function () {
      if (toc && toc.classList.contains("open")) {
        closeToc();
      } else {
        openToc();
      }
    });
  }

  var closeBtn = document.querySelector(".toc .toc-close");
  if (closeBtn) closeBtn.addEventListener("click", closeToc);

  /* Desktop only — pre-scrolling the drawer would scroll its close button out of view. */
  var current = toc && toc.querySelector('a[aria-current="page"]');
  if (current && window.matchMedia && window.matchMedia("(min-width: 1024px)").matches) {
    try {
      toc.scrollTop = current.offsetTop - (toc.clientHeight - current.offsetHeight) / 2;
    } catch (e) {
      /* leave the list at the top */
    }
  }

  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") closeToc();
  });
})();
