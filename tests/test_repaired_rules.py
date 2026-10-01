"""The repaired definite and better moves in the Python reference (loop0007 item 01).

`decide(..., repaired_rules=True)` applies the premises proved sound in
`lean/MOSPFormalization/Search/`: the definite move needs `q` hereditarily
definite, tested by the matching condition (`HasDefiniteMatching`), and the
better move cites only under `IsRepairedBetter`. These tests check the
production filter against `paper2/search_check.py`, which shares no code with
the solver, and that with the flag off nothing changed, node for node.
"""

import hashlib
import json
import random

import pytest

from mosp.instance import MOSPInstance
from paper2.search_check import (
    BUG_B_CEX,
    DEFINITE_CEX,
    d_counts,
    d_hereditary,
    k_repaired_filter,
    labelled_graphs,
    s_searchsol_table,
    s_tables,
)
from paper2.solver_fix_check import (
    check_nodes,
    check_searches,
    matching_test,
    production_filter,
)
from satisfiability.customer_search import _has_definite_matching, decide
from satisfiability.native import decide_native, native_available

needs_native = pytest.mark.skipif(not native_available(),
                                  reason="the C search did not build here")


def _baseline_rows(rng, max_customers=12, max_patterns=10):
    rows = [[1 if rng.random() < rng.choice([0.15, 0.3, 0.5]) else 0
             for _ in range(rng.randint(1, max_patterns))]
            for _ in range(rng.randint(1, max_customers))]
    width = max(len(r) for r in rows)
    return [r + [0] * (width - len(r)) for r in rows]


# Status and node count of `decide(native=False)` on 40 seeded instances, at
# every k, under all 32 combinations of subset rule, definite move, old move,
# memo and restrict, computed with the code as it stood before `repaired_rules`
# existed (2026-10-01, commit 392a2bda2). 9,312 decisions, 19,438 nodes.
BASELINE_DIGEST = "3d4178fd56ea172cdc5d0a1898d32ab75c9bf2b9a7ec0437707e924e810f2832"
BASELINE_NODES = 19438


def test_with_the_flag_off_nothing_changed_node_for_node():
    rng = random.Random(7001)
    configs = [dict(subset_rule=s, definite_move=d, old_move=o, memo=m, restrict=r)
               for s in (0, 1) for d in (0, 1) for o in (0, 1) for m in (0, 1) for r in (0, 1)]
    rows = []
    for i in range(40):
        inst = MOSPInstance.from_matrix(_baseline_rows(rng), name="b")
        for k in range(0, inst.n_customers + 1):
            for ci, c in enumerate(configs):
                d = decide(inst, k, native=False, repaired_rules=False,
                           **{a: bool(b) for a, b in c.items()})
                rows.append((i, k, ci, d.status, d.nodes))
    assert sum(r[4] for r in rows) == BASELINE_NODES
    assert hashlib.sha256(json.dumps(rows).encode()).hexdigest() == BASELINE_DIGEST


@needs_native
def test_the_python_better_move_is_the_c_node_for_node():
    """The Python had no Theorem 2 before 2026-10-01; its port must be the C's rule."""
    rng = random.Random(11)
    pruned = 0
    for _ in range(60):
        rows = [[1 if rng.random() < rng.choice([0.1, 0.2, 0.35]) else 0
                 for _ in range(rng.randint(1, 12))] for _ in range(rng.randint(2, 13))]
        width = max(len(r) for r in rows)
        inst = MOSPInstance.from_matrix([r + [0] * (width - len(r)) for r in rows], name="t")
        active = {c for c in range(inst.n_customers) if inst.customer_patterns(c)}
        for k in range(0, inst.n_customers + 1):
            for dom in (0, 1, 4):
                for om, me in ((False, False), (False, True), (True, False)):
                    cfg = dict(old_move=om, memo=me, better_move=True, better_move_dominators=dom)
                    a = decide(inst, k, native=False, **cfg)
                    b = decide_native(inst, k, **cfg)
                    assert (a.status, a.nodes) == (b.status, b.nodes), (k, cfg)
                    if a.order is not None:
                        # the C also lists customers with no product; the Python omits them
                        assert a.order == [c for c in b.order if c in active]
                    pruned += a.nodes < decide(inst, k, native=False, old_move=om, memo=me).nodes
    assert pruned, "the better move never pruned; the test proves nothing"


def test_on_the_counterexample_the_repaired_filter_no_longer_keeps_0_alone():
    masks, S, q, k = DEFINITE_CEX[0]
    O, CL = s_tables(masks)
    SS = s_searchsol_table(masks, k, O, CL)
    open_q, close_q = d_counts(masks, O, S, q)
    assert open_q <= close_q                       # Chu & Stuckey's premise holds
    assert not matching_test(masks, O, S, q)       # the repaired premise does not
    assert SS[S] and not SS[CL[S | 1 << q]]        # and indeed 0 leads nowhere
    for L in (0, 1, 2):
        assert production_filter(masks, S, 0, k, L, repaired=False) == [q]
        kept = production_filter(masks, S, 0, k, L, repaired=True)
        assert kept != [q]
        assert any(SS[CL[S | 1 << c]] for c in kept)
        assert kept == sorted(k_repaired_filter(masks, O, CL, S, 0, k, L))


def test_on_both_counterexamples_the_whole_search_is_right():
    for masks, _, _, k in DEFINITE_CEX:
        t = check_searches(masks, ks=[k - 1, k])
        assert t["searches_repaired"] and not t["fail_answer_repaired"]
        assert not t["fail_witness_repaired"]


def test_the_bug_b_node_under_the_repaired_filter():
    masks, S, k = BUG_B_CEX
    O, CL = s_tables(masks)
    SS = s_searchsol_table(masks, k, O, CL)
    for L in (0, 1, 2):
        kept = production_filter(masks, S, 0, k, L, repaired=True)
        assert kept == sorted(k_repaired_filter(masks, O, CL, S, 0, k, L))
        assert not SS[S] or any(SS[CL[S | 1 << c]] for c in kept)


def test_the_repaired_filter_is_the_lean_filter_and_node_sound_to_four_vertices():
    """Every labelled graph on 1-4 vertices, every state, k, refuted old-move set and L."""
    total = {}
    for n in range(1, 5):
        for masks in labelled_graphs(n):
            for key, v in check_nodes(masks).items():
                total[key] = total.get(key, 0) + v
    assert total["nodes"] > 1000
    for key in ("fail_eq_repaired", "fail_eq_code", "fail_sound_repaired", "fail_matching"):
        assert total.get(key, 0) == 0, key


def test_the_repaired_search_answers_what_the_oracle_answers_to_five_vertices():
    rng = random.Random(5)
    graphs = [m for n in range(1, 5) for m in labelled_graphs(n)]
    graphs += rng.sample(list(labelled_graphs(5)), 150)
    for masks in graphs:
        t = check_searches(masks)
        assert not t["fail_answer_repaired"] and not t["fail_witness_repaired"], masks
        assert not t["fail_answer_code"], masks


def test_the_matching_test_is_the_hereditary_premise_on_the_pinned_graphs():
    for masks, _, _, _ in DEFINITE_CEX:
        O, _ = s_tables(masks)
        full = (1 << len(masks)) - 1
        rng = random.Random(3)
        for S in [0, 0b100] + [rng.randrange(full) for _ in range(30)]:
            for q in range(len(masks)):
                if S >> q & 1:
                    continue
                o, c = d_counts(masks, O, S, q)
                if o <= c:
                    assert matching_test(masks, O, S, q) == d_hereditary(masks, O, S, q)


def test_the_matching_itself():
    assert _has_definite_matching([], 0)
    assert _has_definite_matching([], -1)
    assert not _has_definite_matching([], 1)
    assert not _has_definite_matching([0b1, 0b1], 2)          # both need only stack 0
    assert _has_definite_matching([0b1, 0b11], 2)             # 0 -> stack 0, 1 -> stack 1
    assert _has_definite_matching([0b11, 0b1], 2)             # needs an augmenting path
    assert not _has_definite_matching([0b11, 0b11, 0b11], 3)  # Hall fails
    assert _has_definite_matching([0b11, 0b11, 0b11], 2)


def test_open_at_most_one_always_passes():
    """Corollary to Theorem 4.7: `open(q, S) ≤ 1` is hereditarily definite."""
    assert _has_definite_matching([], 0)
    assert _has_definite_matching([0b1], 0)


# ---------------------------------------------------------------------------
# item 02: the C carries the flag, node for node with the Python
# ---------------------------------------------------------------------------

# Old move and memo in the settings both implementations run identically: with
# both on the C runs both and the Python drops the memo, by design.
_MATCHED = [dict(subset_rule=s, definite_move=d, better_move=b, better_move_dominators=L,
                 old_move=o, memo=m)
            for s, d in ((True, True), (False, True), (True, False))
            for b, L in ((False, 4), (True, 0), (True, 1), (True, 4))
            for o, m in ((True, False), (False, True), (False, False))]


def _same(instance, k, cfg, repaired, max_nodes=None):
    py = decide(instance, k, native=False, repaired_rules=repaired, max_nodes=max_nodes, **cfg)
    c = decide_native(instance, k, repaired_rules=repaired, max_nodes=max_nodes, **cfg)
    assert c is not None
    active = {x for x in range(instance.n_customers) if instance.customer_patterns(x)}
    # the C lists customers needing nothing as root free moves; the Python omits them
    c_order = None if c.order is None else [x for x in c.order if x in active]
    assert (py.status, py.nodes, py.order) == (c.status, c.nodes, c_order), (k, cfg, repaired, py, c)
    return c


def _from_masks(masks, name):
    from paper2.search_check import matrix_from_masks
    return MOSPInstance.from_matrix(matrix_from_masks(masks), name=name)


@needs_native
def test_the_c_equals_the_python_on_the_native_test_inputs():
    """`tests/test_native.py`'s generator, every k, both settings, 36 configurations."""
    rng = random.Random(90)
    for _ in range(25):
        rows = [[1 if rng.random() < rng.choice([0.2, 0.4, 0.6, 0.8]) else 0
                 for _ in range(rng.randint(1, 7))]
                for _ in range(rng.randint(1, 8))]
        width = max(len(r) for r in rows)
        inst = MOSPInstance.from_matrix([r + [0] * (width - len(r)) for r in rows], name="t")
        for k in range(0, inst.n_customers + 2):
            for cfg in _MATCHED:
                for repaired in (False, True):
                    _same(inst, k, cfg, repaired)


BUG_B_10 = [523, 519, 678, 73, 16, 548, 72, 388, 384, 551]


@needs_native
def test_the_c_equals_the_python_on_the_counterexamples():
    """Both `DEFINITE_CEX` graphs and the 8- and 10-vertex Bug B instances,
    every k, and the two settings really part somewhere on them."""
    graphs = [m for m, _, _, _ in DEFINITE_CEX] + [BUG_B_CEX[0], BUG_B_10]
    parted = 0
    for i, masks in enumerate(graphs):
        inst = _from_masks(masks, f"cex{i}")
        for k in range(1, len(masks) + 1):
            for cfg in _MATCHED:
                old = _same(inst, k, cfg, False)
                new = _same(inst, k, cfg, True)
                assert old.status == new.status
                parted += old.nodes != new.nodes
    assert parted > 0


@needs_native
def test_the_c_answers_the_oracle_on_definite_cex():
    """The repaired C on `DEFINITE_CEX` answers the oracle's `Sol_k(∅)` at every
    k under every matched configuration. (The node where the published filter
    loses the solution, S = {2} at k = 6, has one: `truth[CL[S]]`.)"""
    masks, S, q, k = DEFINITE_CEX[0]
    from paper2.search_check import s_tables
    O, CL = s_tables(masks)
    truth = s_searchsol_table(masks, k, O, CL)
    assert truth[CL[S]]
    # The Lean filter on the C's own run is checked node by node in item 01;
    # here the whole search must answer the oracle at every k, both settings.
    inst = _from_masks(masks, "cex")
    for kk in range(1, len(masks) + 1):
        want = s_searchsol_table(masks, kk, O, CL)[CL[0]]
        for cfg in _MATCHED:
            assert (decide_native(inst, kk, repaired_rules=True, **cfg).status == "sat") == want


@needs_native
def test_the_c_equals_the_python_past_64_customers():
    """The second 64-bit half of the C's customer words, under a node cap."""
    from pathlib import Path

    from benchmarks.ratchet import find_instances
    found = find_instances(["SP4"], Path("benchmarks/instances"))
    if not found:
        pytest.skip("SP4 benchmark file not found")
    inst = found[0]
    assert inst.n_customers > 64
    cfg = dict(subset_rule=True, definite_move=True, better_move=True,
               better_move_dominators=4, old_move=True, memo=False)
    for k in (52, 53):                        # SP4's optimum is 53
        for repaired in (False, True):
            _same(inst, k, cfg, repaired, max_nodes=3000)


@needs_native
def test_the_c_equals_the_python_on_a_real_refutation():
    """SP2 at 18 (optimum 19), the refutation `tests/test_native.py` uses."""
    from pathlib import Path

    from benchmarks.ratchet import find_instances
    found = find_instances(["SP2"], Path("benchmarks/instances"))
    if not found:
        pytest.skip("SP2 benchmark file not found")
    cfg = dict(subset_rule=True, definite_move=True, better_move=True,
               better_move_dominators=4, old_move=False, memo=True)
    c = _same(found[0], 18, cfg, True)
    assert c.status == "unsat" and c.nodes > 1000


@needs_native
def test_the_old_entry_point_keeps_the_published_rules():
    """`cs_decide_variant`, kept for processes that loaded the library before
    `repaired_rules` existed, is `cs_decide_rules` with the flag off."""
    import ctypes

    from satisfiability.heuristics import _neighbour_masks
    from satisfiability.native import _load
    lib = _load()
    masks, _, _, k = DEFINITE_CEX[0]
    inst = _from_masks(masks, "cex")
    n = inst.n_customers
    packed = (ctypes.c_uint64 * (2 * n))()
    for i, mask in enumerate(_neighbour_masks(inst)):
        packed[2 * i] = mask & ((1 << 64) - 1)
        packed[2 * i + 1] = mask >> 64
    for kk in range(1, n + 1):
        path = (ctypes.c_int * n)()
        nodes = ctypes.c_longlong(0)
        length = ctypes.c_int(0)
        status = lib.cs_decide_variant(n, kk, packed, -1, 0.0, 1, 1, 0, 0, 4_000_000,
                                       1, 0, 1, 0, 0, path, ctypes.byref(nodes),
                                       ctypes.byref(length))
        old = decide_native(inst, kk, better_move=True, better_move_dominators=0,
                            old_move=True, memo=False, repaired_rules=False)
        assert (status, nodes.value) == ({"sat": 1, "unsat": 0}[old.status], old.nodes)
