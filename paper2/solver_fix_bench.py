"""loop0007 item 08: the pathwidth benchmarks under the repaired rules.

    python paper2/solver_fix_bench.py run [--lane rome|other|all]
    python paper2/solver_fix_bench.py compare

`run` reruns `pathwidth_solver/bench/run.py` on every set at the caps of the
first sweep (2026-09-27/28, `pathwidth_solver/PLAN.md` §3 and phase 6b), with
the repaired default (`--rules repaired`), into
`pathwidth_solver/bench/results/repaired/`:

- coloring, VSPLIB grids / hb / trees: 600 s per graph;
- named: 120 s per graph, then the graphs above 128 vertices at 600 s, as the
  `_w` rerun did (`named_w.csv`);
- Rome: 10 s for all 11,534, then the unproved at 120 s, then those still
  unproved at 600 s.

Every stage appends with `--resume`, so `run` continues where its CSVs stop.

`compare` joins the new rows with the old results (the base file, overridden by
the `_w` rerun for graphs that had fallen to the Python path, and Rome's
120 s and 600 s passes) and writes `paper2/data/solver_fix_bench.csv` and
`paper2/data/solver_fix_bench_tables.md`. The old files key graphs by stem and
the three VSPLIB tree folders reuse stems, so trees are compared against the
width their name encodes (`TREE_<n>_<width>_rot<i>`), which is the known
pathwidth (Ellis, Sudborough & Turner), and against the old row of that stem.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PW = ROOT / "pathwidth_solver"
OLD = PW / "bench" / "results"
NEW = OLD / "repaired"
DATA = ROOT / "paper2" / "data"
PROVED = ("refutation", "bound")

OTHER = [("coloring", 600, None, "coloring.csv"),
         ("vsplib-grids", 600, None, "vsplib-grids.csv"),
         ("vsplib-hb", 600, None, "vsplib-hb.csv"),
         ("vsplib-tree", 600, None, "vsplib-tree.csv"),
         ("named", 120, None, "named.csv"),
         ("named", 600, OLD / "named_python_path.txt", "named_w.csv")]


def stem(name: str) -> str:
    return Path(name).stem.replace(".mtx", "")


def rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as fh:
        return list(csv.DictReader(fh))


def bench(setname, cap, names, out, procs):
    cmd = [sys.executable, str(PW / "bench" / "run.py"), setname, "--time", str(cap),
           "--procs", str(procs), "--rules", "repaired", "--resume", "--out", str(NEW / out)]
    if names:
        cmd += ["--names", str(names)]
    print(time.strftime("%H:%M:%S"), " ".join(cmd[1:]), flush=True)
    subprocess.run(cmd, check=True, cwd=PW)


def unproved(out: str) -> Path:
    names = sorted(r["name"] for r in rows(NEW / out) if r["proof"] not in PROVED)
    p = NEW / (Path(out).stem + "_unproved.txt")
    p.write_text("\n".join(names) + "\n")
    return p


def lane_rome(procs, wait_for: Path | None, procs_last):
    bench("rome", 10, None, "rome.csv", procs)
    bench("rome", 120, unproved("rome.csv"), "rome_120s.csv", procs)
    still = unproved("rome_120s.csv")
    while wait_for is not None and not wait_for.exists():
        time.sleep(30)
    bench("rome", 600, still, "rome_600s.csv", procs_last)


def lane_other(procs):
    for setname, cap, names, out in OTHER:
        bench(setname, cap, names, out, procs)
    (NEW / "other.done").write_text(time.strftime("%Y-%m-%d %H:%M:%S\n"))


# ---------------------------------------------------------------- compare

def latest(paths: list[Path], key) -> dict:
    """Later files override earlier ones, row by row."""
    out: dict = {}
    for p in paths:
        for r in rows(p):
            out[key(r)] = r
    return out


def old_table() -> dict[tuple[str, str], dict]:
    """Old final result per (set, stem): base file, then `_w`, then Rome passes."""
    table = {}
    for s in ("coloring", "named", "vsplib-grids", "vsplib-hb", "vsplib-tree"):
        for k, r in latest([OLD / f"{s}.csv", OLD / f"{s}_w.csv"], lambda r: r["name"]).items():
            table[(s, k)] = r
    for k, r in latest([OLD / "rome.csv", OLD / "rome_capped_120s.csv", OLD / "rome_capped_600s.csv"],
                       lambda r: r["name"]).items():
        table[("rome", k)] = r
    return table


def new_table() -> dict[tuple[str, str], dict]:
    table = {}
    files = {"coloring": ["coloring.csv"], "named": ["named.csv", "named_w.csv"],
             "vsplib-grids": ["vsplib-grids.csv"], "vsplib-hb": ["vsplib-hb.csv"],
             "vsplib-tree": ["vsplib-tree.csv"], "rome": ["rome.csv", "rome_120s.csv", "rome_600s.csv"]}
    for s, fs in files.items():
        for k, r in latest([NEW / f for f in fs], lambda r: r["name"]).items():
            table[(s, k)] = r
    return table


def compare():
    old, new = old_table(), new_table()
    joined = []
    shared = Counter((s, stem(n)) for s, n in new)
    for (s, name), r in sorted(new.items()):
        st = stem(name)
        o = dict(old.get((s, st), {}))
        if shared[(s, st)] > 1 and o:
            # the old files cannot say which of the same-stem files this row was:
            # keep its width (the stems share it, the name encodes it), drop its cost
            o["nodes"] = o["seconds"] = ""
        known = ""
        if s == "vsplib-tree":
            known = st.split("_")[2]
        row = dict(set=s, name=name, n=r["n"], m=r["m"], engine=r["engine"],
                   new_width=r["width"], new_proof=r["proof"], new_nodes=r["nodes"],
                   new_seconds=r["seconds"], new_error=r["error"],
                   old_width=o.get("width", ""), old_proof=(o.get("proof", "") if o.get("proof") in PROVED else ""),
                   old_nodes=o.get("nodes", ""), old_seconds=o.get("seconds", ""), known_width=known)
        both = row["new_proof"] and row["old_proof"]
        row["status"] = ("both proved, same width" if both and row["new_width"] == row["old_width"] else
                         "BOTH PROVED, WIDTH DIFFERS" if both else
                         "proved new only" if row["new_proof"] else
                         "proved old only" if row["old_proof"] else "proved neither")
        if row["new_proof"] and known and row["new_width"] != known:
            row["status"] = "NEW PROVED WIDTH != KNOWN"
        if row["new_proof"] and row["old_width"] and not row["old_proof"] and int(row["new_width"]) > int(row["old_width"]):
            row["status"] = "NEW PROVED WIDTH ABOVE OLD UPPER BOUND"
        if row["old_proof"] and row["new_width"] and not row["new_proof"] and int(row["new_width"]) < int(row["old_width"]):
            row["status"] = "NEW UPPER BOUND BELOW OLD PROVED WIDTH"
        joined.append(row)
    DATA.mkdir(exist_ok=True)
    with (DATA / "solver_fix_bench.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(joined[0]))
        w.writeheader()
        w.writerows(joined)
    seen = {(s, stem(n)) for s, n in new}
    missing = sorted(k for k in old if k[0] != "vsplib-tree" and k not in seen)
    tables(joined, missing)


def tables(joined, missing):
    lines = ["# loop0007 item 08: pathwidth benchmarks, repaired rules against the old results", "",
             "Regenerate: `python paper2/solver_fix_bench.py compare` (after `run`).", ""]
    by = defaultdict(list)
    for r in joined:
        by[r["set"]].append(r)
    lines += ["| set | graphs | proved old | proved new | both | same width | width differs | new only | old only |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    tot = Counter()
    for s in ("coloring", "named", "vsplib-grids", "vsplib-hb", "vsplib-tree", "rome"):
        rs = by[s]
        c = Counter(r["status"] for r in rs)
        po = sum(bool(r["old_proof"]) for r in rs)
        pn = sum(bool(r["new_proof"]) for r in rs)
        both = sum(bool(r["old_proof"] and r["new_proof"]) for r in rs)
        diff = sum(v for k, v in c.items() if k.isupper() or "DIFFERS" in k or "!=" in k)
        vals = (len(rs), po, pn, both, c["both proved, same width"], diff, c["proved new only"], c["proved old only"])
        tot.update(dict(zip("abcdefgh", vals)))
        lines.append(f"| {s} | " + " | ".join(f"{v:,}" for v in vals) + " |")
    lines.append("| **all** | " + " | ".join(f"**{tot[k]:,}**" for k in "abcdefgh") + " |")
    lines += ["", "Findings (any row here is a changed width or a contradiction):", ""]
    bad = [r for r in joined if r["status"].isupper() or "DIFFERS" in r["status"]]
    lines += [f"- {r['set']} `{r['name']}`: {r['status']} (old {r['old_width']} {r['old_proof']}, "
              f"new {r['new_width']} {r['new_proof']}, known {r['known_width']})" for r in bad] or ["- none"]
    trees = [r for r in joined if r["set"] == "vsplib-tree"]
    lines += ["", f"VSPLIB trees: {sum(r['new_proof'] != '' for r in trees)} of {len(trees)} proved, "
              f"{sum(r['new_proof'] != '' and r['new_width'] == r['known_width'] for r in trees)} at the width "
              "the name encodes."]
    flips = [r for r in joined if r["status"] in ("proved new only", "proved old only")]
    if flips:
        lines += ["", "Proved on one side only (a cap effect, not a width change):", "",
                  "| set | graph | n | old | old s | new | new s |", "|---|---|---:|---|---:|---|---:|"]
        lines += [f"| {r['set']} | {stem(r['name'])} | {r['n']} | {r['old_width']} {r['old_proof'] or 'ub'} | "
                  f"{r['old_seconds']} | {r['new_width']} {r['new_proof'] or 'ub'} | {r['new_seconds']} |"
                  for r in sorted(flips, key=lambda r: (r["set"], r["status"], r["name"]))]
    # nodes on graphs proved by refutation under both, single-pass comparable
    lines += ["", "Nodes where both sides proved by refutation (sum new / sum old; median and worst pair ratio):", "",
              "| set | pairs | nodes old | nodes new | ratio | median | max | min |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for s in ("coloring", "named", "vsplib-grids", "vsplib-hb", "vsplib-tree", "rome"):
        ps = [(int(r["old_nodes"]), int(r["new_nodes"])) for r in by[s]
              if r["old_proof"] == "refutation" and r["new_proof"] == "refutation" and r["old_nodes"] and r["new_nodes"]]
        rat = sorted(b / a for a, b in ps if a > 0)
        if not ps:
            continue
        so, sn = sum(a for a, _ in ps), sum(b for _, b in ps)
        lines.append(f"| {s} | {len(ps):,} | {so:,} | {sn:,} | {sn / so:.4f} | {rat[len(rat)//2]:.4f} | "
                     f"{rat[-1]:.3f} | {rat[0]:.3f} |")
    settle = {stem(r["name"]): r for r in rows(NEW / "rome_3600s.csv")}
    olds = [r for r in joined if r["status"] == "proved old only"]
    if olds:
        lines += ["", "The graphs proved by the old run only, rerun under the repaired rules at 3,600 s "
                  "(`rome_3600s.csv`; a longer cap than the like-for-like table above):", "",
                  "| graph | n | old width | old nodes | old s | new width | proof | new nodes | new s | nodes new/old |",
                  "|---|---:|---:|---:|---:|---:|---|---:|---:|---:|"]
        for r in sorted(olds, key=lambda r: r["name"]):
            t = settle.get(stem(r["name"]))
            if t is None:
                lines.append(f"| {stem(r['name'])} | {r['n']} | {r['old_width']} | {r['old_nodes']} | {r['old_seconds']} "
                             "| not run | | | | |")
                continue
            ratio = (f"{int(t['nodes']) / int(r['old_nodes']):.3f}" if t["nodes"] and r["old_nodes"] else "")
            flag = "" if not t["proof"] or t["width"] == r["old_width"] else " **DIFFERS**"
            lines.append(f"| {stem(r['name'])} | {r['n']} | {r['old_width']} | {r['old_nodes']} | {r['old_seconds']} | "
                         f"{t['width']}{flag} | {t['proof'] or 'unproved'} | {t['nodes']} | {t['seconds']} | {ratio} |")
    errs = [r for r in joined if r["new_error"]]
    lines += ["", f"Errors or kills in the new run: {len(errs)}"]
    lines += [f"- {r['set']} `{r['name']}`: {r['new_error']}" for r in errs]
    lines += ["", f"Old graphs with no new row: {len(missing)}"] + [f"- {s} {n}" for s, n in missing[:50]]
    (DATA / "solver_fix_bench_tables.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("run", "compare"))
    ap.add_argument("--lane", choices=("rome", "other", "all"), default="all")
    a = ap.parse_args()
    NEW.mkdir(parents=True, exist_ok=True)
    if a.stage == "compare":
        compare()
    elif a.lane == "rome":
        lane_rome(16, NEW / "other.done", 24)
    elif a.lane == "other":
        lane_other(8)
    else:
        lane_other(24)
        lane_rome(24, None, 24)


if __name__ == "__main__":
    main()
