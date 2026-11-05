#!/usr/bin/env python3
"""For the practitioner: a SAT solver and two model counters against the verified bound and 2^n.

Paper 3, item 06 (Ralph loop0015, 2026-11-05).  The verified statement of OpenAI's family
378 (comparator file lines 194-217 at commit 4eaee875) guarantees, for each fixed width
k, one deterministic machine that counts the satisfying assignments of a k-CNF in at most
C (L+1)^d 2^(A rho(n)) steps, rho(n) = n (ln ln(n+16))^2 / sqrt(ln(n+16)).  The constants
C, A, d are existential and never computed; no implementation of the machine exists.  Brute
force is 2^n * poly.  What a practitioner has on a machine is a CDCL solver (decision) and
a model counter (the count).  This script measures those on random 3-CNF and tabulates the
two *guarantees* beside them.

Instances: random 3-CNF, n variables, m = round(4.26 n) clauses (the satisfiability
threshold of Selman, Mitchell & Levesque 1996; Mertens, Mezard & Zecchina 2006 put it at
4.2667), each clause three distinct variables and uniform signs, generated here from
(n, seed) with Python's random module; 20 seeds per size.  No MOSP or pathwidth instance,
nothing read from solutions/.

Tools (each in its own subprocess under `timeout`, at most 8 at a time, nice -n 19):
  cadical   CaDiCaL 1.9.5 through python-sat ("cadical195"): the decision bit, one solve()
  enum      exact count by blocking-clause enumeration over CaDiCaL, n <= 30 only (a loop
            over a SAT solver is not a counter at larger n; here it is the independent check
            of the two counters at the sizes it can reach)
  ganak     Ganak (pyganak 2.8.0; Arjun preprocessing + Ganak), the exact count
  approxmc  ApproxMC (pyapproxmc 4.4.0), epsilon 0.8, delta 0.2, projection = all variables,
            the (epsilon, delta)-approximate count cells * 2^hashes

Timing is wall-clock (time.perf_counter) around construction and the one call, inside the
subprocess; the interpreter's start-up is outside it.  A call that exceeds TIMEOUT seconds is
killed and recorded as censored ("> TIMEOUT"); a size at which a tool finishes fewer than half
of its 20 instances stops that tool's escalation to larger sizes.

Guarantees: 2^rho(n) and 2^n at constant 1, drawn as shapes with one common factor t20 / 2^20
where t20 is CaDiCaL's median at n = 20: so 2^n passes through the n = 20 measurement and
2^rho(n) crosses it at n = 50 (rho(n) >= n from n = 50, Section 2).  Nothing about the
verified machine's running time follows from any of this: the constants are unknown.

Regenerate (about 20 minutes of wall clock on the machine of record):
    nice -n 19 python3 -I paper3/scripts/practitioner.py --regenerate
  -> paper3/latex/tables/practitioner_raw.csv   (every call: n, m, seed, tool, status, seconds, answer)
     paper3/latex/tables/practitioner_meta.json (versions, CPU, load, timeout, sizes, date)
Rebuild the table and figure from the CSV (seconds):
    python3 -I paper3/scripts/practitioner.py
  -> paper3/latex/tables/practitioner.tex, paper3/latex/figures/practitioner.{pdf,png}, stdout
Verify the CSV's internal consistency without writing:
    python3 -I paper3/scripts/practitioner.py --check
"""
import argparse
import csv
import json
import math
import os
import pathlib
import platform
import random
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent.parent
TAB = HERE / "latex" / "tables"
FIG = HERE / "latex" / "figures"
RAW = TAB / "practitioner_raw.csv"
META = TAB / "practitioner_meta.json"

RATIO = 4.26
SEEDS = 20
WORKERS = 8
TIMEOUT = 60.0  # seconds per call
SIZES = [20, 30, 40, 50, 60, 80, 100, 150, 200, 250, 300, 400, 500]
ENUM_MAX_N = 30
TOOLS = ["cadical", "enum", "ganak", "approxmc"]
TOOL_LABEL = {"cadical": "CaDiCaL 1.9.5 (decision)", "enum": "enumeration (count, $n \\le 30$)",
              "ganak": "Ganak 2.8.0 (exact count)", "approxmc": "ApproxMC 4.4.0 (approximate count)"}


# --- the formulas -----------------------------------------------------------------------
def clauses_of(n: int, seed: int):
    rng = random.Random(1_000_003 * seed + n)
    m = round(RATIO * n)
    out = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), 3)
        out.append([v if rng.random() < 0.5 else -v for v in vs])
    return out


def rho(n: float) -> float:
    y = math.log(n + 16.0)
    return n * math.log(y) ** 2 / math.sqrt(y)


# --- one call, in a subprocess ----------------------------------------------------------
def run_one(tool: str, n: int, seed: int) -> dict:
    """Executed in the child: `python3 -I practitioner.py --task tool n seed`."""
    cls = clauses_of(n, seed)
    if tool in ("cadical", "enum"):
        from pysat.solvers import Solver
    elif tool == "ganak":
        import pyganak
    elif tool == "approxmc":
        import pyapproxmc
    t0 = time.perf_counter()  # the import is outside the timer; construction and the call are inside
    if tool == "cadical":
        with Solver(name="cadical195", bootstrap_with=cls) as s:
            answer = int(s.solve())
    elif tool == "enum":
        answer = 0
        with Solver(name="cadical195", bootstrap_with=cls) as s:
            while s.solve():
                answer += 1
                s.add_clause([-l for l in s.get_model()])
    elif tool == "ganak":
        c = pyganak.Counter()
        c.new_vars(n)
        c.add_clauses(cls)
        answer = c.count()
    elif tool == "approxmc":
        c = pyapproxmc.Counter(epsilon=0.8, delta=0.2, seed=seed)
        c.add_clauses(cls)
        cells, hashes = c.count(list(range(1, n + 1)))
        answer = cells * 2 ** hashes
    else:
        raise ValueError(tool)
    dt = time.perf_counter() - t0
    return {"tool": tool, "n": n, "m": len(cls), "seed": seed, "status": "ok",
            "seconds": dt, "answer": str(answer)}


def launch(tool: str, n: int, seed: int) -> dict:
    cmd = ["nice", "-n", "19", sys.executable, "-I", str(pathlib.Path(__file__).resolve()),
           "--task", tool, str(n), str(seed)]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT + 5.0)
    except subprocess.TimeoutExpired:
        return {"tool": tool, "n": n, "m": round(RATIO * n), "seed": seed, "status": "timeout",
                "seconds": TIMEOUT, "answer": ""}
    if p.returncode != 0:
        return {"tool": tool, "n": n, "m": round(RATIO * n), "seed": seed, "status": "error",
                "seconds": "", "answer": p.stderr.strip().splitlines()[-1][:80] if p.stderr.strip() else ""}
    rec = json.loads(p.stdout.strip().splitlines()[-1])
    if rec["seconds"] > TIMEOUT:  # finished after the budget: censor it the same way
        rec["status"], rec["seconds"], rec["answer"] = "timeout", TIMEOUT, ""
    return rec


def versions() -> dict:
    import pysat
    import pyganak
    import pyapproxmc
    from pysat.solvers import Solver
    with Solver(name="cadical195") as s:
        pass
    cpu = ""
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    return {"python": platform.python_version(), "python-sat": pysat.__version__,
            "cadical": "1.9.5 (python-sat name cadical195)", "pyganak": pyganak.VERSION,
            "pyapproxmc": pyapproxmc.__version__, "cpu": cpu, "kernel": platform.release(),
            "nproc": os.cpu_count(), "load_at_start": os.getloadavg()}


# --- the measurement --------------------------------------------------------------------
def regenerate():
    meta = {"date": time.strftime("%Y-%m-%d %H:%M:%S"), "ratio": RATIO, "seeds": SEEDS,
            "workers": WORKERS, "timeout_s": TIMEOUT, "sizes": SIZES, "enum_max_n": ENUM_MAX_N,
            "versions": versions(), "stopped_at": {}}
    rows = []
    active = {t: True for t in TOOLS}
    t_all = time.perf_counter()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for n in SIZES:
            tools = [t for t in TOOLS if active[t] and not (t == "enum" and n > ENUM_MAX_N)]
            if not tools:
                break
            futs = [pool.submit(launch, t, n, s) for t in tools for s in range(SEEDS)]
            got = [f.result() for f in as_completed(futs)]
            rows.extend(got)
            for t in tools:
                done = sum(1 for r in got if r["tool"] == t and r["status"] == "ok")
                secs = [r["seconds"] for r in got if r["tool"] == t and r["status"] == "ok"]
                print(f"n={n:4d} {t:9s} finished {done:2d}/{SEEDS}  "
                      f"median {statistics.median(secs) if secs else float('nan'):9.4f}s  "
                      f"max {max(secs) if secs else float('nan'):9.4f}s   [{time.perf_counter() - t_all:6.0f}s elapsed]",
                      flush=True)
                if done < SEEDS / 2:
                    active[t] = False
                    meta["stopped_at"][t] = n
    meta["wall_s"] = time.perf_counter() - t_all
    meta["load_at_end"] = os.getloadavg()
    rows.sort(key=lambda r: (TOOLS.index(r["tool"]), r["n"], r["seed"]))
    with open(RAW, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["tool", "n", "m", "seed", "status", "seconds", "answer"])
        w.writeheader()
        w.writerows(rows)
    with open(META, "w") as fh:
        json.dump(meta, fh, indent=1)
    print("written", RAW, META, f"({meta['wall_s']:.0f} s wall)")


# --- reading back ------------------------------------------------------------------------
def load():
    rows = list(csv.DictReader(open(RAW)))
    for r in rows:
        r["n"], r["m"], r["seed"] = int(r["n"]), int(r["m"]), int(r["seed"])
        r["seconds"] = float(r["seconds"]) if r["seconds"] else None
    meta = json.load(open(META))
    return rows, meta


def censored_stats(recs):
    """Median and max over all SEEDS runs with censored runs as +inf: (median, med_censored, max, max_censored, finished)."""
    secs = sorted((r["seconds"] if r["status"] == "ok" else math.inf) for r in recs)
    k = len(secs)
    fin = sum(1 for r in recs if r["status"] == "ok")
    if k == 0:
        return None
    med = secs[k // 2] if k % 2 else 0.5 * (secs[k // 2 - 1] + secs[k // 2])
    mx = secs[-1]
    return (med if med < math.inf else TIMEOUT, med == math.inf, mx if mx < math.inf else TIMEOUT,
            mx == math.inf, fin)


def checks(rows, meta):
    """Internal consistency: counts agree where two counters finish; the decision bit agrees with count > 0."""
    by = {}
    for r in rows:
        by[(r["tool"], r["n"], r["seed"])] = r
    problems = []
    agree_enum = agree_approx = within = 0
    for (tool, n, seed), r in by.items():
        if tool != "ganak" or r["status"] != "ok":
            continue
        g = int(r["answer"])
        e = by.get(("enum", n, seed))
        if e and e["status"] == "ok":
            if int(e["answer"]) != g:
                problems.append(f"ganak {g} != enum {e['answer']} at n={n} seed={seed}")
            else:
                agree_enum += 1
        c = by.get(("cadical", n, seed))
        if c and c["status"] == "ok" and (int(c["answer"]) == 1) != (g > 0):
            problems.append(f"cadical {c['answer']} vs ganak {g} at n={n} seed={seed}")
        a = by.get(("approxmc", n, seed))
        if a and a["status"] == "ok":
            agree_approx += 1
            ac = int(a["answer"])
            if (g == 0 and ac == 0) or (g > 0 and g / 1.8 <= ac <= g * 1.8):
                within += 1
    for r in rows:
        if r["status"] == "error":
            problems.append(f"error: {r['tool']} n={r['n']} seed={r['seed']}: {r['answer']}")
    return problems, agree_enum, agree_approx, within


CLONE = pathlib.Path.home() / "dev" / "untrusted" / "openai-math"
FAMILY = CLONE / "lean" / "OAI" / "Algorithms" / "SubexponentialSAT"


def clone_check() -> dict:
    """Read-only (open() only): the family has no #eval, no `def main`, no IO action; the
    comparator theorem is existential in the machine.  So no implementation of the verified
    machine that could be run is on record in the clone."""
    import re
    n_files = n_eval = n_main = n_io = 0
    for f in FAMILY.rglob("*.lean"):
        n_files += 1
        txt = f.read_text(errors="replace")
        n_eval += len(re.findall(r"^\s*#eval\b", txt, re.M))
        n_main += len(re.findall(r"^\s*def\s+main\b", txt, re.M))
        n_io += len(re.findall(r"\bIO\s+(Unit|Bool|Nat|String|\()", txt))
    comp = (CLONE / "lean" / "ComparatorChallenges" / "SubexponentialSAT.lean").read_text().splitlines()
    existential = comp[194].strip().startswith("∃ (machine : Computation.PrimitiveMachine)")
    return {"family_files": n_files, "eval": n_eval, "def_main": n_main, "io_actions": n_io,
            "theorem_existential_in_machine": existential}


def summary(rows):
    out = {}
    for r in rows:
        out.setdefault((r["tool"], r["n"]), []).append(r)
    return {k: censored_stats(v) for k, v in out.items()}


def fmt_s(x, censored):
    if censored:
        return f"$>{TIMEOUT:.0f}$"
    if x >= 100:
        return f"{x:.0f}"
    if x >= 1:
        return f"{x:.2f}"
    if x >= 1e-3:
        return f"{x:.4f}"
    e = int(math.floor(math.log10(x)))
    return f"${x / 10 ** e:.1f}\\times 10^{{{e}}}$"


def fmt_big(x):
    """Seconds as a readable number: plain below 10^4, otherwise 10^e."""
    if x < 1e4:
        return fmt_s(x, False)
    e = math.log10(x)
    return f"$10^{{{e:.1f}}}$"


def write_table(rows, meta):
    S = summary(rows)
    sizes = sorted({r["n"] for r in rows})
    t20 = S[("cadical", 20)][0]
    scale = t20 / 2.0 ** 20
    with open(TAB / "practitioner.tex", "w") as fh:
        fh.write("% Generated by paper3/scripts/practitioner.py (python3 -I) from practitioner_raw.csv; do not edit.\n")
        fh.write(f"% {meta['date']}, {meta['versions']['cpu']}, timeout {TIMEOUT:.0f} s per call, {SEEDS} seeds per size.\n")
        fh.write("\\begin{tabular}{@{}rrr rr rrr rrr rr@{}}\n\\toprule\n")
        fh.write("& & & \\multicolumn{2}{c}{CaDiCaL} & \\multicolumn{3}{c}{Ganak} & \\multicolumn{3}{c}{ApproxMC} & \\multicolumn{2}{c}{guarantee, s} \\\\\n")
        fh.write("\\cmidrule(lr){4-5}\\cmidrule(lr){6-8}\\cmidrule(lr){9-11}\\cmidrule(lr){12-13}\n")
        fh.write("$n$ & $m$ & sat & med & max & fin & med & max & fin & med & max & $2^{n}$ & $2^{\\rhon}$ \\\\\n\\midrule\n")
        for n in sizes:
            c = S.get(("cadical", n))
            g = S.get(("ganak", n))
            a = S.get(("approxmc", n))
            m = round(RATIO * n)
            sat = sum(1 for r in rows if r["tool"] == "cadical" and r["n"] == n and r["status"] == "ok" and r["answer"] == "1")
            cells = [f"{n}", f"{m}", f"{sat}/{SEEDS}"]
            cells += [fmt_s(c[0], c[1]), fmt_s(c[2], c[3])] if c else ["---", "---"]
            for st in (g, a):
                cells += [f"{st[4]}", fmt_s(st[0], st[1]), fmt_s(st[2], st[3])] if st else ["---", "---", "---"]
            cells += [fmt_big(scale * 2.0 ** n), fmt_big(scale * 2.0 ** rho(n))]
            fh.write(" & ".join(cells) + " \\\\\n")
        fh.write("\\bottomrule\n\\end{tabular}\n")
    print("written", TAB / "practitioner.tex")
    return S, t20, scale


def write_figure(rows, meta, S, t20, scale):
    try:
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.ticker import LogLocator, NullFormatter
    except ImportError as exc:
        print("figure skipped:", exc)
        return
    # dataviz reference palette (light mode): categorical slots 1-3 for the three tools,
    # neutrals for the two guarantees (they are not measurements)
    BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
    INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d3"
    plt.rcParams.update({"font.family": "serif", "font.size": 8.5, "axes.edgecolor": INK2,
                         "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK})
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(6.6, 3.9), dpi=200)
    fig.patch.set_facecolor("white")
    N = np.linspace(20, max(SIZES), 500)
    G2 = scale * 2.0 ** N
    GR = scale * 2.0 ** np.array([rho(x) for x in N])
    series = []
    for tool, col, mk in (("cadical", BLUE, "o"), ("ganak", ORANGE, "s"), ("approxmc", AQUA, "^")):
        xs, meds, mxs, cens, mxcens = [], [], [], [], []
        for n in sorted({r["n"] for r in rows if r["tool"] == tool}):
            st = S[(tool, n)]
            xs.append(n)
            meds.append(st[0])
            mxs.append(st[2])
            cens.append(st[1])
            mxcens.append(st[3])
        series.append((tool, col, mk, np.array(xs), np.array(meds), np.array(mxs), cens, mxcens))
    label = {"cadical": "CaDiCaL 1.9.5, decision", "ganak": "Ganak 2.8.0, exact count",
             "approxmc": "ApproxMC 4.4.0, approximate count"}
    for ax, title in ((axl, "measured, with the guarantees leaving the panel"),
                      (axr, "the same, on the guarantees' scale")):
        ax.set_facecolor("#fcfcfb")
        ax.plot(N, G2, color=INK2, lw=1.5, ls=(0, (4, 3)), zorder=2, label="$2^n$ (brute force, guarantee)")
        ax.plot(N, GR, color=INK, lw=1.5, zorder=2, label="$2^{\\rho(n)}$ (verified, guarantee, $A = 1$)")
        for tool, col, mk, xs, meds, mxs, cens, mxcens in series:
            ax.plot(xs, mxs, color=col, lw=0.9, ls=":", zorder=3)
            ax.plot(xs, meds, color=col, lw=1.8, marker=mk, ms=4.5, mfc="white", mew=1.3, zorder=4, label=label[tool])
        ax.axhline(TIMEOUT, color=GRID, lw=0.8, zorder=1)
        ax.axvline(50, color=GRID, lw=0.8, zorder=1)
        ax.set_yscale("log")
        ax.set_xlim(15, max(SIZES) + 10)
        ax.grid(True, color=GRID, lw=0.5, which="major")
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.set_title(title, fontsize=8.5, color=INK2, loc="left")
    axl.set_ylim(5e-5, 3e2)
    axl.yaxis.set_major_locator(LogLocator(base=10, numticks=8))
    axl.yaxis.set_minor_formatter(NullFormatter())
    axl.text(max(SIZES) + 5, TIMEOUT * 1.3, f"{TIMEOUT:.0f} s budget", fontsize=7, color=INK2, ha="right", va="bottom")
    axl.text(52, 6e-5, "$n = 50$", fontsize=7, color=INK2, ha="left", va="bottom")
    axl.set_ylabel("seconds (solid: median; dotted: max; 20 seeds)")
    axr.set_ylim(5e-5, 1e200)
    axr.set_yticks([1e0, 1e50, 1e100, 1e150, 1e200])
    axr.yaxis.set_minor_formatter(NullFormatter())
    axr.text(52, 1e185, "$n = 50$:\n$\\rho(n) \\geq n$\nfrom here", fontsize=7, color=INK2, ha="left", va="top")
    handles, labels = axl.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=7, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.supxlabel("number of variables $n$ (random 3-CNF, $m = \\lfloor 4.26\\,n \\rceil$ clauses)", fontsize=8.5, y=0.13)
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    fig.savefig(FIG / "practitioner.pdf")
    fig.savefig(FIG / "practitioner.png")
    print("written", FIG / "practitioner.pdf")


def report(rows, meta):
    S, t20, scale = write_table(rows, meta)
    problems, ae, aa, within = checks(rows, meta)
    print(f"date {meta['date']}; {meta['versions']}")
    print(f"timeout {TIMEOUT} s; wall {meta.get('wall_s', 0):.0f} s; stopped: {meta['stopped_at']}")
    print(f"CaDiCaL median at n=20: t20 = {t20:.6f} s; common factor t20/2^20 = {scale:.3e}")
    print(f"ganak = enumeration on {ae} instances (n <= {ENUM_MAX_N}); approxmc within 1.8x of ganak on {within}/{aa}")
    for n in sorted({r["n"] for r in rows}):
        line = [f"n={n:4d}"]
        for t in TOOLS:
            st = S.get((t, n))
            if st:
                line.append(f"{t} {st[4]:2d}/{SEEDS} med {'>' if st[1] else ''}{st[0]:.4f} max {'>' if st[3] else ''}{st[2]:.4f}")
        line.append(f"2^n*s {scale * 2.0 ** n:.3g}  2^rho*s {scale * 2.0 ** rho(n):.3g}  2^(rho-n) {2.0 ** (rho(n) - n):.3g}")
        print("  ".join(line))
    # a few derived numbers the section quotes
    c500 = S.get(("cadical", 500))
    print(f"2^(rho(n)-n) at n = 50, 100, 500: {2 ** (rho(50) - 50):.3f}, {2 ** (rho(100) - 100):.3g}, {2 ** (rho(500) - 500):.3g}")
    for n in (60, 100, 200, 500):
        st = S.get(("cadical", n))
        if st:
            print(f"n={n}: measured CaDiCaL median {st[0]:.4f} s against 2^n guarantee {scale * 2 ** n:.3g} s "
                  f"({math.log10(scale * 2 ** n / st[0]):.1f} decades) and 2^rho guarantee {scale * 2 ** rho(n):.3g} s "
                  f"({math.log10(scale * 2 ** rho(n) / st[0]):.1f} decades)")
    if CLONE.exists():
        cc = clone_check()
        print(f"clone (read-only): {cc}")
        if cc["eval"] or cc["def_main"] or cc["io_actions"] or not cc["theorem_existential_in_machine"]:
            problems.append(f"clone check changed: {cc}")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  ", p)
        return 1
    print("ALL CHECKS PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", nargs=3, metavar=("TOOL", "N", "SEED"))
    ap.add_argument("--regenerate", action="store_true", help="run the measurement (about 20 min)")
    ap.add_argument("--check", action="store_true", help="verify the CSV without writing")
    a = ap.parse_args()
    if a.task:
        tool, n, seed = a.task[0], int(a.task[1]), int(a.task[2])
        print(json.dumps(run_one(tool, n, seed)))
        return 0
    if a.regenerate:
        regenerate()
    rows, meta = load()
    if a.check:
        problems, ae, aa, within = checks(rows, meta)
        print(f"ganak = enumeration on {ae}; approxmc within 1.8x on {within}/{aa}; problems {len(problems)}")
        for p in problems:
            print("  ", p)
        print("ALL CHECKS PASSED" if not problems else "CHECKS FAILED")
        return 1 if problems else 0
    rc = report(rows, meta)
    S, t20, scale = write_table(rows, meta)
    write_figure(rows, meta, S, t20, scale)
    return rc


if __name__ == "__main__":
    sys.exit(main())
