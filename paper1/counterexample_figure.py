"""The counterexample to Chu & Stuckey's Theorem 1 (the definite move), as a figure.

The 14-customer graph of `paper1/revised_algorithm.md`, Counterexample 4.5
(`cexGraph` in `lean/MOSPFormalization/Search/DefiniteMove.lean`;
`DEFINITE_CEX[0]` in `paper1/search_check.py`), drawn at the state where the
rule fails: S = {2}, k = 6. Customer 0 is playable and close(0, S) = open(0, S)
= 3, so the definite move keeps 0 alone. A solution from S exists, starting
with 1, 3, 4 or 6, and none starts with 0. Panel (b) is the intermediate set
B = {2, 3, 4} at which the repaired (hereditary) test fails: b(B) = 2 < 3 = b(X).
No title is drawn inside the figure; the caption carries it.

The script recomputes every fact it labels from the bitmasks, so the figure
cannot drift from the instance.

    python -m paper1.counterexample_figure
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


def border(T: int) -> list[int]:
    """The open stacks after closing T: opened by T, not yet closed."""
    OT = opened(T)
    return [i for i in range(N) if OT >> i & 1 and not T >> i & 1]


B = S | 1 << 3 | 1 << 4          # the intermediate set where the repair's test fails
X = S | 1 << Q                   # the child the definite move commits to


def facts() -> dict:
    OS = opened(S)
    new = {c: MASKS[c] & ~OS for c in range(N) if not S >> c & 1}
    close_set = [d for d in new if new[d] & ~new[Q] == 0]
    first_moves = [c for c in new if ((OS | MASKS[c]) & ~S).bit_count() <= K and solvable(S | 1 << c)]
    f = dict(open_stacks=border(S),
             q_new=[i for i in range(N) if new[Q] >> i & 1],
             close=close_set, first_moves=first_moves,
             solvable_S=solvable(S), solvable_Sq=solvable(S | 1 << Q),
             border_B=border(B), border_X=border(X | 1 << 3 | 1 << 4))
    assert len(f["q_new"]) == 3 and len(close_set) == 3, f      # open = close = 3
    assert f["solvable_S"] and not f["solvable_Sq"], f           # the theorem's conclusion fails
    assert len(f["border_B"]) == 2 < 3 == len(f["border_X"]), f  # b(B) = 2 < 3 = b(X): the repair refuses
    return f


# A fixed, hand-tuned layout: S and its stacks on the left, q and its new
# stacks in the middle, the rest on the right.
POS = {2: (0.0, 0.0), 1: (-0.9, 1.0), 3: (0.9, 0.9), 4: (0.9, -0.9),
       0: (2.2, 0.0), 7: (3.4, 1.0), 11: (3.4, -1.0),
       5: (1.4, -2.3), 6: (0.0, 2.4), 8: (4.6, 0.0), 9: (4.4, -2.0),
       10: (5.8, 0.4), 12: (3.0, -3.0), 13: (4.2, 2.8)}
CLOSED, OPEN, MOVE, NEW, OTHER = "#444444", "#1f77b4", "#d62728", "#ff9896", "#e6e6e6"
FONT = 7.5                       # every text in the figure; it is drawn at its printed width


def _panel(ax, G, colour: dict, thick: set, red_edges: list, label: str, note: str) -> None:
    import networkx as nx
    nx.draw_networkx_edges(G, POS, edgelist=[e for e in G.edges if e not in red_edges],
                           edge_color="0.72", width=0.7, ax=ax)
    nx.draw_networkx_edges(G, POS, edgelist=red_edges, edge_color=MOVE, width=1.5, ax=ax)
    nx.draw_networkx_nodes(G, POS, node_color=[colour[v] for v in G], node_size=190,
                           edgecolors="k", linewidths=[2.0 if v in thick else 0.6 for v in G], ax=ax)
    dark = {v for v in G if colour[v] in (CLOSED, MOVE, OPEN)}
    for v in G:
        ax.text(*POS[v], str(v), ha="center", va="center", fontsize=FONT, fontweight="bold",
                color="white" if v in dark else "black")
    ax.text(-1.2, 3.25, label, ha="left", va="bottom", fontsize=FONT, fontweight="bold")
    ax.text(2.45, -3.75, note, ha="center", va="top", fontsize=FONT, linespacing=1.25)
    ax.set_xlim(-1.3, 6.2)
    ax.set_ylim(-4.7, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")


def draw() -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx
    from matplotlib.lines import Line2D

    plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42})
    f = facts()
    G = nx.Graph()
    G.add_nodes_from(range(N))
    G.add_edges_from((i, j) for i in range(N) for j in range(i + 1, N) if MASKS[i] >> j & 1)
    fmt = lambda xs: ", ".join(map(str, xs))

    # (a) the state where the rule fires.
    col_a = {}
    for v in range(N):
        col_a[v] = (CLOSED if S >> v & 1 else MOVE if v == Q else NEW if v in f["q_new"]
                    else OPEN if v in f["open_stacks"] else OTHER)
    # (b) the intermediate set B = S + {3, 4} that the repair checks.
    col_b = {}
    for v in range(N):
        col_b[v] = (CLOSED if B >> v & 1 else OPEN if v in f["border_B"]
                    else NEW if v in f["border_X"] else OTHER)

    fig, axs = plt.subplots(1, 2, figsize=(6.5, 3.35))
    _panel(axs[0], G, col_a, {3, 4}, [(u, v) for u, v in G.edges if Q in (u, v)],
           "(a) S = {2}: the definite move keeps 0",
           f"closing 0 opens {fmt(f['q_new'])} and closes {fmt(f['close'])}:\n"
           f"open = close = 3; 3 and 4 need only stack 0")
    _panel(axs[1], G, col_b, set(), [],
           "(b) B = {2, 3, 4}: closing 3 and 4 first",
           f"b(B) = 2 (open {fmt(f['border_B'])}) < 3 = b(X) (open {fmt(f['border_X'])}),\n"
           f"X = {{0, 2, 3, 4}}: the repaired rule does not fire")
    handles = [Line2D([], [], marker="o", ls="", ms=7, mfc=c, mec="k", mew=0.6, label=l) for c, l in [
        (CLOSED, "closed"),
        (OPEN, "open stack"),
        (MOVE, "customer 0, the move kept"),
        (NEW, "(a) new stacks of 0; (b) open at X only"),
        (OTHER, "other customers")]]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=FONT, frameon=False,
               handletextpad=0.3, columnspacing=1.2, bbox_to_anchor=(0.5, 0.0))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.13, wspace=0.04)
    OUT.mkdir(exist_ok=True)
    outs = [OUT / "definite_counterexample.png", OUT / "definite_counterexample.pdf"]
    for p in outs:
        fig.savefig(p, dpi=200)
    return outs


if __name__ == "__main__":
    for p in draw():
        print(p)
