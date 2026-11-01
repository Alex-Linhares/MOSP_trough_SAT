#!/usr/bin/env python3
"""`beta+` on paper (loop0010 item 07): the two recursions of `learning.beta_plus`
against item 05's simulation at every cell, `n = 100-5000`.

1. The layer lemma, checked on 1,000 random graphs before it is stated.
2. Every accepted instance of `learning/data/excess_constructions.csv` is
   regenerated from its seed (nothing solved): the BFS layers are rebuilt with
   item 05's random choices (the layer bound is asserted equal to the recorded
   one), the exploration recursion is run from the observed state at the first
   layer of `>= max(10, n / 500)` customers and compared with the observed
   layers; the phase-free limit (`sup`, `inf` over the phase) is computed from
   the instance's degree and size histograms; the pattern-count and random
   greedies are simulated and compared with their differential-equation
   yields; item 05's min-degree greedy is read from the csv.
3. The same on fresh instances of the *unpadded* uniform model (the model the
   recursions describe; the generators pad), 5 per cell at `n = 1000, 5000`.
4. The tables: the comparison per cell, and `beta+(d, mu) = min(beta+_BFS,
   1 - alpha+_pc)` on the uniform model beside `beta*`, item 02's `b`, item
   05's rule and min-degree greedy.

Usage (from the repository root, about 5 minutes on 8 workers):
    nice -n 19 python3 reports/scratch/beta_plus/recursion.py [--workers 8] [--quick]
Outputs: `instances.csv`, `pure.csv`, `tables.md`, `run.log` beside this file.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from learning import beta_plus as bp  # noqa: E402
from learning import excess_constructions as ec  # noqa: E402
from learning.excess import _map, default_workers  # noqa: E402
from learning.first_moment import beta_star  # noqa: E402

LOG = HERE / "run.log"


def log(msg: str) -> None:
    print(msg, flush=True)
    with LOG.open("a") as f:
        f.write(msg + "\n")


def analyse(matrix: np.ndarray, seed: int, alpha_min_degree: float | None, generator_mu_d: tuple | None = None) -> dict:
    """Everything the item compares, on one matrix."""
    a = np.asarray(matrix, dtype=np.int8)
    n, m = a.shape
    out: dict = {"n": n, "m": m, "n_ones": int(a.sum())}
    adj = ec.mosp_adjacency(a)
    t = time.perf_counter()
    comps = bp.bfs_components(adj, np.random.default_rng(seed))
    out["bfs_layer_bound"] = bp.layer_layout_bound(comps)
    out["bfs_components"] = len(comps)
    largest = max(comps, key=lambda ls: sum(len(x) for x in ls))
    out["largest_fraction"] = sum(len(x) for x in largest) / n
    out["observed_layer_max"] = bp.layer_max([len(x) / n for x in largest])
    state = bp.bfs_state(a, comps, min_layer=max(10, n // 500))
    if state is None:
        out.update(i0=-1, predicted_layer_max=np.nan, layers_predicted=0, layer_rel_err=np.nan, layer_rmse=np.nan)
    else:
        pred = bp.bfs_recursion(state["deg_unreached"], state["sizes_unrevealed"], state["slots_layer"],
                                deg_unreached=state["deg_unreached"], sizes_unrevealed=state["sizes_unrevealed"])
        series = state["observed_before"] + pred
        out["i0"] = state["i0"]
        out["predicted_layer_max"] = bp.layer_max(series)
        obs_after = state["observed_after"]
        k = min(len(obs_after), len(pred))
        out["layers_predicted"] = k
        out["layer_rel_err"] = (out["predicted_layer_max"] - out["observed_layer_max"]) / out["observed_layer_max"]
        out["layer_rmse"] = float(np.sqrt(np.mean((np.array(obs_after[:k]) - np.array(pred[:k])) ** 2))) if k else np.nan
        out["observed_layers"] = ";".join(f"{x:.5f}" for x in state["observed_before"] + obs_after)
        out["predicted_layers"] = ";".join(f"{x:.5f}" for x in series[: len(state["observed_before"]) + k])
    out["bfs_seconds"] = time.perf_counter() - t
    deg, sizes = bp.degree_and_size_histograms(a)
    t = time.perf_counter()
    scan = bp.bfs_phase_scan(deg, sizes)
    out.update(phase_sup=scan["sup"], phase_inf=scan["inf"], phase_mean=scan["mean"], rho=scan["rho"])
    out["phase_seconds"] = time.perf_counter() - t
    out["observed_in_phase_band"] = scan["inf"] <= out["observed_layer_max"] <= scan["sup"]
    if generator_mu_d is not None:
        pad = bp.padded_phase_scan(generator_mu_d[0], generator_mu_d[1])
        out.update(padded_sup=pad["sup"], padded_inf=pad["inf"], padded_mean=pad["mean"])
        out["observed_in_padded_band"] = pad["inf"] <= out["observed_layer_max"] <= pad["sup"]
    else:
        out.update(padded_sup=np.nan, padded_inf=np.nan, padded_mean=np.nan, observed_in_padded_band=False)
    rng = np.random.default_rng(seed + 1)
    for policy in ("pattern_count", "random"):
        t = time.perf_counter()
        alpha, chosen = bp.greedy_simulation(a, policy, rng)
        assert bp.is_independent(a, chosen)
        out[f"{policy}_sim"] = alpha / n
        out[f"{policy}_sim_seconds"] = time.perf_counter() - t
        t = time.perf_counter()
        out[f"{policy}_ode"] = bp.greedy_ode(deg, sizes, policy)["alpha"]
        out[f"{policy}_ode_seconds"] = time.perf_counter() - t
        out[f"{policy}_rel_err"] = (out[f"{policy}_ode"] - out[f"{policy}_sim"]) / out[f"{policy}_sim"]
    out["min_degree_sim"] = alpha_min_degree / n if alpha_min_degree is not None else np.nan
    out["deg_hist"] = ";".join(f"{k}:{v:.6f}" for k, v in sorted(deg.items()))
    out["size_hist"] = ";".join(f"{s}:{v:.6f}" for s, v in sorted(sizes.items()))
    return out


def _job(row: dict) -> dict:
    gen, n, mu, d, seed = row["generator"], int(row["n"]), float(row["mu"]), int(row["d"]), int(row["seed"])
    t = time.perf_counter()
    if gen == "fixed":
        matrix, tries = ec.draw_fixed(n, mu, d, seed)
    else:
        matrix, tries = ec.draw_fitted(n, mu, d, seed, ec.FITTED_CAP.get(n, 10))
    assert matrix is not None and tries == int(row["tries"]), (gen, n, mu, d, tries, row["tries"])
    assert int(matrix.sum()) == int(row["n_ones"]), "regenerated instance differs from item 05's record"
    out = {"generator": gen, "n": n, "mu": mu, "d": d, "index": int(row["index"]), "seed": seed, "draw_seconds": time.perf_counter() - t}
    out.update(analyse(matrix, seed, float(row["alpha_greedy"]), (mu, d) if gen == "fixed" else None))
    assert out["bfs_layer_bound"] == int(row["bfs_layer_bound"]), "the rebuilt BFS layout differs from item 05's"
    out["seconds"] = time.perf_counter() - t
    return out


def _pure_job(args) -> dict:
    mu, d, n, index = args
    seed = 7_070_000 + (n * 3 + {0.5: 0, 1.0: 1, 2.0: 2}[mu]) * 16 + d * 10 + index
    rng = np.random.default_rng(seed)
    m = int(round(mu * n))
    matrix = np.zeros((n, m), dtype=np.int8)
    for j in range(m):
        matrix[rng.choice(n, size=d, replace=False), j] = 1
    t = time.perf_counter()
    alpha_md = ec.greedy_independent_set(ec.mosp_adjacency(matrix))
    out = {"generator": "pure", "n": n, "mu": mu, "d": d, "index": index, "seed": seed}
    out.update(analyse(matrix, seed, float(alpha_md)))
    out["seconds"] = time.perf_counter() - t
    return out


def _fmt(x, nd=3):
    return "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}"


def tables(inst: pd.DataFrame, pure: pd.DataFrame, lemma: dict) -> str:
    cell05 = ec.cell_table(ec.load())
    cell05 = cell05.set_index(["generator", "mu", "d"])
    lines = [f"Layer lemma: {lemma['checked']} random graphs, 0 violations, tight on {lemma['tight']}.", ""]
    # ---- comparison per cell at the largest n, both generators and the pure model
    lines += ["### The recursions against simulation, per cell at the largest `n` (per customer)", "",
              "| generator | mu | d | n | inst. | layer bound observed | phase-matched prediction | rel. err. median | rel. err. max abs | phase band [inf, sup] | in band | padded band (fixed gen.) | in band | pc greedy sim | pc ODE | rel. err. | random sim | random ODE | rel. err. | min-degree sim (item 05) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    both = pd.concat([inst, pure], ignore_index=True)
    for (gen, mu, d), g in both.groupby(["generator", "mu", "d"]):
        nmax = g["n"].max()
        h = g[g["n"] == nmax]
        lb = (h["bfs_layer_bound"] / h["n"]).mean()
        lines.append(f"| {gen} | {mu} | {d} | {nmax} | {len(h)} | {lb:.3f} | {_fmt(h['predicted_layer_max'].mean())} | "
                     f"{_fmt(h['layer_rel_err'].median())} | {_fmt(h['layer_rel_err'].abs().max())} | "
                     f"[{h['phase_inf'].mean():.3f}, {h['phase_sup'].mean():.3f}] | {int(h['observed_in_phase_band'].sum())}/{len(h)} | "
                     + (f"[{h['padded_inf'].mean():.3f}, {h['padded_sup'].mean():.3f}] | {int(h['observed_in_padded_band'].sum())}/{len(h)} | " if gen == "fixed" else "— | — | ")
                     +                      f"{h['pattern_count_sim'].mean():.4f} | {h['pattern_count_ode'].mean():.4f} | {h['pattern_count_rel_err'].median():+.4f} | "
                     f"{h['random_sim'].mean():.4f} | {h['random_ode'].mean():.4f} | {h['random_rel_err'].median():+.4f} | {_fmt(h['min_degree_sim'].mean(), 4)} |")
    # ---- error by n, pooled
    lines += ["", "### Relative error by `n`, pooled over cells (median and max |.|)", "",
              "| generator | n | cells | layer max: median | max abs | pc greedy: median | max abs | random: median | max abs |", "|---|---|---|---|---|---|---|---|---|"]
    for (gen, n), g in both.groupby(["generator", "n"]):
        lines.append(f"| {gen} | {n} | {g.groupby(['mu', 'd']).ngroups} | {_fmt(g['layer_rel_err'].median())} | {_fmt(g['layer_rel_err'].abs().max())} | "
                     f"{g['pattern_count_rel_err'].median():+.4f} | {g['pattern_count_rel_err'].abs().max():.4f} | "
                     f"{g['random_rel_err'].median():+.4f} | {g['random_rel_err'].abs().max():.4f} |")
    # ---- the beta+ table on the uniform model
    lines += ["", "### `beta+(d, mu)` from the analysed constructions (uniform model), beside `beta*`, `b`, item 05", "",
              "| mu | d | e | rho | beta+_BFS (sup over phase) | inf over phase | 1 - alpha+ pattern-count | 1 - alpha+ random (closed form) | **beta+ = min** | beta* | beta+ - beta* | b certified (item 02) | rule beta+ (item 05) | rule trusted | n - alpha_mindeg beta+ (item 05) | kill (> 0.5) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    rows = []
    for mu in ec.GRID_MU:
        for d in ec.GRID_D:
            deg, sizes = bp.uniform_model_histograms(mu, d)
            scan = bp.bfs_phase_scan(deg, sizes)
            pc = bp.greedy_ode(deg, sizes, "pattern_count")["alpha"]
            rg = bp.random_greedy_uniform(mu, d)
            bplus = min(scan["sup"], 1 - pc)
            bstar = beta_star(mu, {d: 1})
            key = ("fixed", mu, d)
            c = cell05.loc[key] if key in cell05.index else None
            b = c["b (certified, n <= 100)"] if c is not None else np.nan
            rule = c["rule beta+"] if c is not None else np.nan
            trusted = bool(c["trusted"]) if c is not None else False
            nma = c["n_minus_alpha beta+"] if c is not None else np.nan
            gap = bplus - bstar
            rows.append({"mu": mu, "d": d, "e": mu * (d - 1), "rho": scan["rho"], "beta_bfs_sup": scan["sup"], "beta_bfs_inf": scan["inf"],
                         "beta_pc": 1 - pc, "beta_random": 1 - rg, "beta_plus": bplus, "beta_star": bstar, "gap": gap,
                         "b": b, "rule_beta_plus": rule, "rule_trusted": trusted, "n_minus_alpha_beta_plus": nma})
            lines.append(f"| {mu} | {d} | {mu * (d - 1):.1f} | {scan['rho']:.0f} | {scan['sup']:.3f} | {scan['inf']:.3f} | {1 - pc:.3f} | {1 - rg:.3f} | **{bplus:.3f}** | {bstar:.3f} | {gap:.3f} | "
                         f"{_fmt(b)} | {_fmt(rule)} | {'yes' if trusted else 'no'} | {_fmt(nma)} | {'met' if gap > 0.5 else 'not met'} |")
    bt = pd.DataFrame(rows)
    bt.to_csv(HERE / "beta_plus_table.csv", index=False)
    n_cells = len(bt)
    n_over = int((bt["gap"] > 0.5).sum())
    lines += ["", f"Kill: `beta+ - beta* > 0.5` on {n_over} of {n_cells} cells; below 0.5 on {n_cells - n_over}; "
              f"smallest gap {bt['gap'].min():.3f} at (d, mu) = ({int(bt.loc[bt['gap'].idxmin(), 'd'])}, {bt.loc[bt['gap'].idxmin(), 'mu']}); "
              f"largest {bt['gap'].max():.3f}.", ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=default_workers())
    ap.add_argument("--quick", action="store_true", help="n <= 500 only, for a smoke test")
    args = ap.parse_args()
    LOG.write_text("")
    started = time.time()
    log(f"# item 07 recursion check, {time.strftime('%Y-%m-%d %H:%M')}, workers {args.workers}, load {os.getloadavg()[0]:.1f}")
    lemma = bp.layer_lemma_check(1000, np.random.default_rng(2026))
    log(f"layer lemma: {lemma}")
    frame = ec.load()
    frame = frame[frame["accepted"]].copy()
    if args.quick:
        frame = frame[frame["n"] <= 500]
    jobs = frame.to_dict("records")
    jobs.sort(key=lambda r: (-r["n"], -r["d"]))
    log(f"regenerating {len(jobs)} item 05 instances")
    rows = _map(_job, jobs, args.workers)
    inst = pd.DataFrame(rows)
    inst.to_csv(HERE / "instances.csv", index=False)
    log(f"item 05 instances: {len(inst)} rows, {inst['seconds'].sum():.0f} s of instance time, {time.time() - started:.0f} s wall")
    ns = (1000,) if args.quick else (1000, 5000)
    pure_jobs = [(mu, d, n, i) for n in ns for mu in ec.GRID_MU for d in ec.GRID_D for i in range(5)]
    rows = _map(_pure_job, pure_jobs, args.workers)
    pure = pd.DataFrame(rows)
    pure.to_csv(HERE / "pure.csv", index=False)
    log(f"pure model: {len(pure)} rows, {pure['seconds'].sum():.0f} s, {time.time() - started:.0f} s wall")
    text = tables(inst, pure, lemma)
    (HERE / "tables.md").write_text(text + "\n")
    log(text)
    log(f"done in {time.time() - started:.0f} s wall")


if __name__ == "__main__":
    main()
