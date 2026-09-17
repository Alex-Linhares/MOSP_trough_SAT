"""Upper bound heuristics for MOSP, selectable by name.

The solver needs a good initial solution: it bounds the search from above, and
under the descending-ratchet strategy (`benchmarks/ratchet.py`) it is also the
point the descent starts from, so every unit of slack is an extra satisfiable
call. No single heuristic is best everywhere, and comparing them fairly requires
running the same instances through each, so they are registered here behind one
signature rather than wired into the solver individually.

Every strategy takes a `MOSPInstance` and returns `(value, ordering)`, where
`ordering` is a permutation of the patterns and `value` is the number of open
stacks it achieves, as counted by `mosp.verify.max_open_stacks`.

Available strategies:

- `tabu` — swap-move tabu search over raw permutations. Generic: it knows
  nothing about MOSP structure.
- `mcn` — least cost node (Becceneri 1999; Becceneri, Yanasse & Soma 2004).
  Works on the MOSP graph, repeatedly closing the customer that is cheapest to
  close. Yanasse & Senne (2010) describe its solution quality as "the best or
  among the best of the literature".
- `mcn+tabu` — MCN to construct, tabu to improve. The default.

Measured on the SP instances, our tabu search returns 22/42/63 against optima of
19/34/53, while Frinhani et al. (2018) report HBF2r reaching 19/35/53 in under a
second. That gap is algorithmic, not a matter of speed, which is why MCN exists
here.
"""

from __future__ import annotations

from typing import Callable, Optional

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks

UpperBound = tuple[int, list[int]]
Strategy = Callable[..., UpperBound]


def least_cost_node(instance: MOSPInstance, **_: object) -> UpperBound:
    """Minimal cost node: repeatedly close the cheapest customer to close.

    Yanasse & Senne (2010) state the rule as choosing "the next arcs of the MOSP
    graph to be traversed ... by closing the node with the least number of arcs
    incident to it". Closing a customer means cutting every pattern it still
    needs, which traverses all its incident arcs; the cost of doing so is its
    degree among the customers still open, and its neighbours become open as a
    side effect. So the construction is a minimum-degree elimination ordering on
    the MOSP graph.

    Three readings of this were implemented and measured on SP2/SP3/SP4 (optima
    19/34/53), because the rule is only ever stated in one sentence:

        selecting on missing patterns rather than degree   31/51/64
        this version, minimum degree among the open        26/49/74
        Poliquit (2008) §3 verbatim, growing a connected
          open region from the frontier                    30/57/80

    The third is the published algorithm written out in full, and it scores
    worst here, because that statement is explicitly "for an MOSP with at most
    two piece types a pattern" -- patterns are arcs there, whereas a pattern with
    k piece types is a clique of size k in general, so traversing "the arcs
    incident to a node" is not the same operation. Adapting it properly needs
    Becceneri, Yanasse & Soma (2004), which we do not have.

    None of the three reproduces the published MCNh, which Frinhani et al. report
    at 23/37/57. This version is kept because it seeds tabu best (`mcn+tabu`
    reaches 21/39/62, against 22/42/63 for tabu alone), not because it is a
    faithful MCNh.
    """
    n_customers = instance.n_customers
    n_patterns = instance.n_patterns
    if n_patterns == 0:
        return 0, []

    customer_patterns = [set(instance.customer_patterns(c)) for c in range(n_customers)]
    remaining = {c for c in range(n_customers) if customer_patterns[c]}

    neighbours: list[set[int]] = [set() for _ in range(n_customers)]
    for pattern in range(n_patterns):
        holders = set(instance.pattern_customers(pattern))
        for customer in holders:
            neighbours[customer] |= holders
    for customer in range(n_customers):
        neighbours[customer].discard(customer)

    produced: list[int] = []
    produced_set: set[int] = set()

    while remaining:
        closing = min(
            remaining,
            key=lambda c: (len(neighbours[c] & remaining),
                           len(customer_patterns[c] - produced_set),
                           c),
        )
        for pattern in sorted(customer_patterns[closing] - produced_set):
            produced.append(pattern)
            produced_set.add(pattern)
        remaining.remove(closing)

    for pattern in range(n_patterns):
        if pattern not in produced_set:
            produced.append(pattern)

    return max_open_stacks(instance, produced), produced


def tabu(instance: MOSPInstance, seed: int = 42, **_: object) -> UpperBound:
    """Random restarts improved by swap-move tabu search."""
    from satisfiability.mosp_solver import _tabu_search, _random_restarts

    value, ordering = _random_restarts(instance, seed=seed)
    return _tabu_search(instance, ordering, value, seed=seed)


def mcn_then_tabu(instance: MOSPInstance, seed: int = 42, **_: object) -> UpperBound:
    """Construct with MCN, then improve with tabu, keeping the better start.

    MCN usually starts far below a random permutation, so tabu spends its
    iterations refining a good solution instead of escaping a bad one. The
    random restarts still run, because on some instances they win, and taking
    the better of the two costs one extra evaluation.
    """
    from satisfiability.mosp_solver import _tabu_search, _random_restarts

    mcn_value, mcn_ordering = least_cost_node(instance)
    rand_value, rand_ordering = _random_restarts(instance, seed=seed)

    if mcn_value <= rand_value:
        start_value, start_ordering = mcn_value, mcn_ordering
    else:
        start_value, start_ordering = rand_value, rand_ordering

    return _tabu_search(instance, start_ordering, start_value, seed=seed)


STRATEGIES: dict[str, Strategy] = {
    "tabu": tabu,
    "mcn": least_cost_node,
    "mcn+tabu": mcn_then_tabu,
}

DEFAULT_STRATEGY = "mcn+tabu"


def upper_bound(
    instance: MOSPInstance,
    strategy: Optional[str] = None,
    **kwargs: object,
) -> UpperBound:
    """Compute an upper bound using the named strategy.

    Raises:
        KeyError: if `strategy` is not registered, naming what is available.
    """
    name = strategy or DEFAULT_STRATEGY
    if name not in STRATEGIES:
        raise KeyError(
            f"unknown upper bound strategy {name!r}; "
            f"available: {', '.join(sorted(STRATEGIES))}"
        )
    return STRATEGIES[name](instance, **kwargs)
