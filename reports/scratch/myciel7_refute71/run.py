"""myciel7: refute pathwidth <= 71 with our proposed solver (minor step on), one core, no limit.

Known: 71 <= pw(myciel7) <= 72 (minor lower bound, reports/minor_bound_verification.md;
width-72 layout, reports/scratch/minor_certificates/myciel7_w72_order.txt). This
runs the descent from that layout (upper = 72), so its only question is k = 71:
the minor step first, then the full refutation, with no node or time cap.
Uses a frozen snapshot of the committed solver (code_snapshot/, commit in
code_snapshot/COMMIT), with the large minor budget. First launched 03:20 on the
default budget; relaunched 2026-10-12 with the large one.
    python reports/scratch/myciel7_refute71/run.py
"""
import json, sys, time
from datetime import datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE / "code_snapshot"))
from pathwidth.solve import solve_masks
from pathwidth.minor import MinorConfig

# The owner's decision (2026-10-12): long runs on unsolved problems use the large minor budget.
LARGE = MinorConfig(first_nodes=1_000_000, total_nodes=500_000_000, time_fraction=0.9)

C = ROOT / "reports/scratch/minor_certificates"
lines = (C / "myciel7_full_edges.txt").read_text().split("\n")
n, m = map(int, lines[0].split())
edges = [tuple(map(int, l.split())) for l in lines[1:] if l.strip()]
assert len(edges) == m == 2360 and n == 191
# the edge list is myciel7.dgf relabelled 0-based: check it
dgf = [tuple(int(x) - 1 for x in l.split()[1:3]) for l in
       (ROOT / "pathwidth_solver/bench/instances/coloring/myciel7.dgf").read_text().splitlines() if l.startswith("e ")]
assert {frozenset(e) for e in dgf} == {frozenset(e) for e in edges}
masks = [1 << v for v in range(n)]
for u, v in edges:
    masks[u] |= 1 << v; masks[v] |= 1 << u
order = list(map(int, (C / "myciel7_w72_order.txt").read_text().split()))
# width of the layout, recomputed here in the search's convention (closing order):
# after each prefix S, the unplaced vertices with a neighbour in S. The same
# number is the vertex separation of the reversed order.
placed, width = 0, 0
for v in order:
    placed |= 1 << v
    nb = 0
    for u in range(n):
        if placed >> u & 1:
            nb |= masks[u]
    width = max(width, bin(nb & ~placed).count("1"))
assert width == 72, width
log = HERE / "run.log"
def say(s):
    with log.open("a") as f: f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {s}\n")
say("start: upper 72 from the stored layout (checked), refuting 71, large minor budget, no limit")
t = time.time()
sol = solve_masks(masks, upper=72, upper_order=order, minor=LARGE)
rec = dict(width=sol.width, proof=sol.proof, lower=sol.lower, nodes=sol.nodes,
           minor_nodes=getattr(sol, "minor_nodes", None), seconds=round(time.time() - t, 1),
           minor=getattr(sol, "minor", None), order=list(sol.order))
(HERE / "result.json").write_text(json.dumps(rec, indent=1))
say(f"done: width={sol.width} proof={sol.proof!r} lower={sol.lower} nodes={sol.nodes} {rec['seconds']}s")
