"""The descent: from an upper bound down to a refutation or a lower bound.

Ported from `solve()` in the MOSP reference (`src/customer_search.py`), with
the product-specific steps replaced: the witness is re-measured with
`vertex_separation_masks` instead of a product-order simulation (on a graph the
search's cost *is* the vertex separation plus one, so the two cannot
disagree), the starting bound is the greedy order plus a restricted-search
descent, and the lower bound is `bounds.lower_bound`.

Connected components are solved independently and their orders concatenated:
a boundary never crosses a component, so the width is the maximum.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Hashable, Sequence
from dataclasses import dataclass, field

import networkx as nx

from pathwidth.bounds import greedy_order, lower_bound
from pathwidth.graph import masks_from_graph, vertex_separation_masks
from pathwidth.search import decide


@dataclass
class Solution:
    """What a descent established, and how -- which is not the same question.

    `proof` is "refutation" when the search exhausted `width - 1`, "bound" when
    `width` met a lower bound that needed no refutation, and "" when the
    descent ran out of budget. The last is still an upper bound worth keeping
    but is not an optimality claim. For a disconnected graph the proof is that
    of the widest component, provided every component was proved.

    `order` is a closing order over the graph's own labels; `width` is its
    vertex separation, checked, not trusted.
    """

    width: int
    order: list
    proof: str
    nodes: int
    seconds: float
    lower: int
    upper_start: int
    components: list["Solution"] = field(default_factory=list)

    @property
    def proved(self) -> bool:
        return bool(self.proof)


def initial_upper_bound(masks: Sequence[int], *, max_nodes: int = 20_000,
                        **flags: object) -> tuple[int, list[int]]:
    """Greedy order, then improved by Chu & Stuckey's restricted search
    (`ub_MOSP`, §3.4): descend with `restrict=True` and a small node budget
    until it can find nothing better."""
    order = greedy_order(masks)
    width = vertex_separation_masks(masks, order)
    flags = {k: v for k, v in flags.items() if k not in ("restrict", "max_nodes", "deadline")}
    while width > 0:
        answer = decide(masks, width, restrict=True, max_nodes=max_nodes, **flags)  # pw <= width-1 ?
        if answer.status != "sat":
            break
        found = vertex_separation_masks(masks, answer.order)
        if found >= width:
            break
        width, order = found, answer.order
    return width, order


def solve_masks(masks: Sequence[int], *, upper: int | None = None,
                upper_order: Sequence[int] | None = None,
                lower: int | None = None, max_nodes: int | None = None,
                time_budget: float | None = None,
                on_improve: "Callable[[int, list[int]], None] | None" = None,
                **flags: object) -> Solution:
    """Descend `w` with the complete search until it refutes or runs out.

    Args:
        upper, upper_order: where to start; default the greedy + restricted
            search bound. `upper_order` must achieve `upper` if given.
        lower: a known lower bound; default `bounds.lower_bound`. Reaching it
            ends the descent with proof "bound".
        max_nodes, time_budget: per-`w` node budget and overall wall-clock
            budget. An exhausted budget stops the descent with `proved` False.
        on_improve: called with `(width, order)` at each improvement.
        flags: passed to `decide` (`native`, `better_move`, `fan_order`, ...).
    """
    started = time.monotonic()
    nodes = 0
    n = len(masks)
    active = [v for v in range(n) if masks[v]]
    if not active:
        return Solution(0 if n else -1, [], "bound", 0, 0.0, 0, 0)

    if lower is None:
        lower = lower_bound(masks)
    if upper is None:
        width, order = initial_upper_bound(masks, **flags)
    else:
        width = upper
        order = list(upper_order) if upper_order is not None else greedy_order(masks)
        if vertex_separation_masks(masks, order) > width:
            raise ValueError("upper_order does not achieve upper")
    upper_start = width

    if width <= lower:
        return Solution(width, order, "bound", 0, time.monotonic() - started, lower, upper_start)

    w = width - 1
    while w >= lower:
        deadline = None if time_budget is None else started + time_budget
        answer = decide(masks, w + 1, max_nodes=max_nodes, deadline=deadline, **flags)
        nodes += answer.nodes
        if answer.status == "unsat":
            proof = "refutation" if width == w + 1 else ""
            return Solution(width, order, proof, nodes, time.monotonic() - started, lower, upper_start)
        if answer.status == "unknown":
            return Solution(width, order, "", nodes, time.monotonic() - started, lower, upper_start)
        achieved = vertex_separation_masks(masks, answer.order)
        if achieved < width:
            width, order = achieved, answer.order
            if on_improve is not None:
                on_improve(width, order)
        w = min(w, achieved) - 1

    return Solution(width, order, "bound", nodes, time.monotonic() - started, lower, upper_start)


def solve(G: nx.Graph, *, components: bool = True, **kwargs: object) -> Solution:
    """`solve_masks` on a graph, component by component, in the graph's labels."""
    started = time.monotonic()
    if G.number_of_nodes() == 0:
        return Solution(-1, [], "bound", 0, 0.0, -1, -1)
    parts = [G.subgraph(c) for c in nx.connected_components(G)] if components else [G]
    if len(parts) == 1:
        masks, labels = masks_from_graph(G)
        sol = solve_masks(masks, **kwargs)
        sol.order = [labels[i] for i in sol.order]
        return sol

    kwargs = dict(kwargs)
    on_improve = kwargs.pop("on_improve", None)
    time_budget = kwargs.pop("time_budget", None)
    # widest components first, so the budget goes where the width is decided
    parts.sort(key=lambda H: -H.number_of_nodes())
    solved: list[Solution] = []
    order: list = []
    for H in parts:
        remaining = None if time_budget is None else max(0.0, started + time_budget - time.monotonic())
        sub = solve(H, components=False, time_budget=remaining, **kwargs)
        solved.append(sub)
        order.extend(sub.order)
    width = max(s.width for s in solved)
    widest = [s for s in solved if s.width == width]
    all_proved = all(s.proved for s in solved)
    proof = ("refutation" if any(s.proof == "refutation" for s in widest) else "bound") if all_proved else ""
    if on_improve is not None:
        on_improve(width, order)
    return Solution(width, order, proof, sum(s.nodes for s in solved), time.monotonic() - started,
                    max(s.lower for s in solved), max(s.upper_start for s in solved), solved)
