"""The test logic of `paper2/false_refutation_hunt.py`.

The hunt is only worth its compute if (a) it accepts a false refutation
certified by a witness that simulates to <= k, (b) it rejects one whose witness
does not, (c) it does not flag what is known to be answered correctly, (d) the
repaired optimum it certifies against agrees with an independent oracle, (e)
its instrumented walk is the production search, node for node, and (f) it
resumes after being stopped.
"""
import json
import random
import time

from paper2 import false_refutation_hunt as H
from paper2 import search_check as sc

CEX = sc.DEFINITE_CEX[0][0]


def _valid(masks):
    n = len(masks)
    for u in range(n):
        assert masks[u] >> u & 1
        assert masks[u] < 1 << n
        for v in H.bits(masks[u]):
            assert masks[v] >> u & 1


def _sample(count, seed=3, lo=5, hi=14):
    rng = random.Random(seed)
    return [H.gen_family(rng, rng.randint(lo, hi), rng.randrange(5)) for _ in range(count)]


# --- the certificate --------------------------------------------------------

def test_accepts_a_false_refutation_certified_by_the_witness():
    """A published unsat at the repaired optimum, with a witness that simulates, is a hit."""
    k = H.certify(CEX)["k"]

    def mock(masks, kk, cfg, repaired):
        if not repaired and cfg == H.CSEARCH and kk == k:
            return 0, [], 1
        return H.c_decide(masks, kk, cfg, repaired)

    res = H.certify(CEX, mock)
    assert res["status"] == "ok" and res["peak"] <= res["k"] == k
    assert res["hits"] == [(H.CSEARCH, k)]
    assert res["repaired_bad"] == []
    assert H.evaluate(CEX, mock)["fitness"] >= 100


def test_rejects_a_hit_whose_witness_does_not_simulate():
    """The repaired side claims sat with an order that costs more than k: nothing is certified."""
    greedy = H.greedy_order(CEX)

    def mock(masks, kk, cfg, repaired):
        return (1, greedy, 1) if repaired else (0, [], 1)

    res = H.certify(CEX, mock)
    assert H.order_cost(CEX, greedy) > res["k"]
    assert res["status"] == "witness_invalid" and res["hits"] == []

    def truncated(masks, kk, cfg, repaired):          # not a closing order of every customer
        return (1, greedy[:-1], 1) if repaired else (0, [], 1)

    res = H.certify(CEX, truncated)
    assert res["status"] == "witness_invalid" and res["hits"] == []
    assert H.evaluate(CEX, truncated)["fitness"] < 0


def test_flags_a_synthetic_repaired_bug():
    k = H.certify(CEX)["k"]
    cfg = H.CONFIGS[-1]

    def mock(masks, kk, c, repaired):
        if repaired and c == cfg and kk == k:
            return 0, [], 1
        return H.c_decide(masks, kk, c, repaired)

    res = H.certify(CEX, mock)
    assert res["repaired_bad"] == [(cfg, k)] and res["hits"] == []


def test_does_not_flag_cex_graph():
    """cexGraph loses the last solution at {2}, k = 6, and is answered right as a whole."""
    res = H.certify(CEX)
    assert res["status"] == "ok" and res["k"] == 6 and res["peak"] <= 6
    assert res["hits"] == [] and res["repaired_bad"] == []
    assert H.evaluate(CEX)["fitness"] < 100
    assert H.any_hit(CEX) is None


def test_repaired_optimum_agrees_with_the_oracle():
    for masks in _sample(60):
        res = H.certify(masks)
        assert res["status"] == "ok" and res["hits"] == [] and res["repaired_bad"] == []
        assert H.order_cost(masks, res["witness"]) == res["peak"] <= res["k"]
        assert H.oracle(masks) == res["k"]
        O = sc.d_opened_table(masks)                       # and search_check's oracle
        assert sc.d_solvable_table(masks, res["k"], O)[0]
        assert res["k"] == 0 or not sc.d_solvable_table(masks, res["k"] - 1, O)[0]


def test_c_decide_is_decide_native():
    from mosp.instance import MOSPInstance
    from satisfiability.native import decide_native
    for masks in _sample(15, seed=5):
        k = H.oracle(masks)
        inst = MOSPInstance.from_matrix(sc.matrix_from_masks(masks), name="t")
        for cfg in H.CONFIGS[::9]:
            for rep in (0, 1):
                st, _, nodes = H.c_decide(masks, k, cfg, rep)
                d = decide_native(inst, k, repaired_rules=bool(rep), **H.config_kwargs(cfg))
                assert (d.status, d.nodes) == ({1: "sat", 0: "unsat"}[st], nodes)


# --- the walk ---------------------------------------------------------------

def test_walk_is_the_production_search():
    for masks in _sample(60, seed=7, hi=24):
        k = H.certify(masks)["k"]
        for cfg in H.CONFIGS[::5]:
            for kk in (k - 1, k):
                st, _, nodes = H.c_decide(masks, kk, cfg, 0)
                w = H.walk(masks, kk, cfg)
                assert (w["answer"], w["nodes"]) == (st, nodes)


def test_walk_sees_the_known_node_loss():
    """RUN_LOST_CEX: the code's run loses the last solution at {1} and still answers sat."""
    masks, k, S = sc.RUN_LOST_CEX
    w = H.walk(masks, k, H.CSEARCH)
    assert w["answer"] == 1 and w["filter_loss"] >= 1 and w["false_ref"] >= 1
    assert w["first_loss_state"] == S and w["judge_aborts"] == 0


# --- minimisation and moves -------------------------------------------------

def test_minimise_shrinks_while_the_certificate_holds(monkeypatch):
    def fake(masks):
        has_edge = any(m & ~(1 << v) for v, m in enumerate(masks))
        return {"k": 2, "hits": [(H.DEFAULT, 2)]} if has_edge else None

    monkeypatch.setattr(H, "any_hit", fake)
    assert H.minimise(CEX) == [0b11, 0b11]


def test_moves_keep_graphs_valid():
    rng = random.Random(11)
    g = list(CEX)
    for _ in range(3000):
        g2, _ = H.mutate(g, rng, {"first_loss": 0b100})
        _valid(g2)
        if 2 <= len(g2) <= H.MAX_N:
            g = g2
    for _ in range(50):
        g = H.baseline_graph(rng)
        _valid(g)
        assert len(g) <= H.MAX_N


# --- resuming ---------------------------------------------------------------

def test_stop_and_resume(tmp_path):
    out = tmp_path / "hunt"
    H.run(1, time.time() + 8, out)
    ck1 = json.loads((out / "checkpoint.json").read_text())
    assert ck1["epoch"] == 1 and ck1["counters"]["tested"] > 0
    arch1 = (out / "archive.jsonl").read_text().splitlines() if (out / "archive.jsonl").exists() else []
    with open(out / "archive.jsonl", "a") as fh:            # a crash mid-line
        fh.write('{"masks": [3, 3], "fitn')
    H.run(1, time.time() + 8, out)
    ck2 = json.loads((out / "checkpoint.json").read_text())
    assert ck2["epoch"] == 2
    assert ck2["counters"]["tested"] > ck1["counters"]["tested"]
    arch2 = (out / "archive.jsonl").read_text().splitlines()
    assert all(line in arch2 for line in arch1)
    log = (out / "progress.log").read_text().splitlines()
    assert log[0].startswith("# restart") and "false_refutation_hunt" in log[1]
    assert any(f"resumed from checkpoint at {ck1['saved']}" in line for line in log)


def test_found_md_means_nothing_to_do(tmp_path):
    out = tmp_path / "hunt"
    out.mkdir()
    (out / "FOUND.md").write_text("found\n")
    t = time.time()
    assert H.run(1, None, out) == 0
    assert time.time() - t < 5 and not (out / "checkpoint.json").exists()
