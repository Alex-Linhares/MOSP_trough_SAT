"""Joint size statistics of the 200 Chu & Stuckey files, per class (n, m, d).
rows of the file = patterns (size = customers per pattern), columns = customers (patterns per customer)."""
import glob, collections, statistics as st, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
by = collections.defaultdict(lambda: {"ps": [], "cs": [], "ones": [], "files": 0, "min_col": [], "conn": []})
def connected(M, m, n):
    # MOSP graph on customers: union of cliques per pattern; BFS over patterns
    adj = [set() for _ in range(n)]
    for r in M:
        cs = [j for j in range(n) if r[j]]
        for a in cs:
            adj[a].update(cs)
    seen = {0}; stack = [0]
    while stack:
        v = stack.pop()
        for w in adj[v]:
            if w not in seen: seen.add(w); stack.append(w)
    return len(seen) == n
for f in sorted(glob.glob(str(ROOT / "benchmarks/instances/MOSP_Instances/Chu_Stuckey/Random-*.txt"))):
    L = [l for l in open(f).read().split("\n") if l.strip()]
    m, n = map(int, L[0].split())
    M = [list(map(int, L[1 + i].split())) for i in range(m)]
    assert len(M) == m and all(len(r) == n for r in M)
    name = Path(f).stem; d = int(name.split("-")[3])
    key = (n, m, d); c = by[key]
    ps = [sum(r) for r in M]; cs = [sum(M[i][j] for i in range(m)) for j in range(n)]
    c["ps"] += ps; c["cs"] += cs; c["ones"].append(sum(ps)); c["files"] += 1
    c["min_col"].append(min(cs)); c["conn"].append(connected(M, m, n))
    # correlation between pattern size and patterns-per-customer: per-cell -> mean over patterns of mean col sum of its customers
print("class (n,m,d) | files | ones mean (d*m) | pattern size: min mean var max  binom var d(1-d/n) | patterns/customer: min mean var max  binom var (m d/n)(1-d/n) | #files min col=1 | #files min col=2 | all connected")
for key in sorted(by):
    n, m, d = key; c = by[key]
    ps, cs = c["ps"], c["cs"]
    print(f"{key} | {c['files']} | {st.mean(c['ones']):7.1f} ({d*m}) | {min(ps):2d} {st.mean(ps):6.2f} {st.pvariance(ps):6.2f} {max(ps):2d}  {d*(1-d/n):5.2f} | {min(cs):2d} {st.mean(cs):6.2f} {st.pvariance(cs):6.2f} {max(cs):2d}  {(m*d/n)*(1-d/n):5.2f} | {sum(x==1 for x in c['min_col'])} | {sum(x==2 for x in c['min_col'])} | {all(c['conn'])}")
