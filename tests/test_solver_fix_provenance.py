"""loop0007 item 06: the list of values that rest only on the customer search.

`paper1/solver_fix_provenance.py` writes the list; these tests re-read the
records it was built from and check the list against them, so a regenerated
list that drops an instance with no independent proof, or keeps one that has
one, fails here.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from paper1 import solver_fix_provenance as prov

ROOT = Path(__file__).resolve().parent.parent
LIST = ROOT / "paper1/data/solver_fix_provenance.csv"
ALL = ROOT / "paper1/data/solver_fix_provenance_all.csv.gz"

pytestmark = pytest.mark.skipif(not LIST.exists() or not ALL.exists(),
                                reason="run python -m paper1.solver_fix_provenance first")


@pytest.fixture(scope="module")
def listed() -> pd.DataFrame:
    return pd.read_csv(LIST)


@pytest.fixture(scope="module")
def everything() -> pd.DataFrame:
    return pd.read_csv(ALL)


def test_every_listed_value_is_still_the_stored_certified_value(listed):
    for r in listed.itertuples(index=False):
        data = json.loads((ROOT / r.solution_file).read_text())
        assert data["mosp_value"] == r.value, r.instance_name
        assert data["provenance"] == "certified:refutation", r.instance_name


def test_no_listed_instance_has_an_independent_proof(listed):
    drat, lattice = prov._drat(), prov._lattice()
    sat, _ = prov._sat_sweeps(set())
    races = prov._races()
    for r in listed.itertuples(index=False):
        assert (r.value - 1) not in drat.get(r.instance_name, ()), r.instance_name
        assert lattice.get(r.instance_name) != r.value, r.instance_name
        assert r.value not in sat.get(r.instance_name, ()), r.instance_name
        assert r.value not in races.get(r.instance_name, ()), r.instance_name
        assert r.lb_best < r.value, r.instance_name


def test_every_certified_instance_is_either_listed_or_independently_proved(listed, everything):
    certified = everything[everything.certified]
    independent = set(certified.loc[certified.independent, "instance_name"])
    names = set(listed.instance_name)
    assert names.isdisjoint(independent)
    assert names | independent == set(certified.instance_name)


def test_no_proved_bound_sits_above_a_stored_value(everything):
    assert not everything.bound_above_value.any()


def test_every_listed_instance_is_above_the_lattice_and_drat_range(listed):
    # The lattice covers n <= 15 and DRAT reaches into n <= 40: nothing small
    # should be on the list except where DRAT ran out of budget.
    assert listed.n_customers.min() >= 40
