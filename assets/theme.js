/* Natalie Gill — dark-mode switch. Runs in <head> before paint (inlined by
   _templates/partials/head.html; this file is the readable source copy, keep the
   two in sync). Sets <html data-theme="light|dark"> from localStorage.theme, else
   from prefers-color-scheme. Any [data-theme-toggle] button flips and stores it. */
(function () {
  var root = document.documentElement;
  var media = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
  function stored() {
    try { var v = localStorage.getItem("theme"); return v === "dark" || v === "light" ? v : null; }
    catch (e) { return null; }
  }
  function system() { return media && media.matches ? "dark" : "light"; }
  /* The toggle shows the theme it switches to; its accessible name says the same word. */
  function label() {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    var bs = document.querySelectorAll("[data-theme-toggle]");
    for (var i = 0; i < bs.length; i++) { bs[i].setAttribute("aria-label", "Switch to " + next + " theme"); bs[i].setAttribute("title", "Switch to " + next + " theme"); }
  }
  function apply(mode) { root.setAttribute("data-theme", mode === "dark" ? "dark" : "light"); label(); }
  window.ngSetTheme = function (mode) {
    apply(mode);
    try { localStorage.setItem("theme", root.getAttribute("data-theme")); } catch (e) {}
  };
  apply(stored() || system());
  if (media) {
    var follow = function () { if (!stored()) apply(system()); };
    if (media.addEventListener) media.addEventListener("change", follow);
    else if (media.addListener) media.addListener(follow);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", label);
  document.addEventListener("click", function (e) {
    var t = e.target && e.target.closest ? e.target.closest("[data-theme-toggle]") : null;
    if (t) window.ngSetTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
  });
})();
