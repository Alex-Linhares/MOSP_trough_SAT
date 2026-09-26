"""Set-valued imitation: does a policy learn more than the rule when the target
is the *set* of optimal moves? (plan 2 §2.8, loop0003 item 10)

Question. §7 of `reports/ml_nature.md` found the two-key rule -- *close the
customer that opens the fewest new stacks; on ties, the one with the most
unclosed neighbours* -- beating the LightGBM ranker of `learning.policy` on
held-out construction value (MAE 0.348 / exact 80.7% against 0.519 / 75.0%),
and §8 found that the ranker's imitation target was ~90% arbitrary: the corpus
witnesses are one member each of a set of 10^5-10^10 optimal closing orders,
so a step "agreeing with the witness" measures reproduction of the solver's
tie-breaks, not optimality. This module gives imitation its one honest chance:
the label of a candidate move is whether it *keeps the best achievable
construction value*, computed exactly on the subset lattice, and a step is
right when it lands in that set.

Method.

  * **The lattice, vectorised** (`Lattice`). `learning.degeneracy.closing_weights`
    walks `2^a * a` states in Python and reaches n = 15. Here every array is
    over all `2^a` closed-customer sets at once: `opened[S]`, `made[S]`,
    `done[S]` by one pass per customer; the construction cost `w[S, c]` -- the
    peak of open stacks while `c`'s unproduced products are made in index
    order, exactly `mosp.verify.count_open_stacks` on the constructed product
    order -- by one pass per (customer, product, holder) triple; and the
    bottleneck-to-go `h[S] = min over completions of the max cost`, layer by
    layer downward. It reaches n = 20 (2^20 states, ~1-3 s, ~60 MB) for all
    4,122 certified corpus instances with n <= 20 -- the 1,298 at n = 20 the
    plan names and everything below. `h[0]` is the optimum, which is a free
    audit against the certified value on every instance.
  * **Labels.** From a state `S` reached with running peak `P`, closing `c`
    is *good* iff `max(w[S, c], h[S | c]) <= max(h[S], P)`: it does not worsen
    the best value the construction can still reach. At `P <= h[S] = optimum`
    this is exactly `learning.degeneracy.optimal_choices`; off the optimal
    paths it is the natural extension, so the rule's and MCN's own
    trajectories can be labelled too. States labelled per instance: every
    prefix of the witness's induced closing order, of the two-key rule's
    order, of MCN's order, and of one seeded rollout choosing uniformly
    among optimal moves; duplicates dropped; steps with one candidate
    skipped.
  * **Features.** `learning.policy.step_features` (8) and `patterns`, plus the
    two-key rule's keys relative to the step (`rel_newly_opened`,
    `rel_remaining_degree`), the rule's own rank of the candidate (`rule_rank`,
    0 for the rule's pick), the number of candidates and the running peak.
    With `rule_rank` a feature and the rule's key breaking score ties, the
    constant model *is* the rule: the learned model can only add to it or
    fall below it by learning something false.
  * **Models.** LightGBM binary on the good/bad rows (`set-binary`) and
    LambdaRank with one query per step and relevance = good (`set-rank`),
    each used greedily; the old ranker (`learning.policy._fit` on the
    training groups' witnesses at every size, as in §7); MCN; the rule.
    Every split is five folds by **file ∪ MOSP-graph isomorphism class**
    (`learning.fingerprint.union_groups`), groups assigned largest first to
    the smallest fold. Set-valued models are fitted on the n <= 20 training
    rows only (labels exist only there) and scored held out at every size.
  * **Scores.** Construction value over the optimum (MAE, exact, worst),
    held out, at n <= 20 (the training regime) and on the whole corpus
    (transfer to 21-134); step accuracy *under the correct objective*: the
    fraction of a policy's own steps that were good, along its own
    trajectory (`own_good`), and along the witness (`wit_good`), at n <= 20.
  * **The ceiling at 50-125** (`ceiling` stage). Along every witness with
    n >= 50, at every step, a lower bound on the number of optimal choices:
    an alternative `c` is confirmed if (a) the witness's own suffix with `c`
    moved to the front still constructs to the optimum -- the search
    "restricted to the witness's own prefixes" -- or, failing that, (b) a
    node-bounded restricted DFS (Chu & Stuckey's `ub_MOSP` shape: branch on
    already-open customers, cheapest first) from `S ∪ {c}` finds a completion
    within the optimum under the exact construction cost. Confirmed counts
    are lower bounds, so `mean(1 / confirmed)` is an **upper bound on the
    step-accuracy ceiling** of §8 at these sizes. The same bounded procedure
    is run on the 16-20 instances and compared with the exact counts to
    calibrate how much it misses.

Not a bound, not a solver change: nothing here touches `_lower_bound`, no
default changes, nothing is written to `solutions/`.

Run (all stages, ~25 min on 8 workers):
    python -m learning.set_imitation --workers 8
    python -m learning.set_imitation --stage lattice --workers 8    # rows + exact choices, n <= 20
    python -m learning.set_imitation --stage train                  # folds, models, held-out values
    python -m learning.set_imitation --stage ceiling --workers 8    # bounded choices at >= 50, calibration 16-20
    python -m learning.set_imitation --stage tables                 # reports/set_imitation_tables.md

Writes `learning/data/set_imitation/` (rows, git-ignored, regenerable),
`learning/data/ensemble/set_imitation_{lattice,eval,ceiling,calibration}.csv[.gz]`
(committed) and `reports/set_imitation_tables.md`.

The pool uses `spawn`: forking after LightGBM has run deadlocks libgomp.
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing
import random
import time
from collections import Counter
from pathlib import Path
from typing import Callable, Sequence

import numpy as np
import pandas as pd

from learning.distil import (
    COL,
    COLUMNS,
    HYPOTHESES,
    HYPOTHESIS_RULE,
    MCN_KEY,
    candidate_matrix,
    lex_key,
    pick_min,
)
from learning.policy import STEP_FEATURE_NAMES, _corpus, _fit
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.heuristics import (
    _customer_order_from_products,
    _neighbour_masks,
    product_order_from_customers,
)

DATA_DIR = Path("learning/data/set_imitation")
ENSEMBLE_DIR = Path("learning/data/ensemble")
LATTICE_CSV = ENSEMBLE_DIR / "set_imitation_lattice.csv"
EVAL_CSV = ENSEMBLE_DIR / "set_imitation_eval.csv.gz"
CEILING_CSV = ENSEMBLE_DIR / "set_imitation_ceiling.csv"
CALIB_CSV = ENSEMBLE_DIR / "set_imitation_calibration.csv"
ROWS_NPZ = DATA_DIR / "rows.npz"
MODELS_JSON = DATA_DIR / "models.json"
TABLES_OUT = Path("reports/set_imitation_tables.md")
CANONICAL_CSV = Path("learning/data/canonical.csv")

MAX_LATTICE = 20
RULE = HYPOTHESES[HYPOTHESIS_RULE]              # min newly_opened, max remaining_degree
EXTRA_NAMES = ["rel_newly_opened", "rel_remaining_degree", "rule_rank",
               "n_candidates", "peak_so_far"]
FEATURE_NAMES = STEP_FEATURE_NAMES + ["patterns"] + EXTRA_NAMES
SIZE_BANDS = ((9, 15), (16, 20), (21, 40), (41, 75), (76, 134))
STRATEGIES = ["mcn", "rule", "old-ranker", "set-binary", "set-rank"]


# --------------------------------------------------------------------------
# Bit helpers
# --------------------------------------------------------------------------

def _bits(mask: int):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


_M1 = np.uint32(0x55555555)
_M2 = np.uint32(0x33333333)
_M4 = np.uint32(0x0F0F0F0F)
_H01 = np.uint32(0x01010101)


def popcount32(x: np.ndarray) -> np.ndarray:
    """Population count of a uint32 array (SWAR; numpy < 2 has no bitwise_count)."""
    x = x.astype(np.uint32, copy=True)
    x -= (x >> np.uint32(1)) & _M1
    x = (x & _M2) + ((x >> np.uint32(2)) & _M2)
    x = (x + (x >> np.uint32(4))) & _M4
    with np.errstate(over="ignore"):
        return ((x * _H01) >> np.uint32(24)).astype(np.int8)


class Masks:
    """Bitmask view of an instance over its active customers and products.

    Customers keep their original indices (bit `c` is customer `c`), so
    orders read the same as everywhere else in the repository; products with
    no customer are simply never produced.
    """

    def __init__(self, instance: MOSPInstance):
        matrix = np.asarray(instance.matrix)
        self.n = instance.n_customers
        self.m = instance.n_patterns
        self.prod = [0] * self.n
        self.holders = [0] * self.m
        for c in range(self.n):
            for p in np.flatnonzero(matrix[c]):
                self.prod[c] |= 1 << int(p)
                self.holders[int(p)] |= 1 << c
        self.neigh = [0] * self.n
        for p in range(self.m):
            for c in _bits(self.holders[p]):
                self.neigh[c] |= self.holders[p]
        self.active = [c for c in range(self.n) if self.prod[c]]
        self.full = sum(1 << c for c in self.active)

    def block_cost(self, opened: int, made: int, done: int, c: int
                   ) -> tuple[int, int, int, int]:
        """Close `c` from a state: (peak while its products are made, opened',
        made', done'). Exactly `learning.degeneracy.closing_weights`'s
        construction cost, one state at a time."""
        rem = self.prod[c] & ~made
        opened2 = opened | self.neigh[c]
        if rem == 0:
            return 0, opened2, made, done
        started, dcur, T2, peak = opened, done, made, 0
        holders, prod = self.holders, self.prod
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
        return peak, started, T2, dcur

    def order_value(self, order: Sequence[int], cap: int | None = None) -> int:
        """Construction value of a closing order (max block cost); stops early
        past `cap` and returns `cap + 1`."""
        opened = made = done = 0
        peak = 0
        for c in order:
            cost, opened, made, done = self.block_cost(opened, made, done, c)
            if cost > peak:
                peak = cost
                if cap is not None and peak > cap:
                    return cap + 1
        return peak


# --------------------------------------------------------------------------
# The vectorised lattice (n <= 20)
# --------------------------------------------------------------------------

class Lattice:
    """Construction-cost lattice over all closed sets of the active customers.

    Attributes (all over `2^a` compact states; `pos[c]` is customer `c`'s bit):
      w[S, i]  int8   cost of closing compact customer `i` from `S` (0 if i ∈ S)
      h[S]     int8   bottleneck-to-go: min over completions of the max cost
    `h[0]` is the optimum of the instance.
    """

    def __init__(self, instance: MOSPInstance):
        mk = Masks(instance)
        self.masks = mk
        self.customers = mk.active                  # compact index -> customer
        self.pos = {c: i for i, c in enumerate(self.customers)}
        a = len(self.customers)
        if a > MAX_LATTICE:
            raise ValueError(f"{a} active customers exceeds the lattice limit {MAX_LATTICE}")
        self.a = a
        size = 1 << a
        # compact masks over customers (uint32) and products (uint64)
        cprod = [mk.prod[c] for c in self.customers]
        cneigh = [self._compact(mk.neigh[c]) for c in self.customers]
        cholders = [self._compact(mk.holders[p]) for p in range(mk.m)]
        S = np.arange(size, dtype=np.uint32)
        opened = np.zeros(size, dtype=np.uint32)
        made = np.zeros(size, dtype=np.uint64)
        for i in range(a):
            has = ((S >> np.uint32(i)) & np.uint32(1)).astype(bool)
            opened[has] |= np.uint32(cneigh[i])
            made[has] |= np.uint64(cprod[i])
        done = np.zeros(size, dtype=np.uint32)
        for i in range(a):
            pm = np.uint64(cprod[i])
            done[(made & pm) == pm] |= np.uint32(1 << i)
        popc = popcount32(S)
        layers = [np.flatnonzero(popc == j).astype(np.uint32) for j in range(a + 1)]

        w = np.zeros((size, a), dtype=np.int8)
        for i in range(a):
            started = opened.copy()
            dcur = done.copy()
            T2 = made.copy()
            peak = np.zeros(size, dtype=np.int8)
            for p in _bits(cprod[i]):
                bitp = np.uint64(1 << p)
                idx = np.flatnonzero((T2 & bitp) == 0)
                if idx.size == 0:
                    continue
                T2[idx] |= bitp
                started[idx] |= np.uint32(cholders[p])
                cnt = popcount32(started[idx] & ~dcur[idx])
                peak[idx] = np.maximum(peak[idx], cnt)
                for d in _bits(cholders[p]):
                    pd_ = np.uint64(cprod[d])
                    fin = (T2[idx] & pd_) == pd_
                    dcur[idx[fin]] |= np.uint32(1 << d)
            # only meaningful where i ∉ S
            has = ((S >> np.uint32(i)) & np.uint32(1)).astype(bool)
            peak[has] = 0
            w[:, i] = peak

        h = np.full(size, 127, dtype=np.int8)
        h[size - 1] = 0
        for j in range(a - 1, -1, -1):
            idx = layers[j]
            best = np.full(idx.size, 127, dtype=np.int8)
            for i in range(a):
                bit = np.uint32(1 << i)
                free = (idx & bit) == 0
                sel = idx[free]
                cand = np.maximum(w[sel, i], h[sel | bit])
                best[free] = np.minimum(best[free], cand)
            h[idx] = best
        self.w = w
        self.h = h
        self.optimum = int(h[0])

    def _compact(self, mask: int) -> int:
        out = 0
        for c in _bits(mask):
            if c in self.pos:
                out |= 1 << self.pos[c]
        return out

    def state(self, closed_customers: Sequence[int]) -> int:
        return sum(1 << self.pos[c] for c in closed_customers if c in self.pos)

    def good_moves(self, S: int, peak: int) -> dict[int, bool]:
        """Customer -> whether closing it keeps `max(peak, h[S])` reachable."""
        target = max(int(self.h[S]), peak)
        out = {}
        for i, c in enumerate(self.customers):
            if (S >> i) & 1:
                continue
            val = max(int(self.w[S, i]), int(self.h[S | (1 << i)]))
            out[c] = val <= target
        return out

    def optimal_choices(self, S: int) -> list[int]:
        """Customers that begin an optimal completion from `S` (budget = optimum)."""
        k = self.optimum
        return [c for i, c in enumerate(self.customers)
                if not (S >> i) & 1 and self.w[S, i] <= k and self.h[S | (1 << i)] <= k]


# --------------------------------------------------------------------------
# Features, keys and greedy construction
# --------------------------------------------------------------------------

_RULE_KEY = lex_key(RULE)
_MCN_KEY_FN = lex_key([])
_NEW, _DEG = COL["newly_opened"], COL["remaining_degree"]


def extended_matrix(X: np.ndarray, peak_so_far: int) -> np.ndarray:
    """Append the rule-relative columns to a `candidate_matrix` block."""
    keys = _RULE_KEY(X)
    order = np.lexsort(keys.T[::-1])
    rank = np.empty(len(X), dtype=np.float64)
    rank[order] = np.arange(len(X), dtype=np.float64)
    extra = np.column_stack([
        X[:, _NEW] - X[:, _NEW].min(),
        X[:, _DEG] - X[:, _DEG].max(),
        rank,
        np.full(len(X), float(len(X))),
        np.full(len(X), float(peak_so_far)),
    ])
    return np.hstack([X[:, :len(COLUMNS) - 1], extra])   # drop `index`


KeyFn = Callable[[np.ndarray, int], np.ndarray]
"""(candidate_matrix block, peak_so_far) -> key columns; lexicographic minimum closes."""


def rule_key(X: np.ndarray, peak: int) -> np.ndarray:
    return _RULE_KEY(X)


def mcn_key(X: np.ndarray, peak: int) -> np.ndarray:
    return _MCN_KEY_FN(X)


def score_key_rule_ties(scores_of: Callable[[np.ndarray], np.ndarray]) -> KeyFn:
    """Higher score first; ties by the rule's key, then MCN's."""
    def key(X: np.ndarray, peak: int) -> np.ndarray:
        s = np.asarray(scores_of(extended_matrix(X, peak)), dtype=np.float64)
        return np.hstack([-s[:, None], _RULE_KEY(X)])
    return key


def old_ranker_key(booster) -> KeyFn:
    """§7's `lgbm` row: the old ranker's score, ties by index."""
    def key(X: np.ndarray, peak: int) -> np.ndarray:
        s = booster.predict(X[:, :len(STEP_FEATURE_NAMES)].astype(np.float32),
                            raw_score=True, num_threads=1)
        return np.hstack([-np.asarray(s)[:, None], X[:, [COL["index"]]]])
    return key


def greedy_order(instance: MOSPInstance, key: KeyFn, masks: Masks | None = None
                 ) -> list[int]:
    """Close, at every step, the candidate with the smallest key; the running
    construction peak is tracked exactly and offered to the key."""
    mk = masks or Masks(instance)
    nb = _neighbour_masks(instance)
    closed = opened = made = done = 0
    peak = 0
    remaining = list(mk.active)
    order: list[int] = []
    while remaining:
        X = candidate_matrix(nb, mk.n, mk.prod, closed, opened, made, remaining)
        pick = remaining[pick_min(key(X, peak))]
        cost, opened, made, done = mk.block_cost(opened, made, done, pick)
        peak = max(peak, cost)
        closed |= 1 << pick
        order.append(pick)
        remaining.remove(pick)
    return order


def construction_value(instance: MOSPInstance, order: Sequence[int]) -> int:
    return max_open_stacks(instance, product_order_from_customers(instance, order))


# --------------------------------------------------------------------------
# Stage 1: the lattice -- rows with set-valued labels, exact choices
# --------------------------------------------------------------------------

def label_states(instance: MOSPInstance, lat: Lattice, orders: dict[str, Sequence[int]],
                 rollouts: int = 1, seed: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Rows (features, good?, step id) over the prefixes of the given orders
    and `rollouts` seeded uniform-optimal rollouts; duplicate states dropped."""
    mk = lat.masks
    nb = _neighbour_masks(instance)
    rng = random.Random(seed)
    trajectories = dict(orders)
    for r in range(rollouts):
        S = 0
        order = []
        for _ in range(lat.a):
            choices = lat.optimal_choices(S)
            c = rng.choice(choices)
            order.append(c)
            S |= 1 << lat.pos[c]
        trajectories[f"rollout{r}"] = order
    seen: set[int] = set()
    X_rows, y_rows, step_rows = [], [], []
    step = 0
    stats = Counter()
    for name, order in trajectories.items():
        closed = opened = made = done = 0
        peak = 0
        for c in order:
            if c not in lat.pos or (closed >> c) & 1:
                continue
            S = lat.state(_bits(closed))
            remaining = [d for d in mk.active if not (closed >> d) & 1]
            if S not in seen and len(remaining) > 1:
                seen.add(S)
                good = lat.good_moves(S, peak)
                X = extended_matrix(candidate_matrix(nb, mk.n, mk.prod, closed, opened, made, remaining), peak)
                y = np.array([good[d] for d in remaining], dtype=np.int8)
                X_rows.append(X.astype(np.float32))
                y_rows.append(y)
                step_rows.append(np.full(len(remaining), step, dtype=np.int32))
                step += 1
                stats["states"] += 1
                stats["good"] += int(y.sum())
                stats["cands"] += len(remaining)
                # is the rule's pick good here?
                stats["rule_good"] += int(y[int(np.argmin(X[:, FEATURE_NAMES.index("rule_rank")]))])
            cost, opened, made, done = mk.block_cost(opened, made, done, c)
            peak = max(peak, cost)
            closed |= 1 << c
    if not X_rows:
        return (np.zeros((0, len(FEATURE_NAMES)), np.float32), np.zeros(0, np.int8),
                np.zeros(0, np.int32), dict(stats))
    return np.vstack(X_rows), np.concatenate(y_rows), np.concatenate(step_rows), dict(stats)


def witness_choice_counts(lat: Lattice, closing: Sequence[int]) -> tuple[list[int], bool]:
    """Exact optimal-choice count at every step of a closing order, and whether
    the order is itself optimal (every step within budget and completable)."""
    S = 0
    counts = []
    optimal = True
    k = lat.optimum
    for c in closing:
        if c not in lat.pos or (S >> lat.pos[c]) & 1:
            continue
        counts.append(len(lat.optimal_choices(S)))
        i = lat.pos[c]
        if lat.w[S, i] > k or lat.h[S | (1 << i)] > k:
            optimal = False
        S |= 1 << i
    return counts, optimal and S == (1 << lat.a) - 1


def _lattice_job(task):
    file, instance, optimum, ordering, seed = task
    started = time.time()
    lat = Lattice(instance)
    witness = _customer_order_from_products(instance, ordering)
    mk = lat.masks
    orders = {
        "witness": witness,
        "rule": greedy_order(instance, rule_key, mk),
        "mcn": greedy_order(instance, mcn_key, mk),
    }
    X, y, steps, stats = label_states(instance, lat, orders, rollouts=1, seed=seed)
    counts, wit_opt = witness_choice_counts(lat, witness)
    row = {
        "source_file": file, "instance_name": instance.name,
        "n_customers": instance.n_customers, "n_patterns": instance.n_patterns,
        "n_active": lat.a, "optimum": optimum, "lattice_optimum": lat.optimum,
        "audit": lat.optimum == optimum,
        "witness_construction_value": construction_value(instance, witness),
        "witness_optimal": wit_opt,
        "witness_steps": len(counts),
        "witness_mean_choices": float(np.mean(counts)) if counts else float("nan"),
        "witness_ceiling": float(np.mean([1 / c for c in counts])) if counts else float("nan"),
        "witness_forced_frac": float(np.mean([c == 1 for c in counts])) if counts else float("nan"),
        "witness_choices": json.dumps(counts),
        "rule_value": construction_value(instance, orders["rule"]),
        "mcn_value": construction_value(instance, orders["mcn"]),
        "states": stats.get("states", 0), "rows": int(len(y)),
        "good_rows": stats.get("good", 0), "rule_good_states": stats.get("rule_good", 0),
        "seconds": time.time() - started,
    }
    return row, X, y, steps


def run_lattice(workers: int = 8, limit: int | None = None, verbose: bool = True) -> pd.DataFrame:
    corpus = [(f, inst, sol) for f, inst, sol in _corpus()
              if inst.n_customers <= MAX_LATTICE]
    corpus.sort(key=lambda t: -t[1].n_customers)
    if limit:
        corpus = corpus[:limit]
    tasks = [(f, inst, int(sol["mosp_value"]), sol["ordering"], i)
             for i, (f, inst, sol) in enumerate(corpus)]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows, Xs, ys, steps_all = [], [], [], []
    offset = 0
    started = time.time()
    ctx = multiprocessing.get_context("spawn")
    with ctx.Pool(workers) as pool:
        for i, (row, X, y, steps) in enumerate(pool.imap_unordered(_lattice_job, tasks, chunksize=2), 1):
            row["row_start"] = offset
            row["row_end"] = offset + len(y)
            rows.append(row)
            Xs.append(X)
            ys.append(y)
            steps_all.append(steps)
            offset += len(y)
            if verbose and (i % 200 == 0 or i == len(tasks)):
                print(f"[lattice] {i}/{len(tasks)} in {time.time() - started:.0f}s", flush=True)
    frame = pd.DataFrame(rows)
    # re-base step ids to be unique across instances
    step_id = np.zeros(offset, dtype=np.int64)
    inst_id = np.zeros(offset, dtype=np.int32)
    base = 0
    for j, (row, steps) in enumerate(zip(rows, steps_all)):
        n = len(steps)
        if n:
            step_id[row["row_start"]:row["row_end"]] = steps.astype(np.int64) + base
            inst_id[row["row_start"]:row["row_end"]] = j
            base += int(steps.max()) + 1
    X = np.vstack(Xs) if Xs else np.zeros((0, len(FEATURE_NAMES)), np.float32)
    y = np.concatenate(ys) if ys else np.zeros(0, np.int8)
    np.savez_compressed(ROWS_NPZ, X=X, y=y, step=step_id, inst=inst_id,
                        names=np.array(FEATURE_NAMES))
    frame.to_csv(LATTICE_CSV, index=False)
    if verbose:
        bad = int((~frame["audit"]).sum())
        print(f"[lattice] {len(frame)} instances, {len(y):,} rows, {int(frame['states'].sum()):,} states, "
              f"audit failures {bad}, {time.time() - started:.0f}s", flush=True)
    return frame


# --------------------------------------------------------------------------
# Stage 2: folds, models, held-out evaluation
# --------------------------------------------------------------------------

def assign_folds(groups: np.ndarray, folds: int = 5, seed: int = 2) -> np.ndarray:
    """Fold per row: groups shuffled, then placed largest first into the
    currently smallest fold (the largest union group holds 1,620 instances)."""
    sizes = Counter(groups.tolist())
    order = sorted(sizes, key=lambda g: (-sizes[g], g))
    rng = random.Random(seed)
    # shuffle ties of equal size so the assignment is not a function of ids
    order.sort(key=lambda g: (-sizes[g], rng.random()))
    load = [0] * folds
    fold_of: dict = {}
    for g in order:
        f = min(range(folds), key=lambda i: load[i])
        fold_of[g] = f
        load[f] += sizes[g]
    return np.array([fold_of[g] for g in groups])


def corpus_frame() -> tuple[list, pd.DataFrame]:
    """The certified corpus with union groups (file ∪ isomorphism class)."""
    from learning.fingerprint import union_groups

    corpus = _corpus()
    frame = pd.DataFrame({
        "source_file": [f for f, _, _ in corpus],
        "instance_name": [inst.name for _, inst, _ in corpus],
        "n_customers": [inst.n_customers for _, inst, _ in corpus],
        "optimum": [int(sol["mosp_value"]) for _, _, sol in corpus],
    })
    canon = pd.read_csv(CANONICAL_CSV, usecols=["instance_name", "source_file", "graph_cert"])
    frame = frame.merge(canon, on=["instance_name", "source_file"], how="left")
    frame["group"] = union_groups(frame["source_file"], frame["graph_cert"])
    return corpus, frame


def fit_set_models(X: np.ndarray, y: np.ndarray, step: np.ndarray, threads: int = 8,
                   n_estimators: int = 300) -> dict[str, str]:
    """Binary and LambdaRank LightGBM models on the labelled rows; boosters as
    strings so they travel to spawned workers."""
    import lightgbm as lgb

    params = dict(n_estimators=n_estimators, learning_rate=0.08, num_leaves=31,
                  min_child_samples=50, verbose=-1, num_threads=threads)
    out = {}
    clf = lgb.LGBMClassifier(**params)
    clf.fit(X, y, feature_name=FEATURE_NAMES)
    out["set-binary"] = clf.booster_.model_to_string()
    order = np.argsort(step, kind="stable")
    Xs, ys, ss = X[order], y[order], step[order]
    _, sizes = np.unique(ss, return_counts=True)
    rk = lgb.LGBMRanker(**params, label_gain=[0, 1])
    rk.fit(Xs, ys, group=sizes, feature_name=FEATURE_NAMES)
    out["set-rank"] = rk.booster_.model_to_string()
    return out


_WORK: dict = {}


def _init_worker(work: dict) -> None:
    _WORK.clear()
    _WORK.update(work)


def _fold_keys(fold: int) -> dict[str, KeyFn]:
    cache = _WORK.setdefault("_keys", {})
    if fold in cache:
        return cache[fold]
    import lightgbm as lgb

    models = _WORK["models"][fold]
    keys: dict[str, KeyFn] = {"mcn": mcn_key, "rule": rule_key}
    if "old-ranker" in models:
        keys["old-ranker"] = old_ranker_key(lgb.Booster(model_str=models["old-ranker"]))
    for name in ("set-binary", "set-rank"):
        if name in models:
            b = lgb.Booster(model_str=models[name])
            keys[name] = score_key_rule_ties(
                lambda F, b=b: b.predict(F.astype(np.float32), raw_score=True, num_threads=1))
    cache[fold] = keys
    return keys


def _eval_job(task):
    file, instance, optimum, ordering, fold, has_lattice = task
    keys = _fold_keys(fold)
    mk = Masks(instance)
    out = {"source_file": file, "instance_name": instance.name, "fold": fold,
           "n_customers": instance.n_customers, "optimum": optimum}
    lat = Lattice(instance) if has_lattice else None
    nb = _neighbour_masks(instance)
    for name, key in keys.items():
        order = greedy_order(instance, key, mk)
        out[name] = construction_value(instance, order)
        if lat is not None:
            # step accuracy under the correct objective, along the policy's own path
            good_steps, steps = _own_good(lat, mk, nb, order)
            out[f"own_good:{name}"] = good_steps
            out[f"own_steps:{name}"] = steps
    if lat is not None:
        witness = _customer_order_from_products(instance, ordering)
        wit = _witness_good(lat, mk, nb, witness, keys)
        out.update(wit)
    return out


def _own_good(lat: Lattice, mk: Masks, nb, order: Sequence[int]) -> tuple[int, int]:
    closed = opened = made = done = 0
    peak = 0
    good_steps = steps = 0
    for c in order:
        remaining = [d for d in mk.active if not (closed >> d) & 1]
        if len(remaining) > 1:
            S = lat.state(_bits(closed))
            good = lat.good_moves(S, peak)
            steps += 1
            good_steps += int(good[c])
        cost, opened, made, done = mk.block_cost(opened, made, done, c)
        peak = max(peak, cost)
        closed |= 1 << c
    return good_steps, steps


def _witness_good(lat: Lattice, mk: Masks, nb, witness: Sequence[int],
                  keys: dict[str, KeyFn]) -> dict:
    """Along the witness: is each policy's pick in the exact optimal set?"""
    closed = opened = made = done = 0
    peak = 0
    counts = {f"wit_good:{name}": 0 for name in keys}
    steps = 0
    for c in witness:
        if c not in lat.pos or (closed >> c) & 1:
            continue
        remaining = [d for d in mk.active if not (closed >> d) & 1]
        if len(remaining) > 1:
            S = lat.state(_bits(closed))
            good = lat.good_moves(S, peak)
            X = candidate_matrix(nb, mk.n, mk.prod, closed, opened, made, remaining)
            steps += 1
            for name, key in keys.items():
                pick = remaining[pick_min(key(X, peak))]
                counts[f"wit_good:{name}"] += int(good[pick])
        cost, opened, made, done = mk.block_cost(opened, made, done, c)
        peak = max(peak, cost)
        closed |= 1 << c
    counts["wit_steps"] = steps
    return counts


def run_train(workers: int = 8, folds: int = 5, seed: int = 2, threads: int = 8,
              old_ranker: bool = True, verbose: bool = True) -> pd.DataFrame:
    data = np.load(ROWS_NPZ, allow_pickle=True)
    X, y, step, inst = data["X"], data["y"], data["step"], data["inst"]
    lattice = pd.read_csv(LATTICE_CSV)
    corpus, frame = corpus_frame()
    frame["fold"] = assign_folds(frame["group"].to_numpy(), folds, seed)
    key = frame.set_index(["source_file", "instance_name"])["fold"]
    lat_fold = np.array([key.get((f, n), -1) for f, n in
                         zip(lattice["source_file"], lattice["instance_name"])])
    row_fold = lat_fold[inst]
    models: dict[int, dict[str, str]] = {}
    fit_seconds = {}
    for f in range(folds):
        started = time.time()
        train = row_fold != f
        models[f] = fit_set_models(X[train], y[train], step[train], threads=threads)
        if old_ranker:
            train_corpus = [row for row, fold in zip(corpus, frame["fold"]) if fold != f]
            booster, n_rows = _fit(train_corpus)
            models[f]["old-ranker"] = booster.model_to_string()
        fit_seconds[f] = time.time() - started
        if verbose:
            print(f"[train] fold {f}: {int(train.sum()):,} set rows"
                  f"{'' if not old_ranker else f', old ranker on {n_rows:,} rows'}, "
                  f"{fit_seconds[f]:.0f}s", flush=True)
    MODELS_JSON.write_text(json.dumps({str(f): m for f, m in models.items()}))
    has_lattice = set(zip(lattice["source_file"], lattice["instance_name"]))
    tasks = [(f, inst_, int(sol["mosp_value"]), sol["ordering"], int(fold),
              (f, inst_.name) in has_lattice)
             for (f, inst_, sol), fold in zip(corpus, frame["fold"])]
    tasks.sort(key=lambda t: -t[1].n_customers)
    started = time.time()
    ctx = multiprocessing.get_context("spawn")
    with ctx.Pool(workers, initializer=_init_worker, initargs=({"models": models},)) as pool:
        rows = []
        for i, row in enumerate(pool.imap_unordered(_eval_job, tasks, chunksize=4), 1):
            rows.append(row)
            if verbose and (i % 1000 == 0 or i == len(tasks)):
                print(f"[eval] {i}/{len(tasks)} in {time.time() - started:.0f}s", flush=True)
    out = pd.DataFrame(rows).merge(frame[["source_file", "instance_name", "group"]],
                                   on=["source_file", "instance_name"], how="left")
    out.to_csv(EVAL_CSV, index=False)
    return out


# --------------------------------------------------------------------------
# Stage 3: bounded optimal choices along the witnesses at 50-125
# --------------------------------------------------------------------------

def bounded_completes(mk: Masks, closed: int, opened: int, made: int, done: int,
                      k: int, budget: list[int]) -> bool:
    """Restricted DFS (branch on already-open customers, cheapest first) for a
    completion whose every block cost is <= k. `budget[0]` nodes; False when
    exhausted (which is *not* a refutation)."""
    remaining = mk.full & ~closed
    if remaining == 0:
        return True
    if budget[0] <= 0:
        return False
    budget[0] -= 1
    # free moves: neighbourhood wholly opened -> closing opens nothing
    free = 0
    bits = remaining
    while bits:
        b = bits & -bits
        bits ^= b
        if mk.neigh[b.bit_length() - 1] & ~opened == 0:
            free |= b
    if free:
        for c in _bits(free):
            cost, opened, made, done = mk.block_cost(opened, made, done, c)
            if cost > k:
                return False
            closed |= 1 << c
        return bounded_completes(mk, closed, opened, made, done, k, budget)
    cands = []
    for c in _bits(remaining):
        cost, o2, m2, d2 = mk.block_cost(opened, made, done, c)
        if cost <= k:
            cands.append((cost, -((mk.neigh[c] & ~closed).bit_count()), c, o2, m2, d2))
    if not cands:
        return False
    open_cands = [t for t in cands if (opened >> t[2]) & 1]
    if open_cands:
        cands = open_cands
    cands.sort()
    for cost, _, c, o2, m2, d2 in cands:
        if bounded_completes(mk, closed | (1 << c), o2, m2, d2, k, budget):
            return True
        if budget[0] <= 0:
            return False
    return False


def bounded_choices(instance: MOSPInstance, k: int, witness: Sequence[int],
                    nodes: int = 300, deadline: float | None = None) -> dict:
    """Per step of `witness`: confirmed optimal choices (lower bound), how many
    came from the suffix test and from the DFS, and how many stayed unknown."""
    mk = Masks(instance)
    order = [c for c in witness if c in set(mk.active)]
    seen = set()
    order = [c for c in order if not (c in seen or seen.add(c))]
    closed = opened = made = done = 0
    peak = 0
    confirmed, by_suffix, by_dfs, unknown, censored = [], [], [], [], False
    n = len(order)
    for i, c in enumerate(order):
        remaining = order[i:]
        if len(remaining) > 1:
            conf = suf = dfs = unk = 0
            for alt in remaining:
                if deadline is not None and time.monotonic() > deadline:
                    censored = True
                    break
                cost, o2, m2, d2 = mk.block_cost(opened, made, done, alt)
                if max(cost, peak) > k:
                    continue
                # (a) the witness's own suffix, with `alt` moved to the front
                rest = [d for d in remaining if d != alt]
                o3, m3, d3, pk = o2, m2, d2, max(peak, cost)
                ok = True
                for d in rest:
                    cst, o3, m3, d3 = mk.block_cost(o3, m3, d3, d)
                    if cst > k:
                        ok = False
                        break
                if ok:
                    conf += 1
                    suf += 1
                    continue
                # (b) a bounded restricted DFS from the state after `alt`
                if bounded_completes(mk, closed | (1 << alt), o2, m2, d2, k, [nodes]):
                    conf += 1
                    dfs += 1
                else:
                    unk += 1
            confirmed.append(conf)
            by_suffix.append(suf)
            by_dfs.append(dfs)
            unknown.append(unk)
            if censored:
                break
        cost, opened, made, done = mk.block_cost(opened, made, done, c)
        peak = max(peak, cost)
        closed |= 1 << c
    return {"confirmed": confirmed, "by_suffix": by_suffix, "by_dfs": by_dfs,
            "unknown": unknown, "censored": censored, "steps_total": n - 1}


def _ceiling_job(task):
    file, instance, optimum, ordering, nodes, seconds = task
    started = time.time()
    witness = _customer_order_from_products(instance, ordering)
    mk = Masks(instance)
    value = mk.order_value(witness)
    res = bounded_choices(instance, optimum, witness, nodes=nodes,
                          deadline=time.monotonic() + seconds if seconds else None)
    conf = res["confirmed"]
    row = {
        "source_file": file, "instance_name": instance.name,
        "n_customers": instance.n_customers, "n_patterns": instance.n_patterns,
        "optimum": optimum, "witness_construction_value": value,
        "witness_optimal": value == optimum,
        "steps": len(conf), "steps_total": res["steps_total"], "censored": res["censored"],
        "confirmed_mean": float(np.mean(conf)) if conf else float("nan"),
        "ceiling_upper": float(np.mean([1 / max(c, 1) for c in conf])) if conf else float("nan"),
        "forced_upper_frac": float(np.mean([c <= 1 for c in conf])) if conf else float("nan"),
        "multi_frac": float(np.mean([c >= 2 for c in conf])) if conf else float("nan"),
        "by_suffix": int(sum(res["by_suffix"])), "by_dfs": int(sum(res["by_dfs"])),
        "unknown": int(sum(res["unknown"])),
        "confirmed": json.dumps(conf), "nodes": nodes,
        "seconds": time.time() - started,
    }
    return row


def run_ceiling(workers: int = 8, nodes: int = 300, seconds: float = 300.0,
                min_n: int = 50, verbose: bool = True) -> pd.DataFrame:
    corpus = [(f, inst, sol) for f, inst, sol in _corpus() if inst.n_customers >= min_n]
    corpus.sort(key=lambda t: -t[1].n_customers)
    tasks = [(f, inst, int(sol["mosp_value"]), sol["ordering"], nodes, seconds)
             for f, inst, sol in corpus]
    started = time.time()
    ctx = multiprocessing.get_context("spawn")
    rows = []
    with ctx.Pool(workers) as pool:
        for i, row in enumerate(pool.imap_unordered(_ceiling_job, tasks), 1):
            rows.append(row)
            if verbose and (i % 25 == 0 or i == len(tasks)):
                print(f"[ceiling] {i}/{len(tasks)} in {time.time() - started:.0f}s", flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(CEILING_CSV, index=False)
    return frame


def run_calibration(workers: int = 8, nodes: int = 300, seconds: float = 60.0,
                    lo: int = 16, hi: int = 20, verbose: bool = True) -> pd.DataFrame:
    """The bounded procedure on 16-20 against the exact counts."""
    lattice = pd.read_csv(LATTICE_CSV)
    exact = lattice.set_index(["source_file", "instance_name"])
    corpus = [(f, inst, sol) for f, inst, sol in _corpus() if lo <= inst.n_customers <= hi]
    tasks = [(f, inst, int(sol["mosp_value"]), sol["ordering"], nodes, seconds)
             for f, inst, sol in corpus]
    ctx = multiprocessing.get_context("spawn")
    started = time.time()
    with ctx.Pool(workers) as pool:
        rows = pool.map(_ceiling_job, tasks, chunksize=4)
    frame = pd.DataFrame(rows)
    ex_counts, ex_ceil = [], []
    for f, name in zip(frame["source_file"], frame["instance_name"]):
        # the exact list carries the forced last step; the bounded one stops before it
        counts = json.loads(exact.loc[(f, name), "witness_choices"])[:-1]
        ex_counts.append(json.dumps(counts))
        ex_ceil.append(float(np.mean([1 / c for c in counts])) if counts else float("nan"))
    frame["exact_choices"] = ex_counts
    frame["exact_ceiling"] = ex_ceil
    frame["exact_mean_choices"] = [float(np.mean(json.loads(s))) if json.loads(s) else float("nan")
                                   for s in ex_counts]
    frame["steps_exact_match"] = [sum(a == b for a, b in zip(json.loads(x), json.loads(y)))
                                  for x, y in zip(frame["confirmed"], ex_counts)]
    frame.to_csv(CALIB_CSV, index=False)
    if verbose:
        print(f"[calibration] {len(frame)} instances in {time.time() - started:.0f}s", flush=True)
    return frame


# --------------------------------------------------------------------------
# Stage 4: tables
# --------------------------------------------------------------------------

def _md(frame: pd.DataFrame, floats: int = 3) -> str:
    cols = list(frame.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |",
             "|" + "---|" * len(cols)]
    for _, r in frame.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                cells.append("nan" if math.isnan(v) else f"{v:.{floats}f}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def summary(ev: pd.DataFrame, strategies: Sequence[str] = STRATEGIES) -> pd.DataFrame:
    truth = ev["optimum"].to_numpy()
    rows = []
    for s in strategies:
        if s not in ev:
            continue
        err = ev[s].to_numpy() - truth
        rows.append({"strategy": s, "instances": len(ev), "MAE": float(np.abs(err).mean()),
                     "exact": float((err == 0).mean()), "worst": int(err.max()),
                     "total_overshoot": int(err.sum())})
    return pd.DataFrame(rows)


def by_band(ev: pd.DataFrame, strategies: Sequence[str] = STRATEGIES,
            bands=SIZE_BANDS) -> pd.DataFrame:
    rows = []
    for lo, hi in bands:
        sub = ev[ev["n_customers"].between(lo, hi)]
        if sub.empty:
            continue
        row = {"customers": f"{lo}–{hi}", "instances": len(sub)}
        for s in strategies:
            if s in sub:
                row[s] = float(np.abs(sub[s] - sub["optimum"]).mean())
        rows.append(row)
    return pd.DataFrame(rows)


def head_to_head(ev: pd.DataFrame, pairs) -> pd.DataFrame:
    rows = []
    for a, b in pairs:
        if a in ev and b in ev:
            d = ev[a] - ev[b]
            rows.append({"first": a, "second": b, "better": int((d < 0).sum()),
                         "equal": int((d == 0).sum()), "worse": int((d > 0).sum())})
    return pd.DataFrame(rows)


def step_accuracy(ev: pd.DataFrame, strategies: Sequence[str] = STRATEGIES) -> pd.DataFrame:
    sub = ev[ev["wit_steps"].notna()] if "wit_steps" in ev else ev.iloc[0:0]
    rows = []
    for s in strategies:
        if f"wit_good:{s}" not in sub:
            continue
        rows.append({"strategy": s,
                     "own path: good steps": float(sub[f"own_good:{s}"].sum() / sub[f"own_steps:{s}"].sum()),
                     "witness states: good picks": float(sub[f"wit_good:{s}"].sum() / sub["wit_steps"].sum())})
    return pd.DataFrame(rows)


def grouped_mae(ev: pd.DataFrame, a: str, b: str) -> dict:
    """Difference of MAE, `a - b`, with a bootstrap over groups (file ∪ class)."""
    g = ev.groupby("group")
    da = (ev[a] - ev["optimum"]).abs()
    db = (ev[b] - ev["optimum"]).abs()
    per = pd.DataFrame({"da": da, "db": db, "g": ev["group"]}).groupby("g").agg(["sum", "count"])
    sums_a = per[("da", "sum")].to_numpy(); sums_b = per[("db", "sum")].to_numpy()
    cnt = per[("da", "count")].to_numpy()
    rng = np.random.default_rng(0)
    diffs = []
    for _ in range(2000):
        idx = rng.integers(0, len(cnt), len(cnt))
        diffs.append((sums_a[idx].sum() - sums_b[idx].sum()) / cnt[idx].sum())
    diffs = np.array(diffs)
    return {"first": a, "second": b, "MAE diff": float(da.mean() - db.mean()),
            "bootstrap p5": float(np.percentile(diffs, 5)),
            "bootstrap p95": float(np.percentile(diffs, 95)), "groups": int(len(cnt))}


def ceiling_table(lat: pd.DataFrame, ceil: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for lo, hi in ((9, 15), (16, 20)):
        sub = lat[lat["n_customers"].between(lo, hi) & (lat["n_active"] > lat["optimum"])]
        if sub.empty:
            continue
        rows.append({"customers": f"{lo}–{hi}", "instances": len(sub), "kind": "exact",
                     "mean choices per step": float(sub["witness_mean_choices"].median()),
                     "ceiling (median)": float(sub["witness_ceiling"].median()),
                     "ceiling (mean)": float(sub["witness_ceiling"].mean()),
                     "forced steps": float(sub["witness_forced_frac"].mean())})
    if not ceil.empty:
        for lo, hi in ((50, 75), (76, 100), (101, 134)):
            sub = ceil[ceil["n_customers"].between(lo, hi)]
            if sub.empty:
                continue
            rows.append({"customers": f"{lo}–{hi}", "instances": len(sub), "kind": "bounded (lower bound on choices)",
                         "mean choices per step": float(sub["confirmed_mean"].median()),
                         "ceiling (median)": float(sub["ceiling_upper"].median()),
                         "ceiling (mean)": float(sub["ceiling_upper"].mean()),
                         "forced steps": float(sub["forced_upper_frac"].mean())})
    return pd.DataFrame(rows)


def write_tables(out: Path = TABLES_OUT) -> str:
    lat = pd.read_csv(LATTICE_CSV)
    ev = pd.read_csv(EVAL_CSV)
    ceil = pd.read_csv(CEILING_CSV) if CEILING_CSV.exists() else pd.DataFrame()
    cal = pd.read_csv(CALIB_CSV) if CALIB_CSV.exists() else pd.DataFrame()
    small = ev[ev["n_customers"] <= MAX_LATTICE]
    parts = ["# Set-valued imitation — tables (loop0003 item 10)\n",
             "Regenerate: `python -m learning.set_imitation --stage tables`.\n",
             "## Lattice audit\n",
             f"- instances: {len(lat)}; audit failures (lattice optimum ≠ certified): {int((~lat['audit']).sum())}; "
             f"witnesses not construction-optimal: {int((~lat['witness_optimal']).sum())}; "
             f"labelled states: {int(lat['states'].sum()):,}; rows: {int(lat['rows'].sum()):,}; "
             f"good rows: {int(lat['good_rows'].sum()):,}; "
             f"rule's pick good on {lat['rule_good_states'].sum() / max(lat['states'].sum(), 1):.3f} of labelled states; "
             f"lattice seconds total {lat['seconds'].sum():.0f}, max {lat['seconds'].max():.1f}.\n",
             "## Held out, n ≤ 20 (training regime)\n", _md(summary(small)), "",
             "## Held out, whole corpus (models fitted at n ≤ 20)\n", _md(summary(ev)), "",
             "## MAE by size band, whole corpus\n", _md(by_band(ev)), "",
             "## Head to head (whole corpus)\n",
             _md(head_to_head(ev, [("set-binary", "rule"), ("set-rank", "rule"), ("old-ranker", "rule"),
                                   ("set-binary", "old-ranker"), ("rule", "mcn")])), "",
             "## Head to head (n ≤ 20)\n",
             _md(head_to_head(small, [("set-binary", "rule"), ("set-rank", "rule"), ("old-ranker", "rule")])), "",
             "## Grouped MAE difference with a bootstrap over groups\n",
             _md(pd.DataFrame([grouped_mae(small, "set-binary", "rule"), grouped_mae(small, "set-rank", "rule"),
                               grouped_mae(ev, "set-binary", "rule"), grouped_mae(ev, "set-rank", "rule"),
                               grouped_mae(ev, "old-ranker", "rule")])), "",
             "## Step accuracy under the correct objective, n ≤ 20\n", _md(step_accuracy(small)), "",
             "## The imitation ceiling along the witnesses\n", _md(ceiling_table(lat, ceil)), ""]
    if not ceil.empty:
        parts += ["## Bounded search at ≥ 50: where the confirmations came from\n",
                  f"- instances {len(ceil)}, censored {int(ceil['censored'].sum())}, witnesses not construction-optimal "
                  f"{int((~ceil['witness_optimal']).sum())}; confirmations by suffix {int(ceil['by_suffix'].sum()):,}, "
                  f"by DFS {int(ceil['by_dfs'].sum()):,}, unknown {int(ceil['unknown'].sum()):,}; "
                  f"seconds total {ceil['seconds'].sum():.0f}, max {ceil['seconds'].max():.0f}.\n"]
        per = ceil.groupby("n_customers").agg(instances=("instance_name", "size"),
                                              ceiling_upper_median=("ceiling_upper", "median"),
                                              ceiling_upper_max=("ceiling_upper", "max"),
                                              confirmed_mean_median=("confirmed_mean", "median"),
                                              multi_frac_mean=("multi_frac", "mean"),
                                              censored=("censored", "sum")).reset_index()
        parts += [_md(per), ""]
    if not cal.empty:
        parts += ["## Calibration of the bounded procedure at 16–20 against the exact counts\n",
                  f"- instances {len(cal)}; confirmed / exact choices (sum over steps): "
                  f"{sum(sum(json.loads(s)) for s in cal['confirmed']) / max(sum(sum(json.loads(s)) for s in cal['exact_choices']), 1):.3f}; "
                  f"mean ceiling upper bound {cal['ceiling_upper'].mean():.3f} vs exact {cal['exact_ceiling'].mean():.3f}; "
                  f"instances where the bound equals the exact ceiling: "
                  f"{int((np.isclose(cal['ceiling_upper'], cal['exact_ceiling'])).sum())}; "
                  f"steps where the confirmed count equals the exact count: "
                  f"{cal['steps_exact_match'].sum() / max(cal['steps'].sum(), 1):.4f}; "
                  f"seconds per instance max {cal['seconds'].max():.3f}.\n"]
    text = "\n".join(parts)
    out.write_text(text)
    return text


# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", choices=["all", "lattice", "train", "ceiling", "calibration", "tables"],
                    default="all")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--threads", type=int, default=8, help="LightGBM threads")
    ap.add_argument("--limit", type=int, default=None, help="lattice: instances (largest first)")
    ap.add_argument("--nodes", type=int, default=300, help="ceiling: DFS nodes per alternative")
    ap.add_argument("--seconds", type=float, default=300.0, help="ceiling: deadline per instance")
    ap.add_argument("--no-old-ranker", action="store_true")
    args = ap.parse_args()
    ENSEMBLE_DIR.mkdir(parents=True, exist_ok=True)
    if args.stage in ("all", "lattice"):
        run_lattice(args.workers, args.limit)
    if args.stage in ("all", "train"):
        run_train(args.workers, threads=args.threads, old_ranker=not args.no_old_ranker)
    if args.stage in ("all", "ceiling"):
        run_ceiling(args.workers, nodes=args.nodes, seconds=args.seconds)
    if args.stage in ("all", "calibration"):
        run_calibration(args.workers, nodes=args.nodes)
    if args.stage in ("all", "tables"):
        print(write_tables())


if __name__ == "__main__":
    main()
