"""loop0013 item 01: `learning.obstruction_ledger` — the bit-mask floors against
brute force on small graphs, the reading of the minor certificates on record
against `reports/minor_bound_verification.md`'s table, and the committed
ledger files: no bound on record above a certified optimum, no dataset floor
above a certified width, the targets' counts and disjointness."""
from __future__ import annotations

import json
import random
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import pytest

from learning import obstruction_ledger as ol

LEDGER_DIR = Path(__file__).resolve().parents[1] / "reports" / "scratch" / "obstruction_search" / "01_ledger"


def _random_graph(rng: random.Random, n: int, p: float) -> tuple[list[int], nx.Graph]:
    edges = [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p]
    return ol.adjacency_from_edges(n, edges), nx.Graph([(u, v) for u, v in edges] + [(v, v) for v in range(n)])


# ----------------------------------------------------------------------------
# the bit-mask floors against brute force
# ----------------------------------------------------------------------------


def test_degeneracy_and_clique_number_against_networkx():
    rng = random.Random(13)
    for _ in range(150):
        n = rng.randint(1, 14)
        adj, g = _random_graph(rng, n, rng.choice([0.15, 0.4, 0.7]))
        g.remove_edges_from(nx.selfloop_edges(g))
        assert ol.degeneracy(adj) == (max(nx.core_number(g).values()) if g.number_of_edges() else 0)
        omega, censored = ol.clique_number_budget(adj, seconds=5.0)
        assert not censored
        assert omega == max(len(c) for c in nx.find_cliques(g))


def test_mmd_plus_sits_between_degeneracy_and_treewidth():
    """MMD+ never drops below the degeneracy (contraction keeps every other
    degree at least as high as deletion does) and never exceeds the treewidth
    (`treewidth_reference`, the exact subset recurrence)."""
    from learning.treewidth import treewidth_reference

    rng = random.Random(7)
    for _ in range(120):
        n = rng.randint(2, 10)
        adj, _ = _random_graph(rng, n, rng.choice([0.2, 0.5, 0.8]))
        tw = treewidth_reference(list(adj))
        d = ol.degeneracy(adj)
        for rule in ("least-c", "min-d"):
            v = ol.mmd_plus(adj, rule)
            assert d <= v <= tw, (rule, d, v, tw)


def test_mmd_plus_least_c_agrees_with_the_solver_on_mosp_graphs():
    """The same rule as `satisfiability.mosp_solver._contraction_degeneracy`
    (`lb_contraction - 1`), on random MOSP instances."""
    from satisfiability.mosp_solver import _contraction_degeneracy

    rng = np.random.default_rng(3)
    for _ in range(40):
        n, m = int(rng.integers(3, 16)), int(rng.integers(3, 16))
        matrix = (rng.random((n, m)) < 0.3).astype(int)
        adj = ol.adjacency_from_matrix(matrix)
        g = nx.Graph()
        g.add_nodes_from(range(n))
        for v in range(n):
            for u in range(v + 1, n):
                if adj[v] >> u & 1:
                    g.add_edge(v, u)
        assert ol.mmd_plus(adj, "least-c") == _contraction_degeneracy(g)


def test_mosp_graph_adjacency_matches_the_expansion_bound_masks():
    from mosp.instance import MOSPInstance
    from satisfiability.expansion_bound import _closed_masks

    rng = np.random.default_rng(5)
    for _ in range(30):
        n, m = int(rng.integers(2, 12)), int(rng.integers(2, 12))
        matrix = (rng.random((n, m)) < 0.35).astype(int)
        closed, _ = _closed_masks(MOSPInstance.from_matrix(matrix, name="t"))
        adj = ol.adjacency_from_matrix(matrix)
        assert [c & ~(1 << v) for v, c in enumerate(closed)] == adj


def test_components_and_dataset_floors_on_a_disjoint_union():
    k5 = [(u, v) for u in range(5) for v in range(u + 1, 5)]
    path = [(5 + i, 6 + i) for i in range(4)]
    adj = ol.adjacency_from_edges(10, k5 + path)
    comps = ol.components(adj)
    assert sorted(c.bit_count() for c in comps) == [5, 5]
    row = ol.dataset_floors(10, k5 + path)
    assert row["degeneracy"] == 4 and row["mmd_leastc"] == 4 and row["mmd_mind"] == 4 and row["omega"] == 5
    assert row["n_components"] == 2 and row["skipped_components"] == 0
    big = ol.dataset_floors(10, k5 + path, max_component=4)
    assert big["skipped_components"] == 2 and big["degeneracy"] == 0


def test_bands_excess_and_class_parsing_match_the_record():
    from learning.bound_harness import BANDS
    from learning.excess import excess

    assert ol.BANDS == BANDS
    assert ol.excess(125, 125, 402) == excess(125, 125, 402)
    assert ol.band_label(9) == "9–20" and ol.band_label(134) == "101–134" and ol.band_label(8) == "?"
    assert ol.chu_stuckey_class("Random-125-125-2-3_0") == (125, 125, 2)
    assert ol.chu_stuckey_class("SP4") is None


def test_stratified_sample_is_deterministic_and_fills_the_quota():
    rng = np.random.default_rng(11)
    pool = pd.DataFrame({"instance_name": [f"i{k}" for k in range(900)],
                         "n": rng.integers(9, 135, 900)})
    pool["band"] = pool["n"].map(ol.band_label)
    a = ol.stratified_sample(pool, 100, 0)
    b = ol.stratified_sample(pool, 100, 0)
    assert a == b and len(a) == 100 and len(set(a)) == 100
    assert ol.stratified_sample(pool, 100, 1) != a
    bands = pd.Series([ol.band_label(int(pool.loc[pool.instance_name == nm, "n"].iloc[0])) for nm in a]).value_counts()
    shares = pool["band"].value_counts() / len(pool) * 100
    for band, cnt in bands.items():
        assert abs(cnt - shares[band]) < 1.5


# ----------------------------------------------------------------------------
# the minor certificates on record
# ----------------------------------------------------------------------------


@pytest.mark.skipif(not ol.MINOR_CERT_DIR.exists(), reason="no minor certificates on record")
def test_minor_certificates_read_as_minor_bound_verification_reports():
    """`reports/minor_bound_verification.md`, the summary table: 2-3_0 >= 21,
    2-1_0 >= 24, 6-1_0 >= 81, SP4 >= 53 (optimum units)."""
    expected = {"Random-125-125-2-3_0": 21, "Random-125-125-2-1_0": 24, "Random-125-125-6-1_0": 81, "SP4": 53}
    for name, value in expected.items():
        got, source = ol.minor_floors_on_record(name)
        assert got == value, (name, got, source)
        assert source.startswith("reports/scratch/minor_")
    none, src = ol.minor_floors_on_record("no-such-instance")
    assert np.isnan(none) and src == ""


# ----------------------------------------------------------------------------
# the committed ledger files
# ----------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ledger() -> pd.DataFrame:
    path = LEDGER_DIR / "ledger_corpus.csv"
    if not path.exists():
        pytest.skip("ledger_corpus.csv not built")
    return pd.read_csv(path)


def test_no_bound_on_record_above_a_certified_optimum(ledger):
    """The item's guard: a violation here is a wrong value or a wrong bound on
    record, the most important possible finding (TASK.md)."""
    assert len(ledger) == 6376
    for col, _ in ol.CORPUS_BOUNDS:
        have = ledger[col].notna()
        assert int((ledger.loc[have, col] > ledger.loc[have, "optimum"]).sum()) == 0, col
    assert (ledger["floor0"] <= ledger["optimum"]).all()
    assert (ledger["optimum_file"] == ledger["optimum"]).all()
    assert set(ledger["provenance_file"]) <= {"certified:refutation", "certified:bound"}


def test_floor0_is_the_max_of_its_parts_and_harper_is_sound_where_run(ledger):
    parts = ledger[list(ol.FLOOR0_PARTS)].astype(float).max(axis=1)
    assert (parts == ledger["floor0"]).all()
    run = ledger["harper12"].notna()
    assert (ledger.loc[run, "harper12"] >= ledger.loc[run, "exp_rec"]).sum() >= 0.95 * run.sum()
    assert (ledger.loc[run, "harper12_cap"] <= ol.HARPER_CAP).all()


@pytest.mark.skipif(not (LEDGER_DIR / "targets.json").exists(), reason="targets not frozen")
def test_targets_counts_and_disjointness(ledger):
    t = json.loads((LEDGER_DIR / "targets.json").read_text())
    names = set(ledger["instance_name"])
    assert len(t["gap338"]) == 338 and set(t["gap338"]) <= names
    assert len(t["cs200"]) == 200 and set(t["cs200"]) <= names
    assert len(t["rest500"]) == 500 and set(t["rest500"]) <= names
    assert len(t["open24"]) == 24
    assert set(t["small"]) == set(ledger.loc[ledger["n"] <= ol.SMALL_N, "instance_name"])
    assert set(t["rest500"]).isdisjoint(set(t["gap338"]) | set(t["cs200"]))
    assert len(set(t["rest500"])) == 500
    assert set(t["gap338"]) == set(ledger.loc[ledger["optimum"] - ledger["lb_best"] >= 2, "instance_name"])
    assert t["seed"] == ol.REST_SEED
    for rec in t["open24"]:
        assert rec["lower"] is not None and rec["lower"] < rec["width"]
    # frozen: the sample regenerates from the ledger with the recorded seed
    pool = ledger[~ledger["is_gap338"] & ~ledger["is_cs200"]]
    assert ol.stratified_sample(pool, ol.REST_SIZE, t["seed"]) == t["rest500"]


@pytest.mark.skipif(not (LEDGER_DIR / "ledger_dataset.csv.gz").exists(), reason="dataset ledger not built")
def test_dataset_floors_never_above_the_width():
    ds = pd.read_csv(LEDGER_DIR / "ledger_dataset.csv.gz")
    assert len(ds) == 16636
    for col in ("degeneracy", "mmd_leastc", "mmd_mind", "omega1", "floor_cheap"):
        assert int((ds[col] > ds["width"]).sum()) == 0, col
    assert (ds["mmd_leastc"] >= ds["degeneracy"]).all() and (ds["mmd_mind"] >= ds["degeneracy"]).all()
