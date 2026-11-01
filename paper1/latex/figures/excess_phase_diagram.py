"""Figure E.1 of the paper: the excess phase diagram, drawn for print (loop0010 item 12).

    python3 paper1/latex/figures/excess_phase_diagram.py extract   # -> paper1/latex/data/excess_phase_diagram.csv
    python3 paper1/latex/figures/excess_phase_diagram.py draw      # -> paper1/figures/excess_phase_diagram.{pdf,png}
    python3 paper1/latex/figures/excess_phase_diagram.py           # both

Two panels on one axis, the realised excess `e = (n_ones - m) / n`.

Top: where the instances on record sit. One row per collection: the 24 SCOOP
instances as points; the Chu & Stuckey `m = n` classes as the median of each
density `d` over every size (30-125 customers); the median and quartiles of
the other collections. Three lines: `e_g(1) = 0.618`, the branching-factor-one
point of the random incidence graph at `m = n`; `e = 1`, where the first-moment
constant becomes positive; the band `e = 2-2.4`, where the nodes to refute
`optimum - 1` peak on generated covers at 15-75 customers.

Bottom: what is proved and measured about `opt / n` on random covers with
`m = n` patterns: the first-moment constant `beta*(d, 1)` (a theorem, below the
truth), the slope `b` of `opt = a + b n` fitted to certified instances at
30-100 customers with its 2 se bar (measured), and the constant `beta+(d, 1)`
of the analysed constructions, the BFS layers and the pattern-count greedy
independent set (proved on paper for the uniform model with the concentration
step cited). The thin grey lines are `b` at `m = n / 2` and `m = 2 n`: at
equal excess the slope differs, so `opt / n` is not a function of `e` alone.

`extract` reads the recorded CSVs -- `learning/data/excess.csv` (item 01's map),
`learning/data/excess_rule.csv` through `learning.excess.series_slopes` (item
02), `reports/scratch/beta_plus/beta_plus_table.csv` (item 07) -- and writes
one small CSV under `paper1/latex/data/`, which is committed; `draw` reads that
CSV and nothing else, so the figure regenerates from the repository.
`tests/test_paper1_latex.py` checks the CSV against its sources.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA_CSV = ROOT / "paper1" / "latex" / "data" / "excess_phase_diagram.csv"
OUT_PDF = ROOT / "paper1" / "figures" / "excess_phase_diagram.pdf"
OUT_PNG = ROOT / "reports" / "figures" / "excess_phase_diagram.png"
BETA_PLUS_CSV = ROOT / "reports" / "scratch" / "beta_plus" / "beta_plus_table.csv"

E_GIANT = (5 ** 0.5 - 1) / 2          # e_g(r) = (sqrt(r^2 + 4r) - r) / 2 at r = 1
E_THRESHOLD = 1.0
RIDGE = (2.0, 2.4)
COLLECTIONS = ["SCOOP", "Faggioli-Bentivoglio", "Harvey", "Simonis", "Shaw", "Challenge"]
_CS_CLASS = re.compile(r"Random-(\d+)-(\d+)-(\d+)")

# the reference palette, categorical slots 1-3 (validated all-pairs) and the inks
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, INK3, RULE = "#0b0b0b", "#52514e", "#9a9994", "#c3c2b7"
BAND = "#f1f0eb"


# ----------------------------------------------------------------------------
# extract
# ----------------------------------------------------------------------------

def _class_rows(corpus: pd.DataFrame) -> list[dict]:
    cs = corpus[corpus["collection"] == "Chu & Stuckey"].copy()
    parts = cs["instance_name"].str.extract(_CS_CLASS).astype(float)
    cs["n_cls"], cs["m_cls"], cs["d"] = parts[0], parts[1], parts[2]
    square = cs[cs["n_cls"] == cs["m_cls"]]
    rows = []
    for d, g in square.groupby("d"):
        rows.append({"kind": "class", "label": f"Chu & Stuckey d = {int(d)}", "d": int(d), "mu": 1.0,
                     "e": float(g["e"].median()), "e_lo": float(g["e"].min()), "e_hi": float(g["e"].max()),
                     "value": float((g["optimum"] / g["n"]).mean()), "count": len(g)})
    return rows


def extract(out: Path = DATA_CSV) -> pd.DataFrame:
    from learning.excess import RATIO_LABELS_INV, load, load_rule, series_slopes
    frame = load()
    corpus = frame[frame["source"] == "corpus"]
    rows: list[dict] = []
    for name in COLLECTIONS:
        g = corpus[corpus["collection"] == name]
        rows.append({"kind": "collection", "label": name, "e": float(g["e"].median()),
                     "e_lo": float(g["e"].quantile(0.25)), "e_hi": float(g["e"].quantile(0.75)), "count": len(g)})
    for _, r in corpus[corpus["collection"] == "SCOOP"].sort_values("e").iterrows():
        rows.append({"kind": "scoop", "label": r["instance_name"], "e": float(r["e"]),
                     "value": float(r["optimum"] / r["n"]), "count": 1})
    rows += _class_rows(corpus)
    slopes = series_slopes(load_rule())
    slopes = slopes[slopes["constant e"] & (slopes["generator"] == "fixed")]
    for _, s in slopes.iterrows():
        rows.append({"kind": "series", "label": f"fixed d = {int(s['param'])}, m = {s['r']}", "d": int(s["param"]),
                     "mu": float(RATIO_LABELS_INV[s["r"]]), "e": float(s["e"]), "value": float(s["b"]), "value_se": float(s["se b"]),
                     "value2": float(s["beta* (sizes)"]), "count": int(s["instances"])})
    bp = pd.read_csv(BETA_PLUS_CSV)
    for _, s in bp.iterrows():
        rows.append({"kind": "beta_plus", "label": f"uniform d = {int(s['d'])}, mu = {s['mu']:g}", "d": int(s["d"]),
                     "mu": float(s["mu"]), "e": float(s["e"]), "value": float(s["beta_plus"]),
                     "value2": float(s["beta_star"]), "count": 0})
    table = pd.DataFrame(rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as handle:
        handle.write("# Generated by python3 paper1/latex/figures/excess_phase_diagram.py extract. Do not edit by hand.\n"
                     "# Sources: learning/data/excess.csv (item 01), learning/data/excess_rule.csv via "
                     "learning.excess.series_slopes (item 02), reports/scratch/beta_plus/beta_plus_table.csv (item 07).\n")
        table.to_csv(handle, index=False, float_format="%.6g")
    return table


def load_data(path: Path = DATA_CSV) -> pd.DataFrame:
    return pd.read_csv(path, comment="#")


# ----------------------------------------------------------------------------
# draw
# ----------------------------------------------------------------------------

def _style(ax):
    ax.grid(False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(RULE)
    ax.tick_params(colors=INK2, labelsize=7.5, length=3)


def _lines(ax, labels: bool):
    ax.axvspan(*RIDGE, color=BAND, zorder=0)
    ax.axvline(E_GIANT, color=INK3, lw=0.9, ls="--", zorder=1)
    ax.axvline(E_THRESHOLD, color=INK3, lw=0.9, zorder=1)
    if labels:
        y = 1.02
        kw = dict(fontsize=7, color=INK2, ha="center", va="bottom", transform=ax.get_xaxis_transform())
        ax.text(E_GIANT, y, "$e_g$", **kw)
        ax.text(E_THRESHOLD, y, "$e = 1$", **kw)
        ax.text((RIDGE[0] * RIDGE[1]) ** 0.5, y, "ridge", **kw)


def draw(data: pd.DataFrame, out_pdf: Path = OUT_PDF, out_png: Path = OUT_PNG) -> tuple[Path, Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    plt.rcParams.update({"font.family": "serif", "font.size": 8, "pdf.fonttype": 42})
    fig, (top, bot) = plt.subplots(2, 1, figsize=(6.4, 4.9), sharex=True,
                                   gridspec_kw={"height_ratios": [0.9, 1.3], "hspace": 0.12})

    # --- top: where the instances sit -------------------------------------------------
    rows = [("SCOOP (24)", "scoop", None),
            ("Chu & Stuckey, $m = n$ (125)", "class", None),
            ("Faggioli–Bentivoglio (300)", "collection", "Faggioli-Bentivoglio"),
            ("Harvey (2,130)", "collection", "Harvey"),
            ("Simonis (3,630)", "collection", "Simonis"),
            ("Shaw (25)", "collection", "Shaw"),
            ("Challenge (46)", "collection", "Challenge")]
    _lines(top, labels=True)
    ys = list(range(len(rows)))[::-1]
    for y, (name, kind, label) in zip(ys, rows):
        if kind == "scoop":
            g = data[data["kind"] == "scoop"]
            jitter = [((i * 7919) % 11 - 5) * 0.035 for i in range(len(g))]
            top.plot(g["e"], [y + j for j in jitter], ls="none", marker="o", ms=3.2, mfc=INK, mec="white",
                     mew=0.4, zorder=3)
        elif kind == "class":
            g = data[data["kind"] == "class"].sort_values("d")
            top.plot(g["e"], [y] * len(g), ls="none", marker="s", ms=5, color=BLUE, zorder=3)
            for _, r in g.iterrows():
                top.text(r["e"], y + 0.3, f"$d={int(r['d'])}$", fontsize=6.5, color=INK2, ha="center", va="bottom")
        else:
            r = data[(data["kind"] == "collection") & (data["label"] == label)].iloc[0]
            top.plot([r["e_lo"], r["e_hi"]], [y, y], color=INK2, lw=1.2, solid_capstyle="butt", zorder=2)
            top.plot([r["e"]], [y], ls="none", marker="o", ms=4.5, mfc="white", mec=INK, mew=1.0, zorder=3)
    top.set_yticks(ys)
    top.set_yticklabels([r[0] for r in rows], fontsize=7.5, color=INK2)
    top.set_ylim(-0.7, len(rows) - 0.3)
    top.tick_params(axis="y", length=0)
    _style(top)
    top.spines["left"].set_visible(False)

    # --- bottom: opt / n on random covers ---------------------------------------------
    _lines(bot, labels=False)
    series = data[data["kind"] == "series"]
    for mu, ls in ((0.5, ":"), (2.0, "--")):
        g = series[series["mu"] == mu].sort_values("e")
        bot.plot(g["e"], g["value"], color=INK3, lw=0.9, ls=ls, zorder=2)
    s1 = series[series["mu"] == 1.0].sort_values("e")
    bp = data[(data["kind"] == "beta_plus") & (data["mu"] == 1.0)].sort_values("e")
    bot.plot(bp["e"], bp["value"], color=ORANGE, lw=1.6, marker="o", ms=4, zorder=3)
    bot.plot(s1["e"], s1["value2"], color=AQUA, lw=1.6, marker="o", ms=4, zorder=3)
    bot.errorbar(s1["e"], s1["value"], yerr=2 * s1["value_se"], fmt="o", ms=4, color=BLUE, lw=1.6, elinewidth=0.9,
                 capsize=0, zorder=4)
    bot.plot(s1["e"], s1["value"], color=BLUE, lw=1.6, zorder=3)
    bot.text(bp["e"].iloc[-1] * 1.06, bp["value"].iloc[-1], r"$\beta^{+}$", fontsize=7.5, color=ORANGE, va="center")
    bot.text(s1["e"].iloc[-1] * 1.06, s1["value"].iloc[-1] + 0.035, "$b$", fontsize=7.5, color=BLUE, va="center")
    bot.text(s1["e"].iloc[-1] * 1.06, s1["value2"].iloc[-1] - 0.045, r"$\beta^{*}$", fontsize=7.5, color=AQUA,
             va="center")
    bot.set_xscale("log")
    bot.set_xlim(0.5, 25)
    bot.set_ylim(-0.02, 1.0)
    bot.set_xticks([0.5, 1, 2, 5, 10, 20])
    bot.set_xticklabels(["0.5", "1", "2", "5", "10", "20"])
    bot.set_xlabel("realised excess $e = (n_{\\mathrm{ones}} - m)/n$", fontsize=8, color=INK2)
    bot.set_ylabel("per customer", fontsize=8, color=INK2)
    _style(bot)
    handles = [Line2D([], [], color=AQUA, marker="o", ms=4, lw=1.6, label=r"$\beta^{*}(d,1)$, first moment (theorem)"),
               Line2D([], [], color=BLUE, marker="o", ms=4, lw=1.6, label="$b$, certified slope at $30$–$100$ (measured)"),
               Line2D([], [], color=ORANGE, marker="o", ms=4, lw=1.6, label=r"$\beta^{+}(d,1)$, analysed constructions"),
               Line2D([], [], color=INK3, lw=0.9, ls=":", label="$b$ at $m = n/2$ (measured)"),
               Line2D([], [], color=INK3, lw=0.9, ls="--", label="$b$ at $m = 2n$ (measured)")]
    bot.legend(handles=handles, loc="upper left", frameon=False, fontsize=7, handlelength=2.2)

    for p in (out_pdf, out_png):
        p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig(out_png, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out_pdf, out_png


def main(argv: list[str]) -> int:
    stage = argv[0] if argv else "all"
    if stage in ("extract", "all"):
        sys.path.insert(0, str(ROOT))
        table = extract()
        print(f"wrote {DATA_CSV} ({len(table)} rows)")
    if stage in ("draw", "all"):
        pdf, png = draw(load_data())
        print(f"wrote {pdf} and {png}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
