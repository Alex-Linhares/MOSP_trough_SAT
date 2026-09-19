"""The C port must answer exactly what the Python reference answers.

`satisfiability/customer_search.py` is the reference: it is what the exhaustive
tests are written against, and where the two differ it is right. The C exists
only for speed -- about 120x -- and a fast search that disagrees with its
reference produces refutations that are confidently false. A refutation is the
half of an optimality claim nobody can check by inspection, so this is the file
standing between a 120x speedup and a corrupted corpus.
"""

import itertools
import random

import pytest

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.customer_search import decide
from satisfiability.heuristics import product_order_from_customers
from satisfiability.native import decide_native, native_available

CONFIGS = [
    pytest.param(dict(subset_rule=False, definite_move=False, memo=False), id="plain"),
    pytest.param(dict(subset_rule=True, definite_move=False, memo=False), id="subset"),
    pytest.param(dict(subset_rule=False, definite_move=True, memo=False), id="definite"),
    pytest.param(dict(subset_rule=True, definite_move=True, memo=True), id="all"),
    pytest.param(dict(subset_rule=True, definite_move=True, memo=True, restrict=True),
                 id="restricted"),
]

needs_native = pytest.mark.skipif(not native_available(),
                                  reason="the C search did not build here")


def _random(rng, max_customers=8, max_patterns=7):
    rows = [[1 if rng.random() < rng.choice([0.2, 0.4, 0.6, 0.8]) else 0
             for _ in range(rng.randint(1, max_patterns))]
            for _ in range(rng.randint(1, max_customers))]
    width = max(len(r) for r in rows)
    rows = [r + [0] * (width - len(r)) for r in rows]
    return MOSPInstance.from_matrix(rows, name="t")


@needs_native
@pytest.mark.parametrize("config", CONFIGS)
def test_the_c_answers_what_the_python_answers(config):
    """Same status at every k, under every combination of the rules."""
    rng = random.Random(90)
    for _ in range(40):
        instance = _random(rng)
        for k in range(0, instance.n_customers + 2):
            reference = decide(instance, k, native=False, **config)
            ported = decide_native(instance, k, **config)
            assert ported is not None, "the C declined an instance it should take"
            assert ported.status == reference.status, (
                f"k={k}: python said {reference.status}, C said {ported.status}")


@needs_native
def test_the_c_witnesses_are_real():
    """A sat answer must carry a closing order that achieves the k asked for."""
    rng = random.Random(91)
    for _ in range(60):
        instance = _random(rng)
        optimum = min(max_open_stacks(instance, list(p))
                      for p in itertools.permutations(range(instance.n_patterns)))
        answer = decide_native(instance, optimum)
        assert answer.status == "sat"
        ordering = product_order_from_customers(instance, answer.order)
        assert sorted(ordering) == list(range(instance.n_patterns))
        assert max_open_stacks(instance, ordering) <= optimum


@needs_native
def test_the_c_visits_the_same_nodes_on_a_real_refutation():
    """Equal node counts are the sharpest evidence the two are the same search,
    and would catch a divergence that happened to agree on small instances.

    It takes a real instance to show anything: the dominance rules prune
    constructed ones so hard that a 16x14 sparse instance never branches past a
    couple of hundred nodes, so the comparison would be vacuous there. SP2's
    refutation at 18 branches enough to mean something and still runs in
    milliseconds under the C.
    """
    from pathlib import Path

    from benchmarks.ratchet import find_instances

    found = find_instances(["SP2"], Path("benchmarks/instances"))
    if not found:
        pytest.skip("SP2 benchmark file not found")
    instance = found[0]

    ported = decide_native(instance, 18)          # SP2's optimum is 19
    assert ported.status == "unsat"
    assert ported.nodes > 1000, "not enough branching to be evidence"

    reference = decide(instance, 18, native=False)
    assert ported.nodes == reference.nodes, (
        f"python visited {reference.nodes}, C {ported.nodes}")


@needs_native
def test_it_declines_rather_than_guessing():
    """Out of its range it returns None, so the caller falls back to the Python
    instead of getting an answer from a search that ignored a flag."""
    instance = MOSPInstance.from_matrix([[1, 1], [0, 1]], name="small")
    assert decide_native(instance, 1, old_move=True) is None

    wide = MOSPInstance.from_matrix([[1] * 3 for _ in range(129)], name="wide")
    assert decide_native(wide, 129) is None
    # and the Python still answers it
    assert decide(wide, 129).status == "sat"


@needs_native
def test_a_budget_stops_the_c_without_claiming_a_refutation():
    rng = random.Random(93)
    for _ in range(40):
        instance = _random(rng)
        settled = decide_native(instance, 0)
        if settled.status != "unsat" or settled.nodes < 2:
            continue
        assert decide_native(instance, 0, max_nodes=1).status == "unknown"
        break
