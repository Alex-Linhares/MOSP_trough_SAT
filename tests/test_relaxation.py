"""Guards on the contraction relaxation driver.

The failure that matters here is a false proof: `prove(instance, ub)` returning
true for a `ub` above the real optimum would publish a lower bound that is
wrong, and the corpus would record it as certified. Every test below is built
around that one risk, and the central one asks for a proof at every `ub` from
the optimum up to the customer count -- exactly one of which may succeed.
"""

import itertools
import random

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.relaxation import (
    build,
    contract_to,
    merge_once,
    prove,
    singletons,
    split_once,
)


def _brute(inst):
    if inst.n_patterns == 0:
        return 0
    return min(max_open_stacks(inst, list(perm))
               for perm in itertools.permutations(range(inst.n_patterns)))


def _random_instance(rng, max_customers=6, max_patterns=6):
    n_customers = rng.randint(2, max_customers)
    n_patterns = rng.randint(2, max_patterns)
    density = rng.choice([0.3, 0.5, 0.7])
    rows = [[1 if rng.random() < density else 0 for _ in range(n_patterns)]
            for _ in range(n_customers)]
    return MOSPInstance.from_matrix(rows, name="r")


def test_a_proof_is_only_ever_offered_at_the_true_optimum():
    """The soundness test. Above the optimum there is nothing to prove, and
    claiming otherwise would be a fabricated lower bound."""
    rng = random.Random(31)
    proofs = 0
    for _ in range(120):
        inst = _random_instance(rng)
        optimum = _brute(inst)
        for ub in range(optimum, inst.n_customers + 2):
            result = prove(inst, ub)
            if result.proved:
                assert ub == optimum, (
                    f"claimed MOSP >= {ub} but the optimum is {optimum}")
                proofs += 1
    assert proofs > 30, "nothing was ever proved; the test proves nothing"


def test_contraction_only_ever_relaxes():
    """Every partition the driver can reach has an optimum at or below the
    original's, which is what makes a refutation on it transfer."""
    rng = random.Random(32)
    checked = 0
    for _ in range(60):
        inst = _random_instance(rng, max_customers=6, max_patterns=5)
        base = _brute(inst)
        groups = singletons(inst)
        while True:
            nxt = merge_once(inst, groups)
            if nxt is None or len(nxt) == len(groups):
                break
            groups = nxt
            checked += 1
            assert _brute(build(inst, groups)) <= base
    assert checked > 100, "too few contractions to be evidence"


def test_splitting_undoes_exactly_one_merge():
    rng = random.Random(33)
    for _ in range(40):
        inst = _random_instance(rng)
        groups = contract_to(inst, singletons(inst), 2)
        while True:
            split = split_once(inst, groups, None, 0)
            if split is None:
                break
            assert len(split) == len(groups) + 1
            assert (sorted(c for g in split for c in g.members)
                    == sorted(c for g in groups for c in g.members))
            groups = split
        # Fully split means back to the original instance.
        assert len(groups) == inst.n_customers
        assert all(not g.splittable for g in groups)


def test_a_witness_is_only_returned_when_it_beats_the_bound():
    """The one non-proof outcome that carries information: the descent reached
    the original instance and found a solution below `ub`."""
    rng = random.Random(34)
    seen = 0
    for _ in range(60):
        inst = _random_instance(rng)
        optimum = _brute(inst)
        result = prove(inst, optimum + 1)
        assert not result.proved
        if result.witness is not None:
            seen += 1
            from satisfiability.heuristics import product_order_from_customers
            ordering = product_order_from_customers(inst, result.witness)
            assert max_open_stacks(inst, ordering) <= optimum
    assert seen > 10, "no witness was ever returned; the test proves nothing"


def test_the_contracted_instance_keeps_every_customer():
    rng = random.Random(35)
    for _ in range(40):
        inst = _random_instance(rng)
        groups = contract_to(inst, singletons(inst), 2)
        members = sorted(c for group in groups for c in group.members)
        assert members == list(range(inst.n_customers))
        relaxed = build(inst, groups)
        assert relaxed.n_patterns == inst.n_patterns
        assert relaxed.n_customers == len(groups)
