"""loop0010 item 04: the planner's regimes, the Faggioli-Bentivoglio cell parser,
the floor flags against an exact-rational recomputation of the union bound, and
the join of every certification record on synthetic files."""

from fractions import Fraction
from math import comb

import numpy as np
import pandas as pd
import pytest

from learning.excess import giant_threshold_excess
from learning.excess_scoop import (corpus_floor_table, fb_cell, floor_columns, join_records, node_count_records,
                                   regime_of, sweep_records)


def test_regimes_in_order():
    assert regime_of(0.3, 1.0, forest=True) == "forest"
    assert regime_of(5.0, 1.0, forest=True) == "forest"            # a forest is a forest at any excess
    assert regime_of(0.3, 1.0) == "below e_g"                      # e_g(1) = 0.618
    assert regime_of(0.8, 1.0) == "[e_g, 1)"
    assert regime_of(0.5, 0.25) == "[e_g, 1)"                      # e_g(1/4) = 0.39
    assert regime_of(0.3, 0.25) == "below e_g"
    assert regime_of(1.0, 1.0) == "[1, 2)"
    assert regime_of(1.99, 1.0) == "[1, 2)"
    assert regime_of(2.0, 1.0) == "ridge [2, 2.4]"
    assert regime_of(2.4, 1.0) == "ridge [2, 2.4]"
    assert regime_of(2.41, 1.0) == "> 2.4"
    assert giant_threshold_excess(1.0) == pytest.approx(0.618, abs=1e-3)


def test_fb_cell_reads_the_nominal_sizes():
    assert fb_cell("p1050n3_0") == (10, 50)
    assert fb_cell("p4010n10_0") == (40, 10)
    assert fb_cell("scoop-B_REVAL_145_0") is None


def _exact_union_bound(n: int, sizes: dict, k: int) -> Fraction:
    """The first-moment union bound on P(pw <= k) with exact rationals, written
    independently of `learning.first_moment` (`t = ceil((n - k) / 2)`)."""
    t = (n - k + 1) // 2
    b = Fraction(comb(n, t) * comb(n - t, t - 1))
    for s, c in sizes.items():
        b *= Fraction(comb(n - t, s) + comb(n - t + 1, s) - comb(n - 2 * t + 1, s), comb(n, s)) ** c
    return b


def test_floor_flags_against_exact_rationals():
    # scoop-B_REVAL_145_0's size law: 60 customers, 49 patterns of sizes 1..6.
    n, sizes = 60, {1: 1, 2: 13, 3: 15, 4: 11, 5: 8, 6: 1}
    k01 = max(k for k in range(n) if _exact_union_bound(n, sizes, k) < Fraction(1, 100))
    k1 = max(k for k in range(n) if _exact_union_bound(n, sizes, k) < 1)
    frame = pd.DataFrame({"n": [n, n], "m": [49, 49], "sizes": ["1:1;2:13;3:15;4:11;5:8;6:1"] * 2,
                          "optimum": [7.0, 9.0]})
    out = floor_columns(frame)
    assert list(out["floor_lt001"]) == [k01 + 2, k01 + 2] == [9, 9]
    assert list(out["floor_lt1"]) == [k1 + 2, k1 + 2] == [11, 11]
    assert list(out["below_floor_001"]) == [True, False]
    assert list(out["below_floor_1"]) == [True, True]
    assert out["beta_star"].iloc[0] > 0                               # e = (162 - 49) / 60 > 1
    assert out["beta_star_n"].iloc[0] == pytest.approx(out["beta_star"].iloc[0] * n)


def test_floor_is_trivial_below_the_threshold():
    # one pattern of size 2 on 5 customers: the union bound never drops below 1
    out = floor_columns(pd.DataFrame({"n": [5], "m": [1], "sizes": ["2:1"], "optimum": [2.0]}))
    assert out["floor_lt1"].iloc[0] == 1 and out["floor_lt001"].iloc[0] == 1
    assert not out["below_floor_1"].iloc[0]
    assert out["beta_star"].iloc[0] == 0.0


@pytest.fixture
def records(tmp_path):
    results = tmp_path / "results"
    results.mkdir()
    cols = "dataset,filename,instance_name,n_customers,n_patterns,mosp_value,verified,time_seconds,status,error\n"
    (results / "first.csv").write_text(cols + "S,a.txt,A,105,37,,,60.0,timeout,\nS,b.txt,B,60,49,7,7,16.2,solved,\n")
    (results / "second.csv").write_text(cols + "S,a.txt,A,105,37,12,12,116.0,solved,\nS,b.txt,B,60,49,7,7,0.2,solved,\n")
    ledger = tmp_path / "ledger.csv"
    ledger.write_text("when,driver,instance,seconds,nodes\n2026-09-18,csearch,Other,2.0,\n")
    nc = tmp_path / "node_counts.csv"
    nc.write_text("instance_name,source_file,collection,n_customers,n_patterns,optimum,config,status,nodes,seconds\n"
                  "A,a.txt,S,105,37,12,default,unsat,500,0.01\nA,a.txt,S,105,37,12,csearch,unsat,400,0.01\n")
    diff = tmp_path / "differential.csv"
    diff.write_text("base_name,labelling,instance_name,source,cell,class,n,m,optimum,config,sides,better_move,"
                    "status_lo,nodes_lo,seconds_lo,status_hi,nodes_hi,seconds_hi,witness_value,witness_ok\n"
                    "B,identity,B,corpus,S,S,60,49,7,default,both,False,unsat,1881,0.002,sat,143,0.001,7,True\n"
                    "B,relabel0,B#0,corpus,S,S,60,49,7,default,both,False,unsat,1770,0.002,sat,140,0.001,7,True\n"
                    "B,relabel1,B#1,corpus,S,S,60,49,7,default,both,False,unsat,1928,0.002,sat,150,0.001,7,True\n"
                    "B,identity,B,corpus,S,S,60,49,7,csearch,both,True,unknown,1593,120.0,sat,121,0.001,7,True\n")
    cert = tmp_path / "cert.csv"
    cert.write_text("instance_name,config,k,status,nodes,check_ok\nB,default,6,unsat,68368,True\nB,csearch,6,unsat,12742,False\n")
    proofs = tmp_path / "proofs.csv"
    proofs.write_text("instance_name,k,status,verdict,solve_seconds,conflicts\nA,11,unsat,verified,0.5,1234\n")
    return dict(results_dir=results, files=("first.csv", "second.csv"), ledger=ledger, node_counts=nc,
                differential=diff, certificate=cert, proofs=proofs)


def test_sweep_takes_the_first_solved_row(records):
    s = sweep_records(["A", "B", "C"], results_dir=records["results_dir"], files=records["files"])
    s = s.set_index("instance_name")
    assert s.loc["A", "certified_by"] == "second" and s.loc["A", "certified_seconds"] == 116.0
    assert s.loc["B", "certified_by"] == "first" and s.loc["B", "certified_seconds"] == 16.2   # the 0.2 s is a cache hit
    assert s.loc["C", "certified_by"] == "" and np.isnan(s.loc["C", "certified_seconds"])
    assert s.loc["A", "first_status"] == "timeout"


def test_node_counts_prefer_the_small_size_file_and_flag_censoring(records):
    nc = node_count_records(["A", "B", "C"], node_counts=records["node_counts"],
                            differential=records["differential"]).set_index("instance_name")
    assert nc.loc["A", "nodes_source_default"] == "node_counts" and nc.loc["A", "nodes_default"] == 500
    assert nc.loc["B", "nodes_source_default"] == "differential_scale (identity)"
    assert nc.loc["B", "nodes_default"] == 1881
    assert (nc.loc["B", "nodes_default_labelling_min"], nc.loc["B", "nodes_default_labelling_max"]) == (1770, 1928)
    assert nc.loc["B", "status_csearch"] == "unknown"                 # censored: kept, flagged, never a value
    assert nc.loc["C", "nodes_source_default"] == "not recorded" and np.isnan(nc.loc["C", "nodes_default"])


def test_join_records_one_row_per_instance(records):
    j = join_records(["A", "B", "C"], **records).set_index("instance_name")
    assert len(j) == 3
    assert list(j["ledger_rows"]) == [0, 0, 0]                        # the ledger has no row for any of them
    assert j.loc["A", "drat_verdict"] == "verified" and j.loc["A", "drat_conflicts"] == 1234
    assert j.loc["B", "drat_verdict"] == ""
    assert j.loc["B", "cert_nodes_default"] == 68368 and j.loc["B", "cert_ok_default"] == "ok"
    assert j.loc["B", "cert_ok_csearch"] == "FAIL"
    assert j.loc["C", "cert_ok_default"] == ""


def test_corpus_floor_table_counts_from_a_synthetic_rule_frame():
    rule = pd.DataFrame({
        "source": ["corpus"] * 4 + ["ensemble"], "certified": [True, True, True, False, True],
        "generator": ["chu_stuckey", "SCOOP", "Harvey", "SCOOP", "fixed"],
        "cell": ["Random-60-60-4", "SCOOP", "wbo_10_10", "SCOOP", "f"],
        "n": [60, 60, 5, 60, 60], "sizes": ["1:1;2:13;3:15;4:11;5:8;6:1"] * 2 + ["2:1"] * 3,
        "optimum": [12.0, 7.0, 2.0, 7.0, 7.0],
    })
    t = corpus_floor_table(rule).set_index("collection")
    assert set(t.index) == {"Chu & Stuckey", "SCOOP", "Harvey"}            # uncertified and ensemble rows dropped
    assert t.loc["SCOOP", "below_floor_001"] == 1 and t.loc["SCOOP", "largest_shortfall_001"] == 2   # 9 - 7
    assert t.loc["Chu & Stuckey", "below_floor_001"] == 0 and t.loc["Chu & Stuckey", "below_floor_1"] == 0
    assert t.loc["Harvey", "below_floor_1"] == 0 and t.loc["Harvey", "largest_shortfall_001"] == 0
