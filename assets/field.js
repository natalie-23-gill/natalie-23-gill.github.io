/* The field: Day & Night (B3678/S34678) on a torus, every cell colored by its
   count of live neighbours onto --step-0..--step-8. Ported from the design
   system's bundle.js (Field + Engine) without React. No dependencies.
   Markup: <div class="ng-field" data-field="live|still" data-seed="7|time"><canvas aria-hidden="true"></canvas>...</div>
   A click on a live field pauses and resumes it (remembered across pages); a button that shows on
   keyboard focus does the same. Defaults are the `field` tokens; assets/field-config.js (window.NGFieldConfig) overrides them. */
(function (root) {
  "use strict";
  var FIELD = { rule: { B: [3, 6, 7, 8], S: [3, 4, 6, 7, 8] }, rainEvery: 3, rainSize: 14, speed: 3, easeMs: 350, cell: 8, density: 0.5 }; /* @generated from the field tokens by tools/gen_tokens.py */
  /* Site settings (spec): warm-up generations for a still frame, and the simulated width cap.
     Wider than maxWidth the 120-column torus is drawn tiled, so cells stay at FIELD.cell. */
  FIELD.generations = 40; FIELD.maxWidth = 960; FIELD.seed = "time";

  /* Apply window.NGFieldConfig over the token defaults; bad values are ignored with a warning. */
  var LIMITS = { speed: [0.1, 60], easeMs: [0, 5000], rainEvery: [0, 1000], rainSize: [1, 120], density: [0, 1], cell: [2, 64], generations: [0, 1000], maxWidth: [64, 10000] };
  function configure(cfg) {
    if (!cfg || typeof cfg !== "object") return FIELD;
    Object.keys(cfg).forEach(function (k) {
      var v = cfg[k], m;
      if (k === "rule") {
        m = /^B([0-8]*)\/S([0-8]*)$/i.exec(String(v).trim());
        if (m) FIELD.rule = { B: m[1].split("").map(Number), S: m[2].split("").map(Number) };
        else warn(k, v);
      } else if (k === "seed") {
        if (v === "time" || (typeof v === "number" && isFinite(v))) FIELD.seed = v; else warn(k, v);
      } else if (LIMITS[k]) {
        if (typeof v === "number" && v >= LIMITS[k][0] && v <= LIMITS[k][1]) FIELD[k] = v; else warn(k, v);
      } else warn(k, v);
    });
    return FIELD;
  }
  function warn(k, v) { if (root.console) root.console.warn("field-config: ignoring " + k + " = " + JSON.stringify(v)); }
  function timeSeed() { /* clock plus a sub-millisecond reading, so two fields on one page differ */
    var p = root.performance && root.performance.now ? Math.floor(root.performance.now() * 1000) : 0;
    return (Date.now() ^ Math.imul(p, 2654435761)) >>> 0;
  }
  function resolveSeed(attr) {
    var s = attr == null || attr === "" ? FIELD.seed : attr;
    if (s === "time") return timeSeed();
    var n = parseInt(s, 10);
    return isNaN(n) ? timeSeed() : n >>> 0;
  }
  configure(root.NGFieldConfig);

  /* mulberry32, identical to bundle.js; tools/still_frames.py implements the same. */
  function rng(seed) {
    var s = seed >>> 0;
    return function () { s = (s + 0x6D2B79F5) | 0; var t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }

  function Engine(W, H, rand) {
    this.W = W; this.H = H; this.rng = rand || Math.random;
    this.cells = new Uint8Array(W * H); this.next = new Uint8Array(W * H); this.counts = new Uint8Array(W * H); this.gen = 0;
  }
  Engine.prototype.idx = function (x, y) { return ((y + this.H) % this.H) * this.W + ((x + this.W) % this.W); };
  Engine.prototype.seed = function (p) { for (var i = 0; i < this.W * this.H; i++) this.cells[i] = this.rng() < p ? 1 : 0; this.gen = 0; };
  Engine.prototype.poke = function (x, y) { for (var dy = -2; dy <= 2; dy++) for (var dx = -2; dx <= 2; dx++) if (this.rng() < 0.6) this.cells[this.idx(x + dx, y + dy)] = 1; };
  Engine.prototype.countAlive = function () {
    var W = this.W, H = this.H, c = this.cells, cnt = this.counts;
    for (var y = 0; y < H; y++) for (var x = 0; x < W; x++) {
      var s = 0;
      for (var dy = -1; dy <= 1; dy++) for (var dx = -1; dx <= 1; dx++) if (dx || dy) s += c[this.idx(x + dx, y + dy)];
      cnt[y * W + x] = s;
    }
  };
  Engine.prototype.step = function () {
    this.countAlive();
    var B = FIELD.rule.B, S = FIELD.rule.S, c = this.cells, n = this.next, W = this.W, H = this.H;
    for (var i = 0; i < W * H; i++) { var k = this.counts[i]; n[i] = c[i] ? (S.indexOf(k) >= 0 ? 1 : 0) : (B.indexOf(k) >= 0 ? 1 : 0); }
    var t = this.cells; this.cells = this.next; this.next = t; this.gen++;
    if (FIELD.rainEvery > 0 && this.gen % FIELD.rainEvery === 0) {
      var rx = Math.floor(this.rng() * W), ry = Math.floor(this.rng() * H), half = Math.floor(FIELD.rainSize / 2);
      for (var py = -half; py < half; py++) for (var px = -half; px < half; px++) this.cells[this.idx(rx + px, ry + py)] = this.rng() < 0.5 ? 1 : 0;
    }
  };

  function readLUT(el) {
    var cs = root.getComputedStyle(el), st = [], lut = new Uint8Array(257 * 3);
    for (var i = 0; i <= 8; i++) {
      var m = /^#([0-9a-f]{6})$/i.exec((cs.getPropertyValue("--step-" + i) || "").trim()), v = m ? parseInt(m[1], 16) : 0;
      st.push([v >> 16 & 255, v >> 8 & 255, v & 255]);
    }
    for (var k = 0; k <= 256; k++) {
      var f = k / 256 * 8, a = Math.min(7, Math.floor(f)), t = f - a, c0 = st[a], c1 = st[a + 1];
      for (var ch = 0; ch < 3; ch++) lut[k * 3 + ch] = Math.round(c0[ch] + (c1[ch] - c0[ch]) * t);
    }
    return lut;
  }

  function init(el) {
    if (!el || el.__ngField) return el && el.__ngField;
    var cv = el.querySelector("canvas");
    if (!cv) { cv = document.createElement("canvas"); cv.setAttribute("aria-hidden", "true"); el.insertBefore(cv, el.firstChild); }
    var ctx = cv.getContext("2d"), off = document.createElement("canvas"), octx = off.getContext("2d");
    var seed = resolveSeed(el.getAttribute("data-seed"));
    var mq = function (q) { return root.matchMedia ? root.matchMedia(q) : { matches: false }; };
    var reduceMq = mq("(prefers-reduced-motion: reduce)"), darkMq = mq("(prefers-color-scheme: dark)");
    var live = el.getAttribute("data-field") !== "still" && !reduceMq.matches;
    var E = null, disp = null, img = null, lut = readLUT(el), cell = FIELD.cell, cssW = 0, cssH = 0;
    var raf = 0, timer = 0, lastT = 0, onScreen = true, ro = null, io = null, mo = null;
    var paused = readPaused(), btn = null;

    function build(w, h) {
      var W = Math.max(1, Math.min(Math.ceil(w / cell), Math.floor(FIELD.maxWidth / cell))), H = Math.max(1, Math.ceil(h / cell));
      if (E && E.W === W && E.H === H) return;
      var old = E;
      E = new Engine(W, H, rng(seed)); E.seed(FIELD.density);
      if (old && live) { /* keep the running picture where the grids overlap (phone toolbars resize the hero) */
        for (var y = 0; y < Math.min(H, old.H); y++) for (var x = 0; x < Math.min(W, old.W); x++) E.cells[y * W + x] = old.cells[y * old.W + x];
      } else for (var g = 0; g < FIELD.generations; g++) E.step();
      E.countAlive(); disp = new Float32Array(W * H);
      for (var i = 0; i < W * H; i++) disp[i] = E.counts[i];
      off.width = W; off.height = H; img = octx.createImageData(W, H);
    }
    function size() {
      var w = el.clientWidth || 960, h = el.clientHeight || 480, dpr = Math.min(root.devicePixelRatio || 1, 2);
      if (w === cssW && h === cssH && cv.width === Math.round(w * dpr)) return;
      cssW = w; cssH = h; cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); build(w, h); draw(null);
    }
    function draw(dt) {
      var k = dt == null ? 1 : 1 - Math.exp(-dt / FIELD.easeMs), d = img.data, n = disp.length;
      for (var j = 0; j < n; j++) {
        disp[j] += (E.counts[j] - disp[j]) * k;
        var li = Math.max(0, Math.min(256, Math.round(disp[j] / 8 * 256))) * 3, p = j * 4;
        d[p] = lut[li]; d[p + 1] = lut[li + 1]; d[p + 2] = lut[li + 2]; d[p + 3] = 255;
      }
      octx.putImageData(img, 0, 0);
      ctx.imageSmoothingEnabled = false;
      for (var x = 0, tw = E.W * cell; x < cssW; x += tw) ctx.drawImage(off, x, 0, tw, E.H * cell); /* torus: tiles join without a seam */
    }
    function frame(t) { var dt = lastT ? Math.min(100, t - lastT) : 16; lastT = t; draw(dt); raf = root.requestAnimationFrame(frame); }
    function tick() { E.step(); E.countAlive(); }
    function run() {
      var want = live && !paused && onScreen && !document.hidden;
      if (want && !timer) { lastT = 0; raf = root.requestAnimationFrame(frame); timer = root.setInterval(tick, 1000 / FIELD.speed); }
      if (!want && timer) { root.cancelAnimationFrame(raf); root.clearInterval(timer); raf = timer = 0; }
    }
    function recolor() { lut = readLUT(el); if (img) draw(timer ? 0 : null); }
    /* A click on the field (or the keyboard-focusable button) pauses and resumes it; the choice is remembered. */
    function setPaused(p) {
      paused = p; run(); if (paused) draw(null);
      el.classList.toggle("is-paused", paused);
      if (btn) { btn.textContent = paused ? "Play animation" : "Pause animation"; btn.setAttribute("aria-pressed", paused ? "true" : "false"); }
      try { root.localStorage.setItem(PAUSE_KEY, paused ? "1" : "0"); } catch (e) { /* storage blocked: still pauses for this page */ }
    }
    function onClick() { if (live) setPaused(!paused); }
    function onReduce() { if (reduceMq.matches && live) { live = false; run(); draw(null); el.classList.remove("is-live"); if (btn) btn.hidden = true; } }
    function listen(m, f) { if (m.addEventListener) m.addEventListener("change", f); else if (m.addListener) m.addListener(f); }

    size();
    if (live) {
      cv.addEventListener("click", onClick);
      btn = document.createElement("button"); btn.type = "button"; btn.className = "ng-field__toggle";
      btn.addEventListener("click", onClick); el.appendChild(btn);
      el.classList.add("is-live"); setPaused(paused);
    }
    document.addEventListener("visibilitychange", run);
    listen(darkMq, recolor); listen(reduceMq, onReduce);
    if (root.MutationObserver) { mo = new MutationObserver(recolor); mo.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] }); }
    if (root.ResizeObserver) { ro = new ResizeObserver(size); ro.observe(el); } else root.addEventListener("resize", size);
    if (live && root.IntersectionObserver) { io = new IntersectionObserver(function (es) { onScreen = es[es.length - 1].isIntersecting; run(); }); io.observe(el); }
    run();

    el.__ngField = {
      engine: function () { return E; },
      destroy: function () {
        live = false; run(); cv.removeEventListener("click", onClick); if (btn) btn.remove(); document.removeEventListener("visibilitychange", run);
        if (mo) mo.disconnect(); if (ro) ro.disconnect(); else root.removeEventListener("resize", size); if (io) io.disconnect();
        delete el.__ngField;
      }
    };
    return el.__ngField;
  }

  var PAUSE_KEY = "fieldPaused";
  function readPaused() { try { return root.localStorage.getItem(PAUSE_KEY) === "1"; } catch (e) { return false; } }

  function initAll() { var els = document.querySelectorAll("[data-field]"); for (var i = 0; i < els.length; i++) init(els[i]); }

  var api = { init: init, initAll: initAll, configure: configure, Engine: Engine, FIELD: FIELD, rng: rng };
  root.NGField = api;
  if (typeof module === "object" && module.exports) module.exports = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initAll); else initAll();
  }
})(typeof window !== "undefined" ? window : globalThis);
