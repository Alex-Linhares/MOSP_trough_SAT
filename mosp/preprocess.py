"""Instance reductions: pattern dominance, component decomposition, contraction.

Three operations on a `MOSPInstance`, two of which preserve the optimum and one
of which deliberately does not.

**Pattern dominance** (`remove_dominated_patterns`) drops a product whose
customers are a subset of another product's. Producing it immediately after its
dominator opens no stack that was not already open, so it costs nothing and the
optimum is unchanged. Yanasse & Senne (2010) list this among six pre-processing
operations, none of which this project implemented until now.

**Component decomposition** (`components`) splits the instance along the
connected components of the MOSP graph. The components share no customer and no
product, so their sequences can be concatenated and `MOSP(I)` is the maximum
over them. Chu & Stuckey (2009) discard decomposable instances from their
benchmark rather than exploit them, which is itself evidence the reduction is
worth controlling for.

**Contraction** (`contract`) merges two customers that share a product by
OR-ing their rows. This is an edge contraction of the MOSP graph, and by
Lemma 1 of Chu & Stuckey (attributed to Becceneri, Yanasse & Soma 2004) the
result is a *relaxation*: its optimum is a lower bound on the original's, not
equal to it. Merging two customers that share no product is not a contraction
and breaks the lemma — measured at 17 violations in 1,044 attempts, against
none in 3,167 genuine contractions — so `contract` refuses it.

Each value-preserving reduction comes with a lift: an ordering of the reduced
instance becomes an ordering of the original achieving the same count. The
reductions are only useful if that lift is exact, so it is what the tests check,
against exhaustive search rather than against the reduction's own arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mosp.instance import MOSPInstance


@dataclass
class PatternReduction:
    """The result of dropping dominated patterns, with the lift back."""

    instance: MOSPInstance
    kept: list[int]
    """Original indices of the surviving patterns, in the reduced order."""
    dependents: dict[int, list[int]]
    """Original index of each survivor -> the dropped patterns it dominates."""

    def lift(self, ordering: list[int]) -> list[int]:
        """Turn an ordering of the reduced instance into one of the original.

        Each dropped pattern follows its dominator immediately. Because its
        customers are a subset of the dominator's, it opens nothing new, and any
        customer it keeps open was open at the dominator's step already — so the
        count at its step cannot exceed the count at the dominator's.
        """
        full: list[int] = []
        for index in ordering:
            original = self.kept[index]
            full.append(original)
            full.extend(self.dependents.get(original, ()))
        return full


def remove_dominated_patterns(instance: MOSPInstance) -> PatternReduction:
    """Drop every pattern whose customer set sits inside another pattern's.

    Ties — patterns needed by exactly the same customers — keep the lowest
    index. Patterns with no customers at all are dominated by everything and
    are dropped unless the instance has nothing else.
    """
    customers = [frozenset(instance.pattern_customers(p))
                 for p in range(instance.n_patterns)]

    kept: list[int] = []
    for p, own in enumerate(customers):
        dominated = any(
            (own < other) or (own == other and q < p)
            for q, other in enumerate(customers) if q != p
        )
        if not dominated:
            kept.append(p)

    if not kept:  # every pattern empty, or a single pattern instance
        kept = list(range(instance.n_patterns))

    kept_set = set(kept)
    dependents: dict[int, list[int]] = {}
    for p, own in enumerate(customers):
        if p in kept_set:
            continue
        dominator = next(q for q in kept if own <= customers[q])
        dependents.setdefault(dominator, []).append(p)

    if instance.n_patterns:
        matrix = instance.matrix[:, kept]
    else:
        matrix = instance.matrix

    reduced = MOSPInstance(
        matrix=np.ascontiguousarray(matrix),
        n_customers=instance.n_customers,
        n_patterns=len(kept),
        name=instance.name,
    )
    return PatternReduction(instance=reduced, kept=kept, dependents=dependents)


@dataclass
class Component:
    """One connected component of the MOSP graph, as a standalone instance."""

    instance: MOSPInstance
    customers: list[int]
    """Original customer indices, in the component instance's row order."""
    patterns: list[int]
    """Original pattern indices, in the component instance's column order."""


def components(instance: MOSPInstance) -> tuple[list[Component], list[int]]:
    """Split along connected components of the MOSP graph.

    Two customers are adjacent when they share a product, so a component owns
    its products outright: no product is needed by customers of two different
    components. Products nobody needs belong to no component and are returned
    separately.

    Returns:
        (components, free_patterns). `MOSP(instance)` is the maximum of the
        components' optima, and 0 if there are none.
    """
    parent = list(range(instance.n_customers))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    free: list[int] = []
    pattern_owner: list[int | None] = []
    for p in range(instance.n_patterns):
        holders = sorted(instance.pattern_customers(p))
        if not holders:
            free.append(p)
            pattern_owner.append(None)
            continue
        pattern_owner.append(holders[0])
        for other in holders[1:]:
            a, b = find(holders[0]), find(other)
            if a != b:
                parent[a] = b

    groups: dict[int, list[int]] = {}
    for c in range(instance.n_customers):
        if instance.customer_patterns(c):
            groups.setdefault(find(c), []).append(c)

    result: list[Component] = []
    for root, member_customers in groups.items():
        member_patterns = [p for p, owner in enumerate(pattern_owner)
                           if owner is not None and find(owner) == root]
        matrix = instance.matrix[np.ix_(member_customers, member_patterns)]
        result.append(Component(
            instance=MOSPInstance(
                matrix=np.ascontiguousarray(matrix),
                n_customers=len(member_customers),
                n_patterns=len(member_patterns),
                name=f"{instance.name}#{len(result)}" if instance.name else "",
            ),
            customers=member_customers,
            patterns=member_patterns,
        ))
    return result, free


def lift_component_orderings(
    parts: list[Component], orderings: list[list[int]], free: list[int]
) -> list[int]:
    """Concatenate per-component orderings into one for the whole instance.

    While one component's products are being made, every other component's
    customers are either not yet open or already closed, so the count at each
    step is the count within that component alone and the concatenation
    achieves the maximum of the parts.
    """
    full: list[int] = []
    for part, ordering in zip(parts, orderings):
        full.extend(part.patterns[index] for index in ordering)
    full.extend(free)
    return full


def contract(instance: MOSPInstance, c: int, d: int) -> MOSPInstance:
    """Contract the MOSP-graph edge between customers `c` and `d`.

    The merged customer needs the union of the two product sets, so it inherits
    exactly the union of the two neighbourhoods and no other adjacency changes.
    The result is a relaxation: `MOSP(contracted) <= MOSP(instance)`, which
    makes an optimum of the contracted instance a certified lower bound on the
    original.

    Raises:
        ValueError: if the two customers share no product, which is a merge
            rather than a contraction and does not preserve the bound.
    """
    if c == d:
        raise ValueError("cannot contract a customer with itself")
    shared = instance.customer_patterns(c) & instance.customer_patterns(d)
    if not shared:
        raise ValueError(
            f"customers {c} and {d} share no product: merging them is not an "
            "edge contraction and does not relax the instance"
        )

    lo, hi = min(c, d), max(c, d)
    matrix = instance.matrix.copy()
    matrix[lo] = np.maximum(matrix[lo], matrix[hi])
    matrix = np.delete(matrix, hi, axis=0)
    return MOSPInstance(
        matrix=np.ascontiguousarray(matrix),
        n_customers=instance.n_customers - 1,
        n_patterns=instance.n_patterns,
        name=instance.name,
    )


def contraction_scores(instance: MOSPInstance) -> list[float]:
    """Chu & Stuckey's equation (1): `F(c) = Σ_{c'∈N(c)} |N(c) - N(c')| / |N(c)|`.

    High `F(c)` marks a customer whose neighbours do not cover it — one that
    opens stacks nobody else opens. They merge highest-`F` first and report
    low-degree-first as clearly worse.
    """
    neighbours = _neighbourhoods(instance)
    scores = []
    for c in range(instance.n_customers):
        own = neighbours[c]
        if not own:
            scores.append(0.0)
            continue
        scores.append(sum(len(own - neighbours[other]) for other in own) / len(own))
    return scores


def merge_one(instance: MOSPInstance) -> tuple[MOSPInstance, tuple[int, int]]:
    """Contract the edge Chu & Stuckey's ranking picks: highest `F(c)`, then the
    neighbour `c'` maximising `|N(c) - N(c')|`.

    Returns:
        (contracted instance, (c, c')) with the pair in original indices. The
        contracted instance keeps `min(c, c')`'s row position and shifts every
        customer above `max(c, c')` down by one.

    Raises:
        ValueError: if no customer has a neighbour, so there is no edge left.
    """
    neighbours = _neighbourhoods(instance)
    scores = contraction_scores(instance)

    best: tuple[float, int, int] | None = None
    for c in range(instance.n_customers):
        partners = neighbours[c] - {c}
        if not partners:
            continue
        partner = max(partners, key=lambda o: (len(neighbours[c] - neighbours[o]), -o))
        if best is None or scores[c] > best[0]:
            best = (scores[c], c, partner)

    if best is None:
        raise ValueError("no two customers share a product: nothing to contract")
    _, c, partner = best
    return contract(instance, c, partner), (c, partner)


def _neighbourhoods(instance: MOSPInstance) -> list[set[int]]:
    """Self-inclusive MOSP-graph neighbourhoods, as sets."""
    neighbours: list[set[int]] = [set() for _ in range(instance.n_customers)]
    for p in range(instance.n_patterns):
        holders = set(instance.pattern_customers(p))
        for customer in holders:
            neighbours[customer] |= holders
    return neighbours
