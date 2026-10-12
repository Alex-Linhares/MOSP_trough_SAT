"""W4 (Oliveira & Lorena 2002, 202 nets, dataset class pwc-04432): refute pathwidth 26.

Known: 26 <= pw <= 27 (28 tracks against 27). Two complementary attempts, one core
each, no time limit, started 2026-10-12 at the owner's request:
  A  the solver with the large minor budget (sizes 50-85%), then the full refutation;
  B  minor-heavy: sizes 50-97% in 2% steps, both rules, an effectively unlimited
     minor budget, then the full refutation.
Both start from the recorded width-27 layout (checked). Solver: the frozen committed
snapshot reports/scratch/myciel7_refute71/code_snapshot.
    python reports/scratch/w4/run.py A|B
"""
import gzip, json, sys, time
from datetime import datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "reports/scratch/myciel7_refute71/code_snapshot"))
from pathwidth.solve import solve_masks
from pathwidth.minor import MinorConfig

mode = sys.argv[1]
CFG = {"A": MinorConfig(first_nodes=1_000_000, total_nodes=500_000_000, time_fraction=0.9),
       "B": MinorConfig(first_nodes=1_000_000, total_nodes=10**15, share=1.0, max_fraction=0.97,
                        step_fraction=0.02, time_fraction=0.9)}[mode]
r = next(json.loads(l) for l in gzip.open(ROOT / "paper1/data/dataset/pathwidth_dataset.jsonl.gz", "rt")
         if json.loads(l)["id"] == "pwc-04432")
n = r["n"]
masks = [1 << v for v in range(n)]
for u, v in r["edges"]:
    masks[u] |= 1 << v; masks[v] |= 1 << u

def width_closing(order):
    placed, nb, w = 0, 0, 0
    for v in order:
        placed |= 1 << v; nb |= masks[v]; w = max(w, bin(nb & ~placed).count("1"))
    return w

order = next(o for o in (r["layout"], r["layout"][::-1]) if width_closing(o) == r["width"])
log = HERE / f"run_{mode}.log"
def say(s):
    with log.open("a") as f: f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {s}\n")
say(f"start {mode}: n={n} m={r['m']} upper {r['width']} (layout checked), refuting {r['width']-1}, {CFG}")
t = time.time()
s = solve_masks(masks, upper=r["width"], upper_order=order, minor=CFG)
rec = dict(mode=mode, width=s.width, proof=s.proof, lower=s.lower, nodes=s.nodes, seconds=round(time.time() - t, 1),
           minor=getattr(s, "minor", None), order=list(s.order))
(HERE / f"result_{mode}.json").write_text(json.dumps(rec, indent=1))
say(f"done {mode}: width={s.width} proof={s.proof!r} lower={s.lower} nodes={s.nodes} {rec['seconds']}s")
