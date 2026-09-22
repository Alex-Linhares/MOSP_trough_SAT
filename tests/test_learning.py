"""Guards on the learning package.

The one that matters is `test_learned_bound_is_verified_by_simulation`: the
whole case for letting a model near the solver is that its output is an
*ordering*, checked on the original instance, so a bad model costs quality and
never correctness. If a learned value could ever come back unsimulated, that
argument is gone.

The rest are shape and invariance checks. Features must not depend on how the
customers happen to be numbered, because the optimum does not.
"""

import random

import numpy as np
import pytest

from learning.features import feature_names, instance_features
from learning.policy import (
    STEP_FEATURE_NAMES,
    learned_closing_order,
    step_features,
    training_rows,
    witness_closing_order,
)
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.heuristics import _neighbour_masks, product_order_from_customers

lgb = pytest.importorskip("lightgbm")


def _random_instance(seed: int, n_c: int = 8, n_p: int = 6) -> MOSPInstance:
    rng = random.Random(seed)
    matrix = [[rng.randint(0, 1) for _ in range(n_p)] for _ in range(n_c)]
    for row in matrix:
        if not any(row):
            row[rng.randrange(n_p)] = 1
    return MOSPInstance.from_matrix(matrix, name=f"rand{seed}")


@pytest.mark.parametrize("seed", range(5))
def test_features_are_permutation_invariant(seed):
    """Renaming customers changes nothing a model is allowed to see."""
    instance = _random_instance(seed)
    perm = list(range(instance.n_customers))
    random.Random(seed).shuffle(perm)
    shuffled = MOSPInstance.from_matrix(instance.matrix[perm], name="shuffled")

    a = instance_features(instance, groups=("matrix", "graph"))
    b = instance_features(shuffled, groups=("matrix", "graph"))
    for key in a:
        assert a[key] == pytest.approx(b[key]), key


def test_feature_names_match_what_is_produced():
    instance = _random_instance(1)
    assert list(instance_features(instance).keys()) == feature_names()


def test_step_features_length_matches_names():
    instance = _random_instance(2)
    masks = _neighbour_masks(instance)
    feats = step_features(masks, instance.n_customers, 0, 0, 0)
    assert len(feats) == len(STEP_FEATURE_NAMES)


def test_training_rows_have_one_positive_per_decision():
    """Every replayed step labels exactly one candidate as the one taken."""
    instance = _random_instance(3)
    order = list(range(instance.n_customers))
    random.Random(3).shuffle(order)
    rows, labels = training_rows(instance, order)
    assert len(rows) == len(labels)
    # Steps with a single candidate are skipped, so the positives are at most
    # the number of closings, and each contributes at most one.
    assert 0 < sum(labels) <= len(order)


def test_witness_closing_order_covers_every_active_customer():
    instance = _random_instance(4)
    ordering = list(range(instance.n_patterns))
    order = witness_closing_order(instance, ordering)
    active = {c for c in range(instance.n_customers) if instance.customer_patterns(c)}
    assert set(order) == active
    assert len(order) == len(set(order))


def _toy_model(instances):
    X, y = [], []
    for instance in instances:
        order = witness_closing_order(instance, list(range(instance.n_patterns)))
        rows, labels = training_rows(instance, order)
        X.extend(rows)
        y.extend(labels)
    model = lgb.LGBMClassifier(n_estimators=10, num_leaves=4, verbose=-1,
                               min_child_samples=1)
    model.fit(np.array(X, dtype=np.float32), np.array(y))
    return model.booster_


def test_learned_closing_order_is_a_permutation():
    instances = [_random_instance(s) for s in range(6)]
    model = _toy_model(instances)
    instance = instances[0]
    order = learned_closing_order(instance, model)
    active = {c for c in range(instance.n_customers) if instance.customer_patterns(c)}
    assert set(order) == active


def test_learned_bound_is_verified_by_simulation():
    """The value reported is what simulating the ordering gives, not a prediction."""
    from learning.policy import learned_upper_bound

    instances = [_random_instance(s) for s in range(6)]
    model = _toy_model(instances)
    for instance in instances:
        value, ordering = learned_upper_bound(instance, model)
        assert sorted(ordering) == list(range(instance.n_patterns))
        assert value == max_open_stacks(instance, ordering)


def test_learned_order_never_beats_the_optimum():
    """An upper bound that came in below the optimum would mean the simulation lied."""
    from satisfiability.mosp_solver import solve_mosp_sat

    instances = [_random_instance(s, n_c=6, n_p=5) for s in range(4)]
    model = _toy_model(instances)
    for instance in instances:
        order = learned_closing_order(instance, model)
        value = max_open_stacks(instance, product_order_from_customers(instance, order))
        optimum, _ = solve_mosp_sat(instance, solutions_dir=None)
        assert value >= optimum


# -------------------------------------------------------
# The registered strategies
# -------------------------------------------------------


def test_learned_strategies_are_registered():
    from satisfiability.heuristics import STRATEGIES

    assert "learned" in STRATEGIES
    assert "learned+cs-dfs" in STRATEGIES


def test_missing_model_raises_rather_than_falling_back():
    """A silent fallback would let a sweep report `cs-dfs` numbers as learned ones."""
    from satisfiability.heuristics import upper_bound

    instance = _random_instance(7)
    for strategy in ("learned", "learned+cs-dfs"):
        with pytest.raises(RuntimeError, match="no trained policy"):
            upper_bound(instance, strategy, model_path="learning/models/absent.txt")


@pytest.mark.skipif(not __import__("pathlib").Path("learning/models/policy.txt").exists(),
                    reason="no trained policy on disk")
def test_registered_strategies_return_simulated_values():
    from mosp.verify import max_open_stacks
    from satisfiability.heuristics import upper_bound

    for seed in range(4):
        instance = _random_instance(seed, n_c=10, n_p=8)
        for strategy in ("learned", "learned+cs-dfs"):
            value, ordering = upper_bound(instance, strategy)
            assert sorted(ordering) == list(range(instance.n_patterns))
            assert value == max_open_stacks(instance, ordering)


@pytest.mark.skipif(not __import__("pathlib").Path("learning/models/policy.txt").exists(),
                    reason="no trained policy on disk")
def test_seeding_never_makes_the_dfs_report_below_the_optimum():
    """The seed changes which order the DFS finds, never what simulation says."""
    from satisfiability.heuristics import restricted_dfs, upper_bound
    from satisfiability.mosp_solver import solve_mosp_sat

    for seed in range(4):
        instance = _random_instance(seed, n_c=7, n_p=6)
        optimum, _ = solve_mosp_sat(instance, solutions_dir=None)
        assert restricted_dfs(instance)[0] >= optimum
        assert upper_bound(instance, "learned+cs-dfs")[0] >= optimum
