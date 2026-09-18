"""Guards on the instance reductions, against exhaustive search.

Every reduction here is a claim about optima, and four earlier claims of this
kind in this project were wrong in ways no amount of reading caught. So each one
is checked the same way: enumerate every product order of a small random
instance, reduce, enumerate again, and compare -- never compare a reduction
against another piece of the same reasoning.

The two value-preserving reductions are held to equality *and* to their lift
reproducing that value on the original instance. Contraction is held to the
inequality it actually claims, and to refusing the merge that breaks it.
"""

import itertools
import random

import pytest

from mosp.instance import MOSPInstance
from mosp.preprocess import (
    components,
    contract,
    contraction_scores,
    lift_component_orderings,
    merge_one,
    remove_dominated_patterns,
)
from mosp.verify import max_open_stacks


def _brute(inst):
    if inst.n_patterns == 0:
        return 0
    return min(max_open_stacks(inst, list(perm))
               for perm in itertools.permutations(range(inst.n_patterns)))


def _random_instance(rng, max_customers=6, max_patterns=6, density=None):
    n_customers = rng.randint(1, max_customers)
    n_patterns = rng.randint(1, max_patterns)
    density = density if density is not None else rng.choice([0.2, 0.4, 0.6, 0.8])
    rows = [[1 if rng.random() < density else 0 for _ in range(n_patterns)]
            for _ in range(n_customers)]
    return MOSPInstance.from_matrix(rows, name="t")


def test_pattern_dominance_preserves_the_optimum():
    """Dropping a dominated product may not change the answer, in either direction."""
    rng = random.Random(0)
    fired = 0
    for _ in range(300):
        inst = _random_instance(rng)
        reduced = remove_dominated_patterns(inst)
        if reduced.instance.n_patterns < inst.n_patterns:
            fired += 1
        assert _brute(reduced.instance) == _brute(inst)
    assert fired > 100, "the reduction never fired; the test proves nothing"


def test_pattern_dominance_lift_achieves_the_reduced_value():
    """An ordering of the reduced instance must transfer at no cost."""
    rng = random.Random(1)
    for _ in range(300):
        inst = _random_instance(rng)
        reduced = remove_dominated_patterns(inst)
        for perm in itertools.permutations(range(reduced.instance.n_patterns)):
            order = list(perm)
            lifted = reduced.lift(order)
            assert sorted(lifted) == list(range(inst.n_patterns))
            assert (max_open_stacks(inst, lifted)
                    <= max_open_stacks(reduced.instance, order))


def test_pattern_dominance_keeps_one_of_a_duplicated_pair():
    """Identical columns dominate each other; exactly one has to survive."""
    inst = MOSPInstance.from_matrix([[1, 1, 0], [1, 1, 1]], name="dup")
    reduced = remove_dominated_patterns(inst)
    assert reduced.kept == [0]
    assert reduced.dependents == {0: [1, 2]}
    assert sorted(reduced.lift([0])) == [0, 1, 2]


def test_decomposition_optimum_is_the_maximum_over_components():
    """`MOSP(I) = max over components`, and the concatenation attains it."""
    rng = random.Random(2)
    split = 0
    for _ in range(200):
        inst = _random_instance(rng, max_customers=6, max_patterns=6, density=0.25)
        parts, free = components(inst)
        if len(parts) > 1:
            split += 1

        assert sorted([p for part in parts for p in part.patterns] + free) == \
            list(range(inst.n_patterns))

        values, orderings = [], []
        for part in parts:
            best = min(
                (max_open_stacks(part.instance, list(perm))
                 for perm in itertools.permutations(range(part.instance.n_patterns))),
                default=0)
            values.append(best)
            orderings.append(next(
                list(perm)
                for perm in itertools.permutations(range(part.instance.n_patterns))
                if max_open_stacks(part.instance, list(perm)) == best))

        assert max(values, default=0) == _brute(inst)

        lifted = lift_component_orderings(parts, orderings, free)
        assert sorted(lifted) == list(range(inst.n_patterns))
        assert max_open_stacks(inst, lifted) == _brute(inst)
    assert split > 20, "no instance decomposed; the test proves nothing"


def test_contraction_relaxes_the_instance():
    """Lemma 1: contracting an edge can only lower the optimum."""
    rng = random.Random(3)
    contractions = 0
    for _ in range(200):
        inst = _random_instance(rng, max_customers=6, max_patterns=5)
        base = _brute(inst)
        for c, d in itertools.combinations(range(inst.n_customers), 2):
            if not (inst.customer_patterns(c) & inst.customer_patterns(d)):
                continue
            contractions += 1
            assert _brute(contract(inst, c, d)) <= base
    assert contractions > 500, "too few contractions to be evidence"


def test_contraction_refuses_a_non_adjacent_merge():
    """Merging customers that share no product is not a contraction and
    measurably breaks the bound, so it is rejected rather than allowed."""
    inst = MOSPInstance.from_matrix([[1, 0], [0, 1]], name="apart")
    with pytest.raises(ValueError, match="share no product"):
        contract(inst, 0, 1)
    with pytest.raises(ValueError):
        contract(inst, 0, 0)


def test_contraction_score_matches_equation_one():
    """F(c) = sum over neighbours c' of |N(c) - N(c')|, divided by |N(c)|."""
    rng = random.Random(4)
    for _ in range(40):
        inst = _random_instance(rng)
        neighbours = [set() for _ in range(inst.n_customers)]
        for p in range(inst.n_patterns):
            holders = set(inst.pattern_customers(p))
            for c in holders:
                neighbours[c] |= holders

        for c, score in enumerate(contraction_scores(inst)):
            own = neighbours[c]
            expected = (sum(len(own - neighbours[o]) for o in own) / len(own)
                        if own else 0.0)
            assert score == pytest.approx(expected)


def test_merge_one_contracts_an_edge_and_loses_a_customer():
    rng = random.Random(5)
    for _ in range(40):
        inst = _random_instance(rng, density=0.6)
        try:
            contracted, (c, d) = merge_one(inst)
        except ValueError:
            continue
        assert inst.customer_patterns(c) & inst.customer_patterns(d)
        assert contracted.n_customers == inst.n_customers - 1
        assert contracted.n_patterns == inst.n_patterns
        assert _brute(contracted) <= _brute(inst)
