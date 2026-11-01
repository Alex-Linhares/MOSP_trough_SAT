"""The first-moment bound on random clique covers, as a library (loop0010 item 02).

Moved from `reports/scratch/clique_cover_moment/asymptotic_cs.py` (the
asymptotic constant) and `bound_lib.py` / `finite_bound_cs.py` (the finite
floor), with the same formulas; `tests/test_first_moment.py` reproduces the two
scratch logs to their printed digits.

Model (the Chu & Stuckey model, `CliqueCoverMoment.lean`): `n` customers,
`m = mu * n` patterns, each pattern an independent uniform random customer set
of its own size `s_j` (fixed `d`, or a size histogram read from the instances).
`EmptyPair.lean`: `pw <= k` forces an *empty pair* `(A, R)` with `|A| = t`,
`|R| = t - 1`, `t = ceil((n - k) / 2)`, no pattern meeting both sides.

Finite (`log_bound`, `floors`): a union bound over the pairs,

    P(pw <= k) <= C(n, t) C(n - t, t - 1) prod_j q(n, t, s_j),
    q(n, t, s) = [C(n - t, s) + C(n - t + 1, s) - C(n - 2t + 1, s)] / C(n, s),

so the optimum `pw + 1` is at least `k + 2` for the largest `k` whose bound is
below 1 (or below 0.01, the floor the paper quotes).

Asymptotic (`rate`, `beta_star`): with `|A| = |R| = a n`,

    (1 / n) log E[#empty pairs] -> g(a) = H(a, a, 1 - 2a) + mu E_s log(2 (1 - a)^s - (1 - 2a)^s),

`g(0+) = 0`, `g(1/2) < 0` for `s >= 2`, and `pw >= (1 - 2 a*) n` with high
probability where `a*` is the point above which `g < 0`; `beta*(d, mu) = 1 - 2 a*`
(the scan is from `a = 1/2` downward in steps of `1e-4`, as in the scratch).
`beta* > 0` iff `mu (d - 1) > 1`, i.e. iff the excess `e > 1`
(`reports/scratch/clique_cover_moment/REPORT_generator.md` section 3.1).

Nothing here is a theorem about the generators we actually run: the fitted
generator pads and rejects (Appendix E.3), and item 10 of loop0010 is where
that is settled. A first moment is a lower bound, never the constant.

Usage:
    python -m learning.first_moment            # the two scratch tables, from the benchmark files
    python -m pytest tests/test_first_moment.py -q
"""
from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path

lg = math.lgamma
STEP = 1e-4
CS_DIR = Path("benchmarks/instances/MOSP_Instances/Chu_Stuckey")

# ----------------------------------------------------------------------------
# the asymptotic constant
# ----------------------------------------------------------------------------


def phi(x: float) -> float:
    """`-x log x`, with `phi(0) = 0`."""
    return -x * math.log(x) if x > 0 else 0.0


def _histogram(sizes: Iterable[int] | Mapping[int, int]) -> dict[int, int]:
    if isinstance(sizes, Mapping):
        return {int(s): int(c) for s, c in sizes.items() if c}
    return dict(Counter(int(s) for s in sizes))


def rate(a: float, mu: float, sizes: Iterable[int] | Mapping[int, int]) -> float:
    """`g(a)`: the exponent per customer of the expected number of empty pairs
    with both sides of size `a n`, for `m = mu n` patterns with the given size
    histogram (a list of sizes or a `{size: count}` mapping; a real-valued size
    is accepted, which is how the threshold in `d` is bisected)."""
    hist = _histogram(sizes) if not isinstance(sizes, Mapping) else dict(sizes)
    total = sum(hist.values())
    mean_log = sum(c * math.log(max(2 * (1 - a) ** s - (1 - 2 * a) ** s, 1e-300)) for s, c in hist.items()) / total
    return 2 * phi(a) + phi(1 - 2 * a) + mu * mean_log


def beta_star(mu: float, sizes: Iterable[int] | Mapping[int, int], step: float = STEP) -> float:
    """`beta*(d, mu) = 1 - 2 a*`: the first-moment lower bound on `lim pw / n`.
    Zero when `g` is non-negative just below `a = 1/2` (no bound)."""
    hist = sizes if isinstance(sizes, Mapping) else _histogram(sizes)
    a = 0.5 - step
    if rate(a, mu, hist) >= 0:
        return 0.0
    while a - step > 0 and rate(a - step, mu, hist) < 0:
        a -= step
    return 1 - 2 * a


def threshold_d(mu: float = 1.0, lo: float = 2.0, hi: float = 4.0, iterations: int = 40) -> float:
    """The real size `d` above which `beta*(d, mu) > 0`, by bisection with the
    formula extended to real `s` (2.0031 at `mu = 1`; the closed form is
    `mu (d - 1) = 1`, i.e. `d = 2`, the scan's step accounting for the rest)."""
    for _ in range(iterations):
        mid = (lo + hi) / 2
        if beta_star(mu, {mid: 1}) > 0:
            hi = mid
        else:
            lo = mid
    return hi


# ----------------------------------------------------------------------------
# the finite floor
# ----------------------------------------------------------------------------


def lchoose(a: int, b: int) -> float:
    if b < 0 or b > a:
        return -math.inf
    return lg(a + 1) - lg(b + 1) - lg(a - b + 1)


def lq(n: int, t: int, s: int) -> float:
    """log P(a uniform `s`-subset of `n` avoids `A` (size `t`) or avoids `R` (size `t - 1`))."""
    terms = [lchoose(n - t, s), lchoose(n - t + 1, s)]
    neg = lchoose(n - 2 * t + 1, s)
    m = max(terms)
    val = math.exp(terms[0] - m) + math.exp(terms[1] - m) - (math.exp(neg - m) if neg > -math.inf else 0.0)
    if val <= 0:
        return -math.inf
    return m + math.log(val) - lchoose(n, s)


def log_pairs(n: int, t: int) -> float:
    return lchoose(n, t) + lchoose(n - t, t - 1)


def log_bound(n: int, sizes: Iterable[int] | Mapping[int, int], k: int) -> float:
    """log of the union bound on `P(pw <= k)`; `+inf` where the pair does not exist."""
    t = (n - k + 1) // 2
    if t < 1 or 2 * t - 1 > n:
        return math.inf
    hist = _histogram(sizes)
    return log_pairs(n, t) + sum(c * lq(n, t, s) for s, c in hist.items())


def floors(n: int, sizes: Iterable[int] | Mapping[int, int]) -> tuple[int, int]:
    """(floor at bound < 1, floor at bound < 0.01) on the optimum `pw + 1`."""
    hist = _histogram(sizes)
    k1 = max((k for k in range(n) if log_bound(n, hist, k) < 0), default=-1)
    k2 = max((k for k in range(n) if log_bound(n, hist, k) < math.log(0.01)), default=-1)
    return k1 + 2, k2 + 2


# ----------------------------------------------------------------------------
# the scratch tables, from the benchmark files (no solutions/ read)
# ----------------------------------------------------------------------------


def chu_stuckey_sizes(cs_dir: Path = CS_DIR) -> dict[tuple[int, int, int], dict]:
    """Per class `(n, m, d)`: the pooled pattern-size histogram and the
    per-instance histograms with their names, read from the instance files
    (patterns x customers in the files)."""
    classes: dict[tuple[int, int, int], dict] = {}
    for f in sorted(cs_dir.glob("Random-*.txt")):
        lines = [line for line in f.read_text().split("\n") if line.strip()]
        m, n = map(int, lines[0].split())
        sizes = [sum(map(int, lines[1 + i].split())) for i in range(m)]
        d = int(f.stem.split("-")[3])
        c = classes.setdefault((n, m, d), {"sizes": Counter(), "instances": []})
        c["sizes"].update(sizes)
        c["instances"].append((f.stem, sizes))
    return classes


def main() -> None:
    import pandas as pd

    classes = chu_stuckey_sizes()
    table = pd.read_csv("learning/data/instances.csv", usecols=["instance_name", "optimum", "provenance"])
    opt = {r.instance_name: r.optimum for r in table.itertuples() if str(r.provenance).startswith("certified")}
    print("class (n,m,d): opt/n | beta* (empirical sizes) | beta* (fixed d) | floor<1 | floor<0.01 | violations")
    for key in sorted(classes):
        n, m, d = key
        c = classes[key]
        mu = m / n
        opts = [opt[f"{name}_0"] for name, _ in c["instances"]]
        f1 = [floors(n, s)[0] for _, s in c["instances"]]
        f2 = [floors(n, s)[1] for _, s in c["instances"]]
        viol = sum(o < f for o, f in zip(opts, f2))
        print(f"{key}: {sum(opts) / len(opts) / n:.3f} | {beta_star(mu, c['sizes']):.3f} | {beta_star(mu, [d]):.3f}"
              f" | {sum(f1) / len(f1):6.1f} | {sum(f2) / len(f2):6.1f} | {viol}")
    print("\nfixed size d, mu = m/n: beta*(d, mu)")
    print("d\\mu " + " ".join(f"{mu:>6}" for mu in (0.5, 1, 2, 4)))
    for d in (2, 3, 4, 5, 6, 8, 10, 15, 20):
        print(f"{d:<5}" + " ".join(f"{beta_star(mu, [d]):6.3f}" for mu in (0.5, 1, 2, 4)))
    print(f"\nthreshold at mu = 1: beta* > 0 iff d > {threshold_d():.4f} (fixed size d)")


if __name__ == "__main__":
    main()
