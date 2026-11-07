"""Redraw the "Growth of the NCBI Sequence Read Archive" plot from the What is bioinformatics? slides
in the design system: sra_growth-light.png and sra_growth-dark.png, next to this file.

Data: sra_stat.csv, NCBI's SRA growth statistics (https://www.ncbi.nlm.nih.gov/sra/docs/sragrowth/,
CSV from https://trace.ncbi.nlm.nih.gov/Traces/sra/sra_stat.cgi, downloaded 2026-11-03; the series
ends 2024-02-25, the same data as the slide). Columns: date, bases, open_access_bases, bytes,
open_access_bytes. Plotted: bytes (all data) and open_access_bytes (publicly available), in petabytes.

Not run at render time (the post has no executable code, so nothing goes in _freeze/). Rerun after
changing the plot, then paste the printed <figure> block into index.qmd if alt/caption changed.

Deps: pandas, plotnine (use a venv, never the system Python).
Usage (from the repo root): python writing/2026-11-what-is-bioinformatics/sra_growth.py
"""
import pathlib, sys

import pandas as pd
from plotnine import (ggplot, aes, geom_line, geom_point, annotate, labs, theme,
                      scale_x_datetime, scale_y_continuous)

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "tools" / "plots"))
from ng_figure import ng_figure                                                  # noqa: E402
from ngtheme import (theme_ng, scale_color_ng, scale_fill_ng, scale_shape_ng,    # noqa: E402
                     TOKENS, LINE, POINT, RING, SANS)

PB = 1e15
LOC_PB = 21                                  # Library of Congress digital collection, as on the slide
GENOME_1000 = pd.Timestamp("2019-02-28")     # NHGRI cost per genome first below $1,000 ($993), and stays below
LABEL_SIZE = 9                               # direct labels match the tick labels (9pt)

raw = pd.read_csv(HERE / "sra_stat.csv")
raw["date"] = pd.to_datetime(raw["date"], format="%m/%d/%Y")
long = pd.concat([
    pd.DataFrame({"date": raw["date"], "pb": raw["bytes"] / PB, "access": "All data"}),
    pd.DataFrame({"date": raw["date"], "pb": raw["open_access_bytes"] / PB, "access": "Publicly available"}),
])
start, end = raw["date"].min(), raw["date"].max()
last = long[long["date"] == end].set_index("access")["pb"]
at_1000 = raw.iloc[(raw["date"] - GENOME_1000).abs().argsort().iloc[0]]


def nearest(when):
    return raw.iloc[(raw["date"] - when).abs().argsort().iloc[0]]["date"]


# Sparse markers give each series a shape as well as a colour (circle, then square); the extra
# all-data marker is the $1,000 genome. The line ends carry a marker and a direct label.
mark_dates = [nearest(pd.Timestamp(d)) for d in ("2017-07-01", "2021-01-01")] + [end]
marks = pd.concat([
    long[long["date"].isin(mark_dates)],
    long[(long["date"] == at_1000["date"]) & (long["access"] == "All data")],
])


def plot(mode):
    t = TOKENS[mode]
    label_x = end + pd.Timedelta(days=90)
    return (
        ggplot(long, aes("date", "pb", color="access"))
        + annotate("segment", x=start, xend=end, y=LOC_PB, yend=LOC_PB, color=t["muted"], size=0.5,
                   linetype="dashed")   # first layer: drawn behind the series, markers and labels
        + annotate("text", x=pd.Timestamp("2008-01-01"), y=LOC_PB + 0.8, ha="left", va="bottom",
                   label=f"Library of Congress digital collection ({LOC_PB} PB)",
                   family=SANS, size=LABEL_SIZE, color=t["muted"])
        + geom_line(size=LINE)
        + geom_point(aes(shape="access", fill="access"), data=marks, color=t["surface"],
                     size=POINT, stroke=RING)
        + annotate("text", x=at_1000["date"] - pd.Timedelta(days=60), y=at_1000["bytes"] / PB + 1.2, ha="right", va="bottom",
                   label="Whole genome\nsequencing < $1,000", family=SANS, size=LABEL_SIZE, color=t["ink"])
        # every line ends in a direct label in ink, so no legend is needed
        + annotate("text", x=label_x, y=last["All data"], ha="left", va="center",
                   label=f"All data\n{last['All data']:.1f} PB", family=SANS, size=LABEL_SIZE, color=t["ink"])
        + annotate("text", x=label_x, y=last["Publicly available"], ha="left", va="center",
                   label=f"Publicly available\n{last['Publicly available']:.1f} PB", family=SANS,
                   size=LABEL_SIZE, color=t["ink"])
        + scale_color_ng(mode) + scale_fill_ng(mode) + scale_shape_ng()
        + scale_x_datetime(date_labels="%Y", breaks=pd.date_range("2009-01-01", "2023-01-01", freq="2YS"),
                           limits=(start, end + pd.Timedelta(days=1150)))
        + scale_y_continuous(breaks=[0, 10, 20, 30], limits=(0, 34), expand=(0, 0))
        + labs(x="", y="Data stored (PB)", title="Growth of the NCBI Sequence Read Archive",
               subtitle=f"Total data stored, {start:%B %Y} to {end:%B %Y}, n = {len(raw):,} snapshots",
               caption="Sources: NCBI SRA growth statistics and NHGRI sequencing costs, downloaded November 2026")
        + theme_ng(mode)
        + theme(legend_position="none")
    )


if __name__ == "__main__":
    fig = ng_figure(
        plot, "sra_growth", dir=str(HERE),
        alt=(f"Line chart of data stored in the NCBI Sequence Read Archive from 2007 to 2024. "
             f"Both lines stay near zero until about 2013, then rise steeply: all data reaches "
             f"{last['All data']:.1f} petabytes and publicly available data {last['Publicly available']:.1f} "
             f"petabytes by February 2024, passing the {LOC_PB} petabyte Library of Congress digital "
             f"collection. A point marks February 2019, when whole genome sequencing fell below $1,000."),
        caption=f"NCBI Sequence Read Archive storage, n = {len(raw):,} snapshots, {start:%b %Y} to {end:%b %Y}.")
    print(fig.html.replace(str(HERE) + "/", ""))
