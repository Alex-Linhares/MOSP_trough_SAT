"""loop0007 item 10: the root split (`paper2/solver_fix_split.py`).

The split must be the sequential search cut into pieces and nothing else. With
the memo off the two visit the same tree, so the split's node count (each child
of an expanded node, plus every task's own count) must equal the sequential
count exactly, wherever the cuts fall; with the memo on only the answer must
agree. A "sat" split must carry a witness that simulates within `k`. And the
records must say only what was found: no task ever answered "sat", and every
finished instance is a refutation of its listed `value - 1`.
"""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pytest

from mosp.instance import MOSPInstance
from paper2 import solver_fix_split as split
from paper2.search_check import BUG_A_CEX, BUG_B_CEX, DEFINITE_CEX, RUN_LOST_CEX, matrix_from_masks
from satisfiability.native import decide_native, native_available

ROOT = Path(__file__).resolve().parent.parent
needs_native = pytest.mark.skipif(not native_available(), reason="C library unavailable")

PINNED = [m for m, *_ in DEFINITE_CEX] + [BUG_A_CEX[0], BUG_B_CEX[0], RUN_LOST_CEX[0]]
CUTS = [(1, None), (4, None), (16, 40), (2, 3)]   # (initial tasks, node cap per task)


def _instances():
    out = []
    for masks in PINNED:
        m = np.array(matrix_from_masks(masks), dtype=np.int8)
        out.append(MOSPInstance(matrix=m, n_customers=m.shape[0], n_patterns=m.shape[1],
                                name="pinned"))
    rng = random.Random(20261002)
    while len(out) < len(PINNED) + 60:
        n, m, p = rng.randint(8, 28), rng.randint(5, 36), rng.choice([0.08, 0.15, 0.25])
        mat = np.array([[rng.random() < p for _ in range(m)] for _ in range(n)], dtype=np.int8)
        mat = mat[:, mat.sum(0) > 0]
        if mat.shape[1]:
            out.append(MOSPInstance(matrix=mat, n_customers=mat.shape[0],
                                    n_patterns=mat.shape[1], name="random"))
    return out


def _sequential(inst, k, flags, memo):
    kw = {x: y for x, y in flags.items() if x != "restrict"}
    return decide_native(inst, k, memo=memo, **kw)


@needs_native
@pytest.mark.parametrize("repaired", [True, False])
def test_the_split_is_the_sequential_search_cut_into_pieces(repaired):
    runs = 0
    for inst in _instances():
        for better in (False, True):
            flags = dict(split.csearch_flags(inst), better_move=better, repaired_rules=repaired)
            k = 1
            while _sequential(inst, k, flags, True).status != "sat":
                k += 1
            for kk in (k - 1, k):
                if kk < 1:
                    continue
                for memo in (False, True):
                    seq = _sequential(inst, kk, flags, memo)
                    for target, cap in CUTS:
                        got = split.split_refute(inst, kk, flags=flags, target=target,
                                                 cap=cap, memo=memo)
                        runs += 1
                        assert got["status"] == seq.status
                        if got["status"] == "unsat" and not memo:
                            assert got["nodes"] == seq.nodes
                        if got["status"] == "sat":
                            assert split.cost_of(inst, got["witness"]) <= kk
    assert runs > 1000


@needs_native
def test_a_task_starts_where_the_sequential_search_would_be():
    from satisfiability.heuristics import _neighbour_masks
    checked = 0
    for inst in _instances():
        flags = split.csearch_flags(inst)
        k = 1
        while _sequential(inst, k, flags, True).status != "sat":
            k += 1
        witness, kids = split.expand(inst, k, split.root(), flags, _neighbour_masks(inst))
        if witness is None and len(kids) > 1:
            _check_inheritance(kids)
            checked += 1
    assert checked > 10


def _check_inheritance(kids):
    # The first child inherits no old moves; later ones only earlier siblings.
    assert kids[0].seen == 0
    earlier = 0
    for child in kids:
        assert child.seen & ~earlier == 0
        earlier |= 1 << child.key[-1]


def test_the_composition_is_proved_in_lean():
    text = (ROOT / "lean" / "MOSPFormalization" / "Search" / "Split.lean").read_text()
    assert "sorry" not in text
    assert "theorem execSplit_repairedFullFilter_mospValue" in text
    assert "import MOSPFormalization.Search.Split" in \
        (ROOT / "lean" / "MOSPFormalization.lean").read_text()


def test_the_records_claim_only_refutations():
    rows = split._read_rows(split.TASKS)
    assert not [r for r in rows if r["kind"] == "task" and r["status"] == "sat"]
    listed = {t["instance_name"]: t for t in split.targets()}
    for row in split._read_rows(split.RESULTS):
        t = listed[row["instance_name"]]
        assert row["status"] == "unsat"
        assert int(row["k"]) == t["k"] == t["value"] - 1
        assert int(row["total_nodes"]) == int(row["task_nodes"]) + int(row["edges"])
