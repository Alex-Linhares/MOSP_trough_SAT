"""The port is faithful: same masks, same trace, same node counts as MOSP.

Runs only when the MOSP project is present (`~/dev/MOSP` or
`PATHWIDTH_MOSP_DIR`). Builds each challenge instance's customer graph, checks
the masks coincide, and runs both Python implementations with identical flags
and `k`, asserting identical status, order and node count.
"""
from pathlib import Path

import pytest

from conftest import MOSP_DIR

mosp = pytest.importorskip("mosp.instance", reason="MOSP project not found")
from mosp.instance import MOSPInstance  # noqa: E402
from satisfiability import customer_search as mosp_cs  # noqa: E402
from satisfiability.heuristics import _cs_cost, _neighbour_masks  # noqa: E402
from customer_inter.customer_graph import build_customer_graph  # noqa: E402

from pathwidth.graph import masks_from_graph, search_cost  # noqa: E402
from pathwidth.search import decide  # noqa: E402

CHALLENGE = MOSP_DIR / "benchmarks" / "instances" / "ChallengeInstances2005"
MIN_CUSTOMERS, MAX_CUSTOMERS = 8, 26
PER_SOURCE = 16


def challenge_instances():
    """A spread over the five challenge sources and over sizes 8..26, largest
    first within each source, all customers active (every customer has a
    product), so the customer graph has no vertex the MOSP search would skip."""
    out = []
    if not CHALLENGE.is_dir():
        return out
    for source in sorted(d for d in CHALLENGE.iterdir() if d.is_dir()):
        pool = []
        for path in sorted(source.rglob("*")):
            if not path.is_file() or path.name.startswith("README"):
                continue
            try:
                instances = MOSPInstance.from_benchmark_file(path)
            except Exception:
                continue
            for i, inst in enumerate(instances):
                if (MIN_CUSTOMERS <= inst.n_customers <= MAX_CUSTOMERS and inst.n_patterns >= 2
                        and all(inst.customer_patterns(c) for c in range(inst.n_customers))):
                    pool.append((f"{source.name}/{path.name}#{i}", inst))
        pool.sort(key=lambda item: -item[1].n_customers)
        # take every j-th so several sizes are represented, largest first
        step = max(1, len(pool) // PER_SOURCE)
        out.extend(pool[::step][:PER_SOURCE])
    return out


INSTANCES = challenge_instances()


def graph_masks(inst):
    G = build_customer_graph(inst)
    masks, labels = masks_from_graph(G)
    assert labels == list(range(inst.n_customers))
    return masks


@pytest.mark.skipif(not INSTANCES, reason="no challenge instances found")
def test_the_customer_graph_masks_equal_the_mosp_masks():
    for name, inst in INSTANCES:
        assert graph_masks(inst) == _neighbour_masks(inst), name


@pytest.mark.skipif(not INSTANCES, reason="no challenge instances found")
def test_the_cost_functions_agree():
    import random
    rng = random.Random(3)
    for name, inst in INSTANCES[:40]:
        masks = graph_masks(inst)
        order = list(range(inst.n_customers))
        rng.shuffle(order)
        assert search_cost(masks, order) == _cs_cost(masks, order), name


FLAG_SETS = [
    dict(),
    dict(old_move=False),
    dict(subset_rule=False),
    dict(definite_move=False),
    dict(expansion_prune=True),
    dict(fan_order="degree"),
    dict(restrict=True),
]


@pytest.mark.skipif(not INSTANCES, reason="no challenge instances found")
@pytest.mark.parametrize("flags", FLAG_SETS, ids=lambda f: ",".join(f"{k}={v}" for k, v in f.items()) or "default")
def test_identical_decisions_and_node_counts(flags):
    """Descend `k` from a loose upper bound until the first refutation (or a
    budget abort), comparing both implementations at every step. The last step
    is the real refutation at optimum − 1, the hardest decision the search
    makes on the instance."""
    budget = 300_000
    compared = refutations = total_nodes = 0
    for name, inst in INSTANCES:
        masks = graph_masks(inst)
        k = _cs_cost(masks, list(range(inst.n_customers))) - 1
        while k >= 1:
            theirs = mosp_cs.decide(inst, k, native=False, max_nodes=budget, **flags)
            ours = decide(masks, k, max_nodes=budget, native=False, **flags)
            assert (ours.status, ours.order, ours.nodes) == (theirs.status, theirs.order, theirs.nodes), (name, k, flags)
            compared += 1
            total_nodes += ours.nodes
            if ours.status == "unsat":
                refutations += 1
                break
            if ours.status == "unknown":
                break
            # a satisfying order may be worth more than k: jump to what it achieves
            k = min(k, search_cost(masks, ours.order)) - 1
    assert compared > 0
    if not flags.get("restrict"):
        assert refutations > 0


@pytest.mark.skipif(not INSTANCES, reason="no challenge instances found")
def test_the_c_ports_agree_too():
    """Same C file, same masks: MOSP's `decide_native` and ours must match
    exactly, node counts included, with `better_move` on and off."""
    from satisfiability.native import decide_native as mosp_native, native_available as mosp_ok
    from pathwidth.native import decide_native as our_native, native_available as our_ok
    if not (mosp_ok() and our_ok()):
        pytest.skip("C port unavailable on one side")
    compared = 0
    for name, inst in INSTANCES:
        masks = graph_masks(inst)
        k = _cs_cost(masks, list(range(inst.n_customers))) - 1
        for better in (False, True):
            kk = k
            while kk >= 1:
                theirs = mosp_native(inst, kk, better_move=better, max_nodes=2_000_000)
                ours = our_native(masks, kk, better_move=better, max_nodes=2_000_000)
                assert (ours.status, ours.order, ours.nodes) == (theirs.status, theirs.order, theirs.nodes), (name, kk, better)
                compared += 1
                if ours.status != "sat":
                    break
                kk = min(kk, search_cost(masks, ours.order)) - 1
    assert compared > 0
