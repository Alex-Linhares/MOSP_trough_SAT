"""All second contractions of Q_6 after the WLOG first step 0->1 (edge-transitive):
which keep pw 23?  Classify by the coordinate of the contracted edge."""
import iw, json
from concurrent.futures import ThreadPoolExecutor
G = iw.hypercube(6); H1, _ = iw.apply_seq(G, [(0, 1)])
cands = [(v, u) for v, u in H1.edges()] + [(u, v) for v, u in H1.edges()]
def ev(c):
    H2, _ = iw.apply_seq(H1, [c]); w, st, r = iw.proved_width(H2, t=120)
    return dict(step=c, width=w if w is not None else r["width"], status=st, secs=round(r["seconds"], 1))
with ThreadPoolExecutor(max_workers=4) as ex:
    R = list(ex.map(ev, cands))
json.dump(R, open("q6_level2.json", "w"), indent=1)
acc = [r for r in R if r["width"] == 23 and r["status"] in iw.PROVED]
und = [r for r in R if r["status"] not in iw.PROVED]
print(len(R), "candidates;", len(acc), "keep pw 23;", len(und), "undecided")
def coord(v, u):
    x = v ^ u
    return x.bit_length() - 1 if v != 1 and u != 1 else "touches merged vertex 1 (" + format(v, '06b') + "," + format(u, '06b') + ")"
import collections
print("accepted steps by coordinate of the edge:", collections.Counter(str(coord(*r["step"])) for r in acc))
print("accepted:", [(format(r["step"][0], '06b'), format(r["step"][1], '06b')) for r in acc])
print("rejected widths:", collections.Counter(r["width"] for r in R if r not in acc))
