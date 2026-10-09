"""Figure: the 34-customer instance on which the published rules refute a feasible k.

    python -m paper2.false_refutation_figure

Panels:
  (a) the gate matrix layout of the published search's answer: the order its
      full solver returns, as proved optimal, 7 tracks;
  (b) the gate matrix layout of an optimal order (the repaired search's
      answer), 6 tracks; gates in production order, nets packed into tracks by
      the left-edge algorithm;
  (c) the number of open stacks (nets crossing each gate) along both orders;
  (d) the MOSP graph: two copies of a 17-customer near-miss joined by one edge.

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
    from satisfiability.customer_search import solve
    rep = solve(inst, repaired_rules=True)
    pub = solve(inst, repaired_rules=False)
    assert (rep.value, pub.value) == (k, k + 1) and rep.proved and pub.proved
    prod = product_order(edges, rep.order)
    sp = spans(n, edges, prod)
    profile = [sum(1 for a, b in sp.values() if a <= t <= b) for t in range(len(prod))]
    tracks = left_edge(sp)
    pprod = product_order(edges, pub.order)
    psp = spans(n, edges, pprod)
    pprofile = [sum(1 for a, b in psp.values() if a <= t <= b) for t in range(len(pprod))]
    ptracks = left_edge(psp)
    f = dict(n=n, m=len(edges), k=k, prod=prod, spans=sp, profile=profile, tracks=tracks,
             peak=max(profile), verify_peak=max_open_stacks(inst, prod),
             n_tracks=max(tracks.values()) + 1,
             pub_value=pub.value, pub_prod=pprod, pub_spans=psp, pub_profile=pprofile,
             pub_tracks=ptracks, pub_peak=max(pprofile),
             pub_verify_peak=max_open_stacks(inst, pprod),
             pub_n_tracks=max(ptracks.values()) + 1,
             repaired_k=decide(inst, k, repaired_rules=True).status,
             repaired_k1=decide(inst, k - 1, repaired_rules=True).status,
             published_k=decide(inst, k, repaired_rules=False).status,
             published_k_plus=decide(inst, k + 1, repaired_rules=False).status,
             masks=masks, edges=edges)
    assert f["peak"] == f["verify_peak"] == f["n_tracks"] == k
    assert f["pub_peak"] == f["pub_verify_peak"] == f["pub_n_tracks"] == k + 1
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

    fig = plt.figure(figsize=(6.5, 7.6))
    gs = fig.add_gridspec(3, 2, height_ratios=[1.15, 1.0, 1.05], width_ratios=[1.35, 1.0],
                          hspace=0.5, wspace=0.18)
    ax_p = fig.add_subplot(gs[0, :])
    ax_a = fig.add_subplot(gs[1, :])
    ax_b = fig.add_subplot(gs[2, 0])
    ax_c = fig.add_subplot(gs[2, 1])
    m = len(prod)

    def layout(ax, order, spans_, tracks_, ntr, title):
        for t in range(m):
            ax.plot([t, t], [-0.6, ntr - 0.4], color="0.85", lw=0.5, zorder=0)
        pos = {p: t for t, p in enumerate(order)}
        for c, (a, b) in spans_.items():
            y = ntr - 1 - tracks_[c]
            ax.plot([a, b], [y, y], color=col(c), lw=2.0, solid_capstyle="round", zorder=2)
            for p, e in enumerate(f["edges"]):
                if c in e:
                    ax.plot(pos[p], y, "o", ms=2.4, color=col(c), zorder=3)
        ax.set_xlim(-1, m)
        ax.set_ylim(-0.8, ntr - 0.2)
        ax.set_yticks(range(ntr), [f"track {ntr - y}" for y in range(ntr)])
        ax.set_xticks([0, m - 1], ["gate 1", f"gate {m}"])
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(title, loc="left", fontsize=8.5)

    layout(ax_p, f["pub_prod"], f["pub_spans"], f["pub_tracks"], k + 1,
           f"(a) The published rules (Chu and Stuckey 2009), reported as optimal: {k + 1} tracks")
    layout(ax_a, prod, sp, tracks, k,
           f"(b) Our repaired search: an optimal layout, {k} tracks")

    # (c) open stacks along both orders
    ax_b.step(range(1, m + 1), f["pub_profile"], where="mid", color=copy_b, lw=1.1,
              label=f"published rules (peak {k + 1})")
    ax_b.step(range(1, m + 1), f["profile"], where="mid", color="0.15", lw=1.1,
              label=f"our repaired search (peak {k})")
    ax_b.set_ylim(0, k + 4.2)
    ax_b.set_xlim(0.5, m + 0.5)
    ax_b.set_xlabel("gate (production order)")
    ax_b.set_ylabel("open stacks")
    ax_b.legend(loc="upper right", fontsize=7.5, frameon=False, ncol=1)
    for s in ("top", "right"):
        ax_b.spines[s].set_visible(False)
    ax_b.set_title("(c) Open stacks at each gate", loc="left", fontsize=8.5)

    # (d) the MOSP graph: two glued copies
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(f["edges"])
    half_a = nx.kamada_kawai_layout(G.subgraph(range(17)))
    half_b = nx.kamada_kawai_layout(G.subgraph(range(17, n)))
    pos2 = {v: (x - 1.25, y) for v, (x, y) in half_a.items()}
    pos2.update({v: (x + 1.25, y) for v, (x, y) in half_b.items()})
    joins = [e for e in f["edges"] if (e[0] < 17) != (e[1] < 17)]
    other = [e for e in f["edges"] if e not in joins]
    nx.draw_networkx_edges(G, pos2, edgelist=other, ax=ax_c, width=0.6, edge_color="0.55")
    nx.draw_networkx_edges(G, pos2, edgelist=joins, ax=ax_c, width=1.6, edge_color="black",
                           style="dashed")
    nx.draw_networkx_nodes(G, pos2, ax=ax_c, node_size=16,
                           node_color=[col(v) for v in range(n)], linewidths=0)
    ax_c.set_axis_off()
    ax_c.set_title("(d) The graph: two copies, one join", loc="left", fontsize=8.5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(OUT.with_suffix(".png"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    return OUT.with_suffix(".pdf")


def main() -> None:
    path = draw()
    f = facts()
    print(f"{path}: n={f['n']} gates={f['m']} k={f['k']} tracks={f['n_tracks']} "
          f"published answer={f['pub_value']} ({f['pub_n_tracks']} tracks) "
          f"published(k)={f['published_k']} published(k+1)={f['published_k_plus']}")


if __name__ == "__main__":
    main()
