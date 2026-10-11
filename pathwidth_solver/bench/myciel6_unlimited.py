"""myciel6 (Mycielski M7, 95 vertices, pw 38) with no time limit.

Coudert, Mazauric & Nisse (2016) prove it in about 10 minutes; our search did
not in 1,500 s (bench/results/myciel6_bettermove.log). Started 2026-10-11 to
see how long it takes. `python bench/myciel6_unlimited.py [--better-move]`;
appends one line to bench/results/myciel6_unlimited.log when done.
"""
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from readers import HERE, read_any  # noqa: E402
from pathwidth import solve  # noqa: E402

flags = {"better_move": "--better-move" in sys.argv}
G = read_any(HERE / "coloring" / "myciel6.dgf")
log = Path(__file__).resolve().parent / "results" / "myciel6_unlimited.log"
start = time.monotonic()
with log.open("a") as f:
    f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} start myciel6 {flags} n={G.number_of_nodes()}\n")
sol = solve(G, **flags)
with log.open("a") as f:
    f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} done myciel6 {flags}: width={sol.width} "
            f"proof={sol.proof!r} lower={sol.lower} nodes={sol.nodes} order={sol.order} seconds={time.monotonic() - start:.0f}\n")
