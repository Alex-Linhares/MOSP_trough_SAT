"""Guards on the complete customer search and its dominance rules.

This search is the only thing in the project that produces a *refutation*
without a SAT solver, so a wrong dominance rule here does not merely lose a
solution -- it manufactures a lower bound that is false, and the corpus records
it as certified. That is the failure this file exists to prevent.

Each rule is therefore varied one at a time against exhaustive enumeration: the
point at which the answer flips from unsat to sat must be the true optimum under
every combination. The medium-instance cross-check against the SAT solver
matters for the same reason -- it shares no code with this search, so agreement
is evidence rather than a restatement.
"""

import itertools
import random

import pytest

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.customer_search import decide, solve
from satisfiability.heuristics import product_order_from_customers

COMBINATIONS = [
    pytest.param(dict(subset_rule=False, definite_move=False, memo=False), id="plain"),
    pytest.param(dict(subset_rule=False, definite_move=False, memo=True), id="memo"),
    pytest.param(dict(subset_rule=True, definite_move=False, memo=False), id="subset"),
    pytest.param(dict(subset_rule=False, definite_move=True, memo=False), id="definite"),
    pytest.param(dict(subset_rule=True, definite_move=True, memo=True), id="all"),
    pytest.param(dict(subset_rule=False, definite_move=False, memo=False,
                      old_move=True), id="old-move"),
    pytest.param(dict(subset_rule=True, definite_move=True, memo=False,
                      old_move=True), id="old-move+rules"),
]


def _brute(inst):
    if inst.n_patterns == 0:
        return 0
    return min(max_open_stacks(inst, list(perm))
               for perm in itertools.permutations(range(inst.n_patterns)))


def _random_instance(rng, max_customers=7, max_patterns=7):
    n_customers = rng.randint(1, max_customers)
    n_patterns = rng.randint(1, max_patterns)
    density = rng.choice([0.2, 0.4, 0.6, 0.8])
    rows = [[1 if rng.random() < density else 0 for _ in range(n_patterns)]
            for _ in range(n_customers)]
    return MOSPInstance.from_matrix(rows, name="t")


@pytest.mark.parametrize("rules", COMBINATIONS)
def test_the_flip_point_is_the_optimum(rules):
    """Under every combination of dominance rules, unsat below and sat at."""
    rng = random.Random(21)
    for _ in range(60):
        inst = _random_instance(rng)
        optimum = _brute(inst)
        for k in range(optimum + 2):
            answer = decide(inst, k, **rules)
            expected = "unsat" if k < optimum else "sat"
            assert answer.status == expected, (
                f"k={k}, optimum={optimum}, got {answer.status}")


@pytest.mark.parametrize("rules", COMBINATIONS)
def test_every_witness_achieves_its_k(rules):
    """A closing order is only worth having if its product sequence holds up."""
    rng = random.Random(22)
    for _ in range(60):
        inst = _random_instance(rng)
        optimum = _brute(inst)
        answer = decide(inst, optimum, **rules)
        assert answer.status == "sat"
        ordering = product_order_from_customers(inst, answer.order)
        assert sorted(ordering) == list(range(inst.n_patterns))
        assert max_open_stacks(inst, ordering) <= optimum


def test_old_move_and_the_memo_are_refused_together():
    """A failure found by old-move pruning depends on the path to the state, and
    the memo is keyed on the state alone. Combining them would refute states
    that are not refuted, so the combination is rejected rather than risked."""
    inst = MOSPInstance.from_matrix([[1, 1], [0, 1]], name="clash")
    with pytest.raises(ValueError, match="cannot both be on"):
        decide(inst, 1, old_move=True, memo=True)


def test_the_restricted_search_never_claims_a_refutation():
    """`ub_MOSP` discards branches it cannot justify, so exhausting what is left
    proves nothing. It must say so rather than report unsat."""
    rng = random.Random(23)
    saw_unknown = False
    for _ in range(60):
        inst = _random_instance(rng)
        optimum = _brute(inst)
        for k in range(optimum + 2):
            answer = decide(inst, k, restrict=True)
            assert answer.status != "unsat"
            if answer.status == "unknown":
                saw_unknown = True
                assert k < optimum or True  # unknown is allowed anywhere
        assert decide(inst, optimum, restrict=True).status in ("sat", "unknown")
    assert saw_unknown, "restriction never bit; the test proves nothing"


def test_an_exhausted_budget_is_unknown_not_unsat():
    """A budget abort has refuted nothing, and must never be reported as if it
    had -- including into the memo, where it would poison later states.

    The instances here are larger than brute force reaches, because on small
    ones the dominance rules refute before branching at all and a node budget
    has nothing to bite on.
    """
    rng = random.Random(25)
    checked = 0
    for _ in range(25):
        n_patterns = rng.randint(10, 16)
        rows = [[1 if rng.random() < 0.3 else 0 for _ in range(n_patterns)]
                for _ in range(rng.randint(12, 20))]
        inst = MOSPInstance.from_matrix(rows, name="budget")

        settled = solve(inst)
        assert settled.proved
        if settled.value == 0:
            continue
        full = decide(inst, settled.value - 1)
        assert full.status == "unsat"
        if full.nodes < 2:
            continue  # refuted before branching; no budget can bite
        checked += 1
        assert decide(inst, settled.value - 1, max_nodes=1).status == "unknown"
    assert checked > 5, "no instance needed real search; the test proves nothing"


def test_free_customers_are_closed_without_being_branched_on():
    """A customer whose products are all made costs nothing to close. Leaving it
    open would inflate the count and lose optima."""
    # c0 needs p0; c1 needs p0 and p1; c2 needs p1. Closing c1 opens all three.
    inst = MOSPInstance.from_matrix([[1, 0], [1, 1], [0, 1]], name="free")
    answer = decide(inst, 2)
    assert answer.status == "sat"
    assert sorted(answer.order) == [0, 1, 2]
    assert _brute(inst) == 2


def test_solve_descends_to_the_optimum_and_says_how():
    rng = random.Random(24)
    for _ in range(40):
        inst = _random_instance(rng)
        optimum = _brute(inst)
        got = solve(inst)
        assert got.value == optimum
        assert got.proof in ("refutation", "bound")
        if got.order:
            ordering = product_order_from_customers(inst, got.order)
            assert max_open_stacks(inst, ordering) == optimum


def test_solve_reports_no_proof_when_it_runs_out():
    """An unfinished descent returns its bound with `proof` empty, so a caller
    cannot mistake it for a certified optimum."""
    matrix = [[1, 1, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0], [0, 0, 1, 1, 0, 0],
              [0, 0, 0, 1, 1, 0], [0, 0, 0, 0, 1, 1], [1, 0, 0, 0, 0, 1]]
    inst = MOSPInstance.from_matrix(matrix, name="stopped")
    got = solve(inst, upper=inst.n_customers, max_nodes=0)
    assert got.proof == ""
    assert not got.proved


@pytest.mark.parametrize("seed", range(3))
def test_agrees_with_the_sat_solver_beyond_brute_force(seed):
    """Instances too large to enumerate, decided by two unrelated algorithms."""
    from satisfiability.mosp_solver import solve_mosp_sat

    rng = random.Random(700 + seed)
    for _ in range(8):
        n_customers = rng.randint(8, 14)
        n_patterns = rng.randint(6, 12)
        density = rng.choice([0.2, 0.4, 0.6])
        rows = [[1 if rng.random() < density else 0 for _ in range(n_patterns)]
                for _ in range(n_customers)]
        inst = MOSPInstance.from_matrix(rows, name="x")

        sat_value, _ = solve_mosp_sat(inst, solutions_dir=None)
        got = solve(inst)
        assert got.proved
        assert got.value == sat_value
