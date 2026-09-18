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
