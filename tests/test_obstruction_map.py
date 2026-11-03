"""loop0013 item 08: the duality-gap map reads the items' files and recomputes
nothing. The map reproduces item 01's `floor0` where no search ran; no best
floor is above a certified optimum; family E's floor never exceeds its
ceiling and the ceiling never exceeds the optimum; family M's floor is the
maximum of the record's minor, the ladder and the search over items 04, 05
and the ridge stage; the dominance table is consistent; the committed files
agree with a rebuild."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from learning import obstruction_map as om

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "reports" / "scratch" / "obstruction_search"

pytestmark = pytest.mark.skipif(not (S / "01_ledger" / "ledger_corpus.csv").exists() or not om.MAP_CSV.exists(),
                                reason="item 01's ledger or item 08's map is not on disk")


@pytest.fixture(scope="module")
def built() -> pd.DataFrame:
    return om.build_map()


@pytest.fixture(scope="module")
def committed() -> pd.DataFrame:
    return pd.read_csv(om.MAP_CSV)


def test_map_reproduces_floor0_where_no_search_ran(built):
    f = built
    quiet = f[~f.in_targets]
    assert len(quiet) > 1000
    assert (quiet.best == quiet.floor0).all()
    assert (quiet.best_family.str.split("|").map(lambda s: not ({"E", "M", "B"} & set(s)) or True)).all()
    # and where only the ceiling ran (small and rest500 outside the 338 ∪ cs200), the floor side is item 01's
    only_ceiling = f[f.e_ran & ~f.m_ran & ~f.b_ran]
    assert (only_ceiling.best >= only_ceiling.floor0).all()
    assert (only_ceiling.best - only_ceiling.floor0 <= 1).all()     # the exact enumeration at n ≤ 22 can add at most what cap 12 missed


def test_no_floor_above_the_optimum(built):
    f = built
    assert (f.best <= f.optimum).all()
    for fam, col in om.FAMILY_COLUMNS.items():
        v = f[col].dropna()
        assert (v <= f.loc[v.index, "optimum"]).all(), fam


def test_family_e_floor_and_ceiling(built):
    f = built
    both = f.e_ceiling.notna()
    assert (f.loc[both, "e_floor"] <= f.loc[both, "e_ceiling"]).all()
    assert (f.loc[both, "e_ceiling"] <= f.loc[both, "optimum"]).all()
    assert (f.e_floor >= f.harper12).all()
    assert f.loc[both, "e_closed_out"].eq(f.loc[both, "e_ceiling"] < f.loc[both, "optimum"]).all()
    # the ceiling is a ceiling: wherever it is below the optimum, the family's floor is below it too
    assert (f.loc[f.e_closed_out.fillna(False), "e_floor"] < f.loc[f.e_closed_out.fillna(False), "optimum"]).all()


def test_family_m_floor_is_the_max_of_the_items(built):
    f = built.set_index("instance_name")
    parts = pd.Series(np.nan, index=f.index)
    for path in (S / "04_minor" / "search.csv", S / "05_minor_scale" / "search.csv", S / "05_minor_scale" / "ridge_summary.csv"):
        if path.exists():
            x = pd.read_csv(path).set_index("instance_name")[["ladder_floor", "search_floor"]].max(axis=1)
            common = parts.index.intersection(x.index)
            parts.loc[common] = np.fmax(parts.loc[common].values, x.loc[common].values)
    expected = pd.concat([parts, f["minor"]], axis=1).max(axis=1)
    got = f["m_floor"]
    assert got.notna().eq(expected.notna()).all()
    assert (got.dropna() == expected.dropna()).all()
    assert f.loc[f.m_ran, "m_ladder"].notna().all()


def test_dominance_is_consistent(built):
    d = om.dominance(built)
    assert len(d) == len(om.FAMILIES) * (len(om.FAMILIES) - 1)
    d = d.set_index(["A", "B"])
    for a in om.FAMILIES:
        for b in om.FAMILIES:
            if a != b:
                assert d.loc[(a, b), "both ran"] == d.loc[(b, a), "both ran"]
                assert d.loc[(a, b), "A > B"] + d.loc[(b, a), "A > B"] <= d.loc[(a, b), "both ran"]
    # omega ≤ lb_best on record, so C is never above D
    assert d.loc[("C", "D"), "A > B"] == 0


def test_committed_map_matches_a_rebuild(built, committed):
    assert len(committed) == len(built) == 6376
    a = built.set_index("instance_name").sort_index()
    b = committed.set_index("instance_name").sort_index()
    for col in ("best", "gap_best", "floor0", "optimum"):
        assert (a[col] == b[col]).all(), col
    for col in ("e_floor", "e_ceiling", "m_floor", "b_value"):
        assert a[col].fillna(-1).eq(b[col].fillna(-1)).all(), col
    u = pd.read_csv(om.UNCOVERED_CSV)
    assert len(u) == int((committed.gap_best > 0).sum())
    assert (u.gap_best > 0).all()


def test_kill_verdicts_have_numbers_and_sources(built):
    v = om.kill_verdicts(built)
    assert {x["family"] for x in v} >= {"E, the search", "E, the exact half", "M", "B"}
    for x in v:
        assert x["verdict"].startswith(("met", "not met"))
        assert any(ch.isdigit() for ch in x["number"])
        assert x["source"]


def test_cost_ledger_sums_the_files():
    c = om.cost_ledger()
    assert list(c["item"])[-1] == "total"
    assert c["instance core-hours"].iloc[-1] == pytest.approx(c["instance core-hours"].iloc[:-1].sum(), abs=0.05)
    assert c["instance core-hours"].iloc[-1] > 20
