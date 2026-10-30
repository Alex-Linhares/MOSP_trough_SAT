"""Third contractions of Q_6 after 0->1 and a weight-4 second step (0b011110 -> 0b011111): any keep 23?"""
import iw, json, collections
from concurrent.futures import ThreadPoolExecutor
G = iw.hypercube(6); H2, _ = iw.apply_seq(G, [(0, 1), (0b011110, 0b011111)])
w2, st2, _ = iw.proved_width(H2, t=120); print("after two steps (weight-4 orbit): pw", w2, st2)
cands = [(v, u) for v, u in H2.edges()] + [(u, v) for v, u in H2.edges()]
def ev(c):
    H3, _ = iw.apply_seq(H2, [c]); w, st, r = iw.proved_width(H3, t=120)
    return dict(step=c, width=w if w is not None else r["width"], status=st)
with ThreadPoolExecutor(max_workers=4) as ex: R = list(ex.map(ev, cands))
json.dump(R, open("q6_level3.json", "w"), indent=1)
acc = [r for r in R if r["width"] == 23 and r["status"] in iw.PROVED]
print(len(R), "third-step candidates;", len(acc), "keep 23;", sum(1 for r in R if r["status"] not in iw.PROVED), "undecided; widths", collections.Counter(r["width"] for r in R))
print("accepted:", [(format(r["step"][0], '06b'), format(r["step"][1], '06b')) for r in acc])
