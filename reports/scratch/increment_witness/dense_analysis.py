import json, collections
import numpy as np
D = json.load(open("dense.json"))
print(len(D), "graphs;", sum(1 for r in D if not r["proved"]), "unproved (status upper/timeout):", [r["name"] for r in D if not r["proved"]])
print("proof types:", collections.Counter(r["status"] for r in D))
print("\npw == n - alpha (independence bound tight):", sum(1 for r in D if r["proved"] and r["pw"] == r["n_minus_alpha"]), "of", sum(1 for r in D if r["proved"]))
by = collections.defaultdict(list)
for r in D: by[r["family"]].append(r)
for fam, rs in by.items():
    rs.sort(key=lambda r: (str(r["param"]), r["n"]))
    print(f"\n## {fam}")
    print("name | n | m | degree | alpha | n-alpha | pw | deficit n-pw | (n-alpha)-pw | status | s")
    for r in rs:
        print(f"{r['name']} | {r['n']} | {r['m']} | {r['min_degree']}-{r['max_degree']} | {r['alpha']} | {r['n_minus_alpha']} | {r['pw']} | {r['deficit']} | {r['n_minus_alpha'] - r['pw'] if r['pw'] is not None else None} | {r['status']} | {r['seconds']}")
# fits: deficit as a function of n within each (family, k) series
print("\n## deficit n - pw against n, per series (least squares line, exact where residual 0)")
series = collections.defaultdict(list)
for r in D:
    if not r["proved"]: continue
    p = r["param"]
    key = (r["family"], p if r["family"] == "cycle_power" else (p[1] if r["family"] == "multipartite" else (tuple(p) if r["family"] == "circulant" else None)))
    series[key].append((r["n"], r["deficit"], r["pw"], r["n_minus_alpha"]))
for key, pts in sorted(series.items(), key=str):
    pts.sort()
    ns = np.array([p[0] for p in pts], float); de = np.array([p[1] for p in pts], float); pw = np.array([p[2] for p in pts], float)
    if len(pts) >= 3:
        a, b = np.polyfit(ns, de, 1); res = np.abs(np.polyval([a, b], ns) - de).max()
        a2, b2 = np.polyfit(ns, pw, 1); res2 = np.abs(np.polyval([a2, b2], ns) - pw).max()
        print(f"{key}: n={list(map(int, ns))} deficit={list(map(int, de))} pw={list(map(int, pw))}; deficit ~ {a:.3f} n + {b:.2f} (max resid {res:.2f}); pw ~ {a2:.3f} n + {b2:.2f} (max resid {res2:.2f})")
    else:
        print(f"{key}: n={list(map(int, ns))} deficit={list(map(int, de))} pw={list(map(int, pw))}")
