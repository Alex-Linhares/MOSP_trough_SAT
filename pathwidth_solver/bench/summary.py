"""Summarise `bench/results/*.csv` and compare with the published values.
`python bench/summary.py [SET ...]`"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import COUDERT_MYCIELSKI, COUDERT_TABLE4  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results"


def load(setname):
    p = RESULTS / f"{setname}.csv"
    if not p.exists():
        return []
    with p.open() as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for k in ("n", "m", "lower", "upper_start", "width", "nodes", "components"):
            r[k] = int(r[k]) if r[k] not in ("", None) else None
        r["seconds"] = float(r["seconds"])
    return rows


def overview(rows):
    c = Counter(r["proof"] for r in rows)
    proved = c["refutation"] + c["bound"]
    by_engine = Counter((r["engine"], r["proof"] in ("refutation", "bound")) for r in rows)
    print(f"  {len(rows)} graphs, {proved} proved ({100*proved/max(1,len(rows)):.1f}%): "
          f"{c['refutation']} by refutation, {c['bound']} by bound, {c['budget']} budget, "
          f"{sum(v for k, v in c.items() if k.startswith('error'))} errors")
    print(f"  engine C: {by_engine[('C', True)]} proved / {by_engine[('C', True)] + by_engine[('C', False)]};"
          f"  python: {by_engine[('python', True)]} proved / {by_engine[('python', True)] + by_engine[('python', False)]}")
    if rows:
        solved = [r for r in rows if r["proof"] in ("refutation", "bound")]
        if solved:
            print(f"  largest proved: n={max(r['n'] for r in solved)}; median time proved: "
                  f"{sorted(r['seconds'] for r in solved)[len(solved)//2]:.3f}s")


def coloring(rows):
    print("\n  vs Coudert et al. 2016 Table 4 (their pw, their seconds):")
    print(f"  {'graph':12s} {'n':>4s} {'ours pw':>7s} {'proof':11s} {'ours s':>9s} | {'C&al pw':>7s} {'C&al s':>8s}")
    byname = {r["name"]: r for r in rows}
    for name, (pw, sec) in sorted(COUDERT_TABLE4.items()):
        r = byname.get(name)
        if r is None:
            print(f"  {name:12s}  (not run)")
            continue
        flag = "" if r["width"] == pw else ("  ** differs" if r["proof"] in ("refutation", "bound") else "  (ub)")
        print(f"  {name:12s} {r['n']:4d} {r['width']!s:>7} {r['proof']:11s} {r['seconds']:9.3f} | {pw:7d} {sec:8.3f}{flag}")
    print("\n  Mycielski (Coudert Table 1):")
    for name, pw in COUDERT_MYCIELSKI.items():
        r = byname.get(name)
        if r:
            print(f"  {name:12s} n={r['n']:<4d} ours pw={r['width']} {r['proof']:11s} {r['seconds']:8.1f}s | C&al {pw if pw is not None else '<= 72 (open)'}")
    others = [r for r in rows if r["name"] not in COUDERT_TABLE4 and r["name"] not in COUDERT_MYCIELSKI and r["proof"] in ("refutation", "bound")]
    if others:
        print(f"\n  also proved, not in their table: " + ", ".join(f"{r['name']}={r['width']}" for r in sorted(others, key=lambda r: r['n'])))


def grids(rows):
    print("\n  VSPLIB grids (pw = side; Coudert et al. exact for side <= 13):")
    ok = [r for r in rows if r["proof"] in ("refutation", "bound")]
    sides = sorted(int(r["name"].split("_")[1]) for r in ok)
    print(f"  proved: sides {sides}")
    bad = [r for r in ok if r["width"] != int(r["name"].split("_")[1])]
    print(f"  wrong widths: {[(r['name'], r['width']) for r in bad]}")
    ub_ok = sum(1 for r in rows if r["width"] == int(r["name"].split("_")[1]))
    print(f"  best value equals the side on {ub_ok}/{len(rows)} grids (C&al: all)")


def trees(rows):
    print("\n  VSPLIB trees (pw 3/4/5 for 22/67/202 nodes; Coudert et al. exact for n <= 67):")
    for n in sorted({r["n"] for r in rows}):
        sub = [r for r in rows if r["n"] == n]
        proved = sum(1 for r in sub if r["proof"] in ("refutation", "bound"))
        widths = Counter(r["width"] for r in sub)
        print(f"  n={n:<4d} {len(sub)} trees, {proved} proved, widths found {dict(widths)}")


def hb(rows):
    print("\n  VSPLIB hb (Coudert et al.: 26 of 73 proved):")
    ok = sorted((r for r in rows if r["proof"] in ("refutation", "bound")), key=lambda r: r["n"])
    print(f"  proved {len(ok)}/{len(rows)}: " + ", ".join(f"{r['name']}(n={r['n']},pw={r['width']})" for r in ok))


def rome(rows):
    print("\n  Rome graphs (Coudert et al.: 95.6% in 10 min, all n <= 82 solved):")
    ok = [r for r in rows if r["proof"] in ("refutation", "bound")]
    print(f"  proved {len(ok)}/{len(rows)} = {100*len(ok)/max(1,len(rows)):.1f}%")
    unsolved = Counter(r["n"] for r in rows if r["proof"] not in ("refutation", "bound"))
    if unsolved:
        print(f"  unsolved by n: {dict(sorted(unsolved.items()))}")
        print(f"  smallest unsolved n = {min(unsolved)}")


SPECIAL = {"coloring": coloring, "vsplib-grids": grids, "vsplib-tree": trees, "vsplib-hb": hb, "rome": rome}

if __name__ == "__main__":
    sets = sys.argv[1:] or ["named", "coloring", "vsplib-grids", "vsplib-tree", "vsplib-hb", "rome"]
    for s in sets:
        rows = load(s)
        print(f"\n== {s}: " + ("(no results yet)" if not rows else ""))
        if rows:
            overview(rows)
            if s in SPECIAL:
                SPECIAL[s](rows)
