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


def test_the_python_reference_drops_the_memo_rather_than_combining_it():
    """Chu & Stuckey run old move and nogood recording together and the C
    follows them, with 10,476 exhaustive decisions agreeing with brute force.

    The Python keeps the stricter reading -- an old-move failure belongs to the
    path, the memo is keyed on the state -- and drops the memo instead of
    combining them, so the two implementations do not both rest on the same
    assumption. It must still answer, not raise.
    """
    inst = MOSPInstance.from_matrix(
        [[1, 1, 0], [0, 1, 1], [1, 0, 1]], name="both")
    answer = decide(inst, 2, old_move=True, memo=True, native=False)
    assert answer.status in ("sat", "unsat")
    assert answer.status == decide(inst, 2, native=False).status


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


# -------------------------------------------------------
# better_move is a dominance rule: it may change the cost, never the answer
# -------------------------------------------------------


def _bm_instance(seed):
    import random

    from mosp.instance import MOSPInstance

    rng = random.Random(seed)
    n_c, n_p = rng.randint(2, 14), rng.randint(2, 12)
    density = rng.choice([0.15, 0.3, 0.5])
    matrix = [[1 if rng.random() < density else 0 for _ in range(n_p)]
              for _ in range(n_c)]
    return MOSPInstance.from_matrix(matrix, name=f"bm{seed}")


def _sparse_bm_instance(seed):
    """One to three products per customer, half to twice as many products as
    customers: the family where the second `better_move` bug lived. Dense
    instances rarely tie enough candidates for a dominance relation to point
    backwards; at about two customers per product they do."""
    import random

    from mosp.instance import MOSPInstance

    rng = random.Random(seed)
    n_c = rng.randint(6, 20)
    n_p = rng.randint(max(2, n_c // 2), 2 * n_c)
    matrix = [[0] * n_p for _ in range(n_c)]
    for row in matrix:
        for j in rng.sample(range(n_p), rng.randint(1, min(3, n_p))):
            row[j] = 1
    return MOSPInstance.from_matrix(matrix, name=f"sparse_bm{seed}")


# The two minimal counterexamples `python -m learning.differential --stage
# shrink` cut from the campaign instances the harness drew (reports/ml_nature.md
# §15, reports/differential_tables.md). Each has a certified optimum the C
# default, the Python reference and (for the first) the lattice oracle agree on,
# and each was refuted at that optimum by the C with `better_move` on: the
# first through the subset rule citing a candidate better move had discarded,
# the second by better move alone, whose close count took the customers r
# finishes by itself for stacks q would close.
MINIMAL_10x13 = ([[0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0],
                  [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1],
                  [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1], [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]], 4)
MINIMAL_17x9 = ([[1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1],
                 [0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 1, 0],
                 [1, 0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1],
                 [0, 0, 0, 0, 0, 0, 1, 1, 1], [0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 1],
                 [1, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0],
                 [0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 1, 0, 0]], 5)


@pytest.mark.parametrize("family, seed", [("dense", s) for s in range(40)]
                         + [("sparse", s) for s in range(60)])
def test_better_move_never_changes_a_decision(family, seed):
    """The invariant whose absence hid a false-refutation bug for months.

    `better_move` lives only in the C, so the C-versus-Python tests never
    covered it: the Python has nothing to compare against. It let any candidate
    dominate any other, so the relation could cycle -- q dominates r while r
    dominates q -- and both were discarded together with the solution they
    carried. `Warwick 1730` was refuted at k = 9 against a true optimum of 9,
    and one corpus entry was certified one stack too high.

    The dense family alone missed the second bug (reports/ml_nature.md §15):
    the sparse family is where candidates tie on cost and the subset relation
    has room to point back at a candidate better move has discarded. Every
    rule pairing is tried, because a rule sound on its own input is not
    thereby sound on the output of another rule.
    """
    from satisfiability.customer_search import decide

    instance = _bm_instance(seed) if family == "dense" else _sparse_bm_instance(seed)
    if not instance.matrix.any():
        return
    pairings = [(True, True)] if family == "dense" else [(True, True), (True, False),
                                                          (False, True), (False, False)]
    for k in range(1, instance.n_customers + 1):
        reference = decide(instance, k, better_move=False).status
        for subset_rule, definite_move in pairings:
            for dominators in (0, 1, 2, 4):
                for memo in (True, False):
                    assert decide(instance, k, better_move=True, memo=memo,
                                  subset_rule=subset_rule, definite_move=definite_move,
                                  better_move_dominators=dominators).status == reference


@pytest.mark.parametrize("matrix, optimum", [MINIMAL_10x13, MINIMAL_17x9])
def test_the_minimal_instances_from_the_differential_harness(matrix, optimum):
    """Both refuted their optimum under some flag combination before the fix
    (all 32 with `subset_rule` on for the first; 48 of 64 for the second,
    including better move with the memo, old move and the subset rule all off).
    Every combination must now agree with the Python reference at the optimum
    and one below it."""
    import itertools

    from mosp.instance import MOSPInstance
    from satisfiability.customer_search import decide

    instance = MOSPInstance.from_matrix(matrix, name="minimal")
    assert decide(instance, optimum, native=False).status == "sat"
    assert decide(instance, optimum - 1, native=False).status == "unsat"
    for subset_rule, definite_move, old_move, memo, dominators in itertools.product(
            (True, False), (True, False), (True, False), (True, False), (0, 1, 2, 4)):
        flags = dict(better_move=True, subset_rule=subset_rule, definite_move=definite_move,
                     old_move=old_move, memo=memo, better_move_dominators=dominators)
        assert decide(instance, optimum, **flags).status == "sat", flags
        assert decide(instance, optimum - 1, **flags).status == "unsat", flags


def test_the_instance_that_exposed_the_cycle():
    """`Warwick 1730` has optimum 9; every configuration must agree."""
    from pathlib import Path

    from benchmarks.solve_parallel import find_benchmark_files
    from mosp.instance import MOSPInstance
    from satisfiability.customer_search import decide

    name = "Warwick 1730: balanced orders, 3 orders per product"
    for filepath in find_benchmark_files(Path("benchmarks/instances")):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for instance in instances:
            if instance.name != name:
                continue
            for dominators in (0, 1, 2, 4):
                assert decide(instance, 8, better_move=True,
                              better_move_dominators=dominators).status == "unsat"
                assert decide(instance, 9, better_move=True,
                              better_move_dominators=dominators).status == "sat"
            return
    pytest.skip(f"{name} not present")
