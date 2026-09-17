"""Draw a MOSP solution as a packed gate matrix layout.

Linhares & Yanasse (2002) show MOSP is the gate matrix layout problem, and the
picture that makes it obvious is the *fill-in* matrix: permute the columns by the
production sequence, then in every row fill the zeros lying between its first and
last 1. Each filled run is one customer's stack, from the step it opens to the
step it closes, so the number of filled cells in a column is exactly the number
of stacks open at that step, and the tallest column is the MOSP value.

Rows cycle through a small palette — five or ten colours — because the thing a
reader wants to do with this picture is count open stacks in a column by eye, and
a repeating cycle makes that countable in a way that fifty distinct colours or one
flat colour does not.

Usage:
    from mosp.visualize import plot_solution
    fig = plot_solution(instance, ordering)
    fig.savefig("sp2.png", dpi=150)

    # or from the command line, for any cached solution
    python -m mosp.visualize SP2 --out sp2.png
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from mosp.instance import MOSPInstance

# Cycling palettes. Ten is the default; five suits dense instances where ten
# colours start to look like noise.
PALETTE_10 = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
    "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD",
]
PALETTE_5 = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"]


def packed_matrix(
    instance: MOSPInstance, ordering: Sequence[int]
) -> np.ndarray:
    """Return the fill-in matrix for `ordering`: 1 where a stack is open.

    Columns follow the production sequence. Row `c` is 1 at every step from the
    first pattern of customer `c` to its last, inclusive — the span over which
    its stack is open.
    """
    order = list(ordering)
    position = {pattern: index for index, pattern in enumerate(order)}
    packed = np.zeros((instance.n_customers, len(order)), dtype=np.int8)

    for customer in range(instance.n_customers):
        steps = [position[p] for p in instance.customer_patterns(customer)
                 if p in position]
        if not steps:
            continue
        packed[customer, min(steps):max(steps) + 1] = 1
    return packed


def open_counts(packed: np.ndarray) -> np.ndarray:
    """Open stacks at each step: the column sums of the fill-in matrix."""
    return packed.sum(axis=0)


def plot_solution(
    instance: MOSPInstance,
    ordering: Sequence[int],
    n_colors: int = 10,
    sort_rows: bool = True,
    title: Optional[str] = None,
    show_counts: bool = True,
):
    """Draw the packed gate matrix for a solution.

    Args:
        instance: the MOSP instance.
        ordering: production sequence, a permutation of the patterns.
        n_colors: 10 or 5; rows cycle through the palette so that open stacks in
            a column can be counted by eye.
        sort_rows: order rows by the step at which they open. This is the
            staircase form the gate-matrix literature draws, and it makes the
            structure legible; the open-stack counts are unaffected, since
            reordering rows cannot change a column sum.
        title: overrides the default caption.
        show_counts: draw the per-step open-stack profile beneath the matrix.

    Returns:
        A matplotlib Figure.
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import to_rgba

    palette = PALETTE_5 if n_colors == 5 else PALETTE_10

    packed = packed_matrix(instance, ordering)
    counts = open_counts(packed)
    peak = int(counts.max()) if counts.size else 0

    rows = list(range(packed.shape[0]))
    if sort_rows:
        def opens_at(row: int) -> tuple[int, int]:
            nonzero = np.flatnonzero(packed[row])
            if nonzero.size == 0:
                return (packed.shape[1] + 1, 0)
            return (int(nonzero[0]), int(nonzero[-1]))
        rows.sort(key=opens_at)

    n_rows, n_cols = packed.shape
    height = max(2.5, min(14.0, 0.16 * n_rows + 1.6))
    width = max(4.0, min(18.0, 0.16 * n_cols + 2.0))

    if show_counts:
        fig, (ax, ax_counts) = plt.subplots(
            2, 1, figsize=(width, height + 1.4), sharex=True,
            gridspec_kw={"height_ratios": [4, 1], "hspace": 0.08},
            layout="constrained",
        )
    else:
        fig, ax = plt.subplots(figsize=(width, height), layout="constrained")
        ax_counts = None

    # Each stack is drawn as a bar spanning the steps it is open, with a gap
    # between rows. Drawn as contiguous cells the bars merge into blocks and the
    # thing this picture exists for — counting stacks down a column — stops
    # working; the gap keeps every row individually countable.
    bar_height = 0.74
    for drawn_index, row in enumerate(rows):
        nonzero = np.flatnonzero(packed[row])
        if nonzero.size == 0:
            continue
        colour = palette[drawn_index % len(palette)]
        start, stop = int(nonzero[0]), int(nonzero[-1])
        ax.broken_barh(
            [(start - 0.5, stop - start + 1)],
            (drawn_index - bar_height / 2, bar_height),
            facecolors=to_rgba(colour), edgecolors="none",
        )

    ax.set_xlim(-0.5, n_cols - 0.5)
    ax.set_ylim(n_rows - 0.5, -0.5)
    ax.set_ylabel(f"customers (n={n_rows})")
    ax.set_yticks([])

    # Shade the steps that attain the peak rather than ruling lines through the
    # bars: on instances where the peak is held for many steps, the lines become
    # the loudest thing in the figure and obscure what they point at.
    peak_steps = np.flatnonzero(counts == peak) if peak else np.array([], dtype=int)
    for step in peak_steps:
        ax.axvspan(step - 0.5, step + 0.5, color="#000000", alpha=0.07,
                   zorder=0, lw=0)

    if title is None:
        title = (f"{instance.name or 'instance'} — {n_rows}x{n_cols}, "
                 f"max open stacks = {peak}")
    ax.set_title(title, fontsize=11)

    if ax_counts is not None:
        ax_counts.fill_between(range(n_cols), counts, step="mid",
                               color="#4C72B0", alpha=0.35)
        ax_counts.step(range(n_cols), counts, where="mid",
                       color="#2A4E7C", lw=1.0)
        ax_counts.axhline(peak, color="#C44E52", lw=1.0, ls="--",
                          label=f"peak = {peak}")
        ax_counts.set_ylabel("open")
        ax_counts.set_xlabel("production step")
        ax_counts.set_ylim(0, max(1, peak * 1.15))
        ax_counts.legend(loc="upper right", fontsize=8, frameon=False)
    else:
        ax.set_xlabel("production step")

    return fig


def load_cached_solution(
    name: str,
    solutions_dir: Path = Path("solutions"),
    instance_dir: Path = Path("benchmarks/instances"),
) -> tuple[MOSPInstance, list[int]]:
    """Find a cached solution by instance name and pair it with its instance."""
    import json

    from benchmarks.solve_parallel import find_benchmark_files

    candidates = sorted(solutions_dir.glob("*.json"))
    payload = None
    for path in candidates:
        data = json.loads(path.read_text())
        if data["instance_name"] == name or path.stem == name:
            payload = data
            break
    if payload is None:
        raise SystemExit(f"no cached solution named {name!r} in {solutions_dir}")

    for filepath in find_benchmark_files(instance_dir):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for inst in instances:
            if inst.name == payload["instance_name"]:
                return inst, payload["ordering"]

    raise SystemExit(f"cached solution {name!r} found, but its instance was not")


def main() -> None:
    import argparse

    import matplotlib
    matplotlib.use("Agg")

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("name", help="instance name, e.g. SP2")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--colors", type=int, default=10, choices=[5, 10])
    parser.add_argument("--no-sort", action="store_true",
                        help="keep original customer order instead of the staircase")
    parser.add_argument("--no-counts", action="store_true")
    parser.add_argument("--dpi", type=int, default=150)
    args = parser.parse_args()

    instance, ordering = load_cached_solution(args.name)
    figure = plot_solution(
        instance, ordering,
        n_colors=args.colors,
        sort_rows=not args.no_sort,
        show_counts=not args.no_counts,
    )
    out = args.out or Path(f"{args.name}.png")
    figure.savefig(out, dpi=args.dpi, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
