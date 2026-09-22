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
- `customer-tabu` — tabu search over customer closing orders rather than
  product orders.
- `cs-dfs` — Chu & Stuckey's `ub_MOSP`: depth-first search over customer
  closing orders, branching only on customers already open.
- `customer-tabu+cs-dfs` — tabu first, then the DFS pruning against it.

Measured on the SP instances, our tabu search returns 22/42/63 against optima of
19/34/53, while Frinhani et al. (2018) report HBF2r reaching 19/35/53 in under a
second. That gap is algorithmic, not a matter of speed, which is why MCN exists
here.
"""

from __future__ import annotations

from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path
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


def product_order_from_customers(
    instance: MOSPInstance, customer_order: Sequence[int]
) -> list[int]:
    """Build a production sequence from a customer closing order.

    Chu & Stuckey (2009), §2: schedule every product needed by the first
    customer, then those still needed by the second, and so on. Their result is
    that this loses nothing — for any product ordering there is a customer order
    whose construction is at least as good — so a search over customer orders
    covers an optimum.

    That claim was checked here against exhaustive search on 118 random
    instances, with no loss. What could *not* be reconstructed is a closed-form
    cost in customer-order terms; four attempts each failed (see
    `reports/chu_stuckey_transferable.md` §2.1). A local search does not need
    one: it builds the sequence and counts, which is exactly what this does.
    """
    produced: list[int] = []
    seen: set[int] = set()
    for customer in customer_order:
        for pattern in sorted(instance.customer_patterns(customer)):
            if pattern not in seen:
                produced.append(pattern)
                seen.add(pattern)
    for pattern in range(instance.n_patterns):
        if pattern not in seen:
            produced.append(pattern)
    return produced


def customer_tabu(
    instance: MOSPInstance,
    seed: int = 42,
    max_iterations: int = 500,
    tabu_tenure: int = 7,
    n_neighbors: int = 200,
    **_: object,
) -> UpperBound:
    """Tabu search over *customer closing orders* rather than product orders.

    The existing `tabu` strategy permutes products directly, which knows nothing
    about the problem: most of the orderings it moves between differ only in the
    arrangement of products inside one customer's block and score identically,
    so its neighbourhood is largely wasted.

    Searching customer orders instead moves through a space that provably
    contains an optimum and in which every move changes the objective for a
    reason. Each candidate is scored by constructing its production sequence and
    counting open stacks, so no closed-form cost is needed.
    """
    import random

    n_customers = instance.n_customers
    active = [c for c in range(n_customers) if instance.customer_patterns(c)]
    if not active or instance.n_patterns == 0:
        order = list(range(instance.n_patterns))
        return max_open_stacks(instance, order), order

    def evaluate(customer_order: Sequence[int]) -> int:
        return max_open_stacks(
            instance, product_order_from_customers(instance, customer_order))

    # Seed from MCN's closing order, which is already a good construction, and
    # fall back on random restarts if it is not.
    rng = random.Random(seed)
    best_order = _mcn_customer_order(instance)
    best_value = evaluate(best_order)

    for _ in range(3):
        candidate = list(active)
        rng.shuffle(candidate)
        value = evaluate(candidate)
        if value < best_value:
            best_value, best_order = value, candidate

    current, current_value = list(best_order), best_value
    tabu: dict[int, int] = {}
    size = len(current)

    for iteration in range(max_iterations):
        move = None
        move_value = None
        for _ in range(min(n_neighbors, size * size)):
            i, j = rng.randrange(size), rng.randrange(size)
            if i == j:
                continue
            trial = list(current)
            trial[i], trial[j] = trial[j], trial[i]
            value = evaluate(trial)
            blocked = tabu.get(i, 0) > iteration or tabu.get(j, 0) > iteration
            # Aspiration: a tabu move that beats the incumbent is taken anyway.
            if blocked and value >= best_value:
                continue
            if move_value is None or value < move_value:
                move, move_value = (i, j), value

        if move is None:
            break

        i, j = move
        current[i], current[j] = current[j], current[i]
        current_value = move_value
        tabu[i] = iteration + tabu_tenure
        tabu[j] = iteration + tabu_tenure

        if current_value < best_value:
            best_value, best_order = current_value, list(current)

    return best_value, product_order_from_customers(instance, best_order)


def _mcn_customer_order(instance: MOSPInstance) -> list[int]:
    """The closing order implied by least cost node (minimum remaining degree)."""
    n_customers = instance.n_customers
    customer_patterns = [set(instance.customer_patterns(c)) for c in range(n_customers)]
    remaining = {c for c in range(n_customers) if customer_patterns[c]}

    neighbours: list[set[int]] = [set() for _ in range(n_customers)]
    for pattern in range(instance.n_patterns):
        holders = set(instance.pattern_customers(pattern))
        for customer in holders:
            neighbours[customer] |= holders
    for customer in range(n_customers):
        neighbours[customer].discard(customer)

    order: list[int] = []
    while remaining:
        chosen = min(remaining,
                     key=lambda c: (len(neighbours[c] & remaining),
                                    len(customer_patterns[c]), c))
        order.append(chosen)
        remaining.remove(chosen)
    return order


def _neighbour_masks(instance: MOSPInstance) -> list[int]:
    """Self-inclusive customer neighbourhoods of the MOSP graph, as bitmasks.

    `N(c)` in Chu & Stuckey's notation: every customer sharing a product with
    `c`, including `c` itself. A customer with no products gets an empty mask
    and never appears in a search state.
    """
    masks = [0] * instance.n_customers
    for pattern in range(instance.n_patterns):
        holders = sorted(instance.pattern_customers(pattern))
        mask = 0
        for customer in holders:
            mask |= 1 << customer
        for customer in holders:
            masks[customer] |= mask
    return masks


def _cs_cost(masks: Sequence[int], order: Sequence[int]) -> int:
    """Chu & Stuckey's cost of a customer closing order: `max_i |O(S_i) - S_{i-1}|`.

    This is an upper estimate of the value of the product order the closing
    order builds, not an equality — it over-charges orders that are not
    realisable as product orders. Measured at 313/400 agreement per order, but
    400/400 as a minimum over all orders (`reports/chu_stuckey_plan.md` §0.1),
    which is the property the search below relies on.
    """
    opened = closed = peak = 0
    for customer in order:
        opened |= masks[customer]
        peak = max(peak, (opened & ~closed).bit_count())
        closed |= 1 << customer
    return peak


def restricted_dfs(
    instance: MOSPInstance,
    max_nodes: int = 200_000,
    seed_order: Optional[Sequence[int]] = None,
    **_: object,
) -> UpperBound:
    """Chu & Stuckey's `ub_MOSP` (2009, §3.4): DFS over customer closings,
    branching only on customers whose stack is already open.

    Their complete search branches on every remaining customer, `for c in R`.
    The incomplete one branches on `R ∩ O(S)` instead: a customer nobody has
    opened yet can only add its whole neighbourhood at once, so closing it early
    is rarely part of a good order, and forbidding it cuts the branching factor
    to the frontier. The restriction is a heuristic — it can exclude every
    optimal order — and they report speedups of 104× and 3010× on 100-100-2 and
    125-125-2 for a bound that is almost always optimal anyway.

    Two consequences of searching in `_cs_cost` space rather than simulating:

    - pruning is monotone. The cost of a prefix never falls as the prefix grows,
      so a branch whose running peak has already reached the incumbent cannot
      beat it and is cut. Candidates are expanded cheapest-first, which makes
      that cut fire on the whole rest of the fan at once.
    - the number returned is *not* the search's own score. `_cs_cost` can
      over-charge, so the winning closing order is turned into a product order
      and simulated, which can only come out lower.

    `seed_order` supplies the incumbent to prune against; without one the MCN
    closing order is used. Passing `customer_tabu`'s best order composes the two
    — the DFS then only ever reports something tabu could not find.

    `max_nodes` caps the search. It is anytime: on exhausting the budget it
    returns the best order found so far, which is never worse than the seed.
    """
    n_patterns = instance.n_patterns
    active = [c for c in range(instance.n_customers) if instance.customer_patterns(c)]
    if not active or n_patterns == 0:
        order = list(range(n_patterns))
        return max_open_stacks(instance, order), order

    masks = _neighbour_masks(instance)

    seed = list(seed_order) if seed_order is not None else _mcn_customer_order(instance)
    best_order = seed
    best_cs = _cs_cost(masks, seed)

    remaining_all = 0
    for customer in active:
        remaining_all |= 1 << customer

    budget = [max_nodes]
    path: list[int] = []

    def descend(closed: int, opened: int, remaining: int, peak: int) -> None:
        nonlocal best_cs, best_order

        if remaining == 0:
            if peak < best_cs:
                best_cs, best_order = peak, list(path)
            return

        # The restriction. At the root, and whenever the frontier runs dry
        # because the customer graph is disconnected, every remaining customer
        # is a candidate — some stack has to be opened first.
        candidates = remaining & opened
        if candidates == 0:
            candidates = remaining

        scored: list[tuple[int, int, int, int]] = []
        bits = candidates
        while bits:
            bit = bits & -bits
            bits ^= bit
            customer = bit.bit_length() - 1
            now_open = opened | masks[customer]
            scored.append(((now_open & ~closed).bit_count(), customer, bit, now_open))
        scored.sort()

        for cost, customer, bit, now_open in scored:
            # `peak` is below the incumbent by the caller's own check, so
            # max(peak, cost) clears it exactly when cost does; and the rest of
            # the fan costs at least as much.
            if cost >= best_cs:
                break
            if budget[0] <= 0:
                return
            budget[0] -= 1
            path.append(customer)
            descend(closed | bit, now_open, remaining ^ bit, max(peak, cost))
            path.pop()

    descend(0, 0, remaining_all, 0)

    ordering = product_order_from_customers(instance, best_order)
    return max_open_stacks(instance, ordering), ordering


def mcn_tabu_then_dfs(
    instance: MOSPInstance,
    seed: int = 42,
    max_nodes: int = 200_000,
    **kwargs: object,
) -> UpperBound:
    """`customer-tabu` to find an incumbent, then the restricted DFS under it.

    The DFS prunes against whatever it starts from, so a good seed is worth more
    to it than extra nodes: a tabu incumbent that is one stack lower cuts every
    branch that touches that stack count. The two searches also fail
    differently — tabu samples a neighbourhood at random, the DFS enumerates a
    frontier — so what one leaves on the table the other often takes.
    """
    tabu_value, tabu_ordering = customer_tabu(instance, seed=seed, **kwargs)
    order = _customer_order_from_products(instance, tabu_ordering)
    dfs_value, dfs_ordering = restricted_dfs(
        instance, max_nodes=max_nodes, seed_order=order)
    if dfs_value <= tabu_value:
        return dfs_value, dfs_ordering
    return tabu_value, tabu_ordering


def _customer_order_from_products(
    instance: MOSPInstance, ordering: Sequence[int]
) -> list[int]:
    """The closing order a product sequence induces: customers by last product.

    Inverse in spirit to `product_order_from_customers`, and not an exact
    inverse — a product order can close two customers at the same step, and the
    tie is broken by index.
    """
    position = {pattern: i for i, pattern in enumerate(ordering)}
    active = [c for c in range(instance.n_customers) if instance.customer_patterns(c)]
    return sorted(
        active,
        key=lambda c: (max(position[p] for p in instance.customer_patterns(c)), c),
    )

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


@lru_cache(maxsize=4)
def _load_cached(path: str):
    from learning.policy import load

    return load(Path(path))


def _learned_model(model_path: object = None):
    """Load the learned closing-order policy, or say precisely what is missing.

    Soft: this module imports with no machine learning installed, and only a
    *call* to one of the two strategies below fails. It fails loudly rather than
    falling back to MCN, because a silent fallback would let a benchmark run
    report `learned+cs-dfs` numbers that are `cs-dfs` numbers.
    """
    try:
        from learning.policy import DEFAULT_MODEL
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise RuntimeError(
            "the learned strategies need `pip install -r learning/requirements.txt`"
        ) from exc

    path = Path(model_path) if model_path else DEFAULT_MODEL
    if not path.exists():
        raise RuntimeError(
            f"no trained policy at {path}; run `python -m learning.policy train`"
        )
    return _load_cached(str(path))


def learned(
    instance: MOSPInstance, model_path: object = None, **_: object
) -> UpperBound:
    """Greedy closing order under the policy of `learning.policy`.

    Trained by imitating the closing orders the certified witnesses induce. The
    value returned is `max_open_stacks` of the product order it builds, so the
    model proposes and the simulation decides -- a bad model costs quality and
    never correctness. See `reports/learning.md` §2.
    """
    from learning.policy import learned_closing_order

    order = learned_closing_order(instance, _learned_model(model_path))
    ordering = product_order_from_customers(instance, order)
    return max_open_stacks(instance, ordering), ordering


def learned_then_dfs(
    instance: MOSPInstance,
    max_nodes: int = 200_000,
    model_path: object = None,
    **_: object,
) -> UpperBound:
    """`restricted_dfs` with the learned order as its incumbent.

    The DFS prunes against whatever it starts from, and a better incumbent is
    worth more to it than extra nodes -- the argument `mcn_tabu_then_dfs` makes
    for tabu, with a seed that is better still. Cross-validated over 2,000
    held-out instances it halves the DFS's error (MAE 0.30 -> 0.14, exact
    82% -> 92%, worst case +10 -> +6).
    """
    from learning.policy import learned_closing_order

    order = learned_closing_order(instance, _learned_model(model_path))
    return restricted_dfs(instance, max_nodes=max_nodes, seed_order=order)


STRATEGIES: dict[str, Strategy] = {
    "tabu": tabu,
    "mcn": least_cost_node,
    "mcn+tabu": mcn_then_tabu,
    "customer-tabu": customer_tabu,
    "cs-dfs": restricted_dfs,
    "customer-tabu+cs-dfs": mcn_tabu_then_dfs,
    "learned": learned,
    "learned+cs-dfs": learned_then_dfs,
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
