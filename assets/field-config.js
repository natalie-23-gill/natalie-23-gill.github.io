/* Field animation settings for this site. Edit freely; tools/sync-ds.sh never touches this file.
   Anything left out (or commented out) falls back to the design system's `field` tokens,
   which are the values shown below. Loaded before assets/field.js on every page. */
window.NGFieldConfig = {
  /* "time": a new starting pattern on every page load (seeded from the clock).
     A number (e.g. 7): the same starting pattern every time.
     A data-seed="..." attribute on a [data-field] element overrides this for that element. */
  seed: "time",

  // rule: "B3678/S34678",   // birth/survival neighbour counts (Day & Night)
     speed: 3,               // generations per second
  // easeMs: 350,            // time for a cell to ease to its new colour, in ms
     rainEvery: 2,           // drop a random patch every N generations (0 turns rain off)
     rainSize: 8,           // side of the rain patch, in cells
  // density: 0.5,           // fraction of cells alive at the start (0 to 1)
  // cell: 8,                // cell size in CSS pixels
  // generations: 40,        // warm-up generations before the first frame (and for still frames)
  // maxWidth: 960,          // simulated width cap in px; wider screens tile the field
};
