"""Greedy shrink of G_{k} to a small contraction minor with proved pw = pw(G_k).
usage: search.py family k modes(comma) protect(0/1) seed workers delete(0/1) [t] [tag]"""
import iw, json, sys, time
fam, k = sys.argv[1], int(sys.argv[2])
modes = tuple(sys.argv[3].split(","))
protect = sys.argv[4] == "1"
seed = int(sys.argv[5]); workers = int(sys.argv[6]); allow_delete = sys.argv[7] == "1"
t = int(sys.argv[8]) if len(sys.argv) > 8 else 120
tag = sys.argv[9] if len(sys.argv) > 9 else ""
build, known, copy_of = iw.FAMILIES[fam]
G = build(k); w = known[k]; copy = copy_of(k)
name = f"shrink_{fam}_{k}_{'+'.join(modes)}_{'prot' if protect else 'free'}_s{seed}{'_del' if allow_delete else ''}{tag}"
logf = open(name + ".log", "w")
def log(s):
    print(s); logf.write(s + "\n"); logf.flush()
log(f"{name}: n={G.number_of_nodes()} m={G.number_of_edges()} target pw={w}")
t0 = time.time()
H, seq, trace = iw.shrink(G, w, modes=modes, protect=frozenset(copy) if protect else frozenset(),
                          t=t, seed=seed, log=log, workers=workers, allow_delete=allow_delete)
# final independent confirmation of H
width, status, r = iw.proved_width(H, t=300)
ok_seq, bad_del = iw.check_seq(G, seq)
desc = iw.describe(H, copy)
log(f"FINAL {name}: {desc}; proved width {width} ({status}) in {r['seconds']:.2f}s; seq valid {ok_seq}, non-isolated deletions {bad_del}; preserves copy {iw.preserves_copy(seq, copy)}; steps {len(seq)}; total {time.time()-t0:.0f}s")
iw.save(name, H, seq, r, extra=f"# {desc}\n# G_k copy preserved: {iw.preserves_copy(seq, copy)}")
json.dump(dict(name=name, family=fam, k=k, target=w, n=G.number_of_nodes(), H_nodes=H.number_of_nodes(), H_edges=H.number_of_edges(),
               H_width=width, H_status=status, seq=seq, preserves_copy=iw.preserves_copy(seq, copy), describe=desc,
               trace=trace, seconds=time.time() - t0), open(name + ".json", "w"), indent=1)
