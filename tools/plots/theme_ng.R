# Natalie Gill plot theme for ggplot2.
#
#   source("theme_ng.R")
#   ng_fonts("path/to/fonts")      # once per session: registers Fira Mono and Fira Sans (needs systemfonts; use ragg or showtext devices)
#   ggplot(df, aes(x, y, colour = group)) + geom_line() + scale_colour_ng() + theme_ng()
#   theme_ng("dark") for the dark theme.
#
# Every value comes from the design system's tokens.json. The Python file ngtheme.py is the same
# theme, element for element, so plots from either language match.

ng_tokens <- list(
  light= list(surface = "#eef1ff", raised = "#cfd1f7", ink = "#2a1d27", muted = "#5d545f",
    steps = c("#eef1ff", "#cfd1f7", "#b7afed", "#a58cdc", "#946cc0", "#7f5298", "#643e6d", "#5c2a64", "#2a1d27"),
    cat   = c("#2a1d27", "#014f8a", "#9e5701", "#9978cf", "#02837a", "#c4780b", "#72294c", "#7f5bb6"),
    div   = c("#1a895c", "#2c9f6a", "#5ab280", "#89c19c", "#b2cfba", "#d4e0d6", "#eef1ff",
              "#d6d2e3", "#c0b0d4", "#b08ac7", "#a462b4", "#943d94", "#7a246c")),
  dark = list(surface = "#171216", raised = "#322531", ink = "#e5eafe", muted = "#a7a9b8",
    steps = c("#171216", "#322531", "#4f3854", "#6c4c7e", "#8563ab", "#9a81d2", "#aea3ec", "#c5c7fc", "#e5eafe"),
    cat   = c("#e5eafe", "#e0ae57", "#00a9cd", "#825eb9", "#b4561a", "#b3c5fc", "#3f8d7f", "#c78b09"),
    div   = c("#80e2b0", "#53c088", "#419969", "#3c7251", "#334d3b", "#222c25", "#171216",
              "#26212d", "#43314e", "#673e74", "#8f4a97", "#b65bb2", "#d579c2"))
)
ng_shapes <- c(16, 15, 17, 18, 25, 3, 4, 8)   # circle, square, triangle, diamond, then down-triangle, plus, cross, star: series order
ng_mono <- "Fira Mono"; ng_sans <- "Fira Sans"

ng_fonts <- function(fonts_dir) {
  stopifnot(requireNamespace("systemfonts", quietly = TRUE))
  f <- function(name) file.path(fonts_dir, name)
  systemfonts::register_font(ng_mono, plain = f("FiraMono-Regular.ttf"), bold = f("FiraMono-Bold.ttf"))
  systemfonts::register_font(paste(ng_mono, "Medium"), plain = f("FiraMono-Medium.ttf"))
  systemfonts::register_font(ng_sans, plain = f("FiraSans-Regular.ttf"), italic = f("FiraSans-Italic.ttf"),
                             bold = f("FiraSans-SemiBold.ttf"))
  invisible(TRUE)
}

#' The theme. grid: "y" (default), "x" (horizontal bars), "xy" (scatter) or "none" (heatmaps).
theme_ng <- function(mode = "light", base_size = 10, grid = "y") {
  t <- ng_tokens[[mode]]
  hair <- ggplot2::element_line(colour = t$raised, linewidth = 0.5)
  gx <- if (grepl("x", grid)) hair else ggplot2::element_blank()
  gy <- if (grepl("y", grid)) hair else ggplot2::element_blank()
  ggplot2::theme(
    # ground
    plot.background  = ggplot2::element_rect(fill = t$surface, colour = t$surface),
    panel.background = ggplot2::element_rect(fill = t$surface, colour = t$surface),
    panel.border     = ggplot2::element_blank(),
    # grid: hairlines in step-1, no minor grid, no dashes
    panel.grid.major.x = gx, panel.grid.major.y = gy,
    panel.grid.minor   = ggplot2::element_blank(),
    # axes: bottom spine only, no tick marks, mono tick labels in muted ink
    axis.line.x  = hair,
    axis.line.y  = ggplot2::element_blank(),
    axis.ticks   = ggplot2::element_blank(),
    axis.ticks.length = grid::unit(0, "pt"),
    axis.text    = ggplot2::element_text(family = ng_mono, size = base_size - 1, colour = t$muted),
    axis.text.x  = ggplot2::element_text(margin = ggplot2::margin(t = 6)),
    axis.text.y  = ggplot2::element_text(margin = ggplot2::margin(r = 6)),
    axis.title   = ggplot2::element_text(family = ng_sans, size = base_size, colour = t$muted),
    axis.title.x = ggplot2::element_text(margin = ggplot2::margin(t = 8)),
    axis.title.y = ggplot2::element_text(margin = ggplot2::margin(r = 8), angle = 90),
    # frame: mono title, caption subtitle, caption source
    plot.title    = ggplot2::element_text(family = paste(ng_mono, "Medium"), size = base_size + 3, colour = t$ink, hjust = 0,
                                          margin = ggplot2::margin(b = 4)),
    plot.subtitle = ggplot2::element_text(family = ng_mono, size = base_size - 1, colour = t$muted, hjust = 0,
                                          margin = ggplot2::margin(b = 12)),
    plot.caption  = ggplot2::element_text(family = ng_mono, size = base_size - 1.5, colour = t$muted, hjust = 0,
                                          margin = ggplot2::margin(t = 12)),
    plot.title.position = "plot", plot.caption.position = "plot",
    # legend: no box, below the plot, ink text
    legend.position = "bottom", legend.direction = "horizontal",
    legend.background = ggplot2::element_blank(), legend.key = ggplot2::element_blank(),
    legend.title = ggplot2::element_blank(),
    legend.text  = ggplot2::element_text(family = ng_sans, size = base_size, colour = t$ink),
    legend.key.size = grid::unit(12, "pt"), legend.margin = ggplot2::margin(0, 0, 0, 0),
    legend.box.spacing = grid::unit(10, "pt"),
    # facets: label in mono, no strip box
    strip.background = ggplot2::element_blank(),
    strip.text = ggplot2::element_text(family = paste(ng_mono, "Medium"), size = base_size - 1, colour = t$ink, hjust = 0,
                                       margin = ggplot2::margin(b = 6)),
    panel.spacing = grid::unit(12, "pt"),
    # everything else
    text = ggplot2::element_text(family = ng_sans, size = base_size, colour = t$ink),
    plot.margin = ggplot2::margin(12, 12, 12, 12)
  )
}

# Categorical, fixed order, eight series; prefer four or fewer and facet when the data allows.
scale_colour_ng <- function(mode = "light", ...) ggplot2::scale_colour_manual(values = ng_tokens[[mode]]$cat, ...)
scale_color_ng  <- scale_colour_ng
scale_fill_ng   <- function(mode = "light", ...) ggplot2::scale_fill_manual(values = ng_tokens[[mode]]$cat, ...)
# Marker shapes in series order, so identity never rides on color alone.
scale_shape_ng  <- function(...) ggplot2::scale_shape_manual(values = ng_shapes, ...)
# Sequential: the nine-step scale, lightest for lowest.
scale_fill_ng_seq   <- function(mode = "light", ...) ggplot2::scale_fill_gradientn(colours = ng_tokens[[mode]]$steps, ...)
scale_colour_ng_seq <- function(mode = "light", ...) ggplot2::scale_colour_gradientn(colours = ng_tokens[[mode]]$steps, ...)
# Diverging: green arm negative, violet (brand) arm positive, ground at zero. Domain forced symmetric.
scale_fill_ng_div   <- function(mode = "light", limit = 1, ...) ggplot2::scale_fill_gradientn(colours = ng_tokens[[mode]]$div, limits = c(-limit, limit), ...)
scale_colour_ng_div <- function(mode = "light", limit = 1, ...) ggplot2::scale_colour_gradientn(colours = ng_tokens[[mode]]$div, limits = c(-limit, limit), ...)

# Mark specs: geom_line(linewidth = ng_line), geom_point(size = ng_point, stroke = ng_ring), geom_col(width = ng_bar)
ng_line  <- 1.0    # 2px at 200 dpi
ng_point <- 2.6    # ~8px markers
ng_ring  <- 0.5    # surface ring on filled shapes (21–25) with colour = surface
ng_bar   <- 0.5    # bar width as a fraction of the slot

# Save at the system's sizes: 16:9 default, 4:3 for documents, square for social.
ng_save <- function(filename, plot = ggplot2::last_plot(), size = c("wide", "doc", "square"), dpi = 200) {
  size <- match.arg(size)
  dims <- switch(size, wide = c(6.4, 3.6), doc = c(6.4, 4.8), square = c(5, 5))
  dev <- if (requireNamespace("ragg", quietly = TRUE)) ragg::agg_png else "png"
  ggplot2::ggsave(filename, plot, width = dims[1], height = dims[2], dpi = dpi, device = dev)
}
