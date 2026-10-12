"""The new descent (minor step on, 60 s per graph) against the recorded runs
without it (pathwidth_solver/bench/results/repaired/, up to 600 s per graph;
Rome in stages of 10, 120 and 600 s). Node counts without the step are
deterministic and equal to the baseline's on every graph proved by both, so
the node comparison is exactly paired; seconds are not (shared machine).

usage: vs_baseline.py SET[=onfile]..."""
import csv, statistics, sys
from pathlib import Path
HERE = Path(__file__).parent
BASE = HERE.parents[2] / "pathwidth_solver" / "bench" / "results" / "repaired"
PROVED = ("refutation", "minor", "bound")


def baseline(setname):
    if setname.startswith("rome"):
        rows = {}
        for f in ("rome.csv", "rome_120s.csv", "rome_600s.csv"):
            for r in csv.DictReader(open(BASE / f)):
                if r["name"] not in rows or r["proof"] in PROVED:
                    rows[r["name"]] = r
        return rows
    return {r["name"]: r for r in csv.DictReader(open(BASE / f"{setname}.csv"))}


for arg in sys.argv[1:]:
    setname, _, onfile = arg.partition("=")
    on = {r["name"]: r for r in csv.DictReader(open(HERE / (onfile or f"bench_{setname}_on.csv")))}
    base = baseline(setname)
    names = [n for n in on if n in base]
    pb = {n for n in names if base[n]["proof"] in PROVED}
    po = {n for n in names if on[n]["proof"] in PROVED}
    both = sorted(pb & po)
    bad = [n for n in both if on[n]["width"] != base[n]["width"]]
    gained, lost = sorted(po - pb), sorted(pb - po)
    ratio = [int(on[n]["nodes"]) / max(1, int(base[n]["nodes"])) for n in both]
    nb = sum(int(base[n]["nodes"]) for n in both); no = sum(int(on[n]["nodes"]) for n in both)
    fired = [n for n in both if int(on[n]["minor_nodes"] or 0) > 0]
    print(f"== {setname}: {len(names)} graphs; baseline (<=600 s) proved {len(pb)}, new (60 s) {len(po)}: "
          f"+{len(gained)} / -{len(lost)}; width disagreements {len(bad)}; minor proofs {sum(on[n]['proof']=='minor' for n in names)}")
    if both:
        print(f"   proved by both {len(both)}: nodes {nb:,} -> {no:,} ({no/max(nb,1)-1:+.1%}); step ran on {len(fired)}; "
              f"median node ratio where it ran {statistics.median([int(on[n]['nodes'])/max(1,int(base[n]['nodes'])) for n in fired]) if fired else 1:.2f}")
    if gained:
        secs = sorted(float(on[n]["seconds"]) for n in gained)
        print(f"   gained: median {statistics.median(secs):.1f} s, max {secs[-1]:.1f} s; "
              f"under 10 s {sum(s < 10 for s in secs)}")
        for n in gained[:12]:
            print(f"     + {n} n={on[n]['n']} pw={on[n]['width']} {on[n]['proof']} {on[n]['seconds']} s "
                  f"(baseline lower {base[n]['lower']}, width {base[n]['width']})")
    for n in lost:
        print(f"     - {n} n={on[n]['n']} baseline {base[n]['width']} {base[n]['proof']} {base[n]['seconds']} s "
              f"| new {on[n]['width']} lower {on[n]['lower']}")
    up = [n for n in names if n not in po and n not in pb and on[n]["lower"] and base[n]["lower"]
          and int(on[n]["lower"]) > int(base[n]["lower"])]
    if up:
        print(f"   lower bound raised on {len(up)} still open: " + ", ".join(
            f"{Path(n).stem} {base[n]['lower']}->{on[n]['lower']} (ub {on[n]['width']})" for n in up[:12]))
    worst = sorted(both, key=lambda n: int(on[n]["nodes"]) - int(base[n]["nodes"]), reverse=True)[:5]
    for n in worst:
        d = int(on[n]["nodes"]) - int(base[n]["nodes"])
        if d > 0:
            print(f"     slow {n} n={on[n]['n']} nodes {int(base[n]['nodes']):,} -> {int(on[n]['nodes']):,} "
                  f"(+{d:,}; minor {int(on[n]['minor_nodes'] or 0):,}) {base[n]['seconds']} s -> {on[n]['seconds']} s")
