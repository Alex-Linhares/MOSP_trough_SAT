"""First-moment lower bound for the Chu & Stuckey random classes, from pattern sizes alone.

Model: the m patterns are independent uniformly random customer subsets of their observed
sizes s_1..s_m (the generator's sizes are not fixed at d; they are read from each file).
Deterministic step (EmptyPair.lean): pw <= k implies an empty pair (A, R), |A| = t, |R| >= t - 1,
t = ceil((n - k)/2).  Union bound over pairs; a pair is empty iff no pattern meets both sides:
  P(pw <= k) <= C(n,t) C(n-t,t-1) prod_j q(s_j),   q(s) = [C(n-t,s) + C(n-t+1,s) - C(n-2t+1,s)] / C(n,s).
Optimum = pw + 1.  For each instance: the largest k with bound < 1 and < 0.01 (so opt >= k + 2 is
the floor the bound gives at that confidence), against the certified optimum.
    python3 finite_bound_cs.py
"""
import glob, json, math, collections, statistics as st
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
lg = math.lgamma
def lchoose(a, b):
    if b < 0 or b > a: return -math.inf
    return lg(a + 1) - lg(b + 1) - lg(a - b + 1)
def lq(n, t, s):
    # log probability that a uniform s-subset of n avoids A (size t) or avoids R (size t-1)
    terms = [lchoose(n - t, s), lchoose(n - t + 1, s)]
    neg = lchoose(n - 2 * t + 1, s)
    m = max(terms)
    val = math.exp(terms[0] - m) + math.exp(terms[1] - m) - (math.exp(neg - m) if neg > -math.inf else 0.0)
    if val <= 0: return -math.inf
    return m + math.log(val) - lchoose(n, s)
def log_bound(n, sizes, k):
    t = (n - k + 1) // 2
    if t < 1 or 2 * t - 1 > n: return math.inf
    lb = lchoose(n, t) + lchoose(n - t, t - 1)
    for s in sizes:
        lb += lq(n, t, s)
    return lb
rows = []
for f in sorted(glob.glob(str(ROOT / "benchmarks/instances/MOSP_Instances/Chu_Stuckey/Random-*.txt"))):
    L = [l for l in open(f).read().split("\n") if l.strip()]
    m, n = map(int, L[0].split())            # patterns x pieces
    M = [list(map(int, L[1 + i].split())) for i in range(m)]
    sizes = [sum(r) for r in M]
    name = Path(f).stem; d = int(name.split("-")[3])
    sol = ROOT / "solutions" / f"{name}_0.json"
    opt = json.load(open(sol))["mosp_value"]
    k1 = max((k for k in range(n) if log_bound(n, sizes, k) < 0), default=-1)
    k2 = max((k for k in range(n) if log_bound(n, sizes, k) < math.log(0.01)), default=-1)
    rows.append((n, m, d, name, opt, k1 + 2, k2 + 2))      # floors on the optimum
by = collections.defaultdict(list)
for r in rows: by[(r[0], r[1], r[2])].append(r)
print("class (customers n, patterns m, d): mean certified optimum | floor from the bound (<1) | floor (<0.01) | opt/n, floor/n | violations")
viol = 0
for key in sorted(by):
    L = by[key]; n = key[0]
    o = st.mean(r[4] for r in L); f1 = st.mean(r[5] for r in L); f2 = st.mean(r[6] for r in L)
    v = sum(r[4] < r[6] for r in L); viol += v
    print(f"{key}: opt {o:6.1f} | floor<1 {f1:6.1f} | floor<0.01 {f2:6.1f} | {o/n:.3f} {f2/n:.3f} | {v}")
print("instances where the certified optimum is below the 0.01-floor:", viol, "of", len(rows))
