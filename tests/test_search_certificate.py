"""The search certificate: emitter fidelity, checker soundness, both historical bugs.

`learning.search_certificate` gives the complete customer search a proof
object. Two things have to hold for it to be worth anything: the emitter must
visit exactly the tree the search visits (or its certificate says nothing about
the search's answer), and the checker must reject every certificate that is not
a refutation -- including the two the project actually shipped, the 2026-09-26
close-count and rule-order bugs of `reports/better_move_bug.md` §7.
"""

import itertools
import json
import random

import pandas as pd
import pytest

from learning.search_certificate import (
    Certificate,
    certify_refutation,
    check,
    config_kwargs,
    emit,
    summarise,
)
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.customer_search import decide
from tests.test_customer_search import MINIMAL_10x13, MINIMAL_17x9

# `ens_f_n10_m20_d2_i070`, identity labelling: the C's `old-order` variant
# refuted it at its optimum of 4 in the loop0004 item 04 harness (Bug B alone).
CYCLE_10x20 = ([[1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1],
                [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]], 4)


def _brute(inst):
    return min(max_open_stacks(inst, list(perm))
               for perm in itertools.permutations(range(inst.n_patterns)))


def _random(rng, nmax=8, mmax=8):
    n, m = rng.randint(2, nmax), rng.randint(2, mmax)
    d = rng.choice([0.2, 0.3, 0.5])
    return MOSPInstance.from_matrix([[1 if rng.random() < d else 0 for _ in range(m)]
                                     for _ in range(n)], name="t")


def _sparse(rng, nmin=6, nmax=13):
    n, m = rng.randint(nmin, nmax), rng.randint(6, 16)
    rows = [[0] * m for _ in range(n)]
    for r in range(n):
        for p in rng.sample(range(m), rng.randint(1, 3)):
            rows[r][p] = 1
    return MOSPInstance.from_matrix(rows, name="s")


def _tamper(cert, edit):
    data = cert.to_json()
    edit(data)
    return Certificate.loads(json.dumps(data))


# ---------------------------------------------------------------------------
# a hand-checkable instance
# ---------------------------------------------------------------------------


def test_four_cycle_by_hand():
    """Four customers on a 4-cycle of products: optimum 3, refuted at 2 at the root.

    Each customer's neighbourhood is itself and its two cycle neighbours, so
    the first customer closed opens three stacks: every candidate costs 3 > 2
    and the root has no children, no steps and nothing to cover.
    """
    inst = MOSPInstance.from_matrix([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]],
                                    name="c4")
    assert _brute(inst) == 3
    cert = emit(inst, 2)
    assert cert.status == "unsat" and cert.branches == 0
    assert len(cert.nodes) == 1 and not cert.nodes[0].children and not cert.nodes[0].steps
    assert check(inst, cert).ok
    assert emit(inst, 3).status == "sat"
    # every customer once the first is closed is free: two branches, then free moves
    sat = emit(inst, 3)
    assert sorted(sat.order) == [0, 1, 2, 3]


def test_minimal_17x9_certificate_shape():
    inst = MOSPInstance.from_matrix(MINIMAL_17x9[0], name="m17")
    cert = emit(inst, MINIMAL_17x9[1] - 1, better_move=True, better_move_dominators=0)
    assert cert.status == "unsat"
    result = check(inst, Certificate.loads(cert.dumps()))
    assert result.ok and result.nodes == len(cert.nodes)
    sizes = cert.sizes()
    assert sizes["nodes"] == cert.branches + 1      # one record per branch plus the root
    assert sizes["gz_bytes"] < sizes["bytes"]
    assert cert.step_counts()["better"] + cert.step_counts()["subset"] + cert.step_counts()["definite"] == sizes["steps"]


# ---------------------------------------------------------------------------
# emitter fidelity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cfg", [
    pytest.param(dict(), id="default"),
    pytest.param(dict(old_move=False, memo=True), id="memo"),
    pytest.param(dict(old_move=False, memo=False), id="rules-only"),
    pytest.param(dict(subset_rule=False, definite_move=False, old_move=False, memo=False), id="plain"),
])
def test_emitter_visits_the_reference_tree(cfg):
    """Status and branch count equal `decide(native=False)` at every k; every refutation checks."""
    rng = random.Random(3)
    checked = 0
    for _ in range(40):
        inst = _random(rng)
        opt = _brute(inst)
        for k in range(max(0, opt - 2), opt + 1):
            ref = decide(inst, k, native=False, **cfg)
            cert = emit(inst, k, **cfg)
            assert (ref.status, ref.nodes) == (cert.status, cert.branches)
            if cert.status == "unsat":
                assert k < opt
                assert check(inst, Certificate.loads(cert.dumps())).ok
                checked += 1
            else:
                assert k >= opt
    assert checked > 20


def test_emitter_matches_the_c_with_theorem_2():
    """With `better_move`, the emitter is the C's tree: same status, same nodes, and Theorem 2 steps appear."""
    from satisfiability.native import decide_native

    rng = random.Random(11)
    better_steps = 0
    compared = 0
    for _ in range(60):
        inst = _sparse(rng)
        for k in range(1, inst.n_customers + 1):
            native = decide_native(inst, k, better_move=True, better_move_dominators=0, memo=False)
            if native is None:
                pytest.skip("C library unavailable")
            cert = emit(inst, k, better_move=True, better_move_dominators=0)
            assert (native.status, native.nodes) == (cert.status, cert.branches)
            compared += 1
            if cert.status == "unsat":
                better_steps += cert.step_counts()["better"]
                assert check(inst, cert).ok
    assert compared > 100 and better_steps > 0


def test_memo_references_are_emitted_and_checked():
    rng = random.Random(7)
    seen_memo = 0
    for _ in range(40):
        inst = _sparse(rng, nmin=9, nmax=12)
        # the optimum by descent through the emitter itself; memo hits need a
        # refutation deep enough to reach one closed set by two paths
        k = inst.n_customers
        while k > 0 and emit(inst, k - 1, old_move=False, memo=True).status == "sat":
            k -= 1
        cert = emit(inst, k - 1, old_move=False, memo=True) if k > 0 else None
        if cert is None or cert.status != "unsat":
            continue
        memo_nodes = [n for n in cert.nodes if n.kind == "memo"]
        if not memo_nodes:
            continue
        seen_memo += 1
        assert check(inst, cert).ok
        # a memo citing a node with a different closed set is rejected
        target = memo_nodes[0]

        def redirect(data, tid=target.id):
            for node in data["nodes"]:
                if node["id"] == tid:
                    node["memo_of"] = 0
        assert not check(inst, _tamper(cert, redirect)).ok
    assert seen_memo > 0


def test_memo_with_old_move_is_refused():
    inst = MOSPInstance.from_matrix(MINIMAL_17x9[0], name="m17")
    with pytest.raises(ValueError):
        emit(inst, 4, old_move=True, memo=True)
    cert = emit(inst, 4)
    forged = _tamper(cert, lambda d: d["config"].update(memo=True, old_move=True))
    result = check(inst, forged)
    assert not result.ok and "old move" in result.reason


# ---------------------------------------------------------------------------
# the checker rejects what is not a refutation
# ---------------------------------------------------------------------------


def test_close_count_bug_is_rejected_at_a_better_step():
    """§7 Bug A: the old close count refutes the 17 × 9 at its optimum; the checker recomputes the premise."""
    inst = MOSPInstance.from_matrix(MINIMAL_17x9[0], name="m17")
    cert = emit(inst, MINIMAL_17x9[1], better_move=True, better_move_dominators=0,
                old_close_count=True)
    assert cert.status == "unsat"                      # the false refutation, reproduced
    result = check(inst, cert)
    assert not result.ok and "better step" in result.reason and "close" in result.reason
    assert emit(inst, MINIMAL_17x9[1], better_move=True, better_move_dominators=0).status == "sat"


def test_rule_order_bug_is_rejected_as_a_covering_cycle():
    """§7 Bug B alone: every step's premise holds and the coverings form a cycle."""
    inst = MOSPInstance.from_matrix(CYCLE_10x20[0], name="ens_f_n10_m20_d2_i070")
    cert = emit(inst, CYCLE_10x20[1], better_move=True, better_move_dominators=0,
                old_rule_order=True)
    assert cert.status == "unsat"
    root = cert.nodes[0]
    rules = {tuple(step) for step in root.steps}
    assert ["better", 9, 6] in root.steps and ["subset", 6, 9] in root.steps, rules
    result = check(inst, cert)
    assert not result.ok and "cycle" in result.reason
    assert emit(inst, CYCLE_10x20[1], better_move=True, better_move_dominators=0).status == "sat"


def test_both_bugs_on_the_10x13_are_rejected():
    inst = MOSPInstance.from_matrix(MINIMAL_10x13[0], name="m10")
    cert = emit(inst, MINIMAL_10x13[1], better_move=True, better_move_dominators=0,
                old_close_count=True, old_rule_order=True)
    assert cert.status == "unsat"
    assert not check(inst, cert).ok
    for flags in (dict(old_close_count=True), dict(old_rule_order=True), dict()):
        assert emit(inst, MINIMAL_10x13[1], better_move=True, better_move_dominators=0,
                    **flags).status == "sat"


def test_corruptions_are_rejected():
    inst = MOSPInstance.from_matrix(MINIMAL_17x9[0], name="m17")
    cert = emit(inst, 4, better_move=True, better_move_dominators=0)
    assert cert.status == "unsat" and check(inst, cert).ok

    def drop_child(data):
        for node in data["nodes"]:
            if len(node.get("children", [])) >= 2:
                node["children"] = node["children"][1:]
                return
        raise AssertionError("no node with two children")

    def forge_subset(data):
        for node in data["nodes"]:
            for step in node.get("steps", []):
                if step[0] == "subset":
                    step[2] = (step[2] + 1) % 17 if (step[2] + 1) % 17 != step[1] else (step[2] + 2) % 17
                    return
        raise AssertionError("no subset step")

    def forge_better(data):
        for node in data["nodes"]:
            for step in node.get("steps", []):
                if step[0] == "better":
                    step[1], step[2] = step[2], step[1]
                    return
        raise AssertionError("no better step")

    def raise_k(data):
        data["k"] = 5

    def sat_leaf(data):
        data["nodes"][-1]["kind"] = "sat"

    for edit in (drop_child, forge_subset, forge_better, raise_k, sat_leaf):
        result = check(inst, _tamper(cert, edit))
        assert not result.ok, edit.__name__

    other = MOSPInstance.from_matrix(MINIMAL_10x13[0], name="m10")
    result = check(other, cert)
    assert not result.ok and "digest" in result.reason
    assert not check(inst, _tamper(cert, lambda d: d.update(status="sat"))).ok


def test_checker_answers_agree_with_brute_force():
    """A verified certificate at k implies optimum > k; a sat emission at k implies optimum ≤ k."""
    rng = random.Random(19)
    for _ in range(30):
        inst = _random(rng, nmax=7, mmax=7)
        opt = _brute(inst)
        for k in range(0, opt + 1):
            cert = emit(inst, k, better_move=True, better_move_dominators=0)
            if cert.status == "unsat":
                assert check(inst, cert).ok and opt > k
            else:
                assert cert.status == "sat" and opt <= k


# ---------------------------------------------------------------------------
# the study's plumbing
# ---------------------------------------------------------------------------


def test_certify_row_and_tables():
    inst = MOSPInstance.from_matrix(MINIMAL_17x9[0], name="m17")
    rows = []
    for config in ("default", "csearch", "memo"):
        row = certify_refutation(inst, MINIMAL_17x9[1], config)
        assert row["status"] == "unsat" and row["check_ok"] is True
        row.update(instance_name="m17", source_file="x", collection="t", n=17, m=9,
                   optimum=MINIMAL_17x9[1], oracle_search=MINIMAL_17x9[1])
        rows.append(row)
    assert rows[1]["better_move"] is True and rows[1]["steps_better"] >= 0
    tables = summarise(pd.DataFrame(rows))
    verdicts = tables["verdicts"].set_index("config")
    assert (verdicts["certificates verified"] == 1).all()
    assert (verdicts["oracle agrees"] == 1).all()
    assert tables["flagged"].empty
    assert set(tables["by_band"].band) == {"16–20"}
    assert config_kwargs(inst, "memo") == {"old_move": False, "memo": True}
