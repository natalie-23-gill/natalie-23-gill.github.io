"""Natalie Gill plot theme for plotnine.

    from ngtheme import theme_ng, scale_color_ng, scale_fill_ng, scale_fill_ng_seq, scale_fill_ng_div, ng_fonts
    ng_fonts("path/to/fonts")          # once per session: registers Fira Mono and Fira Sans with matplotlib
    (ggplot(df, aes("x", "y", color="group")) + geom_line() + scale_color_ng() + theme_ng())
    theme_ng("dark") for the dark theme.

Every value comes from the design system's tokens.json. The R file theme_ng.R is the same theme,
element for element, so plots from either language match.
"""
from __future__ import annotations
import json, pathlib
from plotnine import (theme, element_text, element_line, element_rect, element_blank,
                      scale_color_manual, scale_fill_manual, scale_color_gradientn, scale_fill_gradientn,
                      scale_shape_manual, guide_legend)

TOKENS = {
    "light": {"surface": "#eef1ff", "raised": "#cfd1f7", "ink": "#2a1d27", "muted": "#5d545f",
              "steps": ["#eef1ff", "#cfd1f7", "#b7afed", "#a58cdc", "#946cc0", "#7f5298", "#643e6d", "#5c2a64", "#2a1d27"],
              "cat": ["#2a1d27", "#014f8a", "#9e5701", "#9978cf", "#02837a", "#c4780b", "#72294c", "#7f5bb6"],
              "div": ["#1a895c", "#2c9f6a", "#5ab280", "#89c19c", "#b2cfba", "#d4e0d6", "#eef1ff",
                      "#d6d2e3", "#c0b0d4", "#b08ac7", "#a462b4", "#943d94", "#7a246c"]},
    "dark": {"surface": "#171216", "raised": "#322531", "ink": "#e5eafe", "muted": "#a7a9b8",
              "steps": ["#171216", "#322531", "#4f3854", "#6c4c7e", "#8563ab", "#9a81d2", "#aea3ec", "#c5c7fc", "#e5eafe"],
              "cat": ["#e5eafe", "#e0ae57", "#00a9cd", "#825eb9", "#b4561a", "#b3c5fc", "#3f8d7f", "#c78b09"],
              "div": ["#80e2b0", "#53c088", "#419969", "#3c7251", "#334d3b", "#222c25", "#171216",
                      "#26212d", "#43314e", "#673e74", "#8f4a97", "#b65bb2", "#d579c2"]}
}
SHAPES = ["o", "s", "^", "D", "v", "P", "X", "*"]   # circle, square, triangle, diamond, then down-triangle, plus, cross, star: series order
MONO, SANS = "Fira Mono", "Fira Sans"   # plots are set entirely in SANS; MONO is kept for code annotations only


def ng_fonts(fonts_dir: str | pathlib.Path) -> None:
    """Register the system's Fira files with matplotlib (plotnine's renderer)."""
    from matplotlib import font_manager
    for f in pathlib.Path(fonts_dir).glob("*.ttf"):
        font_manager.fontManager.addfont(str(f))


def theme_ng(mode: str = "light", base_size: float = 10, grid: str = "y"):
    """The theme. grid: 'y' (default), 'x' (horizontal bars), 'xy' (scatter) or 'none' (heatmaps)."""
    t = TOKENS[mode]
    gx = element_line(color=t["raised"], size=0.5) if "x" in grid else element_blank()
    gy = element_line(color=t["raised"], size=0.5) if "y" in grid else element_blank()
    return theme(
        # ground
        plot_background=element_rect(fill=t["surface"], color=t["surface"]),
        panel_background=element_rect(fill=t["surface"], color=t["surface"]),
        panel_border=element_blank(),
        # grid: hairlines in step-1, no minor grid, no dashes
        panel_grid_major_x=gx, panel_grid_major_y=gy,
        panel_grid_minor=element_blank(),
        # axes: bottom spine only, no tick marks, tick labels in muted ink
        axis_line_x=element_line(color=t["raised"], size=0.5),
        axis_line_y=element_blank(),
        axis_ticks=element_blank(),
        axis_ticks_length=0,
        axis_text=element_text(family=SANS, size=base_size - 1, color=t["muted"]),
        axis_text_x=element_text(margin={"t": 6}),
        axis_text_y=element_text(margin={"r": 6}),
        axis_title=element_text(family=SANS, size=base_size, color=t["muted"]),
        axis_title_x=element_text(margin={"t": 8}),
        axis_title_y=element_text(margin={"r": 8}, angle=90),
        # frame: title, subtitle, source line; all text in the plot is Fira Sans
        plot_title=element_text(family=SANS, size=base_size + 3, weight="medium", color=t["ink"], ha="left", margin={"b": 4}),
        plot_subtitle=element_text(family=SANS, size=base_size - 1, color=t["muted"], ha="left", margin={"b": 12}),
        plot_caption=element_text(family=SANS, size=base_size - 1.5, color=t["muted"], ha="left", margin={"t": 12}),
        # legend: no box, below the plot, ink text
        legend_position="bottom", legend_direction="horizontal",
        legend_background=element_blank(), legend_key=element_blank(),
        legend_title=element_blank(),
        legend_text=element_text(family=SANS, size=base_size, color=t["ink"]),
        legend_key_size=12, legend_margin=0, legend_box_spacing=0.02,  # figure units, despite the docstring
        # facets: medium-weight label, no strip box
        strip_background=element_blank(),
        strip_text=element_text(family=SANS, size=base_size - 1, weight="medium", color=t["ink"], ha="left", margin={"b": 6}),
        panel_spacing=0.03,
        # everything else
        text=element_text(family=SANS, size=base_size, color=t["ink"]),
        plot_margin=0.03,
        figure_size=(6.4, 3.6), dpi=200,
        # (ggplot2's plot.title.position = "plot" has no plotnine equivalent; plotnine already aligns titles to the plot edge)
    )


def scale_color_ng(mode: str = "light", **kw):
    """Categorical, fixed order, eight series; prefer four or fewer and facet when the data allows."""
    return scale_color_manual(values=TOKENS[mode]["cat"], **kw)

def scale_fill_ng(mode: str = "light", **kw):
    return scale_fill_manual(values=TOKENS[mode]["cat"], **kw)

def scale_shape_ng(**kw):
    """Marker shapes in series order, so identity never rides on color alone."""
    return scale_shape_manual(values=SHAPES, **kw)

def scale_fill_ng_seq(mode: str = "light", **kw):
    """Sequential: the nine-step scale, lightest for lowest."""
    return scale_fill_gradientn(colors=TOKENS[mode]["steps"], **kw)

def scale_color_ng_seq(mode: str = "light", **kw):
    return scale_color_gradientn(colors=TOKENS[mode]["steps"], **kw)

def scale_fill_ng_div(mode: str = "light", limit: float = 1.0, **kw):
    """Diverging: green arm negative, violet (brand) arm positive, ground at zero. Domain forced symmetric."""
    return scale_fill_gradientn(colors=TOKENS[mode]["div"], limits=(-limit, limit), **kw)

def scale_color_ng_div(mode: str = "light", limit: float = 1.0, **kw):
    return scale_color_gradientn(colors=TOKENS[mode]["div"], limits=(-limit, limit), **kw)

# Mark specs, for use in geoms: geom_line(size=LINE), geom_point(size=POINT, stroke=RING), geom_col(width=BAR)
LINE = 1.0      # 2px at 200 dpi
POINT = 2.6     # ~8px markers
RING = 0.5      # surface ring: pass color=surface via aes or stroke on filled shapes
BAR = 0.5       # bar width as a fraction of the slot; keeps bars under 24px in a 6.4in figure with ≤ 8 bars
