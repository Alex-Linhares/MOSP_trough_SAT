"""loop0010 item 10: validity of the first-moment floor under the real generator.

Every lemma of `reports/excess_phase_diagram.md` §10 is checked here by brute
force before it is stated. Stages (each appends to `check.log`):

    exact     (a): the Bernoulli avoid probability is the binomial average of the
              uniform one, exactly in rationals (n <= 12); the pair probability,
              the cut bound and the repair bound against full enumeration of
              every base matrix at m x n = 2 x 6 and 3 x 4.
    law       the explicit-randomness generator has the law of
              `gen_candidates.bern_padC1_padP2_conn` (statistics on 4,000 draws).
    coupling  (b), (c) at n = 8, m = 8, d in {2, 4}, 10,000 draws each, both pad
              orders: M >= B and M <= M+ in every draw; every empty pair of G_M
              is empty in G_B; pw(G_B) <= pw(G_M); the repair map is not
              monotone (counted over every single-entry increase of the base);
              M+ is; Monte Carlo of P(pw(G_M) <= k | accepted) against the
              rigorous forms.
    classes   P(accepted), P(M+ connected), P(no repair), P(repair and accepted)
              on the 40 Chu & Stuckey classes at p = d / n, both pad orders
              (`classes.csv`; 8 workers, nice 19).
    table     the floors per class: measured model (realised sizes) beside the
              rigorous ones (`floors.csv`, `tables.md`).

    nice -n 19 python3 reports/scratch/validity/check.py {exact,law,coupling,classes,table,all}
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from learning import first_moment as fm  # noqa: E402

HERE = Path(__file__).resolve().parent
LOG = HERE / "check.log"
SOLUTIONS = ROOT / "solutions"


def log(*args):
    line = " ".join(str(a) for a in args)
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def avoid_count(n, t, s):
    return math.comb(n - t, s) + math.comb(n - t + 1, s) - math.comb(n - 2 * t + 1, s)


# ----------------------------------------------------------------------------
def stage_exact():
    log("\n== exact ==", time.strftime("%Y-%m-%d %H:%M"))
    bad = 0
    cases = 0
    for n in range(2, 13):
        for p in (Fraction(1, 3), Fraction(2, 7), Fraction(1, 5), Fraction(1, 2), Fraction(3, 50)):
            for t in range(1, (n + 1) // 2 + 1):
                lhs = sum(p ** s * (1 - p) ** (n - s) * avoid_count(n, t, s) for s in range(n + 1))
                rhs = (1 - p) ** t + (1 - p) ** (t - 1) - (1 - p) ** (2 * t - 1)
                cases += 1
                bad += lhs != rhs
                trunc = sum(math.comb(n, s) * p ** s * (1 - p) ** (n - s) * Fraction(avoid_count(n, t, max(s, 2)), math.comb(n, max(s, 2)))
                            for s in range(n + 1))
                bad += abs(fm.lq_truncated(n, float(p), t) - math.log(float(trunc))) > 1e-9
                bad += trunc > rhs
    log(f"(a) sum_s Bin(n,p)(s) q(n,t,s) = (1-p)^t + (1-p)^(t-1) - (1-p)^(2t-1): {cases} cases at n <= 12, {bad} failures"
        f" (also: the truncated average equals lq_truncated and is <= the Bernoulli one)")
    for m, n in ((2, 6), (3, 4)):
        p = Fraction(1, 3)
        weights = []
        mats = []
        for bits in itertools.product((0, 1), repeat=m * n):
            B = np.array(bits, dtype=bool).reshape(m, n)
            mats.append(B)
            weights.append(p ** sum(bits) * (1 - p) ** (m * n - sum(bits)))
        assert sum(weights) == 1
        fails = 0
        pairs = 0
        for t in range(1, (n + 1) // 2 + 1):
            for A in itertools.combinations(range(n), t):
                rest = [v for v in range(n) if v not in A]
                for R in itertools.combinations(rest, t - 1):
                    empty = Fraction(0)
                    for B, w in zip(mats, weights):
                        meets = any(B[i, list(A)].any() and (len(R) > 0 and B[i, list(R)].any()) for i in range(m))
                        empty += w * (not meets)
                    formula = ((1 - p) ** t + (1 - p) ** (t - 1) - (1 - p) ** (2 * t - 1)) ** m
                    pairs += 1
                    fails += empty != formula
        disc = sum(w for B, w in zip(mats, weights) if not fm.mosp_connected(B))
        rep = sum(w for B, w in zip(mats, weights) if not fm.no_repair_needed(B))
        cut = math.exp(fm.log_disconnected_bound(n, m, float(p)))
        repb = math.exp(fm.log_repair_bound(n, m, float(p)))
        log(f"enumeration m={m} n={n} p=1/3 ({2 ** (m * n)} matrices): P(pair empty) = formula on {pairs} pairs, {fails} failures;"
            f" P(G_B disconnected) = {float(disc):.4f} <= cut bound {cut:.4f}: {float(disc) <= cut + 1e-12};"
            f" P(repair fires) = {float(rep):.4f} <= repair bound {repb:.4f}: {float(rep) <= repb + 1e-12}")


# ----------------------------------------------------------------------------
def load_gen_candidates():
    spec = importlib.util.spec_from_file_location("gen_candidates", ROOT / "reports/scratch/clique_cover_moment/gen_candidates.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stage_law():
    log("\n== law ==", time.strftime("%Y-%m-%d %H:%M"))
    gc = load_gen_candidates()
    draws = 4000
    for (n, m, d) in ((30, 30, 2), (50, 50, 2), (30, 30, 4), (100, 50, 2)):
        p = d / n
        rows = {"scratch": [], "explicit": []}
        rng = np.random.default_rng(1)
        for _ in range(draws):
            M = gc.pad_patterns(gc.pad_customers(gc.bern(n, m, p, rng), 1, rng), 2, rng)
            rows["scratch"].append((M.sum(), M.sum(axis=1).var(), (M.sum(axis=1) == 2).mean(), (M.sum(axis=0) == 1).mean(), gc.mosp_connected(M)))
        rng = np.random.default_rng(2)
        for _ in range(draws):
            dd = fm.generator_draw(n, m, p, rng)
            M = dd["M"]
            rows["explicit"].append((M.sum(), M.sum(axis=1).var(), (M.sum(axis=1) == 2).mean(), (M.sum(axis=0) == 1).mean(), dd["accepted"]))
        a, b = np.array(rows["scratch"], float), np.array(rows["explicit"], float)
        names = ["ones", "row var", "frac rows of size 2", "frac customers with 1 pattern", "accepted"]
        zs = []
        for i, name in enumerate(names):
            se = math.sqrt(a[:, i].var() / draws + b[:, i].var() / draws)
            z = (a[:, i].mean() - b[:, i].mean()) / se if se > 0 else 0.0
            zs.append(f"{name} {a[:, i].mean():.4f} vs {b[:, i].mean():.4f} (z {z:+.2f})")
        log(f"({n},{m},{d}) scratch generator vs explicit-randomness generator, {draws} draws each: " + "; ".join(zs))


# ----------------------------------------------------------------------------
def all_pairs(n):
    A, R = [], []
    for a in range(1, 1 << n):
        for r in range(1, 1 << n):
            if a & r == 0:
                A.append(a)
                R.append(r)
    return np.array(A, dtype=np.int64), np.array(R, dtype=np.int64)


def pattern_masks(M):
    m, n = M.shape
    return np.array([sum(1 << int(c) for c in np.flatnonzero(M[i])) for i in range(m)], dtype=np.int64)


def empty_pairs(pm, A, R):
    meets = ((pm[None, :] & A[:, None]) != 0) & ((pm[None, :] & R[:, None]) != 0)
    return ~meets.any(axis=1)


def pw_of(M):
    return fm.vertex_separation_brute(fm.customer_masks(M))


def stage_coupling(draws=10000, n=8, m=8, flip_draws=2000, flip_pw_draws=300):
    log("\n== coupling ==", time.strftime("%Y-%m-%d %H:%M"), f"n={n} m={m} draws={draws} flip_draws={flip_draws}")
    A, R = all_pairs(n)
    log(f"ordered disjoint nonempty pairs (A, R) at n = {n}: {len(A)}")
    summary = []
    for d in (2, 4):
        p = d / n
        for first in (False, True):
            order = "patterns-first" if first else "customers-first (fitted)"
            rng = np.random.default_rng(100 + d + 10 * first)
            c = dict(superset=0, dominated=0, pair_incl=0, pw_mono=0, acc=0, acc_plus=0, base_conn=0, norep=0, rep_acc=0,
                     flips=0, pad_vanished=0, acc_lost=0, pw_fell=0, plus_not_mono=0, plus_conn_lost=0, base_conn_lost=0, base_pw_fell=0,
                     m_pw_rose_over_plus=0)
            pwM, pwB, accs, pwPlus = [], [], [], []
            for it in range(draws):
                dd = fm.generator_draw(n, m, p, rng, patterns_first=first)
                B, M, Mp = dd["B"], dd["M"], dd["Mp"]
                c["superset"] += bool(np.all(M >= B))
                c["dominated"] += bool(np.all(Mp >= M))
                pmB, pmM = pattern_masks(B), pattern_masks(M)
                eM, eB = empty_pairs(pmM, A, R), empty_pairs(pmB, A, R)
                c["pair_incl"] += bool(np.all(eB | ~eM))
                a, b_ = pw_of(M), pw_of(B)
                c["pw_mono"] += b_ <= a
                pwM.append(a)
                pwB.append(b_)
                accs.append(dd["accepted"])
                c["acc"] += dd["accepted"]
                c["acc_plus"] += dd["accepted_plus"]
                c["base_conn"] += dd["base_connected"]
                c["norep"] += dd["no_repair"]
                c["rep_acc"] += (not dd["no_repair"]) and dd["accepted"]
                if it < flip_draws:
                    U, sigma = dd["U"], dd["sigma"]
                    connM, connMp, connB = dd["accepted"], dd["accepted_plus"], dd["base_connected"]
                    pwMp_cache = None
                    for (i, j) in zip(*np.nonzero(~B)):
                        B2 = B.copy()
                        B2[i, j] = True
                        M2 = fm.pad_with_aux(B2, U, sigma, patterns_first=first)
                        Mp2 = fm.unconditional_pad(B2, U, sigma)
                        c["flips"] += 1
                        vanished = not np.all(M2 >= M)
                        c["pad_vanished"] += vanished
                        if vanished:
                            conn2 = fm.mosp_connected(M2)
                            c["acc_lost"] += connM and not conn2
                            c["pw_fell"] += pw_of(M2) < a
                        c["plus_not_mono"] += not np.all(Mp2 >= Mp)
                        c["plus_conn_lost"] += connMp and not fm.mosp_connected(Mp2)
                        c["base_conn_lost"] += connB and not fm.mosp_connected(B2)
                        if it < flip_pw_draws:
                            c["base_pw_fell"] += pw_of(B2) < b_
            pwM, pwB, accs = np.array(pwM), np.array(pwB), np.array(accs, bool)
            log(f"\n-- d = {d} (p = {p:.3f}), {order}: {draws} draws --")
            log(f"M >= B in {c['superset']} of {draws}; M <= M+ in {c['dominated']}; every empty pair of G_M empty in G_B in {c['pair_incl']};"
                f" pw(G_B) <= pw(G_M) in {c['pw_mono']}")
            log(f"P(accepted) = {c['acc'] / draws:.4f}, P(M+ connected) = {c['acc_plus'] / draws:.4f}, P(G_B connected) = {c['base_conn'] / draws:.4f},"
                f" P(no repair) = {c['norep'] / draws:.4f}, P(repair and accepted) = {c['rep_acc'] / draws:.4f}")
            log(f"single-entry increases of the base on the first {flip_draws} draws: {c['flips']}; a pad vanished (M' not >= M) in {c['pad_vanished']};"
                f" acceptance lost in {c['acc_lost']}; pw(G_M) fell in {c['pw_fell']}  -> the repair map is not monotone;"
                f" M+ not monotone in {c['plus_not_mono']}; M+ connectivity lost in {c['plus_conn_lost']};"
                f" G_B connectivity lost in {c['base_conn_lost']}; pw(G_B) fell in {c['base_pw_fell']} (pw of the base checked on the first {flip_pw_draws} draws)")
            nacc = int(accs.sum())
            p_acc = nacc / draws
            p_plus = c["acc_plus"] / draws
            p_repacc = c["rep_acc"] / draws
            lrep = math.exp(fm.log_repair_bound(n, m, p))
            model = "truncated" if first else "bernoulli"
            lb_fn = fm.log_bound_truncated if first else fm.log_bound_bernoulli
            log(f"k | P^(pw(G_M)<=k | acc) (se) | P^(pw(G_B)<=k) | P^(pw(G_M)<=k) | UB_B(k) | UB_trunc(k) | trivial UB/P(acc) | Harris+ UB*P(M+conn)/P(acc)"
                f" | Harris_E UB + P(E^c)/P(acc) [closed form P(E^c) <= {lrep:.3f}; measured P(E^c|acc) = {p_repacc / p_acc:.3f}]")
            viol = 0
            for k in range(n):
                cond = (pwM[accs] <= k).mean()
                se = math.sqrt(cond * (1 - cond) / max(nacc, 1))
                ubB = math.exp(min(fm.log_bound_bernoulli(n, m, p, k), 700))
                ubT = math.exp(min(fm.log_bound_truncated(n, m, p, k), 700))
                ub = ubT if first else ubB
                triv = ub / p_acc
                harris = ubB * p_plus / p_acc
                harrisE = ub + lrep / p_acc
                tol = 3 * se + 1e-9
                ok = cond <= triv + tol and cond <= harrisE + tol and (first or cond <= harris + tol)
                viol += not ok
                log(f"{k} | {cond:.4f} ({se:.4f}) | {(pwB <= k).mean():.4f} | {(pwM <= k).mean():.4f} | {ubB:.4g} | {ubT:.4g} | {triv:.4g} | {harris:.4g} | {harrisE:.4g}"
                    + ("" if ok else "  VIOLATION"))
            direction = sum((pwM[accs] <= k).mean() <= (pwB <= k).mean() + 1e-12 for k in range(n))
            log(f"Monte Carlo against the rigorous forms (3 se): {viol} violations over {n} values of k; measured P(pw(G_M)<=k | acc) <= P(pw(G_B)<=k) at {direction} of {n} k")
            summary.append((d, order, c, p_acc, p_plus, viol))
    return summary


# ----------------------------------------------------------------------------
def classes_list():
    cl = fm.chu_stuckey_sizes()
    return sorted(cl)


def _rates_job(args):
    n, m, d, first, seed = args
    p = d / n
    c = fm.generator_event_rates(n, m, p, draws=2000, seed=seed, min_accepted=300, max_draws=60000, patterns_first=first)
    return (n, m, d, first, c)


def stage_classes(workers=8):
    import csv
    from multiprocessing import Pool

    log("\n== classes ==", time.strftime("%Y-%m-%d %H:%M"))
    load1 = os.getloadavg()[0]
    workers = 4 if load1 > 24 else workers
    log(f"load {load1:.1f}, workers {workers}")
    jobs = [(n, m, d, first, 1000 * d + n + 7 * first) for (n, m, d) in classes_list() for first in (False, True)]
    t0 = time.time()
    with Pool(workers, initializer=os.nice, initargs=(19,)) as pool:
        res = pool.map(_rates_job, jobs)
    log(f"{len(jobs)} jobs in {time.time() - t0:.0f} s wall")
    with open(HERE / "classes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "m", "d", "order", "draws", "accepted", "accepted_plus", "base_connected", "no_repair", "repair_and_accepted",
                    "p_acc", "p_acc_lo", "p_acc_hi", "p_plus", "p_plus_hi", "p_norep", "p_repair_given_acc"])
        for (n, m, d, first, c) in sorted(res, key=lambda r: (r[0], r[1], r[2], r[3])):
            lo, hi = fm.wilson(c["accepted"], c["draws"])
            plo, phi = fm.wilson(c["accepted_plus"], c["draws"])
            w.writerow([n, m, d, "patterns-first" if first else "customers-first", c["draws"], c["accepted"], c["accepted_plus"],
                        c["base_connected"], c["no_repair"], c["repair_and_accepted"],
                        c["accepted"] / c["draws"], lo, hi, c["accepted_plus"] / c["draws"], phi, c["no_repair"] / c["draws"],
                        (c["repair_and_accepted"] / c["accepted"]) if c["accepted"] else float("nan")])
    log("classes.csv written")


# ----------------------------------------------------------------------------
def stage_table():
    import csv

    log("\n== table ==", time.strftime("%Y-%m-%d %H:%M"))
    rates = {}
    with open(HERE / "classes.csv") as f:
        for r in csv.DictReader(f):
            rates[(int(r["n"]), int(r["m"]), int(r["d"]), r["order"])] = r
    cl = fm.chu_stuckey_sizes()
    rows = []
    for key in sorted(cl):
        n, m, d = key
        p = d / n
        inst = cl[key]["instances"]
        opts = []
        f1s, f2s = [], []
        for name, sizes in inst:
            opts.append(json.load(open(SOLUTIONS / f"{name}_0.json"))["mosp_value"])
            a, b = fm.floors(n, sizes)
            f1s.append(a)
            f2s.append(b)
        rc = rates[(n, m, d, "customers-first")]
        rp = rates[(n, m, d, "patterns-first")]
        p_acc, p_acc_lo = float(rc["p_acc"]), float(rc["p_acc_lo"])
        p_plus_hi = float(rc["p_plus_hi"])
        pp_acc, pp_acc_lo = float(rp["p_acc"]), float(rp["p_acc_lo"])
        bern = fm.rejection_floors(n, m, p, p_acc=p_acc, p_acc_plus=float(rc["p_plus"]))
        bern_lo = fm.rejection_floors(n, m, p, p_acc=p_acc_lo, p_acc_plus=p_plus_hi)
        trunc = fm.rejection_floors(n, m, p, p_acc=pp_acc, model="truncated")
        trunc_lo = fm.rejection_floors(n, m, p, p_acc=pp_acc_lo, model="truncated")
        def quenched_floors(kmin, draws=200):
            # typical-instance diagnostic (not a theorem): the per-instance uniform-model floor at
            # sizes drawn from Bin(n, p) (lifted to kmin), averaged over draws, like the per-file floors
            rng = np.random.default_rng(5)
            vals = []
            for _ in range(draws):
                sizes = np.maximum(rng.binomial(n, p, size=m), kmin)
                vals.append(fm.floors(n, [int(x) for x in sizes])[1])
            return (float(np.mean(vals)),)
        qb, qt = quenched_floors(0), quenched_floors(2)
        bb = fm.floors_best(n, m, p, 0)
        bb_triv = fm.floors_best(n, m, p, 0, log_factor=-math.log(p_acc))
        bb_triv_lo = fm.floors_best(n, m, p, 0, log_factor=-math.log(p_acc_lo))
        tb = fm.floors_best(n, m, p, 2)
        tb_triv = fm.floors_best(n, m, p, 2, log_factor=-math.log(pp_acc))
        tb_triv_lo = fm.floors_best(n, m, p, 2, log_factor=-math.log(pp_acc_lo))
        row = dict(n=n, m=m, d=d, p=p, opt_mean=np.mean(opts), opt_min=min(opts),
                   bern_best_f1=bb[0], bern_best_f2=bb[1], bern_best_triv_f2=bb_triv[1], bern_best_triv_lo_f2=bb_triv_lo[1],
                   trunc_best_f1=tb[0], trunc_best_f2=tb[1], trunc_best_triv_f2=tb_triv[1], trunc_best_triv_lo_f2=tb_triv_lo[1],
                   quenched_bin_f2=qb[0], quenched_trunc_f2=qt[0],
                   meas_f1=np.mean(f1s), meas_f2=np.mean(f2s), meas_f2_min=min(f2s), meas_f2_max=max(f2s),
                   p_acc=p_acc, p_acc_lo=p_acc_lo, p_plus=float(rc["p_plus"]), p_norep=float(rc["p_norep"]),
                   p_rep_acc=float(rc["p_repair_given_acc"]), p_acc_pf=pp_acc,
                   bern_base_f1=bern["base"][0], bern_base_f2=bern["base"][1],
                   bern_triv_f2=bern["trivial"][1], bern_triv_lo_f2=bern_lo["trivial"][1],
                   bern_hplus_f2=bern["harris_plus"][1], bern_hplus_lo_f2=bern_lo["harris_plus"][1],
                   bern_hE_f2=bern["harris_E"][1], bern_closed_f2=bern["closed"][1],
                   closed_valid=fm.log_disconnected_bound(n, m, p) < 0,
                   log_pdisc=fm.log_disconnected_bound(n, m, p), log_prep=fm.log_repair_bound(n, m, p),
                   trunc_base_f1=trunc["base"][0], trunc_base_f2=trunc["base"][1],
                   trunc_triv_f2=trunc["trivial"][1], trunc_triv_lo_f2=trunc_lo["trivial"][1],
                   trunc_hE_f2=trunc["harris_E"][1], trunc_closed_f2=trunc["closed"][1],
                   bern105_f2=fm.floors_bernoulli(n, m, 1.05 * p)[1], bern110_f2=fm.floors_bernoulli(n, m, 1.10 * p)[1],
                   trunc105_f2=fm.floors_truncated(n, m, 1.05 * p)[1], trunc110_f2=fm.floors_truncated(n, m, 1.10 * p)[1])
        rows.append(row)
    with open(HERE / "floors.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    # tables.md
    out = []
    out.append("### Floors per class: the measured model beside the rigorous ones (0.01 level unless marked)\n")
    out.append("Columns: class; mean certified optimum (min); measured-model floor at < 1 / < 0.01 (per file, averaged); "
               "Bernoulli rigorous: base (no rejection) < 1 / < 0.01, trivial `/ P(acc)` (point; Wilson-lower acceptance), "
               "Harris on `M+`, Harris on `E`, closed form, best of annealed and quenched (V3, V3′) < 1 / < 0.01 and with the rejection; truncated (patterns-first) rigorous: base < 1 / < 0.01, trivial, Harris on `E`, closed form, best < 1 / < 0.01 and with the rejection; "
               "`P(acc)` (fitted order), `P(acc)` (patterns-first), `P(M+ conn)`, `P(no repair)`, measured `P(repair | acc)`.\n")
    out.append("| class | opt (min) | meas <1 / <0.01 | B base <1 / <0.01 | B triv (lo) | B Harris+ (lo) | B Harris_E | B closed | B best <1 / <0.01 | B best triv (lo) | T base <1 / <0.01 | T triv (lo) | T Harris_E | T closed | T best <1 / <0.01 | T best triv (lo) | P(acc) | P(acc) pf | P(M+ conn) | P(no rep) | P(rep|acc) |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        clo = r["bern_closed_f2"] if r["closed_valid"] else "—"
        tclo = r["trunc_closed_f2"] if r["closed_valid"] else "—"
        out.append(f"| ({r['n']},{r['m']},{r['d']}) | {r['opt_mean']:.1f} ({r['opt_min']}) | {r['meas_f1']:.1f} / {r['meas_f2']:.1f} | "
                   f"{r['bern_base_f1']} / {r['bern_base_f2']} | {r['bern_triv_f2']} ({r['bern_triv_lo_f2']}) | {r['bern_hplus_f2']} ({r['bern_hplus_lo_f2']}) | "
                   f"{r['bern_hE_f2']} | {clo} | {r['bern_best_f1']} / {r['bern_best_f2']} | {r['bern_best_triv_f2']} ({r['bern_best_triv_lo_f2']}) | {r['trunc_base_f1']} / {r['trunc_base_f2']} | {r['trunc_triv_f2']} ({r['trunc_triv_lo_f2']}) | {r['trunc_hE_f2']} | {tclo} | {r['trunc_best_f1']} / {r['trunc_best_f2']} | {r['trunc_best_triv_f2']} ({r['trunc_best_triv_lo_f2']}) | "
                   f"{r['p_acc']:.4f} | {r['p_acc_pf']:.4f} | {r['p_plus']:.3f} | {r['p_norep']:.3f} | {r['p_rep_acc']:.3f} |")
    out.append("\n### Where the rigorous 0.01 floor differs from the measured-model one by more than one stack\n")
    out.append("| class | measured | B best, with rejection | diff | T best, with rejection | diff | B annealed trivial | T annealed trivial | mean certified optimum |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    nb = nt = 0
    for r in rows:
        db = r["bern_best_triv_f2"] - r["meas_f2"]
        dt = r["trunc_best_triv_f2"] - r["meas_f2"]
        nb += abs(db) > 1
        nt += abs(dt) > 1
        if abs(db) > 1 or abs(dt) > 1:
            out.append(f"| ({r['n']},{r['m']},{r['d']}) | {r['meas_f2']:.1f} | {r['bern_best_triv_f2']} | {db:+.1f} | {r['trunc_best_triv_f2']} | {dt:+.1f} | {r['bern_triv_f2']} | {r['trunc_triv_f2']} | {r['opt_mean']:.1f} |")
    out.append(f"\nClasses where |rigorous − measured| > 1 stack (best form, with the rejection): Bernoulli sizes {nb} of 40; truncated sizes {nt} of 40.\n")
    out.append("### Where the price of rigour comes from (0.01 floors): annealed (rigorous) -> per-instance floors at simulated Bin(n, d/n) sizes, mean of 200 (typical instance, not a theorem) -> realised sizes\n")
    out.append("| class | B rigorous (annealed, Bin sizes) | quenched at Bin sizes | T rigorous (annealed, max(Bin,2)) | quenched at max(Bin,2) | measured (realised sizes) |")
    out.append("|---|---|---|---|---|---|")
    for r in rows:
        out.append(f"| ({r['n']},{r['m']},{r['d']}) | {r['bern_base_f2']} | {r['quenched_bin_f2']:.1f} | {r['trunc_base_f2']} | {r['quenched_trunc_f2']:.1f} | {r['meas_f2']:.1f} |")
    out.append("")
    out.append("### Sensitivity to the density constant (0.01 floor, no rejection)\n")
    out.append("| class | B at d/n | B at 1.05 d/n | B at 1.10 d/n | T at d/n | T at 1.05 d/n | T at 1.10 d/n | measured |")
    out.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        out.append(f"| ({r['n']},{r['m']},{r['d']}) | {r['bern_base_f2']} | {r['bern105_f2']} | {r['bern110_f2']} | {r['trunc_base_f2']} | {r['trunc105_f2']} | {r['trunc110_f2']} | {r['meas_f2']:.1f} |")
    (HERE / "tables.md").write_text("\n".join(out) + "\n")
    log("\n".join(out))
    # violations: certified optimum below any rigorous floor?
    v = sum(r["opt_min"] < r["bern_triv_f2"] for r in rows) + sum(r["opt_min"] < r["trunc_triv_f2"] for r in rows)
    log(f"certified optima below a rigorous trivial-form floor: {v}")


if __name__ == "__main__":
    stages = sys.argv[1:] or ["all"]
    if "all" in stages:
        stages = ["exact", "law", "coupling", "classes", "table"]
    for s in stages:
        globals()[f"stage_{s}"]()
