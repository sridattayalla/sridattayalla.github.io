/* LLM Internals — assets/site.js
   Enhancements only: theme toggle + mobile drawer.
   Every page stays fully readable and navigable with JavaScript disabled;
   the inline head script adds the 'js' class and applies the stored theme
   before first paint (no flash of wrong theme). */
(function () {
  'use strict';
  var doc = document;
  var root = doc.documentElement;

  /* ---- theme toggle ---- */
  var mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function storedTheme() {
    try {
      var t = localStorage.getItem('llmi-theme');
      return (t === 'dark' || t === 'light') ? t : null;
    } catch (e) { return null; }
  }
  function currentTheme() {
    var t = root.getAttribute('data-theme');
    if (t === 'dark' || t === 'light') return t;
    return (mq && mq.matches) ? 'dark' : 'light';
  }
  function syncToggles() {
    var dark = currentTheme() === 'dark';
    var btns = doc.querySelectorAll('.theme-toggle');
    for (var i = 0; i < btns.length; i++) {
      btns[i].setAttribute('aria-pressed', dark ? 'true' : 'false');
    }
  }
  doc.addEventListener('click', function (e) {
    var el = e.target;
    var btn = el && el.closest ? el.closest('.theme-toggle') : null;
    if (!btn) return;
    var next = currentTheme() === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('llmi-theme', next); } catch (err) {}
    syncToggles();
  });
  /* follow the OS while the user has made no explicit choice */
  if (mq && mq.addEventListener) {
    mq.addEventListener('change', function () {
      if (!storedTheme()) { root.removeAttribute('data-theme'); syncToggles(); }
    });
  }
  syncToggles();

  /* ---- mobile drawer ---- */
  var body = doc.body;
  var menuBtn = doc.querySelector('.menu-btn');
  var nav = doc.querySelector('.site-nav');
  var backdrop = doc.querySelector('.drawer-backdrop');

  function drawerIsOpen() { return body.classList.contains('drawer-open'); }
  function setDrawer(open) {
    if (!menuBtn || !nav) return;
    body.classList.toggle('drawer-open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    menuBtn.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    if (open) {
      var first = nav.querySelector('a');
      if (first) first.focus();
    } else if (menuBtn.offsetParent !== null) {
      menuBtn.focus(); /* focus returns to the hamburger */
    }
  }
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () { setDrawer(!drawerIsOpen()); });
    if (backdrop) backdrop.addEventListener('click', function () { setDrawer(false); });
    doc.addEventListener('keydown', function (e) {
      if (!drawerIsOpen()) return;
      if (e.key === 'Escape') { setDrawer(false); return; }
      if (e.key === 'Tab') { /* keep focus inside the drawer while open */
        var links = nav.querySelectorAll('a[href], button');
        if (!links.length) return;
        var first = links[0];
        var last = links[links.length - 1];
        var active = doc.activeElement;
        if (e.shiftKey && active === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && active === last) { e.preventDefault(); first.focus(); }
        else if (active !== nav && !nav.contains(active)) { e.preventDefault(); first.focus(); }
      }
    });
    /* close the drawer when the viewport grows to desktop size */
    var wide = window.matchMedia('(min-width: 1120px)');
    var onWide = function () { if (wide.matches && drawerIsOpen()) setDrawer(false); };
    if (wide.addEventListener) wide.addEventListener('change', onWide);
    else if (wide.addListener) wide.addListener(onWide);
  }
})();
