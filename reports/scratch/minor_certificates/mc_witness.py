"""Upper side, independently: simulate the stored witness ordering of each corpus
instance with code written here (a customer's stack is open from the first to the
last product it needs, inclusive) and compare with the stored value."""
import json
from pathlib import Path
from mc_graph import _blocks
ROOT = Path(__file__).resolve().parents[3]
CS = ROOT / "benchmarks/instances/MOSP_Instances/Chu_Stuckey"
for name, path, fmt, idx in [("Random-125-125-2-3_0", CS / "Random-125-125-2-3.txt", "A", 0),
                             ("Random-125-125-2-1_0", CS / "Random-125-125-2-1.txt", "A", 0),
                             ("Random-125-125-6-1_0", CS / "Random-125-125-6-1.txt", "A", 0),
                             ("SP4", ROOT / "benchmarks/instances/ChallengeInstances2005/Wilson/sp4.txt", "B", 3)]:
    mat = _blocks(path)[idx]
    if fmt == "A":
        pats = [{c for c, x in enumerate(r) if x} for r in mat]
    else:
        pats = [{c for c in range(len(mat)) if mat[c][p]} for p in range(len(mat[0]))]
    sol = json.load(open(ROOT / "solutions" / f"{name}.json"))
    order = sol["ordering"]
    assert sorted(order) == list(range(len(pats))), "ordering is not a permutation of the products"
    first, last = {}, {}
    for t, p in enumerate(order):
        for c in pats[p]:
            first.setdefault(c, t); last[c] = t
    worst = max(sum(1 for c in first if first[c] <= t <= last[c]) for t in range(len(order)))
    print(f"{name}: witness simulates to {worst}; stored {sol['mosp_value']} ({sol.get('provenance')})")
    assert worst == sol["mosp_value"]
