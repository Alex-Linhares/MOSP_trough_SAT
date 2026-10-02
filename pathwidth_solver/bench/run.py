"""Benchmark runner: `python bench/run.py SET [--time 600] [--procs 32]`.

Writes `bench/results/SET.csv` incrementally (one row per graph as it
finishes) and prints a summary. Graphs above `native.MAX_VERTICES` vertices
run on the Python search (the C declines), which the `engine` column records.

The result file follows MOSP's conventions (fixed 2026-10-02, loop0007 item 08,
the two issues `TRANSFER.md` lists):

- `name` is the instance's path relative to `bench/instances/`, so the
  VSPLIB trees in the three rotation folders keep distinct keys;
- `proof` is `refutation` or `bound` for a proved width and **empty** for an
  unproved one. An exception goes to the `error` column, not into `proof`.

`rules` records the dominance rules the search ran with: `repaired` (the
default since 2026-10-01, the premises proved sound in
`lean/MOSPFormalization/Search/`) or `published` (Chu & Stuckey's, kept for
comparison). Each graph runs in its own process and is killed after `--hard`
seconds, because the Python path does not check the budget during its initial
upper bound. `--resume` appends to an existing file and skips the names in it.
"""

from __future__ import annotations

import argparse
import csv
import multiprocessing as mp
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from readers import HERE, SETS, read_any  # noqa: E402

FIELDS = ["set", "name", "n", "m", "engine", "rules", "lower", "upper_start", "width", "proof",
          "nodes", "seconds", "components", "error"]
PROVED = ("refutation", "bound")


def key(path: Path) -> str:
    """The result key: the path relative to `bench/instances/`."""
    return path.resolve().relative_to(HERE.resolve()).as_posix()


def stem(name: str) -> str:
    """The old key (file stem, `.mtx` dropped), for `--names` and comparisons."""
    return Path(name).stem.replace(".mtx", "")


def one(setname: str, path: Path, time_limit: float, rules: str) -> dict:
    import networkx as nx
    from pathwidth import solve
    from pathwidth.native import MAX_VERTICES
    G = read_any(path)
    n, m = G.number_of_nodes(), G.number_of_edges()
    biggest = max((len(c) for c in nx.connected_components(G)), default=0)
    row = dict(set=setname, name=key(path), n=n, m=m, rules=rules,
               engine="C" if biggest <= MAX_VERTICES else "python", error="")
    t = time.perf_counter()
    try:
        sol = solve(G, time_budget=time_limit, repaired_rules=(rules == "repaired"))
        row.update(lower=sol.lower, upper_start=sol.upper_start, width=sol.width,
                   proof=sol.proof if sol.proof in PROVED else "", nodes=sol.nodes,
                   components=len(sol.components) or 1)
    except Exception as exc:  # keep the sweep alive
        row.update(lower="", upper_start="", width="", proof="", nodes="", components="",
                   error=f"{type(exc).__name__}: {exc}"[:80])
    row["seconds"] = round(time.perf_counter() - t, 3)
    return row


def _child(args, queue):
    queue.put(one(*args))


def _warm() -> None:
    """Build the C engines in the parent, so forked workers do not race to."""
    import networkx as nx
    from pathwidth import solve
    for n in (10, 200, 300, 600, 1000):
        solve(nx.path_graph(n), time_budget=5)


def run(tasks, procs: int, hard: float):
    """Yield one row per task, at most `procs` processes at once."""
    ctx = mp.get_context("fork")
    pending = list(reversed(tasks))
    live: dict = {}
    while pending or live:
        while pending and len(live) < procs:
            args = pending.pop()
            q = ctx.Queue()
            p = ctx.Process(target=_child, args=(args, q), daemon=True)
            p.start()
            live[p] = (args, q, time.monotonic())
        time.sleep(0.005)
        for p in list(live):
            args, q, started = live[p]
            row = None
            try:
                row = q.get_nowait()
            except Exception:
                pass
            if row is not None:
                p.join()
            elif not p.is_alive() or time.monotonic() - started > hard:
                if p.is_alive():
                    p.kill()
                p.join()
                try:
                    row = q.get(timeout=0.5)
                except Exception:
                    setname, path, _, rules = args
                    row = dict(set=setname, name=key(path), n="", m="", engine="", rules=rules,
                               lower="", upper_start="", width="", proof="", nodes="",
                               seconds=round(time.monotonic() - started, 3), components="",
                               error=f"killed after {hard:.0f} s" if p.exitcode and p.exitcode < 0
                               else f"exit {p.exitcode}")
            if row is not None:
                q.close()
                del live[p]
                yield row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("set", choices=sorted(SETS))
    ap.add_argument("--time", type=float, default=600.0, help="per-graph wall-clock budget (s)")
    ap.add_argument("--hard", type=float, default=None,
                    help="kill a graph after this many seconds (default 1.5 x --time + 120)")
    ap.add_argument("--procs", type=int, default=min(32, mp.cpu_count()))
    ap.add_argument("--limit", type=int, default=None, help="only the first N graphs")
    ap.add_argument("--out", default=None)
    ap.add_argument("--names", default=None,
                    help="file with one graph per line, as a path key or a file stem: run only those")
    ap.add_argument("--rules", choices=("repaired", "published"), default="repaired")
    ap.add_argument("--resume", action="store_true", help="append, skipping names already in --out")
    a = ap.parse_args()
    paths = SETS[a.set]()
    if a.names:
        wanted = set(Path(a.names).read_text().split())
        paths = [p for p in paths if key(p) in wanted or stem(key(p)) in wanted]
    if a.limit:
        paths = paths[:a.limit]
    out = Path(a.out) if a.out else Path(__file__).resolve().parent / "results" / f"{a.set}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    done_names: set = set()
    if a.resume and out.exists():
        with out.open() as fh:
            done_names = {r["name"] for r in csv.DictReader(fh)}
        paths = [p for p in paths if key(p) not in done_names]
    hard = a.hard if a.hard is not None else 1.5 * a.time + 120
    _warm()
    started = time.time()
    done = proved = 0
    fresh = not (a.resume and out.exists())
    with out.open("w" if fresh else "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if fresh:
            w.writeheader()
        for row in run([(a.set, p, a.time, a.rules) for p in paths], a.procs, hard):
            w.writerow(row)
            fh.flush()
            done += 1
            proved += row["proof"] in PROVED
            if a.set != "rome" or done % 100 == 0 or a.names:
                print(f"[{done}/{len(paths)}] {stem(row['name']):24s} n={row['n']!s:<4} pw={row['width']!s:>3} "
                      f"{row['proof'] or row['error'] or 'unproved':11s} {row['nodes']!s:>12} "
                      f"{row['seconds']:>8}s {row['engine']}", flush=True)
    print(f"done: {done} graphs, {proved} proved, {time.time()-started:.0f}s wall -> {out}")


if __name__ == "__main__":
    main()
