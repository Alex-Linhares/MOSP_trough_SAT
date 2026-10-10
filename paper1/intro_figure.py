"""Figure 1.1 of the pathwidth complex paper: one small instance read three ways.

The example of `paper1/review_readability.md` §7.3, as the owner's notes of
2026-10-06 ask: six customers a-f and four patterns,

    P1 = {a, b}, P2 = {b, c, d}, P3 = {c, d, e}, P4 = {e, f}.

Order A = P1 P2 P3 P4 keeps at most 3 stacks open, order B = P1 P3 P4 P2 keeps
5; over all 24 orders, 2 reach 3, 16 give 4 and 6 give 5. The panels are
(a) the matrix with its open stacks under both orders, (b) and (c) the gate
matrix layouts of the two orders packed into 3 and 5 tracks by the left-edge
algorithm, and (d) the MOSP graph with the bags of order A, a path
decomposition of width 2.

Every number the figure prints is recomputed here from PATTERNS, and
tests/test_intro_figure.py checks them.

    python -m paper1.intro_figure
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations, permutations
from pathlib import Path

CUSTOMERS = "abcdef"
PATTERNS = {"P1": "ab", "P2": "bcd", "P3": "cde", "P4": "ef"}
ORDER_A = ("P1", "P2", "P3", "P4")
ORDER_B = ("P1", "P3", "P4", "P2")
FIGS = Path(__file__).resolve().parent / "figures"


def open_sets(order) -> list[set[str]]:
    """The customers with an open stack while each pattern of `order` is cut."""
    pos = {c: [i for i, p in enumerate(order) if c in PATTERNS[p]] for c in CUSTOMERS}
    return [{c for c in CUSTOMERS if min(pos[c]) <= i <= max(pos[c])} for i in range(len(order))]


def profile(order) -> list[int]:
    return [len(s) for s in open_sets(order)]


def peak_counts() -> Counter:
    """How many of the 24 orders reach each maximum number of open stacks."""
    return Counter(max(profile(o)) for o in permutations(PATTERNS))


def spans(order) -> dict[str, tuple[int, int]]:
    """Each net's interval of gate positions in `order`."""
    pos = {c: [i for i, p in enumerate(order) if c in PATTERNS[p]] for c in CUSTOMERS}
    return {c: (min(pos[c]), max(pos[c])) for c in CUSTOMERS}


def left_edge(order) -> dict[str, int]:
    """Track of each net by the left-edge algorithm: nets by left end, first track free."""
    sp, last, track = spans(order), [], {}
    for c in sorted(CUSTOMERS, key=lambda c: (sp[c][0], c)):
        t = next((t for t, end in enumerate(last) if end < sp[c][0]), len(last))
        if t == len(last):
            last.append(-1)
        last[t], track[c] = sp[c][1], t
    return track


def edges() -> set[frozenset[str]]:
    """The MOSP graph: customers joined when some pattern holds both."""
    return {frozenset(e) for p in PATTERNS.values() for e in combinations(p, 2)}


def vertex_separation() -> int:
    """vs(G) = pw(G), by brute force over the 720 layouts."""
    E = edges()
    best = len(CUSTOMERS)
    for L in permutations(CUSTOMERS):
        width = 0
        for i in range(1, len(L)):
            left, right = set(L[:i]), set(L[i:])
            width = max(width, sum(any(frozenset((u, v)) in E for v in right) for u in left))
        best = min(best, width)
    return best


def is_path_decomposition(bags) -> bool:
    E = edges()
    covers = set().union(*bags) == set(CUSTOMERS)
    every_edge = all(any(e <= b for b in bags) for e in E)
    interval = all(bags[i] & bags[l] <= bags[j]
                   for i in range(len(bags)) for j in range(i, len(bags)) for l in range(j, len(bags)))
    return covers and every_edge and interval


def draw() -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.family": "DejaVu Sans"})
    INK, GREY, BLUE, RED = "0.1", "0.55", "#2c6db5", "#b2182b"

    fig, axs = plt.subplots(1, 4, figsize=(6.5, 2.35), gridspec_kw={"width_ratios": [1.05, 1, 1, 1.15]})
    for ax in axs:
        ax.set_axis_off()

    # (a) the matrix in order A, each customer's open interval as a bar
    ax = axs[0]
    nrow = len(CUSTOMERS)
    for j, p in enumerate(ORDER_A):
        ax.text(j, nrow + 0.1, p, ha="center", va="bottom", fontsize=7.5)
    sp = spans(ORDER_A)
    for r, c in enumerate(CUSTOMERS):
        y = nrow - 1 - r
        ax.text(-0.75, y, c, ha="center", va="center", fontsize=7.5)
        a, b = sp[c]
        ax.add_patch(FancyBboxPatch((a - 0.32, y - 0.3), b - a + 0.64, 0.6,
                                    boxstyle="round,pad=0,rounding_size=0.25", fc="#dbe7f5", ec="none"))
        for j, p in enumerate(ORDER_A):
            ax.text(j, y, "1" if c in PATTERNS[p] else "0", ha="center", va="center",
                    fontsize=7.5, color=INK if c in PATTERNS[p] else GREY)
    ax.text(-0.75, -1.05, "A", ha="center", va="center", fontsize=7.5, fontweight="bold", color=BLUE)
    for j, v in enumerate(profile(ORDER_A)):
        ax.text(j, -1.05, str(v), ha="center", va="center", fontsize=7.5, color=BLUE)
    ax.text(-0.75, -1.85, "B", ha="center", va="center", fontsize=7.5, fontweight="bold", color=RED)
    for j, v in enumerate(profile(ORDER_B)):
        ax.text(j, -1.85, str(v), ha="center", va="center", fontsize=7.5, color=RED)
    ax.text(1.5, -2.6, "open stacks per position", ha="center", va="center", fontsize=7, color=GREY)
    ax.set_xlim(-1.1, 3.5)
    ax.set_ylim(-3.0, nrow + 1.5)

    # (b), (c) the gate matrix layouts of A and B
    for ax, order, colour in ((axs[1], ORDER_A, BLUE), (axs[2], ORDER_B, RED)):
        sp, track = spans(order), left_edge(order)
        ntr = max(track.values()) + 1
        prof = profile(order)
        peak = prof.index(max(prof))
        top, bottom = nrow - 0.45, nrow - ntr - 0.55
        ax.add_patch(plt.Rectangle((peak - 0.28, bottom), 0.56, top - bottom, fc=colour, alpha=0.12, lw=0))
        for j, p in enumerate(order):
            ax.plot([j, j], [bottom, top], color=GREY, lw=0.8, zorder=1)
            ax.text(j, nrow + 0.1, p, ha="center", va="bottom", fontsize=7.5)
        for c in CUSTOMERS:
            a, b = sp[c]
            y = nrow - 1 - track[c]
            ax.plot([a - 0.12, b + 0.12], [y, y], color=INK, lw=1.6, solid_capstyle="round", zorder=2)
            for j, p in enumerate(order):
                if c in PATTERNS[p]:
                    ax.plot(j, y, "o", ms=3.4, color=INK, zorder=3)
            ax.text(a - 0.2, y + 0.22, c, ha="right", va="bottom", fontsize=7.5, zorder=4)
        ax.text(1.5, bottom - 0.55, f"{ntr} tracks", ha="center", va="center", fontsize=7.5,
                fontweight="bold", color=colour)
        ax.set_xlim(-0.75, 3.5)
        ax.set_ylim(-3.0, nrow + 1.5)

    # (d) the MOSP graph and the bags of order A
    ax = axs[3]
    xy = {"a": (0, 4.2), "b": (1, 4.2), "c": (2, 5.0), "d": (2, 3.4), "e": (3, 4.2), "f": (4, 4.2)}
    for e in edges():
        u, v = sorted(e)
        ax.plot([xy[u][0], xy[v][0]], [xy[u][1], xy[v][1]], color=INK, lw=1.0, zorder=1)
    for c, (x, y) in xy.items():
        ax.plot(x, y, "o", ms=10, mfc="white", mec=INK, mew=0.9, zorder=2)
        ax.text(x, y, c, ha="center", va="center", fontsize=7.5, zorder=3)
    bags = open_sets(ORDER_A)
    for i, bag in enumerate(bags):
        y = 1.6 - 1.05 * i
        ax.add_patch(FancyBboxPatch((0.9, y - 0.33), 2.2, 0.66, boxstyle="round,pad=0,rounding_size=0.3",
                                    fc="#dbe7f5" if len(bag) == max(map(len, bags)) else "white",
                                    ec=BLUE, lw=0.8))
        ax.text(2.0, y, "{" + ", ".join(sorted(bag)) + "}", ha="center", va="center", fontsize=7.5)
        if i:
            ax.plot([2.0, 2.0], [y + 0.33, y + 0.72], color=BLUE, lw=0.8)
    ax.text(2.0, -2.6, f"bags of A: width {max(map(len, bags)) - 1}", ha="center", va="center",
            fontsize=7, color=GREY)
    ax.set_xlim(-0.4, 4.4)
    ax.set_ylim(-3.0, nrow + 1.5)

    for ax, tag in zip(axs, "abcd"):
        ax.text(0.0, 1.0, f"({tag})", transform=ax.transAxes, ha="left", va="top",
                fontsize=8, fontweight="bold")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02, wspace=0.08)
    FIGS.mkdir(exist_ok=True)
    out = FIGS / "sec1_fig1_example.pdf"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(FIGS / "sec1_fig1_example.png", dpi=200, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return out


def main() -> None:
    print("order A", profile(ORDER_A), "order B", profile(ORDER_B))
    print("peaks over 24 orders", dict(sorted(peak_counts().items())))
    print("tracks", max(left_edge(ORDER_A).values()) + 1, max(left_edge(ORDER_B).values()) + 1)
    print("pathwidth", vertex_separation(), "bags of A a path decomposition:",
          is_path_decomposition(open_sets(ORDER_A)))
    print(draw())


if __name__ == "__main__":
    main()
