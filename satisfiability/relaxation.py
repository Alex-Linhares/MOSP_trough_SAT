"""Prove a lower bound by contracting customers (Chu & Stuckey 2009, §3.5).

Contracting an edge of the MOSP graph -- OR-ing two rows that share a product --
relaxes the instance, so `MOSP(contracted) <= MOSP(original)` (their Lemma 1,
measured here on 3,167 contractions, `reports/chu_stuckey_plan.md` §0.2). A
contracted instance is smaller and much easier to search, and its optimum is a
certified lower bound on the original's. When that bound meets the upper bound
already held, **the instance closes with no refutation on the full instance at
all**.

**The question asked is a decision, not an optimum.** Their driver computes
`MOSP(I')` exactly and compares it against `ub`. We only need to know whether
`MOSP(I') >= ub`, which is one refutation at `ub - 1` on a small instance rather
than a full descent on it. By Lemma 1 that refutation refutes `ub - 1` on the
original, which is the certificate wanted, and the calls are cheaper and stop
earlier.

**Why contraction and the customer search fit together.** The complete search of
`satisfiability.customer_search` is fast on dense instances and slow on sparse
ones, where the branching factor and the depth both inflate. Contraction makes
an instance smaller and denser at once, so it repairs precisely the case that
search is worst at. That is also the case where our own gaps are smallest, which
is the honest limit of the method and is stated in `chu_stuckey_plan.md` §2
rather than discovered by a referee.

**Search shape.** Contract greedily down to `ub` customers -- where at most `ub`
stacks can be open, so the bound is trivially satisfiable and proves nothing --
then *unmerge* one group at a time. Each split makes the relaxation tighter and
the search harder, until either the refutation lands or the budget runs out.
Splitting is guided by the witness: a group whose splitting the current solution
survives cannot be the one holding the bound down, so one it does not survive is
chosen instead. This is what repairs the greedy merge order's mistakes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np

from mosp.instance import MOSPInstance
from satisfiability.customer_search import decide
from satisfiability.heuristics import _cs_cost, _neighbour_masks


@dataclass(frozen=True)
class Group:
    """A set of original customers merged into one, and how it was built.

    The children record the single contraction that formed this group, so it can
    be undone without undoing anything else. Splitting a group leaves a
    partition still reachable by edge contractions: whether two groups share a
    product depends only on the groups themselves, never on the rest of the
    partition, so every merge that remains is still legal.
    """

    members: frozenset[int]
    left: "Group | None" = None
    right: "Group | None" = None

    @property
    def splittable(self) -> bool:
        return self.left is not None


def singletons(instance: MOSPInstance) -> list[Group]:
    """One group per customer: the original instance, uncontracted."""
    return [Group(frozenset({c})) for c in range(instance.n_customers)]


def build(instance: MOSPInstance, groups: list[Group]) -> MOSPInstance:
    """The contracted instance: one row per group, the OR of its members."""
    rows = np.zeros((len(groups), instance.n_patterns), dtype=np.int8)
    for index, group in enumerate(groups):
        for member in group.members:
            rows[index] |= instance.matrix[member]
    return MOSPInstance(
        matrix=rows,
        n_customers=len(groups),
        n_patterns=instance.n_patterns,
        name=f"{instance.name}/relax{len(groups)}" if instance.name else "",
    )


def merge_once(instance: MOSPInstance, groups: list[Group]) -> list[Group] | None:
    """Contract the edge Chu & Stuckey's equation (1) ranking picks.

    `F(c) = Σ_{c'∈N(c)} |N(c) - N(c')| / |N(c)|` scores a customer by how much
    of its own neighbourhood its neighbours fail to cover; the highest scorer is
    merged with the neighbour covering it least. They report low-degree-first as
    clearly worse. Returns None when no two groups share a product.
    """
    masks = _neighbour_masks(build(instance, groups))

    best: tuple[float, int, int] | None = None
    for index, own in enumerate(masks):
        partners = own & ~(1 << index)
        if not own or not partners:
            continue

        score, bits = 0.0, own
        while bits:
            bit = bits & -bits
            bits ^= bit
            score += (own & ~masks[bit.bit_length() - 1]).bit_count()
        score /= own.bit_count()

        partner, distinct = -1, -1
        bits = partners
        while bits:
            bit = bits & -bits
            bits ^= bit
            other = bit.bit_length() - 1
            count = (own & ~masks[other]).bit_count()
            if count > distinct:
                partner, distinct = other, count

        if best is None or score > best[0]:
            best = (score, index, partner)

    if best is None:
        return None

    _, first, second = best
    low, high = min(first, second), max(first, second)
    merged = Group(groups[low].members | groups[high].members,
                   groups[low], groups[high])
    kept = list(groups)
    kept[low] = merged
    del kept[high]
    return kept


def contract_to(
    instance: MOSPInstance, groups: list[Group], target: int
) -> list[Group]:
    """Merge until at most `target` groups remain, or no edge is left."""
    while len(groups) > target:
        nxt = merge_once(instance, groups)
        if nxt is None:
            break
        groups = nxt
    return groups


def split_once(
    instance: MOSPInstance,
    groups: list[Group],
    witness: list[int] | None,
    k: int,
) -> list[Group] | None:
    """Undo one contraction, preferring one the witness does not survive.

    A witness is a closing order of the *current* groups achieving at most `k`.
    If splitting a group leaves that same order still achieving `k` -- with the
    two halves closed one after the other, in whichever of the two orders is
    better -- then the split cannot be what raises the bound, and there is no
    point paying for a harder search to find out. A group the order does not
    survive is chosen instead.

    Returns None when nothing is left to split.
    """
    candidates = [i for i, group in enumerate(groups) if group.splittable]
    if not candidates:
        return None

    def apply(index: int) -> list[Group]:
        group = groups[index]
        return groups[:index] + [group.left, group.right] + groups[index + 1:]

    if witness is not None:
        for index in candidates:
            split = apply(index)
            masks = _neighbour_masks(build(instance, split))
            # Reindex the witness: everything after the split shifts by one,
            # and the split group becomes two adjacent closings.
            survives = False
            for pair in ((index, index + 1), (index + 1, index)):
                order: list[int] = []
                for position in witness:
                    if position == index:
                        order.extend(pair)
                    else:
                        order.append(position + 1 if position > index else position)
                if _cs_cost(masks, order) <= k:
                    survives = True
                    break
            if not survives:
                return split

    # Everything survived, or there is no witness to test against: split the
    # largest group, which is where the relaxation is loosest.
    largest = max(candidates, key=lambda i: len(groups[i].members))
    return apply(largest)


@dataclass
class RelaxationResult:
    """What the driver established, and where it stopped.

    `proved` means a contracted instance refuted `ub - 1`, so `ub` is optimal.
    `witness` is set only in the opposite case -- the search ran all the way back
    to the original instance and found a solution below `ub`, which is not a
    proof but is a better upper bound, in customer closing order.
    """

    proved: bool
    groups: int
    calls: int
    nodes: int
    seconds: float
    note: str
    witness: list[int] | None = None


def prove(
    instance: MOSPInstance,
    ub: int,
    *,
    start: int | None = None,
    time_budget: float | None = None,
    max_nodes: int | None = None,
    **kwargs: object,
) -> RelaxationResult:
    """Try to certify that `MOSP(instance) >= ub` from a contracted instance.

    Args:
        ub: the upper bound to meet. A refutation of `ub - 1` on any contraction
            proves the instance optimal at `ub`.
        start: how many groups to contract down to before unmerging. Defaults to
            `ub`, their choice, which is the loosest relaxation that can still
            be tight.
        time_budget: overall wall-clock budget, shared across calls.
        max_nodes: per-call node budget.

    Returns:
        A `RelaxationResult`. `proved` true means `ub` is the optimum.
    """
    started = time.monotonic()
    deadline = None if time_budget is None else started + time_budget

    groups = contract_to(instance, singletons(instance), start or ub)
    calls = nodes = 0

    while True:
        relaxed = build(instance, groups)
        answer = decide(relaxed, ub - 1, max_nodes=max_nodes,
                        deadline=deadline, **kwargs)
        calls += 1
        nodes += answer.nodes

        if answer.status == "unsat":
            return RelaxationResult(
                True, len(groups), calls, nodes, time.monotonic() - started,
                f"refuted k={ub - 1} on a {len(groups)}-customer contraction")

        if answer.status == "unknown":
            return RelaxationResult(
                False, len(groups), calls, nodes, time.monotonic() - started,
                f"budget out at {len(groups)} customers")

        # Satisfiable: this contraction is too loose to hold the bound.
        split = split_once(instance, groups, answer.order, ub - 1)
        if split is None:
            # Nothing left to undo, so the original instance itself admits a
            # solution below ub. Not a proof -- a better upper bound. The order
            # is in group indices, and the groups are singletons here but not in
            # customer order, so it has to be mapped back.
            witness = [next(iter(groups[index].members)) for index in answer.order]
            return RelaxationResult(
                False, len(groups), calls, nodes, time.monotonic() - started,
                f"the instance itself is satisfiable at k={ub - 1}",
                witness=witness)
        groups = split


def lower_bound(
    instance: MOSPInstance,
    target: int,
    *,
    time_budget: float | None = None,
    max_nodes: int | None = None,
) -> tuple[int, int]:
    """A certified lower bound from one contraction, without needing to close.

    `prove` answers yes or no: either the relaxation holds the upper bound or it
    does not. This answers *how far* the relaxation gets, by solving the
    contracted instance outright -- its optimum is a lower bound on the
    original's by Lemma 1, whatever that optimum turns out to be.

    That is the outcome worth having on the instances relaxation cannot close.
    Chu & Stuckey note the same thing in passing: insisting only on a bound five
    below the true optimum lets around 45 customers go on 125-125-4, provable in
    seconds. A bound of 55 in place of 41 improves the reported gap even when
    nothing closes, and unlike a heuristic upper bound it is a proof.

    Args:
        target: how many customers to contract down to. Smaller is easier to
            solve and weaker as a bound.

    Returns:
        `(bound, groups)`. The bound is 0 when the contracted instance could not
        be settled within the budget, which is no information rather than a
        claim of zero.
    """
    from satisfiability.customer_search import solve
    from satisfiability.mosp_solver import _lower_bound

    groups = contract_to(instance, singletons(instance), target)
    relaxed = build(instance, groups)
    settled = solve(relaxed, lower=_lower_bound(relaxed),
                    time_budget=time_budget, max_nodes=max_nodes)
    return (settled.value if settled.proved else 0), len(groups)


# ---------------------------------------------------------------------------
# The contraction-minor step (2026-10-12, `reports/minor_bound.md`)
#
# The same relaxation as above, with a different merge rule and a different
# driver. `prove` merges by Chu & Stuckey's F(c) ranking down to `ub` and
# unmerges by the witness; the minor step contracts a minimum-degree customer
# into a neighbour (the survey's "min-d": its least-degree neighbour; or
# "least-c": the neighbour sharing fewest neighbours with it), which is plain
# minimum-degree-first, the order Chu & Stuckey call "clearly worse" for their
# driver and which on the hard corpus instances beats every stored relaxation
# bound (`reports/pathwidth_lower_bounds_survey.md` §5): 24 vs 16 on
# Random-125-125-2-1_0, 21 vs 13 on 2-3_0. It then refutes `k` on contractions
# of growing size, under node budgets, before the descent refutes `k` on the
# full instance.
#
# Merging two customers that share a product contracts that edge of the MOSP
# graph: the merged customer shares a product with exactly the customers either
# did. So by minor monotonicity of pathwidth and `MOSPGraph.lean`
# (MOSP = pathwidth(MOSP graph) + 1), MOSP(contracted) <= MOSP(original), which
# is Lemma 1 above, now a consequence of a classical theorem (Fellows & Langston
# 1987, Lemma 4.2) rather than a measurement. Minor monotonicity itself is not
# yet in Lean.
#
# The contraction mirrors `pathwidth_solver/pathwidth/minor.py` exactly, so the
# two sides contract the same graph the same way; `tests/test_minor_bound.py`
# checks that they agree.
# ---------------------------------------------------------------------------

MINOR_RULES = ("min-d", "least-c")


def minor_sequence(instance: MOSPInstance, size: int, rule: str = "min-d") -> list[tuple[int, int]]:
    """Greedy contractions taking the MOSP graph down to `size` customers.

    Returns `(v, u)` pairs over customer indices: merge customer `v` into `u`
    (they share a product at that point), or `u == -1` to drop a customer that
    shares no product with any other, which deletes an isolated vertex. A
    minimum-degree customer is chosen (ties by index) and merged into its
    neighbour by `rule`. Customers with no products are not in the graph and
    are never touched.
    """
    if rule not in MINOR_RULES:
        raise ValueError(f"rule must be one of {MINOR_RULES}, not {rule!r}")
    masks = _neighbour_masks(instance)
    adj = [m & ~(1 << c) for c, m in enumerate(masks)]
    alive = sum(1 << c for c, m in enumerate(masks) if m)
    n = len(masks)
    seq: list[tuple[int, int]] = []
    while alive.bit_count() > max(size, 0):
        v, low = -1, n + 1
        bits = alive
        while bits:
            bit = bits & -bits
            bits ^= bit
            x = bit.bit_length() - 1
            d = adj[x].bit_count()
            if d < low:
                low, v = d, x
        nb = adj[v]
        u, best = -1, None
        bits = nb
        while bits:
            bit = bits & -bits
            bits ^= bit
            c = bit.bit_length() - 1
            score = adj[c].bit_count() if rule == "min-d" else (adj[c] & nb).bit_count()
            if best is None or score < best:
                best, u = score, c
        seq.append((v, u))
        if u >= 0:
            merged = (adj[u] | nb) & ~((1 << u) | (1 << v))
            adj[u] = merged
            bits = merged
            while bits:
                bit = bits & -bits
                bits ^= bit
                w = bit.bit_length() - 1
                adj[w] = (adj[w] | (1 << u)) & ~(1 << v)
        adj[v] = 0
        alive &= ~(1 << v)
    return seq


def minor_groups(instance: MOSPInstance, sequence: list[tuple[int, int]]) -> list[Group]:
    """Replay a contraction sequence as groups, checking every step.

    Each merge must join two current groups that share a product -- an edge of
    the contracted MOSP graph -- and each drop must remove a group sharing no
    product with any other. Raises `ValueError` otherwise, so a recorded
    sequence that replays is a genuine minor. Groups are returned in the order
    of the customer each was merged into; customers with no products stay as
    singletons, inactive in `build`'s instance as in the original.
    """
    groups: dict[int, Group] = {c: Group(frozenset({c})) for c in range(instance.n_customers)}
    rows = {c: set(instance.customer_patterns(c)) for c in groups}
    for step, (v, u) in enumerate(sequence):
        if v not in groups or not rows[v]:
            raise ValueError(f"step {step}: customer {v} is not in the current graph")
        if u == -1:
            if any(rows[v] & rows[c] for c in groups if c != v):
                raise ValueError(f"step {step}: dropping {v}, which shares a product")
            groups.pop(v)
            rows.pop(v)
            continue
        if u not in groups or u == v or not (rows[v] & rows[u]):
            raise ValueError(f"step {step}: {v} and {u} share no product")
        groups[u] = Group(groups[u].members | groups[v].members, groups[u], groups.pop(v))
        rows[u] |= rows.pop(v)
    return [groups[c] for c in sorted(groups)]


@dataclass
class MinorConfig:
    """Budgets of the minor step on the MOSP side; the same fields and
    defaults as `pathwidth_solver`'s `MinorConfig` (see its docstring),
    justified in `reports/minor_bound.md`: skipped below `min_customers`;
    a `probe_nodes` look at the full instance first; contractions from half
    the customers to 85% in 5% steps; `first_nodes` growing by `growth` per
    size, `share` of the remaining `total_nodes` per target, `time_fraction`
    of a time budget; a stalled size retried with a larger budget; a
    contraction that admits `k` (lifted order, `restrict_nodes` restricted
    search) never searched."""

    min_customers: int = 40
    start_fraction: float = 0.5
    step_fraction: float = 0.05
    max_fraction: float = 0.85
    rules: tuple[str, ...] = MINOR_RULES
    first_nodes: int = 100_000
    growth: float = 3.0
    total_nodes: int = 20_000_000
    time_fraction: float = 0.25
    on_stall: str = "retry"
    probe_nodes: int = 100_000
    share: float = 0.5
    restrict_nodes: int = 20_000

    def sizes(self, n: int, k: int) -> list[int]:
        """Contraction sizes for refuting `MOSP <= k`: a contraction with at
        most `k` customers can never hold more than `k` stacks open."""
        import math
        lo = max(k + 1, math.ceil(self.start_fraction * n))
        hi = int(self.max_fraction * n)
        step = max(2, int(round(self.step_fraction * n)))
        return list(range(lo, min(hi, n - 1) + 1, step))


@dataclass
class MinorCertificate:
    """`MOSP <= refuted` is false on the contraction `minor_groups(instance,
    contractions)`, hence on the instance: the optimum is at least
    `refuted + 1`."""

    refuted: int
    size: int
    rule: str
    contractions: list
    nodes: int

    def as_dict(self) -> dict:
        return dict(refuted=self.refuted, size=self.size, rule=self.rule,
                    contractions=[list(p) for p in self.contractions], nodes=self.nodes)


class MinorLadder:
    """The minor step's state across one descent (see the section comment)."""

    def __init__(self, instance: MOSPInstance, config: MinorConfig | None = None):
        self.instance = instance
        self.config = config or MinorConfig()
        self.n = sum(1 for c in range(instance.n_customers) if instance.customer_patterns(c))
        self.nodes = 0
        self.seconds = 0.0
        self.calls = 0
        self.log: list[tuple] = []
        self._sequences: dict[str, list[tuple[int, int]]] = {}
        self._minors: dict[tuple[str, int], MOSPInstance] = {}
        self._upper: dict[tuple[str, int], int] = {}
        self._refuted: dict[tuple[str, int], int] = {}
        self._groups: dict[tuple[str, int], list[Group]] = {}
        self._cheap_done: set[tuple[str, int]] = set()
        self._restricted: dict[tuple[str, int], int] = {}
        self.best: MinorCertificate | None = None     # the highest lower bound proved

    @property
    def applies(self) -> bool:
        return self.n >= self.config.min_customers

    def minor(self, rule: str, size: int) -> tuple[MOSPInstance, list[tuple[int, int]]]:
        need = self.n - size
        seq = self._sequences.get(rule)
        if seq is None or len(seq) < need:
            smallest = min(self.config.sizes(self.n, 0) or [size])
            seq = minor_sequence(self.instance, min(size, smallest), rule)
            self._sequences[rule] = seq
        seq = seq[:need]
        key = (rule, size)
        if key not in self._minors:
            self._groups[key] = minor_groups(self.instance, seq)
            self._minors[key] = build(self.instance, self._groups[key])
        return self._minors[key], seq

    def lifted_cost(self, rule: str, size: int, order: list[int] | None) -> int | None:
        """The descent's closing order lifted to the contraction: each group
        closes when its last member does. Its cost never exceeds the order's
        (a group on the boundary of a prefix has a member there), so a cheap
        "sat" when the contraction is looser. None without an order."""
        if not order:
            return None
        minor, _ = self.minor(rule, size)
        groups = self._groups[(rule, size)]
        position = {c: i for i, c in enumerate(order)}
        active = [i for i in range(minor.n_customers) if minor.customer_patterns(i)]
        last = {i: max(position.get(c, -1) for c in groups[i].members) for i in active}
        return _cs_cost(_neighbour_masks(minor), sorted(active, key=lambda i: last[i]))

    def _decide(self, minor: MOSPInstance, k: int, budget: int, deadline, note: str,
                size: int, rule: str, flags: dict):
        started = time.monotonic()
        answer = decide(minor, k, max_nodes=budget, deadline=deadline, **flags)
        elapsed = time.monotonic() - started
        self.nodes += answer.nodes
        self.seconds += elapsed
        self.calls += 1
        self.log.append((k, size, rule, note + answer.status, answer.nodes, round(elapsed, 3)))
        return answer

    def try_refute(self, k: int, *, deadline: float | None = None, max_nodes: int | None = None,
                   order: list[int] | None = None, **flags: object) -> MinorCertificate | None:
        """Try to prove `MOSP >= k + 1` on a contraction. `order`, the
        descent's closing order, gives free "sat" answers when lifted."""
        cfg = self.config
        if self.n < cfg.min_customers:
            return None
        flags = {f: v for f, v in flags.items() if f not in ("max_nodes", "deadline", "restrict")}
        budget = float(cfg.first_nodes)
        # one call may spend at most `share` of what is left, so a target far
        # above the optimum cannot starve the ones below it
        cap = self.nodes + int(cfg.share * max(0, cfg.total_nodes - self.nodes))
        sizes = cfg.sizes(self.n, k)
        i = 0
        while i < len(sizes):
            size = sizes[i]
            stalled = asked = 0
            seen: set = set()
            for rule in cfg.rules:
                key = (rule, size)
                minor, seq = self.minor(rule, size)
                shape = tuple(sorted(tuple(sorted(g.members)) for g in self._groups[key]))
                if shape in seen:
                    continue                      # both rules built the same contraction
                seen.add(shape)
                if self._upper.get(key, self.n + 1) <= k:
                    continue
                if key not in self._cheap_done:
                    self._cheap_done.add(key)
                    lifted = self.lifted_cost(rule, size, order)
                    if lifted is not None:
                        self._upper[key] = min(self._upper.get(key, self.n + 1), lifted)
                        if lifted <= k:
                            continue
                remaining = cap - self.nodes
                if max_nodes is not None:
                    remaining = min(remaining, max_nodes)
                if remaining <= 0 or (deadline is not None and time.monotonic() >= deadline):
                    return None
                if cfg.restrict_nodes and self._restricted.get(key, self.n + 1) > k:
                    # the restricted search finds most solutions cheaply; it
                    # never refutes, so it can only save a call
                    self._restricted[key] = k
                    quick = self._decide(minor, k, min(cfg.restrict_nodes, remaining), deadline,
                                         "restrict:", size, rule, dict(flags, restrict=True))
                    if quick.status == "sat":
                        self._upper[key] = _cs_cost(_neighbour_masks(minor), quick.order)
                        continue
                asked += 1
                answer = self._decide(minor, k, int(min(budget, remaining)), deadline, "",
                                      size, rule, flags)
                if answer.status == "unsat":
                    self._refuted[key] = max(k, self._refuted.get(key, -1))
                    cert = MinorCertificate(k, size, rule, list(seq), answer.nodes)
                    if self.best is None or k > self.best.refuted:
                        self.best = cert
                    return cert
                if answer.status == "sat":
                    self._upper[key] = _cs_cost(_neighbour_masks(minor), answer.order)
                else:
                    stalled += 1
            budget *= cfg.growth
            if asked and stalled == asked:
                # every contraction asked ran out at this size; bigger cost more
                if cfg.on_stall != "retry":
                    return None
                continue                      # the same size, with the grown budget
            i += 1
        return None

    def raise_lower(self, lower: int, *, deadline: float | None = None,
                    max_nodes: int | None = None, **flags: object) -> MinorCertificate | None:
        """Prove minors' exact optimum, to raise the lower bound above `lower`.

        A minor that answered "sat" has a witness of value `p`; descending on
        it until a refutation proves its exact value, a lower bound for the
        instance. Minors are taken smallest first, each only while its witness
        is above the best bound so far, so the bound climbs with the size; the
        first budget overrun stops the climb (a larger minor costs more).
        Returns the best certificate held, if it beats `lower`; its
        `refuted + 1` is the bound.
        """
        cfg = self.config
        flags = {f: v for f, v in flags.items() if f not in ("max_nodes", "deadline", "restrict")}
        best = self.best
        cap = self.nodes + int(cfg.share * max(0, cfg.total_nodes - self.nodes))
        floor = max(lower, best.refuted + 1 if best else lower)
        for size, rule in sorted(((s_, r_) for (r_, s_) in self._upper), key=lambda t: t):
            p = self._upper[(rule, size)]
            minor, seq = self.minor(rule, size)
            stop = False
            while p > floor:
                if self._refuted.get((rule, size), -1) >= p - 1:
                    best, floor = MinorCertificate(p - 1, size, rule, list(seq), 0), p
                    break
                remaining = cap - self.nodes
                if max_nodes is not None:
                    remaining = min(remaining, max_nodes)
                if remaining <= 0 or (deadline is not None and time.monotonic() >= deadline):
                    stop = True
                    break
                if cfg.restrict_nodes:
                    quick = self._decide(minor, p - 1, min(cfg.restrict_nodes, int(remaining)), deadline,
                                         "restrict:", size, rule, dict(flags, restrict=True))
                    if quick.status == "sat":
                        p = min(p - 1, _cs_cost(_neighbour_masks(minor), quick.order))
                        self._upper[(rule, size)] = p
                        continue
                    remaining = cap - self.nodes
                    if max_nodes is not None:
                        remaining = min(remaining, max_nodes)
                    if remaining <= 0:
                        stop = True
                        break
                # what is left of this call's share: minors come smallest
                # first, and the first overrun ends the climb
                budget = int(remaining)
                answer = self._decide(minor, p - 1, budget, deadline, "lower:", size, rule, flags)
                if answer.status == "unsat":
                    self._refuted[(rule, size)] = p - 1
                    best, floor = MinorCertificate(p - 1, size, rule, list(seq), answer.nodes), p
                    break
                if answer.status != "sat":
                    stop = True
                    break
                p = min(p - 1, _cs_cost(_neighbour_masks(minor), answer.order))
                self._upper[(rule, size)] = p
            if stop:
                break
        self.best = best
        return best if best is not None and best.refuted + 1 > lower else None
