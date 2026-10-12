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
from pathwidth.minor import MinorConfig, MinorLadder
from pathwidth.search import decide

PROOFS = ("refutation", "minor", "bound")      # a proved width; "" is unproved


@dataclass
class Solution:
    """What a descent established, and how -- which is not the same question.

    `proof` is "refutation" when the search exhausted `width - 1`, "bound" when
    `width` met a lower bound that needed no refutation, "minor" when
    `width - 1` was refuted on a contracted minor (`pathwidth/minor.py`), and
    "" when the descent ran out of budget. The last is still an upper bound worth keeping
    but is not an optimality claim. For a disconnected graph the proof is that
    of the widest component, provided every component was proved.

    `order` is a closing order over the graph's own labels; `width` is its
    vertex separation, checked, not trusted.

    `minor` is set when a minor raised the lower bound: the certificate of the
    highest width refuted on a minor (`MinorCertificate.as_dict()`, its
    contraction sequence in mask indices for `solve_masks` and in the graph's
    labels for `solve`), with `minor_nodes` and `minor_seconds` the cost of
    the whole step, successful or not. `lower` includes what the minors proved.
    """

    width: int
    order: list
    proof: str
    nodes: int
    seconds: float
    lower: int
    upper_start: int
    components: list["Solution"] = field(default_factory=list)
    minor: dict | None = None
    minor_nodes: int = 0
    minor_seconds: float = 0.0

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
                minor: "bool | MinorConfig" = True,
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
        minor: the contraction-minor step (`pathwidth/minor.py`): before each
            refutation of `w` on the graph, try to refute `w` on contracted
            minors under a node budget. True (default; the owner's decision
            of 2026-10-12) uses `MinorConfig()`, a `MinorConfig` sets the
            budgets, False switches it off -- for measurements and tests
            only. Below 40 vertices, and at any width a 100,000-node probe
            of the full graph settles, it costs nothing. Its nodes
            are counted in `nodes` and separately in `minor_nodes`.
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

    ladder = None
    if minor:
        ladder = MinorLadder(masks, minor if isinstance(minor, MinorConfig) else MinorConfig())
    certificate = None
    lower_proof = "bound"

    def finish(proof: str) -> Solution:
        sol = Solution(width, order, proof, nodes, time.monotonic() - started, lower, upper_start)
        if ladder is not None:
            sol.minor_nodes, sol.minor_seconds = ladder.nodes, ladder.seconds
            sol.minor = certificate.as_dict() if certificate is not None else None
        return sol

    w = width - 1
    while w >= lower:
        deadline = None if time_budget is None else started + time_budget
        probe = None
        if ladder is not None and ladder.config.probe_nodes and ladder.applies:
            # a cheap look at the full graph first: most graphs settle here and
            # never pay for the minors
            probe = decide(masks, w + 1, max_nodes=min(ladder.config.probe_nodes, max_nodes or 1 << 62),
                           deadline=deadline, **flags)
            nodes += probe.nodes
            if probe.status == "unknown":
                probe = None
        if ladder is not None and probe is None and ladder.applies:
            before = ladder.nodes
            cutoff = (None if time_budget is None
                      else started + ladder.config.time_fraction * time_budget)
            found = ladder.try_refute(w, deadline=cutoff, max_nodes=max_nodes, order=order, **flags)
            if found is not None:
                # pw >= w + 1 = width: the width is proved by the minor.
                certificate, lower, lower_proof = found, w + 1, "minor"
                nodes += ladder.nodes - before
                break
            raised = ladder.raise_lower(lower, deadline=cutoff, max_nodes=max_nodes, **flags)
            if raised is not None and raised.refuted + 1 > lower:
                # a minor's exact pathwidth p: pw >= p, below the width
                certificate, lower, lower_proof = raised, raised.refuted + 1, "minor"
            nodes += ladder.nodes - before
            if w < lower:
                break                          # a minor's exact pathwidth reached the width
        if probe is not None:
            answer = probe
        else:
            answer = decide(masks, w + 1, max_nodes=max_nodes, deadline=deadline, **flags)
            nodes += answer.nodes
        if answer.status == "unsat":
            return finish("refutation" if width == w + 1 else "")
        if answer.status == "unknown":
            return finish("")
        achieved = vertex_separation_masks(masks, answer.order)
        if achieved < width:
            width, order = achieved, answer.order
            if on_improve is not None:
                on_improve(width, order)
        w = min(w, achieved) - 1

    return finish(lower_proof if width <= lower else "")


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
        if sol.minor is not None:
            sol.minor["contractions"] = [[labels[v], labels[u] if u >= 0 else None]
                                         for v, u in sol.minor["contractions"]]
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
    proof = next(p for p in PROOFS if any(s.proof == p for s in widest)) if all_proved else ""
    if on_improve is not None:
        on_improve(width, order)
    certified = next((s.minor for s in widest if s.proof == "minor"), None)
    return Solution(width, order, proof, sum(s.nodes for s in solved), time.monotonic() - started,
                    max(s.lower for s in solved), max(s.upper_start for s in solved), solved,
                    minor=certified, minor_nodes=sum(s.minor_nodes for s in solved),
                    minor_seconds=sum(s.minor_seconds for s in solved))
