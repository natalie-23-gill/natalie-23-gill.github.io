"""ng_figure(): one figure, both themes, for a Quarto post rendered with Jupyter.

Deps: plotnine (and so matplotlib); IPython for display (present in any Jupyter kernel).

    import sys; sys.path.insert(0, "../../tools/plots")       # from writing/<post>/
    from ng_figure import ng_figure
    from ngtheme import theme_ng, scale_color_ng, LINE
    ng_figure(lambda mode: ggplot(df, aes("x", "y", color="g")) + geom_line(size=LINE)
                           + scale_color_ng(mode) + theme_ng(mode),
              "f1", alt="Line chart of ...", caption="F1 by caller. n = 48, GIAB HG002, 2026-10.")

`plot` is either a function of mode ("light" or "dark") that builds the whole plot, so scales match the
theme, or a finished plotnine ggplot, to which theme_ng(mode) is added (its scales then stay as built;
pass a function whenever the plot uses scale_*_ng()). Writes <name>-light.png and <name>-dark.png
(6.4 x 3.6 in at 200 dpi) into `dir` (default: the notebook's folder, the kernel's working directory).

Output: the returned object displays as text/html, the <figure class="ng-fig"> block, so make it the
last expression of the cell and no chunk option is needed. Alternatively print() it in a cell with
`#| output: asis`, which emits a ```{=html} raw block.

Fonts: matplotlib needs the TTFs, not the site's WOFF2. They are read from `fonts_dir`, defaulting to
$NG_FONTS_DIR, else tools/plots/fonts/ beside this file (tools/sync-ds.sh copies the TTFs there).
"""
from __future__ import annotations
import html, os, pathlib, sys, warnings

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ngtheme import theme_ng, ng_fonts  # noqa: E402

SIZES = {"wide": (6.4, 3.6), "doc": (6.4, 4.8), "square": (5, 5)}
_fonts_done = False


def _fonts_dir() -> pathlib.Path:
    return pathlib.Path(os.environ.get("NG_FONTS_DIR") or HERE / "fonts")


class NgFigure:
    def __init__(self, block: str):
        self.html = block

    def _repr_html_(self) -> str:
        return self.html

    def __str__(self) -> str:
        return f"\n```{{=html}}\n{self.html}\n```\n"


def ng_figure(plot, name: str, alt: str | None = None, caption: str | None = None, *, dir: str = ".",
              size: str = "wide", dpi: int = 200, fonts_dir: str | os.PathLike | None = None) -> NgFigure:
    global _fonts_done
    if not alt or not alt.strip():
        raise ValueError("ng_figure(): `alt` text is required")
    if not caption or not caption.strip():
        raise ValueError("ng_figure(): `caption` is required (n, dataset, date)")
    fd = pathlib.Path(fonts_dir) if fonts_dir else _fonts_dir()
    if not _fonts_done:
        if any(fd.glob("*.ttf")):
            ng_fonts(fd)
            _fonts_done = True
        else:
            warnings.warn(f"ng_figure(): no Fira TTFs in {fd}; set NG_FONTS_DIR")
    out = pathlib.Path(dir)
    out.mkdir(parents=True, exist_ok=True)
    w, h = SIZES[size]
    src = {}
    for mode in ("light", "dark"):
        p = plot(mode) if callable(plot) else plot + theme_ng(mode)
        file = f"{name}-{mode}.png"
        p.save(out / file, width=w, height=h, dpi=dpi, units="in", verbose=False)
        src[mode] = file if dir == "." else (out / file).as_posix()
    a = html.escape(alt, quote=True)
    return NgFigure(
        '<figure class="ng-fig">\n'
        f'  <img class="ng-fig-light" src="{src["light"]}" alt="{a}">\n'
        f'  <img class="ng-fig-dark" src="{src["dark"]}" alt="{a}">\n'
        f"  <figcaption>{html.escape(caption, quote=False)}</figcaption>\n"
        "</figure>")
