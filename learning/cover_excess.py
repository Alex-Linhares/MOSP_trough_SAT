"""Why cover excess two? The ridge against the thresholds of the random bipartite incidence graph.

Question (`reports/ml_nature_plan_3.md` §1 Q3, loop0004 item 09). §25 found
the hardness ridge -- the density at which the nodes to refute `optimum - 1`
peak at fixed `n` -- at cover excess `(n_ones - m) / n ~ 2-2.4` for every
product ratio `m / n` from 2 to 1/8, i.e. at about one independent cycle of
the customer-product incidence graph per customer (its cyclomatic number is
`n_ones - n - m + c`). Why two? This module treats the excess as a quantity
of the random bipartite incidence graph and asks whether any of that graph's
known thresholds coincides with the ridge:

  * the giant component / 2-core emergence (branching factor 1; Schmidt-Pruzan
    & Shamir 1985, Karonski & Luczak 2002 for hypergraphs; Molloy-Reed);
  * the emergence of the deeper cores of the bipartite graph -- the
    (3, 2)-core (customers with >= 3 products, products with >= 2 customers),
    the (2, 3)-core and the (3, 3)-core -- which appear discontinuously, as
    the k-core of G(n, p) does for k >= 3 (Pittel, Spencer & Wormald 1996;
    Fernholz & Ramachandran 2007; Riordan 2008; Molloy 2005 for hypergraphs);
  * natural values of the 2-core's own quantities: half the customers in the
    core, the core's cyclomatic number equal to its customer count (the
    XORSAT-style condition, Dubois & Mandler 2002, Mezard, Ricci-Tersenghi &
    Zecchina 2003, where the 2-core of the factor graph has as many
    constraints as variables), the core's excess two;
  * the random-intersection-graph literature's thresholds for G(n, m, p) at
    m = Theta(n) (Karonski, Scheinerman & Singer-Cohen 1999; Behrisch 2007;
    Lageras & Lindholm 2008; Rybarczyk 2011): the giant is the branching
    factor above; connectivity sits at products per customer ~ ln n, which
    moves with n where the ridge does not.

Every threshold is derived in the configuration model with the generators'
actual degree distributions (Poisson products per customer with the empty-row
repair; products of exactly `d` customers for the fixed generator, Poisson for
Bernoulli) in `col_mean` coordinates, checked against peeled cores on the
regenerated instances of every cell at n in {50, 60, 75}, and then scored
against §25's measured peaks two ways: at its natural value (an uncalibrated
prediction of where the ridge sits per `m / n`) and calibrated at `m = n` as
§25 (d) did. The empirical core, kernel and dominance-reduced quantities are
added to §25's constancy table.

Nothing here is a bound, a solver change or a prediction of a value; nothing
is written to `solutions/`. Instances regenerate byte for byte from the
ensemble manifests.

Usage:
    python -m learning.cover_excess --stage measure --workers 16   # peel every certified instance at n in {50, 60, 75}: ~2 min
    python -m learning.cover_excess --stage tables                 # reports/cover_excess_tables.md, ~1 min
    python -m pytest tests/test_cover_excess.py -q
"""
from __future__ import annotations

import argparse
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binom, poisson

from learning.ensemble import ENSEMBLE_DIR, Cell
from learning.ridge_theory import (CANDIDATE_TEXT, CANDIDATES, _interp_at, branching_factor, cell_medians,
                                   excess, giant_threshold_col_mean, load_frames, peak_table,
                                   tree_threshold_col_mean)
from mosp.instance import MOSPInstance

MEASURES_CSV = ENSEMBLE_DIR / "cover_excess_measures.csv"
TABLES = Path("reports/cover_excess_tables.md")
SIZES = (50, 60, 75)
RATIOS = {"2n": 2.0, "n": 1.0, "n/2": 0.5, "n/4": 0.25, "n/8": 0.125}
MAX_DEG = 400

# ----------------------------------------------------------------------------
# (a) the configuration model of the incidence graph
# ----------------------------------------------------------------------------


def degree_pmfs(generator: str, r: float, c: float, repair: bool = True,
                max_deg: int = MAX_DEG) -> tuple[np.ndarray, np.ndarray]:
    """Customer-side and product-side degree pmfs of the incidence graph in the
    large-n limit at fixed products-per-customers ratio `r = m / n` and
    realised customers per product `c` (`col_mean`).

    Customers: products per customer is Poisson(r c) in both generators
    (Binomial(m, c / n) with m = r n). Both generators then give every empty
    row one random product, so the mass at 0 moves to 1 and each product
    receives, on average, P(0) / r extra customers. Products: exactly `d`
    customers in the fixed generator (a non-integer `c` is the mixture of the
    two neighbouring integers with mean `c`), Poisson(c) for Bernoulli, plus
    the repair's Poisson(P(0) / r) customers. `c` is the mean of the returned
    product pmf only up to the repair, which is how the generators behave.
    """
    rho = r * c
    top = max(rho, c)
    max_deg = int(min(max_deg, top + 12.0 * np.sqrt(top) + 25))
    k = np.arange(max_deg + 1)
    p_c = poisson.pmf(k, rho)
    p0 = float(p_c[0]) if repair else 0.0
    if repair:
        p_c[1] += p_c[0]
        p_c[0] = 0.0
    if generator == "fixed":
        base = c - p0 / r if repair else c          # the design d is the pre-repair mean
        lo = int(np.floor(base))
        w_hi = base - lo
        p_p = np.zeros(max_deg + 1)
        p_p[max(lo, 0)] += 1.0 - w_hi
        if lo + 1 <= max_deg:
            p_p[lo + 1] += w_hi
    else:
        p_p = poisson.pmf(k, c)
        p_p[0] = 0.0                                # empty columns are repaired too
        p_p /= p_p.sum()
    if repair and p0 > 0:
        extra = poisson.pmf(k, p0 / r)
        p_p = np.convolve(p_p, extra)[: max_deg + 1]
        p_p /= p_p.sum()
    return p_c / p_c.sum(), p_p


def size_biased(pmf: np.ndarray) -> np.ndarray:
    """The pmf of the number of *other* edges at the far end of a random edge."""
    k = np.arange(len(pmf))
    mean = float((k * pmf).sum())
    q = np.zeros_like(pmf)
    q[:-1] = (k[1:] * pmf[1:]) / mean
    return q


def _tail_ge(pmf_other: np.ndarray, prob: float, k_min: int) -> float:
    """P(Bin(J, prob) >= k_min) with J ~ pmf_other."""
    if k_min <= 0:
        return 1.0
    j = np.arange(len(pmf_other))
    return float((pmf_other * binom.sf(k_min - 1, j, prob)).sum())


def core_fixed_point(p_c: np.ndarray, p_p: np.ndarray, k_c: int, k_p: int,
                     tol: float = 1e-9, max_iter: int = 1_500) -> tuple[float, float]:
    """Peeling fixed point of the (k_c, k_p)-core: `a` is the probability that an
    edge walked from its customer finds a product with at least k_p - 1 other
    alive edges; `b` the same from a product towards a customer with at least
    k_c - 1 other alive edges. Iterated from (1, 1); the core is empty when
    the iteration collapses to (0, 0)."""
    q_c, q_p = size_biased(p_c), size_biased(p_p)
    a = b = 1.0
    for _ in range(max_iter):
        a_new = _tail_ge(q_p, b, k_p - 1)
        b_new = _tail_ge(q_c, a_new, k_c - 1)
        if abs(a_new - a) < tol and abs(b_new - b) < tol:
            a, b = a_new, b_new
            break
        a, b = a_new, b_new
        if a < 1e-7 or b < 1e-7:
            return 0.0, 0.0
    return a, b


def core_quantities(generator: str, r: float, c: float, k_c: int = 2, k_p: int = 2,
                    repair: bool = True) -> dict:
    """Expected (k_c, k_p)-core of the incidence graph per customer: the share
    of customers and products in it, its edges per customer, its cyclomatic
    number per customer and per core customer, its excess (edges minus
    products over customers, the cover excess of the core instance) and the
    core customers' mean degree."""
    p_c, p_p = degree_pmfs(generator, r, c, repair)
    a, b = core_fixed_point(p_c, p_p, k_c, k_p)
    if a <= 0.0:
        return {"a": 0.0, "b": 0.0, "cust_frac": 0.0, "prod_frac": 0.0, "edges_n": 0.0, "cyc_n": 0.0,
                "cyc_per_core_cust": np.nan, "core_excess": np.nan, "core_row_mean": np.nan}
    j = np.arange(len(p_c))
    cust = float((p_c * binom.sf(k_c - 1, j, a)).sum())
    # edges of a core customer: alive edges i >= k_c, summed with weight i
    i_grid = np.arange(len(p_c))
    pm = binom.pmf(i_grid[None, :], j[:, None], a)          # P(Bin(j, a) = i)
    keep = (i_grid[None, :] >= k_c)
    edges = float((p_c[:, None] * pm * keep * i_grid[None, :]).sum())
    jp = np.arange(len(p_p))
    prod = float((p_p * binom.sf(k_p - 1, jp, b)).sum()) * r
    cyc = edges - cust - prod
    return {"a": a, "b": b, "cust_frac": cust, "prod_frac": prod / r if r else np.nan, "edges_n": edges,
            "cyc_n": cyc, "cyc_per_core_cust": cyc / cust if cust > 0 else np.nan,
            "core_excess": (edges - prod) / cust if cust > 0 else np.nan,
            "core_row_mean": edges / cust if cust > 0 else np.nan}


def core_threshold_col_mean(generator: str, r: float, k_c: int, k_p: int, c_lo: float = 1.0,
                            c_hi: float = 200.0, repair: bool = True, iters: int = 24) -> float:
    """Smallest `col_mean` at which the (k_c, k_p)-core is non-empty (bisection
    on the fixed point; the core fraction is monotone in c)."""
    def empty(c: float) -> bool:
        return core_quantities(generator, r, c, k_c, k_p, repair)["cust_frac"] <= 1e-9
    if not empty(c_lo):
        return c_lo
    if empty(c_hi):
        return np.nan
    lo, hi = c_lo, c_hi
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if empty(mid):
            lo = mid
        else:
            hi = mid
    return hi


def connectivity_col_mean(r: float, n: int) -> float:
    """Products per customer ~ ln n is where isolated customers vanish in the
    Poisson model (before the repair): col_mean = ln n / r. It moves with n."""
    return float(np.log(n) / r)


def invert_analytic(fn, target: float, c_lo: float = 1.0001, c_hi: float = 400.0, iters: int = 22,
                    scan: int = 100) -> float:
    """The smallest `col_mean` at which an analytic quantity first reaches
    `target`, scanning a geometric grid from `c_lo` for the first crossing from
    below and bisecting inside that bracket; NaN when it never crosses. A
    scan first, because the core quantities are undefined (NaN) below the
    core's emergence and need not be monotone just above it."""
    grid = np.geomspace(c_lo, c_hi, scan)
    vals = np.array([fn(g) for g in grid], dtype=float)
    ok = np.isfinite(vals)
    if not ok.any():
        return np.nan
    for i in range(len(grid)):
        if ok[i] and vals[i] >= target:
            if i == 0 or not ok[i - 1]:
                return float(grid[i])
            lo, hi = float(grid[i - 1]), float(grid[i])
            for _ in range(iters):
                mid = 0.5 * (lo + hi)
                v = fn(mid)
                if np.isfinite(v) and v >= target:
                    hi = mid
                else:
                    lo = mid
            return 0.5 * (lo + hi)
    return np.nan


# the analytic candidates of this section: name -> (text, natural value, function(generator, r, c, n) -> value)
def _q(key: str, k_c: int = 2, k_p: int = 2):
    return lambda g, r, c, n: core_quantities(g, r, c, k_c, k_p)[key]


NEW_ANALYTIC = {
    "excess": ("excess r (c − 1); natural value 2 = one incidence cycle per customer", 2.0,
               lambda g, r, c, n: excess(r, c)),
    "branch": ("branching factor; giant / 2-core emergence at 1", 1.0,
               lambda g, r, c, n: branching_factor(r, c, g)),
    "tree": ("excess; incidence forest threshold at 1", 1.0, lambda g, r, c, n: excess(r, c)),
    "core2_cust_frac": ("share of customers in the 2-core; natural value ½", 0.5, _q("cust_frac")),
    "core2_cyc_per_core_cust": ("2-core cyclomatic number per core customer; natural value 1", 1.0,
                                _q("cyc_per_core_cust")),
    "core2_cyc_n": ("2-core cyclomatic number per customer; natural value 1", 1.0, _q("cyc_n")),
    "core32_cust_frac": ("share of customers in the (3,2)-core; emergence at 0⁺", 1e-6, _q("cust_frac", 3, 2)),
    "core23_cust_frac": ("share of customers in the (2,3)-core; emergence at 0⁺", 1e-6, _q("cust_frac", 2, 3)),
    "core33_cust_frac": ("share of customers in the (3,3)-core; emergence at 0⁺", 1e-6, _q("cust_frac", 3, 3)),
    "row_mean_conn": ("products per customer; connectivity at ln n", None,
                      lambda g, r, c, n: r * c),
}


def threshold_table(peaks: pd.DataFrame, min_n: int = 50) -> pd.DataFrame:
    """Every analytic threshold at its natural value, per (generator, ratio):
    the predicted ridge col_mean against every measured peak at n >= min_n."""
    rows = []
    sub = peaks[peaks["n"] >= min_n]
    for (gen, lab), g in sub.groupby(["generator", "ratio_label"]):
        r = float(g["r_exact"].median())
        for _, p in g.iterrows():
            n = int(p["n"])
            preds = {
                "giant (branching 1)": giant_threshold_col_mean(r, gen),
                "incidence forest (excess 1)": tree_threshold_col_mean(r),
                "excess 2 (one cycle per customer)": 1.0 + 2.0 / r,
                "(3,2)-core emergence": core_threshold_col_mean(gen, r, 3, 2),
                "(2,3)-core emergence": core_threshold_col_mean(gen, r, 2, 3),
                "(3,3)-core emergence": core_threshold_col_mean(gen, r, 3, 3),
                "2-core holds half the customers": invert_analytic(lambda c: core_quantities(gen, r, c)["cust_frac"], 0.5),
                "2-core cyclomatic = core customers": invert_analytic(
                    lambda c: core_quantities(gen, r, c)["cyc_per_core_cust"], 1.0),
                "2-core cyclomatic = n": invert_analytic(lambda c: core_quantities(gen, r, c)["cyc_n"], 1.0),
                "connectivity (products per customer ln n)": connectivity_col_mean(r, n),
            }
            for name, pred in preds.items():
                meas, lo, hi = p["peak_col_mean"], p["ci_lo"], p["ci_hi"]
                err = float(np.log10(pred / meas)) if np.isfinite(pred) and pred > 0 else np.nan
                within = bool(lo <= pred <= hi) if np.isfinite(lo) else bool(np.isfinite(err) and abs(err) <= 0.05)
                rows.append({"threshold": name, "generator": gen, "ratio_label": lab, "n": n, "r_exact": r,
                             "predicted_col_mean": pred, "measured_col_mean": meas, "ci_lo": lo, "ci_hi": hi,
                             "log10_error": err, "within_ci": within,
                             "peak_is_edge": not bool(p["interior"])})
    return pd.DataFrame(rows)


def threshold_summary(table: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, g in table.groupby("threshold", sort=False):
        piv = g.groupby("ratio_label")["log10_error"].mean()
        rows.append({"threshold": name, "series": len(g),
                     "mean_abs_log10_error": float(g["log10_error"].abs().mean()),
                     "max_abs_log10_error": float(g["log10_error"].abs().max()),
                     "mean_signed_log10_error": float(g["log10_error"].mean()),
                     "within_ci": int(g["within_ci"].sum()),
                     "undefined": int(g["log10_error"].isna().sum()),
                     **{f"err_{k}": float(piv.get(k, np.nan)) for k in RATIOS}})
    return pd.DataFrame(rows).sort_values("mean_abs_log10_error").reset_index(drop=True)


# ----------------------------------------------------------------------------
# (b) peeling and dominance on real instances
# ----------------------------------------------------------------------------


def peel(matrix: np.ndarray, k_c: int = 2, k_p: int = 2) -> tuple[np.ndarray, np.ndarray]:
    """The (k_c, k_p)-core of the incidence graph: repeatedly drop customers
    with fewer than k_c remaining products and products with fewer than k_p
    remaining customers. Returns boolean masks (customers kept, products kept)."""
    a = np.asarray(matrix, dtype=np.int64)
    cust = np.ones(a.shape[0], dtype=bool)
    prod = np.ones(a.shape[1], dtype=bool)
    while True:
        deg_c = a[:, prod].sum(axis=1)
        new_c = cust & (deg_c >= k_c)
        deg_p = a[new_c, :].sum(axis=0)
        new_p = prod & (deg_p >= k_p)
        if new_c.sum() == cust.sum() and new_p.sum() == prod.sum():
            return cust, prod
        cust, prod = new_c, new_p


def bipartite_components(matrix: np.ndarray, cust: np.ndarray, prod: np.ndarray) -> int:
    """Connected components of the incidence subgraph induced by the masks."""
    a = np.asarray(matrix, dtype=bool)
    ci = np.where(cust)[0]
    pi = np.where(prod)[0]
    if len(ci) == 0 and len(pi) == 0:
        return 0
    parent = {("c", i): ("c", i) for i in ci}
    parent.update({("p", j): ("p", j) for j in pi})

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in ci:
        for j in pi[a[i, pi]]:
            ra, rb = find(("c", i)), find(("p", j))
            if ra != rb:
                parent[ra] = rb
    return len({find(x) for x in parent})


def core_record(matrix: np.ndarray, k_c: int, k_p: int, prefix: str) -> dict:
    a = np.asarray(matrix, dtype=np.int64)
    n, m = a.shape
    cust, prod = peel(a, k_c, k_p)
    nc, npd = int(cust.sum()), int(prod.sum())
    edges = int(a[np.ix_(cust, prod)].sum()) if nc and npd else 0
    comps = bipartite_components(a, cust, prod) if nc else 0
    cyc = edges - nc - npd + comps
    return {f"{prefix}_cust_frac": nc / n, f"{prefix}_prod_frac": npd / m if m else np.nan,
            f"{prefix}_edges_n": edges / n, f"{prefix}_cyc_n": cyc / n,
            f"{prefix}_cyc_per_core_cust": cyc / nc if nc else np.nan,
            f"{prefix}_excess": (edges - npd) / nc if nc else np.nan,
            f"{prefix}_row_mean": edges / nc if nc else np.nan, f"{prefix}_components": comps}


def dominance_record(matrix: np.ndarray) -> dict:
    """The instance the solver sees at the root: products whose customer set
    sits inside another's dropped (pattern dominance, `mosp.preprocess`), then
    customers whose closed neighbourhood sits inside another's (the search's
    subset rule at the root; ties keep the lowest index). Excess and
    cyclomatic number of what survives."""
    a = np.asarray(matrix, dtype=bool)
    n, m = a.shape
    cols = [frozenset(np.where(a[:, j])[0]) for j in range(m)]
    keep_p = [j for j, own in enumerate(cols)
              if len(own) and not any((own < other) or (own == other and q < j) for q, other in enumerate(cols) if q != j)]
    b = a[:, keep_p]
    adj = (b.astype(np.int64) @ b.astype(np.int64).T) > 0
    nbh = [frozenset(np.where(adj[i])[0]) | {i} for i in range(n)]
    keep_c = [i for i, own in enumerate(nbh)
              if not any((own < other) or (own == other and q < i) for q, other in enumerate(nbh) if q != i)]
    c = b[keep_c, :]
    cols2 = [frozenset(np.where(c[:, j])[0]) for j in range(c.shape[1])]
    keep_p2 = [j for j, own in enumerate(cols2)
               if len(own) and not any((own < other) or (own == other and q < j) for q, other in enumerate(cols2) if q != j)]
    d = c[:, keep_p2]
    nd, md = d.shape
    ones = int(d.sum())
    comps = bipartite_components(d, np.ones(nd, bool), np.ones(md, bool)) if nd else 0
    return {"dom_cust_frac": nd / n, "dom_prod_frac": md / m if m else np.nan,
            "dom_excess": (ones - md) / nd if nd else np.nan,
            "dom_cyc_per_cust": (ones - nd - md + comps) / nd if nd else np.nan,
            "dom_row_mean": ones / nd if nd else np.nan}


def measure_instance(instance: MOSPInstance) -> dict:
    a = np.asarray(instance.matrix, dtype=np.int64)
    n, m = a.shape
    comps = bipartite_components(a, np.ones(n, bool), np.ones(m, bool))
    row = {"instance_name": instance.name, "bip_cyc_exact": (int(a.sum()) - n - m + comps) / n,
           "bip_components": comps}
    row.update(core_record(a, 2, 2, "core2"))
    row.update(core_record(a, 3, 2, "core32"))
    row.update(core_record(a, 2, 3, "core23"))
    row.update(core_record(a, 3, 3, "core33"))
    row.update(dominance_record(a))
    return row


def _measure_job(args) -> dict:
    from learning.ensemble import generate

    name, generator, n, m, param, index = args
    inst = generate(Cell(generator, int(n), int(m), float(param)), int(index))
    row = measure_instance(inst)
    row["instance_name"] = name
    return row


def measure(frame: pd.DataFrame | None = None, csv: Path = MEASURES_CSV, sizes=SIZES,
            workers: int = 16, limit: int | None = None) -> pd.DataFrame:
    """Peel and reduce every certified instance of every cell at n in `sizes`
    (both generators, every ratio; ~9,500 instances); resumable, appends."""
    frame = load_frames() if frame is None else frame
    todo = frame[frame["n"].isin(sizes)][["instance_name", "generator", "n", "m", "param", "index"]]
    todo = todo.drop_duplicates("instance_name")
    done = set()
    if csv.exists():
        done = set(pd.read_csv(csv)["instance_name"])
    todo = todo[~todo["instance_name"].isin(done)]
    if limit is not None:
        todo = todo.head(limit)
    jobs = [tuple(x) for x in todo.itertuples(index=False, name=None)]
    print(f"[cover_excess] {len(jobs)} instances to measure ({len(done)} done)", flush=True)
    t0 = time.time()
    rows = []
    if jobs:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for i, row in enumerate(pool.map(_measure_job, jobs, chunksize=32), 1):
                rows.append(row)
                if i % 2000 == 0:
                    print(f"  {i}/{len(jobs)} in {time.time() - t0:.0f}s", flush=True)
        new = pd.DataFrame(rows)
        new.to_csv(csv, mode="a", header=not csv.exists(), index=False)
    print(f"[cover_excess] measured {len(rows)} in {time.time() - t0:.0f}s", flush=True)
    return pd.read_csv(csv).drop_duplicates("instance_name")


# ----------------------------------------------------------------------------
# (c) checks, constancy and calibrated predictions with the new candidates
# ----------------------------------------------------------------------------

NEW_EMPIRICAL = {
    "core2_cust_frac": "2-core: share of customers",
    "core2_prod_frac": "2-core: share of products",
    "core2_cyc_n": "2-core: cyclomatic number / n",
    "core2_cyc_per_core_cust": "2-core: cyclomatic number per core customer",
    "core2_excess": "2-core: excess of the core instance",
    "core2_row_mean": "2-core: products per core customer",
    "core32_cust_frac": "(3,2)-core: share of customers",
    "core32_cyc_per_core_cust": "(3,2)-core: cyclomatic number per core customer",
    "core33_cust_frac": "(3,3)-core: share of customers",
    "dom_cust_frac": "dominance-reduced: share of customers kept",
    "dom_prod_frac": "dominance-reduced: share of products kept",
    "dom_excess": "dominance-reduced: excess",
    "dom_cyc_per_cust": "dominance-reduced: cyclomatic number per kept customer",
    "dom_row_mean": "dominance-reduced: products per kept customer",
}


def merged_frame(measures: pd.DataFrame, frame: pd.DataFrame | None = None) -> pd.DataFrame:
    frame = load_frames() if frame is None else frame
    return frame.merge(measures, on="instance_name", how="left")


def cell_medians_new(frame: pd.DataFrame, config: str = "default") -> pd.DataFrame:
    """§25's cell medians plus the medians of the new empirical candidates."""
    cells = cell_medians(frame, config)
    extra = (frame.groupby(["generator", "ratio_label", "n", "param"])[list(NEW_EMPIRICAL)]
             .median().reset_index())
    return cells.merge(extra, on=["generator", "ratio_label", "n", "param"], how="left")


def peaks_with_new(frame: pd.DataFrame, cells: pd.DataFrame, config: str = "default", min_n: int = 50,
                   resamples: int = 500) -> pd.DataFrame:
    """§25's interpolated peaks, each new candidate interpolated to the peak
    col_mean (cell medians, linear in log col_mean), and the analytic core
    quantities at the peak."""
    peaks = peak_table(frame, cells, config, min_n, resamples)
    for i, p in peaks.iterrows():
        g = cells[(cells["generator"] == p["generator"]) & (cells["ratio_label"] == p["ratio_label"])
                  & (cells["n"] == p["n"])]
        for cand in NEW_EMPIRICAL:
            peaks.loc[i, cand] = _interp_at(g, cand, p["peak_col_mean"])
        for cand, (_, _, fn) in NEW_ANALYTIC.items():
            peaks.loc[i, "an_" + cand] = fn(p["generator"], p["r_exact"], p["peak_col_mean"], p["n"])
    return peaks


def constancy_new(peaks: pd.DataFrame, min_n: int = 50) -> pd.DataFrame:
    """§25 (c) with the new candidates: CV across ratios at fixed (generator, n)."""
    from learning.ridge_theory import constancy

    text = dict(CANDIDATE_TEXT)
    text.update(NEW_EMPIRICAL)
    text.update({"an_" + k: "analytic " + v[0] for k, v in NEW_ANALYTIC.items()})
    cands = [c for c in list(CANDIDATES) + list(NEW_EMPIRICAL) + ["an_" + k for k in NEW_ANALYTIC]
             if c in peaks.columns]
    import learning.ridge_theory as rt
    saved = rt.CANDIDATE_TEXT
    rt.CANDIDATE_TEXT = text
    try:
        out = constancy(peaks, min_n, cands)
    finally:
        rt.CANDIDATE_TEXT = saved
    out["new"] = out["candidate"].isin(list(NEW_EMPIRICAL) + ["an_" + k for k in NEW_ANALYTIC])
    return out


def predict_new(peaks: pd.DataFrame, cells: pd.DataFrame, min_n: int = 50, calibrate_on: str = "n") -> pd.DataFrame:
    """§25 (d) for the new candidates: calibrated at the m = n peaks of each
    generator, predict every other series' peak; analytic candidates by
    inversion, empirical ones by interpolation along the series."""
    rows = []
    cands = {**{k: ("empirical", v) for k, v in NEW_EMPIRICAL.items()},
             **{"an_" + k: ("analytic", v[0]) for k, v in NEW_ANALYTIC.items() if k not in ("tree", "row_mean_conn")}}
    for cand, (kind, text) in cands.items():
        for gen in peaks["generator"].unique():
            cal = peaks[(peaks["generator"] == gen) & (peaks["ratio_label"] == calibrate_on) & (peaks["n"] >= min_n)]
            if not len(cal) or not np.isfinite(cal[cand]).all():
                continue
            target = float(cal[cand].mean())
            sub = peaks[(peaks["generator"] == gen) & (peaks["n"] >= min_n)]
            for _, p in sub.iterrows():
                if kind == "analytic":
                    fn = NEW_ANALYTIC[cand[3:]][2]
                    pred = invert_analytic(lambda c: fn(gen, p["r_exact"], c, p["n"]), target)
                else:
                    g = cells[(cells["generator"] == gen) & (cells["ratio_label"] == p["ratio_label"])
                              & (cells["n"] == p["n"])].sort_values("col_mean")
                    x, y = np.log10(g["col_mean"].to_numpy(float)), g[cand].to_numpy(float)
                    ok = np.isfinite(y)
                    x, y = x[ok], y[ok]
                    if len(y) < 2:
                        pred = np.nan
                    elif y[-1] >= y[0]:
                        pred = 10 ** float(np.interp(target, y, x, left=np.nan, right=np.nan))
                    else:
                        pred = 10 ** float(np.interp(-target, -y, x, left=np.nan, right=np.nan))
                meas, lo, hi = p["peak_col_mean"], p["ci_lo"], p["ci_hi"]
                err = float(np.log10(pred / meas)) if np.isfinite(pred) and pred > 0 else np.nan
                within = bool(lo <= pred <= hi) if np.isfinite(lo) else bool(np.isfinite(err) and abs(err) <= 0.05)
                rows.append({"candidate": cand, "text": text, "generator": gen, "ratio_label": p["ratio_label"],
                             "n": int(p["n"]), "calibration": target, "predicted_col_mean": pred,
                             "measured_col_mean": meas, "ci_lo": lo, "ci_hi": hi, "log10_error": err,
                             "within_ci": within, "is_calibration": p["ratio_label"] == calibrate_on})
    return pd.DataFrame(rows)


def prediction_summary_new(pred: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cand, g in pred[~pred["is_calibration"]].groupby("candidate"):
        dec = g[g["ratio_label"].isin(["n/2", "n/4", "n/8"])]
        rows.append({"candidate": cand, "text": g["text"].iloc[0], "series": len(g),
                     "mean_abs_log10_error": float(g["log10_error"].abs().mean()),
                     "max_abs_log10_error": float(g["log10_error"].abs().max()),
                     "within_ci": int(g["within_ci"].sum()), "undefined": int(g["log10_error"].isna().sum()),
                     "deciding_series": len(dec),
                     "deciding_mean_abs_log10_error": float(dec["log10_error"].abs().mean()) if len(dec) else np.nan,
                     "deciding_within_ci": int(dec["within_ci"].sum())})
    return pd.DataFrame(rows).sort_values("mean_abs_log10_error").reset_index(drop=True)


def core_check(cells: pd.DataFrame, min_n: int = 50) -> pd.DataFrame:
    """Analytic 2-core and (3,2)-core shares against the peeled medians, per cell."""
    rows = []
    for _, c in cells[cells["n"] >= min_n].iterrows():
        q2 = core_quantities(c["generator"], c["r_exact"], c["col_mean"], 2, 2)
        q32 = core_quantities(c["generator"], c["r_exact"], c["col_mean"], 3, 2)
        rows.append({"generator": c["generator"], "ratio_label": c["ratio_label"], "n": int(c["n"]),
                     "col_mean": c["col_mean"], "instances": int(c["instances"]),
                     "core2_cust_measured": c["core2_cust_frac"], "core2_cust_predicted": q2["cust_frac"],
                     "core2_cyc_measured": c["core2_cyc_n"], "core2_cyc_predicted": q2["cyc_n"],
                     "core32_cust_measured": c["core32_cust_frac"], "core32_cust_predicted": q32["cust_frac"]})
    out = pd.DataFrame(rows)
    out["core2_cust_err"] = out["core2_cust_predicted"] - out["core2_cust_measured"]
    out["core2_cyc_err"] = out["core2_cyc_predicted"] - out["core2_cyc_measured"]
    out["core32_cust_err"] = out["core32_cust_predicted"] - out["core32_cust_measured"]
    return out


def height_vs_new(peaks: pd.DataFrame, min_n: int = 50) -> pd.DataFrame:
    """The new quantities at every peak, one row per series, for the report."""
    cols = ["generator", "ratio_label", "n", "peak_col_mean", "peak_median_log_nodes", "excess", "bip_cyc",
            "core2_cust_frac", "core2_prod_frac", "core2_cyc_n", "core2_cyc_per_core_cust", "core2_excess",
            "core2_row_mean", "core32_cust_frac", "core33_cust_frac", "dom_cust_frac", "dom_prod_frac",
            "dom_excess", "dom_cyc_per_cust", "an_core2_cust_frac", "an_core2_cyc_per_core_cust",
            "an_core32_cust_frac"]
    return peaks[peaks["n"] >= min_n][[c for c in cols if c in peaks.columns]].reset_index(drop=True)


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def report(out: Path = TABLES, resamples: int = 500, csv: Path = MEASURES_CSV) -> dict:
    t0 = time.time()
    measures = pd.read_csv(csv).drop_duplicates("instance_name")
    frame = merged_frame(measures)
    cells = cell_medians_new(frame)
    peaks = peaks_with_new(frame, cells, resamples=resamples)
    thr = threshold_table(peaks)
    thr_sum = threshold_summary(thr)
    cons = constancy_new(peaks)
    pred = predict_new(peaks, cells)
    pred_sum = prediction_summary_new(pred)
    check = core_check(cells)
    at_peaks = height_vs_new(peaks)
    # the analytic curves per ratio, for the report's derivation table
    curve_rows = []
    for gen in ("fixed", "bernoulli"):
        for lab, r in RATIOS.items():
            row = {"generator": gen, "ratio_label": lab, "r": r,
                   "giant": giant_threshold_col_mean(r, gen), "forest": tree_threshold_col_mean(r),
                   "excess2": 1 + 2 / r, "excess2.4": 1 + 2.4 / r,
                   "core32": core_threshold_col_mean(gen, r, 3, 2), "core23": core_threshold_col_mean(gen, r, 2, 3),
                   "core33": core_threshold_col_mean(gen, r, 3, 3),
                   "core2_half": invert_analytic(lambda c: core_quantities(gen, r, c)["cust_frac"], 0.5),
                   "core2_cyc_eq_cust (= core excess 2)": invert_analytic(
                       lambda c: core_quantities(gen, r, c)["cyc_per_core_cust"], 1.0),
                   "conn_n50": connectivity_col_mean(r, 50), "conn_n75": connectivity_col_mean(r, 75)}
            meas = peaks[(peaks["generator"] == gen) & (peaks["ratio_label"] == lab) & (peaks["n"] >= 50)]
            row["measured_peaks"] = " / ".join(f"{v:.2f}" for v in meas.sort_values("n")["peak_col_mean"]) if len(meas) else ""
            curve_rows.append(row)
    curves = pd.DataFrame(curve_rows)
    states = pd.read_csv(STATES_CSV).drop_duplicates("instance_name") if STATES_CSV.exists() else pd.DataFrame()
    st = states_tables(states) if len(states) else {"cells": pd.DataFrame(), "peaks": pd.DataFrame()}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as fh:
        fh.write("# Cover excess tables (§36)\n\n")
        fh.write(f"*Regenerate: `python -m learning.cover_excess --stage tables`. Measured instances: "
                 f"{len(measures)}; merged rows at n in {SIZES}: {int(frame['n'].isin(SIZES).sum())}. "
                 f"{time.time() - t0:.0f} s.*\n\n")
        fh.write("## Analytic thresholds of the incidence graph in col_mean, per generator and ratio, against the measured peaks (n = 50 / 60 / 75)\n\n")
        fh.write(_md(curves) + "\n\n")
        fh.write("## Every threshold at its natural value: predicted ridge against measured peaks, summary\n\n")
        fh.write(_md(thr_sum) + "\n\n")
        fh.write("## Every threshold at its natural value, per series\n\n")
        fh.write(_md(thr) + "\n\n")
        fh.write("## Analytic cores against peeled cores, per cell (n >= 50)\n\n")
        fh.write(_md(check) + "\n\n")
        fh.write("## The new quantities at every interpolated peak (n >= 50)\n\n")
        fh.write(_md(at_peaks) + "\n\n")
        fh.write("## Constancy across m / n at fixed (generator, n), §25's candidates and the new ones\n\n")
        fh.write(_md(cons) + "\n\n")
        fh.write("## Calibrated at m = n, predicted at the other ratios: the new candidates, summary\n\n")
        fh.write(_md(pred_sum) + "\n\n")
        fh.write("## Calibrated predictions, per series\n\n")
        fh.write(_md(pred) + "\n\n")
        fh.write("## Mechanism: exact counts of (optimum − 1)-feasible closed sets at n = 20 and 25, per series\n\n")
        fh.write((_md(st["peaks"]) if len(st["peaks"]) else "(no state counts on disk)") + "\n\n")
        fh.write("## Mechanism: per cell at n = 20 and 25\n\n")
        fh.write((_md(st["cells"]) if len(st["cells"]) else "(none)") + "\n\n")

    print(f"[cover_excess] wrote {out} in {time.time() - t0:.0f}s")
    return {"curves": curves, "thresholds": thr, "threshold_summary": thr_sum, "check": check, "states": st,
            "peaks": peaks, "constancy": cons, "predictions": pred, "prediction_summary": pred_sum,
            "at_peaks": at_peaks, "cells": cells, "frame": frame}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=("measure", "tables"), required=True)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--resamples", type=int, default=500)
    args = ap.parse_args()
    if args.stage == "measure":
        measure(workers=args.workers, limit=args.limit)
    else:
        report(resamples=args.resamples)



# ----------------------------------------------------------------------------
# (d) a mechanism: the number of k-feasible closed sets
# ----------------------------------------------------------------------------
#
# The customer search visits closed sets S whose open-stack cost |N[S] \ S| is
# at most k, modulo dominance and memoisation. If the refutation cost at
# k = optimum - 1 tracks the number of such sets, the ridge is where that
# number peaks: connectivity multiplies the sets with small boundary until the
# optimum's rise towards n starves them. The count is exact by subset DP at
# n <= 25 and is approximated in the random model by treating the customers
# outside S as independent, each in N[S] with the probability a product joins
# it to S.

STATES_CSV = ENSEMBLE_DIR / "cover_excess_states.csv"
_POPCOUNT8 = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def _popcount32(a: np.ndarray) -> np.ndarray:
    return _POPCOUNT8[a.view(np.uint8)].reshape(-1, 4).sum(axis=1, dtype=np.uint8)


def feasible_states(instance: MOSPInstance, k: int) -> int:
    """The number of customer sets S (including the empty set and V) whose
    closed neighbourhood has at most k customers outside S; n <= 25."""
    a = np.asarray(instance.matrix, dtype=np.int64)
    n = a.shape[0]
    if n > 25:
        raise ValueError("subset DP is for n <= 25")
    adj = (a @ a.T) > 0
    masks = np.array([int("".join("1" if adj[i, j] else "0" for j in reversed(range(n))), 2) for i in range(n)],
                     dtype=np.uint32)
    nb = np.zeros(1 << n, dtype=np.uint32)
    for b in range(n):
        lo, hi = 1 << b, 1 << (b + 1)
        nb[lo:hi] = nb[:lo] | masks[b]
    idx = np.arange(1 << n, dtype=np.uint32)
    cost = _popcount32(nb).astype(np.int16) - _popcount32(idx).astype(np.int16)
    return int(np.count_nonzero(cost <= k))


def reachable_states(instance: MOSPInstance, k: int) -> tuple[int, int]:
    """(feasible, reachable): the number of customer sets S whose closing step
    fits -- the search's cost of closing the last customer of S is
    |N[S]| - |S| + 1 (every customer of N[S] has opened, those of S other than
    the one being closed have closed) -- and the number of those reachable
    from the empty set through a chain of fitting sets, S \\ {c} -> S. The
    reachable count is the search tree without dominance and without the memo:
    the state space the refutation at k = optimum - 1 has to exhaust."""
    a = np.asarray(instance.matrix, dtype=np.int64)
    n = a.shape[0]
    if n > 25:
        raise ValueError("subset DP is for n <= 25")
    adj = (a @ a.T) > 0
    masks = np.array([int("".join("1" if adj[i, j] else "0" for j in reversed(range(n))), 2) for i in range(n)],
                     dtype=np.uint32)
    size = 1 << n
    nb = np.zeros(size, dtype=np.uint32)
    for b in range(n):
        lo, hi = 1 << b, 1 << (b + 1)
        nb[lo:hi] = nb[:lo] | masks[b]
    idx = np.arange(size, dtype=np.uint32)
    pop = _popcount32(idx).astype(np.int16)
    fits = (_popcount32(nb).astype(np.int16) - pop + 1) <= k
    fits[0] = True
    order = np.argsort(pop, kind="stable").astype(np.uint32)
    counts = np.bincount(pop, minlength=n + 1)
    starts = np.concatenate([[0], np.cumsum(counts)])
    reach = np.zeros(size, dtype=bool)
    reach[0] = True
    for s in range(1, n + 1):
        layer = order[starts[s]:starts[s + 1]]
        pred = np.zeros(len(layer), dtype=bool)
        for b in range(n):
            bit = np.uint32(1 << b)
            has = (layer & bit) != 0
            pred |= has & reach[layer ^ bit]
        reach[layer] = fits[layer] & pred
    return int(np.count_nonzero(fits)), int(np.count_nonzero(reach))


def expected_feasible_states(n: int, m: float, c: float, generator: str, k: float) -> float:
    """log10 of the expected number of sets S with |N[S] \\ S| <= k in the random
    model, customers outside S treated as independent: sum over s of
    C(n, s) P(Bin(n - s, pi_s) <= k), where pi_s is the probability that a
    fixed customer outside S shares a product with S."""
    from scipy.special import gammaln

    s = np.arange(0, n + 1, dtype=float)
    if generator == "fixed":
        d = float(c)
        # P(a product misses S | it contains v) = C(n-1-s, d-1) / C(n-1, d-1), by log-gamma for real d
        def logc(a, b):
            return gammaln(a + 1) - gammaln(b + 1) - gammaln(a - b + 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            miss = np.exp(logc(n - 1 - s, d - 1) - logc(n - 1, d - 1))
        miss = np.where(n - 1 - s >= d - 1, np.nan_to_num(miss, nan=0.0), 0.0)
        q = (d / n) * (1.0 - miss)
    else:
        p = c / n
        q = p * (1.0 - (1.0 - p) ** s)
    pi = 1.0 - (1.0 - np.clip(q, 0.0, 1.0)) ** m
    tail = binom.cdf(np.floor(k), (n - s).astype(int), pi)         # P(boundary <= k)
    log_terms = gammaln(n + 1) - gammaln(s + 1) - gammaln(n - s + 1) + np.log(np.maximum(tail, 1e-300))
    top = log_terms.max()
    return float((top + np.log(np.exp(log_terms - top).sum())) / np.log(10))


def _states_job(args) -> dict:
    from learning.ensemble import generate

    name, generator, n, m, param, index, optimum = args
    inst = generate(Cell(generator, int(n), int(m), float(param)), int(index))
    k = int(optimum) - 1
    boundary = feasible_states(inst, k)                       # |N[S] \\ S| <= k, the boundary count
    fits, reach = reachable_states(inst, k)                   # the search's step cost, and reachability
    return {"instance_name": name, "k": k, "feasible_states": boundary, "log10_states": float(np.log10(boundary)),
            "fitting_states": fits, "log10_fitting": float(np.log10(fits)),
            "reachable_states": reach, "log10_reachable": float(np.log10(max(reach, 1))),
            "log10_states_predicted": expected_feasible_states(int(n), int(m), float(inst.matrix.sum() / m),
                                                               generator, k)}


def measure_states(csv: Path = STATES_CSV, sizes=(20, 25), per_cell: dict | None = None,
                   workers: int = 8) -> pd.DataFrame:
    """Exact k-feasible set counts at k = optimum - 1 on the campaign cells at
    n in `sizes` (default 150 per cell at 20, 40 at 25), with the random-model
    prediction beside each; resumable, appends."""
    from learning.ensemble import load_results
    from learning.ridge_theory import RESULTS_CSV

    per_cell = per_cell or {20: 150, 25: 40}
    frame = load_results(RESULTS_CSV)
    frame = frame[frame["n"].isin(sizes) & frame["certified"].astype(bool)]
    parts = []
    for (n, gen, m, param), g in frame.groupby(["n", "generator", "m", "param"]):
        parts.append(g.sort_values("index").head(per_cell.get(int(n), 40)))
    todo = pd.concat(parts)[["instance_name", "generator", "n", "m", "param", "index", "optimum"]]
    done = set(pd.read_csv(csv)["instance_name"]) if csv.exists() else set()
    todo = todo[~todo["instance_name"].isin(done)]
    jobs = [tuple(x) for x in todo.itertuples(index=False, name=None)]
    print(f"[cover_excess] {len(jobs)} state counts to do ({len(done)} done)", flush=True)
    t0 = time.time()
    rows = []
    if jobs:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for i, row in enumerate(pool.map(_states_job, jobs, chunksize=4), 1):
                rows.append(row)
                if i % 500 == 0:
                    print(f"  {i}/{len(jobs)} in {time.time() - t0:.0f}s", flush=True)
        pd.DataFrame(rows).to_csv(csv, mode="a", header=not csv.exists(), index=False)
    print(f"[cover_excess] counted {len(rows)} in {time.time() - t0:.0f}s", flush=True)
    return pd.read_csv(csv).drop_duplicates("instance_name")


def states_tables(states: pd.DataFrame, frame: pd.DataFrame | None = None) -> dict:
    """Per cell at n in {20, 25}: median log10 nodes (default), median log10
    feasible states (exact) and predicted; per series the peak cell of each;
    Spearman correlation between nodes and states across instances."""
    from scipy.stats import spearmanr

    from learning.ensemble import load_results
    from learning.ridge_theory import RESULTS_CSV, derive

    frame = derive(load_results(RESULTS_CSV)) if frame is None else frame
    f = frame.merge(states, on="instance_name", how="inner")
    cells = (f.groupby(["generator", "ratio_label", "n", "param"])
             .agg(instances=("instance_name", "size"), col_mean=("col_mean", "median"),
                  excess=("excess", "median"), optimum=("optimum", "median"),
                  median_log_nodes=("ln_default", "median"), median_log_states=("log10_states", "median"),
                  median_log_reachable=("log10_reachable", "median"),
                  median_log_states_predicted=("log10_states_predicted", "median"),
                  censored=("cens_default", "sum")).reset_index())
    peaks = []
    for (gen, lab, n), g in cells.groupby(["generator", "ratio_label", "n"]):
        g = g.sort_values("col_mean")
        pn, ps, pr = (g.loc[g[col].idxmax()] for col in ("median_log_nodes", "median_log_states",
                                                          "median_log_reachable"))
        sub = f[(f["generator"] == gen) & (f["ratio_label"] == lab) & (f["n"] == n)]
        rho = spearmanr(sub["ln_default"], sub["log10_states"]).correlation
        rho_r = spearmanr(sub["ln_default"], sub["log10_reachable"]).correlation
        peaks.append({"generator": gen, "ratio_label": lab, "n": int(n), "cells": len(g),
                      "peak_nodes_col_mean": pn["col_mean"], "peak_nodes_excess": pn["excess"],
                      "peak_states_col_mean": ps["col_mean"], "peak_states_excess": ps["excess"],
                      "peak_reachable_col_mean": pr["col_mean"], "peak_reachable_excess": pr["excess"],
                      "states_monotone": bool(np.all(np.diff(g["median_log_states"].to_numpy()) >= -1e-9)),
                      "spearman_nodes_states": float(rho), "spearman_nodes_reachable": float(rho_r),
                      "median_log_nodes_minus_reachable": float((sub["ln_default"] - sub["log10_reachable"]).median()),
                      "median_abs_prediction_error": float((sub["log10_states_predicted"] - sub["log10_states"]).abs().median())})
    return {"cells": cells, "peaks": pd.DataFrame(peaks), "merged": f}


if __name__ == "__main__":
    main()
