# ng_figure(): one figure, both themes, for a Quarto post rendered with knitr.
#
# Deps: ggplot2; systemfonts (font registration) and ragg (the PNG device) are used when installed.
#
#   source(file.path(rprojroot::find_root("_quarto.yml"), "tools/plots/ng_figure.R"))   # or a relative path
#   ng_figure(function(mode) ggplot(df, aes(x, y, colour = g)) + geom_line(linewidth = ng_line) +
#               scale_colour_ng(mode) + theme_ng(mode),
#             "f1", alt = "Line chart of ...", caption = "F1 by caller. n = 48, GIAB HG002, 2026-10.")
#
# `plot` is either a function of mode ("light" or "dark") that builds the whole plot, so scales match
# the theme, or a finished ggplot, to which theme_ng(mode) is added (its scales then stay as built;
# pass a function whenever the plot uses scale_*_ng()). Writes <name>-light.png and <name>-dark.png
# (6.4 x 3.6 in at 300 dpi) into `dir` (default: the document's folder, knitr's working directory)
# and returns the <figure class="ng-fig"> block as raw HTML. No chunk option is needed: the result is
# knitr::asis_output, so it is emitted as-is (results: asis is implied); keep the default echo: false.
#
# Fonts: matplotlib and systemfonts need the TTFs, not the site's WOFF2. They are read from
# `fonts_dir`, defaulting to $NG_FONTS_DIR, else tools/plots/fonts/ under the project root (the folder
# holding _quarto.yml; tools/sync-ds.sh copies the TTFs there).

ng_root <- function(start = getwd()) {
  d <- normalizePath(start, mustWork = FALSE)
  repeat {
    if (file.exists(file.path(d, "_quarto.yml"))) return(d)
    up <- dirname(d); if (up == d) return(NULL); d <- up
  }
}

local({
  root <- ng_root()
  here <- if (!is.null(root)) file.path(root, "tools", "plots") else "."
  source(file.path(here, "theme_ng.R"), local = globalenv())
})

ng_fonts_dir <- function() {
  env <- Sys.getenv("NG_FONTS_DIR")
  if (nzchar(env)) return(env)
  root <- ng_root()
  if (!is.null(root)) file.path(root, "tools", "plots", "fonts") else NULL
}

ng_html_escape <- function(x) {
  x <- gsub("&", "&amp;", x, fixed = TRUE); x <- gsub("<", "&lt;", x, fixed = TRUE)
  x <- gsub(">", "&gt;", x, fixed = TRUE); gsub("\"", "&quot;", x, fixed = TRUE)
}

.ng_fonts_done <- new.env()

ng_figure <- function(plot, name, alt, caption, dir = ".", size = "wide", dpi = 300,
                      fonts_dir = ng_fonts_dir()) {
  if (missing(alt) || !nzchar(trimws(alt))) stop("ng_figure(): `alt` text is required")
  if (missing(caption) || !nzchar(trimws(caption))) stop("ng_figure(): `caption` is required (n, dataset, date)")
  if (!isTRUE(.ng_fonts_done$ok)) {
    if (!is.null(fonts_dir) && dir.exists(fonts_dir) && requireNamespace("systemfonts", quietly = TRUE)) {
      ng_fonts(fonts_dir); .ng_fonts_done$ok <- TRUE
    } else warning("ng_figure(): Fira fonts not registered (need systemfonts and NG_FONTS_DIR or tools/plots/fonts)")
  }
  dir.create(dir, showWarnings = FALSE, recursive = TRUE)
  src <- character()
  for (mode in c("light", "dark")) {
    p <- if (is.function(plot)) plot(mode) else plot + theme_ng(mode)
    file <- sprintf("%s-%s.png", name, mode)
    ng_save(file.path(dir, file), p, size = size, dpi = dpi)
    src[mode] <- if (identical(dir, ".")) file else file.path(dir, file)
  }
  a <- ng_html_escape(alt)
  html <- paste0(
    '<figure class="ng-fig">\n',
    '  <img class="ng-fig-light" src="', src[["light"]], '" alt="', a, '">\n',
    '  <img class="ng-fig-dark" src="', src[["dark"]], '" alt="', a, '">\n',
    '  <figcaption>', ng_html_escape(caption), '</figcaption>\n',
    '</figure>')
  knitr::asis_output(paste0("\n```{=html}\n", html, "\n```\n"))
}
