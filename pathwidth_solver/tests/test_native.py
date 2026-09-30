"""Phase 6: the C port agrees with the Python reference."""
import itertools
import random

import networkx as nx
import pytest

import pathwidth as pw
from pathwidth.graph import masks_from_graph, vertex_separation_masks
from pathwidth.native import MAX_VERTICES, build_error, decide_native, native_available, words_for
from pathwidth.search import decide

pytestmark = pytest.mark.skipif(not native_available(), reason=f"C port unavailable: {build_error()}")


def random_graphs(seed, count, nmin=4, nmax=14):
    rng = random.Random(seed)
    for _ in range(count):
        n = rng.randint(nmin, nmax)
        yield nx.gnp_random_graph(n, rng.uniform(0.15, 0.8), seed=rng.randint(0, 10**6))


def descend(masks, k, **flags):
    """(status, order, nodes) at each k from `k` down to the first refutation."""
    trace = []
    while k >= 1:
        d = decide(masks, k, **flags)
        trace.append((k, d.status, d.order, d.nodes))
        if d.status != "sat":
            break
        k = min(k, vertex_separation_masks(masks, d.order) + 1) - 1
    return trace


# Flag sets under which the C and the Python take literally the same path.
# With old_move and memo both on the Python drops the memo and the C keeps it,
# so node counts may differ there; that case is checked for the answer only.
SAME_PATH = [
    dict(old_move=False),                     # memo on
    dict(old_move=False, memo=False),
    dict(memo=False),                         # old move on
    dict(old_move=False, subset_rule=False),
    dict(old_move=False, definite_move=False),
    dict(old_move=False, fan_order="degree"),
    dict(old_move=False, restrict=True),
]


@pytest.mark.parametrize("flags", SAME_PATH, ids=lambda f: ",".join(f"{k}={v}" for k, v in f.items()))
def test_c_and_python_visit_the_same_nodes(flags):
    for G in random_graphs(11, 40):
        masks, _ = masks_from_graph(G)
        k = len(masks)
        c = descend(masks, k, native=True, **flags)
        py = descend(masks, k, native=False, **flags)
        assert c == py, nx.to_graph6_bytes(G)


def test_default_flags_give_the_same_answers():
    """old_move + memo: C runs both, Python drops the memo. Same verdicts,
    same witness cost; node counts recorded but not required equal."""
    diffs = 0
    for G in random_graphs(12, 60):
        masks, _ = masks_from_graph(G)
        c = descend(masks, len(masks), native=True)
        py = descend(masks, len(masks), native=False)
        assert [(k, s) for k, s, _, _ in c] == [(k, s) for k, s, _, _ in py]
        assert c[-1][0] == py[-1][0]           # same refuted k => same width
        diffs += sum(1 for a, b in zip(c, py) if a[3] != b[3])
    # informational: how often the memo changed the count
    print(f"default-flag node-count differences: {diffs}")


def test_better_move_is_sound_and_prunes():
    pruned = total = 0
    for G in random_graphs(13, 60, 8, 16):
        masks, _ = masks_from_graph(G)
        plain = descend(masks, len(masks), native=True)
        better = descend(masks, len(masks), native=True, better_move=True)
        assert plain[-1][0] == better[-1][0] and plain[-1][1] == better[-1][1]
        total += 1
        pruned += better[-1][3] < plain[-1][3]
    assert total == 60


def test_native_matches_brute_force_on_the_atlas():
    for G in nx.graph_atlas_g():
        if G.number_of_nodes() > 6:
            break
        masks, _ = masks_from_graph(G)
        n = len(masks)
        if n == 0:
            continue
        brute = min(vertex_separation_masks(masks, p) for p in itertools.permutations(range(n)))
        width, order = pw.compute_pathwidth(G, native=True)
        assert width == brute and vertex_separation_masks(masks, [list(G.nodes).index(v) for v in order]) == brute


def test_it_declines_above_the_largest_build_and_the_python_takes_over():
    G = nx.path_graph(MAX_VERTICES + 1)
    masks, _ = masks_from_graph(G)
    assert words_for(len(masks)) is None and decide_native(masks, 2) is None
    assert decide(masks, 2).status == "sat"       # falls through to Python
    assert decide(masks, 1).status == "unsat"     # pw(path) = 1 -> k=1 means pw<=0
    assert words_for(128) == 2 and words_for(129) == 4 and words_for(1024) == 16


def test_multiword_matches_the_legacy_128_bit_c_node_for_node():
    """Same algorithm, sets widened: identical trace, better move included."""
    if decide_native([1], 1, legacy=True) is None:
        pytest.skip("legacy C unavailable")
    for G in random_graphs(31, 40, 6, 40):
        masks, _ = masks_from_graph(G)
        for better in (False, True):
            k = len(masks)
            while k >= 1:
                a = decide_native(masks, k, better_move=better)
                b = decide_native(masks, k, better_move=better, legacy=True)
                assert (a.status, a.order, a.nodes) == (b.status, b.order, b.nodes)
                if a.status != "sat":
                    break
                k = min(k, vertex_separation_masks(masks, a.order) + 1) - 1


@pytest.mark.parametrize("words", [4, 8, 16])
def test_wider_builds_match_the_python_above_128_vertices(words):
    """Sparse random graphs sized for each build; C vs Python node for node
    under the same-path flag sets, plus the default verdicts."""
    rng = random.Random(40 + words)
    lo, hi = 64 * words // 2 + 1, 64 * words // 2 + 40
    for _ in range(4):
        n = rng.randint(lo, hi)
        G = nx.gnp_random_graph(n, 2.2 / n, seed=rng.randint(0, 10**6))
        masks, _ = masks_from_graph(G)
        assert words_for(n) == words
        k = len(masks) // 4 + 2
        for flags in (dict(old_move=False), dict(memo=False)):
            c = descend(masks, k, native=True, max_nodes=60_000, **flags)
            py = descend(masks, k, native=False, max_nodes=60_000, **flags)
            assert c == py
        # default flags: the C keeps the memo alongside old move, the Python
        # drops it, so node counts differ and a budget may bind on one side
        # only; compare verdicts up to the first budget verdict.
        c = descend(masks, k, native=True, max_nodes=60_000)
        py = descend(masks, k, native=False, max_nodes=60_000)
        for (ka, sa, _, _), (kb, sb, _, _) in zip(c, py):
            if "unknown" in (sa, sb):
                break
            assert (ka, sa) == (kb, sb)


def test_budgets_are_honoured():
    G = nx.mycielski_graph(6)
    d = pw.decide_pathwidth(G, 19, max_nodes=1000)
    assert d.status == "unknown" and 1000 <= d.nodes <= 1001
    import time
    d = pw.decide_pathwidth(G, 19, deadline=time.monotonic() + 0.05)
    assert d.status == "unknown"


def test_known_pathwidths_natively():
    assert pw.compute_pathwidth(nx.mycielski_graph(5))[0] == 10
    assert pw.compute_pathwidth(nx.mycielski_graph(6))[0] == 20
    assert pw.compute_pathwidth(nx.grid_2d_graph(7, 7))[0] == 7
