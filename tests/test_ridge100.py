"""Tests for `learning.ridge100` (loop0004 item 07): the cell's identity, the
scheduler's state machine and priorities, the censored summary, the audit."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from learning import ridge100
from learning.ridge100 import (CALL_COLUMNS, CELL, audit, cell_summary, check_against_upward,
                               heuristic_upper_bounds, instance_states, law_prediction, manifest,
                               next_jobs, per_instance)
from mosp.instance import MOSPInstance


def _calls(rows):
    frame = pd.DataFrame(rows, columns=CALL_COLUMNS)
    return frame


def test_manifest_shares_sec16_sample_and_digests_agree():
    man = manifest(per_cell=6)
    assert list(man["index"]) == list(range(6))
    assert man["instance_name"].iloc[0] == "ens_f_n100_m100_d3_i000"
    # i000-i004 are §16's sample, byte for byte; i005 is new
    assert check_against_upward(man) == 5


def test_instance_states_descent_and_certification():
    ubs = {"a": 6, "b": 6, "c": 6, "d": 6}
    calls = _calls([
        # a: UB 6, sat at 5 (achieved 5), sat at 4 (achieved 3!), unsat at 2 under csearch
        {"instance_name": "a", "purpose": "descent", "config": "csearch", "k": 5, "status": "sat", "nodes": 1, "achieved": 5},
        {"instance_name": "a", "purpose": "descent", "config": "csearch", "k": 4, "status": "sat", "nodes": 1, "achieved": 3},
        {"instance_name": "a", "purpose": "descent", "config": "csearch", "k": 2, "status": "unsat", "nodes": 9},
        # b: descent censored at 5
        {"instance_name": "b", "purpose": "descent", "config": "csearch", "k": 5, "status": "unknown", "nodes": 7},
        # c: certified and the default refutation done (censored)
        {"instance_name": "c", "purpose": "descent", "config": "csearch", "k": 5, "status": "unsat", "nodes": 3},
        {"instance_name": "c", "purpose": "refute", "config": "default", "k": 5, "status": "unknown", "nodes": 4},
        # d: a disagreement, recorded never hidden
        {"instance_name": "d", "purpose": "descent", "config": "csearch", "k": 5, "status": "unsat", "nodes": 3},
        {"instance_name": "d", "purpose": "refute", "config": "default", "k": 5, "status": "sat", "nodes": 4, "achieved": 5},
    ])
    s = instance_states(calls, ubs)
    assert s["a"] == {"value": 3, "certified": True, "descent_censored": False, "default_done": False, "disagreement": False}
    assert s["b"]["value"] == 6 and not s["b"]["certified"] and s["b"]["descent_censored"]
    assert s["c"]["certified"] and s["c"]["default_done"]
    assert s["d"]["disagreement"]


def test_next_jobs_priority_and_running_exclusion():
    ubs = {"x": 5, "y": 5, "z": 5}
    calls = _calls([
        {"instance_name": "y", "purpose": "descent", "config": "csearch", "k": 4, "status": "unsat", "nodes": 1},
        {"instance_name": "z", "purpose": "descent", "config": "csearch", "k": 4, "status": "unknown", "nodes": 1},
    ])
    s = instance_states(calls, ubs)
    jobs = next_jobs(s, ["z", "y", "x"], running=set())
    # x's descent step comes before y's default refutation whatever the order; z is done (censored)
    assert jobs == [("x", "descent", "csearch", 4), ("y", "refute", "default", 4)]
    assert next_jobs(s, ["x", "y"], running={("x", "descent", "csearch", 4)}) == [("y", "refute", "default", 4)]
    # once y's default call is recorded nothing is pending for it
    calls2 = pd.concat([calls, _calls([{"instance_name": "y", "purpose": "refute", "config": "default", "k": 4,
                                        "status": "unsat", "nodes": 2}])])
    assert next_jobs(instance_states(calls2, ubs), ["x", "y"], running=set()) == [("x", "descent", "csearch", 4)]


def test_heuristic_upper_bounds_on_a_chain():
    # three customers on a path of patterns: optimum 2, every strategy reaches it
    inst = MOSPInstance.from_matrix([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]], name="chain")
    ubs, ordering = heuristic_upper_bounds(inst)
    assert ubs["ub_best"] == 2
    assert sorted(ordering) == [0, 1, 2, 3]
    for name in ridge100.UB_STRATEGIES:
        assert ubs[f"ub_{name}"] == 2


def test_law_prediction_numbers():
    law = law_prediction(100)
    assert law["constant"] == pytest.approx(6.78 + 0.0951 * 25, abs=1e-9)
    assert law["drifting"] == pytest.approx(6.78 + 0.0951 * 25 - 0.5 * 0.000217 * 625, abs=1e-9)
    cs = law_prediction(100, "csearch")
    assert cs["constant"] == pytest.approx(6.662 + 0.0924 * 25, abs=1e-9)
    assert law["sec11_law"] == pytest.approx(-0.191 + 9.51, abs=1e-9)


def test_cell_summary_censored_median_by_hand():
    table = pd.DataFrame({
        "log_nodes_default": [9.0, 9.5, 10.0, np.nan],
        "censored_default": [False, True, False, np.nan],
    })
    s = cell_summary(table, "default")
    assert s["n_counts"] == 3 and s["settled"] == 2 and s["censored"] == 1
    assert s["median_log_nodes"] == 9.5 and s["median_is_lower_bound"] is True
    assert s["min_settled"] == 9.0 and s["max_settled"] == 10.0 and s["max_censored"] == 9.5
    table.loc[1, "censored_default"] = False
    assert cell_summary(table, "default")["median_is_lower_bound"] is False


def test_per_instance_and_audit_with_a_real_witness(tmp_path: Path):
    from learning.ensemble import generate
    inst = generate(CELL, 0)
    ubs, ordering = heuristic_upper_bounds(inst, strategies=("cs-dfs",))
    ub = ubs["ub_best"]
    ridge100.save_witness(inst, ub, ordering, certified=False, solutions_dir=tmp_path)
    saved = json.loads((tmp_path / f"{inst.name}.json").read_text())
    assert saved["mosp_value"] == ub and saved["provenance"] == "solution"
    price = pd.DataFrame([{"instance_name": inst.name, "index": 0, "ub_best": ub, "lb_best": 1,
                           "graph_cert": "g", "g_components": 1, "pred_log_nodes_default": 9.9}])
    calls = _calls([
        {"instance_name": inst.name, "purpose": "descent", "config": "csearch", "k": ub - 1, "status": "unsat",
         "nodes": 10 ** 9 - 1, "seconds": 500.0},
        {"instance_name": inst.name, "purpose": "refute", "config": "default", "k": ub - 1, "status": "unknown",
         "nodes": 10 ** 9 - 1, "seconds": 2400.0},
    ])
    ridge100.save_witness(inst, ub, ordering, certified=True, solutions_dir=tmp_path)
    table = per_instance(calls, price)
    assert table.iloc[0]["status"] == "certified" and table.iloc[0]["value"] == ub
    assert table.iloc[0]["log_nodes_csearch"] == 9.0 and not table.iloc[0]["censored_csearch"]
    assert table.iloc[0]["log_nodes_default"] == 9.0 and table.iloc[0]["censored_default"]
    aud = audit(calls, price, solutions_dir=tmp_path)
    assert aud["certified"] == 1 and aud["witness_ok"] == 1 and aud["witness_bad"] == 0
    assert aud["default_censored"] == 1 and aud["disagreements"] == 0 and aud["certified_provenance"] == 1
    # a save at a higher value never demotes the certified witness
    ridge100.save_witness(inst, ub + 1, ordering, certified=False, solutions_dir=tmp_path)
    again = json.loads((tmp_path / f"{inst.name}.json").read_text())
    assert again["mosp_value"] == ub and again["provenance"] == "certified:refutation"


def test_refute_censored_dispatches_nothing_when_nothing_is_censored(tmp_path: Path):
    price = pd.read_csv(ridge100.PRICE_CSV)
    calls = _calls([{"instance_name": n, "purpose": "descent", "config": "csearch", "k": int(u) - 1,
                     "status": "unsat", "nodes": 1, "seconds": 1.0}
                    for n, u in zip(price["instance_name"], price["ub_best"])])
    csv = tmp_path / "calls.csv"
    calls.to_csv(csv, index=False)
    out = ridge100.refute_censored(workers=1, deadline=1.0, calls_csv=csv, verbose=False)
    assert len(out) == len(price)                      # no call was made
    assert (out["status"] == "unsat").all()
