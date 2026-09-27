"""The `better_move` fix variants (loop0004 item 04, `learning/fix_cost.py`,
`reports/ml_nature.md` §31).

Two flags on the C search, `old_close_count` and `old_rule_order`, each
*revert* one change of the 2026-09-26 fix (`reports/better_move_bug.md` §7).
They exist to be measured, and they are unsound by construction, so the usual
"a flag never changes a status" invariant is deliberately false for them; what
must hold instead is:

- the default path is byte-for-byte unchanged: no flag, both flags off, and
  the old entry points visit the same nodes and return the same witness, and
  the default reproduces the node counts recorded before the flags existed;
- with `better_move` off the flags are no-ops (they live inside the rule);
- the flags reproduce the *documented* behaviour on the harness's drawn
  instances: the pre-fix variant refutes both minimal counterexamples at
  their optimum and reproduces the pre-fix node counts recorded in the
  campaign results; the close-count revert alone refutes the 17 × 9 instance
  (§7's Bug A) and no flag combination changes a status on the 10 × 13
  instance except both together;
- `bm-first` (`subset_after_better_move`), the candidate composition that is
  not a revert, never changes a status against the Python reference;
- the study's arithmetic is right on hand-built rows.
"""

import random

import numpy as np
import pandas as pd
import pytest

from mosp.instance import MOSPInstance
from satisfiability.customer_search import decide
from satisfiability.native import decide_native, native_available

needs_native = pytest.mark.skipif(not native_available(),
                                  reason="the C search did not build here")

CSEARCH = {"better_move": True, "better_move_dominators": 0}
FLAGS = ({}, {"old_close_count": True}, {"old_rule_order": True},
         {"old_close_count": True, "old_rule_order": True})
BM_FIRST = {"subset_after_better_move": True}


def _random(rng, max_customers=12, max_patterns=10):
    n = rng.randint(2, max_customers)
    m = rng.randint(1, max_patterns)
    per_customer = rng.choice([1, 2, 3])
    rows = [[0] * m for _ in range(n)]
    for row in rows:
        for p in rng.sample(range(m), min(per_customer, m)):
            row[p] = 1
    return MOSPInstance.from_matrix(rows, name="t")


def _minimal():
    from tests.test_customer_search import MINIMAL_10x13, MINIMAL_17x9

    return MINIMAL_10x13, MINIMAL_17x9


@needs_native
def test_the_default_is_unchanged_by_naming_the_flags_off():
    """No flag, both flags named off, and `cs_decide_fan` / `cs_decide` are the
    same search: status, nodes and witness."""
    import ctypes

    from satisfiability.heuristics import _neighbour_masks
    from satisfiability.native import _load

    lib = _load()
    lib.cs_decide_fan.restype = ctypes.c_int
    lib.cs_decide_fan.argtypes = lib.cs_decide_variant.argtypes[:13] + lib.cs_decide_variant.argtypes[14:]
    lib.cs_decide.restype = ctypes.c_int
    lib.cs_decide.argtypes = lib.cs_decide_variant.argtypes[:12] + lib.cs_decide_variant.argtypes[14:]

    def old_entry(inst, k, bm):
        n = inst.n_customers
        packed = (ctypes.c_uint64 * (2 * n))()
        for i, mask in enumerate(_neighbour_masks(inst)):
            packed[2 * i] = mask & ((1 << 64) - 1)
            packed[2 * i + 1] = (mask >> 64) & ((1 << 64) - 1)
        out = []
        for fn, extra in ((lib.cs_decide_fan, (0,)), (lib.cs_decide, ())):
            path = (ctypes.c_int * n)()
            nodes = ctypes.c_longlong(0)
            length = ctypes.c_int(0)
            st = fn(n, k, packed, -1, 0.0, 1, 1, 1, 0, 4_000_000, int(bm), 0, 1, *extra,
                    path, ctypes.byref(nodes), ctypes.byref(length))
            out.append(({1: "sat", 0: "unsat"}[st], nodes.value, [path[i] for i in range(length.value)]))
        return out

    rng = random.Random(4)
    checked = 0
    for _ in range(150):
        inst = _random(rng)
        for k in range(1, inst.n_customers + 1):
            for bm in (False, True):
                cfg = CSEARCH if bm else {}
                bare = decide(inst, k, **cfg)
                named = decide(inst, k, old_close_count=False, old_rule_order=False, **cfg)
                assert (bare.status, bare.nodes, bare.order) == (named.status, named.nodes, named.order)
                for st, nodes, order in old_entry(inst, k, bm):
                    assert (bare.status, bare.nodes, bare.order or []) == (st, nodes, order)
                checked += 1
    assert checked > 500


def test_the_default_reproduces_the_counts_recorded_before_the_flags_existed():
    """Byte-for-byte on the campaign: `nodes_default` from `results.csv`, and
    under the pre-fix variant the pre-fix `nodes_csearch` the same file
    recorded on 2026-09-26 06:43, before the fix."""
    from learning.canonical import matrix_digest
    from learning.differential import RESULTS_CSV
    from learning.ensemble import Cell, generate
    from satisfiability.customer_search import sparse_enough_for_better_move

    if not RESULTS_CSV.exists():
        pytest.skip("campaign results not present")
    frame = pd.read_csv(RESULTS_CSV, low_memory=False)
    frame = frame[frame.certified.astype(bool) & (frame.status_csearch == "unsat")
                  & (frame.nodes_csearch != frame.nodes_default) & (frame.n <= 25)]
    for row in frame.sample(n=12, random_state=3).to_dict("records"):
        inst = generate(Cell(row["generator"], int(row["n"]), int(row["m"]), float(row["param"])),
                        int(row["index"]))
        assert matrix_digest(inst) == row["matrix_digest"]
        k = int(row["optimum"]) - 1
        assert decide(inst, k).nodes == int(row["nodes_default"]), row["instance_name"]
        bm = sparse_enough_for_better_move(inst)
        prefix = decide(inst, k, better_move=bm, better_move_dominators=0,
                        old_close_count=True, old_rule_order=True)
        assert prefix.status == "unsat"
        assert prefix.nodes == int(row["nodes_csearch"]), row["instance_name"]


def test_the_flags_are_no_ops_without_better_move():
    rng = random.Random(9)
    for _ in range(80):
        inst = _random(rng)
        for k in range(1, inst.n_customers + 1):
            base = decide(inst, k)
            for flags in FLAGS[1:]:
                other = decide(inst, k, **flags)
                assert (base.status, base.nodes, base.order) == (other.status, other.nodes, other.order)


def test_the_variants_reproduce_the_documented_behaviour_on_the_drawn_instances():
    """§7: Bug A (the close count) alone refutes the 17 × 9 minimal instance
    at its optimum; the 10 × 13 needs the two together (the cycle only forms
    once the over-count has discarded `r`); today's rule and the reordering
    alone are sound on both; every variant agrees at `optimum − 1`."""
    m10, m17 = _minimal()
    expected = {
        # (matrix, optimum) -> statuses at the optimum for FLAGS in order, then bm-first
        "10x13": ("sat", "sat", "sat", "unsat", "sat"),
        "17x9": ("sat", "unsat", "sat", "unsat", "sat"),
    }
    for name, (matrix, optimum) in (("10x13", m10), ("17x9", m17)):
        inst = MOSPInstance.from_matrix(matrix, name=name)
        assert decide(inst, optimum, native=False).status == "sat"
        got = tuple(decide(inst, optimum, **CSEARCH, **flags).status for flags in FLAGS + (BM_FIRST,))
        assert got == expected[name], (name, got)
        for flags in FLAGS + (BM_FIRST,):
            assert decide(inst, optimum - 1, **CSEARCH, **flags).status == "unsat"


def test_the_reordering_alone_and_bm_first_are_different_searches():
    """`old_rule_order` and `subset_after_better_move` each change node counts
    somewhere (neither is a no-op); on random sparse instances at this size
    neither changes a status, and `bm-first` must never: it is the candidate
    sound composition, checked against the Python reference at every k."""
    rng = random.Random(21)
    differing = {"order": 0, "bm-first": 0}
    for _ in range(120):
        inst = _random(rng)
        for k in range(1, inst.n_customers + 1):
            reference = decide(inst, k, native=False)
            fixed = decide(inst, k, **CSEARCH)
            order = decide(inst, k, old_rule_order=True, **CSEARCH)
            first = decide(inst, k, **BM_FIRST, **CSEARCH)
            assert fixed.status == reference.status == order.status == first.status
            differing["order"] += fixed.nodes != order.nodes
            differing["bm-first"] += fixed.nodes != first.nodes
    assert min(differing.values()) > 0
    # bm-first is a no-op without better_move, like the reverts
    inst = _random(rng)
    for k in range(1, inst.n_customers + 1):
        assert decide(inst, k).nodes == decide(inst, k, **BM_FIRST).nodes


def test_decide_variant_and_false_answers():
    from learning.fix_cost import VARIANTS, decide_variant, false_answers

    m10, _ = _minimal()
    inst = MOSPInstance.from_matrix(m10[0], name="m")
    assert set(VARIANTS) == {"fixed", "old-close", "old-order", "prefix", "bm-first"}
    answer, seconds, bm = decide_variant(inst, m10[1], "prefix")
    assert bm is True and answer.status == "unsat" and seconds >= 0
    answer, _, _ = decide_variant(inst, m10[1], "fixed")
    assert answer.status == "sat"
    assert false_answers({"status_lo": "unsat", "status_hi": "sat", "witness_ok": True}) == 0
    assert false_answers({"status_lo": "sat", "status_hi": "unsat", "witness_ok": None}) == 2
    assert false_answers({"status_lo": "unsat", "status_hi": "sat", "witness_ok": False}) == 1


def test_harness_rows_flag_the_prefix_variant_on_the_minimal_instance():
    from learning.fix_cost import harness_rows, soundness_table

    m10, _ = _minimal()
    inst = MOSPInstance.from_matrix(m10[0], name="m10")
    rows = pd.DataFrame(harness_rows(inst, m10[1], relabellings=1))
    assert set(rows.variant) == {"fixed", "old-close", "old-order", "prefix", "bm-first"}
    assert rows.labelling.nunique() >= 2
    ident = rows[rows.labelling == "identity"].set_index("variant")
    assert ident.loc["prefix", "status_hi"] == "unsat" and ident.loc["prefix", "false"] == 1
    assert ident.loc["fixed", "status_hi"] == "sat" and ident.loc["fixed", "false"] == 0
    table = soundness_table(rows).set_index("variant")
    assert table.loc["prefix", "instances with a false answer"] == 1
    assert table.loc["fixed", "instances with a false answer"] == 0
    # A dense instance is skipped: Theorem 2 is off, the variants are one search.
    dense = MOSPInstance.from_matrix([[1] * 8] * 4, name="dense")
    assert harness_rows(dense, 4) == []


def test_ratio_arithmetic_by_hand():
    from learning.fix_cost import (
        VARIANT_ORDER,
        _paired,
        attribution_table,
        ratio_summary,
        totals_table,
    )

    wide = pd.DataFrame({"fixed": [9, 19, 99], "old-close": [4, 9, 49],
                         "old-order": [4, 19, 49], "prefix": [4, 9, 49], "bm-first": [9, 19, 99],
                         "n": [10, 10, 20], "m": [10, 10, 20], "optimum": [3, 3, 4]})
    s = ratio_summary(wide, "fixed", "prefix")
    assert s["pairs"] == 3 and s["median"] == 2.0 and s["max"] == 2.0 and s["more"] == 3
    assert s["total ratio"] == pytest.approx(127 / 62)
    t = totals_table(wide).set_index("variant")
    assert t.loc["prefix", "total nodes"] == 62 and t.loc["fixed", "vs prefix (total)"] == pytest.approx(127 / 62)
    a = attribution_table(wide).set_index("comparison")
    assert a.loc["the candidate: bm-first / fixed", "equal"] == 3
    assert a.loc["close count alone, from pre-fix: old-order / prefix", "median"] == 1.0
    assert a.loc["rule order alone, from pre-fix: old-close / prefix", "median"] == 1.0
    # _paired keeps only refutations every variant settled
    rows = []
    for i, v in enumerate(VARIANT_ORDER):
        rows.append({"base_name": "a", "labelling": "identity", "variant": v, "status_lo": "unsat",
                     "nodes_lo": i, "n": 5, "m": 5, "optimum": 2})
        rows.append({"base_name": "b", "labelling": "identity", "variant": v,
                     "status_lo": "unknown" if v == "fixed" else "unsat",
                     "nodes_lo": 7, "n": 5, "m": 5, "optimum": 2})
    paired = _paired(pd.DataFrame(rows))
    assert list(paired.index.get_level_values(0)) == ["a"]
    assert paired.loc[("a", "identity"), "prefix"] == 3
