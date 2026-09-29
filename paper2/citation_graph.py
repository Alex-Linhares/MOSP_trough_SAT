"""Who cites the twelve papers of Linhares & Yanasse (2002) Table 1?

Companion figure to `popularity.md`. For every Table 1 reference that OpenAlex
indexes, fetch the works that cite it, and draw one network:

- **large nodes**: the Table 1 papers, coloured by the discipline Table 1 gives
  their problem (operations research, VLSI design, graph theory) and labelled
  with the problem name;
- **small nodes**: the works citing them, coloured by their OpenAlex field;
- **edges**: citations. A work that cites several Table 1 papers sits between
  them, so the bridges between communities are visible.

A second figure is `popularity.md`'s table as bars, same colours.

    python -m paper2.citation_graph            # fetch (cached) and draw
    python -m paper2.citation_graph --refresh  # re-fetch from OpenAlex

Cache: `paper2/data/openalex_citations.json`. Figures: `paper2/figures/`.
Kashiwabara & Fujisawa (1979), reference [5], has no OpenAlex record and is
absent, as in `popularity.md`. Counts are OpenAlex's and run lower than Google
Scholar's.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "data" / "openalex_citations.json"
FIGS = HERE / "figures"
MAILTO = "a@linhares.ltd"

# ref, DOI, short label, problem(s), Table 1 discipline
TABLE1 = [
    ("LY2002", "10.1016/S0305-0548(01)00054-5", "Linhares & Yanasse 2002", "Table 1 itself", "OR"),
    ("1", "10.1016/S0377-2217(97)84107-0", "Yanasse 1997", "MOSP", "OR"),
    ("4", "10.1016/S0305-0548(98)80001-4", "Fink & Voss 1999", "MOSP", "OR"),
    ("6", "10.1007/978-3-7091-9076-0_2", "Möhring 1990", "gate matrix layout,\nPLA folding", "VLSI"),
    ("7", "10.1109/TCS.1979.1084695", "Ohtsuki et al. 1979", "one-dimensional logic", "VLSI"),
    ("8", "10.1109/TCAD.1985.1270118", "Wing, Huang & Wang 1985", "gate matrix layout", "VLSI"),
    ("9", "10.1016/0012-365X(85)90046-9", "Kirousis & Papadimitriou 1985", "node search game", "GT"),
    ("10", "10.1016/0304-3975(86)90146-5", "Kirousis & Papadimitriou 1986", "edge search game", "GT"),
    ("11", "10.1016/0166-218X(92)90208-R", "Kornai & Tuza 1992", "narrowness", "GT"),
    ("12", "10.1016/S0166-218X(97)00131-5", "Fomin 1998", "split bandwidth", "GT"),
    ("13", "10.1016/0020-0190(92)90234-M", "Kinnersley 1992", "pathwidth,\nvertex separation", "GT"),
    ("14", "10.1007/BF00264496", "Lengauer 1981", "edge separation", "GT"),
]
DISCIPLINE = {"OR": ("operations research", "#d62728"),
              "VLSI": ("VLSI design", "#ff7f0e"),
              "GT": ("graph theory", "#1f77b4")}
FIELD_COLOURS = {"Computer Science": "#6baed6", "Mathematics": "#74c476",
                 "Engineering": "#fdae6b", "Decision Sciences": "#e377c2",
                 "Business, Management and Accounting": "#c49c94"}
OTHER = "#bdbdbd"


def _get(url: str) -> dict:
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"OpenAlex unreachable: {url}")


def fetch() -> dict:
    out = {"fetched": time.strftime("%Y-%m-%d"), "refs": {}, "works": {}}
    for ref, doi, label, problem, disc in TABLE1:
        w = _get(f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}"
                 f"?select=id,display_name,cited_by_count,publication_year&mailto={MAILTO}")
        wid = w["id"].rsplit("/", 1)[1]
        citing, cursor = [], "*"
        while cursor:
            page = _get("https://api.openalex.org/works?"
                        f"filter=cites:{wid}&per-page=200&cursor={cursor}"
                        "&select=id,display_name,publication_year,primary_topic"
                        f"&mailto={MAILTO}")
            for c in page["results"]:
                cid = c["id"].rsplit("/", 1)[1]
                citing.append(cid)
                pt = c.get("primary_topic") or {}
                out["works"][cid] = {
                    "title": c.get("display_name"), "year": c.get("publication_year"),
                    "field": (pt.get("field") or {}).get("display_name"),
                    "domain": (pt.get("domain") or {}).get("display_name")}
            cursor = page["meta"].get("next_cursor")
        out["refs"][ref] = {"openalex": wid, "cited_by_count": w["cited_by_count"],
                            "year": w.get("publication_year"), "citing": citing}
        print(f"[{ref}] {label}: {len(citing)} citing works")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, indent=1))
    return out


def draw_network(data: dict) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx
    from matplotlib.lines import Line2D

    meta = {ref: (label, problem, disc) for ref, _, label, problem, disc in TABLE1}
    table_ids = {data["refs"][r]["openalex"]: r for r in data["refs"]}
    G = nx.Graph()
    for ref in data["refs"]:
        G.add_node(("T", ref))
    for ref, rec in data["refs"].items():
        for cid in rec["citing"]:
            if cid in table_ids:                     # a Table 1 paper citing another
                G.add_edge(("T", table_ids[cid]), ("T", ref), kind="table")
            else:
                G.add_edge(("C", cid), ("T", ref), kind="cite")
    # Table 1 papers fixed on a circle, grouped by discipline in table order;
    # citing works settle by spring force, so single-citers ring their paper
    # and works citing several papers are pulled inside, between them.
    import math
    order = [r for r, *_ in TABLE1 if r in data["refs"]]
    fixed = {}
    for i, ref in enumerate(order):
        a = math.pi / 2 - 2 * math.pi * i / len(order)
        fixed[("T", ref)] = (math.cos(a), math.sin(a))
    pos = nx.spring_layout(G, k=0.035, iterations=400, seed=3,
                           pos=dict(fixed), fixed=list(fixed))

    fig, ax = plt.subplots(figsize=(18, 12.5))
    cite_edges = [e for e in G.edges(data=True) if e[2]["kind"] == "cite"]
    nx.draw_networkx_edges(G, pos, edgelist=cite_edges, width=0.25, alpha=0.18,
                           edge_color="0.4", ax=ax)
    tab_edges = [e for e in G.edges(data=True) if e[2]["kind"] == "table"]
    nx.draw_networkx_edges(G, pos, edgelist=tab_edges, width=0.9, alpha=0.45,
                           edge_color="k", style="dashed", ax=ax)
    cnodes = [n for n in G if n[0] == "C"]
    ccol = [FIELD_COLOURS.get(data["works"][n[1]]["field"], OTHER) for n in cnodes]
    csize = [6 + 10 * (G.degree(n) - 1) for n in cnodes]
    nx.draw_networkx_nodes(G, pos, nodelist=cnodes, node_color=ccol, node_size=csize,
                           linewidths=0, alpha=0.9, ax=ax)
    tnodes = [n for n in G if n[0] == "T"]
    tcol = [DISCIPLINE[meta[n[1]][2]][1] for n in tnodes]
    tsize = [300 + 9 * data["refs"][n[1]]["cited_by_count"] for n in tnodes]
    nx.draw_networkx_nodes(G, pos, nodelist=tnodes, node_color=tcol, node_size=tsize,
                           edgecolors="k", linewidths=1.2, ax=ax)
    for n in tnodes:
        label, problem, _ = meta[n[1]]
        cnt = data["refs"][n[1]]["cited_by_count"]
        x, y = fixed[n]
        r = 1.22 + 0.14 * (tsize[tnodes.index(n)] / max(tsize)) ** 0.5
        ax.text(r * x, r * y, f"{problem}\n{label} ({cnt})", ha="center", va="center",
                fontsize=9.5, weight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.7", alpha=0.9))
    ax.set_xlim(-1.75, 1.75); ax.set_ylim(-1.7, 1.7); ax.set_aspect("equal")

    bridges = sum(1 for n in cnodes if G.degree(n) >= 2)
    handles = [Line2D([], [], marker="o", ls="", ms=13, mfc=c, mec="k", label=f"Table 1 paper: {name}")
               for name, c in DISCIPLINE.values()]
    counts = Counter(data["works"][n[1]]["field"] for n in cnodes)
    for field, c in FIELD_COLOURS.items():
        if counts.get(field):
            handles.append(Line2D([], [], marker="o", ls="", ms=7, mfc=c, mec="none",
                                  label=f"citing work, {field} ({counts[field]})"))
    other = sum(v for k, v in counts.items() if k not in FIELD_COLOURS)
    handles.append(Line2D([], [], marker="o", ls="", ms=7, mfc=OTHER, mec="none",
                          label=f"citing work, other field ({other})"))
    handles.append(Line2D([], [], color="k", ls="--", label="one Table 1 paper cites another"))
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.93, 1.0), fontsize=9, frameon=False)
    ax.set_title("Who cites the papers behind Linhares & Yanasse (2002), Table 1\n"
                 f"{len(cnodes):,} citing works (OpenAlex, {data['fetched']}); large node size = citations; "
                 f"small nodes that cite two or more Table 1 papers ({bridges}) are drawn larger",
                 fontsize=11)
    ax.axis("off")
    fig.subplots_adjust(left=0.0, right=0.8, top=0.91, bottom=0.01)
    FIGS.mkdir(exist_ok=True)
    out = FIGS / "table1_citation_network.png"
    fig.savefig(out, dpi=150)
    return out


def draw_popularity() -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [  # from popularity.md, OpenAlex 2026-09-17
        ("graph path-width", 1609, "GT"), ("node search game", 127, "GT"),
        ("gate matrix layout", 126, "VLSI"), ("vertex separation", 105, "GT"),
        ("edge search game", 94, "GT"), ("PLA folding", 74, "VLSI"), ("MOSP", 60, "OR"),
        ("narrowness", 35, "GT"), ("split bandwidth", 35, "GT"), ("edge separation", 22, "GT"),
        ("one-dimensional logic", 18, "VLSI"), ("interval thickness", 10, "GT")]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    names = [r[0] for r in rows][::-1]
    vals = [r[1] for r in rows][::-1]
    cols = [DISCIPLINE[r[2]][1] for r in rows][::-1]
    ax.barh(names, vals, color=cols)
    for i, v in enumerate(vals):
        ax.text(v + 15, i, f"{v:,}", va="center", fontsize=9)
    ax.set_xlabel("works using the problem's name in title or abstract")
    ax.set_title("The twelve equivalent problems of Table 1, by how often the name is used\n"
                 "OpenAlex, computer science, mathematics, engineering and decision sciences, 2026-09-17",
                 fontsize=10)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=c, label=n) for n, c in DISCIPLINE.values()],
              loc="lower right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, 1800)
    fig.tight_layout()
    FIGS.mkdir(exist_ok=True)
    out = FIGS / "table1_popularity.png"
    fig.savefig(out, dpi=150)
    return out


# Name usage against citations of the defining paper, both from popularity.md
# (OpenAlex, 2026-09-17). Where Table 1 gives two references the problem's own
# is used: Wing et al. for gate matrix layout (Möhring is PLA folding's),
# Yanasse 1997 for MOSP. Kinnersley serves pathwidth and vertex separation,
# Möhring serves PLA folding and gate matrix layout, so shared papers are joined.
SCATTER = [
    ("graph path-width", 1609, 215, "GT", "Kinnersley 1992"),
    ("node search game", 127, 124, "GT", "Kirousis & Papadimitriou 1985"),
    ("gate matrix layout", 126, 89, "VLSI", "Wing et al. 1985"),
    ("vertex separation", 105, 215, "GT", "Kinnersley 1992"),
    ("edge search game", 94, 294, "GT", "Kirousis & Papadimitriou 1986"),
    ("PLA folding", 74, 134, "VLSI", "Möhring 1990"),
    ("MOSP", 60, 74, "OR", "Yanasse 1997"),
    ("narrowness", 35, 44, "GT", "Kornai & Tuza 1992"),
    ("split bandwidth", 35, 19, "GT", "Fomin 1998"),
    ("edge separation", 22, 77, "GT", "Lengauer 1981"),
    ("one-dimensional logic", 18, 107, "VLSI", "Ohtsuki et al. 1979"),
    ("interval thickness", 10, None, "GT", "Kashiwabara & Fujisawa 1979"),
]


def draw_scatter() -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    fig, ax = plt.subplots(figsize=(9.5, 7.5))
    lo, hi, floor = 7, 3000, 10
    ax.fill_between([lo, hi], [lo, hi], hi, color="#eef3fb", lw=0)
    ax.fill_between([lo, hi], lo, [lo, hi], color="#fbf1e6", lw=0)
    ax.plot([lo, hi], [lo, hi], color="0.5", ls="--", lw=1)
    ax.text(12, 560, "paper cited more\nthan the name is used:\nthe result lives on,\nthe name has faded",
            fontsize=9.5, color="#2b4c7e", va="top")
    ax.text(2700, 8.5, "name used more\nthan the paper is cited:\nthe name has spread\nbeyond its source",
            fontsize=9.5, color="#8a5a1c", ha="right", va="bottom")
    pts = {}
    for name, works, cites, disc, ref in SCATTER:
        c = DISCIPLINE[disc][1]
        if cites is None:
            ax.scatter(works, floor, marker="v", s=90, facecolor="white", edgecolor=c, lw=1.6, zorder=3)
            ax.annotate(f"{name}\n({ref}: not indexed)", (works, floor), xytext=(8, 2),
                        textcoords="offset points", fontsize=8.5, color="0.3")
            continue
        pts[name] = (works, cites)
        ax.scatter(works, cites, s=110, color=c, edgecolor="k", lw=0.6, zorder=3)
    for a, b in [("graph path-width", "vertex separation")]:
        (x1, y1), (x2, y2) = pts[a], pts[b]
        ax.plot([x1, x2], [y1, y2], color="0.6", lw=0.8, ls=":", zorder=2)
    offsets = {"graph path-width": (-10, 10, "right"), "vertex separation": (8, 6, "left"),
               "edge search game": (8, 4, "left"), "node search game": (8, -2, "left"),
               "gate matrix layout": (8, -10, "left"), "PLA folding": (8, 4, "left"),
               "MOSP": (8, -4, "left"), "narrowness": (-8, 4, "right"),
               "split bandwidth": (8, -6, "left"), "edge separation": (-8, 2, "right"),
               "one-dimensional logic": (8, 2, "left")}
    for name, (x, y) in pts.items():
        dx, dy, ha = offsets[name]
        ax.annotate(name, (x, y), xytext=(dx, dy), textcoords="offset points",
                    ha=ha, fontsize=9.5, weight="bold" if name in ("graph path-width", "MOSP") else None)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, 700)
    ax.set_xlabel("works using the problem's name in title or abstract (log scale)")
    ax.set_ylabel("citations of the paper Table 1 cites for it (log scale)")
    ax.set_title("Is the name alive, or only the result?\nThe twelve problems of Linhares & Yanasse (2002), Table 1; OpenAlex, 2026-09-17",
                 fontsize=10.5)
    ax.legend(handles=[Patch(color=c, label=n) for n, c in DISCIPLINE.values()],
              loc="center right", bbox_to_anchor=(1.0, 0.45), frameon=False)
    fig.text(0.01, 0.005, "Dotted line: pathwidth and vertex separation share Kinnersley 1992. "
             "Gate matrix layout uses Wing et al. 1985; MOSP uses Yanasse 1997.",
             ha="left", va="bottom", fontsize=7.5, color="0.35")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    FIGS.mkdir(exist_ok=True)
    out = FIGS / "table1_name_vs_citations.png"
    fig.savefig(out, dpi=150)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()
    data = fetch() if a.refresh or not CACHE.exists() else json.loads(CACHE.read_text())
    print(draw_network(data))
    print(draw_popularity())
    print(draw_scatter())
