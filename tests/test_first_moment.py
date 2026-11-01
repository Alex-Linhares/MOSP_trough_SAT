"""loop0010 item 02: `learning.first_moment` reproduces the two scratch logs
(`reports/scratch/clique_cover_moment/asymptotic_cs.log`, `finite_bound_cs.log`)
to their printed digits, and its histogram interface agrees with the list one."""

import math
from pathlib import Path

import pytest

from learning.first_moment import (CS_DIR, beta_star, chu_stuckey_sizes, floors, log_bound, rate, threshold_d)

# fixed size d, mu = m/n: beta*(d, mu), the table of asymptotic_cs.log (3 digits)
ASYMPTOTIC_TABLE = {
    2: (0.000, 0.000, 0.121, 0.307),
    3: (0.000, 0.140, 0.355, 0.570),
    4: (0.072, 0.286, 0.525, 0.715),
    5: (0.158, 0.411, 0.642, 0.799),
    6: (0.244, 0.513, 0.724, 0.851),
    8: (0.398, 0.661, 0.825, 0.909),
    10: (0.522, 0.757, 0.880, 0.939),
    15: (0.726, 0.877, 0.942, 0.971),
    20: (0.832, 0.927, 0.965, 0.982),
}
MUS = (0.5, 1, 2, 4)

# class (n, m, d): beta* (empirical sizes) from asymptotic_cs.log, and the mean
# floors (< 1, < 0.01) from finite_bound_cs.log
CLASS_LOG = {
    (30, 30, 2): (0.097, 5.4, 4.6),
    (50, 100, 2): (0.277, 16.6, 15.8),
    (75, 75, 6): (0.538, 44.4, 43.2),
    (100, 50, 4): (0.133, 17.0, 15.4),
    (125, 125, 10): (0.762, 99.6, 98.0),
}


@pytest.mark.parametrize("d", sorted(ASYMPTOTIC_TABLE))
def test_beta_star_table_matches_the_scratch_log(d):
    for mu, expected in zip(MUS, ASYMPTOTIC_TABLE[d]):
        assert f"{beta_star(mu, [d]):.3f}" == f"{expected:.3f}"


def test_threshold_in_d_matches_the_scratch_log():
    assert f"{threshold_d():.4f}" == "2.0031"


def test_beta_star_is_positive_exactly_above_excess_one():
    # fixed sizes: e = mu (d - 1); the closed-form threshold is e = 1
    assert beta_star(1.0, [2]) == 0.0           # e = 1
    assert beta_star(0.5, [3]) == 0.0           # e = 1
    assert beta_star(0.5, [4]) > 0.0            # e = 1.5
    assert beta_star(2.0, [2]) > 0.0            # e = 2


def test_rate_accepts_a_histogram_and_agrees_with_the_list():
    sizes = [2, 2, 3, 5, 5, 5, 8]
    hist = {2: 2, 3: 1, 5: 3, 8: 1}
    for a in (0.05, 0.2, 0.4):
        assert rate(a, 1.3, hist) == pytest.approx(rate(a, 1.3, sizes), abs=1e-12)
    assert beta_star(1.3, hist) == pytest.approx(beta_star(1.3, sizes), abs=1e-12)


def test_rate_vanishes_at_zero_and_is_negative_at_one_half_for_sizes_two_or_more():
    assert rate(0.0, 1.0, [3]) == 0.0
    assert rate(0.5 - 1e-4, 1.0, [2]) < 0.0 or beta_star(1.0, [2]) == 0.0
    assert rate(0.5 - 1e-4, 1.0, [4]) < 0.0


def test_log_bound_is_infinite_where_no_pair_exists_and_the_floor_is_where_it_crosses():
    n, sizes = 30, [4] * 30
    assert log_bound(n, sizes, n) == math.inf          # t = 0: no pair
    assert log_bound(n, sizes, n - 1) < math.inf        # t = 1: the pair (A, R) with |A| = 1, |R| = 0
    f1, _ = floors(n, sizes)
    assert log_bound(n, sizes, f1 - 2) < 0              # the floor's k has bound < 1 ...
    assert all(log_bound(n, sizes, k) >= 0 for k in range(f1 - 1, n))   # ... and no larger k does


def test_floors_on_a_small_fixed_cover():
    f1, f2 = floors(30, [4] * 30)
    assert 2 <= f2 <= f1 <= 30


@pytest.mark.skipif(not CS_DIR.exists(), reason="benchmark files absent")
def test_class_values_match_both_scratch_logs():
    classes = chu_stuckey_sizes(Path(CS_DIR))
    for key, (beta, floor1, floor2) in CLASS_LOG.items():
        c = classes[key]
        n, m, _ = key
        assert f"{beta_star(m / n, c['sizes']):.3f}" == f"{beta:.3f}"
        f1 = [floors(n, s)[0] for _, s in c["instances"]]
        f2 = [floors(n, s)[1] for _, s in c["instances"]]
        assert f"{sum(f1) / len(f1):.1f}" == f"{floor1:.1f}"
        assert f"{sum(f2) / len(f2):.1f}" == f"{floor2:.1f}"
