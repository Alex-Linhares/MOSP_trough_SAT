"""The expansion bound must never exceed a true optimum.

Same guard, and for the same reason, as `tests/test_lower_bounds.py`: a lower
bound above the optimum is not a slow bound, it is a wrong answer. The binary
search starts above the true optimum, returns a value, and simulating the
witness does not catch it because the witness really does achieve what is
reported.

The first draft of this bound failed exactly here — it capped `M(i)` without
proving the prefix range that cap is valid over, and returned 122 against an
optimum of 91 — so these tests exist before the bound is used anywhere.
"""

import itertools
import json
import random
from pathlib import Path

import pytest

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.expansion_bound import (
    _closed_masks,
    _f_exact,
    expansion_bound,
    mosp_lower_bound,
)

SOLUTIONS = Path("solutions")
INSTANCE_DIR = Path("benchmarks/instances")


def _random_instance(seed: int, max_c: int = 7, max_p: int = 6) -> MOSPInstance:
    rng = random.Random(seed)
    n_c, n_p = rng.randint(1, max_c), rng.randint(1, max_p)
    matrix = [[rng.randint(0, 1) for _ in range(n_p)] for _ in range(n_c)]
    return MOSPInstance.from_matrix(matrix, name=f"exp{seed}")


def _brute_force(instance: MOSPInstance) -> int:
    return min(max_open_stacks(instance, list(perm))
               for perm in itertools.permutations(range(instance.n_patterns)))


@pytest.mark.parametrize("seed", range(60))
def test_never_exceeds_the_brute_forced_optimum(seed):
    instance = _random_instance(seed)
    if instance.n_patterns == 0 or not instance.matrix.any():
        return
    assert mosp_lower_bound(instance, max_t=4) <= _brute_force(instance)


@pytest.mark.parametrize("max_t", [1, 2, 3, 5, 8])
def test_never_exceeds_the_optimum_at_any_depth(max_t):
    """Deeper caps widen the usable prefix range; none may overshoot."""
    for seed in range(25):
        instance = _random_instance(seed)
        if instance.n_patterns == 0 or not instance.matrix.any():
            continue
        assert mosp_lower_bound(instance, max_t=max_t) <= _brute_force(instance)


def test_f_is_monotone_and_exact():
    """`f(t+1) >= f(t)`: any C of size t+1 contains one of size t inside it."""
    instance = _random_instance(3, max_c=9, max_p=7)
    masks, n = _closed_masks(instance)
    order = sorted(range(n), key=lambda v: masks[v].bit_count())
    previous = 0
    for t in range(1, min(5, n) + 1):
        value = _f_exact(masks, n, t, order, None)
        # Exhaustive cross-check on a graph small enough to enumerate.
        brute = min((sum(masks[v] for v in c) if False else
                     _union(masks, c)).bit_count()
                    for c in itertools.combinations(range(n), t))
        assert value == brute
        assert value >= previous
        previous = value


def _union(masks, combo):
    out = 0
    for v in combo:
        out |= masks[v]
    return out


def test_closed_masks_match_the_mosp_graph():
    from customer_inter.customer_graph import build_customer_graph

    instance = _random_instance(11, max_c=10, max_p=8)
    masks, n = _closed_masks(instance)
    graph = build_customer_graph(instance)
    for v in range(n):
        expected = {v} | set(graph[v])
        got = {u for u in range(n) if masks[v] >> u & 1}
        assert got == expected


def test_an_abandoned_level_is_discarded_not_used():
    """A level cut short yields an overestimate of f, which must not be used.

    The clock is only consulted every 16,384 branches, so this needs a search
    big enough to reach one — a tiny instance finishes before the first check,
    which is correct behaviour and not what this is testing.
    """
    import time as _time

    # Sparse on purpose: a dense graph's first candidate already covers
    # everything and the union cut ends the search before any clock check.
    rng = random.Random(0)
    matrix = [[0] * 60 for _ in range(60)]
    for product in range(60):
        for customer in rng.sample(range(60), 2):
            matrix[customer][product] = 1
    instance = MOSPInstance.from_matrix(matrix, name="sparse")
    masks, n = _closed_masks(instance)
    order = sorted(range(n), key=lambda v: masks[v].bit_count())

    assert _f_exact(masks, n, 8, order, _time.monotonic() - 1.0) is None

    # And the bound itself keeps whatever the completed levels proved.
    result = expansion_bound(instance, max_t=8, time_budget=0.05)
    assert result.value <= _brute_force_free_upper(instance)
    assert result.cap <= 8


def _brute_force_free_upper(instance: MOSPInstance) -> int:
    """Any achievable ordering bounds the optimum from above."""
    from satisfiability.heuristics import upper_bound

    return upper_bound(instance, "cs-dfs")[0]


@pytest.mark.parametrize("name,optimum", [("GP1_0", 45), ("GP5_0", 95),
                                          ("SP2_0", 19), ("SP4_0", 53)])
def test_never_exceeds_a_published_optimum(name, optimum):
    from benchmarks.solve_parallel import find_benchmark_files

    for filepath in find_benchmark_files(INSTANCE_DIR):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for instance in instances:
            if instance.name == name:
                assert mosp_lower_bound(instance, max_t=4, time_budget=30) <= optimum
                return
    pytest.skip(f"{name} not present")


@pytest.mark.parametrize("seed", range(6))
def test_never_exceeds_a_certified_optimum_from_the_corpus(seed):
    """Sampled from the corpus; the full 6,376-instance sweep is in the report."""
    from benchmarks.solve_parallel import find_benchmark_files
    from satisfiability.mosp_solver import _solution_path

    files = find_benchmark_files(INSTANCE_DIR)
    if not files:
        pytest.skip("no benchmark instances")
    rng = random.Random(seed)
    checked = 0
    for filepath in rng.sample(files, min(12, len(files))):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for instance in instances[:6]:
            path = _solution_path(instance, SOLUTIONS)
            if not path.exists():
                continue
            optimum = json.loads(path.read_text())["mosp_value"]
            assert mosp_lower_bound(instance, max_t=4, time_budget=5) <= optimum
            checked += 1
    if not checked:
        pytest.skip("no cached solutions to check against")


# -------------------------------------------------------
# The per-node form of the same argument
# -------------------------------------------------------


@pytest.mark.parametrize("seed", range(30))
def test_expansion_prune_never_changes_a_decision(seed):
    """The per-node cut must be a pure optimisation.

    It refutes a node when even the cheapest continuation must exceed `k`. If
    that reasoning were ever wrong it would turn a satisfiable instance into a
    false refutation, which is the one error nothing downstream would catch.
    """
    from satisfiability.customer_search import decide

    instance = _random_instance(seed, max_c=9, max_p=7)
    if not instance.matrix.any():
        return
    for k in range(1, instance.n_customers + 1):
        assert (decide(instance, k, expansion_prune=True).status
                == decide(instance, k, native=False).status)


def test_expansion_prune_agrees_with_brute_force():
    for seed in range(12):
        instance = _random_instance(seed, max_c=6, max_p=5)
        if not instance.matrix.any():
            continue
        optimum = _brute_force(instance)
        from satisfiability.customer_search import decide

        if optimum > 1:
            assert decide(instance, optimum - 1, expansion_prune=True).status == "unsat"
        assert decide(instance, optimum, expansion_prune=True).status == "sat"
