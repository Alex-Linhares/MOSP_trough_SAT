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

The structured count (loop0010 item 08, `reports/excess_phase_diagram.md` §8):
`ell` nested empty pairs at `ell` prefix sizes of one layout, counted exactly
(`nested_log_bound`, `nested_floors`) and asymptotically (`nested_rate_sup`,
`beta_star_nested`); and the second moment of the single-pair count as the
diagnostic (`second_moment_exact`, `second_moment_rate`). Measured there: the
structured count is *weaker* than the single pair at every `ell >= 2`, every
spacing and every cell (`beta*_2 - beta*` from -0.012 to -0.055), because an
extra cell of size `eps n` costs `eps log(1/eps)` of entropy per customer and
buys `O(eps)` of constraint; the slack of `beta*` is in the union bound (the
empty pairs cluster: `E[X^2] / E[X]^2 = e^{0.23 n}` at `beta*` for `(6, 1)`),
not in the necessary condition (Harper's bound is within 0-1 of the pathwidth
on the record instances to 75 customers).

Usage:
    python -m learning.first_moment            # the two scratch tables, from the benchmark files
    python -m learning.first_moment nested     # beta*_ell for ell = 1..4 on the 18 cells (about a minute)
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


def main_nested() -> None:
    """`beta*_ell`, `ell = 1..4`, at equal spacing on the 18 cells of item 08."""
    print("d  mu   e   | beta*  | beta*_1 beta*_2 beta*_3 beta*_4 | beta*_2 - beta*")
    for d in (2, 3, 4, 6, 8, 10):
        for mu in (0.5, 1, 2):
            b = [beta_star_nested(ell, mu, [d]) for ell in (1, 2, 3, 4)]
            print(f"{d:<2} {mu:<4} {mu * (d - 1):4.1f} | {beta_star(mu, [d]):.4f} | " + " ".join(f"{v:.4f}" for v in b) + f" | {b[1] - beta_star(mu, [d]):+.4f}")


if __name__ == "__main__":
    import sys

    main_nested() if len(sys.argv) > 1 and sys.argv[1] == "nested" else main()


# ----------------------------------------------------------------------------
# the structured count: `ell` nested empty pairs (loop0010 item 08)
# ----------------------------------------------------------------------------
#
# A layout of vertex separation `k` gives, at every prefix size `p`, the prefix
# `A` and an inactive suffix `R` of size `n - p - k` with no `A`-`R` edge
# (`EmptyPair.lean`, `exists_prefix_closedNbhd_card_le`). At prefix sizes
# `p_1 < ... < p_ell` the prefixes grow, `A_1 ⊂ ... ⊂ A_ell`, and the inactive
# suffixes shrink, `R_1 ⊃ ... ⊃ R_ell` (a vertex inactive at a later position is
# in the later suffix and has no neighbour in the larger prefix). Trim each
# `R_j` to a nested subset `R'_j` of size exactly `r_j = n - p_j - k`. Write
# `D_j = A_j \ A_{j-1}` (`D_1 = A_1`), `L_i = R'_i \ R'_{i+1}` (`L_ell = R'_ell`),
# `T` the suffix after `p_ell`; `|L_i| = p_{i+1} - p_i = |D_{i+1}|` for `i < ell`.
# `D_{j'}` may meet `L_i` for `i < j'` (a vertex placed between `p_i` and `p_{j'}`
# with no neighbour before `p_i`), in `delta[j', i]` vertices, and the vertex set
# splits into the cells
#
#     D_{j'} \ R'_1,  D_{j'} ∩ L_i (i < j'),  T ∩ L_i,  F (the rest),
#
# `ell (ell + 1) / 2 + ell + 1` of them, with the forbidden crossings `A_j × R'_j`.
# For every `delta` the number of such cell assignments is a multinomial, and a
# random pattern of size `s` avoids every crossing with a probability that is a
# signed sum of `C(|U|, s) / C(n, s)` over unions `U` of cells (inclusion-
# exclusion over the feasible hit patterns, done once as a Möbius transform).
# Summing over `delta` gives `E[#structures] >= P(pw <= k)`; its exponent at
# `m = mu n` is `sup_delta [H(cells) + mu E_s log P_s(avoid)]`, and `beta*_ell`
# is the root, as for the single pair. `ell = 1` is the single pair with the
# free position `p_1`; at the balanced position it is `beta*`.
#
# The structure's necessity is checked by brute force on random layouts
# (`tests/test_first_moment.py`), the count against an enumeration at `n <= 7`.

import itertools

import numpy as np


def nested_cells(ell: int) -> list[tuple[str, int | None, int | None]]:
    """The cells of the `ell`-nested structure as `(label, a_level, r_level)`:
    a cell lies in `A_j` for every `j >= a_level` and in `R'_j` for every
    `j <= r_level` (`None` for neither). Order: `D_1`, then for `j' = 2..ell`
    `D_{j'} \\ R'_1` and `D_{j'} ∩ L_i` (`i < j'`), then `T ∩ L_i` (`i = 1..ell`),
    then `F`."""
    cells: list[tuple[str, int | None, int | None]] = []
    for jp in range(1, ell + 1):
        cells.append((f"D{jp}", jp, None))
        for i in range(1, jp):
            cells.append((f"D{jp}&L{i}", jp, i))
    for i in range(1, ell + 1):
        cells.append((f"T&L{i}", None, i))
    cells.append(("F", None, None))
    return cells


def delta_index(ell: int) -> list[tuple[int, int]]:
    """The free overlap parameters `(j', i)`, `1 <= i < j' <= ell`, in cell order."""
    return [(jp, i) for jp in range(2, ell + 1) for i in range(1, jp)]


def equal_positions(ell: int, n: float, k: float) -> list[float]:
    """Prefix sizes spaced `(n - k) / (ell + 1)` apart (balanced at `ell = 1`)."""
    return [j * (n - k) / (ell + 1) for j in range(1, ell + 1)]


def nested_sizes(ell: int, n: float, k: float, positions, delta) -> np.ndarray:
    """Cell sizes (in cell order) for prefix sizes `positions` and overlaps
    `delta` (in `delta_index` order); affine in `delta`. Works with fractions
    (`n = 1`) as with integers. Negative entries mean an infeasible `delta`."""
    p = [0.0] + list(positions)
    L = [p[i + 1] - p[i] for i in range(1, ell)] + [n - p[ell] - k]   # L_1..L_ell
    dmap = dict(zip(delta_index(ell), delta))
    sizes = []
    for jp in range(1, ell + 1):
        D = p[jp] - p[jp - 1]
        sizes.append(D - sum(dmap[(jp, i)] for i in range(1, jp)))
        for i in range(1, jp):
            sizes.append(dmap[(jp, i)])
    tl = []
    for i in range(1, ell + 1):
        tl.append(L[i - 1] - sum(dmap[(jp, i)] for jp in range(i + 1, ell + 1)))
    sizes.extend(tl)
    sizes.append(n - p[ell] - sum(tl))
    return np.array(sizes, dtype=float)


def nested_masks(ell: int) -> tuple[list[int], list[int]]:
    """Bit masks over the cells: `A_mask[j]`, `R_mask[j]` for `j = 1..ell`."""
    cells = nested_cells(ell)
    A, R = [], []
    for j in range(1, ell + 1):
        a = r = 0
        for b, (_, al, rl) in enumerate(cells):
            if al is not None and al <= j:
                a |= 1 << b
            if rl is not None and rl >= j:
                r |= 1 << b
        A.append(a)
        R.append(r)
    return A, R


def _mobius_coefficients(feasible: np.ndarray) -> np.ndarray:
    """`c(H') = sum_{H ⊇ H'} (-1)^{|H \\ H'|} feasible(H)`, so that the probability
    that a random set's hit pattern is feasible equals `sum_{H'} c(H') P(S ⊆ U(H'))`."""
    c = feasible.astype(float).copy()
    nbits = int(np.log2(len(c)))
    idx = np.arange(len(c))
    for b in range(nbits):
        without = idx[(idx >> b) & 1 == 0]
        c[without] -= c[without | (1 << b)]
    return c


class NestedStructure:
    """The `ell`-nested empty-pair structure: cells, crossings, and the signed
    inclusion-exclusion coefficients over unions of cells (computed once)."""

    def __init__(self, ell: int):
        self.ell = ell
        self.cells = nested_cells(ell)
        A, R = nested_masks(ell)
        self._build(list(zip(A, R)))

    def _build(self, crossings: list[tuple[int, int]]) -> None:
        C = self.n_cells = len(self.cells)
        H = np.arange(1 << C)
        feasible = np.ones(1 << C, dtype=bool)
        for a, r in crossings:
            feasible &= ~(((H & a) != 0) & ((H & r) != 0))
        self.feasible = feasible
        self.coef = _mobius_coefficients(feasible)
        self.bits = ((H[:, None] >> np.arange(C)[None, :]) & 1).astype(float)   # (2^C, C)
        self.support = np.nonzero(self.coef)[0]
        self.coef_s = self.coef[self.support]
        self.bits_s = self.bits[self.support]

    # --- asymptotic -----------------------------------------------------------
    def avoid_fraction(self, x: np.ndarray, s: float) -> float:
        """`P(a random s-set avoids every crossing)` with cell fractions `x`."""
        u = self.bits_s @ x
        return float(np.dot(self.coef_s, np.power(np.clip(u, 0.0, None), s)))

    def rate(self, x: np.ndarray, mu: float, hist: Mapping[int, int]) -> float:
        if np.any(x < -1e-12):
            return -1e3 * (1.0 + float(np.sum(np.clip(-x, 0.0, None))))   # a finite penalty, for the optimiser
        x = np.clip(x, 0.0, None)
        total = sum(hist.values())
        ent = sum(phi(float(v)) for v in x)
        logs = 0.0
        for s, cnt in hist.items():
            p = self.avoid_fraction(x, s)
            logs += cnt * math.log(max(p, 1e-300))
        return ent + mu * logs / total

    # --- finite ---------------------------------------------------------------
    def log_avoid(self, sizes: np.ndarray, n: int, s: int, lch: np.ndarray) -> np.ndarray:
        """`log P(avoid)` per row of integer cell sizes `sizes` (rows x cells),
        floored at `1e-12` (an over-estimate, hence sound); `lch[j] = log C(j, s)`."""
        u = np.rint(sizes @ self.bits_s.T).astype(int)              # rows x support
        u = np.clip(u, 0, n)
        vals = np.exp(lch[u] - lch[n]) @ self.coef_s
        return np.log(np.clip(vals, 1e-12, 1.0))


_STRUCTURES: dict[int, NestedStructure] = {}


def structure(ell: int) -> NestedStructure:
    if ell not in _STRUCTURES:
        _STRUCTURES[ell] = NestedStructure(ell)
    return _STRUCTURES[ell]


# --- the asymptotic exponent and its sup over the overlaps -------------------


def _affine(ell: int, beta: float, positions) -> tuple[np.ndarray, np.ndarray]:
    """`sizes(delta) = s0 + M delta` with `n = 1`, `k = beta`."""
    q = len(delta_index(ell))
    s0 = nested_sizes(ell, 1.0, beta, positions, [0.0] * q)
    M = np.zeros((len(s0), q))
    for i in range(q):
        e = [0.0] * q
        e[i] = 1.0
        M[:, i] = nested_sizes(ell, 1.0, beta, positions, e) - s0
    return s0, M


def _feasible_starts(s0: np.ndarray, M: np.ndarray, rng: np.random.Generator, count: int) -> list[np.ndarray]:
    """Vertices of `{delta : s0 + M delta >= 0}` in random directions, plus
    their centroid; empty if the polytope is empty."""
    from scipy.optimize import linprog

    q = M.shape[1]
    out = []
    for _ in range(count):
        c = rng.normal(size=q)
        res = linprog(c, A_ub=-M, b_ub=s0 + 1e-12, bounds=[(None, None)] * q, method="highs")
        if res.status == 0:
            out.append(res.x)
    if out:
        out.append(np.mean(out, axis=0))
    return out


def nested_rate_sup(ell: int, beta: float, mu: float, sizes: Iterable[int] | Mapping[int, int],
                    positions=None, starts: int = 6, seed: int = 0, cloud: int = 200) -> tuple[float, np.ndarray]:
    """`sup_delta [H(cells) + mu E_s log P_s(avoid)]` at width fraction `beta`
    and the maximising `delta`. Multi-start SLSQP from random vertices of the
    feasible polytope, checked against a random cloud of feasible points; `-inf`
    if no feasible `delta` exists (the structure does not fit)."""
    from scipy.optimize import minimize

    hist = _histogram(sizes) if not isinstance(sizes, Mapping) else dict(sizes)
    st = structure(ell)
    if positions is None:
        positions = equal_positions(ell, 1.0, beta)
    s0, M = _affine(ell, beta, positions)
    q = M.shape[1]
    if q == 0:
        return st.rate(s0, mu, hist), np.zeros(0)
    rng = np.random.default_rng(seed)
    pts = _feasible_starts(s0, M, rng, starts)
    if not pts:
        return -math.inf, np.zeros(q)
    f = lambda d: -st.rate(s0 + M @ d, mu, hist)  # noqa: E731
    best_val, best_d = -math.inf, pts[0]
    cons = {"type": "ineq", "fun": lambda d: s0 + M @ d, "jac": lambda d: M}
    for d0 in pts:
        res = minimize(f, d0, method="SLSQP", constraints=[cons], options={"maxiter": 300, "ftol": 1e-12})
        d = res.x if np.all(s0 + M @ res.x >= -1e-9) else d0
        v = -f(d)
        if v > best_val:
            best_val, best_d = v, d
    # a random cloud of convex combinations of the vertices, as a check on the optimiser
    V = np.array(pts)
    for _ in range(cloud):
        w = rng.dirichlet(np.ones(len(V)))
        d = w @ V
        v = -f(d)
        if v > best_val + 1e-12:
            res = minimize(f, d, method="SLSQP", constraints=[cons], options={"maxiter": 300, "ftol": 1e-12})
            d2 = res.x if np.all(s0 + M @ res.x >= -1e-9) else d
            v2 = -f(d2)
            best_val, best_d = (v2, d2) if v2 > v else (v, d)
    return best_val, best_d


def nested_rate_grid(beta: float, mu: float, sizes, positions=None, points: int = 2001) -> float:
    """`ell = 2` only: the sup over the single overlap `delta` on a grid (the
    reference for the optimiser in the tests)."""
    hist = _histogram(sizes) if not isinstance(sizes, Mapping) else dict(sizes)
    st = structure(2)
    if positions is None:
        positions = equal_positions(2, 1.0, beta)
    s0, M = _affine(2, beta, positions)
    best = -math.inf
    for d in np.linspace(0.0, positions[1] - positions[0], points):
        best = max(best, st.rate(s0 + M @ np.array([d]), mu, hist))
    return best


def beta_star_nested(ell: int, mu: float, sizes: Iterable[int] | Mapping[int, int], positions=None,
                     coarse: float = 0.005, tol: float = 1e-4, step: float = STEP, **kw) -> float:
    """`beta*_ell`: the first-moment constant of the `ell`-nested structure at
    the given positions (fractions of `n - k`, default equal spacing). For
    `ell = 1` the scan is the single-pair scan on the same grid (`beta = 1 - 2a`,
    `a` from `1/2 - step` downward), so it reproduces `beta_star` digit for
    digit at the balanced position. For `ell >= 2`: a coarse scan upward from
    `2 step` until the exponent is non-negative, then bisection to `tol`."""
    hist = _histogram(sizes) if not isinstance(sizes, Mapping) else dict(sizes)

    def pos(beta):
        if positions is None:
            return None
        return [beta_pos * (1 - beta) for beta_pos in positions]

    def g(beta):
        return nested_rate_sup(ell, beta, mu, hist, positions=pos(beta), **kw)[0]

    b0 = 2 * step
    if g(b0) >= 0:
        return 0.0
    if ell == 1:
        b = b0
        while b + 2 * step < 1 and g(b + 2 * step) < 0:
            b += 2 * step
        return b
    lo, hi = b0, b0
    while hi + coarse < 1:
        if g(hi + coarse) >= 0:
            break
        hi += coarse
    else:
        return hi
    lo, hi = hi, hi + coarse
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if g(mid) < 0:
            lo = mid
        else:
            hi = mid
    return lo


# --- the finite bound -------------------------------------------------------


def _lchoose_table(n: int, s: int) -> np.ndarray:
    """`log C(j, s)` for `j = 0..n` (`-inf` below `s`)."""
    return np.array([lchoose(j, s) for j in range(n + 1)])


def nested_log_bound(ell: int, n: int, sizes: Iterable[int] | Mapping[int, int], k: int,
                     positions=None) -> float:
    """`log E[#ell-nested structures]`, an upper bound on `log P(pw <= k)`, at
    integer prefix sizes `positions` (default: rounded equal spacing), summed
    exactly over every integer overlap `delta`. `+inf` where the structure does
    not fit (some forced cell negative at every `delta`)."""
    hist = _histogram(sizes)
    st = structure(ell)
    if positions is None:
        positions = [int(round(p)) for p in equal_positions(ell, n, k)]
    positions = list(positions)
    if (len(positions) != ell or any(p <= 0 for p in positions) or sorted(set(positions)) != positions
            or n - positions[-1] - k < 0):
        return math.inf
    q = len(delta_index(ell))
    s0 = nested_sizes(ell, n, k, positions, [0] * q)
    M = np.zeros((len(s0), q))
    for i in range(q):
        e = [0] * q
        e[i] = 1
        M[:, i] = nested_sizes(ell, n, k, positions, e) - s0
    # enumerate integer deltas within their box, keep the feasible ones
    p = [0] + positions
    ranges = []
    for jp, i in delta_index(ell):
        ranges.append(range(0, min(p[jp] - p[jp - 1], p[i + 1] - p[i]) + 1))
    if q == 0:
        grid = np.zeros((1, 0))
    else:
        grid = np.array(list(itertools.product(*ranges)), dtype=float)
    sizes_all = s0[None, :] + grid @ M.T
    ok = np.all(sizes_all >= -1e-9, axis=1)
    if not ok.any():
        return math.inf
    sizes_all = np.rint(sizes_all[ok]).astype(int)
    logmult = lg(n + 1) - np.vectorize(lg)(sizes_all + 1).sum(axis=1)
    logp = np.zeros(len(sizes_all))
    for s, cnt in hist.items():
        lch = _lchoose_table(n, s)
        logp += cnt * st.log_avoid(sizes_all.astype(float), n, s, lch)
    terms = logmult + logp
    m = terms.max()
    return float(m + math.log(np.exp(terms - m).sum()))


def nested_floors(ell: int, n: int, sizes: Iterable[int] | Mapping[int, int], positions=None) -> tuple[int, int]:
    """(floor at bound < 1, floor at bound < 0.01) on the optimum `pw + 1` from
    the `ell`-nested count: the largest `k` with `P(pw <= k) <= bound(k)` below
    the threshold, over every `k` (as `floors`; the bound need not be monotone
    in `k`, and each `k` is its own statement)."""
    hist = _histogram(sizes)
    bounds = [nested_log_bound(ell, n, hist, k, positions) for k in range(n)]
    k1 = max((k for k, b in enumerate(bounds) if b < 0), default=-1)
    k2 = max((k for k, b in enumerate(bounds) if b < math.log(0.01)), default=-1)
    return k1 + 2, k2 + 2


# --- brute force, for the tests ---------------------------------------------


def nested_count_brute(ell: int, n: int, sizes: Iterable[int], k: int, positions) -> float:
    """`E[#structures]` by enumerating every assignment of the `n` vertices to
    the cells with the forced sizes (every integer `delta`), and for each the
    exact probability that every pattern avoids every crossing, by enumerating
    the `s`-subsets. `n <= 7`."""
    from math import comb

    st = structure(ell)
    cells = nested_cells(ell)
    A, R = nested_masks(ell)
    C = len(cells)
    q = len(delta_index(ell))
    p = [0] + list(positions)
    ranges = [range(0, min(p[jp] - p[jp - 1], p[i + 1] - p[i]) + 1) for jp, i in delta_index(ell)]
    total = 0.0
    sizes = list(sizes)
    for delta in itertools.product(*ranges) if q else [()]:
        cs = nested_sizes(ell, n, k, positions, list(delta))
        if np.any(cs < -1e-9):
            continue
        cs = [int(round(v)) for v in cs]
        # per-pattern probability: fraction of s-subsets whose hit pattern is feasible, for one representative assignment
        assignment = []
        for b, c in enumerate(cs):
            assignment += [b] * c
        probs = {}
        for s in set(sizes):
            good = 0
            for S in itertools.combinations(range(n), s):
                H = 0
                for v in S:
                    H |= 1 << assignment[v]
                good += st.feasible[H]
            probs[s] = good / comb(n, s)
        count = math.factorial(n)
        for c in cs:
            count //= math.factorial(c)
        pr = 1.0
        for s in sizes:
            pr *= probs[s]
        total += count * pr
    return total


def nested_structure_from_layout(adj: list[int], order: list[int], k: int, positions: list[int]) -> dict | None:
    """The structure a layout `order` of vertex separation `<= k` forces at the
    prefix sizes `positions`: returns the cell assignment (vertex -> cell
    index) and `delta`, after checking the nesting, the sizes and the empty
    crossings; `None` if the layout's separation exceeds `k`. `adj[v]` is a
    neighbour bit mask."""
    n = len(order)
    ell = len(positions)
    cells = nested_cells(ell)
    index = {c[0]: b for b, c in enumerate(cells)}
    # inactive suffixes
    inactive = []
    for p in positions:
        pref = order[:p]
        pm = sum(1 << v for v in pref)
        suff = order[p:]
        inact = [v for v in suff if adj[v] & pm == 0]
        if len(suff) - len(inact) > k:
            return None
        inactive.append(inact)
    # nested trims R'_j of size n - p_j - k, from the last position backward
    Rp = [None] * ell
    for j in range(ell - 1, -1, -1):
        need = n - positions[j] - k
        if need < 0:
            return None
        base = list(Rp[j + 1]) if j + 1 < ell else []
        extra = [v for v in inactive[j] if v not in base]
        assert set(base) <= set(inactive[j]), "nesting R_{j+1} ⊆ R_j fails"
        Rp[j] = base + extra[: need - len(base)]
        assert len(Rp[j]) == need
    assign = {}
    delta = {key: 0 for key in delta_index(ell)}
    p = [0] + positions
    for jp in range(1, ell + 1):
        for v in order[p[jp - 1]:p[jp]]:
            level = None
            for i in range(1, jp):
                if v in Rp[i - 1] and (i == ell or v not in Rp[i]):
                    level = i
            if level is None:
                assign[v] = index[f"D{jp}"]
            else:
                assign[v] = index[f"D{jp}&L{level}"]
                delta[(jp, level)] += 1
    for v in order[p[ell]:]:
        level = None
        for i in range(1, ell + 1):
            if v in Rp[i - 1] and (i == ell or v not in Rp[i]):
                level = i
        assign[v] = index["F"] if level is None else index[f"T&L{level}"]
    sizes = np.rint(nested_sizes(ell, n, k, positions, [delta[key] for key in delta_index(ell)])).astype(int)
    counts = Counter(assign.values())
    for b in range(len(cells)):
        assert counts.get(b, 0) == sizes[b], (cells[b], counts.get(b, 0), sizes[b])
    A, R = nested_masks(ell)
    for a, r in zip(A, R):
        for u in range(n):
            if (a >> assign[u]) & 1:
                for v in range(n):
                    if (r >> assign[v]) & 1:
                        assert adj[u] >> v & 1 == 0, "a crossing edge"
    return {"assign": assign, "delta": delta, "sizes": sizes}


# --- the second moment of the single-pair count (the diagnostic) -------------


def _pair_square_structure() -> NestedStructure:
    """Two single pairs `(A, R)`, `(A', R')` overlaid: 9 cells `{A, R, O} x {A', R', O'}`
    (cell `3 x + y`), crossings `A x R` and `A' x R'`."""
    rowA = sum(1 << (3 * 0 + y) for y in range(3))
    rowR = sum(1 << (3 * 1 + y) for y in range(3))
    colA = sum(1 << (3 * x + 0) for x in range(3))
    colR = sum(1 << (3 * x + 1) for x in range(3))
    st = NestedStructure.__new__(NestedStructure)
    st.ell = 0
    st.cells = [(f"{a}{b}", None, None) for a in "ARO" for b in "ARO"]
    st._build([(rowA, rowR), (colA, colR)])
    return st


def second_moment_exact(n: int, t: int, sizes: Iterable[int] | Mapping[int, int]) -> tuple[float, float, float]:
    """`(log E[X], log E[X^2], E[X^2] / E[X]^2)` for `X` the number of empty pairs
    `(A, R)`, `|A| = t`, `|R| = t - 1`, exactly in the cover model given sizes,
    by summing over the `3 x 3` overlap table of two pairs."""
    hist = _histogram(sizes)
    st = _pair_square_structure()
    r = t - 1
    o = n - t - r
    if o < 0:
        return math.inf, math.inf, math.nan
    logEX = log_pairs(n, t) + sum(c * lq(n, t, s) for s, c in hist.items())
    tabs = []
    for aa in range(t + 1):
        for ar in range(t - aa + 1):
            ao = t - aa - ar
            for ra in range(min(r, t - aa) + 1):
                for rr in range(min(r - ra, r - ar) + 1):
                    ro = r - ra - rr
                    oa = t - aa - ra
                    orr = r - ar - rr
                    oo = o - oa - orr
                    if oo < 0:
                        continue
                    tabs.append((aa, ar, ao, ra, rr, ro, oa, orr, oo))
    tabs = np.array(tabs, dtype=int)
    logmult = lg(n + 1) - np.vectorize(lg)(tabs + 1).sum(axis=1)
    logp = np.zeros(len(tabs))
    for s, cnt in hist.items():
        lch = _lchoose_table(n, s)
        logp += cnt * st.log_avoid(tabs.astype(float), n, s, lch)
    terms = logmult + logp
    m = terms.max()
    logEX2 = float(m + math.log(np.exp(terms - m).sum()))
    return logEX, logEX2, math.exp(logEX2 - 2 * logEX)


def second_moment_rate(a: float, mu: float, sizes: Iterable[int] | Mapping[int, int],
                       starts: int = 8, seed: int = 0) -> tuple[float, float, np.ndarray]:
    """The asymptotic exponent of `E[X^2]` (sup over the overlap table of two
    pairs with both sides `a n`) beside `2 g(a)`; the difference is the
    exponent of `E[X^2] / E[X]^2`. Returns `(sup, 2 g(a), table)`."""
    from scipy.optimize import minimize

    hist = _histogram(sizes) if not isinstance(sizes, Mapping) else dict(sizes)
    st = _pair_square_structure()
    marg = np.array([a, a, 1 - 2 * a])

    def table(v):
        aa, ar, ra, rr = v
        ao = a - aa - ar
        ro = a - ra - rr
        oa = a - aa - ra
        orr = a - ar - rr
        oo = 1 - 2 * a - oa - orr
        return np.array([aa, ar, ao, ra, rr, ro, oa, orr, oo])

    f = lambda v: -st.rate(table(v), mu, hist)  # noqa: E731
    cons = {"type": "ineq", "fun": lambda v: table(v)}
    rng = np.random.default_rng(seed)
    best_v, best = np.array([a * a, a * a, a * a, a * a]), -f(np.array([a * a, a * a, a * a, a * a]))
    pts = [best_v] + [rng.uniform(0, a, 4) for _ in range(starts)]
    for v0 in pts:
        if np.any(table(v0) < 0):
            v0 = np.array([a * a, a * a, a * a, a * a]) * rng.uniform(0.5, 1.5)
            if np.any(table(v0) < 0):
                continue
        res = minimize(f, v0, method="SLSQP", constraints=[cons], options={"maxiter": 300, "ftol": 1e-12})
        if np.all(table(res.x) >= -1e-9):
            val = -f(res.x)
            if val > best:
                best, best_v = val, res.x
    return best, 2 * rate(a, mu, hist), table(best_v)


def empty_pair_count_brute(masks: list[int], n: int, t: int) -> int:
    """`X`: the number of empty pairs `(A, R)`, `|A| = t`, `|R| = t - 1`, of an
    instance given as pattern bit masks, by enumeration (`n <= 14`)."""
    pm = np.array(masks, dtype=np.int64)
    verts = range(n)
    count = 0
    for A in itertools.combinations(verts, t):
        am = sum(1 << v for v in A)
        hitA = (pm & am) != 0
        rest = [v for v in verts if not (am >> v) & 1]
        # patterns meeting A must avoid R: R ⊆ rest minus the union of those patterns
        forbidden = 0
        for pmask in pm[hitA]:
            forbidden |= int(pmask)
        free = [v for v in rest if not (forbidden >> v) & 1]
        if len(free) >= t - 1:
            count += math.comb(len(free), t - 1)
    return count
