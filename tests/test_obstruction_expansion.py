"""loop0013 item 02: `learning.obstruction_expansion` — the exact profile
against a Python reference and against `expansion_bound`'s levels, the two
theorems on small graphs (the exact Harper and empty-pair values never exceed
`vs + 1`), the ceiling between the exact bound and the optimum on the small
corpus instances, the empty-pair ceiling formula, label invariance of the
search, the harness candidate's validity, and the committed files."""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from learning import obstruction_expansion as oe

SCRATCH = Path(__file__).resolve().parents[1] / "reports" / "scratch" / "obstruction_search"


def _random_closed(rng: random.Random, n: int, p: float) -> list[int]:
    adj = [0] * n
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
    return oe.closed_masks(adj)


@pytest.fixture(scope="module")
def small_corpus():
    """The first 60 `targets.small` instances with matrix, optimum and witness."""
    if not oe.TARGETS_JSON.exists() or not oe.LEDGER_CORPUS.exists():
        pytest.skip("item 01's ledger is not on disk")
    led = oe.ledger().set_index("instance_name")
    names = oe.target_names("small")[:60]
    inst = oe.corpus_instances()
    out = []
    for nm in names:
        sol = oe.solution_record(nm)
        out.append((nm, np.asarray(inst[nm][1].matrix, dtype=int), int(led.loc[nm, "optimum"]),
                    sol["ordering"] if sol else None))
    return out


# ----------------------------------------------------------------------------
# the exact profile
# ----------------------------------------------------------------------------


def test_exact_profile_matches_python_reference():
    rng = random.Random(11)
    for _ in range(150):
        n = rng.randint(1, 10)
        closed = _random_closed(rng, n, rng.choice([0.15, 0.4, 0.8]))
        prof = oe.exact_profile(closed)
        assert prof.values == oe.exact_profile_reference(closed)
        for t in range(1, n + 1):
            assert prof.sets[t].bit_count() == t
            assert oe.neighbourhood_size(closed, prof.sets[t]) == prof.values[t]


def test_exact_harper_and_empty_pair_never_exceed_vs_plus_one():
    """The two theorems (`exists_closedNbhd_card_le`,
    `card_sub_two_mul_emptyPairIndex_sub_two_le_pathwidth`) read on the code:
    `max_t (f(t) - t) + 1 <= vs + 1` and `n - 2 s* - 1 <= vs + 1`, on every
    random graph tried, by brute-force vertex separation."""
    from learning.first_moment import vertex_separation_brute

    rng = random.Random(5)
    for _ in range(200):
        n = rng.randint(1, 9)
        closed = _random_closed(rng, n, rng.choice([0.2, 0.5, 0.9]))
        adj = [c & ~(1 << v) for v, c in enumerate(closed)]
        vs = vertex_separation_brute(adj)
        prof = oe.exact_profile(closed)
        harper, _ = prof.harper()
        assert harper <= vs + 1
        assert prof.empty_pair() <= vs + 1
        assert prof.empty_pair() <= harper  # the empty pair is a weakening of the same profile


def test_exact_profile_agrees_with_expansion_bound_levels(small_corpus):
    """`expansion_bound(max_t=12).levels` is `f(1..cap+1)` by branch and bound;
    the subset enumeration must give the same numbers on 50 instances."""
    from mosp.instance import MOSPInstance
    from satisfiability.expansion_bound import expansion_bound

    checked = 0
    for nm, matrix, _, _ in small_corpus[:50]:
        b = expansion_bound(MOSPInstance.from_matrix(matrix, name=nm), max_t=12, time_budget=None)
        prof = oe.exact_profile(oe.closed_masks_from_matrix(matrix))
        assert b.levels == prof.values[1:len(b.levels) + 1], nm
        if len(b.levels) >= matrix.shape[0] - 1:
            assert b.value == prof.harper()[0], nm  # whole profile covered: the same bound
        checked += 1
    assert checked == 50


# ----------------------------------------------------------------------------
# the search and its ceiling
# ----------------------------------------------------------------------------


def _seeds(matrix, ordering):
    adj = oe.adjacency_from_matrix(matrix)
    closed = oe.closed_masks(adj)
    seeds = oe.maximal_clique_seeds(adj)
    if ordering is not None:
        opening, closing = oe.witness_layouts(matrix, ordering)
        seeds += oe.finished_sets(closed, opening) + oe.finished_sets(closed, closing)
    return adj, closed, seeds


def test_opening_layout_has_vertex_separation_optimum_minus_one(small_corpus):
    """The guarantee behind `ceiling <= optimum`: the witness's opening-time
    layout has vertex separation exactly `optimum - 1` (it cannot be less, the
    optimum being certified)."""
    for nm, matrix, optimum, ordering in small_corpus[:40]:
        assert ordering is not None, nm
        adj = oe.adjacency_from_matrix(matrix)
        opening, _ = oe.witness_layouts(matrix, ordering)
        assert sorted(opening) == list(range(matrix.shape[0]))
        assert oe.vertex_separation_of(adj, opening) == optimum - 1, nm


def test_ceiling_between_exact_bound_and_optimum(small_corpus):
    """Never below the exact bound (`fhat >= f`), never above the optimum (the
    witness's prefix sets are seeds); the same for the empty-pair ceiling."""
    for nm, matrix, optimum, ordering in small_corpus:
        adj, closed, seeds = _seeds(matrix, ordering)
        prof = oe.search_profile(closed, seeds, time_budget=1.0, rng_seed=1)
        exact = oe.exact_profile(closed)
        for t in range(1, len(closed) + 1):
            assert prof.values[t] >= exact.values[t]
            assert prof.sets[t].bit_count() == t
            assert oe.neighbourhood_size(closed, prof.sets[t]) == prof.values[t]
        ceiling, _ = prof.harper()
        assert exact.harper()[0] <= ceiling <= optimum, nm
        assert exact.empty_pair() <= prof.empty_pair() <= optimum, nm


def test_empty_pair_ceiling_is_n_minus_2s_minus_1():
    rng = random.Random(2)
    for _ in range(50):
        n = rng.randint(2, 12)
        closed = _random_closed(rng, n, 0.4)
        prof = oe.search_profile(closed, [], time_budget=0.2, rng_seed=3)
        s_hat = max(min(t - 1, n - prof.values[t]) for t in range(1, n + 1))
        assert prof.s_hat() == s_hat
        assert prof.empty_pair() == n - 2 * s_hat - 1


def test_search_is_label_invariant_up_to_the_seed(small_corpus):
    """Relabelling the customers changes nothing the search reports at these
    sizes: the profile found equals the exact profile on both labellings."""
    rng = random.Random(9)
    for nm, matrix, _, ordering in small_corpus[:25]:
        n = matrix.shape[0]
        perm = list(range(n))
        rng.shuffle(perm)
        matrix2 = matrix[perm]
        adj, closed, seeds = _seeds(matrix, ordering)
        adj2, closed2, seeds2 = _seeds(matrix2, ordering)
        p1 = oe.search_profile(closed, seeds, time_budget=1.0, rng_seed=1)
        p2 = oe.search_profile(closed2, seeds2, time_budget=1.0, rng_seed=1)
        exact = oe.exact_profile(closed)
        assert p1.values == exact.values, nm
        assert p2.values == exact.values, nm


# ----------------------------------------------------------------------------
# the harness candidate
# ----------------------------------------------------------------------------


def test_harper_floor_candidate_is_valid_and_is_expansion_bound(small_corpus):
    from learning.bound_harness import Budget, graph_from_matrix
    from mosp.instance import MOSPInstance
    from satisfiability.expansion_bound import expansion_bound

    for nm, matrix, optimum, _ in small_corpus[:30]:
        value, info = oe.harper_floor(graph_from_matrix(matrix), matrix, Budget(seconds=5.0))
        assert 1 <= value <= optimum, nm
        ref = expansion_bound(MOSPInstance.from_matrix(matrix, name=nm), max_t=12, time_budget=5.0)
        assert value == ref.value and info["cap"] == ref.cap


# ----------------------------------------------------------------------------
# the committed files
# ----------------------------------------------------------------------------


def test_committed_ceiling_and_floor_files():
    ceiling = SCRATCH / "02_expansion" / "ceiling.csv"
    if not ceiling.exists():
        pytest.skip("item 02's ceiling.csv is not on disk")
    c = pd.read_csv(ceiling)
    assert c["instance_name"].is_unique
    assert (c["ceiling"] <= c["optimum"]).all(), "a ceiling above a certified optimum"
    assert (c["empty_ceiling"] <= c["optimum"]).all()
    assert (c["witness_vs_opening"] == c["optimum"] - 1).all()
    floor = SCRATCH / "02_expansion" / "floor.csv"
    if floor.exists():
        f = pd.read_csv(floor)
        assert (f["floor"] <= f["optimum"]).all(), "a floor above a certified optimum"
        assert (f["floor"] >= f["harper12"]).all()
        if "ceiling" in f.columns:
            assert (f["floor"] <= f["ceiling"]).all(), "a floor above the ceiling"
    exact = SCRATCH / "02_expansion" / "exact_small.csv"
    if exact.exists():
        e = pd.read_csv(exact)
        assert (e["exact_bound"] <= e["optimum"]).all()
        assert (e["empty_exact"] <= e["exact_bound"]).all()
        assert (e["exact_bound"] >= e["harper12"]).all()
        assert (e["ceiling"] >= e["exact_bound"]).all()


# ----------------------------------------------------------------------------
# item 03: the exact inner minimum by SAT with DRAT, and the independent checker
# ----------------------------------------------------------------------------

import gzip
import hashlib
import importlib.util
import json
import subprocess
import sys


def _checker():
    """`paper1/obstruction_check.py` loaded from its path (paper1 is not a package)."""
    path = Path(__file__).resolve().parents[1] / "paper1" / "obstruction_check.py"
    spec = importlib.util.spec_from_file_location("obstruction_check", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_sat_encoding_agrees_with_enumeration():
    """UNSAT iff `f(t) > b`, for every `(t, b)` on 100 random graphs at n <= 12;
    a SAT answer's set has `t` members and `|N[set]| <= b`."""
    rng = random.Random(17)
    calls = 0
    for _ in range(100):
        n = rng.randint(2, 12)
        closed = _random_closed(rng, n, rng.choice([0.15, 0.3, 0.5, 0.8]))
        f = oe.exact_profile(closed).values
        for t in range(1, n + 1):
            for b in range(0, n):
                res = oe.exact_sat(closed, t, b, proof_dir=None, conflicts=None, deadline=None)
                calls += 1
                assert res["status"] == ("unsat" if f[t] > b else "sat"), (n, t, b, f[t], res["status"])
                if res["status"] == "sat":
                    assert len(res["set"]) == t
                    mask = sum(1 << v for v in res["set"])
                    assert oe.neighbourhood_size(closed, mask) == res["nbhd"] <= b
    assert calls > 3000


def test_profile_floor_and_mark_levels():
    assert oe.profile_floor([]) == 0
    assert oe.profile_floor([3, 4, 5]) == 3          # max(3-1, 4-2, 5-3) + 1
    assert oe.profile_floor([2, 2, 7]) == 5          # f(3) - 3 = 4
    fhat = [0, 2, 3, 5, 7, 9, 10, 10, 10, 10, 10]    # n = 10
    # proved to level 3, floor 3 (f(3) - 3 + 1 = 3): levels 4.. with fhat - t + 1 > 3 are 4 (4), 5 (5), 6 (5), 7 (4)
    assert oe.mark_levels(10, fhat, 3, 3, 5, set()) == [5, 4, 6, 7]
    assert oe.mark_levels(10, fhat, 3, 3, 5, {5}) == [4, 6, 7]
    assert oe.mark_levels(10, fhat, 3, 5, 5, set()) == []          # nothing above the floor
    assert oe.mark_levels(10, fhat, 3, 3, 5, set(), max_levels=1) == [5]


def _cycle_instance(n: int):
    """The MOSP instance whose graph is the n-cycle: pattern j = customers {j, j+1}."""
    matrix = np.zeros((n, n), dtype=int)
    for j in range(n):
        matrix[j, j] = 1
        matrix[(j + 1) % n, j] = 1
    return matrix


def test_certificate_verifies_and_a_damaged_one_is_rejected(tmp_path):
    oc = _checker()
    if not oc.DEFAULT_DRAT_TRIM.exists():
        pytest.skip("drat-trim is not built")
    n = 11
    matrix = _cycle_instance(n)
    closed = oe.closed_masks_from_matrix(matrix)
    f = oe.exact_profile(closed).values
    t = 4
    assert f[t] == t + 2
    oe.write_standard_instance(tmp_path / "instance.mosp", "cycle11", matrix)
    res = oe.exact_sat(closed, t, f[t] - 1, tmp_path, conflicts=100000, deadline=20.0, instance_name="cycle11",
                       matrix_sha=oe.matrix_sha256(matrix), source_file="test")
    assert res["status"] == "unsat" and res["verdict"] == "verified"
    cert = tmp_path / f"t{t}_b{f[t] - 1}.json"
    out = oc.check_expansion(tmp_path / "instance.mosp", cert)
    assert out["verdict"] == "verified", out
    assert out["proves"]["mosp_at_least"] == f[t] - t + 1 == 3
    assert out["cnf_sha256"] == res["cnf_sha256"]
    # the CLI agrees
    rc = subprocess.run([sys.executable, str(Path(oc.__file__)), "check-expansion", str(tmp_path / "instance.mosp"),
                         str(cert)], capture_output=True, text=True)
    assert rc.returncode == 0 and "verdict: verified" in rc.stdout
    # damaged 1: the certificate claims one more than it proves (b + 1): the CNF hash no longer matches
    d = json.loads(cert.read_text())
    d["b"] = d["b"] - 1
    (tmp_path / "damaged_b.json").write_text(json.dumps(d))
    out = oc.check_expansion(tmp_path / "instance.mosp", tmp_path / "damaged_b.json")
    assert out["verdict"] == "rejected"
    assert any(c["check"].startswith("CNF SHA-256") and not c["ok"] for c in out["checks"])
    # damaged 2: a truncated proof with its hash "corrected": drat-trim rejects it
    proof = gzip.open(tmp_path / f"t{t}_b{f[t] - 1}.drat.gz").read()
    cut = proof[: len(proof) // 2]
    with gzip.open(tmp_path / "cut.drat.gz", "wb") as fh:
        fh.write(cut)
    d2 = json.loads(cert.read_text())
    d2["proof_file"] = "cut.drat.gz"
    d2["proof_sha256"] = hashlib.sha256(cut).hexdigest()
    (tmp_path / "damaged_proof.json").write_text(json.dumps(d2))
    out = oc.check_expansion(tmp_path / "instance.mosp", tmp_path / "damaged_proof.json")
    assert out["verdict"] == "rejected"
    assert any(c["check"].startswith("drat-trim") and not c["ok"] for c in out["checks"])
    # damaged 3: a different instance under the same certificate: the rows hash fails
    other = _cycle_instance(n)
    other[0, 5] = 1
    oe.write_standard_instance(tmp_path / "other.mosp", "cycle11", other)
    out = oc.check_expansion(tmp_path / "other.mosp", cert)
    assert out["verdict"] == "rejected"
    assert any(c["check"].startswith("instance rows") and not c["ok"] for c in out["checks"])


def test_checker_cnf_hash_equals_the_search_cnf_hash(small_corpus):
    """Two encoders written separately from the same contract give the same
    canonical CNF on 20 corpus instances at several `(t, b)`."""
    oc = _checker()
    for nm, matrix, _, _ in small_corpus[:20]:
        n = matrix.shape[0]
        closed = oe.closed_masks_from_matrix(matrix)
        rows = matrix.tolist()
        closed_sets = oc.closed_neighbourhoods(rows)
        assert [sorted(s) for s in closed_sets] == [oe.mask_to_list(c) for c in closed], nm
        assert oc.rows_sha256(rows) == oe.matrix_sha256(matrix)
        for t, b in ((1, 0), (2, n // 2), (n // 2, n // 2), (n - 1, n - 2), (n, n - 1)):
            c1, nv1 = oe.expansion_cnf(closed, t, b)
            c2, nv2 = oc.expansion_cnf(closed_sets, t, b)
            assert nv1 == nv2 and c1 == c2, (nm, t, b)
            assert oe.cnf_sha256(c1, nv1) == oc.cnf_sha256(c2, nv2)


def test_checker_shares_only_the_spec():
    """The checker imports none of the four project packages, and its docstring
    carries the contract verbatim."""
    oc = _checker()
    src = Path(oc.__file__).read_text()
    for pkg in ("learning", "satisfiability", "pathwidth_solver", "mosp"):
        assert f"from {pkg}" not in src and f"import {pkg}" not in src, pkg
    spec = oe.ENCODING_SPEC.strip()
    assert spec in oc.__doc__, "the contract in the checker's docstring drifted from ENCODING_SPEC"


def test_committed_sat_files():
    inst = SCRATCH / "03_sat" / "instances.csv"
    if not inst.exists():
        pytest.skip("item 03's instances.csv is not on disk")
    i = pd.read_csv(inst)
    assert i["instance_name"].is_unique
    assert (i["floor_after"] <= i["optimum"]).all(), "a SAT floor above a certified optimum"
    assert (i["floor_after"] <= i["ceiling_after"]).all(), "a floor above the ceiling"
    assert (i["floor_after"] >= i["floor_before"]).all()
    assert (i["ceiling_after"] <= i["ceiling_record"]).all()
    levels = SCRATCH / "03_sat" / "levels.csv"
    if levels.exists():
        c = pd.read_csv(levels)
        u = c[c["status"] == "unsat"]
        assert (u["verdict"] == "verified").all(), "an UNSAT answer drat-trim did not verify"
        assert (u["b"] + 1 <= u["optimum"] + u["t"] - 1).all(), "an UNSAT at (t, b) with b + 2 - t above the optimum"
        s = c[c["status"] == "sat"]
        assert (s["nbhd"] <= s["b"]).all()
