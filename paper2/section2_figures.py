"""Section 2's three figures, print quality, and the numbers their captions quote.

The paper uses three of the six figures `popularity.md` shows (the choice and
its reasons are in `popularity.md`, "For the paper"):

- `figures/sec2_fig1_name_usage.pdf`: relevant works using each name (bars);
- `figures/sec2_fig2_timeline.pdf`: when each name was alive (rate heatmap);
- `figures/sec2_fig3_citation_network.pdf`: who cites the Table 1 papers.

They are redrawn from the same caches as `citation_graph.py` and `trends.py`,
with no network access: vector PDF (fonts embedded as TrueType), 6.5 in wide,
which is the text width of a one-column journal page, and no text below 7 pt
at that size. Titles are left to the LaTeX captions. A PNG preview is written
beside each PDF.

    python -m paper2.section2_figures            # draw, and print the caption numbers
    python -m paper2.section2_figures --numbers  # numbers only

Sources: `paper2/data/openalex_candidates.json` (search hits with text, fetched
2026-09-29), `paper2/data/relevance_labels.json` (the per-work labels),
`paper2/data/openalex_trends.json` (yearly field totals) and
`paper2/data/openalex_citations.json` (citing works, fetched 2026-09-29).
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from itertools import combinations
from pathlib import Path

from paper2.citation_graph import CACHE as CITE_CACHE, DISCIPLINE, FIELD_COLOURS, OTHER, TABLE1
from paper2.relevance import CACHE as CAND_CACHE, kept_works, relevant
from paper2.trends import CACHE as TREND_CACHE, LOW_COVERAGE_BEFORE, QUERIES, STEP, binned

HERE = Path(__file__).resolve().parent
FIGS = HERE / "figures"
WIDTH = 6.5          # inches: one-column text width
OR_REFS = {"LY2002", "1", "4"}
SHORT = {"Business, Management and Accounting": "Business & Management"}
# printed names in the figures, matching the paper's tables (review: one label per name)
LABEL = {"graph path-width": "pathwidth", "edge search game": "edge search",
         "node search game": "node search"}


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 8,
                         "axes.labelsize": 8, "xtick.labelsize": 7.5, "ytick.labelsize": 8,
                         "legend.fontsize": 7.5, "axes.edgecolor": "0.3",
                         "xtick.color": "0.25", "ytick.color": "0.15"})
    return plt


def _save(fig, stem: str) -> Path:
    FIGS.mkdir(exist_ok=True)
    out = FIGS / f"{stem}.pdf"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(FIGS / f"{stem}.png", dpi=200, bbox_inches="tight", pad_inches=0.02)
    return out


# --------------------------------------------------------------------- numbers

def numbers() -> dict:
    """Every number the method paragraph and the captions quote, recomputed."""
    cand = json.loads(CAND_CACHE.read_text())
    out = {"candidates_fetched": cand["fetched"], "names": {}}
    phrase_total = 0
    for name, *_ in QUERIES:
        ws = cand["names"][name]
        kept_list = kept_works(name, cand)
        kept = {w["id"] for w in kept_list}
        rule = {w["id"] for w in ws if relevant(name, w["text"])}
        # "relevant" counts records, as relevance.relevant_counts does (the published
        # figure); "distinct" counts OpenAlex ids, which differ where a record repeats
        out["names"][name] = {"hits": len(ws), "relevant": len(kept_list), "distinct": len(kept),
                              "phrase_rule": len(rule),
                              "agree": len({w["id"] for w in ws}) - len(kept ^ rule)}
        if name != "graph path-width":
            phrase_total += len(rule)
    n = out["names"]
    small = [k for k in n if k != "graph path-width"]
    out["hits_total"] = sum(v["hits"] for v in n.values())
    out["labelled"] = sum(n[k]["hits"] for k in small)
    out["labelled_relevant"] = sum(n[k]["relevant"] for k in small)
    out["labelled_agree_with_phrase_rule"] = sum(n[k]["agree"] for k in small)
    out["phrase_rule_small_total"] = phrase_total
    pw = cand["names"]["graph path-width"]
    kept_pw = kept_works("graph path-width", cand)
    no_word = [w for w in kept_pw if not re.search(r"path[\s\-]?width", w["text"].lower())]
    out["pathwidth_kept_without_the_word"] = len(no_word)
    out["of_which_no_abstract_in_cache"] = sum(1 for w in no_word if len(w["text"]) <= len(w["title"] or "") + 4)
    out["pathwidth_hits"] = len(pw)
    rank = sorted(n, key=lambda k: -n[k]["relevant"])
    out["mosp_rank_labels"] = rank.index("MOSP") + 1
    out["mosp_rank_phrase_rule"] = sorted(n, key=lambda k: -n[k]["phrase_rule"]).index("MOSP") + 1

    trend = json.loads(TREND_CACHE.read_text())
    bins, counts, rates = binned(trend)
    out["pathwidth_2020_24"] = counts["graph path-width"][bins.index(2020)]
    out["pathwidth_1970_2024"] = sum(counts["graph path-width"])
    out["pathwidth_rate_1990s"] = round(sum(rates["graph path-width"][bins.index(1990):bins.index(2000)]) / 2, 1)
    out["pathwidth_rate_2020_24"] = round(rates["graph path-width"][bins.index(2020)], 1)

    cite = json.loads(CITE_CACHE.read_text())
    out["citations_fetched"] = cite["fetched"]
    out["cited_by"] = {r: v["cited_by_count"] for r, v in cite["refs"].items()}
    disc = {r: d for r, _, _, _, d in TABLE1}
    table_ids = {v["openalex"] for v in cite["refs"].values()}
    cites = {}
    for r, v in cite["refs"].items():
        for c in v["citing"]:
            if c not in table_ids:
                cites.setdefault(c, set()).add(r)
    out["citing_works"] = len(cites)
    out["citing_two_or_more"] = sum(1 for s in cites.values() if len(s) >= 2)
    # disciplines of the eleven problem papers only: Linhares & Yanasse (2002), Table 1
    # itself, is not a problem's paper and does not make a work cross a discipline
    spans = Counter(frozenset(disc[r] for r in s if r != "LY2002") for s in cites.values())
    out["span_two_or_more_disciplines"] = sum(v for k, v in spans.items() if len(k) >= 2)
    out["span_gt_vlsi_only"] = spans[frozenset({"GT", "VLSI"})]
    out["mosp_and_graph_theory"] = sum(1 for s in cites.values() if s & OR_REFS and "GT" in {disc[r] for r in s})
    # citing works by the set of disciplines they cite, Linhares & Yanasse (2002) counted
    # as operations research (as mosp_and_graph_theory counts it): Section 3's island table
    sets = Counter("+".join(sorted({disc[r] for r in s})) for s in cites.values())
    out["discipline_sets"] = dict(sets)
    # relevant works per five-year period, 2005-2024: Section 3's period table
    out["periods_2005_24"] = {k: counts[k][bins.index(2005):bins.index(2020) + 1] for k in counts}
    return out


# --------------------------------------------------------------------- figures

def fig_name_usage(n: dict) -> Path:
    plt = _plt()
    from matplotlib.patches import Patch
    rows = sorted(((k, n[k]["relevant"], d) for k, _, d, _ in QUERIES), key=lambda r: (-r[1], r[0]))[::-1]
    fig, ax = plt.subplots(figsize=(WIDTH, 2.9))
    y = range(len(rows))
    ax.barh(list(y), [r[1] for r in rows], height=0.72, color=[DISCIPLINE[r[2]][1] for r in rows])
    for i, (name, v, _) in enumerate(rows):
        if v:
            ax.text(v + 12, i, f"{v:,}", va="center", fontsize=7.5, color="0.1")
        else:
            ax.text(12, i, f"0 (of {n[name]['hits']} search hits, none relevant)", va="center",
                    fontsize=7, color="0.35")
    ax.set_yticks(list(y), [LABEL.get(r[0], r[0]) for r in rows])
    ax.set_xlabel("relevant works using the name in title or abstract")
    ax.set_xlim(0, 1350)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(handles=[Patch(color=c, label=l) for l, c in DISCIPLINE.values()],
              loc="lower right", frameon=False, title="discipline in the 2002 table", title_fontsize=7.5)
    return _save(fig, "sec2_fig1_name_usage")


def fig_timeline() -> Path:
    import numpy as np
    plt = _plt()
    from matplotlib.patches import Patch, Rectangle
    trend = json.loads(TREND_CACHE.read_text())
    bins, counts, rates = binned(trend)
    disc = {k: d for k, _, d, _ in QUERIES}
    names = sorted((k for k in rates if max(rates[k])),
                   key=lambda k: (int(np.argmax(rates[k])), -max(rates[k])))
    empty = [k for k in rates if not max(rates[k])]
    M = np.array([[v / max(rates[k]) for v in rates[k]] for k in names])
    fig, ax = plt.subplots(figsize=(WIDTH - 0.72, 3.25))
    im = ax.imshow(M, aspect="auto", cmap="Purples", vmin=0, vmax=1)
    for i, k in enumerate(names):
        for j, c in enumerate(counts[k]):
            if c:
                ax.text(j, i, str(c), ha="center", va="center", fontsize=7,
                        color="white" if M[i, j] > 0.6 else "0.15")
    ax.set_xticks(range(len(bins)), [f"{b}\n–{str(b + STEP - 1)[2:]}" for b in bins], fontsize=7)
    ax.set_yticks(range(len(names)), [f"{LABEL.get(k, k)} ({sum(counts[k])})" for k in names])
    ax.tick_params(length=0)
    ax.tick_params(axis="y", pad=9)
    # discipline as a coloured tab left of each row; the label text stays black
    for i, k in enumerate(names):
        ax.add_patch(Rectangle((-0.5 - 0.17, i - 0.42), 0.12, 0.84, color=DISCIPLINE[disc[k]][1],
                               clip_on=False, transform=ax.transData))
    low = sum(1 for b in bins if b + STEP <= LOW_COVERAGE_BEFORE)
    ax.add_patch(Rectangle((-0.5, -0.5), low, len(names), fill=False, hatch="////",
                           edgecolor="0.78", lw=0, zorder=1.5))
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.015)
    cb.set_label("rate / that name's peak rate", fontsize=7)
    cb.ax.tick_params(labelsize=7)
    cb.outline.set_visible(False)
    handles = [Patch(color=c, label=l) for l, c in DISCIPLINE.values()]
    handles.append(Patch(facecolor="white", edgecolor="0.6", hatch="////",
                         label="before 1990: thin abstract coverage"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=4,
              frameon=False, fontsize=7, handlelength=1.4, columnspacing=1.2)
    ax.text(0.5, -0.31, "Not shown, no relevant works: " + ", ".join(LABEL.get(k, k) for k in empty) + ".",
            transform=ax.transAxes, ha="center", fontsize=7, color="0.3")
    return _save(fig, "sec2_fig2_timeline")


def fig_network() -> Path:
    plt = _plt()
    import networkx as nx
    from matplotlib.lines import Line2D
    data = json.loads(CITE_CACHE.read_text())
    meta = {r: (label, problem, d) for r, _, label, problem, d in TABLE1}
    table_ids = {data["refs"][r]["openalex"]: r for r in data["refs"]}
    G = nx.Graph()
    for ref in data["refs"]:
        G.add_node(("T", ref))
    for ref, rec in data["refs"].items():
        for cid in rec["citing"]:
            if cid in table_ids:
                G.add_edge(("T", table_ids[cid]), ("T", ref), kind="table")
            else:
                G.add_edge(("C", cid), ("T", ref), kind="cite")
    order = [r for r, *_ in TABLE1 if r in data["refs"]]
    fixed = {}
    for i, ref in enumerate(order):
        a = math.pi / 2 - 2 * math.pi * i / len(order)
        fixed[("T", ref)] = (math.cos(a), math.sin(a))
    pos = nx.spring_layout(G, k=0.035, iterations=400, seed=3, pos=dict(fixed), fixed=list(fixed))

    fig, ax = plt.subplots(figsize=(WIDTH, 5.6))
    cite_edges = [e for e in G.edges(data=True) if e[2]["kind"] == "cite"]
    nx.draw_networkx_edges(G, pos, edgelist=cite_edges, width=0.15, alpha=0.25, edge_color="0.45", ax=ax)
    tab_edges = [e for e in G.edges(data=True) if e[2]["kind"] == "table"]
    nx.draw_networkx_edges(G, pos, edgelist=tab_edges, width=0.6, alpha=0.6, edge_color="0.1",
                           style="dashed", ax=ax)
    cnodes = [v for v in G if v[0] == "C"]
    ccol = [FIELD_COLOURS.get(data["works"][v[1]]["field"], OTHER) for v in cnodes]
    csize = [1.2 + 3.5 * (G.degree(v) - 1) for v in cnodes]
    nx.draw_networkx_nodes(G, pos, nodelist=cnodes, node_color=ccol, node_size=csize, linewidths=0, ax=ax)
    tnodes = [v for v in G if v[0] == "T"]
    tsize = [40 + 1.6 * data["refs"][v[1]]["cited_by_count"] for v in tnodes]
    nx.draw_networkx_nodes(G, pos, nodelist=tnodes, node_color=[DISCIPLINE[meta[v[1]][2]][1] for v in tnodes],
                           node_size=tsize, edgecolors="white", linewidths=1.0, ax=ax)
    for v, s in zip(tnodes, tsize):
        label, problem, _ = meta[v[1]]
        x, y = fixed[v]
        r = 1.06 + 0.10 * (s / max(tsize)) ** 0.5     # just outside the node, text pointing outward
        ha = "left" if x > 0.3 else "right" if x < -0.3 else "center"
        va = "bottom" if y > 0.3 else "top" if y < -0.3 else "center"
        ax.text(r * x, r * y, f"{problem}\n{label} ({data['refs'][v[1]]['cited_by_count']})",
                ha=ha, va=va, multialignment="center", fontsize=7, color="0.1", linespacing=1.1,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="0.75", lw=0.5, alpha=0.95))
    ax.set_xlim(-1.75, 1.75); ax.set_ylim(-1.42, 1.38); ax.set_aspect("equal")
    ax.axis("off")
    counts = Counter(data["works"][v[1]]["field"] for v in cnodes)
    handles = [Line2D([], [], marker="o", ls="", ms=7, mfc=c, mec="white", label=f"Table 1 paper: {l}")
               for l, c in DISCIPLINE.values()]
    for field, c in FIELD_COLOURS.items():
        if counts.get(field):
            handles.append(Line2D([], [], marker="o", ls="", ms=4, mfc=c, mec="none",
                                  label=f"citing work: {SHORT.get(field, field)} ({counts[field]})"))
    other = sum(v for k, v in counts.items() if k not in FIELD_COLOURS)
    handles.append(Line2D([], [], marker="o", ls="", ms=4, mfc=OTHER, mec="none",
                          label=f"citing work: other field ({other})"))
    handles.append(Line2D([], [], color="0.1", ls="--", lw=0.6, label="a Table 1 paper cites another"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=3,
              frameon=False, fontsize=7, handletextpad=0.3, columnspacing=0.8)
    return _save(fig, "sec2_fig3_citation_network")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--numbers", action="store_true", help="print the caption numbers only")
    a = ap.parse_args()
    nums = numbers()
    print(json.dumps(nums, indent=1))
    if not a.numbers:
        print(fig_name_usage(nums["names"]))
        print(fig_timeline())
        print(fig_network())
