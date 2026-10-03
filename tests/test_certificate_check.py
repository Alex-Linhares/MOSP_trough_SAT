"""Certificates for the repaired rules (loop0008 item 05, `paper2/certificates.md`).

The emitter (`learning.search_certificate.emit(..., repaired_rules=True)`) must
visit exactly the tree the repaired search visits, and the independent checker
(`paper2/certificate_check.py`) must accept its refutations and reject every
certificate whose matching does not witness `HasDefiniteMatching` -- above all
the one the published rules emit on `DEFINITE_CEX`, which `learning`'s checker
of the published premises accepts.
"""

import ast
import copy
import gzip
import itertools
import json
import random
import subprocess
import sys
from pathlib import Path

import pytest

from learning.search_certificate import check as published_check
from learning.search_certificate import emit
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from paper2.certificate_check import check, closed_neighbourhoods, matrix_sha256
from paper2.certificates import CORRUPTIONS, _max_matching, _order_cost
from paper2.search_check import DEFINITE_CEX, matrix_from_masks
from satisfiability.customer_search import decide
from tests.test_search_certificate import CYCLE_10x20, _random, _sparse

CHECKER = Path(__file__).resolve().parent.parent / "paper2" / "certificate_check.py"

# Warwick 877 (wbo_20_10.txt), optimum 8: its repaired certificate at k = 7 has a
# definite step and better steps with two-edge matchings.
WARWICK_877 = ["0000000100", "0000001000", "0110000010", "0010010001", "0100101100",
               "0000001000", "0000010000", "0010000010", "0000000100", "0001000010",
               "0100000000", "1000000000", "0000010001", "1000100000", "0011100000",
               "1101000000", "0001011001", "0000000100", "0000100001", "1000000010"]
CSEARCH = {"better_move": True, "better_move_dominators": 0}


def _matrix(rows):
    return [[int(ch) for ch in row] for row in rows]


def _json(cert):
    return json.loads(cert.dumps())


def test_checker_imports_nothing_from_the_repository():
    tree = ast.parse(CHECKER.read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    assert imported <= {"__future__", "gzip", "hashlib", "json", "sys", "time"}, imported


def test_digest_matches_the_emitter():
    inst = MOSPInstance.from_matrix(_matrix(WARWICK_877), name="w877")
    from learning.search_certificate import matrix_sha256 as emitter_digest
    from learning.search_certificate import neighbourhoods

    assert matrix_sha256(inst.matrix.tolist()) == emitter_digest(inst)
    assert closed_neighbourhoods(inst.matrix.tolist()) == neighbourhoods(inst)


@pytest.mark.parametrize("cfg", [{}, CSEARCH, {"old_move": False, "memo": True}])
def test_emitter_visits_the_repaired_tree(cfg):
    """Status and branch count equal `decide(native=False, repaired_rules=True)`; every refutation checks."""
    rng = random.Random(23)
    refuted = 0
    for i in range(40):
        inst = _sparse(rng) if i % 2 else _random(rng, nmax=10, mmax=10)
        for k in range(1, inst.n_customers + 1):
            ref = decide(inst, k, native=False, repaired_rules=True, **cfg)
            cert = emit(inst, k, repaired_rules=True, **cfg)
            assert (ref.status, ref.nodes) == (cert.status, cert.branches)
            if cert.status != "unsat":
                break
            result = check(inst.matrix.tolist(), _json(cert))
            assert result["ok"], result["reason"]
            refuted += 1
    assert refuted > 50


def test_emitter_matches_the_c_without_memo():
    rng = random.Random(29)
    for _ in range(40):
        inst = _sparse(rng, 8, 15)
        for k in range(1, inst.n_customers + 1):
            ref = decide(inst, k, native=True, memo=False, repaired_rules=True, **CSEARCH)
            cert = emit(inst, k, repaired_rules=True, **CSEARCH)
            assert (ref.status, ref.nodes) == (cert.status, cert.branches)
            if cert.status != "unsat":
                break


def test_verified_means_optimum_above_k():
    rng = random.Random(31)
    for _ in range(25):
        inst = _random(rng, nmax=7, mmax=7)
        opt = min(max_open_stacks(inst, list(p)) for p in itertools.permutations(range(inst.n_patterns)))
        for k in range(0, opt + 1):
            cert = emit(inst, k, repaired_rules=True, **CSEARCH)
            if cert.status == "unsat":
                assert check(inst.matrix.tolist(), _json(cert))["ok"] and opt > k
            else:
                assert cert.status == "sat" and opt <= k


@pytest.mark.parametrize("idx", [0, 1])
@pytest.mark.parametrize("cfg", [{}, CSEARCH])
def test_published_rules_on_definite_cex_are_rejected(idx, cfg):
    """From S = {2} the published rules keep only q = 0 and 'refute'; a solution from S exists."""
    masks, S, q, k = DEFINITE_CEX[idx]
    matrix = [[int(v) for v in row] for row in matrix_from_masks(masks)]
    inst = MOSPInstance.from_matrix(matrix, name="cex")
    published = emit(inst, k, start=S, **cfg)
    assert published.status == "unsat"
    assert published.nodes[0].steps[0] == ["definite", q]
    assert published_check(inst, published).ok            # the published premise holds
    result = check(matrix, _json(published))
    assert not result["ok"] and "no matching witness" in result["reason"]

    # the strongest forgery: a largest matching attached to the root's definite step
    forged = _json(published)
    N = closed_neighbourhoods(matrix)
    opened = 0
    for c in range(len(masks)):
        if S >> c & 1:
            opened |= N[c]
    own = N[q] & ~opened
    freed = {d: N[d] & ~opened for d in range(len(masks))
             if d != q and not S >> d & 1 and N[d] & ~opened & ~own == 0}
    forged["nodes"][0]["steps"][0].append(_max_matching(freed))
    result = check(matrix, forged)
    assert not result["ok"] and "matching has 1 edges, open - 1 = 2" in result["reason"]

    # the repaired rules find the solution the published ones discarded
    repaired = emit(inst, k, start=S, repaired_rules=True, **cfg)
    assert repaired.status == "sat" and repaired.order[0] == 2
    assert _order_cost(N, repaired.order) <= k


@pytest.mark.parametrize("name", sorted(CORRUPTIONS))
def test_corrupted_matchings_are_rejected(name):
    matrix = _matrix(WARWICK_877)
    inst = MOSPInstance.from_matrix(matrix, name="w877")
    cert = emit(inst, 7, repaired_rules=True, **CSEARCH)
    data = _json(cert)
    assert cert.status == "unsat" and check(matrix, data)["ok"]
    bad = copy.deepcopy(data)
    CORRUPTIONS[name](bad, matrix)
    assert not check(matrix, bad)["ok"]


def test_tree_corruptions_and_the_rule_order_cycle_are_rejected():
    matrix = _matrix(WARWICK_877)
    inst = MOSPInstance.from_matrix(matrix, name="w877")
    data = _json(emit(inst, 7, repaired_rules=True, **CSEARCH))
    for edit in (lambda d: d.update(k=8), lambda d: d["nodes"][-1].update(kind="sat"),
                 lambda d: d.update(status="sat"),
                 lambda d: d["nodes"][0].update(children=d["nodes"][0]["children"][1:]),
                 lambda d: d.update(matrix_sha256="0" * 64)):
        bad = copy.deepcopy(data)
        edit(bad)
        assert not check(matrix, bad)["ok"]
    # Bug B (rule order), reproduced under the repaired premises: every premise
    # holds, matching included, and the covering relation cycles
    inst = MOSPInstance.from_matrix(CYCLE_10x20[0], name="cycle")
    cert = emit(inst, CYCLE_10x20[1], repaired_rules=True, old_rule_order=True, **CSEARCH)
    assert cert.status == "unsat"
    result = check(CYCLE_10x20[0], _json(cert))
    assert not result["ok"] and "covering cycle" in result["reason"]


def test_command_line_bundle(tmp_path):
    matrix = _matrix(WARWICK_877)
    inst = MOSPInstance.from_matrix(matrix, name="w877")
    bundle = tmp_path / "w877.json.gz"
    bundle.write_bytes(gzip.compress(json.dumps(
        {"matrix": matrix, "certificate": _json(emit(inst, 7, repaired_rules=True))}).encode()))
    out = subprocess.run([sys.executable, str(CHECKER), str(bundle)], capture_output=True, text=True)
    assert out.returncode == 0 and '"ok": true' in out.stdout and "MOSP > 7" in out.stdout
