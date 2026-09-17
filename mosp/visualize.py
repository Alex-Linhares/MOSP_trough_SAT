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


def pack_into_tracks(
    spans: Sequence[tuple[int, int]]
) -> list[int]:
    """Assign each span a track so that overlapping spans never share one.

    This is interval partitioning: sort by opening step and give each span the
    first track whose previous occupant has already closed. The greedy is
    optimal, and the number of tracks it uses equals the maximum number of
    spans open at once — which is the MOSP value. That is Proposition 2 of
    Linhares & Yanasse (2002): open stacks equal tracks.

    Args:
        spans: (first_step, last_step) per net, inclusive.

    Returns:
        A track index per span, in the order given.
    """
    import heapq

    order = sorted(range(len(spans)), key=lambda i: (spans[i][0], spans[i][1]))
    track_of = [0] * len(spans)
    free: list[tuple[int, int]] = []  # (last_step_used, track_index)
    n_tracks = 0

    for index in order:
        start, stop = spans[index]
        if free and free[0][0] < start:
            _, track = heapq.heappop(free)
        else:
            track = n_tracks
            n_tracks += 1
        track_of[index] = track
        heapq.heappush(free, (stop, track))
    return track_of


def plot_gate_matrix(
    instance: MOSPInstance,
    ordering: Sequence[int],
    n_colors: int = 10,
    show_gate_labels: bool = True,
    show_column_sums: bool = True,
    title: Optional[str] = None,
):
    """Draw the solution as a packed gate matrix layout, after Fig. 2(c) of
    Linhares & Yanasse (2002).

    Gates are vertical wires, one per pattern, ordered by the production
    sequence. Nets are horizontal wires, one per customer, running from the
    first gate it needs to the last; a dot marks each gate the net actually
    connects to, so the original matrix entries stay visible inside the span.
    Nets are packed into tracks, so non-overlapping customers share a physical
    row.

    The packing is what makes the figure answer the question it is drawn for:
    the number of tracks *is* the number of open stacks, so the reader counts
    rows rather than inspecting columns. Tracks cycle through a small palette to
    make that count easy.

    Returns:
        A matplotlib Figure.
    """
    import matplotlib.pyplot as plt

    palette = PALETTE_5 if n_colors == 5 else PALETTE_10
    order = list(ordering)
    position = {pattern: index for index, pattern in enumerate(order)}
    n_gates = len(order)

    nets: list[tuple[int, int, list[int]]] = []
    for customer in range(instance.n_customers):
        steps = sorted(position[p] for p in instance.customer_patterns(customer)
                       if p in position)
        if steps:
            nets.append((steps[0], steps[-1], steps))

    spans = [(start, stop) for start, stop, _ in nets]
    tracks = pack_into_tracks(spans) if spans else []
    n_tracks = (max(tracks) + 1) if tracks else 0

    counts = open_counts(packed_matrix(instance, order))
    peak = int(counts.max()) if counts.size else 0

    width = max(5.0, min(22.0, 0.22 * n_gates + 2.0))
    height = max(2.2, min(13.0, 0.30 * n_tracks + 2.0))
    fig, ax = plt.subplots(figsize=(width, height), layout="constrained")

    # Gates: vertical wires spanning every track.
    for gate in range(n_gates):
        ax.plot([gate, gate], [-0.6, n_tracks - 0.4], color="#B0B0B0",
                lw=0.7, zorder=1)

    # Nets: one horizontal wire per customer, on its assigned track, with a dot
    # at each gate it connects to.
    for (start, stop, steps), track in zip(nets, tracks):
        colour = palette[track % len(palette)]
        ax.plot([start, stop], [track, track], color=colour, lw=2.6,
                solid_capstyle="round", zorder=2)
        ax.plot(steps, [track] * len(steps), "o", color=colour,
                markersize=4.2, markeredgecolor="white", markeredgewidth=0.5,
                zorder=3)

    ax.set_ylim(n_tracks - 0.4, -0.9)
    ax.set_xlim(-0.8, n_gates - 0.2)
    ax.set_ylabel(f"tracks ({n_tracks})")
    ax.set_yticks(range(n_tracks))
    ax.set_yticklabels([str(t + 1) for t in range(n_tracks)], fontsize=7)

    # Linhares & Yanasse put gate numbers above the circuit and the per-gate
    # totals below. Keeping that split matters here because both are per-gate
    # numbers: printed on the same edge they interleave and neither can be read.
    label_size = 6 if n_gates > 30 else 7

    if show_column_sums and n_gates <= 80:
        ax.set_xticks(range(n_gates))
        ax.set_xticklabels([str(int(counts[g])) for g in range(n_gates)],
                           fontsize=label_size, color="#444444")
        ax.set_xlabel("open stacks at each gate (maximum = track count)")
    else:
        ax.set_xticks([])
        ax.set_xlabel("gates, in production order")

    if show_gate_labels and n_gates <= 80:
        top = ax.secondary_xaxis("top")
        top.set_xticks(range(n_gates))
        top.set_xticklabels([str(order[i]) for i in range(n_gates)],
                            fontsize=label_size)
        top.set_xlabel("gates, in production order (pattern index)", fontsize=9)
        top.tick_params(length=2)

    if title is None:
        title = (f"{instance.name or 'instance'} — packed gate matrix layout, "
                 f"{n_tracks} tracks = {peak} open stacks")
    ax.set_title(title, fontsize=11, pad=26)
    for spine in ("right", "left"):
        ax.spines[spine].set_visible(False)
    return fig


def plot_comparison(
    entries: Sequence[tuple[MOSPInstance, Sequence[int]]],
    n_colors: int = 10,
    sort_rows: bool = True,
    labels: Optional[Sequence[str]] = None,
    suptitle: Optional[str] = None,
):
    """Draw several solutions side by side on a shared vertical scale.

    Comparing instances is only meaningful if the panels are commensurate, so
    every panel is drawn with the same number of customer rows on the y axis.
    Without that, a sparse instance and a dense one of the same size look alike,
    because each fills its own axes.

    Args:
        entries: (instance, ordering) pairs, left to right.
        labels: captions; defaults to the instance names.

    Returns:
        A matplotlib Figure.
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import to_rgba

    palette = PALETTE_5 if n_colors == 5 else PALETTE_10
    n_panels = len(entries)
    max_rows = max(inst.n_customers for inst, _ in entries)

    fig, axes = plt.subplots(
        1, n_panels, figsize=(5.4 * n_panels, 5.6), layout="constrained",
    )
    if n_panels == 1:
        axes = [axes]

    for axis, (instance, ordering), index in zip(axes, entries, range(n_panels)):
        packed = packed_matrix(instance, ordering)
        counts = open_counts(packed)
        peak = int(counts.max()) if counts.size else 0

        rows = list(range(packed.shape[0]))
        if sort_rows:
            def opens_at(row: int, pk=packed) -> tuple[int, int]:
                nonzero = np.flatnonzero(pk[row])
                if nonzero.size == 0:
                    return (pk.shape[1] + 1, 0)
                return (int(nonzero[0]), int(nonzero[-1]))
            rows.sort(key=opens_at)

        n_cols = packed.shape[1]
        for drawn_index, row in enumerate(rows):
            nonzero = np.flatnonzero(packed[row])
            if nonzero.size == 0:
                continue
            start, stop = int(nonzero[0]), int(nonzero[-1])
            axis.broken_barh(
                [(start - 0.5, stop - start + 1)],
                (drawn_index - 0.37, 0.74),
                facecolors=to_rgba(palette[drawn_index % len(palette)]),
                edgecolors="none",
            )

        for step in np.flatnonzero(counts == peak) if peak else []:
            axis.axvspan(step - 0.5, step + 0.5, color="#000000", alpha=0.07,
                         zorder=0, lw=0)

        # The peak as a horizontal rule: its height against the panel is the
        # fraction of customers open at once, which is the quantity being
        # compared across panels.
        axis.axhline(peak - 0.5, color="#C44E52", lw=1.2, ls="--", zorder=4)
        axis.text(n_cols * 0.99, peak - 1.2, f"peak {peak}", ha="right",
                  va="bottom", fontsize=9, color="#C44E52", zorder=5,
                  bbox=dict(facecolor="white", edgecolor="none", alpha=0.85,
                            pad=1.5))

        # Two densities, because the literature quotes the second. Frinhani et
        # al. (2018) tabulate D for GP1 as 0.98 where its matrix is 0.81 full:
        # their D is the edge density of the MOSP graph, not the fill rate of M.
        fill = float(instance.matrix.sum()) / (instance.n_customers
                                               * instance.n_patterns)
        neighbours: list[set[int]] = [set() for _ in range(instance.n_customers)]
        for pattern in range(instance.n_patterns):
            holders = set(instance.pattern_customers(pattern))
            for customer in holders:
                neighbours[customer] |= holders
        for customer in range(instance.n_customers):
            neighbours[customer].discard(customer)
        edges = sum(len(adj) for adj in neighbours) / 2
        possible = instance.n_customers * (instance.n_customers - 1) / 2
        graph_density = edges / possible if possible else 0.0

        caption = labels[index] if labels else (instance.name or "instance")
        axis.set_title(
            f"{caption}\n{instance.n_customers}x{instance.n_patterns}, "
            f"matrix {fill:.2f} / graph {graph_density:.2f}, optimum {peak}",
            fontsize=10,
        )
        axis.set_xlim(-0.5, n_cols - 0.5)
        axis.set_ylim(max_rows - 0.5, -0.5)
        axis.set_yticks([])
        axis.set_xlabel("production step")
    axes[0].set_ylabel(f"customers (shared scale, {max_rows} rows)")

    if suptitle:
        fig.suptitle(suptitle, fontsize=12)
    return fig


def load_cached_solution(
    name: str,
    solutions_dir: Path = Path("solutions"),
    instance_dir: Path = Path("benchmarks/instances"),
) -> tuple[MOSPInstance, list[int]]:
    """Find a cached solution by instance name and pair it with its instance."""
    import json

    from benchmarks.solve_parallel import find_benchmark_files

    payloads = {}
    for path in sorted(solutions_dir.glob("*.json")):
        data = json.loads(path.read_text())
        payloads[data["instance_name"]] = data

    if not payloads:
        raise SystemExit(f"no cached solutions in {solutions_dir}")

    # Exact name first, then prefix. The prefix fallback matters because some
    # solutions are stored under a bare name such as "GP4" while the benchmark
    # files name the same instance descriptively ("GP4:  50 customers, ..."),
    # and a handful of bare-named files correspond to no enumerated instance at
    # all, being leftovers from an earlier script. Matching only on the exact
    # name finds those orphans and then fails to find their instance.
    for filepath in find_benchmark_files(instance_dir):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for inst in instances:
            if inst.name in payloads and (
                inst.name == name or inst.name.strip().startswith(name)
            ):
                return inst, payloads[inst.name]["ordering"]

    raise SystemExit(
        f"no cached solution for an instance named or starting with {name!r}"
    )


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
