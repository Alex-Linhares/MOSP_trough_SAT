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
- `rule` — the two-key closing rule of `reports/ml_nature.md` §7: close the
  customer that opens the fewest new stacks, on ties the one with the most
  unclosed neighbours. No model, no search.
- `rule+cs-dfs` — the DFS seeded with the rule's order (loop0004 item 01).
- `mcnh` — Becceneri, Yanasse & Soma (2004)'s Minimal Cost Node heuristic as
  they state it: an *arc traversal* of the MOSP graph, patterns sequenced when
  all their pieces have been opened (loop0004 item 02). `mcnh-arcs` is the
  same traversal with a pattern sequenced when its last own arc is traversed.

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
    incident to a node" is not the same operation. Adapting it properly needed
    Becceneri, Yanasse & Soma (2004), obtained 2026-09-27.

    None of the three reproduces the published MCNh, which Frinhani et al. report
    at 23/37/57. This version is kept because it seeds tabu best (`mcn+tabu`
    reaches 21/39/62, against 22/42/63 for tabu alone), not because it is a
    faithful MCNh. The faithful one is `mcnh` below (loop0004 item 02): the
    2004 arc traversal, which gives exactly 23/37/57 and Frinhani's value on
    all 21 named Challenge rows (`reports/ml_nature.md` §29).
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


# Fan orders among equal-cost candidates, shared by `restricted_dfs` and the
# complete search in `customer_search.decide`. "index" is what every recorded
# node count and every `cs-dfs` value was made with and is the default
# everywhere; "degree" is measured behind the flag (reports/ml_nature.md §20).
FAN_ORDERS = ("index", "degree")


def fan_sort_key(fan_order: str, masks: Sequence[int], remaining: int):
    """Sort key over `(cost, customer, ...)` tuples for a named fan order.

    `"index"`: cheapest first, ties by customer index -- the tuple's own order.
    `"degree"`: cheapest first, ties to the customer with the most neighbours
    not yet closed (`|N[c] ∩ remaining| - 1`, `N` self-inclusive), then index.
    That is the two-key rule of `reports/ml_nature.md` §7 read as a fan order:
    its greedy is the first leaf of a DFS sorted this way.
    """
    if fan_order == "index":
        return lambda item: item[:2]
    if fan_order == "degree":
        return lambda item: (item[0], -((masks[item[1]] & remaining).bit_count() - 1), item[1])
    raise ValueError(f"fan_order must be one of {FAN_ORDERS}, not {fan_order!r}")


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
    fan_order: str = "index",
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

    `fan_order` breaks ties among equal-cost candidates: `"index"` (default)
    by customer index, `"degree"` by most neighbours not yet closed, then
    index -- under which the first leaf is the two-key rule of
    `reports/ml_nature.md` §7. Registered as `cs-dfs+degree`; `cs-dfs` is
    unchanged.
    """
    if fan_order not in FAN_ORDERS:
        raise ValueError(f"fan_order must be one of {FAN_ORDERS}, not {fan_order!r}")
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
        if fan_order == "index":
            scored.sort()
        else:
            scored.sort(key=fan_sort_key(fan_order, masks, remaining))

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


def two_key_closing_order(instance: MOSPInstance) -> list[int]:
    """The two-key closing rule of `reports/ml_nature.md` §7, followed greedily.

    At every step, over *every* customer not yet closed (not only the open
    frontier), pick the one that

    1. opens the fewest new stacks: `|N[c] \\ opened|`, `N` self-inclusive;
    2. on ties, has the most unclosed neighbours: `|N[c] \\ closed| - 1`;
    3. on ties, has the fewest products not yet produced; then the lowest index.

    Keys 3 are MCN's own tie-break (`least_cost_node`), so the rule is
    `learning.distil.lex_key(HYPOTHESES["lex:min newly_opened,max
    remaining_degree"])` computed with popcounts instead of a feature matrix;
    `tests/test_heuristics.py` checks the two agree. Key 1 is the cheapest-first
    order in which `restricted_dfs` expands its fan, so the greedy is that
    search's first leaf; key 2 is the *reverse* of MCN's minimum degree.

    Held out over 1,920 corpus instances the rule's construction is 0.348 stacks
    over the optimum against 1.616 for MCN and 0.519 for the LightGBM ranker
    (`reports/ml_nature.md` §7). Returns only customers with at least one
    product, as `restricted_dfs`'s `seed_order` expects.
    """
    masks = _neighbour_masks(instance)
    n = instance.n_customers
    pmasks = [0] * n
    for c in range(n):
        for p in instance.customer_patterns(c):
            pmasks[c] |= 1 << p
    remaining = [c for c in range(n) if masks[c]]
    closed = opened = produced = 0
    order: list[int] = []
    while remaining:
        pick = min(
            remaining,
            key=lambda c: (
                (masks[c] & ~opened).bit_count(),
                -((masks[c] & ~closed).bit_count() - 1),
                (pmasks[c] & ~produced).bit_count(),
                c,
            ),
        )
        order.append(pick)
        opened |= masks[pick]
        closed |= 1 << pick
        produced |= pmasks[pick]
        remaining.remove(pick)
    return order


def two_key_rule(instance: MOSPInstance, **_: object) -> UpperBound:
    """Greedy construction under `two_key_closing_order`, valued by simulation."""
    ordering = product_order_from_customers(instance, two_key_closing_order(instance))
    return max_open_stacks(instance, ordering), ordering


def rule_then_dfs(
    instance: MOSPInstance, max_nodes: int = 200_000, **_: object
) -> UpperBound:
    """`restricted_dfs` with the two-key rule's order as its incumbent.

    The argument of `learned_then_dfs` with a seed that needs no model: the DFS
    prunes against its incumbent, and §7 measured the rule's order as a better
    incumbent than the ranker's (`cs-dfs+rule` 0.127 / 92.7% against 0.157 /
    91.0% held out). Whether that holds over the whole corpus, against the
    709-better / 13-worse `learned+cs-dfs` scored over `cs-dfs`, is what
    `learning.rule_seed` measures (`reports/ml_nature.md` §28). Registered as
    `rule+cs-dfs`; the default of nothing.
    """
    return restricted_dfs(instance, max_nodes=max_nodes,
                          seed_order=two_key_closing_order(instance))


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


def _mosp_graph_untraversed(instance: MOSPInstance) -> list[int]:
    """Adjacency of the MOSP graph as bitmasks, self excluded: the arcs of
    Becceneri, Yanasse & Soma (2004)'s `Gp` not yet traversed, at the start.
    Parallel arcs (two patterns sharing the same pair) are one arc, as their
    §4 says."""
    n = instance.n_customers
    adjacency = [0] * n
    for pattern in range(instance.n_patterns):
        holders = instance.pattern_customers(pattern)
        mask = 0
        for c in holders:
            mask |= 1 << c
        for c in holders:
            adjacency[c] |= mask & ~(1 << c)
    return adjacency


def mcnh_trace(instance: MOSPInstance) -> dict:
    """Becceneri, Yanasse & Soma (2004) §4, the Minimal Cost Node heuristic,
    run to its arc sequence with every loop recorded.

    Their pseudocode, read as the worked example of their Table 1 forces:

    - `Ω(k)` is the degree of node `k` over the arcs not yet traversed; `SETV`
      holds every node with `Ω ≥ 1`, ordered by non-decreasing `Ω`, ties by
      index (their printed `SETV` lists are exactly that);
    - each loop takes `Ω(k)` of the first node of `SETV` and traverses the arc
      `(n1, n2)` with `Ω(n1) = Ω(k)` whose endpoints have the pair-wise
      smallest `Ω` -- so `n1` ranges over *every* minimum-degree node, not only
      the first, and `n2` over its untraversed neighbours, minimising `Ω(n2)`;
      ties go to `SETV` order for `n1`, then for `n2`. (Their first loop picks
      (4, 8) although node 3 heads `SETV`: node 3's cheapest arc costs 3 + 4,
      node 4's 3 + 3.)
    - both endpoints enter `OPEN`; an endpoint whose `Ω` falls to 0 leaves it;
    - then every untraversed arc between two `OPEN` nodes is traversed, in
      lexicographic order of its endpoints (the order their `ARC` lists show),
      closing nodes as their `Ω` reaches 0;
    - `ξ` is the size of `OPEN` with both endpoints counted before either is
      closed, at its largest.

    Returns `{"arcs": [(a, b), ...], "loops": [...], "xi": int}`, `loops` being
    one dict per outer loop with the `(n1, n2)` it chose, `s` after it, `OPEN`
    after it, and `SETV` after it, for comparison with the paper's printed
    states.
    """
    n = instance.n_customers
    untraversed = _mosp_graph_untraversed(instance)
    n_arcs = sum(mask.bit_count() for mask in untraversed) // 2

    def setv() -> list[int]:
        return sorted((c for c in range(n) if untraversed[c]),
                      key=lambda c: (untraversed[c].bit_count(), c))

    arcs: list[tuple[int, int]] = []
    loops: list[dict] = []
    open_mask = 0
    xi = 0

    def traverse(a: int, b: int) -> None:
        nonlocal open_mask, xi
        arcs.append((a, b))
        untraversed[a] &= ~(1 << b)
        untraversed[b] &= ~(1 << a)
        open_mask |= (1 << a) | (1 << b)
        xi = max(xi, open_mask.bit_count())
        for c in (a, b):
            if untraversed[c] == 0:
                open_mask &= ~(1 << c)

    while len(arcs) < n_arcs:
        order = setv()
        position = {c: i for i, c in enumerate(order)}
        degree_k = untraversed[order[0]].bit_count()
        best: tuple | None = None
        for n1 in order:
            if untraversed[n1].bit_count() != degree_k:
                break
            candidates = untraversed[n1]
            while candidates:
                n2 = (candidates & -candidates).bit_length() - 1
                candidates &= candidates - 1
                key = (untraversed[n2].bit_count(), position[n1], position[n2])
                if best is None or key < best[0]:
                    best = (key, n1, n2)
        assert best is not None
        _, n1, n2 = best
        traverse(n1, n2)
        # every arc not yet traversed between two open nodes, lexicographically
        pending: list[tuple[int, int]] = []
        scan = open_mask
        while scan:
            a = (scan & -scan).bit_length() - 1
            scan &= scan - 1
            others = untraversed[a] & open_mask
            while others:
                b = (others & -others).bit_length() - 1
                others &= others - 1
                if a < b:
                    pending.append((a, b))
        for a, b in sorted(pending):
            if untraversed[a] >> b & 1:
                traverse(a, b)
        loops.append({
            "n1": n1, "n2": n2, "s": len(arcs), "xi": xi,
            "open": [c for c in range(n) if open_mask >> c & 1],
            "setv": setv(),
        })
    return {"arcs": arcs, "loops": loops, "xi": xi}


def patterns_from_arcs(
    instance: MOSPInstance, arcs: Sequence[tuple[int, int]], rule: str = "nodes"
) -> list[int]:
    """The pattern sequence an arc sequence dictates.

    `rule="nodes"` is the sentence Becceneri, Yanasse & Soma (2004) quote from
    Becceneri (1999): "sequence a pattern Pi when, for the first time, all the
    nodes corresponding to all the piece types in Pi are open" -- read as
    *have been opened*, since an arc that closes a node still completes the
    pattern it belongs to (their P2 is sequenced by the arc (1, 4), which
    closes node 4). Patterns completed by the same arc are sequenced with the
    ones containing that arc first, then by index; that tie-break is the only
    one the example does not print and is needed for their P12 before P3.

    `rule="arcs"` sequences a pattern when the last of its own arcs has been
    traversed. On patterns of two pieces the two coincide; on their example
    both give the printed sequence. `learning.mcnh` measures how often they
    differ over the corpus.

    Patterns with no arc and no opened node -- empty columns, and the
    single-customer patterns of a customer with no neighbour -- go last, by
    index; they cost at most one stack wherever they sit.
    """
    if rule not in ("nodes", "arcs"):
        raise ValueError(f"unknown pattern rule {rule!r}; use 'nodes' or 'arcs'")
    m = instance.n_patterns
    holders = [instance.pattern_customers(p) for p in range(m)]
    need = [0] * m
    for p in range(m):
        for c in holders[p]:
            need[p] |= 1 << c
    if rule == "arcs":
        remaining_arcs = [{(min(a, b), max(a, b))
                           for a in holders[p] for b in holders[p] if a < b}
                          for p in range(m)]
    touched = 0
    sequenced: list[int] = []
    done = [False] * m
    for a, b in arcs:
        touched |= (1 << a) | (1 << b)
        arc = (min(a, b), max(a, b))
        completed: list[int] = []
        for p in range(m):
            if done[p]:
                continue
            if rule == "nodes":
                ready = need[p] and (need[p] & ~touched) == 0
            else:
                remaining_arcs[p].discard(arc)
                ready = need[p] and not remaining_arcs[p] and (need[p] & ~touched) == 0
            if ready:
                completed.append(p)
        completed.sort(key=lambda p: (not (need[p] >> a & 1 and need[p] >> b & 1), p))
        for p in completed:
            done[p] = True
            sequenced.append(p)
    sequenced.extend(p for p in range(m) if not done[p])
    return sequenced


def mcnh(instance: MOSPInstance, pattern_rule: str = "nodes", **_: object) -> UpperBound:
    """The Minimal Cost Node heuristic of Becceneri, Yanasse & Soma (2004) §4,
    as an arc traversal (`mcnh_trace`) followed by their arcs-to-patterns
    rule (`patterns_from_arcs`); valued by simulation.

    Reproduces their Table 1 example loop by loop -- the arc (4, 8) first,
    seven loops, the sixteen arcs in their printed order, ξ = 4 -- and their
    printed sequence P11, P10, P14, P2, P4, P6, P12, P3, P9, P1, P7, P5, P8,
    P13 with Fig. 2's profile (`tests/test_mcnh.py`). Not the node-closing
    `mcn` above, which Yanasse & Senne (2010) summarise in one sentence and
    which does not reproduce the published MCNh numbers; `reports/ml_nature.md`
    §29 compares the two, the two-key `rule`, and Frinhani et al. (2018)'s
    MCNh column. Registered as `mcnh`; the default of nothing.
    """
    if instance.n_patterns == 0:
        return 0, []
    trace = mcnh_trace(instance)
    ordering = patterns_from_arcs(instance, trace["arcs"], rule=pattern_rule)
    return max_open_stacks(instance, ordering), ordering


STRATEGIES: dict[str, Strategy] = {
    "tabu": tabu,
    "mcn": least_cost_node,
    "mcn+tabu": mcn_then_tabu,
    "customer-tabu": customer_tabu,
    "cs-dfs": restricted_dfs,
    "cs-dfs+degree": lambda instance, **kwargs: restricted_dfs(
        instance, fan_order="degree", **{k: v for k, v in kwargs.items() if k != "fan_order"}),
    "customer-tabu+cs-dfs": mcn_tabu_then_dfs,
    "rule": two_key_rule,
    "rule+cs-dfs": rule_then_dfs,
    "mcnh": mcnh,
    "mcnh-arcs": lambda instance, **kwargs: mcnh(
        instance, pattern_rule="arcs", **{k: v for k, v in kwargs.items() if k != "pattern_rule"}),
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
