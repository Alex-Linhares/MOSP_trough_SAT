"""What readable rule did the closing policy learn? (plan §2.6a)

Question. `learning.policy` imitates the 2.27 M closing decisions in the
certified witnesses with a LightGBM ranker over eight local features and, used
greedily, cuts MCN's error over the optimum by two thirds. The ranker is
opaque. This module asks how much of that gain survives in a rule a person can
read and try to prove:

  * a depth-3 decision tree and a linear scorer fitted to the same decisions
    (`tree`, `linear`), and the same two fitted instead to the ranker's own
    scores on those rows (`tree-fid`, `linear-fid`), which is distillation in
    the strict sense -- imitating the model rather than the witness;
  * every lexicographic rule of depth <= 3 over the per-candidate features
    (`remaining_degree`, `newly_opened`, `already_open`, `total_degree`,
    `patterns`, each in either direction), MCN's own key as the final
    tie-break -- so MCN itself is the empty rule;
  * two fixed rules named in every table (`HYPOTHESES`): "open the fewest new
    stacks", which is the cheapest-first order Chu & Stuckey's `ub_MOSP` DFS
    expands candidates in, followed greedily -- so it is that search's first
    leaf -- and the same with the largest remaining degree breaking ties; the
    second also seeds `restricted_dfs` (`cs-dfs+rule`) beside the MCN seed
    (`cs-dfs`) and the ranker's order (`cs-dfs+lgbm`), 200,000 nodes each;
  * two static hypotheses from the plan: closing in Fiedler-vector order of the
    MOSP graph, and in BFS layers from a minimum-degree root (Cuthill--McKee,
    which is the ordering behind the `bw_rcm` invariant of §4); plus min-degree
    elimination with fill-in, which is MCN made to remember that the open
    neighbours of a closed customer stay open together.

Method. The protocol of `python -m learning.policy evaluate`: five folds
grouped by source file with the same seed, up to `--per-fold` held-out
instances per fold, every construction turned into a product order with
`product_order_from_customers` and *simulated* on the original instance with
`mosp.verify.max_open_stacks`. MCN here is `least_cost_node`'s key exactly --
remaining degree, then products not yet produced, then index -- and the table
reports how often the two constructions disagree (`mcn-ref`), which should be
never. Models are fitted per fold on the training
files' decision rows. Lexicographic rules are *selected* on a sample of
training instances and scored held out, so the "best rule" number is honest;
the full table over the held-out sample is descriptive and says so. The
summary statistic is

    gain kept = (MAE_mcn - MAE_rule) / (MAE_mcn - MAE_lgbm)

with 1.0 meaning the rule matches the ranker and 0.0 meaning it is MCN. At
step level two agreement rates are also reported: imitation (the rule picks
the witness's customer) and fidelity (it picks the ranker's).

One identity worth knowing before reading the coefficients: at any step
`open_after = open_now + newly_opened - 1`, and `open_now`, `progress`,
`n_customers` are the same for every candidate of a step, so a linear scorer
has four effective coefficients and the tree can use the other features only
to switch rules by phase.

Not a bound, not a solver change: nothing here touches `_lower_bound`, no
default changes, nothing is written to `solutions/`.

Run:
    python -m learning.distil                    # ~15 min on 16 workers
    python -m learning.distil --lex-depth 2      # ~3 min
    python -m learning.distil --per-fold 100     # a quick look

The worker pool uses the `spawn` start method on purpose: forking after the
parent has fitted a LightGBM model deadlocks the children in libgomp the first
time they predict (the first run of this module sat for fifteen minutes on
eight sleeping workers). Models travel to the workers pickled, the booster as
its string form.

Writes `reports/distil_tables.md` and `learning/data/distil.csv`.
"""

from __future__ import annotations

import argparse
import itertools
import multiprocessing
import os
import random
import time
import warnings
from pathlib import Path
from typing import Callable, Optional, Sequence

import numpy as np
import pandas as pd

from learning.policy import STEP_FEATURE_NAMES, _corpus, _fit, step_features
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.heuristics import (
    _customer_order_from_products,
    _neighbour_masks,
    product_order_from_customers,
)

DEFAULT_OUT = Path("reports/distil_tables.md")
DATA_OUT = Path("learning/data/distil.csv")

# Same bands as `learning.invariants_study`, restated to keep the import light.
SIZE_BANDS = ((1, 30), (31, 60), (61, 200))

# Per-candidate columns: the eight step features, then two the hand rules use
# for tie-breaking: `patterns` is the number of the candidate's products not yet
# produced, which is MCN's second key (`least_cost_node`), then the index.
AUX_NAMES = ["patterns", "index"]
COLUMNS = STEP_FEATURE_NAMES + AUX_NAMES
COL = {name: i for i, name in enumerate(COLUMNS)}

# Features that differ between the candidates of one step. `open_after` is
# left out of the rule family because it is `open_now + newly_opened - 1`.
DISCRIMINATING = ["remaining_degree", "newly_opened", "already_open",
                  "total_degree", "patterns"]

# MCN's key, minimised: remaining degree, then product count, then index.
MCN_KEY = ("remaining_degree", "patterns", "index")

# Two fixed rules reported by name in every table, whatever the selection
# picks: "open the fewest new stacks" -- the cheapest-first order Chu &
# Stuckey's `ub_MOSP` DFS expands candidates in, followed greedily -- and the
# same with the largest remaining degree breaking ties. They are named here so
# their step-level agreement and DFS-seeded values are computed; their
# held-out numbers are descriptive (the honest selected row is `lex-selected`).
HYPOTHESIS_RULE = "lex:min newly_opened,max remaining_degree"   # seeds `cs-dfs+rule`
HYPOTHESES: dict[str, list[tuple[str, int]]] = {
    "lex:min newly_opened": [("newly_opened", 1)],
    "lex:min newly_opened,max remaining_degree": [("newly_opened", 1), ("remaining_degree", -1)],
}


# -------------------------------------------------------
# Greedy construction under a key
# -------------------------------------------------------

KeyFn = Callable[[np.ndarray], np.ndarray]
"""Maps the (candidates x COLUMNS) matrix of a step to a (candidates x d)
matrix of key columns; the candidate minimising them lexicographically closes
next (first column most significant)."""


def _pattern_masks(instance: MOSPInstance) -> list[int]:
    """Bitmask over products of each customer's patterns."""
    out = []
    for c in range(instance.n_customers):
        m = 0
        for p in instance.customer_patterns(c):
            m |= 1 << p
        out.append(m)
    return out


def candidate_matrix(masks: Sequence[int], n: int, pmasks: Sequence[int],
                     closed: int, opened: int, produced: int,
                     candidates: Sequence[int]) -> np.ndarray:
    """One row per candidate: the eight step features, then the number of its
    products not yet produced and its index."""
    return np.array(
        [step_features(masks, n, closed, opened, c)
         + [float((pmasks[c] & ~produced).bit_count()), float(c)]
         for c in candidates],
        dtype=np.float64,
    )


def pick_min(keys: np.ndarray) -> int:
    """Row index of the lexicographic minimum (first column most significant)."""
    if keys.ndim == 1:
        keys = keys[:, None]
    return int(np.lexsort(keys.T[::-1])[0])


def greedy_closing_order(instance: MOSPInstance, key_fn: KeyFn) -> list[int]:
    """Close, at every step, the candidate with the smallest key."""
    masks = _neighbour_masks(instance)
    n = instance.n_customers
    pmasks = _pattern_masks(instance)
    closed = opened = produced = 0
    remaining = [c for c in range(n) if masks[c]]
    order: list[int] = []
    while remaining:
        X = candidate_matrix(masks, n, pmasks, closed, opened, produced, remaining)
        pick = remaining[pick_min(key_fn(X))]
        order.append(pick)
        opened |= masks[pick]
        closed |= 1 << pick
        produced |= pmasks[pick]
        remaining.remove(pick)
    return order


def lex_key(rule: Sequence[tuple[str, int]], tie: Sequence[str] = MCN_KEY) -> KeyFn:
    """`rule` is a list of (feature, sign): sign +1 prefers small values, -1
    prefers large. The empty rule is MCN."""
    idx = [COL[f] for f, _ in rule]
    signs = np.array([s for _, s in rule], dtype=np.float64)
    tie_idx = [COL[f] for f in tie]

    def key(X: np.ndarray) -> np.ndarray:
        parts = [X[:, idx] * signs] if idx else []
        parts.append(X[:, tie_idx])
        return np.hstack(parts)

    return key


def lex_name(rule: Sequence[tuple[str, int]]) -> str:
    if not rule:
        return "mcn"
    return "lex:" + ",".join(("min " if s > 0 else "max ") + f for f, s in rule)


def lex_family(depth: int = 2, features: Sequence[str] = DISCRIMINATING
               ) -> list[list[tuple[str, int]]]:
    """Every lexicographic rule of length 0..depth over distinct features,
    each in either direction; MCN's key breaks the remaining ties, so the
    empty rule is MCN itself."""
    rules: list[list[tuple[str, int]]] = [[]]   # the empty rule is MCN
    for length in range(1, depth + 1):
        for feats in itertools.permutations(features, length):
            for signs in itertools.product((1, -1), repeat=length):
                rules.append(list(zip(feats, signs)))
    return rules


def score_key(scores_of: Callable[[np.ndarray], np.ndarray],
              tie: Sequence[str] = MCN_KEY) -> KeyFn:
    """Higher score closes first; ties fall through to `tie`."""
    tie_idx = [COL[f] for f in tie]

    def key(X: np.ndarray) -> np.ndarray:
        s = np.asarray(scores_of(X[:, :len(STEP_FEATURE_NAMES)]), dtype=np.float64)
        return np.hstack([-s[:, None], X[:, tie_idx]])

    return key


# -------------------------------------------------------
# Static hypotheses
# -------------------------------------------------------

def _components(masks: Sequence[int], active: Sequence[int]) -> list[list[int]]:
    seen = 0
    out: list[list[int]] = []
    for start in active:
        if (seen >> start) & 1:
            continue
        comp = 0
        frontier = 1 << start
        while frontier:
            comp |= frontier
            nxt = 0
            f = frontier
            while f:
                v = (f & -f).bit_length() - 1
                f &= f - 1
                nxt |= masks[v]
            frontier = nxt & ~comp
        seen |= comp
        out.append([c for c in active if (comp >> c) & 1])
    return out


def fiedler_order(instance: MOSPInstance, reverse: bool = False) -> list[int]:
    """Customers sorted by the Fiedler vector of their component of the MOSP
    graph; components in order of their smallest customer. The eigenvector's
    sign is fixed so the smallest-index customer with a nonzero entry is
    negative, and `reverse` flips every component."""
    masks = _neighbour_masks(instance)
    n = instance.n_customers
    active = [c for c in range(n) if masks[c]]
    order: list[int] = []
    for comp in _components(masks, active):
        if len(comp) == 1:
            order += comp
            continue
        pos = {v: i for i, v in enumerate(comp)}
        lap = np.zeros((len(comp), len(comp)))
        for v in comp:
            for u in comp:
                if u != v and (masks[v] >> u) & 1:
                    lap[pos[v], pos[u]] = -1.0
            lap[pos[v], pos[v]] = -lap[pos[v]].sum()
        _, vecs = np.linalg.eigh(lap)
        f = vecs[:, 1]
        nonzero = np.flatnonzero(np.abs(f) > 1e-9)
        if len(nonzero) and f[nonzero[0]] > 0:
            f = -f
        comp_order = sorted(comp, key=lambda v: (round(float(f[pos[v]]), 9), v))
        if reverse:
            comp_order.reverse()
        order += comp_order
    return order


def bfs_order(instance: MOSPInstance, by_degree: bool = True,
              reverse: bool = False) -> list[int]:
    """BFS layers from a minimum-degree root of each component. With
    `by_degree` the neighbours of a dequeued customer are visited in increasing
    degree, which is Cuthill--McKee; `reverse` gives RCM."""
    masks = _neighbour_masks(instance)
    n = instance.n_customers
    active = [c for c in range(n) if masks[c]]
    degree = [masks[c].bit_count() - 1 for c in range(n)]
    order: list[int] = []
    for comp in _components(masks, active):
        root = min(comp, key=lambda v: (degree[v], v))
        seen = 1 << root
        queue = [root]
        comp_order: list[int] = []
        while queue:
            v = queue.pop(0)
            comp_order.append(v)
            nbrs = [u for u in comp if (masks[v] >> u) & 1 and not (seen >> u) & 1]
            if by_degree:
                nbrs.sort(key=lambda u: (degree[u], u))
            for u in nbrs:
                seen |= 1 << u
                queue.append(u)
        if reverse:
            comp_order.reverse()
        order += comp_order
    return order


def elimination_order(instance: MOSPInstance) -> list[int]:
    """Min-degree elimination with fill-in: close the customer of minimum
    degree in the *filled* graph, then make its remaining neighbours a clique.
    MCN with memory of which customers were open together."""
    masks = list(_neighbour_masks(instance))
    n = instance.n_customers
    pmasks = _pattern_masks(instance)
    remaining = {c for c in range(n) if masks[c]}
    alive = produced = 0
    for c in remaining:
        alive |= 1 << c
    order: list[int] = []
    while remaining:
        v = min(remaining, key=lambda c: ((masks[c] & alive).bit_count() - 1,
                                          (pmasks[c] & ~produced).bit_count(), c))
        nb = masks[v] & alive & ~(1 << v)
        f = nb
        while f:
            u = (f & -f).bit_length() - 1
            f &= f - 1
            masks[u] |= nb
        order.append(v)
        remaining.remove(v)
        alive &= ~(1 << v)
        produced |= pmasks[v]
    return order


STATIC_RULES: dict[str, Callable[[MOSPInstance], list[int]]] = {
    "fiedler": lambda inst: fiedler_order(inst),
    "fiedler-rev": lambda inst: fiedler_order(inst, reverse=True),
    "bfs-fifo": lambda inst: bfs_order(inst, by_degree=False),
    "cuthill-mckee": lambda inst: bfs_order(inst),
    "rcm": lambda inst: bfs_order(inst, reverse=True),
    "elim-min-degree": elimination_order,
}


# -------------------------------------------------------
# Distilled scorers
# -------------------------------------------------------

def decision_rows(corpus) -> tuple[np.ndarray, np.ndarray]:
    from learning.policy import training_rows, witness_closing_order

    X: list[list[float]] = []
    y: list[int] = []
    for _, instance, solution in corpus:
        rows, labels = training_rows(
            instance, witness_closing_order(instance, solution["ordering"]))
        X.extend(rows)
        y.extend(labels)
    return np.array(X, dtype=np.float32), np.array(y)


def fit_tree(X: np.ndarray, y: np.ndarray, depth: int = 3, min_leaf: int = 2000):
    from sklearn.tree import DecisionTreeClassifier

    tree = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=min_leaf,
                                  random_state=0)
    tree.fit(X, y)
    return tree


def fit_linear(X: np.ndarray, y: np.ndarray, rows: int = 600_000, seed: int = 0):
    """Logistic regression on standardised features; returns (model, scaler)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    rng = np.random.default_rng(seed)
    if len(y) > rows:
        keep = rng.choice(len(y), rows, replace=False)
        X, y = X[keep], y[keep]
    scaler = StandardScaler().fit(X)
    model = LogisticRegression(max_iter=1000, C=1.0)
    model.fit(scaler.transform(X), y)
    return model, scaler


def fit_tree_to_scores(X: np.ndarray, scores: np.ndarray, depth: int = 3,
                       min_leaf: int = 2000):
    """A depth-3 regression tree on the ranker's raw scores: distillation in
    the strict sense, imitating the model rather than the witness."""
    from sklearn.tree import DecisionTreeRegressor

    tree = DecisionTreeRegressor(max_depth=depth, min_samples_leaf=min_leaf,
                                 random_state=0)
    tree.fit(X, scores)
    return tree


def fit_linear_to_scores(X: np.ndarray, scores: np.ndarray, rows: int = 600_000,
                         seed: int = 0) -> dict[str, float]:
    """Least squares on the ranker's raw scores; returns feature-unit weights."""
    from sklearn.linear_model import LinearRegression

    rng = np.random.default_rng(seed)
    if len(scores) > rows:
        keep = rng.choice(len(scores), rows, replace=False)
        X, scores = X[keep], scores[keep]
    model = LinearRegression().fit(X, scores)
    return dict(zip(STEP_FEATURE_NAMES, (float(v) for v in model.coef_)))


def linear_weights(model, scaler) -> dict[str, float]:
    """Per-unit weights of the fitted logistic scorer, in feature units."""
    w = model.coef_[0] / scaler.scale_
    return dict(zip(STEP_FEATURE_NAMES, (float(v) for v in w)))


def effective_weights(weights: dict[str, float]) -> dict[str, float]:
    """Fold `open_after` into `newly_opened` (they differ by a per-step
    constant) and drop the features constant within a step."""
    return {
        "remaining_degree": weights["remaining_degree"],
        "newly_opened": weights["newly_opened"] + weights["open_after"],
        "already_open": weights["already_open"],
        "total_degree": weights["total_degree"],
    }


def rounded_weights(weights: dict[str, float], places: int = 2) -> dict[str, float]:
    scale = max(abs(v) for v in weights.values()) or 1.0
    return {k: round(v / scale, places) for k, v in weights.items()}


def weights_key(weights: dict[str, float], tie: Sequence[str] = MCN_KEY) -> KeyFn:
    idx = [COL[f] for f in weights]
    w = np.array(list(weights.values()), dtype=np.float64)
    return score_key(lambda F: np.zeros(len(F)), tie) if not idx else _wkey(idx, w, tie)


def _wkey(idx, w, tie):
    tie_idx = [COL[f] for f in tie]

    def key(X: np.ndarray) -> np.ndarray:
        return np.hstack([-(X[:, idx] @ w)[:, None], X[:, tie_idx]])

    return key


def tree_rules_text(tree) -> str:
    """The tree as indented rules, each leaf labelled with the value the
    greedy ranks by: the fraction of training candidates at that leaf the
    witness closed (classifier) or the mean ranker score (regressor).
    `sklearn.tree.export_text` prints the majority class instead, which is 0
    at every leaf here (8.6% positives), and says nothing."""
    t = tree.tree_
    names = STEP_FEATURE_NAMES
    lines: list[str] = []

    def leaf_value(node: int) -> float:
        v = t.value[node]
        if v.shape[-1] == 2:                      # classifier: [neg, pos] counts or fractions
            return float(v[0, 1] / v[0].sum())
        return float(v[0, 0])

    def walk(node: int, depth: int) -> None:
        pad = "|   " * depth
        if t.children_left[node] == -1:
            lines.append(f"{pad}|--- value: {leaf_value(node):.3f}  (rows {int(t.n_node_samples[node]):,})")
            return
        f, thr = names[t.feature[node]], t.threshold[node]
        lines.append(f"{pad}|--- {f} <= {thr:.2f}")
        walk(t.children_left[node], depth + 1)
        lines.append(f"{pad}|--- {f} >  {thr:.2f}")
        walk(t.children_right[node], depth + 1)

    walk(0, 0)
    return "\n".join(lines) + "\n"


def tree_key(tree, tie: Sequence[str] = MCN_KEY) -> KeyFn:
    """Higher leaf value closes first (probability for a classifier, score
    for a regressor); ties, which a depth-3 tree produces constantly, fall
    through to `tie`."""
    if hasattr(tree, "predict_proba"):
        return score_key(lambda F: tree.predict_proba(F.astype(np.float32))[:, 1], tie)
    return score_key(lambda F: tree.predict(F.astype(np.float32)), tie)


# -------------------------------------------------------
# Evaluation
# -------------------------------------------------------

_WORK: dict = {}   # lex rules and models per fold; set in each worker


def _init_worker(work: dict) -> None:
    """Pool initializer: the spawned worker receives the rules and the fitted
    models pickled (see the module docstring on why not `fork`)."""
    _WORK.clear()
    _WORK.update(work)


def _fold_keys(fold: int) -> dict[str, KeyFn]:
    """Key functions of the fitted scorers for one fold, built lazily in the
    worker (a LightGBM booster travels as its string form)."""
    cache = _WORK.setdefault("_keys", {})
    if fold in cache:
        return cache[fold]
    import lightgbm as lgb

    models = _WORK["models"][fold]
    booster = lgb.Booster(model_str=models["lgbm"])
    linear, scaler = models["linear"]
    lgbm_scores = lambda F: booster.predict(F.astype(np.float32), raw_score=True,
                                            num_threads=1)
    lin_scores = lambda F: linear.decision_function(scaler.transform(F.astype(np.float32)))
    keys = {
        "lgbm": score_key(lgbm_scores, tie=("index",)),
        "lgbm+mcn-ties": score_key(lgbm_scores),
        "tree": tree_key(models["tree"]),
        "tree+index-ties": tree_key(models["tree"], tie=("index",)),
        "tree-fid": tree_key(models["tree_fid"]),
        "linear": score_key(lin_scores),
        "linear-r": weights_key(models["linear_r"]),
        "linear-fid": weights_key(effective_weights(models["weights_fid"])),
    }
    cache[fold] = keys
    return keys


def _step_agreement(instance, closing_order, keys: dict[str, KeyFn]
                    ) -> dict[str, int]:
    """Replay the witness; count steps where each key picks what the witness
    picked (`imit:`) and what the ranker picked (`fid:`)."""
    masks = _neighbour_masks(instance)
    n = instance.n_customers
    pmasks = _pattern_masks(instance)
    closed = opened = produced = 0
    counts = {"steps": 0}
    for chosen in closing_order:
        candidates = [c for c in range(n) if masks[c] and not (closed >> c) & 1]
        if len(candidates) > 1:
            X = candidate_matrix(masks, n, pmasks, closed, opened, produced, candidates)
            picks = {name: candidates[pick_min(key(X))] for name, key in keys.items()}
            counts["steps"] += 1
            ref = picks["lgbm"]
            for name, pick in picks.items():
                counts[f"imit:{name}"] = counts.get(f"imit:{name}", 0) + int(pick == chosen)
                counts[f"fid:{name}"] = counts.get(f"fid:{name}", 0) + int(pick == ref)
        opened |= masks[chosen]
        closed |= 1 << chosen
        produced |= pmasks[chosen]
    return counts


def _value(instance: MOSPInstance, order: Sequence[int]) -> int:
    return max_open_stacks(instance, product_order_from_customers(instance, order))


def _evaluate_one(task) -> dict:
    """One instance: every strategy's simulated value (and, for held-out
    instances, the step-level agreement counts)."""
    file, name, instance, optimum, ordering, fold, role = task
    lex_rules = _WORK["lex_rules"]
    out = {"source_file": file, "instance_name": name, "fold": fold, "role": role,
           "n_customers": instance.n_customers, "optimum": optimum}
    for rule in lex_rules:
        out[lex_name(rule)] = _value(instance, greedy_closing_order(instance, lex_key(rule)))
    if role == "test":
        from satisfiability.heuristics import restricted_dfs, upper_bound

        out["mcn-ref"] = upper_bound(instance, "mcn")[0]
        for rname, fn in STATIC_RULES.items():
            out[rname] = _value(instance, fn(instance))
        keys = _fold_keys(fold)
        orders = {kname: greedy_closing_order(instance, key) for kname, key in keys.items()}
        for kname, order in orders.items():
            out[kname] = _value(instance, order)
        dfs_nodes = _WORK.get("dfs_nodes", 0)
        if dfs_nodes:
            out["cs-dfs"] = restricted_dfs(instance, max_nodes=dfs_nodes)[0]
            out["cs-dfs+lgbm"] = restricted_dfs(instance, max_nodes=dfs_nodes,
                                                seed_order=orders["lgbm"])[0]
            rule = greedy_closing_order(instance, lex_key(HYPOTHESES[HYPOTHESIS_RULE]))
            out["cs-dfs+rule"] = restricted_dfs(instance, max_nodes=dfs_nodes,
                                                seed_order=rule)[0]
        witness = _customer_order_from_products(instance, ordering)
        hyp = {name: lex_key(rule) for name, rule in HYPOTHESES.items()}
        agree = _step_agreement(instance, witness, {**keys, "mcn": lex_key([]), **hyp})
        out.update({f"agree:{k}": v for k, v in agree.items()})
    return out


def _blocks(corpus, folds: int, seed: int) -> list[set[str]]:
    files = sorted({f for f, _, _ in corpus})
    rng = random.Random(seed)
    rng.shuffle(files)
    return [set(files[i::folds]) for i in range(folds)]


def run(folds: int = 5, per_fold: int = 400, seed: int = 2, workers: int = 16,
        lex_depth: int = 3, dfs_nodes: int = 200_000, verbose: bool = True
        ) -> tuple[pd.DataFrame, dict]:
    """Fit per fold, evaluate held out, return (per-instance frame, models)."""
    corpus = _corpus()
    blocks = _blocks(corpus, folds, seed)
    rng = random.Random(seed)
    lex_rules = lex_family(lex_depth)
    _WORK["lex_rules"] = lex_rules
    _WORK["models"] = {}
    tasks = []
    fit_seconds = 0.0
    for fold, held in enumerate(blocks, start=1):
        train_set = [row for row in corpus if row[0] not in held]
        test_set = [row for row in corpus if row[0] in held]
        rng.shuffle(test_set)
        test_set = test_set[:per_fold]
        train_sample = list(train_set)
        rng.shuffle(train_sample)
        train_sample = train_sample[:per_fold]

        started = time.time()
        booster, n_rows = _fit(train_set)
        X, y = decision_rows(train_set)
        tree = fit_tree(X, y)
        linear, scaler = fit_linear(X, y, seed=seed)
        weights = linear_weights(linear, scaler)
        scores = booster.predict(X, raw_score=True)
        tree_fid = fit_tree_to_scores(X, scores)
        weights_fid = fit_linear_to_scores(X, scores, seed=seed)
        _WORK["models"][fold] = {
            "lgbm": booster.model_to_string(),
            "tree": tree,
            "tree_fid": tree_fid,
            "linear": (linear, scaler),
            "weights": weights,
            "weights_fid": weights_fid,
            "linear_r": rounded_weights(effective_weights(weights)),
            "tree_text": tree_rules_text(tree),
            "tree_fid_text": tree_rules_text(tree_fid),
            "rows": n_rows,
            "train_witnesses": len(train_set),
        }
        fit_seconds += time.time() - started
        if verbose:
            print(f"  fold {fold}/{folds}: {len(train_set)} witnesses, {n_rows:,} rows, "
                  f"fitted in {time.time() - started:.0f}s; {len(test_set)} held out",
                  flush=True)
        tasks += [(f, inst.name, inst, int(sol["mosp_value"]), sol["ordering"], fold, "test")
                  for f, inst, sol in test_set]
        tasks += [(f, inst.name, inst, int(sol["mosp_value"]), sol["ordering"], fold, "train")
                  for f, inst, sol in train_sample]

    started = time.time()
    work = {"lex_rules": lex_rules, "models": _WORK["models"], "dfs_nodes": dfs_nodes}
    with multiprocessing.get_context("spawn").Pool(
            workers, initializer=_init_worker, initargs=(work,)) as pool:
        rows = pool.map(_evaluate_one, tasks, chunksize=4)
    if verbose:
        print(f"  {len(tasks)} instance evaluations x {len(lex_rules) + 15} strategies "
              f"in {time.time() - started:.0f}s on {workers} workers", flush=True)
    frame = pd.DataFrame(rows)
    meta = {"models": _WORK["models"], "lex_rules": lex_rules, "folds": folds,
            "per_fold": per_fold, "seed": seed, "fit_seconds": fit_seconds,
            "dfs_nodes": dfs_nodes,
            "eval_seconds": time.time() - started, "corpus": len(corpus)}
    return frame, meta


# -------------------------------------------------------
# Tables
# -------------------------------------------------------

def summary(frame: pd.DataFrame, strategies: Sequence[str]) -> pd.DataFrame:
    """MAE / exact / worst over the optimum, and the share of the ranker's
    gain over MCN each strategy keeps."""
    test = frame[frame["role"] == "test"]
    truth = test["optimum"].to_numpy()
    mae = {s: float(np.abs(test[s].to_numpy() - truth).mean()) for s in strategies}
    base, top = mae["mcn"], mae["lgbm"]
    rows = []
    for s in strategies:
        err = test[s].to_numpy() - truth
        rows.append({"strategy": s, "mae": mae[s], "exact": float((err == 0).mean()),
                     "worst": int(err.max()),
                     "gain_kept": gain_kept(mae[s], base, top)})
    return pd.DataFrame(rows)


def gain_kept(mae: float, mae_mcn: float, mae_lgbm: float) -> float:
    if mae_mcn == mae_lgbm:
        return float("nan")
    return (mae_mcn - mae) / (mae_mcn - mae_lgbm)


def by_band(frame: pd.DataFrame, strategies: Sequence[str]) -> pd.DataFrame:
    test = frame[frame["role"] == "test"]
    rows = []
    for lo, hi in SIZE_BANDS:
        sub = test[(test["n_customers"] >= lo) & (test["n_customers"] <= hi)]
        if sub.empty:
            continue
        truth = sub["optimum"].to_numpy()
        row = {"band": f"{lo}-{hi}", "instances": len(sub)}
        for s in strategies:
            row[s] = float(np.abs(sub[s].to_numpy() - truth).mean())
        rows.append(row)
    return pd.DataFrame(rows)


def by_collection(frame: pd.DataFrame, strategies: Sequence[str]) -> pd.DataFrame:
    """MAE over the optimum per benchmark collection (the directory above the
    source file), held-out instances only."""
    test = frame[frame["role"] == "test"]
    coll = test["source_file"].str.split("/").str[-2]
    rows = []
    for name, sub in test.groupby(coll):
        truth = sub["optimum"].to_numpy()
        row = {"collection": name, "instances": len(sub)}
        for s in strategies:
            row[s] = float(np.abs(sub[s].to_numpy() - truth).mean())
        rows.append(row)
    return pd.DataFrame(rows)


def head_to_head(frame: pd.DataFrame, pairs: Sequence[tuple[str, str]]) -> pd.DataFrame:
    """Held-out instances on which the first strategy's value is below, equal
    to and above the second's."""
    test = frame[frame["role"] == "test"]
    rows = []
    for a, b in pairs:
        rows.append({"first": a, "second": b,
                     "first better": int((test[a] < test[b]).sum()),
                     "equal": int((test[a] == test[b]).sum()),
                     "first worse": int((test[a] > test[b]).sum())})
    return pd.DataFrame(rows)


def agreement(frame: pd.DataFrame) -> pd.DataFrame:
    test = frame[frame["role"] == "test"]
    steps = test["agree:steps"].sum()
    names = sorted({c.split(":", 2)[2] for c in test.columns if c.startswith("agree:imit:")})
    rows = [{"strategy": s,
             "imitation": float(test[f"agree:imit:{s}"].sum() / steps),
             "fidelity": float(test[f"agree:fid:{s}"].sum() / steps)} for s in names]
    return pd.DataFrame(rows).sort_values("imitation", ascending=False)


def select_lex(frame: pd.DataFrame, lex_rules) -> pd.DataFrame:
    """Per fold: the rule with the lowest MAE on the training sample, and
    what it scores held out. The pooled held-out row is `lex-selected`."""
    names = [lex_name(r) for r in lex_rules]
    rows = []
    for fold, sub in frame.groupby("fold"):
        train = sub[sub["role"] == "train"]
        test = sub[sub["role"] == "test"]
        t_truth = train["optimum"].to_numpy()
        train_mae = {s: float(np.abs(train[s].to_numpy() - t_truth).mean()) for s in names}
        best = min(names, key=lambda s: (train_mae[s], s))
        h_truth = test["optimum"].to_numpy()
        rows.append({"fold": fold, "rule": best, "train_mae": train_mae[best],
                     "held_out_mae": float(np.abs(test[best].to_numpy() - h_truth).mean()),
                     "held_out_mcn": float(np.abs(test["mcn"].to_numpy() - h_truth).mean()),
                     "held_out_lgbm": float(np.abs(test["lgbm"].to_numpy() - h_truth).mean())})
    return pd.DataFrame(rows)


def add_selected(frame: pd.DataFrame, selection: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    chosen = dict(zip(selection["fold"], selection["rule"]))
    frame["lex-selected"] = [row[chosen[f]] for f, (_, row) in
                             zip(frame["fold"], frame.iterrows())]
    return frame


def lex_table(frame: pd.DataFrame, lex_rules, top: int = 15) -> pd.DataFrame:
    """Every lexicographic rule over the pooled held-out sample (descriptive:
    this table is what selection looks at, so its best row is optimistic)."""
    names = [lex_name(r) for r in lex_rules]
    table = summary(frame, ["mcn", "lgbm"] + [s for s in names if s != "mcn"])
    return table.sort_values(["mae", "strategy"]).head(top + 2)


def _md(frame: pd.DataFrame, floats: int = 3) -> str:
    cols = list(frame.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, row in frame.iterrows():
        cells = []
        for c in cols:
            v = row[c]
            if isinstance(v, float):
                cells.append("nan" if np.isnan(v) else f"{v:.{floats}f}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(frame: pd.DataFrame, meta: dict, out: Path = DEFAULT_OUT) -> None:
    lex_rules = meta["lex_rules"]
    selection = select_lex(frame, lex_rules)
    frame = add_selected(frame, selection)
    models = meta["models"]
    main = ["mcn", "lgbm", "lgbm+mcn-ties", "tree", "tree+index-ties", "tree-fid",
            "linear", "linear-r", "linear-fid", "lex-selected"] + list(HYPOTHESES) \
        + list(STATIC_RULES)
    dfs_cols = [c for c in ("cs-dfs", "cs-dfs+lgbm", "cs-dfs+rule") if c in frame.columns]
    main += dfs_cols
    test = frame[frame["role"] == "test"]
    test_n = int(len(test))
    mcn_disagree = int((test["mcn"] != test["mcn-ref"]).sum())

    lines = [f"# Distilling the closing policy — regenerated tables\n",
             f"`python -m learning.distil --folds {meta['folds']} --per-fold "
             f"{meta['per_fold']}`; {meta['corpus']} certified witnesses, {test_n} held-out "
             f"instances, fits {meta['fit_seconds']:.0f} s, evaluation "
             f"{meta['eval_seconds']:.0f} s. The `mcn` construction here and "
             f"`satisfiability.heuristics.upper_bound(instance, 'mcn')` disagree on "
             f"{mcn_disagree} of {test_n} held-out instances.\n",
             "## Held-out constructions over the optimum\n", _md(summary(frame, main)),
             "\n## MAE by size band\n", _md(by_band(frame, main)),
             "\n## MAE by collection\n",
             _md(by_collection(frame, ["mcn", "lgbm", *HYPOTHESES, "linear", "fiedler"] + dfs_cols)),
             "\n## Head to head, held out\n",
             _md(head_to_head(frame, [(HYPOTHESIS_RULE, "lgbm"), (HYPOTHESIS_RULE, "mcn"),
                                      (HYPOTHESIS_RULE, "lex:min newly_opened"),
                                      ("lex-selected", "lgbm"), ("linear", "lgbm"),
                                      ("tree", "lgbm"), ("fiedler", "lgbm")]
                              + ([(HYPOTHESIS_RULE, "cs-dfs"), ("cs-dfs+rule", "cs-dfs+lgbm"),
                                  ("cs-dfs+rule", "cs-dfs"), ("cs-dfs+lgbm", "cs-dfs")]
                                 if dfs_cols else []))),
             "\n## Step-level agreement with the witness and with the ranker\n",
             _md(agreement(frame)),
             "\n## Lexicographic rule selected per fold on training instances\n",
             _md(selection),
             "\n## Every lexicographic rule, pooled held out (descriptive; top 15)\n",
             _md(lex_table(frame, lex_rules))]
    lines.append("\n## The fitted linear scorer, per fold (feature units, higher closes first)\n")
    wrows = []
    for fold, m in models.items():
        row = {"fold": fold}
        row.update({k: round(v, 3) for k, v in effective_weights(m["weights"]).items()})
        row["rounded"] = " ".join(f"{v:+.2f}·{k}" for k, v in m["linear_r"].items())
        wrows.append(row)
    lines.append(_md(pd.DataFrame(wrows)))
    lines.append("\nFull coefficients including the per-step constants:\n")
    lines.append(_md(pd.DataFrame([{"fold": f, **{k: round(v, 3) for k, v in m["weights"].items()}}
                                   for f, m in models.items()])))
    lines.append("\n## The linear scorer fitted to the ranker's scores (`linear-fid`), per fold\n")
    lines.append(_md(pd.DataFrame([{"fold": f, **{k: round(v, 3) for k, v in
                                    effective_weights(m["weights_fid"]).items()}}
                                   for f, m in models.items()])))
    lines.append("\n## The depth-3 tree of fold 1 (leaf value = probability the candidate closes next)\n")
    lines.append("```\n" + models[1]["tree_text"] + "```")
    for f, m in models.items():
        if f != 1:
            lines.append(f"\n<details><summary>fold {f}</summary>\n\n```\n{m['tree_text']}```\n</details>")
    lines.append("\n## The depth-3 tree of fold 1 fitted to the ranker's scores (`tree-fid`)\n")
    lines.append("```\n" + models[1]["tree_fid_text"] + "```")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(DATA_OUT, index=False)
    print(f"wrote {out} and {DATA_OUT}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--per-fold", type=int, default=400)
    parser.add_argument("--seed", type=int, default=2)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--lex-depth", type=int, default=3)
    parser.add_argument("--dfs-nodes", type=int, default=200_000,
                        help="node budget of the cs-dfs reference columns; 0 skips them")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    os.environ.setdefault("OMP_NUM_THREADS", str(args.workers))
    warnings.filterwarnings("ignore")
    frame, meta = run(folds=args.folds, per_fold=args.per_fold, seed=args.seed,
                      workers=args.workers, lex_depth=args.lex_depth,
                      dfs_nodes=args.dfs_nodes)
    write_report(frame, meta, args.out)
    print(_md(summary(add_selected(frame, select_lex(frame, meta["lex_rules"])),
                      ["mcn", "lgbm", "tree", "tree-fid", "linear", "linear-r",
                       "linear-fid", "lex-selected", *HYPOTHESES, "fiedler",
                       "cuthill-mckee", "elim-min-degree"]
                      + [c for c in ("cs-dfs", "cs-dfs+lgbm", "cs-dfs+rule")
                         if c in frame.columns])))


if __name__ == "__main__":
    main()
