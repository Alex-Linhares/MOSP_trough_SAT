"""Next members: L(K_10), L(K_11) (formula floor(n^2/4)+floor((n-3)/2) predicts 28, 34), Kneser(10,2) (n - alpha = 36)."""
import iw, dense, json, time
from concurrent.futures import ThreadPoolExecutor
jobs = [("L(K_10)", "line_complete", 45, 10, dense.line_complete(10)), ("L(K_11)", "line_complete", 55, 11, dense.line_complete(11)), ("Kneser(10,2)", "kneser", 45, 10, dense.kneser(10))]
with ThreadPoolExecutor(max_workers=3) as ex:
    res = list(ex.map(dense.run, jobs))
for r in res: print({k: v for k, v in r.items() if k != "g6"})
json.dump(res, open("dense_next.json", "w"), indent=1)
