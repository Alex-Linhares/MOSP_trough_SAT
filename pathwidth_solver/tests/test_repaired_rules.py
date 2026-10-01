"""The repaired definite and better moves in the pathwidth solver (MOSP loop0007 item 03).

`repaired_rules=True` applies the premises proved sound in MOSP's
`lean/MOSPFormalization/Search/`. These tests check that the Python port, the
multiword C at every word count and the 128-bit legacy C are the same search
under both settings, node for node, that each equals MOSP's search on the same
masks, and that the published definite move's counterexample no longer loses
the node. The full sweep is `python -m paper2.solver_fix_pw_check` in MOSP.
"""
import random

import networkx as nx
import pytest

import pathwidth as pw
from pathwidth import native
from pathwidth.graph import masks_from_graph, vertex_separation_masks
from pathwidth.search import Decision, _apply_dominance, _has_definite_matching, decide

needs_native = pytest.mark.skipif(not native.native_available(),
                                  reason=f"C port unavailable: {native.build_error()}")

# `DEFINITE_CEX` of MOSP's `paper2/search_check.py`: (masks, S, q, k). At the
# state S with budget k, Chu & Stuckey's definite move keeps q = 0 alone, and
# no solution from S starts with 0.
DEFINITE_CEX = [
    ([2201, 102, 30, 13, 21, 6690, 8514, 9857, 3904, 4000, 16256, 3873, 13344, 13504], 0b100, 0, 6),
    ([18459, 103, 286, 13, 21, 60578, 8770, 60320, 7044, 20416, 7712, 44961, 13568, 30944,
      58017, 51360], 0b100, 0, 7),
]

CONFIGS = [
    dict(old_move=False),
    dict(old_move=False, memo=False),
    dict(memo=False),
    dict(old_move=False, better_move=True, better_move_dominators=0),
    dict(memo=False, better_move=True, better_move_dominators=4),
    dict(old_move=False, subset_rule=False, better_move=True, better_move_dominators=1),
    dict(old_move=False, fan_order="degree", better_move=True),
]


def words_call(masks, k, words, **flags):
    """The multiword build at `words`, whatever the graph's size."""
    lib = native._load(words)
    full = dict(restrict=False, subset_rule=True, definite_move=True, old_move=True, memo=True,
                better_move=False, better_move_dominators=4, max_nodes=None, seconds=None,
                memo_limit=4_000_000, fan_order="index", repaired_rules=False)
    full.update(flags)
    return native._call(lib.csw_decide, len(masks), k, native._pack(masks, words), **full)


def key(d: Decision):
    return d.status, d.order, d.nodes


def random_graphs(seed, count, nmin=4, nmax=16):
    rng = random.Random(seed)
    for _ in range(count):
        n = rng.randint(nmin, nmax)
        yield nx.gnp_random_graph(n, rng.uniform(0.15, 0.7), seed=rng.randint(0, 10**6))


def test_the_matching_itself():
    assert _has_definite_matching([], 0)
    assert not _has_definite_matching([0b1], 2)
    assert _has_definite_matching([0b11, 0b01], 2)
    assert not _has_definite_matching([0b01, 0b01], 2)
    assert _has_definite_matching([0b011, 0b001, 0b110], 3)


def test_on_the_counterexample_the_repaired_filter_no_longer_keeps_0_alone():
    for masks, S, q, k in DEFINITE_CEX:
        full = (1 << len(masks)) - 1
        opened = 0
        for v in range(len(masks)):
            if S >> v & 1:
                opened |= masks[v]
        remaining = full & ~S
        opens = {v: masks[v] & ~opened for v in range(len(masks)) if remaining >> v & 1}
        # in vertex index order, as the search hands it over
        playable = [(((opened | masks[v]) & ~S).bit_count(), v) for v in sorted(opens)
                    if ((opened | masks[v]) & ~S).bit_count() <= k]
        old = _apply_dominance(playable, opens, True, True)
        new = _apply_dominance(playable, opens, True, True, repaired=True)
        assert [v for _, v in old] == [q]
        assert [v for _, v in new] != [q]


def test_the_python_better_move_now_runs():
    """`better_move` used to be ignored on the Python path."""
    changed = 0
    for G in random_graphs(5, 40, 8, 16):
        masks, _ = masks_from_graph(G)
        k = len(masks) // 2
        a = decide(masks, k, native=False, old_move=False)
        b = decide(masks, k, native=False, old_move=False, better_move=True, better_move_dominators=0)
        assert a.status == b.status
        changed += a.nodes != b.nodes
    assert changed > 0


@needs_native
@pytest.mark.parametrize("repaired", [False, True])
def test_python_c_legacy_and_every_word_build_visit_the_same_nodes(repaired):
    for G in random_graphs(17, 30):
        masks, _ = masks_from_graph(G)
        for flags in CONFIGS:
            k = len(masks)
            while k >= 1:
                flags_r = dict(flags, repaired_rules=repaired)
                py = decide(masks, k, native=False, **flags_r)
                assert key(native.decide_native(masks, k, legacy=True, **flags_r)) == key(py)
                for words in native.WORD_SIZES:
                    assert key(words_call(masks, k, words, **flags_r)) == key(py), (words, flags_r)
                if py.status != "sat":
                    break
                k = min(k, vertex_separation_masks(masks, py.order) + 1) - 1


@needs_native
def test_on_the_counterexamples_every_implementation_agrees_and_is_right():
    for masks, S, q, k in DEFINITE_CEX:
        width = pw.compute_pathwidth(nx.Graph([(u, v) for u in range(len(masks))
                                               for v in range(u + 1, len(masks))
                                               if masks[u] >> v & 1]))[0]
        for repaired in (False, True):
            for flags in CONFIGS:
                for kk in range(k - 2, k + 3):
                    py = decide(masks, kk, native=False, repaired_rules=repaired, **flags)
                    assert py.status == ("sat" if kk >= width + 1 else "unsat")
                    assert key(native.decide_native(masks, kk, repaired_rules=repaired, **flags)) == key(py)
                    assert key(native.decide_native(masks, kk, legacy=True, repaired_rules=repaired,
                                                    **flags)) == key(py)


@needs_native
def test_the_wide_builds_match_the_python_with_the_repaired_rules():
    rng = random.Random(77)
    for words in (4, 8):
        n = 64 * words // 2 + rng.randint(1, 30)
        G = nx.gnp_random_graph(n, 2.2 / n, seed=rng.randint(0, 10**6))
        masks, _ = masks_from_graph(G)
        assert native.words_for(n) == words
        k = len(masks) // 4 + 2
        for flags in (dict(old_move=False), dict(memo=False, better_move=True)):
            py = decide(masks, k, native=False, max_nodes=20_000, repaired_rules=True, **flags)
            c = decide(masks, k, native=True, max_nodes=20_000, repaired_rules=True, **flags)
            assert key(c) == key(py)


def test_the_repaired_rules_are_the_default():
    """The owner's decision of 2026-10-01, applied by loop0007 item 03."""
    import inspect
    assert inspect.signature(decide).parameters["repaired_rules"].default is True
    assert inspect.signature(native.decide_native).parameters["repaired_rules"].default is True
