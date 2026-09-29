"""End-to-end check made when `rule+cs-dfs` became the default (2026-09-28).

On 300 certified corpus instances at n <= 40 (seed 7), run the complete
customer-search descent (`customer_search.solve`) under the old seed
(`cs-dfs`) and the new default (`rule+cs-dfs`), and confirm both certify the
stored optimum. Reports the total seconds of each. Reads `solutions/`, never
writes it.

    PYTHONPATH=. python -m learning.rule_seed_descent_check
"""
import json
import multiprocessing as mp
import random
import time

from learning import dataset as ds
from satisfiability.customer_search import solve
from satisfiability.mosp_solver import SOLUTIONS_DIR, _solution_path


def job(inst):
    cert = json.load(open(_solution_path(inst, SOLUTIONS_DIR)))["mosp_value"]
    t = time.perf_counter()
    a = solve(inst, upper_strategy="cs-dfs")
    ta = time.perf_counter() - t
    t = time.perf_counter()
    b = solve(inst)
    tb = time.perf_counter() - t
    return (inst.name, cert, a.value, b.value, ta, tb)


if __name__ == "__main__":
    items = ds.enumerate_instances(ds.DEFAULT_INSTANCE_DIR)
    insts = [inst for _, inst in items if inst.n_customers <= 40]
    random.seed(7)
    sample = random.sample(insts, 300)
    with mp.get_context("fork").Pool(12) as pool:
        rows = pool.map(job, sample, chunksize=5)
    bad = [r for r in rows if not (r[1] == r[2] == r[3])]
    print(f"instances {len(rows)} | equal to certified under both seeds: "
          f"{len(rows) - len(bad)} | mismatches: {len(bad)}")
    for r in bad[:5]:
        print("  MISMATCH", r)
    print(f"total seconds: old seed {sum(r[4] for r in rows):.1f} | "
          f"new seed {sum(r[5] for r in rows):.1f}")
