"""The MOSP descent with the minor step on the hard corpus instances the
survey names, end to end through `solve_mosp_exact` with a scratch
solutions_dir (nothing is written to solutions/).

usage: mosp_corpus.py CONFIG TIME [NAMES...]   CONFIG in off, default, large,
optionally suffixed "@recorded": then the descent starts from the recorded
optimum as its upper bound (as a re-certification does, from the stored
witness), through `customer_search.solve` with the `_lower_bound` floor.
"""
import json, sys, tempfile, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from benchmarks.ratchet import find_instances
from satisfiability.mosp_solver import solve_mosp_exact
from satisfiability.relaxation import MinorConfig

CONFIGS = {"off": False, "default": MinorConfig(),
           "large": MinorConfig(first_nodes=1_000_000, total_nodes=500_000_000, time_fraction=0.9)}
NAMES = ["Random-125-125-2-1_0", "Random-125-125-2-3_0", "Random-125-125-6-1_0",
         "Random-125-125-4-1_0", "Random-125-125-8-2_0", "SP4"]
config, budget = sys.argv[1], float(sys.argv[2])
from_recorded = config.endswith("@recorded")
config = config.removesuffix("@recorded")
names = sys.argv[3:] or NAMES
scratch = Path(tempfile.mkdtemp(prefix="minor_bound_solutions_"))
for name in names:
    inst = next(i for i in find_instances([name], ROOT / "benchmarks/instances") if i.name == name)
    recorded = json.loads((ROOT / "solutions" / f"{name}.json").read_text())["mosp_value"]
    stats = {}
    t = time.time()
    if from_recorded:
        from satisfiability.customer_search import solve
        from satisfiability.mosp_solver import _lower_bound
        floor = _lower_bound(inst)
        s = solve(inst, upper=recorded, lower=floor, minor=CONFIGS[config], time_budget=budget)
        cert = s.minor
        print(json.dumps(dict(instance=name, config=config + "@recorded", budget=budget, recorded=recorded,
                              value=s.value, proof=s.proof, floor=floor, lower=s.lower, nodes=s.nodes,
                              minor_nodes=s.minor_nodes, minor_seconds=round(s.minor_seconds, 1),
                              wall=round(time.time() - t, 1),
                              cert=cert and dict(size=cert["size"], rule=cert["rule"], refuted=cert["refuted"],
                                                 nodes=cert["nodes"]))), flush=True)
        if cert:
            json.dump(cert, open(Path(__file__).with_name(f"{name}_{config}_recorded_certificate.json"), "w"))
        continue
    val, _ = solve_mosp_exact(inst, solutions_dir=scratch, stats=stats, minor=CONFIGS[config],
                              time_budget=budget)
    cert = stats.get("minor")
    saved = json.loads((scratch / f"{name}.json").read_text())
    print(json.dumps(dict(instance=name, config=config, budget=budget, recorded=recorded, value=val,
                          proof=stats["proof"], provenance=saved["provenance"],
                          lower=saved.get("lower_bound"), lower_source=saved.get("lower_bound_source"),
                          nodes=stats["nodes"], minor_nodes=stats.get("minor_nodes"),
                          search_seconds=round(stats["seconds"], 1), wall=round(time.time() - t, 1),
                          cert=cert and dict(size=cert["size"], rule=cert["rule"], refuted=cert["refuted"],
                                             nodes=cert["nodes"]))), flush=True)
    if cert:
        json.dump(cert, open(Path(__file__).with_name(f"{name}_{config}_certificate.json"), "w"))
