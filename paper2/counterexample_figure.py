"""The counterexample to Chu & Stuckey's Theorem 1 (the definite move), as a figure.

The 14-customer graph of `paper2/revised_algorithm.md`, Counterexample 4.5
(`cexGraph` in `lean/MOSPFormalization/Search/DefiniteMove.lean`;
`DEFINITE_CEX[0]` in `paper2/search_check.py`), drawn at the state where the
rule fails: S = {2}, k = 6. Customer 0 is playable and close(0, S) = open(0, S)
= 3, so the definite move keeps 0 alone. A solution from S exists, starting
with 1, 3, 4 or 6, and none starts with 0.

The script recomputes every fact it labels from the bitmasks, so the figure
cannot drift from the instance.

    python -m paper2.counterexample_figure
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

MASKS = [2201, 102, 30, 13, 21, 6690, 8514, 9857, 3904, 4000, 16256, 3873, 13344, 13504]
N, K, S, Q = len(MASKS), 6, 1 << 2, 0
OUT = Path(__file__).resolve().parent / "figures"


def opened(T: int) -> int:
    o = 0
    for i in range(N):
        if T >> i & 1:
            o |= MASKS[i]
    return o


@lru_cache(None)
def solvable(T: int) -> bool:
    if T == (1 << N) - 1:
        return True
    OT = opened(T)
    return any(not T >> c & 1 and ((OT | MASKS[c]) & ~T).bit_count() <= K and solvable(T | 1 << c)
               for c in range(N))


def facts() -> dict:
    OS = opened(S)
    new = {c: MASKS[c] & ~OS for c in range(N) if not S >> c & 1}
    close_set = [d for d in new if new[d] & ~new[Q] == 0]
    first_moves = [c for c in new if ((OS | MASKS[c]) & ~S).bit_count() <= K and solvable(S | 1 << c)]
    f = dict(open_stacks=[i for i in range(N) if OS >> i & 1 and not S >> i & 1],
             q_new=[i for i in range(N) if new[Q] >> i & 1],
             close=close_set, first_moves=first_moves,
             solvable_S=solvable(S), solvable_Sq=solvable(S | 1 << Q))
    assert len(f["q_new"]) == 3 and len(close_set) == 3, f      # open = close = 3
    assert f["solvable_S"] and not f["solvable_Sq"], f           # the theorem's conclusion fails
    return f


def draw() -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx
    from matplotlib.lines import Line2D

    f = facts()
    G = nx.Graph()
    G.add_nodes_from(range(N))
    G.add_edges_from((i, j) for i in range(N) for j in range(i + 1, N) if MASKS[i] >> j & 1)
    # A fixed, hand-tuned layout: S and its stacks on the left, q and its new
    # stacks in the middle, the rest on the right.
    pos = {2: (0.0, 0.0), 1: (-0.9, 1.0), 3: (0.9, 0.9), 4: (0.9, -0.9),
           0: (2.2, 0.0), 7: (3.4, 1.0), 11: (3.4, -1.0),
           5: (1.4, -2.3), 6: (0.0, 2.4), 8: (4.6, 0.0), 9: (4.4, -2.0),
           10: (5.8, 0.4), 12: (3.0, -3.0), 13: (4.2, 2.8)}
    colour = {}
    for v in range(N):
        if S >> v & 1:
            colour[v] = "#444444"                 # closed
        elif v == Q:
            colour[v] = "#d62728"                 # the move the rule keeps
        elif v in f["q_new"]:
            colour[v] = "#ff9896"                 # new stacks q would open
        elif v in f["open_stacks"]:
            colour[v] = "#1f77b4"                 # open after S
        else:
            colour[v] = "#e0e0e0"
    edge_q = [(u, v) for u, v in G.edges if Q in (u, v)]
    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    nx.draw_networkx_edges(G, pos, edgelist=[e for e in G.edges if e not in edge_q],
                           edge_color="0.7", width=1.0, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=edge_q, edge_color="#d62728", width=2.0, ax=ax)
    nx.draw_networkx_nodes(G, pos, node_color=[colour[v] for v in G], node_size=620,
                           edgecolors="k", linewidths=[2.8 if v in (3, 4) else 0.8 for v in G], ax=ax)
    dark = {v for v in G if colour[v] in ("#444444", "#d62728", "#1f77b4")}
    nx.draw_networkx_labels(G, pos, font_color="white", font_weight="bold",
                            labels={v: str(v) for v in dark}, ax=ax)
    nx.draw_networkx_labels(G, pos, font_color="black", font_weight="bold",
                            labels={v: str(v) for v in G if v not in dark}, ax=ax)
    for v in (3, 4):
        x, y = pos[v]
        ax.annotate("its only new stack: 0", (x, y), xytext=((x - 0.15, y + 0.32) if v == 3 else (x + 0.95, y - 0.5)),
                    fontsize=8.5, color="#333333", ha="center")
    handles = [Line2D([], [], marker="o", ls="", ms=12, mfc=c, mec="k", label=l) for c, l in [
        ("#444444", f"closed: S = {{2}}"),
        ("#1f77b4", f"open after S: {', '.join(map(str, f['open_stacks']))}"),
        ("#d62728", "q = 0, the move the definite move keeps"),
        ("#ff9896", f"new stacks q opens: {', '.join(map(str, f['q_new']))}, 0 itself included (open = 3)"),
        ("#e0e0e0", "other customers")]]
    handles.append(Line2D([], [], marker="o", ls="", ms=12, mfc="#1f77b4", mec="k", mew=2.8,
                          label=f"close(0, S) counts {', '.join(map(str, f['close']))}; 3 and 4 share one new stack"))
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.02), ncol=2,
              fontsize=8.5, frameon=False)
    ax.set_title("A counterexample to Chu & Stuckey's Theorem 1, at k = 6\n"
                 f"0 is playable and close(0, S) ≥ open(0, S), so the rule keeps 0 alone. A solution from S "
                 f"exists\n(first moves {', '.join(map(str, f['first_moves']))}), but none starts with 0.",
                 fontsize=10)
    ax.axis("off")
    ax.margins(0.08)
    fig.tight_layout()
    OUT.mkdir(exist_ok=True)
    outs = [OUT / "definite_counterexample.png", OUT / "definite_counterexample.pdf"]
    for p in outs:
        fig.savefig(p, dpi=200, bbox_inches="tight")
    return outs


if __name__ == "__main__":
    for p in draw():
        print(p)
