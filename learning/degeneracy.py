"""How degenerate is the optimum? Counting every optimal ordering exactly (plan §2.6b)

Question. `learning.policy` imitates "the" witness closing order of each
certified instance, and §7 of `reports/ml_nature.md` found a policy imitating
45% of witness decisions beating a rule imitating 62%. That is only possible if
the witnesses disagree with each other -- if many closing orders are optimal
and the one in `solutions/` is an arbitrary member. This module counts them.

Three exact counts per instance, all by dynamic programming over the subset
lattice rather than by listing permutations, so the counts are exact where
`n!` and `m!` are not enumerable:

  * **closing orders, construction value** (`count_closing`): the number of
    permutations of the customers whose product order, built by
    `product_order_from_customers` (Chu & Stuckey 2009 §2: every unproduced
    product of the first customer in index order, then the second's, ...),
    simulates on the original instance to exactly the optimum. The value of
    a permutation is the peak of `mosp.verify.count_open_stacks`, so this is
    the space `learning.policy` constructs in and is scored in. The state is
    the set `S` of closed customers; the cost of closing `c` next depends on
    `(S, c)` only, so the count is a path count through feasible edges;
  * **closing orders, search measure** (`count_search`): the same with Chu &
    Stuckey's `max_i |O(S_i) - S_{i-1}|` (`satisfiability.heuristics._cs_cost`),
    which is what the complete search branches on. It over-charges orders that
    place a customer whose products are all made late, so it is a subset of
    the first;
  * **product orders** (`count_products`, for `m <= --max-products-exact`):
    the number of permutations of the products whose open-stack peak equals
    the optimum. This is the object the MOSP objective is defined on, and the
    only one of the three where reversal is a symmetry: reversing a product
    order reverses its open-stack profile, so the count is always even and
    "unique up to reversal" means `count_products / (identical columns)! = 2`.

The minimum over each lattice is also returned, so every corpus instance is a
free audit: the construction minimum and the product-order minimum must both
equal the certified optimum (the first by Chu & Stuckey's lemma, the second by
definition), and the module raises if either does not.

Imitation. Along each witness's induced closing order the module counts, at
every step, how many of the remaining customers begin an optimal completion
(`choices`). A policy that always makes an optimal choice, uniformly at random
among them, agrees with the witness at `mean(1 / choices)` of the steps: this
is the **step-accuracy ceiling** of imitation, and how far below 1 it sits is
what §7's imitation rates have to be read against. The same statistics are
computed over all optimal orders, weighted by how many pass through each
state, so the ceiling does not depend on which witness the solver happened to
save.

Symmetries divided out. Customers with identical rows are twins in the MOSP
graph and swapping them changes nothing, so `count_closing` is divisible by the
product of the factorials of the row multiplicities, and `count_products` by
the same over column multiplicities. The search measure is a graph invariant,
so `count_search` is divisible by `|Aut(G)|` from `learning/data/canonical.csv`
when that file is present (the action of an automorphism on orderings is free).
Customers with no products and products with no customers are removed first;
they would multiply the counts by a factorial and contribute nothing.

Scope. Every corpus instance with at most `--max-customers` (default 15)
customers -- 2,812 of 6,376, sizes 9-15 -- and a generated `G(n, m, p)` sample
at n ∈ {8, 10, 12, 15}, m ∈ {n, 2n}, p ∈ {0.1, 0.2, 0.3, 0.5}, whose optimum
the lattice minimum supplies and `solve_mosp_exact` cross-checks, with its
witnesses persisted under `learning/data/degeneracy_solutions/` -- never under
`solutions/`. Nothing here touches `_lower_bound`, changes any default, or
writes to `solutions/`.

Run:
    python -m learning.degeneracy                       # ~90 s on 16 workers
    python -m learning.degeneracy --limit 200 --generated 0
    python -m learning.degeneracy --max-customers 12
    python -m learning.degeneracy --tables-only         # tables from the CSV

Writes `reports/degeneracy_tables.md` and `learning/data/degeneracy.csv`
(git-ignored, regenerable).
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from benchmarks.generator import generate_random_instance
from learning.dataset import DEFAULT_SOLUTIONS_DIR, enumerate_instances
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.heuristics import (
    _customer_order_from_products,
    _cs_cost,
    product_order_from_customers,
)
from satisfiability.mosp_solver import _solution_path

DATA_DIR = Path("learning/data")
DEFAULT_CSV = DATA_DIR / "degeneracy.csv"
DEFAULT_OUT = Path("reports/degeneracy_tables.md")
GENERATED_SOLUTIONS = DATA_DIR / "degeneracy_solutions"
CANONICAL_CSV = DATA_DIR / "canonical.csv"
INSTANCES_CSV = DATA_DIR / "instances.csv"

GENERATED_N = (8, 10, 12, 15)
GENERATED_P = (0.1, 0.2, 0.3, 0.5)
DENSITY_BANDS = ((0.0, 0.15), (0.15, 0.3), (0.3, 0.5), (0.5, 1.01))


# --------------------------------------------------------------------------
# The compact instance: active customers and non-empty products, as bitmasks
# --------------------------------------------------------------------------

class Compact:
    """An instance with empty rows and columns dropped, indexed 0..a-1 / 0..m-1.

    `customers[i]` and `products[j]` are the original indices, in increasing
    order, so the index order `product_order_from_customers` sorts by is the
    same before and after compaction.
    """

    def __init__(self, instance: MOSPInstance):
        matrix = np.asarray(instance.matrix)
        self.customers = [c for c in range(instance.n_customers) if matrix[c].sum() > 0]
        self.products = [p for p in range(instance.n_patterns) if matrix[:, p].sum() > 0]
        self.a = len(self.customers)
        self.m = len(self.products)
        self.prod = [0] * self.a      # product mask per compact customer
        self.holders = [0] * self.m   # customer mask per compact product
        for i, c in enumerate(self.customers):
            for j, p in enumerate(self.products):
                if matrix[c, p]:
                    self.prod[i] |= 1 << j
                    self.holders[j] |= 1 << i
        self.neigh = [0] * self.a     # self-inclusive neighbourhoods N[c]
        for j in range(self.m):
            for i in _bits(self.holders[j]):
                self.neigh[i] |= self.holders[j]
        self.position = {c: i for i, c in enumerate(self.customers)}

    def twin_factor(self) -> int:
        return _multiplicity_factor(self.prod)

    def column_factor(self) -> int:
        return _multiplicity_factor(self.holders)


def _bits(mask: int):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def _multiplicity_factor(masks) -> int:
    factor = 1
    for count in Counter(masks).values():
        factor *= math.factorial(count)
    return factor


# --------------------------------------------------------------------------
# Closing orders: the lattice of closed-customer sets
# --------------------------------------------------------------------------

def closing_weights(comp: Compact) -> tuple[list[int], list[int]]:
    """Edge costs of the closed-customer lattice under both measures.

    Returns `(search, construction)`, each a flat list indexed `S * a + c`
    holding the cost of closing `c` from state `S` (only for `c ∉ S`).

    * search: `|O(S ∪ {c}) − S|`, Chu & Stuckey's measure;
    * construction: the peak number of open stacks while the unproduced
      products of `c` are made in index order, which is exactly what
      `mosp.verify.count_open_stacks` reports on the constructed product
      order at those steps; `0` when `c` has nothing left to produce.
    """
    a, prod, holders, neigh = comp.a, comp.prod, comp.holders, comp.neigh
    size = 1 << a
    opened = [0] * size    # O(S): customers sharing a product with S
    made = [0] * size      # P(S): products of S
    for S in range(1, size):
        low = S & -S
        c = low.bit_length() - 1
        opened[S] = opened[S ^ low] | neigh[c]
        made[S] = made[S ^ low] | prod[c]
    done = [0] * size      # customers all of whose products are in P(S)
    for S in range(size):
        T = made[S]
        d = 0
        for c in range(a):
            if prod[c] & ~T == 0:
                d |= 1 << c
        done[S] = d

    full = size - 1
    search = [0] * (size * a)
    construction = [0] * (size * a)
    for S in range(size):
        O_S, T, dn = opened[S], made[S], done[S]
        base = S * a
        for c in _bits(full & ~S):
            search[base + c] = ((O_S | neigh[c]) & ~S).bit_count()
            rem = prod[c] & ~T
            if rem == 0:
                continue
            started, dcur, T2, peak = O_S, dn, T, 0
            while rem:
                low = rem & -rem
                rem ^= low
                p = low.bit_length() - 1
                T2 |= low
                started |= holders[p]
                cnt = (started & ~dcur).bit_count()
                if cnt > peak:
                    peak = cnt
                cand = holders[p] & ~dcur
                while cand:
                    lb = cand & -cand
                    cand ^= lb
                    if prod[lb.bit_length() - 1] & ~T2 == 0:
                        dcur |= lb
            construction[base + c] = peak
    return search, construction


def lattice_minimum(weights: list[int], a: int) -> int:
    """The bottleneck (min over orders of the max edge cost) through the lattice."""
    size = 1 << a
    best = [0] + [1 << 30] * (size - 1)
    for S in range(1, size):
        b = best[S]
        for c in _bits(S):
            prev = S ^ (1 << c)
            w = weights[prev * a + c]
            v = best[prev] if best[prev] > w else w
            if v < b:
                b = v
        best[S] = b
    return best[size - 1]


def lattice_counts(weights: list[int], a: int, k: int) -> tuple[list[int], list[int]]:
    """Forward and backward path counts through edges of cost `<= k`.

    `f[S]` orders of the customers in `S` reaching `S` within budget; `g[S]`
    completions from `S`. `f[full] == g[0]` is the number of orders of value
    at most `k`; at `k = optimum` that is the number of optimal orders.
    """
    size = 1 << a
    full = size - 1
    f = [0] * size
    f[0] = 1
    for S in range(1, size):
        total = 0
        for c in _bits(S):
            prev = S ^ (1 << c)
            if f[prev] and weights[prev * a + c] <= k:
                total += f[prev]
        f[S] = total
    g = [0] * size
    g[full] = 1
    for S in range(full - 1, -1, -1):
        total = 0
        base = S * a
        for c in _bits(full & ~S):
            nxt = S | (1 << c)
            if g[nxt] and weights[base + c] <= k:
                total += g[nxt]
        g[S] = total
    return f, g


def optimal_choices(weights: list[int], a: int, k: int, g: list[int], S: int) -> int:
    """How many customers can be closed next from `S` and still finish optimally."""
    full = (1 << a) - 1
    base = S * a
    return sum(1 for c in _bits(full & ~S)
               if weights[base + c] <= k and g[S | (1 << c)] > 0)


def path_weighted_choices(weights, a, k, f, g) -> dict[str, float]:
    """Mean optimal choices per step over *all* optimal orders, each order
    counted once (a state `S` lies on `f[S] * g[S]` of them)."""
    size = 1 << a
    full = size - 1
    total = f[full]
    if total == 0 or a == 0:
        return {"mean_choices": float("nan"), "ceiling": float("nan"),
                "forced_frac": float("nan")}
    sum_ch = 0
    sum_inv = 0.0
    sum_forced = 0
    for S in range(full):
        if f[S] == 0 or g[S] == 0:
            continue
        w = f[S] * g[S]
        ch = optimal_choices(weights, a, k, g, S)
        sum_ch += w * ch
        sum_inv += w / ch
        sum_forced += w * (ch == 1)
    steps = total * a
    return {"mean_choices": sum_ch / steps, "ceiling": sum_inv / steps,
            "forced_frac": sum_forced / steps}


def witness_choices(comp: Compact, weights, k, g, closing_order) -> dict:
    """Optimal-choice multiplicity at each step of one closing order.

    `closing_order` is in original customer indices; inactive customers are
    skipped. Returns the per-step choice counts and whether the order is itself
    optimal (every step within budget and completable).
    """
    a = comp.a
    S = 0
    choices: list[int] = []
    optimal = True
    for c in closing_order:
        if c not in comp.position:
            continue
        i = comp.position[c]
        if S & (1 << i):
            continue
        choices.append(optimal_choices(weights, a, k, g, S))
        nxt = S | (1 << i)
        if weights[S * a + i] > k or g[nxt] == 0:
            optimal = False
        S = nxt
    return {"optimal": optimal and S == (1 << a) - 1, "choices": choices}


# --------------------------------------------------------------------------
# Product orders: the lattice of produced-product sets, in numpy
# --------------------------------------------------------------------------

def product_lattice(comp: Compact, k: int | None = None) -> tuple[int, int]:
    """`(minimum, count)` over all product orders.

    The open-stack count at the step producing `p` from produced set `T` is the
    number of customers with a product in `T ∪ {p}` and one outside `T`;
    it depends on `(T, p)` only, so the minimum is a bottleneck path and the
    count of orders of peak `<= k` a path count, both layer by layer over the
    popcount of `T`. `count` is at `k = minimum` when `k` is None.
    """
    m, a, prod = comp.m, comp.a, comp.prod
    if m == 0:
        return 0, 1
    size = 1 << m
    T = np.arange(size, dtype=np.uint32)
    popcount = np.zeros(size, dtype=np.uint8)
    for b in range(m):
        popcount += ((T >> np.uint32(b)) & np.uint32(1)).astype(np.uint8)
    layers = [np.flatnonzero(popcount == j).astype(np.uint32) for j in range(m + 1)]

    touched = [(T & np.uint32(pm)) != 0 for pm in prod]
    finished = [(T & np.uint32(pm)) == np.uint32(pm) for pm in prod]
    counts = []
    for p in range(m):
        cnt = np.zeros(size, dtype=np.int16)
        for d in range(a):
            if (prod[d] >> p) & 1:
                cnt += (~finished[d]).astype(np.int16)
            else:
                cnt += (touched[d] & ~finished[d]).astype(np.int16)
        counts.append(cnt)

    best = np.full(size, np.iinfo(np.int16).max, dtype=np.int16)
    best[0] = 0
    for j in range(m):
        idx = layers[j]
        for p in range(m):
            bit = np.uint32(1 << p)
            sel = idx[(idx & bit) == 0]
            tgt = sel | bit
            cand = np.maximum(best[sel], counts[p][sel])
            best[tgt] = np.minimum(best[tgt], cand)
    minimum = int(best[size - 1])
    budget = minimum if k is None else k

    f = np.zeros(size, dtype=np.uint64)
    f[0] = 1
    for j in range(m):
        idx = layers[j]
        for p in range(m):
            bit = np.uint32(1 << p)
            sel = idx[(idx & bit) == 0]
            tgt = sel | bit
            feasible = counts[p][sel] <= budget
            f[tgt] += f[sel] * feasible.astype(np.uint64)
    return minimum, int(f[size - 1])


# --------------------------------------------------------------------------
# One instance
# --------------------------------------------------------------------------

def analyse(
    instance: MOSPInstance,
    optimum: int | None = None,
    witness: list[int] | None = None,
    max_products_exact: int = 20,
) -> dict:
    """Every count and statistic for one instance.

    `optimum` is the certified value when known; the construction minimum is
    checked against it and an `audit` field records the comparison. When it is
    None the construction minimum is the optimum.
    """
    comp = Compact(instance)
    a = comp.a
    row: dict[str, object] = {
        "instance_name": instance.name,
        "n_customers": instance.n_customers,
        "n_patterns": instance.n_patterns,
        "n_active": a,
        "m_active": comp.m,
        "density": float(np.asarray(instance.matrix).mean()) if instance.n_patterns else 0.0,
    }
    search_w, constr_w = closing_weights(comp)
    min_construction = lattice_minimum(constr_w, a)
    min_search = lattice_minimum(search_w, a)
    k = min_construction if optimum is None else int(optimum)
    row.update({
        "optimum": k,
        "min_construction": min_construction,
        "min_search": min_search,
        "audit_construction": min_construction == k,
        "audit_search": min_search == k,
        "complete_graph": k == a,
    })
    f_c, g_c = lattice_counts(constr_w, a, k)
    f_s, g_s = lattice_counts(search_w, a, k)
    count_closing = f_c[(1 << a) - 1]
    count_search = f_s[(1 << a) - 1]
    twin = comp.twin_factor()
    row.update({
        "count_closing": count_closing,
        "count_search": count_search,
        "twin_factor": twin,
        "closing_up_to_twins": count_closing // twin,
        "closing_fraction": count_closing / math.factorial(a) if a else float("nan"),
        "unique_closing": count_closing // twin == 1,
    })
    row.update({f"all_{key}": val for key, val in
                path_weighted_choices(constr_w, a, k, f_c, g_c).items()})

    if witness is not None:
        closing = _customer_order_from_products(instance, witness)
        info = witness_choices(comp, constr_w, k, g_c, closing)
        ch = info["choices"]
        constructed = product_order_from_customers(instance, closing)
        row.update({
            "witness_value": max_open_stacks(instance, list(witness)),
            "witness_construction_value": max_open_stacks(instance, constructed),
            "witness_construction_optimal": info["optimal"],
            "witness_search_cost": _cs_cost(_search_masks(instance), closing),
            "witness_mean_choices": float(np.mean(ch)) if ch else float("nan"),
            "witness_ceiling": float(np.mean([1 / c for c in ch])) if ch else float("nan"),
            "witness_forced_frac": float(np.mean([c == 1 for c in ch])) if ch else float("nan"),
            "witness_steps": len(ch),
            "witness_forced_steps": sum(c == 1 for c in ch),
            "witness_inv_sum": float(sum(1 / c for c in ch)),
        })
        row["witness_search_optimal"] = row["witness_search_cost"] == k
        # Reversal is not a symmetry of closing orders; this measures how often
        # it happens to preserve optimality anyway.
        reverse = witness_choices(comp, constr_w, k, g_c, closing[::-1])
        row["witness_reverse_optimal"] = reverse["optimal"]

    if comp.m <= max_products_exact:
        min_products, count_products = product_lattice(comp)
        col = comp.column_factor()
        row.update({
            "min_products": min_products,
            "audit_products": min_products == k,
            "count_products": count_products,
            "column_factor": col,
            "products_up_to_columns_reversal": count_products // col / 2,
            "unique_products": count_products // col == 2,
            "products_fraction": count_products / math.factorial(comp.m) if comp.m else float("nan"),
        })
    return row


def _search_masks(instance: MOSPInstance) -> list[int]:
    from satisfiability.heuristics import _neighbour_masks
    return _neighbour_masks(instance)


# --------------------------------------------------------------------------
# The corpus and the generated sample
# --------------------------------------------------------------------------

def _load_witness(instance: MOSPInstance, solutions_dir: Path) -> tuple[int, list[int]] | None:
    path = _solution_path(instance, solutions_dir)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return int(data["mosp_value"]), list(data["ordering"])


def _corpus_job(args):
    filepath, instance, optimum, witness, max_products = args
    started = time.time()
    row = analyse(instance, optimum, witness, max_products)
    row.update({"source": "corpus", "source_file": str(filepath),
                "collection": filepath.parts[2] if len(filepath.parts) > 2 else "",
                "seconds": time.time() - started})
    return row


def generated_sample(seeds: int, sizes=GENERATED_N, probabilities=GENERATED_P) -> list[MOSPInstance]:
    instances = []
    for n in sizes:
        for m in (n, 2 * n):
            for p in probabilities:
                for seed in range(seeds):
                    instances.append(generate_random_instance(
                        n, m, p, seed=1000 * n + 100 * m + seed,
                        name=f"gen_{n}x{m}_p{p:.2f}_s{seed}"))
    return instances


def _generated_job(args):
    instance, max_products, solutions_dir = args
    from satisfiability.mosp_solver import solve_mosp_exact
    started = time.time()
    value, ordering = solve_mosp_exact(instance, solutions_dir=solutions_dir)
    row = analyse(instance, None, ordering, max_products)
    row.update({"source": "generated", "source_file": "", "collection": "generated",
                "gen_p": float(instance.name.split("_p")[1].split("_")[0]),
                "solver_optimum": int(value),
                "audit_solver": int(value) == row["optimum"],
                "seconds": time.time() - started})
    return row


def run(
    max_customers: int = 15,
    max_products: int = 20,
    limit: int | None = None,
    generated_seeds: int = 8,
    workers: int = 16,
    solutions_dir: Path = DEFAULT_SOLUTIONS_DIR,
    verbose: bool = True,
) -> pd.DataFrame:
    jobs = []
    for filepath, instance in enumerate_instances():
        if instance.n_customers > max_customers:
            continue
        loaded = _load_witness(instance, solutions_dir)
        if loaded is None:
            continue
        optimum, witness = loaded
        jobs.append((filepath, instance, optimum, witness, max_products))
    if limit:
        jobs = jobs[:limit]
    gen = generated_sample(generated_seeds) if generated_seeds else []
    GENERATED_SOLUTIONS.mkdir(parents=True, exist_ok=True)
    gen_jobs = [(inst, max_products, GENERATED_SOLUTIONS) for inst in gen]
    if verbose:
        print(f"{len(jobs)} corpus instances with n <= {max_customers}, "
              f"{len(gen_jobs)} generated", flush=True)

    started = time.time()
    rows: list[dict] = []
    # Largest first so the pool's tail is short.
    jobs.sort(key=lambda j: -j[1].n_customers)
    gen_jobs.sort(key=lambda j: -j[0].n_customers)
    with multiprocessing.Pool(workers) as pool:
        for done, row in enumerate(pool.imap_unordered(_corpus_job, jobs, chunksize=4), 1):
            rows.append(row)
            if verbose and done % 250 == 0:
                print(f"  corpus {done}/{len(jobs)} at {time.time() - started:.0f}s", flush=True)
        for done, row in enumerate(pool.imap_unordered(_generated_job, gen_jobs, chunksize=2), 1):
            rows.append(row)
            if verbose and done % 64 == 0:
                print(f"  generated {done}/{len(gen_jobs)} at {time.time() - started:.0f}s", flush=True)
    frame = pd.DataFrame(rows)
    if verbose:
        print(f"{len(frame)} rows in {time.time() - started:.0f}s", flush=True)

    audit_cols = [c for c in ("audit_construction", "audit_products", "audit_solver") if c in frame]
    for col in audit_cols:
        bad = frame[frame[col] == False]  # noqa: E712 - NaN rows are "not computed"
        if len(bad):
            raise AssertionError(
                f"{col} failed on {len(bad)} instances: {bad.instance_name.tolist()[:10]}")

    if CANONICAL_CSV.exists():
        canon = pd.read_csv(CANONICAL_CSV, usecols=["instance_name", "graph_cert", "aut_order"])
        frame = frame.merge(canon, on="instance_name", how="left")
        has = frame.aut_order.notna() & (frame.source == "corpus")
        # 15! is stored as 1307674367999.9998 in the CSV: round before dividing.
        aut = frame.loc[has, "aut_order"].round().astype("int64")
        frame.loc[has, "search_up_to_aut"] = frame.loc[has, "count_search"] // aut
        frame.loc[has, "aut_divides"] = frame.loc[has, "count_search"] % aut == 0
    return frame


# --------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------

def _md(frame: pd.DataFrame, floatfmt: str = ".3f") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def _q(series: pd.Series, q: float) -> float:
    return float(series.quantile(q)) if len(series) else float("nan")


def _log10(series: pd.Series) -> pd.Series:
    return np.log10(series.astype(float).clip(lower=1e-300))


def degeneracy_by(frame: pd.DataFrame, key: str, label: str) -> pd.DataFrame:
    rows = []
    for value, group in frame.groupby(key, observed=True):
        rows.append({
            label: value,
            "instances": len(group),
            "complete %": 100 * group.complete_graph.mean(),
            "unique closing %": 100 * group.unique_closing.mean(),
            "closing orders (median)": float(group.count_closing.median()),
            "closing orders (p10)": _q(group.count_closing, 0.1),
            "closing orders (p90)": _q(group.count_closing, 0.9),
            "up to twins (median)": float(group.closing_up_to_twins.median()),
            "log10 fraction optimal (median)": float(_log10(group.closing_fraction).median()),
            "search-measure orders (median)": float(group.count_search.median()),
        })
    return pd.DataFrame(rows)


def products_by(frame: pd.DataFrame, key: str, label: str) -> pd.DataFrame:
    sub = frame[frame.count_products.notna()]
    rows = []
    for value, group in sub.groupby(key, observed=True):
        rows.append({
            label: value,
            "instances (m ≤ cap)": len(group),
            "complete %": 100 * group.complete_graph.mean(),
            "unique up to reversal %": 100 * group.unique_products.mean(),
            "product orders (median)": float(group.count_products.median()),
            "up to columns & reversal (median)": float(group.products_up_to_columns_reversal.median()),
            "up to columns & reversal (p90)": _q(group.products_up_to_columns_reversal, 0.9),
            "log10 fraction optimal (median)": float(_log10(group.products_fraction).median()),
        })
    return pd.DataFrame(rows)


def imitation_by(frame: pd.DataFrame, key: str, label: str) -> pd.DataFrame:
    sub = frame[frame.witness_steps.notna()]
    rows = []
    for value, group in sub.groupby(key, observed=True):
        steps = group.witness_steps.sum()
        rows.append({
            label: value,
            "instances": len(group),
            "witness optimal %": 100 * group.witness_construction_optimal.mean(),
            "witness search-optimal %": 100 * group.witness_search_optimal.mean(),
            "reversed witness optimal %": 100 * group.witness_reverse_optimal.mean(),
            "choices per step (witness)": float(group.witness_mean_choices.mean()),
            "choices per step (all optimal orders)": float(group.all_mean_choices.mean()),
            "forced steps % (witness)": 100 * group.witness_forced_steps.sum() / steps,
            "ceiling, pooled steps (witness)": float(group.witness_inv_sum.sum() / steps),
            "ceiling, per instance (witness)": float(group.witness_ceiling.mean()),
            "ceiling (all optimal orders)": float(group.all_ceiling.mean()),
        })
    return pd.DataFrame(rows)


DISTIL_CSV = DATA_DIR / "distil.csv"
DISTIL_POLICIES = {
    "agree:imit:lgbm": "LightGBM ranker (§7)",
    "agree:imit:mcn": "MCN (§7)",
    "agree:imit:lex:min newly_opened": "fewest new stacks (§7)",
    "agree:imit:lex:min newly_opened,max remaining_degree": "fewest new, then most neighbours (§7)",
}


def imitation_against_ceiling(frame: pd.DataFrame, distil_csv: Path = DISTIL_CSV) -> pd.DataFrame | None:
    """§7's measured per-instance imitation rates beside the ceiling, on the
    held-out instances the two studies share.

    A policy that agrees with the witness *more* often than `mean(1 / choices)`
    is reproducing the solver's tie-breaks among optimal moves, not optimality.
    """
    if not distil_csv.exists():
        return None
    distil = pd.read_csv(distil_csv)
    distil = distil[distil.role == "test"] if "role" in distil else distil
    cols = [c for c in DISTIL_POLICIES if c in distil]
    if not cols:
        return None
    joined = frame[frame.source == "corpus"].merge(
        distil[["instance_name"] + cols + (["agree:steps"] if "agree:steps" in distil else [])],
        on="instance_name", how="inner")
    if joined.empty:
        return None
    steps = joined.witness_steps
    rows = []
    for col in cols:
        # `agree:imit:*` are counts of agreeing steps; `agree:steps` the steps.
        rate = joined[col] / joined["agree:steps"] if "agree:steps" in joined else joined[col]
        rows.append({
            "policy": DISTIL_POLICIES[col],
            "instances": len(joined),
            "imitation rate (mean)": float(rate.mean()),
            "ceiling (mean)": float(joined.witness_ceiling.mean()),
            "rate − ceiling (mean)": float((rate - joined.witness_ceiling).mean()),
            "instances above ceiling %": 100 * float((rate > joined.witness_ceiling).mean()),
            "instances at or below %": 100 * float((rate <= joined.witness_ceiling).mean()),
            "forced-step share": float(joined.witness_forced_steps.sum() / steps.sum()),
        })
    return pd.DataFrame(rows)


def density_band(series: pd.Series) -> pd.Series:
    edges = [lo for lo, _ in DENSITY_BANDS] + [DENSITY_BANDS[-1][1]]
    labels = [f"{lo:.2f}–{min(hi, 1.0):.2f}" for lo, hi in DENSITY_BANDS]
    return pd.cut(series, edges, labels=labels, include_lowest=True, right=False)


def examples(frame: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    cols = ["instance_name", "collection", "n_active", "m_active", "optimum",
            "count_closing", "closing_up_to_twins", "count_search", "count_products",
            "products_up_to_columns_reversal", "witness_mean_choices"]
    cols = [c for c in cols if c in frame]
    corpus = frame[(frame.source == "corpus") & ~frame.complete_graph]
    least = corpus.sort_values(["closing_up_to_twins", "count_closing"]).head(n)
    most = corpus.sort_values("closing_fraction", ascending=False).head(n)
    return pd.concat([least.assign(which="fewest"), most.assign(which="most")])[["which"] + cols]


def write_tables(frame: pd.DataFrame, out: Path, seconds: float) -> None:
    corpus = frame[frame.source == "corpus"].copy()
    gen = frame[frame.source == "generated"].copy()
    corpus["density band"] = density_band(corpus.density)
    corpus["n"] = corpus.n_customers.astype(int)
    gen["n"] = gen.n_customers.astype(int)
    gen["m/n"] = (gen.n_patterns / gen.n_customers).round().astype(int)
    parts = [
        "# Degeneracy of the optimum — regenerated tables",
        "",
        f"Regenerate: `python -m learning.degeneracy`. Run time {seconds:.0f} s. "
        f"{len(corpus)} corpus instances (n ≤ {int(corpus.n_customers.max()) if len(corpus) else 0}), "
        f"{len(gen)} generated. Counts are exact; `count_products` only where the "
        f"product lattice fits (m ≤ cap).",
        "",
        "## Audit",
        "",
    ]
    audit = {
        "corpus instances": len(corpus),
        "construction minimum == certified optimum": int(corpus.audit_construction.sum()),
        "search-measure minimum == certified optimum": int(corpus.audit_search.sum()),
        "product-order minimum == certified optimum (m ≤ cap)": int(corpus.audit_products.sum()) if "audit_products" in corpus else 0,
        "product-order lattice computed": int(corpus.count_products.notna().sum()) if "count_products" in corpus else 0,
        "witness re-simulates to optimum": int((corpus.witness_value == corpus.optimum).sum()),
        "witness closing order constructs to optimum": int(corpus.witness_construction_optimal.sum()),
        "witness closing order optimal under the search measure": int(corpus.witness_search_optimal.sum()),
        "count_closing divisible by twin factor": int((corpus.count_closing % corpus.twin_factor == 0).sum()),
    }
    if "aut_divides" in corpus:
        audit["count_search divisible by |Aut(G)| (rows with a certificate)"] = (
            f"{int(corpus.aut_divides.sum())} of {int(corpus.aut_divides.notna().sum())}")
    if len(gen):
        audit["generated: solver optimum == construction minimum"] = int(gen.audit_solver.sum())
        audit["generated: search minimum == construction minimum"] = int(gen.audit_search.sum())
    parts.append(_md(pd.DataFrame({"check": list(audit), "value": list(audit.values())})))
    parts += ["", "## Closing orders achieving the optimum, corpus by n", "",
              _md(degeneracy_by(corpus, "n", "n"), ".3g"),
              "", "### Excluding complete graphs", "",
              _md(degeneracy_by(corpus[~corpus.complete_graph], "n", "n"), ".3g"),
              "", "## By matrix density (corpus, excluding complete graphs)", "",
              _md(degeneracy_by(corpus[~corpus.complete_graph], "density band", "density"), ".3g"),
              "", "## By collection (corpus)", "",
              _md(degeneracy_by(corpus, "collection", "collection"), ".3g"),
              "", "## Product orders achieving the optimum (corpus, m ≤ cap), by n", "",
              _md(products_by(corpus, "n", "n"), ".3g"),
              "", "### Excluding complete graphs", "",
              _md(products_by(corpus[~corpus.complete_graph], "n", "n"), ".3g"),
              "", "### By density (excluding complete graphs)", "",
              _md(products_by(corpus[~corpus.complete_graph], "density band", "density"), ".3g"),
              "", "## Imitation: optimal choices per step and the step-accuracy ceiling (corpus)", "",
              _md(imitation_by(corpus, "n", "n")),
              "", "### Excluding complete graphs", "",
              _md(imitation_by(corpus[~corpus.complete_graph], "n", "n")),
              "", "### By collection", "",
              _md(imitation_by(corpus, "collection", "collection")),
              ]
    against = imitation_against_ceiling(frame)
    if against is not None:
        parts += ["", "## §7's imitation rates against the ceiling (shared held-out instances, n ≤ 15)", "",
                  _md(against)]
    if len(gen):
        parts += ["", "## Generated G(n, m, p): closing orders, by n and p", "",
                  _md(_two_key(gen, degeneracy_by), ".3g"),
                  "", "### Generated: by m/n and p", "",
                  _md(_two_key(gen, degeneracy_by, keys=("m/n", "gen_p"), labels=("m/n", "p")), ".3g"),
                  "", "### Generated: product orders (m ≤ cap), by n and p", "",
                  _md(_two_key(gen, products_by), ".3g"),
                  "", "### Generated: imitation ceiling, by n and p", "",
                  _md(_two_key(gen, imitation_by)),
                  ]
    parts += ["", "## Examples: fewest and most optimal closing orders (corpus, non-complete)", "",
              _md(examples(frame), ".3g"), ""]
    out.write_text("\n".join(parts))


def _two_key(frame, table, keys=("n", "gen_p"), labels=("n", "p")) -> pd.DataFrame:
    frame = frame.copy()
    frame["_key"] = list(zip(frame[keys[0]], frame[keys[1]]))
    table_frame = table(frame, "_key", "key")
    table_frame.insert(0, labels[0], [k[0] for k in table_frame["key"]])
    table_frame.insert(1, labels[1], [k[1] for k in table_frame["key"]])
    return table_frame.drop(columns="key")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--max-customers", type=int, default=15)
    parser.add_argument("--max-products-exact", type=int, default=20,
                        help="product-order lattice only where m is at most this")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--generated", type=int, default=8, help="seeds per (n, m, p) cell; 0 to skip")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--solutions-dir", type=Path, default=DEFAULT_SOLUTIONS_DIR)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--tables-only", action="store_true",
                        help="rebuild the tables from an existing --csv without recomputing")
    args = parser.parse_args()

    started = time.time()
    if args.tables_only:
        frame = pd.read_csv(args.csv)
    else:
        frame = run(args.max_customers, args.max_products_exact, args.limit,
                    args.generated, args.workers, args.solutions_dir)
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(args.csv, index=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_tables(frame, args.out, time.time() - started)
    print(f"wrote {args.csv} ({len(frame)} rows) and {args.out}")


if __name__ == "__main__":
    main()
