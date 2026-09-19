"""Guards on the recorded lower bound.

The bound is new state in a published artifact, and it is dangerous in a way the
value is not: a value that is too low is caught the moment its witness is
simulated, while a bound that is too high is caught by nothing at all -- it would
make a descent stop early and record a wrong optimum that still passes every
witness check. So the invariants are pinned here: bounds only rise, never exceed
the value, and never silently change what a solution claims.
"""

import json

import pytest

from mosp.instance import MOSPInstance
from satisfiability.mosp_solver import (
    CERTIFIED,
    PROVENANCE_BOUND,
    PROVENANCE_REFUTATION,
    PROVENANCE_RELAXATION,
    PROVENANCE_SOLUTION,
    _save_solution,
    load_lower_bound,
)

INSTANCE = MOSPInstance.from_matrix([[1, 1, 0], [0, 1, 1], [1, 0, 1]], name="b")
ORDER = [0, 1, 2]


def test_bounds_only_ever_rise(tmp_path):
    _save_solution(INSTANCE, 3, ORDER, tmp_path, lower_bound=1,
                   lower_bound_source="clique")
    assert load_lower_bound(INSTANCE, tmp_path) == (1, "clique")

    _save_solution(INSTANCE, 3, ORDER, tmp_path, lower_bound=2,
                   lower_bound_source="relaxation")
    assert load_lower_bound(INSTANCE, tmp_path) == (2, "relaxation")

    # A later run with a weaker bound must not undo the better one.
    _save_solution(INSTANCE, 3, ORDER, tmp_path, lower_bound=1,
                   lower_bound_source="clique")
    assert load_lower_bound(INSTANCE, tmp_path) == (2, "relaxation")

    # Nor may a save that carries no bound at all erase it.
    _save_solution(INSTANCE, 3, ORDER, tmp_path)
    assert load_lower_bound(INSTANCE, tmp_path) == (2, "relaxation")


def test_a_bound_above_the_value_is_refused(tmp_path):
    """One of the two is wrong, and the corpus must not record both."""
    with pytest.raises(ValueError, match="exceeds the value"):
        _save_solution(INSTANCE, 3, ORDER, tmp_path, lower_bound=4)


def test_recording_a_bound_does_not_change_the_claim(tmp_path):
    """A certified optimum stays certified, and its witness is untouched, when
    a later run only adds a bound."""
    _save_solution(INSTANCE, 3, ORDER, tmp_path,
                   provenance=PROVENANCE_REFUTATION)
    _save_solution(INSTANCE, 3, ORDER, tmp_path,
                   provenance=PROVENANCE_REFUTATION, lower_bound=3,
                   lower_bound_source="relaxation")

    payload = json.loads((tmp_path / "b.json").read_text())
    assert payload["provenance"] == PROVENANCE_REFUTATION
    assert payload["mosp_value"] == 3
    assert payload["ordering"] == ORDER
    assert payload["lower_bound"] == 3


def test_a_better_value_keeps_the_bound(tmp_path):
    """The two are independent: improving the witness must not discard a bound
    an earlier run proved."""
    _save_solution(INSTANCE, 3, ORDER, tmp_path, lower_bound=2,
                   lower_bound_source="relaxation")
    _save_solution(INSTANCE, 2, [1, 0, 2], tmp_path)
    assert load_lower_bound(INSTANCE, tmp_path) == (2, "relaxation")
    assert json.loads((tmp_path / "b.json").read_text())["mosp_value"] == 2


def test_a_worse_value_still_records_a_better_bound(tmp_path):
    """A run that finds nothing better may still have proved more."""
    _save_solution(INSTANCE, 2, ORDER, tmp_path, lower_bound=1,
                   lower_bound_source="clique")
    _save_solution(INSTANCE, 3, ORDER, tmp_path, lower_bound=2,
                   lower_bound_source="relaxation")

    payload = json.loads((tmp_path / "b.json").read_text())
    assert payload["mosp_value"] == 2, "the worse value must not be taken"
    assert payload["lower_bound"] == 2, "but the better bound must be"


def test_a_relaxation_closure_is_its_own_kind_of_claim():
    """Closing on a relaxation bound rests on Lemma 1 as well as on the search,
    so it is distinguishable from a refutation in the corpus."""
    assert PROVENANCE_RELAXATION in CERTIFIED
    assert PROVENANCE_RELAXATION != PROVENANCE_BOUND
    assert PROVENANCE_RELAXATION != PROVENANCE_REFUTATION
    assert PROVENANCE_SOLUTION not in CERTIFIED


def test_missing_bounds_read_as_absent(tmp_path):
    _save_solution(INSTANCE, 3, ORDER, tmp_path)
    assert load_lower_bound(INSTANCE, tmp_path) is None
    assert load_lower_bound(INSTANCE, tmp_path / "nowhere") is None
