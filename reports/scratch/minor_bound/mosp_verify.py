"""Re-check the MOSP minor certificates written by mosp_corpus.py: replay the
contraction sequence (every merge must join customers sharing a product),
and re-refute `refuted` on the contracted instance under the published rules
and with every dominance rule off (memo only), each under a node budget.

usage: mosp_verify.py CERT.json... [--budget N]
"""
import json, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from benchmarks.ratchet import find_instances
from satisfiability.customer_search import decide
from satisfiability.relaxation import build, minor_groups

budget = 2_000_000_000
args = sys.argv[1:]
if "--budget" in args:
    i = args.index("--budget"); budget = int(args[i + 1]); del args[i:i + 2]
for path in args:
    cert = json.loads(Path(path).read_text())
    name = Path(path).name.split("_default")[0].split("_large")[0]
    inst = next(i for i in find_instances([name], ROOT / "benchmarks/instances") if i.name == name)
    groups = minor_groups(inst, [tuple(p) for p in cert["contractions"]])
    minor = build(inst, groups)
    active = sum(1 for c in range(minor.n_customers) if minor.customer_patterns(c))
    assert active == cert["size"], (active, cert["size"])
    k = cert["refuted"]
    for label, flags in (("published", dict(repaired_rules=False)),
                         ("memo-only", dict(subset_rule=False, definite_move=False, old_move=False, memo=True))):
        t = time.time(); a = decide(minor, k, max_nodes=budget, **flags)
        print(f"{name}: {cert['size']}-customer {cert['rule']} contraction replays; MOSP <= {k} "
              f"{label}: {a.status} ({a.nodes:,} nodes, {time.time()-t:.1f}s)", flush=True)
    sat = decide(minor, k + 1, max_nodes=budget)
    print(f"{name}: MOSP <= {k + 1} on the contraction: {sat.status}", flush=True)
