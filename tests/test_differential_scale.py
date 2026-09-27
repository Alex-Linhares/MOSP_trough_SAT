"""Guards on the budgeted differential harness above 40 (`learning.differential_scale`).

The run itself is compute; what is tested here is everything around it that
could silently misreport: the per-cell sample is the first eight by index and
certified only; a censored or missing record is priced at the full deadline
and a settled one is inflated and capped; the schedule keeps every witness
call and adds refutations cheapest instance first within the budget; a job
list is dearest first and skips what is recorded; `run_sides` on a hand
instance gives the certificate's statuses under both configurations and a
`skipped` side where the schedule says so; the per-instance verdict never
turns a censored or skipped call into a disagreement; and the spread table's
arithmetic is right by hand, with censored bases counted and excluded.
"""

import numpy as np
import pandas as pd

from learning.differential_scale import (
    CONFIGS,
    band,
    build_jobs,
    recorded_sides,
    instance_class,
    predicted_call_seconds,
    run_sides,
    sample_per_cell,
    schedule,
    spread_table,
    summaries,
)
from mosp.instance import MOSPInstance
from tests.test_differential import OPTIMUM, SPIDER


def _spider() -> MOSPInstance:
    return MOSPInstance.from_matrix(SPIDER, name="spider")


def test_sample_per_cell_takes_the_first_eight_certified_by_index():
    frame = pd.DataFrame({
        "cell": ["a"] * 12 + ["b"] * 3,
        "index": list(range(11, -1, -1)) + [2, 0, 1],
        "certified": [True] * 10 + [False, False] + [True, True, False],
    })
    picked = sample_per_cell(frame, 8)
    assert list(picked[picked.cell == "a"]["index"]) == list(range(2, 10))   # 0 and 1 are uncertified
    assert list(picked[picked.cell == "b"]["index"]) == [0, 2]


def test_predicted_seconds_cap_inflate_and_price_censored_at_the_deadline():
    assert predicted_call_seconds(None, None, 300) == 300
    assert predicted_call_seconds(120.0, "unknown", 300) == 300
    assert predicted_call_seconds(10.0, "unsat", 300, inflation=1.3) == 13.0
    assert predicted_call_seconds(0.0001, "unsat", 300, floor=0.01) == 0.01
    assert predicted_call_seconds(1000.0, "unsat", 300) == 300


def _priced():
    rows = []
    for name, lo in (("cheap", 10.0), ("mid", 100.0), ("dear", 1000.0)):
        for config in CONFIGS:
            rows.append({"instance_name": name, "config": config, "n": 75, "m": 75,
                         "source": "corpus", "class": "x", "optimum": 5,
                         "predicted_lo_seconds": lo, "predicted_hi_seconds": 1.0,
                         "recorded_lo_status": "unsat", "recorded_lo_seconds": lo / 5,
                         "record": "recorded", "labellings": 5})
    return pd.DataFrame(rows)


def test_schedule_keeps_every_witness_and_adds_refutations_cheapest_first():
    priced = _priced()
    # budget: 6 witness seconds + cheap (20) + mid (200) fits in 300 s; dear (2000) does not
    out = schedule(priced, budget_core_hours=300 / 3600.0)
    assert out.run_hi.all()
    assert set(out[out.run_lo].instance_name) == {"cheap", "mid"}
    assert not out[out.instance_name == "dear"].run_lo.any()
    assert abs(out.scheduled_seconds.sum() - (6 + 20 + 200)) < 1e-9
    # a reserve shrinks the budget
    out = schedule(priced, budget_core_hours=300 / 3600.0, reserve_seconds=200)
    assert set(out[out.run_lo].instance_name) == {"cheap"}


def test_build_jobs_is_dearest_first_and_skips_recorded_triples():
    priced = schedule(_priced(), budget_core_hours=300 / 3600.0)
    jobs = [{"instance_name": n, "source": "corpus", "class": "x", "optimum": 5, "matrix": [[1]]}
            for n in ("cheap", "mid", "dear")]
    args = build_jobs(jobs, priced, relabellings=1, deadline=300,
                      done={("cheap", "identity", "default")})
    names = [a[0]["instance_name"] for a in args]
    assert len(args) == 3 * 2 * 2 - 1
    assert names[0] == "mid" and names[-1] == "dear"           # mid costs 101, cheap 11, dear 1 (witness only)
    assert {a[3] for a in args if a[0]["instance_name"] == "dear"} == {("hi",)}
    assert {a[3] for a in args if a[0]["instance_name"] == "mid"} == {("lo", "hi")}


def test_run_sides_matches_the_certificate_and_records_a_skipped_side():
    inst = _spider()
    for config in CONFIGS:
        row = run_sides(inst, OPTIMUM, config, ("lo", "hi"), 30.0)
        assert row["status_lo"] == "unsat" and row["status_hi"] == "sat"
        assert row["witness_value"] == OPTIMUM and row["witness_ok"] is True
        assert row["nodes_lo"] > 0 and row["sides"] == "lo+hi"
    row = run_sides(inst, OPTIMUM, "default", ("hi",), 30.0)
    assert row["status_lo"] == "skipped" and np.isnan(row["nodes_lo"])
    assert row["status_hi"] == "sat" and row["witness_ok"] is True


def _rows(**over):
    base = {"base_name": "b", "source": "corpus", "class": "x", "n": 75, "m": 75, "optimum": 5,
            "status_lo": "unsat", "nodes_lo": 10, "seconds_lo": 0.1,
            "status_hi": "sat", "nodes_hi": 3, "seconds_hi": 0.01, "witness_ok": True}
    return dict(base, **over)


def test_summaries_never_turn_censored_or_skipped_into_a_disagreement():
    rows = pd.DataFrame([
        _rows(labelling="identity", config="default"),
        _rows(labelling="relabel0", config="default", status_lo="unknown", nodes_lo=999),
        _rows(labelling="identity", config="csearch", status_lo="skipped", nodes_lo=np.nan,
              seconds_lo=np.nan),
        _rows(labelling="relabel0", config="csearch"),
    ])
    s = summaries(rows)
    assert len(s) == 1
    rec = s.iloc[0]
    assert not rec.disagreement and not rec.contradiction
    assert rec.unknown_lo == 1 and rec.refutation_run
    # a settled `sat` below the optimum on one labelling is a disagreement and a contradiction
    rows.loc[3, "status_lo"] = "sat"
    rec = summaries(rows).iloc[0]
    assert rec.disagreement and rec.contradiction and "relabel0/csearch@lo" in rec.disagreeing


def test_spread_table_by_hand_counts_censored_bases_and_excludes_them():
    rows = pd.DataFrame([
        _rows(base_name="a", labelling="identity", config="default", nodes_lo=9),
        _rows(base_name="a", labelling="relabel0", config="default", nodes_lo=4),
        _rows(base_name="a", labelling="relabel1", config="default", nodes_lo=19),
        _rows(base_name="c", labelling="identity", config="default", nodes_lo=9),
        _rows(base_name="c", labelling="relabel0", config="default", status_lo="unknown", nodes_lo=900),
        _rows(base_name="c", labelling="relabel1", config="default", nodes_lo=9),
    ])
    t = spread_table(rows, "lo")
    assert len(t) == 1
    rec = t.iloc[0]
    assert rec.bases == 1 and rec["bases with a censored labelling"] == 1
    assert rec["max/min median"] == 4.0 and rec["identity/min median"] == 2.0
    assert rec["bases with any change"] == 1 and rec["band"] == "61-75"


def test_band_and_class_names():
    assert band(50) == "50" and band(60) == "51-60" and band(75) == "61-75"
    assert band(82) == "76-99" and band(100) == "100"
    assert instance_class("Random-100-100-2-4_0", "corpus", "") == "Random-100-100-2"
    assert instance_class("GP5:  100 customers", "corpus", "") == "Challenge"
    assert instance_class("ens_f_n75_m75_d3_i001", "campaign", "f_n75_m75_d3") == "f_n75_m75_d3"
    assert instance_class("SCOOP-something", "corpus", "") == "SCOOP/other"


def test_resume_runs_only_the_side_still_missing():
    priced = schedule(_priced(), budget_core_hours=300 / 3600.0)
    jobs = [{"instance_name": "mid", "source": "corpus", "class": "x", "optimum": 5, "matrix": [[1]]}]
    recorded = pd.DataFrame([{"base_name": "mid", "labelling": "identity", "config": "default", "sides": "hi"},
                             {"base_name": "mid", "labelling": "relabel0", "config": "default", "sides": "lo+hi"}])
    done = recorded_sides(recorded)
    assert done[("mid", "identity", "default")] == {"hi"}
    args = build_jobs(jobs, priced, relabellings=1, deadline=300, done=done)
    sides = {(a[1], a[2]): a[3] for a in args}
    assert sides[("identity", "default")] == ("lo",)            # the witness is on record, the refutation is not
    assert ("relabel0", "default") not in sides                  # both sides on record
    assert sides[("identity", "csearch")] == ("lo", "hi")        # nothing on record
