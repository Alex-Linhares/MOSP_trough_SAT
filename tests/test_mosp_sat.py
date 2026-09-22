"""Tests for the direct MOSP-to-SAT solver."""

import random

import pytest

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.mosp_solver import solve_mosp_sat, _lower_bound, _upper_bound


# -------------------------------------------------------
# Trivial / small instances
# -------------------------------------------------------


def test_empty_instance():
    """No patterns → MOSP = 0."""
    inst = MOSPInstance.from_matrix([[]], name="empty")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    assert val == 0
    assert ordering == []


def test_single_pattern_single_customer():
    """One pattern, one customer → MOSP = 1."""
    inst = MOSPInstance.from_matrix([[1]], name="single")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    assert val == 1
    assert ordering == [0]


def test_single_pattern_no_customer():
    """One pattern, one customer row but customer doesn't need it → MOSP = 0."""
    inst = MOSPInstance.from_matrix([[0]], name="no_demand")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    assert val == 0
    assert ordering == [0]


def test_two_patterns_one_customer():
    """One customer needs both patterns → MOSP = 1."""
    inst = MOSPInstance.from_matrix([[1, 1]], name="two_pats")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    assert val == 1
    assert len(ordering) == 2
    assert set(ordering) == {0, 1}


def test_two_patterns_two_independent_customers():
    """Two customers each needing different patterns → MOSP = 1."""
    matrix = [[1, 0], [0, 1]]
    inst = MOSPInstance.from_matrix(matrix, name="independent2")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    assert val == 1
    assert set(ordering) == {0, 1}


# -------------------------------------------------------
# Classic small instances
# -------------------------------------------------------


def test_independent_patterns():
    """No patterns share customers → MOSP = 1."""
    matrix = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="independent")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    assert val == 1
    assert set(ordering) == {0, 1, 2}


def test_all_shared():
    """All patterns share all customers → MOSP = n_customers."""
    matrix = [
        [1, 1, 1],
        [1, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="all_shared")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    assert val == 2
    actual = max_open_stacks(inst, ordering)
    assert actual == val


def test_chain_patterns():
    """Chain: C0 needs P0,P1; C1 needs P1,P2; C2 needs P2,P3 → MOSP = 2."""
    matrix = [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="chain")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    assert val == 2
    actual = max_open_stacks(inst, ordering)
    assert actual == val


def test_cycle_patterns():
    """Cycle: each customer needs adjacent pair → MOSP = 3."""
    matrix = [
        [1, 1, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 1, 1],
        [1, 0, 0, 0, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="cycle5")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    # Cycle graph has pathwidth 2, so MOSP via agreement = 3
    # Direct encoding should also find 3
    assert val == 3
    actual = max_open_stacks(inst, ordering)
    assert actual == val


def test_star_patterns():
    """Star: one customer needs all patterns → MOSP = 1."""
    matrix = [
        [1, 1, 1, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="star")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    assert val == 1
    assert len(ordering) == 5


def test_complete_bipartite():
    """Every customer needs every pattern → MOSP = n_customers."""
    matrix = [
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="complete_bip")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    assert val == 3
    actual = max_open_stacks(inst, ordering)
    assert actual == val


# -------------------------------------------------------
# Bounds tests
# -------------------------------------------------------


def test_lower_bound():
    """Lower bound should be max |customers(p)| over all patterns."""
    matrix = [
        [1, 1, 0],
        [1, 0, 1],
        [0, 0, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="lb_test")
    lb = _lower_bound(inst)
    # Pattern 0: customers {0,1} → 2
    # Pattern 1: customers {0} → 1
    # Pattern 2: customers {1,2} → 2
    assert lb == 2


def test_upper_bound():
    """Upper bound from greedy should be >= optimal."""
    matrix = [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="ub_test")
    ub, ordering = _upper_bound(inst)
    assert ub >= 2  # optimal is 2
    actual = max_open_stacks(inst, ordering)
    assert actual == ub


# -------------------------------------------------------
# Verification consistency
# -------------------------------------------------------


def test_ordering_is_valid_permutation():
    """Ordering should be a valid permutation of 0..m-1."""
    matrix = [
        [1, 1, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="perm_check")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    assert len(ordering) == 5
    assert set(ordering) == set(range(5))


def test_sat_value_matches_simulation():
    """SAT result should match simulation on the returned ordering."""
    matrix = [
        [1, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [1, 1, 0, 0, 1],
        [0, 0, 1, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="sim_check")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    actual = max_open_stacks(inst, ordering)
    assert actual == val


# -------------------------------------------------------
# Cross-validation against agreement graph solver
# -------------------------------------------------------


def test_cross_validate_against_agreement_solver():
    """SAT direct encoding should match or beat agreement graph solver on small instances."""
    from mosp.solver import solve_mosp as solve_agreement

    test_matrices = [
        # Chain
        [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]],
        # Independent
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        # All shared
        [[1, 1, 1], [1, 1, 1]],
        # Cycle
        [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]],
    ]

    for i, matrix in enumerate(test_matrices):
        inst = MOSPInstance.from_matrix(matrix, name=f"cross_{i}")
        sat_val, sat_ordering = solve_mosp_sat(inst, solutions_dir=None)
        agr_sol = solve_agreement(inst)

        actual_sat = max_open_stacks(inst, sat_ordering)
        actual_agr = max_open_stacks(inst, agr_sol.ordering)

        # Direct SAT should be at least as good as agreement graph
        assert actual_sat <= actual_agr, (
            f"Instance {i}: SAT={actual_sat} > agreement={actual_agr}"
        )


def test_cross_validate_random_small():
    """Cross-validate on small random instances against brute force."""
    rng = random.Random(42)

    for trial in range(15):
        n_cust = rng.randint(2, 5)
        n_pats = rng.randint(2, 6)
        density = rng.uniform(0.2, 0.6)

        matrix = []
        for _ in range(n_cust):
            row = [1 if rng.random() < density else 0 for _ in range(n_pats)]
            matrix.append(row)

        inst = MOSPInstance.from_matrix(matrix, name=f"random_{trial}")

        # Skip if no customer needs any pattern
        if all(all(v == 0 for v in row) for row in matrix):
            continue

        sat_val, sat_ordering = solve_mosp_sat(inst, solutions_dir=None)
        actual = max_open_stacks(inst, sat_ordering)
        assert actual == sat_val, f"Trial {trial}: reported={sat_val}, simulated={actual}"

        # Brute force: try all permutations for small m
        if n_pats <= 6:
            from itertools import permutations
            best_brute = float("inf")
            for perm in permutations(range(n_pats)):
                v = max_open_stacks(inst, list(perm))
                best_brute = min(best_brute, v)

            assert sat_val == best_brute, (
                f"Trial {trial}: SAT={sat_val}, brute_force={best_brute}"
            )


# -------------------------------------------------------
# Medium-sized instances (SAT-only territory)
# -------------------------------------------------------


def test_medium_chain_15():
    """15-pattern chain → MOSP = 2."""
    n = 14  # customers
    m = 15  # patterns
    matrix = [[0] * m for _ in range(n)]
    for c in range(n):
        matrix[c][c] = 1
        matrix[c][c + 1] = 1
    inst = MOSPInstance.from_matrix(matrix, name="chain15")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    assert val == 2
    actual = max_open_stacks(inst, ordering)
    assert actual == val


def test_medium_dense_10x10():
    """10x10 instance with density ~0.4."""
    rng = random.Random(123)
    n, m = 10, 10
    matrix = []
    for _ in range(n):
        row = [1 if rng.random() < 0.4 else 0 for _ in range(m)]
        matrix.append(row)
    inst = MOSPInstance.from_matrix(matrix, name="dense10")
    val, ordering = solve_mosp_sat(inst, solutions_dir=None)
    actual = max_open_stacks(inst, ordering)
    assert actual == val
    # Verify it's a valid permutation
    assert set(ordering) == set(range(m))


# -------------------------------------------------------
# max_stacks parameter
# -------------------------------------------------------


def test_max_stacks_parameter():
    """max_stacks should limit the search."""
    matrix = [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="max_stacks")
    # Optimal is 2, asking with max_stacks=2 should still find it
    val, ordering = solve_mosp_sat(inst, max_stacks=2, solutions_dir=None)
    assert val == 2

    # Asking with max_stacks=3 should also find optimal
    val2, ordering2 = solve_mosp_sat(inst, max_stacks=3, solutions_dir=None)
    assert val2 == 2


# -------------------------------------------------------
# Published optimal values (regression tests)
# -------------------------------------------------------


@pytest.fixture
def wilson_gp50():
    """Load GP1-4 (50x50) from Wilson benchmarks."""
    from pathlib import Path
    path = Path("benchmarks/instances/ChallengeInstances2005/Wilson/gp50by50.txt")
    if not path.exists():
        pytest.skip("Wilson GP50 benchmark file not found")
    return MOSPInstance.from_benchmark_file(path)


@pytest.fixture
def wilson_gp100():
    """Load GP5-8 (100x100) from Wilson benchmarks."""
    from pathlib import Path
    path = Path("benchmarks/instances/ChallengeInstances2005/Wilson/gp100by100.txt")
    if not path.exists():
        pytest.skip("Wilson GP100 benchmark file not found")
    return MOSPInstance.from_benchmark_file(path)


def test_gp1_published_optimal(wilson_gp50):
    """GP1 (50×50): published optimal = 45."""
    inst = wilson_gp50[0]
    val, ordering = solve_mosp_sat(inst, max_stacks=46, solutions_dir=None)
    actual = max_open_stacks(inst, ordering)
    assert actual == val
    assert val <= 45, f"GP1: got {val}, published optimal is 45"


def test_gp4_published_optimal(wilson_gp50):
    """GP4 (50×50): published optimal = 30."""
    if len(wilson_gp50) < 4:
        pytest.skip("GP4 not found in benchmark file")
    inst = wilson_gp50[3]
    val, ordering = solve_mosp_sat(inst, max_stacks=31, solutions_dir=None)
    actual = max_open_stacks(inst, ordering)
    assert actual == val
    assert val <= 30, f"GP4: got {val}, published optimal is 30"


# -------------------------------------------------------
# Open-stack encoding: linear vs pairwise
# -------------------------------------------------------


def _sat_optimum(inst, pairwise):
    """Smallest k for which the decision encoding is satisfiable."""
    from pysat.solvers import Cadical153

    from satisfiability.mosp_encoding import encode_mosp_decision

    for k in range(inst.n_customers + 1):
        cnf, _, _ = encode_mosp_decision(inst, k, pairwise_open_stacks=pairwise)
        with Cadical153(bootstrap_with=cnf.clauses) as solver:
            if solver.solve():
                return k
    return None


def _brute_force(inst):
    """Optimal MOSP by exhaustive search over all orderings."""
    import itertools

    return min(
        max_open_stacks(inst, list(perm))
        for perm in itertools.permutations(range(inst.n_patterns))
    )


@pytest.mark.parametrize("seed", range(12))
def test_linear_encoding_matches_pairwise_and_brute_force(seed):
    """The O(|P_c|) open-stack encoding agrees with the O(|P_c|^2) one.

    Both are checked against exhaustive search, so this pins the encodings to
    the actual optimum rather than merely to each other.
    """
    rng = random.Random(seed)
    n_customers = rng.randint(2, 5)
    n_patterns = rng.randint(2, 5)
    matrix = [
        [rng.randint(0, 1) for _ in range(n_patterns)] for _ in range(n_customers)
    ]
    if not any(any(row) for row in matrix):
        pytest.skip("degenerate all-zero instance")

    inst = MOSPInstance.from_matrix(matrix, name=f"rand{seed}")
    expected = _brute_force(inst)
    assert _sat_optimum(inst, pairwise=False) == expected
    assert _sat_optimum(inst, pairwise=True) == expected


@pytest.mark.parametrize("density", [0.8, 1.0])
def test_linear_encoding_on_dense_instances(density):
    """Dense instances are where the two encodings diverge most in size."""
    rng = random.Random(int(density * 100))
    n_patterns = 6
    matrix = [
        [1 if rng.random() < density else 0 for _ in range(n_patterns)]
        for _ in range(5)
    ]
    if not any(any(row) for row in matrix):
        pytest.skip("degenerate all-zero instance")

    inst = MOSPInstance.from_matrix(matrix, name="dense")
    expected = _brute_force(inst)
    assert _sat_optimum(inst, pairwise=False) == expected
    assert _sat_optimum(inst, pairwise=True) == expected


def _clause_counts(n):
    """Clause counts for both encodings on the complete n x n instance."""
    from satisfiability.mosp_encoding import encode_mosp_decision

    # Every customer requires every pattern: the worst case for pairwise.
    inst = MOSPInstance.from_matrix([[1] * n for _ in range(n)], name="complete")
    linear, _, _ = encode_mosp_decision(inst, 5, pairwise_open_stacks=False)
    pairwise, _, _ = encode_mosp_decision(inst, 5, pairwise_open_stacks=True)
    return len(linear.clauses), len(pairwise.clauses)


def test_linear_encoding_is_smaller_on_dense_instances():
    """The linear encoding must actually be smaller, not just correct."""
    linear, pairwise = _clause_counts(30)
    assert linear < pairwise / 5


def test_linear_encoding_advantage_grows_with_size():
    """The saving is asymptotic: the pairwise term is the one that blows up.

    Pairwise emits |P_c| * (|P_c| - 1) clauses per (customer, step) against the
    linear encoding's 2 * |P_c| + 1, so the ratio should grow roughly linearly
    in the number of patterns. This is what makes dense 100x100 instances such
    as GP5 tractable to encode at all.
    """
    ratios = []
    for n in (10, 20, 40):
        linear, pairwise = _clause_counts(n)
        ratios.append(pairwise / linear)

    assert ratios == sorted(ratios), f"ratio should grow with n, got {ratios}"
    assert ratios[-1] > 2 * ratios[0]


# -------------------------------------------------------
# The reducing decision procedure
# -------------------------------------------------------


def _brute_optimum(inst):
    import itertools
    return min(max_open_stacks(inst, list(perm))
               for perm in itertools.permutations(range(inst.n_patterns)))


@pytest.mark.parametrize("seed", range(4))
def test_decide_mosp_agrees_with_brute_force(seed):
    """`decide_mosp` decomposes and drops dominated patterns before encoding.
    Both reductions claim to preserve the optimum, so the threshold at which it
    flips from unsat to sat must be the true optimum, and its witness must
    achieve the k it was asked for."""
    from satisfiability.mosp_solver import decide_mosp

    rng = random.Random(500 + seed)
    for _ in range(12):
        n_patterns = rng.randint(1, 6)
        matrix = [[1 if rng.random() < 0.35 else 0 for _ in range(n_patterns)]
                  for _ in range(rng.randint(1, 6))]
        inst = MOSPInstance.from_matrix(matrix, name="decide")
        optimum = _brute_optimum(inst)

        for k in range(0, optimum + 2):
            ordering = decide_mosp(inst, k)
            if k < optimum:
                assert ordering is None, f"k={k} below optimum {optimum} but sat"
            else:
                assert ordering is not None, f"k={k} at or above optimum but unsat"
                assert sorted(ordering) == list(range(inst.n_patterns))
                assert max_open_stacks(inst, ordering) <= k


def test_decide_mosp_handles_a_decomposable_instance():
    """Two blocks sharing nothing: the answer is the larger block's, and the
    witness has to cover both components' products."""
    from satisfiability.mosp_solver import decide_mosp

    matrix = [
        [1, 1, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 1, 1],
        [0, 0, 1, 0, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="split")
    optimum = _brute_optimum(inst)

    assert decide_mosp(inst, optimum - 1) is None
    ordering = decide_mosp(inst, optimum)
    assert sorted(ordering) == list(range(5))
    assert max_open_stacks(inst, ordering) <= optimum


def test_decide_mosp_covers_products_nobody_needs():
    """A column of zeros belongs to no component and still has to be scheduled."""
    from satisfiability.mosp_solver import decide_mosp

    inst = MOSPInstance.from_matrix([[1, 0, 1], [0, 0, 1]], name="free")
    ordering = decide_mosp(inst, 2)
    assert sorted(ordering) == [0, 1, 2]


# -------------------------------------------------------
# The default decision procedure
# -------------------------------------------------------


def test_default_procedure_is_the_customer_search():
    """Flipped 2026-09-22 on the evidence in reports/learned_search.md §3."""
    from satisfiability.mosp_solver import DEFAULT_PROCEDURE

    assert DEFAULT_PROCEDURE == "csearch"


@pytest.mark.parametrize("seed", range(8))
def test_exact_agrees_with_the_sat_path(seed):
    """Two complete procedures must return the same optimum, or one is wrong."""
    import random

    from satisfiability.mosp_solver import solve_mosp_exact

    rng = random.Random(seed)
    n_c, n_p = rng.randint(3, 8), rng.randint(3, 7)
    matrix = [[rng.randint(0, 1) for _ in range(n_p)] for _ in range(n_c)]
    for row in matrix:
        if not any(row):
            row[rng.randrange(n_p)] = 1
    inst = MOSPInstance.from_matrix(matrix, name=f"exact{seed}")

    value, ordering = solve_mosp_exact(inst, solutions_dir=None)
    assert sorted(ordering) == list(range(inst.n_patterns))
    assert value == max_open_stacks(inst, ordering)
    assert value == solve_mosp_sat(inst, solutions_dir=None)[0]


def test_exact_can_still_be_asked_for_the_sat_path():
    inst = MOSPInstance.from_matrix([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]],
                                    name="viasat")
    from satisfiability.mosp_solver import solve_mosp_exact

    assert (solve_mosp_exact(inst, procedure="sat", solutions_dir=None)[0]
            == solve_mosp_sat(inst, solutions_dir=None)[0])


def test_unknown_procedure_is_refused_by_name():
    from satisfiability.mosp_solver import solve_mosp_exact

    inst = MOSPInstance.from_matrix([[1, 0], [0, 1]], name="bad")
    with pytest.raises(ValueError, match="unknown procedure"):
        solve_mosp_exact(inst, procedure="dfs", solutions_dir=None)
