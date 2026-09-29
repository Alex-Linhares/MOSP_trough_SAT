"""Which of the Table 1 names have been growing, and which fading?

Companion to `popularity.md` and `citation_graph.py`. Three figures:

1. `figures/table1_trends_heatmap.png` -- one row per problem name, one column
   per five-year period; the shade is the name's publication *rate* (works per
   million works published in the same four fields that period) as a fraction
   of that row's own peak. Rows are sorted by the period of their peak, so the
   figure reads as a timeline of when each name was alive.
2. `figures/table1_trends_small_multiples.png` -- the same rates as one small
   line chart per name, each on its own vertical scale.
3. `figures/table1_citers_by_decade.png` -- for each Table 1 paper, the works
   citing it by decade of publication, split by the citing work's field. Uses
   the cache `citation_graph.py` already wrote.

Rates, not raw counts: the four fields publish many times more now than in
1980, so a raw count rises for nearly every name. The queries and the field
restriction are the ones behind `popularity.md` (recovered from the session
that produced it), but only works judged relevant by `paper2/relevance.py` are
counted: the raw searches are loose enough that for several names most hits are
about something else (see popularity.md, "Correction, 2026-09-29").

    python -m paper2.trends            # fetch (cached) and draw
    python -m paper2.trends --refresh  # re-fetch from OpenAlex

OpenAlex abstract coverage is thin before about 1990, which undercounts the
early VLSI names; those periods are shaded in the figures.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from paper2.citation_graph import CACHE as CITE_CACHE, DISCIPLINE, FIELD_COLOURS, OTHER, TABLE1

HERE = Path(__file__).resolve().parent
CACHE = HERE / "data" / "openalex_trends.json"
FIGS = HERE / "figures"
MAILTO = "a@linhares.ltd"
FIELDS = "fields/17|fields/26|fields/18|fields/22"   # CS, Mathematics, Decision Sciences, Engineering
START, END, STEP = 1970, 2024, 5                      # 2025-26 not yet fully indexed
LOW_COVERAGE_BEFORE = 1990

# name, query (as in popularity.md), discipline, total reported there
QUERIES = [
    ("MOSP", '"minimization of open stacks" OR "open stacks problem" OR "number of open stacks"', "OR", 60),
    ("gate matrix layout", '"gate matrix layout"', "VLSI", 126),
    ("one-dimensional logic", '"one-dimensional logic" OR "logic gate assignment"', "VLSI", 18),
    ("PLA folding", '"PLA folding" OR "programmable logic array folding"', "VLSI", 74),
    ("interval thickness", '"interval thickness" AND ("graph" OR "pathwidth")', "GT", 10),
    ("node search game", '"node search number" OR "node searching" OR "node search game"', "GT", 127),
    ("edge search game", '"edge search number" OR "edge searching" OR "edge search game"', "GT", 94),
    ("narrowness", '"narrowness of a graph" OR "graph narrowness"', "GT", 35),
    ("split bandwidth", '"split bandwidth" OR "splitting bandwidth"', "GT", 35),
    ("graph path-width", '"pathwidth" OR "path-width"', "GT", 1609),
    ("edge separation", '"edge separation" AND ("graph" OR "pebble" OR "pebbles")', "GT", 22),
    ("vertex separation", '"vertex separation"', "GT", 105),
]


def _get(url: str) -> dict:
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"MOSP-research/1.0 (mailto:{MAILTO})"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception:
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"OpenAlex unreachable: {url}")


def _by_year(flt: str) -> dict[int, int]:
    url = ("https://api.openalex.org/works?filter=" + urllib.parse.quote(flt, safe=':|,')
           + f"&group_by=publication_year&mailto={MAILTO}")
    d = _get(url)
    return {int(g["key"]): g["count"] for g in d["group_by"] if str(g["key"]).isdigit()}


def fetch() -> dict:
    out = {"fetched": time.strftime("%Y-%m-%d"), "fields_total": _by_year(f"primary_topic.field.id:{FIELDS}"),
           "names": {}}
    for name, q, _, reported in QUERIES:
        years = _by_year(f"title_and_abstract.search:{q},primary_topic.field.id:{FIELDS}")
        out["names"][name] = years
        print(f"{name:24} total {sum(years.values()):>5}  (popularity.md: {reported})")
        time.sleep(0.5)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, indent=1))
    return out


def binned(data: dict):
    """Return (bin starts, {name: counts}, {name: rate per million})."""
    bins = list(range(START, END + 1, STEP))
    tot = {int(k): v for k, v in data["fields_total"].items()}
    denom = [sum(tot.get(y, 0) for y in range(b, b + STEP)) for b in bins]
    counts, rates = {}, {}
    from collections import Counter
    from paper2.relevance import CACHE as CAND, kept_works
    cand = json.loads(CAND.read_text())
    for name, _, _, _ in QUERIES:
        # relevant works only (paper2/relevance.py); the raw search is kept in the cache
        yrs = Counter(w["year"] for w in kept_works(name, cand) if w.get("year"))
        c = [sum(yrs.get(y, 0) for y in range(b, b + STEP)) for b in bins]
        counts[name] = c
        rates[name] = [1e6 * x / d if d else 0.0 for x, d in zip(c, denom)]
    return bins, counts, rates


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def draw_heatmap(data: dict) -> Path:
    import numpy as np
    plt = _plt()
    from matplotlib.patches import Rectangle
    bins, counts, rates = binned(data)
    disc = {n: d for n, _, d, _ in QUERIES}
    def peak(n):
        r = rates[n]
        return (int(np.argmax(r)), -max(r))
    names = sorted((n for n in rates if max(rates[n])), key=peak)
    empty = [n for n in rates if not max(rates[n])]
    M = np.array([[v / max(rates[n]) if max(rates[n]) else 0 for v in rates[n]] for n in names])
    fig, ax = plt.subplots(figsize=(12, 6.8))
    im = ax.imshow(M, aspect="auto", cmap="magma_r", vmin=0, vmax=1)
    for i, n in enumerate(names):
        for j, c in enumerate(counts[n]):
            if c:
                ax.text(j, i, str(c), ha="center", va="center", fontsize=7.5,
                        color="white" if M[i, j] > 0.55 else "0.25")
    ax.set_xticks(range(len(bins)), [f"{b}–{str(b + STEP - 1)[2:]}" for b in bins], fontsize=8.5)
    ax.set_yticks(range(len(names)), [f"{n}  ({sum(counts[n])})" for n in names], fontsize=9.5)
    # row label count covers the plotted periods, 1970-2024
    for t, n in zip(ax.get_yticklabels(), names):
        t.set_color(DISCIPLINE[disc[n]][1]); t.set_fontweight("bold")
    low = sum(1 for b in bins if b + STEP <= LOW_COVERAGE_BEFORE)
    ax.add_patch(Rectangle((-0.5, -0.5), low, len(names), fill=False, hatch="///",
                           edgecolor="0.55", lw=0, zorder=3))
    if empty:
        ax.set_xlabel("No relevant works at all, so not shown: " + ", ".join(empty)
                      + ".   Hatched: before 1990, OpenAlex abstract coverage is thin.", fontsize=9)
    else:
        ax.set_xlabel("Hatched: before 1990, OpenAlex abstract coverage is thin.", fontsize=9)
    cb = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cb.set_label("rate as a fraction of that name's own peak")
    ax.set_title("When was each name alive?  Works per million published in CS, mathematics, engineering\n"
                 "and decision sciences, each row scaled to its own peak; numbers are raw works per period. "
                 "Rows sorted by peak.\nLabel colour: operations research (red), VLSI design (orange), "
                 f"graph theory (blue). OpenAlex, {data['fetched']}.", fontsize=9.5)
    fig.tight_layout()
    FIGS.mkdir(exist_ok=True)
    out = FIGS / "table1_trends_heatmap.png"
    fig.savefig(out, dpi=150)
    return out


def draw_small_multiples(data: dict) -> Path:
    plt = _plt()
    bins, counts, rates = binned(data)
    disc = {n: d for n, _, d, _ in QUERIES}
    order = [n for n, *_ in sorted(QUERIES, key=lambda q: -sum(counts[q[0]]))]
    mids = [b + STEP / 2 for b in bins]
    fig, axes = plt.subplots(3, 4, figsize=(14, 8.5), sharex=True)
    for ax, n in zip(axes.flat, order):
        c = DISCIPLINE[disc[n]][1]
        ax.axvspan(START, LOW_COVERAGE_BEFORE, color="0.92", lw=0)
        if not max(rates[n]):
            ax.text(0.5, 0.5, "no relevant works:\nevery search hit was\nabout something else",
                    transform=ax.transAxes, ha="center", va="center", fontsize=9, color="0.4")
            ax.set_yticks([])
        ax.plot(mids, rates[n], color=c, lw=2, marker="o", ms=3.5)
        ax.fill_between(mids, rates[n], color=c, alpha=0.15)
        ax.set_title(f"{n}  ({sum(counts[n])} works)", fontsize=10, color=c, weight="bold")
        ax.set_ylim(bottom=0)
        ax.set_xlim(START, END + 1)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8)
    for ax in axes[:, 0]:
        ax.set_ylabel("per million works", fontsize=8.5)
    fig.suptitle("Each name's publication rate over time, on its own scale (works per million published in the "
                 "same four fields, five-year periods).\nGrey: before 1990, where OpenAlex's abstract coverage is "
                 f"thin. OpenAlex, {data['fetched']}.", fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = FIGS / "table1_trends_small_multiples.png"
    fig.savefig(out, dpi=150)
    return out


def draw_citers(cite: dict) -> Path:
    import numpy as np
    plt = _plt()
    from matplotlib.patches import Patch
    decades = list(range(1970, 2030, 10))
    fields = ["Computer Science", "Engineering", "Mathematics"]
    colours = [FIELD_COLOURS[f] for f in fields] + [OTHER]
    meta = {r: (label, prob.replace("\n", " "), d) for r, _, label, prob, d in TABLE1}
    refs = [r for r, *_ in TABLE1 if r in cite["refs"]]
    fig, axes = plt.subplots(3, 4, figsize=(14, 8.5), sharex=True)
    for ax, ref in zip(axes.flat, refs):
        label, prob, d = meta[ref]
        stack = np.zeros((4, len(decades)))
        for cid in cite["refs"][ref]["citing"]:
            w = cite["works"].get(cid)
            if not w or not w.get("year"):
                continue
            j = min((w["year"] - 1970) // 10, len(decades) - 1)
            if j < 0:
                continue
            f = w.get("field")
            stack[fields.index(f) if f in fields else 3, j] += 1
        bottom = np.zeros(len(decades))
        for k in range(4):
            ax.bar(decades, stack[k], width=8, bottom=bottom, color=colours[k], align="edge")
            bottom += stack[k]
        ax.set_title(f"{prob}\n{label}", fontsize=9, color=DISCIPLINE[d][1], weight="bold")
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8)
        ax.set_xticks([x + 4 for x in decades], [f"{x}s" for x in decades], fontsize=7.5)
    for ax in axes[:, 0]:
        ax.set_ylabel("citing works", fontsize=8.5)
    fig.legend(handles=[Patch(color=c, label=l) for c, l in zip(colours, fields + ["other field"])],
               loc="lower center", ncol=4, frameon=False, fontsize=9)
    fig.suptitle("Who keeps citing each Table 1 paper, by decade of the citing work and its field "
                 f"(raw counts; OpenAlex, {cite['fetched']}; the 2020s are 2020-26).", fontsize=10.5)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    out = FIGS / "table1_citers_by_decade.png"
    fig.savefig(out, dpi=150)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()
    data = fetch() if a.refresh or not CACHE.exists() else json.loads(CACHE.read_text())
    print(draw_heatmap(data))
    print(draw_small_multiples(data))
    print(draw_citers(json.loads(CITE_CACHE.read_text())))
