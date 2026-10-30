"""Nested witnesses: apply the best witness sequence of G_k inside the copy of G_k in
G_{k+1}, confirm pw(G_{k+1}) is preserved, then keep shrinking greedily (min-d, free).
usage: nested.py family k   (k = index of the larger member)"""
import iw, json, glob, sys, time
fam, k = sys.argv[1], int(sys.argv[2])
build, known, copy_of = iw.FAMILIES[fam]
def best(fam, k):
    cands = []
    for f in glob.glob(f"shrink_{fam}_{k}_*.json") + glob.glob(f"nested_{fam}_{k}.json"):
        d = json.load(open(f))
        if d.get("H_width") == known[k]:
            cands.append((d["H_nodes"], d["H_edges"], f, d["seq"]))
    cands.sort()
    return cands[0]
hn, he, f, seq_k = best(fam, k - 1)
G = build(k); w = known[k]
if fam == "ternary":
    # map T_{h-1} labels into the child-1 subtree of T_h: phi(0)=1, phi(3v+i)=3phi(v)+i
    def phi(v):
        if v == 0: return 1
        p, i = divmod(v - 1, 3)
        return 3 * phi(p) + i + 1
    seq_k = [(phi(v), phi(u) if u != -1 else -1) for v, u in seq_k]
# the copy of G_{k-1} is an induced subgraph on labels 0..n_{k-1}-1 (hypercube, mycielski)
H0, _ = iw.apply_seq(G, [tuple(s) for s in seq_k])
w0, st0, r0 = iw.proved_width(H0, t=300)
print(f"{fam} {k}: witness of G_{k-1} = {f} ({hn} vertices); applied inside G_{k}: |V|={H0.number_of_nodes()} pw proved {w0} ({st0}) target {w}")
if w0 != w:
    json.dump(dict(family=fam, k=k, nested_fails=True, after_copy_seq_width=w0, status=st0), open(f"nested_{fam}_{k}.json", "w"))
    sys.exit()
t0 = time.time()
H, seq_more, trace = iw.shrink(H0, w, modes=("min-d",), t=120, seed=0, log=print, workers=1)
seq = [tuple(s) for s in seq_k] + seq_more
width, status, r = iw.proved_width(H, t=300)
copy = copy_of(k)
desc = iw.describe(H, copy)
print(f"FINAL nested_{fam}_{k}: {desc}; proved {width} ({status}); contains witness of G_{k-1} by construction; total {time.time()-t0:.0f}s")
iw.save(f"nested_{fam}_{k}", H, seq, r, extra=f"# {desc}\n# nested: first {len(seq_k)} steps are the G_{k-1} witness sequence")
json.dump(dict(name=f"nested_{fam}_{k}", family=fam, k=k, target=w, H_nodes=H.number_of_nodes(), H_edges=H.number_of_edges(), H_width=width, H_status=status,
               seq=seq, base_witness=f, describe=desc, trace=trace), open(f"nested_{fam}_{k}.json", "w"), indent=1)
