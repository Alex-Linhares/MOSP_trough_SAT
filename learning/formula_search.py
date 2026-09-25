"""A formula for the residual, and for the optimum (plan §2.2b).

`reports/ml_nature.md` §4 found that structure and the pathwidth-adjacent
invariants predict the optimum as well as the solver's bounds do, and that no
invariant explains the residual `optimum - lb_best` beyond what the bound
already knows. Both findings came out of a gradient-boosting model, which
predicts and explains nothing. This study asks whether a *closed-form* formula
in the structure-only features does the same job, for two targets:

- the residual `optimum - lb_best`, which is what the bound work would want a
  conjecture about;
- the optimum itself, compared against `tw_min_fill + 1`, the best point
  estimate §4 found, and against `lb_best` and `ub_best`.

Two searches, the first of them the one every number in the report rests on:

1. **Enumerated monomials.** Every product and ratio of at most three features
   from the pool, `f1^e1 · f2^e2 · f3^e3` with exponents in {-2, -1, -1/2,
   1/2, 1, 2} for one feature, {-1, -1/2, 1/2, 1, 2} for two, {-1, 1} for
   three (a negative exponent only on a strictly positive column). Each term
   `t` is scored as the two-parameter fit `y ≈ a·t + b`, the constants fitted
   on the training folds and the error measured on the held-out folds of a
   grouped split: least squares as the first pass over every term, then least
   absolute deviation for the leading few hundred, since MAE is the metric
   and the target's tail pulls a least-squares line off the bulk. A second stage fits `y ≈ a·t1 + b·t2 + c`
   over all pairs of the leading monomials. About 10^5 terms; a minute on 16
   cores.
2. **PySR** (soft import; `pip install pysr`, which bootstraps Julia on first
   use) with the same operators plus `sqrt`, `square` and `log`, on a held-out
   fifth of the files, so its Pareto front can be read beside the enumerated
   winner and the boosting baseline on the same rows. Each PySR fit runs in a
   child process (`--pysr-child`, internal): Julia's garbage collector aborts
   a process that has forked a `multiprocessing` pool, which the enumerated
   search does, and a child that dies costs one row rather than the run.
   The tables above it are written to `--out` before PySR starts.

Every split groups: by `source_file`, by file ∪ MOSP-graph isomorphism class
(`learning.fingerprint.union_groups`, §1), and random for contrast. Because the
enumerated search *selects* a term by its grouped cross-validation error, that
error is optimistic; a nested protocol (select on the training groups only,
score on the held-out group) is reported beside it and is the honest number.
The baseline the item names is LightGBM on the same pool, grouped
(`HistGradientBoostingRegressor` if lightgbm is absent).

**Nothing here is a bound.** A formula that sits at or under the optimum on
every instance of this corpus is a conjecture at most, and the tables count
how often each formula falls below and above the optimum precisely so that
nobody mistakes a fit for a proof. Nothing reaches `satisfiability.mosp_solver`.

Usage:
    python -m learning.dataset                             # if the table is stale (~90 s)
    python -m learning.formula_search --out reports/formula_tables.md
    python -m learning.formula_search --no-pysr --no-nested   # the quick version
"""

from __future__ import annotations

import argparse
import itertools
import multiprocessing
import os
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from learning.dataset import DEFAULT_OUT, feature_columns
from learning.features import invariant_names
from learning.fingerprint import CANONICAL_CSV, load_table, union_groups
from learning.study_optimum import BOUND_PREFIXES, _scores

TREEWIDTH = ("tw_min_fill", "tw_min_degree")
SIZE_BANDS = ((1, 30), (31, 60), (61, 200))
EXPONENTS = {
    1: (-2.0, -1.0, -0.5, 0.5, 1.0, 2.0),
    2: (-1.0, -0.5, 0.5, 1.0, 2.0),
    3: (-1.0, 1.0),
}
TOP_FOR_PAIRS = 150
CHUNK = 1500

Term = tuple[tuple[str, float], ...]


# ----------------------------------------------------------------------------
# pools, targets, splits
# ----------------------------------------------------------------------------


def pools(frame: pd.DataFrame) -> dict[str, list[str]]:
    """The feature pools: the structure columns (minus `g_nodes`, which equals
    `n_customers` on every row) plus the invariants without the two treewidth
    heuristics, and the same with them. `lb_*`, `ub_*` and `bound_*` are never
    candidates."""
    inv = [c for c in invariant_names() if c in frame.columns]
    cols = [c for c in feature_columns(frame) if c not in ("graph_cert", "bipartite_cert")]
    bounds = [c for c in cols if c.startswith(BOUND_PREFIXES)]
    structure = [c for c in cols if c not in bounds and c not in inv and c != "g_nodes"]
    base = structure + [c for c in inv if c not in TREEWIDTH]
    return {
        "structure": base,
        "structure + treewidth heuristics": base + [c for c in inv if c in TREEWIDTH],
    }


def targets(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    optimum = frame["optimum"].to_numpy(dtype=float)
    return {
        "optimum": optimum,
        "optimum − lb_best": optimum - frame["lb_best"].to_numpy(dtype=float),
    }


def group_ids(frame: pd.DataFrame) -> dict[str, np.ndarray | None]:
    splits: dict[str, np.ndarray | None] = {
        "grouped by file": frame["source_file"].to_numpy(),
    }
    if "graph_cert" in frame.columns and frame["graph_cert"].notna().any():
        splits["grouped by file ∪ class"] = union_groups(frame["source_file"], frame["graph_cert"])
    splits["random (leaks!)"] = None
    return splits


def folds_of(groups: np.ndarray | None, n: int, n_splits: int = 5, seed: int = 0):
    """(train_mask, test_mask) pairs; GroupKFold when groups are given."""
    from sklearn.model_selection import GroupKFold, KFold

    if groups is None:
        splitter = KFold(n_splits=n_splits, shuffle=True, random_state=seed).split(np.zeros(n))
    else:
        splitter = GroupKFold(n_splits=n_splits).split(np.zeros(n), groups=groups)
    out = []
    for train, test in splitter:
        tr = np.zeros(n, dtype=bool)
        te = np.zeros(n, dtype=bool)
        tr[train] = True
        te[test] = True
        out.append((tr, te))
    return out


def holdout_mask(files: pd.Series) -> np.ndarray:
    """Every fifth file in sorted order is held out (the protocol of
    `learning.invariants_study.importances`)."""
    held = set(sorted(files.unique())[::5])
    return files.isin(held).to_numpy()


# ----------------------------------------------------------------------------
# terms
# ----------------------------------------------------------------------------


def format_term(term: Term) -> str:
    """`(('a', 1.0), ('b', 0.5), ('c', -1.0))` -> `a · sqrt(b) / c`."""
    def factor(name: str, e: float) -> str:
        e = abs(e)
        if e == 1.0:
            return name
        if e == 0.5:
            return f"sqrt({name})"
        if e == 2.0:
            return f"{name}²"
        return f"{name}^{e:g}"

    num = [factor(f, e) for f, e in term if e > 0]
    den = [factor(f, e) for f, e in term if e < 0]
    text = " · ".join(num) if num else "1"
    if den:
        text += " / " + (den[0] if len(den) == 1 else "(" + " · ".join(den) + ")")
    return text


def enumerate_terms(columns: list[str], positive: set[str], max_degree: int = 3) -> list[Term]:
    """All monomials of at most `max_degree` distinct features with the
    exponent sets of `EXPONENTS`; a negative exponent only on a column that
    is strictly positive everywhere."""
    terms: list[Term] = []
    for degree in range(1, max_degree + 1):
        exps = EXPONENTS[degree]
        for combo in itertools.combinations(columns, degree):
            for es in itertools.product(exps, repeat=degree):
                if any(e < 0 and f not in positive for f, e in zip(combo, es)):
                    continue
                terms.append(tuple(zip(combo, es)))
    return terms


def evaluate_terms(values: dict[str, np.ndarray], terms: list[Term]) -> np.ndarray:
    """Matrix of term values, one row per term."""
    n = len(next(iter(values.values())))
    out = np.ones((len(terms), n), dtype=float)
    for i, term in enumerate(terms):
        for f, e in term:
            out[i] *= values[f] ** e
    return out


# ----------------------------------------------------------------------------
# the two-parameter fit, cross-validated, vectorised over terms
# ----------------------------------------------------------------------------


def ols_cv(T: np.ndarray, y: np.ndarray, folds) -> tuple[np.ndarray, np.ndarray]:
    """For every row `t` of `T`, fit `y ≈ a·t + b` on each training fold and
    predict the test fold; returns the pooled held-out (MAE, exact-rate) per
    term. Terms with non-finite values or zero variance score infinite."""
    n = T.shape[1]
    bad = ~np.isfinite(T).all(axis=1)
    T = np.where(np.isfinite(T), T, 0.0)
    abs_err = np.zeros(T.shape[0])
    exact = np.zeros(T.shape[0])
    for train, test in folds:
        Ttr = T[:, train]
        ytr = y[train]
        mx = Ttr.mean(axis=1, keepdims=True)
        my = ytr.mean()
        dx = Ttr - mx
        var = (dx * dx).sum(axis=1)
        cov = (dx * (ytr - my)).sum(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            a = np.where(var > 0, cov / var, 0.0)
        b = my - a * mx[:, 0]
        pred = a[:, None] * T[:, test] + b[:, None]
        err = pred - y[test]
        abs_err += np.abs(err).sum(axis=1)
        exact += (np.abs(err) <= 0.5).sum(axis=1)
    mae = abs_err / n
    mae[bad] = np.inf
    return mae, exact / n


def fit_term(t: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """`y ≈ a·t + b` on all rows."""
    dx = t - t.mean()
    var = float((dx * dx).sum())
    a = float((dx * (y - y.mean())).sum() / var) if var > 0 else 0.0
    return a, float(y.mean() - a * t.mean())


def lad_cv(T: np.ndarray, y: np.ndarray, folds, iters: int = 40, eps: float = 1e-3) -> tuple[np.ndarray, np.ndarray]:
    """As `ols_cv`, with the constants of `y ≈ a·t + b` fitted by least
    absolute deviation (iteratively reweighted least squares from the OLS
    start). MAE is the reported metric, so this is the fit that matters; OLS
    is only the cheap first pass over 10^5 terms."""
    n = T.shape[1]
    T = np.where(np.isfinite(T), T, 0.0)
    abs_err = np.zeros(T.shape[0])
    exact = np.zeros(T.shape[0])
    for train, test in folds:
        a, b = _lad_fit_rows(T[:, train], y[train], iters, eps)
        err = a[:, None] * T[:, test] + b[:, None] - y[test]
        abs_err += np.abs(err).sum(axis=1)
        exact += (np.abs(err) <= 0.5).sum(axis=1)
    return abs_err / n, exact / n


def _lad_fit_rows(T: np.ndarray, y: np.ndarray, iters: int, eps: float) -> tuple[np.ndarray, np.ndarray]:
    """LAD constants for every row of `T`, vectorised IRLS."""
    w = np.ones_like(T)
    a = np.zeros(T.shape[0])
    b = np.zeros(T.shape[0])
    for _ in range(iters):
        sw = w.sum(axis=1)
        mx = (w * T).sum(axis=1) / sw
        my = (w * y).sum(axis=1) / sw
        dx = T - mx[:, None]
        var = (w * dx * dx).sum(axis=1)
        cov = (w * dx * (y - my[:, None])).sum(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            a = np.where(var > 0, cov / var, 0.0)
        b = my - a * mx
        w = 1.0 / np.maximum(np.abs(a[:, None] * T + b[:, None] - y), eps)
    return a, b


def fit_term_lad(t: np.ndarray, y: np.ndarray, iters: int = 40, eps: float = 1e-3) -> tuple[float, float]:
    """`y ≈ a·t + b` on all rows, least absolute deviation."""
    a, b = _lad_fit_rows(t[None, :], y, iters, eps)
    return float(a[0]), float(b[0])


def _lad_fit_linear(X: np.ndarray, y: np.ndarray, iters: int = 40, eps: float = 1e-3) -> np.ndarray:
    """LAD coefficients of `y ≈ X·coef` by IRLS (small X only)."""
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    for _ in range(iters):
        w = 1.0 / np.maximum(np.abs(X @ coef - y), eps)
        Xw = X * w[:, None]
        coef = np.linalg.solve(X.T @ Xw + 1e-12 * np.eye(X.shape[1]), Xw.T @ y)
    return coef


_SHARED: dict = {}


def _init_worker(values, y, folds):
    _SHARED["values"] = values
    _SHARED["y"] = y
    _SHARED["folds"] = folds


def _score_chunk(args):
    terms, keep = args
    T = evaluate_terms(_SHARED["values"], terms)
    mae, exact = ols_cv(T, _SHARED["y"], _SHARED["folds"])
    order = np.argsort(mae)[:keep]
    return [(terms[i], float(mae[i]), float(exact[i])) for i in order]


def search(
    values: dict[str, np.ndarray], y: np.ndarray, folds, columns: list[str],
    max_degree: int = 3, keep: int = 400, workers: int | None = None,
) -> tuple[pd.DataFrame, int]:
    """Stage 1: every monomial of the pool scored by `ols_cv`; the best `keep`
    re-scored with LAD constants (`lad_cv`), ranked by that, and returned with
    the whole-corpus LAD constants attached. `mae_ols`/`exact_ols` keep the
    first-pass scores."""
    positive = {c for c in columns if (values[c] > 0).all()}
    terms = enumerate_terms(columns, positive, max_degree)
    chunks = [(terms[i:i + CHUNK], keep) for i in range(0, len(terms), CHUNK)]
    workers = workers or max(1, min(16, multiprocessing.cpu_count() // 2))
    if workers > 1 and len(chunks) > 1:
        with multiprocessing.Pool(workers, initializer=_init_worker,
                                  initargs=(values, y, folds)) as pool:
            parts = pool.map(_score_chunk, chunks)
    else:
        _init_worker(values, y, folds)
        parts = [_score_chunk(c) for c in chunks]
    rows = sorted((r for part in parts for r in part), key=lambda r: r[1])[:keep]
    top_terms = [r[0] for r in rows]
    T = evaluate_terms(values, top_terms)
    mae_lad, exact_lad = lad_cv(T, y, folds)
    table = []
    for k, (term, mae, exact) in enumerate(rows):
        a, b = fit_term_lad(T[k], y)
        table.append({"formula": format_term(term), "degree": len(term), "mae_ols": mae,
                      "exact_ols": exact, "mae": float(mae_lad[k]), "exact": float(exact_lad[k]),
                      "a": a, "b": b, "term": term})
    table = pd.DataFrame(table).sort_values("mae", kind="stable").reset_index(drop=True)
    return table, len(terms)


# ----------------------------------------------------------------------------
# stage 2: pairs of leading monomials, y ≈ a·t1 + b·t2 + c
# ----------------------------------------------------------------------------


def pair_search(
    values: dict[str, np.ndarray], y: np.ndarray, folds, terms: list[Term], keep: int = 50,
) -> pd.DataFrame:
    """Every pair of the given terms as a three-parameter linear fit, scored
    on the held-out folds; terms are standardised on the training fold so the
    normal equations are well conditioned whatever their scale. The best
    `keep` pairs by OLS are refitted by LAD and ranked by that."""
    T = evaluate_terms(values, terms)
    good = np.isfinite(T).all(axis=1) & (T.std(axis=1) > 0)
    idx = np.flatnonzero(good)
    pairs = np.array(list(itertools.combinations(idx, 2)))
    if len(pairs) == 0:
        return pd.DataFrame(columns=["formula", "mae", "exact", "coef", "terms"])
    n = T.shape[1]
    abs_err = np.zeros(len(pairs))
    exact = np.zeros(len(pairs))
    for train, test in folds:
        mu = T[:, train].mean(axis=1, keepdims=True)
        sd = T[:, train].std(axis=1, keepdims=True)
        sd[sd == 0] = 1.0
        Z = (T - mu) / sd
        Ztr, Zte = Z[:, train], Z[:, test]
        ytr = y[train]
        my = ytr.mean()
        G = Ztr @ Ztr.T                      # k x k gram of centred-ish terms
        s = Ztr.sum(axis=1)
        sy = Ztr @ (ytr - my)
        ntr = int(train.sum())
        i, j = pairs[:, 0], pairs[:, 1]
        A = np.empty((len(pairs), 3, 3))
        A[:, 0, 0] = G[i, i]; A[:, 0, 1] = G[i, j]; A[:, 0, 2] = s[i]
        A[:, 1, 0] = G[i, j]; A[:, 1, 1] = G[j, j]; A[:, 1, 2] = s[j]
        A[:, 2, 0] = s[i];    A[:, 2, 1] = s[j];    A[:, 2, 2] = ntr
        rhs = np.stack([sy[i], sy[j], np.zeros(len(pairs))], axis=1)
        A[:, 0, 0] += 1e-9; A[:, 1, 1] += 1e-9
        coef = np.linalg.solve(A, rhs[..., None])[..., 0]
        pred = coef[:, 0:1] * Zte[i] + coef[:, 1:2] * Zte[j] + coef[:, 2:3] + my
        err = pred - y[test]
        abs_err += np.abs(err).sum(axis=1)
        exact += (np.abs(err) <= 0.5).sum(axis=1)
    mae = abs_err / n
    order = np.argsort(mae)[:keep]
    rows = []
    for k in order:
        i, j = pairs[k]
        X = np.stack([T[i], T[j], np.ones(n)], axis=1)
        err = np.zeros(n)
        for train, test in folds:
            c = _lad_fit_linear(X[train], y[train])
            err[test] = X[test] @ c - y[test]
        coef = _lad_fit_linear(X, y)
        rows.append({
            "formula": f"{coef[0]:+.4g} · [{format_term(terms[i])}] {coef[1]:+.4g} · [{format_term(terms[j])}] {coef[2]:+.4g}",
            "mae_ols": float(mae[k]), "exact_ols": float(exact[k] / n),
            "mae": float(np.abs(err).mean()), "exact": float((np.abs(err) <= 0.5).mean()),
            "coef": tuple(float(c) for c in coef), "terms": (terms[i], terms[j]),
        })
    return pd.DataFrame(rows).sort_values("mae", kind="stable").reset_index(drop=True)


def predict_pair(values, terms: tuple[Term, Term], coef) -> np.ndarray:
    T = evaluate_terms(values, list(terms))
    return coef[0] * T[0] + coef[1] * T[1] + coef[2]


# ----------------------------------------------------------------------------
# nested protocol: select on the training groups, score on the held-out group
# ----------------------------------------------------------------------------


def nested(
    values: dict[str, np.ndarray], y: np.ndarray, groups: np.ndarray, columns: list[str],
    max_degree: int = 3, n_splits: int = 5, workers: int | None = None,
) -> dict:
    """Outer GroupKFold; in each outer fold the whole search (stage 1 and 2)
    runs on the training rows with inner grouped folds, the winner is fitted
    on those rows and predicts the held-out rows. Returns the pooled scores
    of the best monomial and of the best pair, and the winners per fold."""
    n = len(y)
    pred_mono = np.zeros(n)
    pred_pair = np.zeros(n)
    winners = []
    for train, test in folds_of(groups, n, n_splits):
        sub = {c: v[train] for c, v in values.items()}
        inner = folds_of(groups[train], int(train.sum()), n_splits)
        table, _ = search(sub, y[train], inner, columns, max_degree, keep=TOP_FOR_PAIRS, workers=workers)
        best = table.iloc[0]
        t_all = evaluate_terms(values, [best["term"]])[0]
        a, b = fit_term_lad(t_all[train], y[train])
        pred_mono[test] = a * t_all[test] + b
        pairs = pair_search(sub, y[train], inner, list(table["term"]), keep=20)
        p = pairs.iloc[0]
        T2 = evaluate_terms(values, list(p["terms"]))
        X = np.stack([T2[0][train], T2[1][train], np.ones(int(train.sum()))], axis=1)
        coef = _lad_fit_linear(X, y[train])
        pred_pair[test] = coef[0] * T2[0][test] + coef[1] * T2[1][test] + coef[2]
        winners.append({"monomial": best["formula"], "inner_mae": float(best["mae"]),
                        "pair": p["formula"], "pair_inner_mae": float(p["mae"])})
    return {"monomial": _scores(pred_mono, y), "pair": _scores(pred_pair, y),
            "pred_monomial": pred_mono, "pred_pair": pred_pair, "winners": winners}


# ----------------------------------------------------------------------------
# baselines: boosting on the same pool, and the solver's own numbers
# ----------------------------------------------------------------------------


def _boosting(seed: int):
    try:
        from lightgbm import LGBMRegressor
        return LGBMRegressor(n_estimators=400, learning_rate=0.05, num_leaves=31,
                             random_state=seed, verbose=-1, n_jobs=4), "LightGBM"
    except ImportError:  # pragma: no cover
        from sklearn.ensemble import HistGradientBoostingRegressor
        return HistGradientBoostingRegressor(random_state=seed, max_iter=300), "HistGradientBoosting"


def boosting_cv(frame: pd.DataFrame, columns: list[str], y: np.ndarray, folds, seed: int = 0) -> np.ndarray:
    pred = np.zeros(len(y))
    X = frame[columns].to_numpy(dtype=float)
    for train, test in folds:
        model, _ = _boosting(seed)
        model.fit(X[train], y[train])
        pred[test] = model.predict(X[test])
    return pred


# ----------------------------------------------------------------------------
# PySR
# ----------------------------------------------------------------------------


def pysr_available() -> bool:
    try:
        import pysr  # noqa: F401
        return True
    except ImportError:
        return False


def pysr_search(X: np.ndarray, y: np.ndarray, names: list[str], seconds: int,
                seed: int = 0, threads: int = 16, niterations: int = 10_000):
    """A PySR run bounded by wall-clock; returns the fitted regressor. Call it
    only through `pysr_front`, which runs it in a child process: Julia must
    never share a process with a `multiprocessing` fork pool (the enumerated
    search forks one), or its garbage collector aborts the interpreter."""
    os.environ.setdefault("PYTHON_JULIACALL_THREADS", str(threads))
    os.environ.setdefault("PYTHON_JULIACALL_HANDLE_SIGNALS", "yes")
    from pysr import PySRRegressor

    model = PySRRegressor(
        niterations=niterations, timeout_in_seconds=seconds,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["sqrt", "square", "log"],
        maxsize=20, populations=24, elementwise_loss="L1DistLoss()",
        parallelism="multithreading", random_state=seed,
        progress=False, verbosity=0, temp_equation_file=True, delete_tempfiles=True,
    )
    model.fit(X, y, variable_names=names)
    return model


def pysr_front(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, names: list[str],
               seconds: int, seed: int = 0, threads: int = 16, niterations: int = 10_000) -> list[dict]:
    """Fit PySR in a fresh child process and return its Pareto front: one dict
    per equation with `complexity`, `train_loss`, `equation`, `chosen` (PySR's
    own pick) and `pred`, the equation evaluated on `X_test`. A child that
    dies takes only its own row with it."""
    import json
    import subprocess
    import sys
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        inp = Path(tmp) / "in.npz"
        out = Path(tmp) / "out.json"
        np.savez(inp, X_train=X_train, y_train=y_train, X_test=X_test,
                 names=np.array(names), seconds=seconds, seed=seed, threads=threads,
                 niterations=niterations)
        proc = subprocess.run([sys.executable, "-m", "learning.formula_search",
                               "--pysr-child", str(inp), str(out)],
                              capture_output=True, text=True, timeout=max(600, 4 * seconds))
        if proc.returncode != 0 or not out.exists():
            tail = (proc.stderr or proc.stdout).strip().splitlines()[-3:]
            raise RuntimeError(f"PySR child exited {proc.returncode}: {' | '.join(tail)}")
        rows = json.loads(out.read_text())
    for row in rows:
        row["pred"] = np.asarray(row["pred"], dtype=float)
    return rows


def _pysr_child(inp: Path, out: Path) -> None:
    """Entry point of the child process behind `pysr_front`."""
    import json

    data = np.load(inp, allow_pickle=False)
    names = [str(c) for c in data["names"]]
    if len(data["y_train"]) < 2 or not np.isfinite(data["X_train"]).all():
        raise ValueError("PySR needs at least two finite training rows")   # before Julia boots
    reg = pysr_search(data["X_train"], data["y_train"], names, int(data["seconds"]),
                      int(data["seed"]), int(data["threads"]), int(data["niterations"]))
    eqs = reg.equations_
    best_i = int(reg.get_best().name)
    rows = []
    for i, row in eqs.iterrows():
        pred = np.asarray(reg.predict(data["X_test"], index=i), dtype=float)
        rows.append({"complexity": int(row["complexity"]), "train_loss": float(row["loss"]),
                     "equation": str(row["equation"]), "chosen": bool(i == best_i),
                     "pred": [float(v) for v in pred]})
    out.write_text(json.dumps(rows))


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def band_of(n: pd.Series) -> pd.Series:
    labels = [f"{lo}-{hi}" for lo, hi in SIZE_BANDS]
    return pd.cut(n, [0] + [hi for _, hi in SIZE_BANDS], labels=labels)


def by_band(frame: pd.DataFrame, preds: dict[str, np.ndarray], truth: np.ndarray) -> pd.DataFrame:
    bands = band_of(frame["n_customers"])
    rows = []
    for band in bands.cat.categories:
        mask = (bands == band).to_numpy()
        if not mask.any():
            continue
        for name, pred in preds.items():
            rows.append({"band": band, "instances": int(mask.sum()), "estimate": name,
                         **_scores(pred[mask], truth[mask])})
    return pd.DataFrame(rows)


def by_collection(frame: pd.DataFrame, preds: dict[str, np.ndarray], truth: np.ndarray) -> pd.DataFrame:
    rows = []
    for coll, idx in frame.groupby("collection").indices.items():
        for name, pred in preds.items():
            rows.append({"collection": coll, "instances": len(idx), "estimate": name,
                         "mae": _scores(pred[idx], truth[idx])["mae"],
                         "exact": _scores(pred[idx], truth[idx])["exact"]})
    return pd.DataFrame(rows)


def bound_check(pred: np.ndarray, optimum: np.ndarray) -> dict[str, float]:
    """How often a rounded estimate of the optimum sits below/above it; a
    valid lower bound would have `above = 0`."""
    r = np.round(pred)
    return {"below": int((r < optimum).sum()), "above": int((r > optimum).sum()),
            "max_below": float((optimum - r).max()), "max_above": float((r - optimum).max())}


SANDWICH_CANDIDATES = {
    "g_degeneracy + 1": lambda f: f["g_degeneracy"] + 1,
    "bw_rcm + 1": lambda f: f["bw_rcm"] + 1,
    "1 + sqrt(g_degeneracy · bw_rcm)": lambda f: 1 + np.sqrt(f["g_degeneracy"] * f["bw_rcm"]),
    "1 + (g_degeneracy + bw_rcm) / 2": lambda f: 1 + (f["g_degeneracy"] + f["bw_rcm"]) / 2,
    "tw_min_fill + 1": lambda f: f["tw_min_fill"] + 1,
    "lb_best": lambda f: f["lb_best"],
}


def sandwich_table(frame: pd.DataFrame) -> dict:
    """The two invariants the searches keep returning, with their constants
    fixed by hand rather than fitted. Degeneracy ≤ treewidth ≤ pathwidth, so
    `g_degeneracy + 1` is a valid lower bound on the optimum; bandwidth ≥
    pathwidth, so `bw_rcm + 1` is a valid upper bound; the corpus is checked
    against both. Between them the optimum is `g_degeneracy + 1 + λ ·
    (bw_rcm − g_degeneracy)` for some λ in [0, 1], and the table reports the
    distribution of that λ where the two differ, the candidate point
    estimates with no fitted constant (whole-corpus and per size band), and
    the gap `optimum − lb_best` on degree-regular graphs (`g_deg_std == 0`).
    Nothing here is fitted, so there is nothing to hold out."""
    optimum = frame["optimum"].to_numpy(dtype=float)
    d = frame["g_degeneracy"].to_numpy(dtype=float)
    bw = frame["bw_rcm"].to_numpy(dtype=float)
    bands = band_of(frame["n_customers"])
    rows = []
    for name, fn in SANDWICH_CANDIDATES.items():
        if not all(c in frame.columns for c in ("g_degeneracy", "bw_rcm", "tw_min_fill", "lb_best")):
            continue
        pred = np.asarray(fn(frame), dtype=float)
        row = {"estimate": name, **_scores(pred, optimum), **bound_check(pred, optimum)}
        for band in bands.cat.categories:
            mask = (bands == band).to_numpy()
            if mask.any():
                row[f"mae {band}"] = _scores(pred[mask], optimum[mask])["mae"]
                row[f"exact {band}"] = _scores(pred[mask], optimum[mask])["exact"]
        rows.append(row)
    differ = bw > d
    lam = (optimum[differ] - 1 - d[differ]) / (bw[differ] - d[differ])
    forced = int((bw == d).sum())
    regular = frame["g_deg_std"].to_numpy(dtype=float) == 0
    gap = optimum - frame["lb_best"].to_numpy(dtype=float)
    checks = {
        "instances": int(len(frame)),
        "g_degeneracy + 1 > optimum (must be 0)": int((d + 1 > optimum).sum()),
        "bw_rcm + 1 < optimum (must be 0)": int((bw + 1 < optimum).sum()),
        "bw_rcm == g_degeneracy (optimum forced)": forced,
        "of those with optimum == g_degeneracy + 1": int(((bw == d) & (optimum == d + 1)).sum()),
        "bw_rcm > g_degeneracy": int(differ.sum()),
        "λ quantiles 10/25/50/75/90": " / ".join(f"{q:.3f}" for q in np.quantile(lam, [0.1, 0.25, 0.5, 0.75, 0.9])),
        "λ mean": round(float(lam.mean()), 3),
        "degree-regular graphs (g_deg_std == 0)": int(regular.sum()),
        "of those complete (g_density == 1)": int((regular & (frame["g_density"].to_numpy(dtype=float) >= 1 - 1e-12)).sum()),
        "max gap optimum − lb_best on regular graphs": float(gap[regular].max()) if regular.any() else float("nan"),
        "mean gap on the rest": round(float(gap[~regular].mean()), 3) if (~regular).any() else float("nan"),
    }
    lam_by_band = []
    for band in bands.cat.categories:
        mask = ((bands == band).to_numpy())[differ]
        if mask.any():
            lam_by_band.append({"band": band, "instances": int(mask.sum()),
                                "λ median": float(np.median(lam[mask])), "λ mean": float(lam[mask].mean())})
    return {"table": pd.DataFrame(rows), "checks": checks, "lambda_by_band": pd.DataFrame(lam_by_band)}


def _md(table: pd.DataFrame, floatfmt: str = ".3f") -> str:
    return table.to_markdown(index=False, floatfmt=floatfmt)


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--data", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--canonical", type=Path, default=CANONICAL_CSV)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--max-degree", type=int, default=3)
    parser.add_argument("--no-nested", action="store_true")
    parser.add_argument("--no-pysr", action="store_true")
    parser.add_argument("--pysr-iterations", type=int, default=2000,
                        help="PySR search length; the wall-clock stop crashes Julia here")
    parser.add_argument("--pysr-threads", type=int, default=4,
                        help="Julia threads per PySR fit; 16 crashes its GC on most runs here")
    parser.add_argument("--pysr-seconds", type=int, default=3600,
                        help="fallback wall-clock cap per PySR fit (its stop path is unsafe)")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--pysr-child", nargs=2, type=Path, metavar=("IN_NPZ", "OUT_JSON"),
                        help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.pysr_child:
        _pysr_child(*args.pysr_child)
        return

    warnings.filterwarnings("ignore")
    started = time.time()
    frame = load_table(args.data, args.canonical)
    the_pools = pools(frame)
    the_targets = targets(frame)
    splits = group_ids(frame)
    n = len(frame)
    values_all = {c: frame[c].to_numpy(dtype=float) for c in the_pools["structure + treewidth heuristics"]}
    optimum = frame["optimum"].to_numpy(dtype=float)
    lb = frame["lb_best"].to_numpy(dtype=float)
    lines: list[str] = []

    def emit(text: str = "") -> None:
        print(text, flush=True)
        lines.append(text)

    def flush() -> None:
        if args.out:
            args.out.write_text("\n".join(lines) + "\n")

    nc = frame["n_customers"]
    emit(f"{n} instances, {frame['source_file'].nunique()} files; n_customers "
         f"{int(nc.min())}-{int(nc.max())}, {int((nc <= 30).sum())} at n <= 30; pools: "
         + ", ".join(f"{k} ({len(v)})" for k, v in the_pools.items())
         + f"; splits: {', '.join(splits)}; boosting: {_boosting(0)[1]}")
    emit()

    # -- 1. the search under each split, each target, each pool ----------------
    chosen: dict[tuple[str, str], dict] = {}
    summary_rows = []
    for tname, y in the_targets.items():
        for pname, columns in the_pools.items():
            if tname == "optimum − lb_best" and pname != "structure":
                continue   # §4: the treewidth heuristics track the bound, not the gap
            values = {c: values_all[c] for c in columns}
            for sname, groups in splits.items():
                folds = folds_of(groups, n, args.folds, args.seed)
                t0 = time.time()
                table, n_terms = search(values, y, folds, columns, args.max_degree,
                                        keep=TOP_FOR_PAIRS, workers=args.workers)
                pairs = pair_search(values, y, folds, list(table["term"]), keep=20)
                boost = boosting_cv(frame, columns, y, folds, args.seed)
                best = table.iloc[0]
                bp = pairs.iloc[0]
                summary_rows.append({
                    "target": tname, "pool": pname, "split": sname, "terms": n_terms,
                    "best monomial": best["formula"], "mae": best["mae"], "exact": best["exact"],
                    "best pair mae": bp["mae"], "pair exact": bp["exact"],
                    "boosting mae": _scores(boost, y)["mae"], "boosting exact": _scores(boost, y)["exact"],
                    "seconds": time.time() - t0,
                })
                if sname == "grouped by file":
                    chosen[(tname, pname)] = {"table": table, "pairs": pairs, "boost": boost,
                                              "folds": folds, "columns": columns, "values": values}
                print(f"  [{tname} | {pname} | {sname}] {n_terms} terms, "
                      f"best {best['formula']} mae {best['mae']:.3f}, pair {bp['mae']:.3f}, "
                      f"boosting {_scores(boost, y)['mae']:.3f} ({time.time() - t0:.0f} s)", flush=True)

    emit("## The searches: best monomial, best pair, boosting on the same pool\n")
    emit("`mae`/`exact` are pooled held-out errors of the two-parameter fit "
         "`y ≈ a·t + b` under the split, constants by least absolute deviation; "
         "the term itself was selected by that error, so these are optimistic "
         "(see the nested table).\n")
    emit(_md(pd.DataFrame(summary_rows)))
    emit()

    # -- 2. the leading formulas per target (grouped by file) -----------------
    for (tname, pname), c in chosen.items():
        emit(f"## Leading monomials — target `{tname}`, pool `{pname}`, grouped by file\n")
        top = c["table"].head(15).copy()
        top["fit on all rows (LAD)"] = [f"{a:+.4g} · t {b:+.3g}" for a, b in zip(top["a"], top["b"])]
        emit("`mae`/`exact`: LAD constants; `mae_ols`/`exact_ols`: the least-squares first pass.\n")
        emit(_md(top[["formula", "degree", "mae", "exact", "mae_ols", "exact_ols", "fit on all rows (LAD)"]], ".4f"))
        emit()
        emit(f"### Leading pairs — target `{tname}`, pool `{pname}`\n")
        emit(_md(c["pairs"].head(8)[["formula", "mae", "exact", "mae_ols"]], ".4f"))
        emit()

    # -- 3. baselines and the chosen formulas as point estimates ------------
    emit("## Point estimates of the optimum: baselines and the chosen formulas\n")
    emit("Formulas here are cross-validated predictions grouped by file "
         "(constants refitted per fold); the residual formula is added to "
         "`lb_best`. `below`/`above` count rounded estimates under/over the "
         "optimum; a valid lower bound would have `above = 0`.\n")
    preds_opt: dict[str, np.ndarray] = {
        "lb_best": lb, "ub_best": frame["ub_best"].to_numpy(dtype=float),
        "tw_min_fill + 1": frame["tw_min_fill"].to_numpy(dtype=float) + 1,
        "lb_best + 0 (no residual)": lb,
    }
    for (tname, pname), c in chosen.items():
        y = the_targets[tname]
        best = c["table"].iloc[0]
        t = evaluate_terms(c["values"], [best["term"]])[0]
        pred = np.zeros(n)
        for train, test in c["folds"]:
            a, b = fit_term_lad(t[train], y[train])
            pred[test] = a * t[test] + b
        pred_pair = np.zeros(n)
        bp = c["pairs"].iloc[0]
        T2 = evaluate_terms(c["values"], list(bp["terms"]))
        for train, test in c["folds"]:
            X = np.stack([T2[0][train], T2[1][train], np.ones(int(train.sum()))], axis=1)
            coef = _lad_fit_linear(X, y[train])
            pred_pair[test] = coef[0] * T2[0][test] + coef[1] * T2[1][test] + coef[2]
        offset = lb if tname.startswith("optimum −") else 0.0
        short = "structure" if pname == "structure" else "structure+tw"
        preds_opt[f"formula[{tname}; {short}]"] = pred + offset
        preds_opt[f"pair[{tname}; {short}]"] = pred_pair + offset
        preds_opt[f"boosting[{tname}; {short}]"] = c["boost"] + offset
    rows = []
    for name, pred in preds_opt.items():
        rows.append({"estimate": name, **_scores(pred, optimum),
                     "mae_rounded": float(np.abs(np.round(pred) - optimum).mean()),
                     **bound_check(pred, optimum)})
    emit(_md(pd.DataFrame(rows)))
    emit()

    emit("### By size band (grouped by file, target optimum)\n")
    emit(_md(by_band(frame, preds_opt, optimum)))
    emit()
    emit("### By collection (grouped by file, target optimum)\n")
    emit(_md(by_collection(frame, preds_opt, optimum)))
    emit()

    # -- 3b. the sandwich: the two invariants with their constants fixed by hand
    emit("## The sandwich: degeneracy + 1 ≤ optimum ≤ bandwidth + 1, constants fixed by hand\n")
    emit("Both searches keep returning `g_degeneracy` and `bw_rcm`. Degeneracy ≤ "
         "treewidth ≤ pathwidth and bandwidth ≥ pathwidth, so `g_degeneracy + 1` "
         "is a proved lower bound on the optimum and `bw_rcm + 1` a proved upper "
         "bound (both checked on every row). The optimum is "
         "`g_degeneracy + 1 + λ · (bw_rcm − g_degeneracy)` for some λ in [0, 1]; "
         "nothing below is fitted, so there is nothing to hold out.\n")
    sandwich = sandwich_table(frame)
    emit(_md(sandwich["table"]))
    emit()
    emit(_md(pd.DataFrame([{"check": k, "value": v} for k, v in sandwich["checks"].items()]), ".3f"))
    emit()
    emit("λ where `bw_rcm > g_degeneracy`, by size band:\n")
    emit(_md(sandwich["lambda_by_band"]))
    emit()

    # -- 4. nested ------------------------------------------------------------
    if not args.no_nested:
        emit("## Nested protocol: the formula selected on the training files only\n")
        emit("Outer GroupKFold by file; the whole search runs inside each training "
             "fold and its winner is scored on the held-out files. These are the "
             "honest grouped errors; the winners per fold show whether one "
             "formula keeps being chosen.\n")
        rows = []
        winners = []
        for (tname, pname), c in chosen.items():
            t0 = time.time()
            y = the_targets[tname]
            res = nested(c["values"], y, splits["grouped by file"], c["columns"],
                         args.max_degree, args.folds, args.workers)
            rows.append({"target": tname, "pool": pname, "estimate": "best monomial",
                         **res["monomial"], "seconds": time.time() - t0})
            rows.append({"target": tname, "pool": pname, "estimate": "best pair", **res["pair"]})
            rows.append({"target": tname, "pool": pname, "estimate": "boosting",
                         **_scores(c["boost"], y)})
            for k, w in enumerate(res["winners"]):
                winners.append({"target": tname, "pool": pname, "fold": k, **w})
            print(f"  nested [{tname} | {pname}] mono {res['monomial']['mae']:.3f} "
                  f"pair {res['pair']['mae']:.3f} ({time.time() - t0:.0f} s)", flush=True)
        emit(_md(pd.DataFrame(rows)))
        emit()
        emit("### Winners per outer fold\n")
        emit(_md(pd.DataFrame(winners), ".4f"))
        emit()

    flush()   # everything above survives a PySR failure

    # -- 5. PySR on a held-out fifth of the files -----------------------------
    if not args.no_pysr:
        emit("## PySR on a held-out fifth of the files\n")
        if not pysr_available():
            emit("`pysr` is not installed; skipped (`pip install pysr`).")
            emit()
        else:
            test = holdout_mask(frame["source_file"])
            train = ~test
            emit(f"Train {int(train.sum())} instances / test {int(test.sum())} instances "
                 f"({frame['source_file'][test].nunique()} files held out). "
                 f"{args.pysr_iterations} iterations of search per row on {args.pysr_threads} "
                 "Julia threads, `L1DistLoss`, operators "
                 "`+ - * /`, `sqrt`, `square`, `log`, maxsize 20. The enumerated "
                 "monomial and pair are selected by grouped CV on the training rows "
                 "only; boosting is fitted on the same rows.\n")
            rows = []
            fronts = []
            for (tname, pname), c in chosen.items():
                y = the_targets[tname]
                columns = c["columns"]
                sub = {col: values_all[col][train] for col in columns}
                inner = folds_of(frame["source_file"].to_numpy()[train], int(train.sum()), args.folds)
                table, _ = search(sub, y[train], inner, columns, args.max_degree,
                                  keep=TOP_FOR_PAIRS, workers=args.workers)
                best = table.iloc[0]
                t_all = evaluate_terms(values_all, [best["term"]])[0]
                a, b = fit_term_lad(t_all[train], y[train])
                rows.append({"target": tname, "pool": pname, "method": "best monomial (enumerated)",
                             "formula": best["formula"], **_scores(a * t_all[test] + b, y[test])})
                pairs = pair_search(sub, y[train], inner, list(table["term"]), keep=20)
                p = pairs.iloc[0]
                T2 = evaluate_terms(values_all, list(p["terms"]))
                X = np.stack([T2[0][train], T2[1][train], np.ones(int(train.sum()))], axis=1)
                coef = _lad_fit_linear(X, y[train])
                rows.append({"target": tname, "pool": pname, "method": "best pair (enumerated)",
                             "formula": p["formula"],
                             **_scores(coef[0] * T2[0][test] + coef[1] * T2[1][test] + coef[2], y[test])})
                model, _ = _boosting(args.seed)
                X_all = frame[columns].to_numpy(dtype=float)
                model.fit(X_all[train], y[train])
                rows.append({"target": tname, "pool": pname, "method": "boosting",
                             "formula": "", **_scores(model.predict(X_all[test]), y[test])})
                t0 = time.time()
                try:
                    for attempt in (1, 2):
                        try:
                            front = pysr_front(X_all[train], y[train], X_all[test], columns,
                                               args.pysr_seconds, args.seed, threads=args.pysr_threads,
                                               niterations=args.pysr_iterations)
                            break
                        except RuntimeError as exc:
                            if attempt == 2:
                                raise
                            print(f"  pysr [{tname} | {pname}] attempt 1 failed ({str(exc)[:80]}), retrying", flush=True)
                    for eq in front:
                        sc = _scores(eq["pred"], y[test])
                        fronts.append({"target": tname, "pool": pname, "complexity": eq["complexity"],
                                       "train_loss": eq["train_loss"], "equation": eq["equation"],
                                       **sc, "chosen": "*" if eq["chosen"] else ""})
                        if eq["chosen"]:
                            rows.append({"target": tname, "pool": pname, "method": "PySR (its own pick)",
                                         "formula": eq["equation"], **sc})
                    best_eq = min(front, key=lambda eq: _scores(eq["pred"], y[test])["mae"])
                    rows.append({"target": tname, "pool": pname, "method": "PySR (best on held-out)",
                                 "formula": best_eq["equation"], **_scores(best_eq["pred"], y[test])})
                    print(f"  pysr [{tname} | {pname}] done in {time.time() - t0:.0f} s", flush=True)
                except Exception as exc:  # pragma: no cover - Julia is a moving target
                    rows.append({"target": tname, "pool": pname, "method": "PySR",
                                 "formula": f"failed: {exc}"[:160], "mae": np.nan, "rmse": np.nan,
                                 "exact": np.nan, "over": np.nan})
                    print(f"  pysr [{tname} | {pname}] failed: {exc}", flush=True)
            emit(_md(pd.DataFrame(rows)))
            emit()
            if fronts:
                emit("### PySR Pareto fronts, scored on the held-out files\n")
                emit(_md(pd.DataFrame(fronts), ".4f"))
                emit()

    emit(f"_{time.time() - started:.0f} s total._")
    flush()
    if args.out:
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
