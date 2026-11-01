"""`beta+` on paper: the analysable constructions of loop0010 item 07.

Two layouts of the MOSP graph of a random clique cover whose width per
customer has a limit that can be written down, each a proved upper bound on
the pathwidth of the instance it is computed on:

(a) **the BFS layer layout.** *Layer lemma* (deterministic, for any graph):
    list the BFS layers `L_0, L_1, ...` of a component in order; the vertex
    separation of that layout is at most `max_i (|L_i| + |L_{i+1}|) - 1`. Proof:
    a cut after the `j`-th vertex of `L_{i+1}` separates only vertices with a
    neighbour placed later, and the neighbours of `L_h` lie in `L_{h-1} .. L_{h+1}`,
    so the separated set lies in `L_i` together with the first `j` vertices of
    `L_{i+1}` (at the cut after the last vertex of `L_{i+1}` it lies in `L_{i+1}`
    alone); `j <= |L_{i+1}| - 1`. Checked by `layer_lemma_check` on random graphs
    before it was stated (`reports/scratch/beta_plus/recursion.py`).
    *Random part*: the layer fractions of the MOSP graph of `m = mu n` independent
    uniform `d`-subsets follow the two-type (customer -> pattern -> customer)
    exploration recursion

        x_{i+1} = u_i (1 - exp(-mu d (u_{i-1}^{d-1} - u_i^{d-1}))),   u_{i+1} = u_i - x_{i+1},

    (`bfs_recursion_uniform`), the analogue of `x_{i+1} = u_i (1 - e^{-c x_i})` for
    `G(n, c/n)` and equal to it at `d = 2`, `c = 2 mu`; `bfs_recursion` is the
    degree- and size-aware form (a bipartite configuration model with given
    customer-degree and pattern-size laws), needed because the generators pad;
    `padded_layers` is the fixed generator's limit exactly (its padded
    customers are leaves of uniform patterns, which the two marginals cannot
    express).
    The limit of the layer bound per customer is `max_i (x_i + x_{i+1})` along
    the orbit -- which depends on the *phase* of the exploration (where in
    `[1, rho)` the layer sizes sit when they become linear in `n`), so the
    constant is `sup` over the phase (`bfs_phase_scan`).

(b) **greedy independent sets**, with `pw <= n - alpha` (`IndependenceBound.lean`,
    `pathwidth_le_card_sub_indepNum`). In the slot picture of the cover (a
    pattern of size `s` has `s` slots; the alive patterns are those avoiding the
    independent set `I`; a vertex not in `I` and in no alive pattern meeting `I`
    is alive) the degree of an alive vertex -- its number of alive patterns --
    never changes, so the *pattern-count greedy* (take a vertex of fewest
    patterns, delete every member of its patterns) runs through phases
    `k = 0, 1, 2, ...` and its yield is the terminal time of the system

        dx_j/dt = -[j = k] - k a j x_j / T,   dy_s/dt = -k s y_s / T,
        T = sum_s s y_s,   a = sum_s s (s - 1) y_s / T,

    (`greedy_ode`, policy `pattern_count`); the *random greedy* (a uniformly
    random alive vertex) replaces `k` by the mean alive degree and `[j = k]` by
    `x_j / sum x`, and for uniform sizes `d` has the closed form
    `int_0^{t*} exp(mu d (1 - (1 - s)^{d-1})) ds = 1` (`random_greedy_uniform`),
    which at `d = 2` is `ln(1 + c) / c`, `c = 2 mu`, the classical `G(n, c/n)`
    value. The min-degree greedy of item 05 is *not* analysed: its key (the
    degree in the alive MOSP graph) reveals how many alive members each
    pattern has, a joint state the slot picture does not carry.

Both derivations are mean-field: the concentration step (Wormald's
differential-equation method) is cited, not re-proved, and no held copy of it
exists in `literature/`. Every limit is checked against simulation on item 05's
instances at `n = 100-5000`, regenerated from their seeds
(`reports/scratch/beta_plus/recursion.py`); nothing is solved.

Usage:
    python reports/scratch/beta_plus/recursion.py          # the comparison, tables and log
    python -m pytest tests/test_beta_plus.py -q
"""
from __future__ import annotations

import math
from collections.abc import Mapping

import numpy as np
from scipy.sparse import csr_matrix

Hist = Mapping[int, float]


# ----------------------------------------------------------------------------
# (a) the layer lemma
# ----------------------------------------------------------------------------


def layer_bound(layer_sizes: list[int]) -> int:
    """`max_i (|L_i| + |L_{i+1}|) - 1` over consecutive layers of one component
    (`|L_0| - 1` for a single layer)."""
    if len(layer_sizes) == 1:
        return layer_sizes[0] - 1
    return max(a + b for a, b in zip(layer_sizes, layer_sizes[1:])) - 1


def bfs_components(adj: csr_matrix, rng: np.random.Generator) -> list[list[np.ndarray]]:
    """The BFS layers of every component, from a uniformly random root and a
    random unvisited root for every further component -- the same random
    choices, in the same order, as `learning.excess_constructions.bfs_layers`,
    so the concatenation is item 05's layout; grouped by component here."""
    n = adj.shape[0]
    visited = np.zeros(n, dtype=bool)
    indptr, indices = adj.indptr, adj.indices
    comps: list[list[np.ndarray]] = []
    while not visited.all():
        root = int(rng.choice(np.flatnonzero(~visited)))
        frontier = np.array([root])
        visited[root] = True
        layers: list[np.ndarray] = []
        while len(frontier):
            layers.append(frontier)
            starts, ends = indptr[frontier], indptr[frontier + 1]
            if (ends - starts).sum() == 0:
                break
            nb = np.unique(np.concatenate([indices[s:e] for s, e in zip(starts, ends)]))
            nb = nb[~visited[nb]]
            visited[nb] = True
            frontier = nb
        comps.append(layers)
    return comps


def layer_layout_bound(comps: list[list[np.ndarray]]) -> int:
    """The layer lemma's bound for the concatenated layout: the maximum over
    components of `max_i (|L_i| + |L_{i+1}|) - 1`."""
    return max(layer_bound([len(layer) for layer in layers]) for layers in comps)


def layer_lemma_check(n_graphs: int, rng: np.random.Generator, n_max: int = 60) -> dict:
    """The lemma on random graphs of three kinds (`G(n, p)`, random clique
    covers, random trees with extra edges): returns the number checked, the
    number where the bound is tight, and raises if it is ever violated."""
    from learning.excess_constructions import mosp_adjacency, vertex_separation
    checked = tight = 0
    for g in range(n_graphs):
        n = int(rng.integers(2, n_max))
        kind = g % 3
        if kind == 0:
            p = rng.uniform(0.02, 0.5)
            dense = (rng.random((n, n)) < p)
            dense = np.triu(dense, 1)
            dense = dense | dense.T
        elif kind == 1:
            m = int(rng.integers(1, 2 * n + 1))
            d = int(rng.integers(2, min(6, n) + 1))
            mat = np.zeros((n, m), dtype=np.int8)
            for j in range(m):
                mat[rng.choice(n, size=d, replace=False), j] = 1
            dense = (mosp_adjacency(mat).toarray() != 0)
        else:
            dense = np.zeros((n, n), dtype=bool)
            for v in range(1, n):
                u = int(rng.integers(0, v))
                dense[u, v] = dense[v, u] = True
            for _ in range(int(rng.integers(0, n))):
                u, v = rng.integers(0, n, size=2)
                if u != v:
                    dense[u, v] = dense[v, u] = True
        adj = csr_matrix(dense.astype(np.int8))
        comps = bfs_components(adj, rng)
        order = np.concatenate([layer for layers in comps for layer in layers])
        vs = vertex_separation(adj, order)
        bound = layer_layout_bound(comps)
        if vs > bound:
            raise AssertionError(f"layer lemma violated: vs {vs} > bound {bound} on graph {g}")
        checked += 1
        tight += vs == bound
    return {"checked": checked, "tight": tight}


# ----------------------------------------------------------------------------
# (a) the exploration recursion
# ----------------------------------------------------------------------------


def bfs_recursion_uniform(mu: float, d: int, u_prev: float, u_cur: float, tol: float = 1e-12,
                          max_steps: int = 100000) -> list[float]:
    """The layer fractions `x_{i+1}, x_{i+2}, ...` of the uniform model from the
    state `(u_{i-1}, u_i)` (fractions of customers unreached before and after
    the current layer), until a layer is below `tol` or the steps run out."""
    xs: list[float] = []
    for _ in range(max_steps):
        lam = mu * d * (u_prev ** (d - 1) - u_cur ** (d - 1))
        x = u_cur * (1.0 - math.exp(-lam))
        xs.append(x)
        u_prev, u_cur = u_cur, u_cur - x
        if x < tol:
            break
    return xs


def gnp_recursion(c: float, u_cur: float, x_cur: float, tol: float = 1e-12, max_steps: int = 100000) -> list[float]:
    """`x_{i+1} = u_i (1 - e^{-c x_i})`, `u_{i+1} = u_i - x_{i+1}`, for `G(n, c/n)`."""
    xs: list[float] = []
    for _ in range(max_steps):
        x = u_cur * (1.0 - math.exp(-c * x_cur))
        xs.append(x)
        u_cur, x_cur = u_cur - x, x
        if x < tol:
            break
    return xs


def bfs_recursion(deg: Hist, sizes: Hist, slots_layer: float, deg_unreached: Hist | None = None,
                  sizes_unrevealed: Hist | None = None, tol: float = 1e-12, max_steps: int = 100000) -> list[float]:
    """The degree- and size-aware recursion. State at the current layer `L_i`:
    `deg_unreached[k]` the unreached customers of degree `k` (per `n`; defaults
    to `deg`, the whole population), `sizes_unrevealed[s]` the patterns of size
    `s` avoiding `R_{i-1}` (per `n`; defaults to `sizes`), `slots_layer` the
    slots of `L_i`'s customers in unrevealed patterns (per `n`). Each step: an
    unrevealed pattern meets `L_i` with probability `1 - (1 - l / T)^s`; a slot
    of an unreached customer lies in such a pattern with probability
    `rho = sum_s (s nu_s / T) (1 - (1 - l / T)^{s-1})`; a degree-`k` customer is
    reached with probability `1 - (1 - rho)^k`. Returns `x_{i+1}, x_{i+2}, ...`."""
    u = {int(k): float(v) for k, v in (deg_unreached if deg_unreached is not None else deg).items() if v > 0}
    nu = {int(s): float(v) for s, v in (sizes_unrevealed if sizes_unrevealed is not None else sizes).items() if v > 0}
    ell = float(slots_layer)
    xs: list[float] = []
    for _ in range(max_steps):
        T = sum(s * v for s, v in nu.items())
        if T <= 0 or ell <= 0:
            xs.append(0.0)
            break
        q = max(0.0, 1.0 - ell / T)
        rho = sum(s * v / T * (1.0 - q ** (s - 1)) for s, v in nu.items())
        rho = min(max(rho, 0.0), 1.0)
        slots_before = sum(k * v for k, v in u.items())
        u_new = {k: v * (1.0 - rho) ** k for k, v in u.items()}
        x = sum(u[k] - u_new[k] for k in u)
        slots_after = sum(k * v for k, v in u_new.items())
        ell = (1.0 - rho) * slots_before - slots_after
        nu = {s: v * q ** s for s, v in nu.items()}
        u = u_new
        xs.append(x)
        if x < tol:
            break
    return xs


def poisson_hist(mean: float, cutoff: float = 1e-14) -> dict[int, float]:
    """`Poisson(mean)` as a `{k: probability}` mapping, truncated at `cutoff`."""
    out, k, p = {}, 0, math.exp(-mean)
    while True:
        if p > cutoff:
            out[k] = p
        k += 1
        p *= mean / k
        if k > mean and p < cutoff:
            break
    return out


def growth_factor(deg: Hist, sizes: Hist) -> float:
    """`rho`: the mean number of customers in layer `i + 1` per customer of
    layer `i` while the layers are small -- the branching factor of the
    two-type process, `(E k(k-1) / E k) (E s(s-1) / E s)`; `mu d (d - 1)` for
    Poisson degrees and uniform size `d`."""
    ek = sum(k * v for k, v in deg.items())
    ekk = sum(k * (k - 1) * v for k, v in deg.items())
    es = sum(s * v for s, v in sizes.items())
    ess = sum(s * (s - 1) * v for s, v in sizes.items())
    return (ekk / ek) * (ess / es)


def layer_max(xs: list[float]) -> float:
    """`max_i (x_i + x_{i+1})` over consecutive entries (`x_0` alone if one)."""
    if len(xs) == 1:
        return xs[0]
    return max(a + b for a, b in zip(xs, xs[1:]))


def bfs_phase_scan(deg: Hist, sizes: Hist, phases: int = 48, eps: float = 1e-7) -> dict:
    """The limit of the layer bound per customer over one period of the phase:
    the recursion is started from a seed layer of `eps rho^theta` customers
    (their slots in unrevealed patterns, nothing yet reached), `theta` on a grid
    over `[0, 1)`; returns `sup`, `inf`, `mean` of `max_i (x_i + x_{i+1})` and
    the orbit's values. `eps` is small enough that one more period changes
    nothing at `1e-6`."""
    rho = growth_factor(deg, sizes)
    ek = sum(k * v for k, v in deg.items())
    values = []
    for theta in np.linspace(0.0, 1.0, phases, endpoint=False):
        seed = eps * rho ** theta
        deg_un = {k: v * (1.0 - seed) for k, v in deg.items()}
        xs = [seed] + bfs_recursion(deg, sizes, seed * ek, deg_unreached=deg_un, sizes_unrevealed=sizes)
        values.append(layer_max(xs))
    values = np.array(values)
    return {"sup": float(values.max()), "inf": float(values.min()), "mean": float(values.mean()),
            "rho": float(rho), "values": values}


def padded_layers(mu: float, d: int, eps: float) -> list[float]:
    """The layer fractions of the fixed generator's limit: the uniform model
    on all `n` customers (whose isolated customers, a fraction `e^{-mu d}`, are
    never reached) with every isolated customer re-attached as a *leaf* to one
    uniform pattern, so a pattern carries `e^{-mu d} / mu` leaves on average
    and a leaf enters the layer after the one that reveals its pattern:
    `x_{i+1} = x_{i+1}^{uniform} + e^{-mu d} (u_{i-1}^d - u_i^d)`. The leaves
    never propagate, so the growth factor stays `mu d (d - 1)`; the marginal
    configuration model of `bfs_recursion` would treat them as ordinary
    degree-1 customers and overstate it (1.47 against 1 at `(2, 1/2)`)."""
    xs = [eps] + bfs_recursion_uniform(mu, d, 1.0, 1.0 - eps)
    us = [1.0, 1.0 - eps]
    for x in xs[1:]:
        us.append(us[-1] - x)
    leaf = math.exp(-mu * d)
    out = [eps]
    for i in range(1, len(xs)):
        # u_{i-2} = us[i-1] is the unreached fraction before layer i-1, u_{i-1} = us[i] after it
        out.append(xs[i] + leaf * (us[i - 1] ** d - us[i] ** d))
    return out


def padded_phase_scan(mu: float, d: int, phases: int = 48, eps: float = 1e-7) -> dict:
    """`bfs_phase_scan` for the fixed generator's limit (`padded_layers`)."""
    rho = mu * d * (d - 1)
    values = np.array([layer_max(padded_layers(mu, d, eps * rho ** theta))
                       for theta in np.linspace(0.0, 1.0, phases, endpoint=False)])
    return {"sup": float(values.max()), "inf": float(values.min()), "mean": float(values.mean()), "rho": rho, "values": values}


def bfs_state(matrix: np.ndarray, comps: list[list[np.ndarray]], min_layer: int) -> dict | None:
    """The exploration state of the largest component at its first layer of
    size `>= min_layer`, from the instance: the unreached customers' degree
    histogram, the unrevealed patterns' size histogram, the layer's slots in
    unrevealed patterns (all per `n`), the layers observed so far (per `n`) and
    the ones after (per `n`). None if no layer is that large."""
    a = np.asarray(matrix) != 0
    n = a.shape[0]
    layers = max(comps, key=lambda ls: sum(len(x) for x in ls))
    sizes = [len(x) for x in layers]
    i0 = next((i for i, s in enumerate(sizes) if s >= min_layer), None)
    if i0 is None:
        return None
    reached_before = np.zeros(n, dtype=bool)
    for layer in layers[:i0]:
        reached_before[layer] = True
    current = np.zeros(n, dtype=bool)
    current[layers[i0]] = True
    unreached = ~reached_before & ~current
    unrevealed = ~a[reached_before].any(axis=0)          # patterns avoiding R_{i0-1}
    deg = a.sum(axis=1)
    deg_un = {int(k): int(c) / n for k, c in zip(*np.unique(deg[unreached], return_counts=True))}
    size_un = {int(s): int(c) / n for s, c in zip(*np.unique(a[:, unrevealed].sum(axis=0), return_counts=True))}
    ell = int(a[np.ix_(current, unrevealed)].sum()) / n
    return {"i0": i0, "deg_unreached": deg_un, "sizes_unrevealed": size_un, "slots_layer": ell,
            "observed_before": [s / n for s in sizes[: i0 + 1]], "observed_after": [s / n for s in sizes[i0 + 1:]],
            "component_fraction": sum(sizes) / n}


# ----------------------------------------------------------------------------
# (b) greedy independent sets
# ----------------------------------------------------------------------------


def random_greedy_uniform(mu: float, d: int) -> float:
    """`alpha / n` of the random greedy on the uniform model: the `t*` with
    `int_0^{t*} exp(mu d (1 - (1 - s)^{d-1})) ds = 1`, by bisection on the
    integral (Simpson, 20,000 panels)."""
    def integral(t: float) -> float:
        if t <= 0:
            return 0.0
        k = 20000
        s = np.linspace(0.0, t, k + 1)
        f = np.exp(mu * d * (1.0 - (1.0 - s) ** (d - 1)))
        w = np.ones(k + 1)
        w[1:-1:2], w[2:-1:2] = 4.0, 2.0
        return float((t / k / 3.0) * (w * f).sum())
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if integral(mid) < 1.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def greedy_ode(deg: Hist, sizes: Hist, policy: str = "pattern_count", dt: float = 1e-4) -> dict:
    """`alpha / n` of the greedy in the slot picture, by Euler steps of `dt`
    (first order; the phase ends are located by linear interpolation).
    `deg[k]` customers of degree `k` per `n` (sums to 1), `sizes[s]` patterns of
    size `s` per `n`. Policy `pattern_count`: phases `k = 0, 1, ...`; `random`:
    a uniform alive vertex. Returns the yield and the per-phase yields."""
    x = {int(k): float(v) for k, v in deg.items() if v > 0}
    y = {int(s): float(v) for s, v in sizes.items() if v > 0}
    ks = sorted(x)
    t = 0.0
    phase_yield: dict[int, float] = {}
    if policy == "pattern_count":
        for k in ks:
            t_phase = 0.0
            while x[k] > 0:
                T = sum(s * v for s, v in y.items())
                X = sum(x.values())
                if X <= 1e-15:
                    break
                if k == 0 or T <= 0:
                    t_phase += x[k]; t += x[k]; x[k] = 0.0
                    break
                a = sum(s * (s - 1) * v for s, v in y.items()) / T
                step = min(dt, x[k])               # do not overshoot the selection term
                rate = 1.0 + k * a * k * x[k] / T
                if x[k] - step * rate <= 0:
                    step = x[k] / rate
                for j in x:
                    x[j] -= step * ((j == k) + k * a * j * x[j] / T)
                    x[j] = max(x[j], 0.0)
                for s in y:
                    y[s] *= max(0.0, 1.0 - step * k * s / T)
                t += step
                t_phase += step
            phase_yield[k] = t_phase
        return {"alpha": t, "phases": phase_yield}
    if policy == "random":
        while True:
            X = sum(x.values())
            if X <= 1e-12:
                break
            T = sum(s * v for s, v in y.items())
            kbar = sum(j * v for j, v in x.items()) / X
            a = sum(s * (s - 1) * v for s, v in y.items()) / T if T > 0 else 0.0
            step = min(dt, X)
            for j in x:
                drift = x[j] / X + (kbar * a * j * x[j] / T if T > 0 else 0.0)
                x[j] = max(0.0, x[j] - step * drift)
            if T > 0:
                for s in y:
                    y[s] *= max(0.0, 1.0 - step * kbar * s / T)
            t += step
        return {"alpha": t, "phases": {}}
    raise ValueError(policy)


def _bipartite_lists(matrix: np.ndarray) -> tuple[list[np.ndarray], list[np.ndarray]]:
    a = np.asarray(matrix) != 0
    rows = [np.flatnonzero(a[i]) for i in range(a.shape[0])]
    cols = [np.flatnonzero(a[:, j]) for j in range(a.shape[1])]
    return rows, cols


def greedy_simulation(matrix: np.ndarray, policy: str, rng: np.random.Generator) -> tuple[int, np.ndarray]:
    """The greedy on one instance, in the slot picture: `pattern_count` scans
    the customers by number of patterns (ties uniformly at random), `random`
    in uniform random order, `min_degree` by minimum remaining degree in the
    MOSP graph (item 05's `greedy_independent_set`, repeated here for the
    witness); a customer is taken if alive, and taking it kills every member
    of every one of its patterns. Returns `alpha` and the independent set."""
    a = np.asarray(matrix) != 0
    n = a.shape[0]
    rows, cols = _bipartite_lists(a)
    if policy == "min_degree":
        from learning.excess_constructions import greedy_independent_set, mosp_adjacency
        return greedy_independent_set(mosp_adjacency(a.astype(np.int8))), np.array([], dtype=int)
    deg = a.sum(axis=1)
    if policy == "pattern_count":
        order = np.lexsort((rng.random(n), deg))
    elif policy == "random":
        order = rng.permutation(n)
    else:
        raise ValueError(policy)
    alive = np.ones(n, dtype=bool)
    chosen = []
    for v in order:
        if not alive[v]:
            continue
        chosen.append(int(v))
        alive[v] = False
        for j in rows[v]:
            alive[cols[j]] = False
    return len(chosen), np.array(chosen)


def is_independent(matrix: np.ndarray, vertices: np.ndarray) -> bool:
    a = np.asarray(matrix) != 0
    return bool((a[vertices].sum(axis=0) <= 1).all())


def degree_and_size_histograms(matrix: np.ndarray) -> tuple[dict[int, float], dict[int, float]]:
    """`(deg, sizes)` per `n`: the customers' pattern counts and the patterns' sizes."""
    a = np.asarray(matrix) != 0
    n = a.shape[0]
    deg = {int(k): int(c) / n for k, c in zip(*np.unique(a.sum(axis=1), return_counts=True))}
    sizes = {int(s): int(c) / n for s, c in zip(*np.unique(a.sum(axis=0), return_counts=True))}
    return deg, sizes


def uniform_model_histograms(mu: float, d: int) -> tuple[dict[int, float], dict[int, float]]:
    """The limiting laws of the uniform model without padding: `Poisson(mu d)`
    degrees and `mu` patterns of size `d` per customer."""
    return poisson_hist(mu * d), {d: mu}


def fixed_generator_histograms(mu: float, d: int) -> tuple[dict[int, float], dict[int, float]]:
    """The limiting laws of `generate_structured_instance`: `Poisson(mu d)`
    degrees with the mass at 0 moved to 1 (the padding), and pattern sizes
    `d + Poisson(e^{-mu d} / mu)` (each padded customer joins one uniform pattern)."""
    deg = poisson_hist(mu * d)
    deg[1] = deg.get(1, 0.0) + deg.pop(0, 0.0)
    extra = poisson_hist(math.exp(-mu * d) / mu)
    sizes = {d + j: mu * p for j, p in extra.items()}
    return deg, sizes
