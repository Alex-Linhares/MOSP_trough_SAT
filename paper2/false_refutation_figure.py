"""Figure: the 34-customer instance on which the published rules refute a feasible k.

    python -m paper2.false_refutation_figure

Panels:
  (a) a gate matrix layout of an optimal order (the repaired search's witness):
      gates in production order, nets packed into tracks by the left-edge
      algorithm, 6 tracks;
  (b) the number of open stacks (nets crossing each gate) along that order,
      peaking at 6, with the published search's answer marked;
  (c) the MOSP graph: two copies of a 17-customer near-miss joined by one edge.

Every number drawn is recomputed here: the order's peak by plain simulation and
by `mosp.verify.max_open_stacks`, the tracks by left-edge packing, and the two
searches' answers through the public `decide`.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "paper2" / "data" / "false_refutation" / "instance34.json"
OUT = ROOT / "paper2" / "figures" / "false_refutation_34"


def load():
    d = json.loads(DATA.read_text())["minimised"]
    masks = d["masks"]
    n = len(masks)
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if masks[i] >> j & 1]
    return d, masks, n, edges


def instance(n, edges):
    from mosp.instance import MOSPInstance
    return MOSPInstance.from_matrix([[1 if v in e else 0 for e in edges] for v in range(n)],
                                    name="false_refutation_34")


def product_order(edges, closing):
    """Closing customer c cuts every pattern of c not yet cut."""
    placed, prod = set(), []
    for c in closing:
        for p, e in enumerate(edges):
            if c in e and p not in placed:
                placed.add(p)
                prod.append(p)
    return prod


def spans(n, edges, prod):
    pos = {p: t for t, p in enumerate(prod)}
    out = {}
    for c in range(n):
        ts = [pos[p] for p, e in enumerate(edges) if c in e]
        out[c] = (min(ts), max(ts))
    return out


def left_edge(sp):
    """Pack intervals into tracks, left end first; returns {net: track}."""
    ends: list[int] = []
    track = {}
    for c, (a, b) in sorted(sp.items(), key=lambda kv: kv[1]):
        for t, e in enumerate(ends):
            if e < a:
                ends[t] = b
                track[c] = t
                break
        else:
            ends.append(b)
            track[c] = len(ends) - 1
    return track


def facts():
    from mosp.verify import max_open_stacks
    from satisfiability.customer_search import decide
    d, masks, n, edges = load()
    k = d["k"]
    inst = instance(n, edges)
    rep = decide(inst, k, repaired_rules=True)
    prod = product_order(edges, rep.order)
    sp = spans(n, edges, prod)
    profile = [sum(1 for a, b in sp.values() if a <= t <= b) for t in range(len(prod))]
    tracks = left_edge(sp)
    f = dict(n=n, m=len(edges), k=k, prod=prod, spans=sp, profile=profile, tracks=tracks,
             peak=max(profile), verify_peak=max_open_stacks(inst, prod),
             n_tracks=max(tracks.values()) + 1,
             repaired_k=rep.status,
             repaired_k1=decide(inst, k - 1, repaired_rules=True).status,
             published_k=decide(inst, k, repaired_rules=False).status,
             published_k_plus=decide(inst, k + 1, repaired_rules=False).status,
             masks=masks, edges=edges)
    assert f["peak"] == f["verify_peak"] == f["n_tracks"] == k
    assert (f["repaired_k"], f["repaired_k1"]) == ("sat", "unsat")
    assert (f["published_k"], f["published_k_plus"]) == ("unsat", "sat")
    return f


def draw() -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx
    plt.rcParams.update({"font.size": 8, "pdf.fonttype": 42, "ps.fonttype": 42})

    f = facts()
    n, k, prod, sp, tracks = f["n"], f["k"], f["prod"], f["spans"], f["tracks"]
    copy_a = "#1f5fa8"
    copy_b = "#c0392b"
    col = lambda c: copy_a if c < 17 else copy_b

    fig = plt.figure(figsize=(6.5, 5.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.35, 1.0], width_ratios=[1.35, 1.0],
                          hspace=0.42, wspace=0.18)
    ax_a = fig.add_subplot(gs[0, :])
    ax_b = fig.add_subplot(gs[1, 0])
    ax_c = fig.add_subplot(gs[1, 1])

    # (a) gate matrix layout
    m = len(prod)
    for t in range(m):
        ax_a.plot([t, t], [-0.6, k - 0.4], color="0.85", lw=0.5, zorder=0)
    pos = {p: t for t, p in enumerate(prod)}
    for c, (a, b) in sp.items():
        y = k - 1 - tracks[c]
        ax_a.plot([a, b], [y, y], color=col(c), lw=2.2, solid_capstyle="round", zorder=2)
        for p, e in enumerate(f["edges"]):
            if c in e:
                ax_a.plot(pos[p], y, "o", ms=2.6, color=col(c), zorder=3)
    ax_a.set_xlim(-1, m)
    ax_a.set_ylim(-0.8, k - 0.2)
    ax_a.set_yticks(range(k), [f"track {k - y}" for y in range(k)])
    ax_a.set_xticks([0, m - 1], ["gate 1", f"gate {m}"])
    ax_a.tick_params(length=0)
    for s in ax_a.spines.values():
        s.set_visible(False)
    ax_a.set_title(f"(a) An optimal gate matrix layout: {n} nets on {m} gates in {k} tracks",
                   loc="left", fontsize=8.5)

    # (b) open stacks along the order
    ax_b.step(range(1, m + 1), f["profile"], where="mid", color="0.2", lw=1.2)
    ax_b.axhline(k, color="0.5", lw=0.6, ls=":")
    ax_b.set_ylim(0, k + 1.8)
    ax_b.set_xlim(0.5, m + 0.5)
    ax_b.set_xlabel("gate (production order)")
    ax_b.set_ylabel("open stacks")
    ax_b.text(1.5, k + 0.35, f"peak {k}: optimum (repaired search)", fontsize=7.5, va="bottom")
    ax_b.text(1.5, k + 1.15, f"published rules: no order with {k}; answer {k + 1}",
              fontsize=7.5, va="bottom", color=copy_b)
    for s in ("top", "right"):
        ax_b.spines[s].set_visible(False)
    ax_b.set_title("(b) Open stacks at each gate", loc="left", fontsize=8.5)

    # (c) the MOSP graph: two glued copies
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(f["edges"])
    half_a = nx.kamada_kawai_layout(G.subgraph(range(17)))
    half_b = nx.kamada_kawai_layout(G.subgraph(range(17, n)))
    layout = {v: (x - 1.25, y) for v, (x, y) in half_a.items()}
    layout.update({v: (x + 1.25, y) for v, (x, y) in half_b.items()})
    joins = [e for e in f["edges"] if (e[0] < 17) != (e[1] < 17)]
    other = [e for e in f["edges"] if e not in joins]
    nx.draw_networkx_edges(G, layout, edgelist=other, ax=ax_c, width=0.6, edge_color="0.55")
    nx.draw_networkx_edges(G, layout, edgelist=joins, ax=ax_c, width=1.6, edge_color="black",
                           style="dashed")
    nx.draw_networkx_nodes(G, layout, ax=ax_c, node_size=16,
                           node_color=[col(v) for v in range(n)], linewidths=0)
    ax_c.set_axis_off()
    ax_c.set_title("(c) The graph: two copies, one join", loc="left", fontsize=8.5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(OUT.with_suffix(".png"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    return OUT.with_suffix(".pdf")


def main() -> None:
    path = draw()
    f = facts()
    print(f"{path}: n={f['n']} gates={f['m']} k={f['k']} tracks={f['n_tracks']} "
          f"published(k)={f['published_k']} published(k+1)={f['published_k_plus']}")


if __name__ == "__main__":
    main()
