"""On/off comparison of bench_<set>_{on,off}.csv: proofs gained and lost,
time and nodes on graphs both prove, and the worst slowdowns.
usage: compare_sets.py SET..."""
import csv, sys
from pathlib import Path
HERE = Path(__file__).parent
PROVED = ("refutation", "minor", "bound")
for s in sys.argv[1:]:
    try:
        on = {r["name"]: r for r in csv.DictReader(open(HERE / f"bench_{s}_on.csv"))}
        off = {r["name"]: r for r in csv.DictReader(open(HERE / f"bench_{s}_off.csv"))}
    except FileNotFoundError:
        continue
    names = sorted(set(on) & set(off))
    p_on = [n for n in names if on[n]["proof"] in PROVED]
    p_off = [n for n in names if off[n]["proof"] in PROVED]
    gained = [n for n in p_on if n not in p_off]
    lost = [n for n in p_off if n not in p_on]
    both = [n for n in p_on if n in p_off]
    bad = [n for n in both if on[n]["width"] != off[n]["width"]]
    t_on = sum(float(on[n]["seconds"]) for n in both); t_off = sum(float(off[n]["seconds"]) for n in both)
    fired = [n for n in both if int(on[n]["minor_nodes"] or 0) > 0 or on[n]["proof"] == "minor"]
    lower_up = [n for n in names if on[n]["proof"] not in PROVED and off[n]["proof"] not in PROVED
                and on[n]["lower"] and off[n]["lower"] and int(on[n]["lower"]) > int(off[n]["lower"])]
    print(f"== {s}: {len(names)} graphs; proved off {len(p_off)}, on {len(p_on)}; gained {len(gained)}, lost {len(lost)}; "
          f"width disagreements {len(bad)}; minor proofs {sum(on[n]['proof']=='minor' for n in names)}")
    print(f"   both proved {len(both)}: {t_off:.1f} s off, {t_on:.1f} s on; step fired on {len(fired)}; "
          f"lower raised on unproved {len(lower_up)}")
    for n in gained:
        print(f"   + {n} n={on[n]['n']} pw={on[n]['width']} {on[n]['proof']} {on[n]['seconds']}s "
              f"(off: {off[n]['width']} lower {off[n]['lower']})")
    for n in lost:
        print(f"   - {n} n={on[n]['n']} off {off[n]['width']} {off[n]['proof']} {off[n]['seconds']}s | on {on[n]['width']} lower {on[n]['lower']}")
    for n in lower_up:
        print(f"   ^ {n} n={on[n]['n']} width {on[n]['width']} lower {off[n]['lower']} -> {on[n]['lower']}")
    slow = sorted(both, key=lambda n: float(on[n]["seconds"]) - float(off[n]["seconds"]), reverse=True)[:5]
    for n in slow:
        print(f"   slow {n} n={on[n]['n']} off {off[n]['seconds']}s {off[n]['nodes']} | on {on[n]['seconds']}s "
              f"{on[n]['nodes']} (minor {on[n]['minor_nodes']}) {on[n]['proof']}")
