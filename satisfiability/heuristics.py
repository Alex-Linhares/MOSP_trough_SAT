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
    """Least cost node: repeatedly close whichever customer is cheapest.

    Yanasse & Senne (2010) describe the rule as choosing "the next arcs of the
    MOSP graph to be traversed ... by closing the node with the least number of
    arcs incident to it". Closing a customer traverses every arc incident to it,
    so the cost of closing is its degree among the customers still open, and the
    heuristic repeatedly closes the cheapest such node. Producing the patterns
    that customer still needs is what performs the closure.

    Ties break towards the customer needing fewest not-yet-produced patterns,
    then by index for determinism.

    An earlier version of this function selected on missing patterns rather than
    degree, and was measurably worse than plain tabu search (31/51/64 against
    22/42/63 on SP2/SP3/SP4). Degree is the rule the literature describes.
    """
    n_customers = instance.n_customers
    n_patterns = instance.n_patterns
    if n_patterns == 0:
        return 0, []

    customer_patterns = [set(instance.customer_patterns(c)) for c in range(n_customers)]
    remaining = {c for c in range(n_customers) if customer_patterns[c]}

    # Adjacency in the MOSP graph: customers are neighbours when some pattern is
    # required by both. Closing a node traverses every arc incident to it, so the
    # degree within the not-yet-closed set is what the selection rule costs.
    neighbours: list[set[int]] = [set() for _ in range(n_customers)]
    pattern_customers = [set(instance.pattern_customers(p)) for p in range(n_patterns)]
    for holders in pattern_customers:
        for c in holders:
            neighbours[c] |= holders
    for c in range(n_customers):
        neighbours[c].discard(c)

    produced: list[int] = []
    produced_set: set[int] = set()

    while remaining:
        best_customer = min(
            remaining,
            key=lambda c: (len(neighbours[c] & remaining),
                           len(customer_patterns[c] - produced_set),
                           c),
        )
        for pattern in sorted(customer_patterns[best_customer] - produced_set):
            produced.append(pattern)
            produced_set.add(pattern)
        remaining.remove(best_customer)

    # Patterns no customer requires never affect the count; append them so the
    # result is a full permutation.
    for pattern in range(n_patterns):
        if pattern not in produced_set:
            produced.append(pattern)
            produced_set.add(pattern)

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
