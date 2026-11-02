/* The 404 page's still frame, applied through field.js's data-hook after the warm-up.
   Loaded in the page body, so the hooks are registered before field.js initialises the field. */
(function (root) {
  "use strict";
  var hooks = root.NGFieldHooks = root.NGFieldHooks || {};

  /* "void": the cells around the panel have died out, leaving bare ground with a ragged edge. */
  hooks["void"] = function (E, ctx) {
    var panel = ctx.el.querySelector(".ng-field__panel");
    if (!panel) return;
    var f = ctx.el.getBoundingClientRect(), p = panel.getBoundingClientRect(), c = ctx.cell, pad = 5;
    var x0 = Math.floor((p.left - f.left) / c) - pad, x1 = Math.ceil((p.right - f.left) / c) + pad;
    var y0 = Math.floor((p.top - f.top) / c) - pad, y1 = Math.ceil((p.bottom - f.top) / c) + pad;
    for (var y = y0 - 3; y <= y1 + 3; y++) {
      var j0 = Math.floor(ctx.rand() * 4), j1 = Math.floor(ctx.rand() * 4);   /* ragged left and right edges */
      for (var x = x0 - j0; x <= x1 + j1; x++) {
        var edge = y < y0 || y > y1;                                           /* ragged top and bottom edges */
        if (x < 0 || y < 0 || x >= E.W || y >= E.H || (edge && ctx.rand() < 0.5)) continue;
        E.cells[y * E.W + x] = 0;
      }
    }
  };
})(window);
