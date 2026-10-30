"""Structure of the best witness per (family, k): branch sets, survivors, added edges."""
import iw, json, glob, collections
import networkx as nx
def best(fam, k, known):
    c = []
    for f in glob.glob(f"shrink_{fam}_{k}_*.json") + glob.glob(f"nested_{fam}_{k}.json"):
        d = json.load(open(f))
        if d.get("H_width") == known[k]:
            c.append((d["H_nodes"], d["H_edges"], f, d["seq"]))
    c.sort(); return c
for fam in ("hypercube", "mycielski", "ternary"):
    build, known, copy_of = iw.FAMILIES[fam]
    ks = sorted(k for k in known if glob.glob(f"shrink_{fam}_{k}_*.json"))
    for k in ks:
        c = best(fam, k, known)
        if not c: continue
        sizes = sorted(set((a, b) for a, b, _, _ in c))
        hn, he, f, seq = c[0]
        G = build(k); copy = copy_of(k); n = G.number_of_nodes()
        H, branch = iw.apply_seq(G, [tuple(s) for s in seq])
        print(f"\n### {fam} k={k}: n={n} m={G.number_of_edges()} pw={known[k]}  best witness {f}: |V|={hn} |E|={he}; all local minima found: {sizes}")
        bs = collections.defaultdict(list)
        for x, r in branch.items():
            if r is not None: bs[r].append(x)
        nontrivial = {r: xs for r, xs in bs.items() if len(xs) > 1}
        print(f"  steps {len(seq)}; branch sets of size >1: {len(nontrivial)}; deleted: {sum(1 for r in branch.values() if r is None)}")
        surv_copy = [v for v in H if v in copy]; surv_new = [v for v in H if v not in copy]
        print(f"  survivors: {len(surv_copy)} of {len(copy)} copy vertices, {len(surv_new)} of {n-len(copy)} new vertices")
        Hc = H.subgraph(surv_copy)
        Gc = G.subgraph([v for v in copy if v in H])
        added = Hc.number_of_edges() - Gc.number_of_edges()
        print(f"  edges inside the surviving copy: {Hc.number_of_edges()} ({Gc.number_of_edges()} original + {added} added by merging new vertices into copy vertices)")
        if fam == "mycielski":
            nk = len(copy); apex = 2 * nk
            kinds = lambda xs: collections.Counter("orig" if x < nk else ("apex" if x == apex else "shadow") for x in xs)
            for r in sorted(nontrivial):
                xs = nontrivial[r]
                print(f"    branch set rep {r} ({'orig' if r < nk else 'apex' if r == apex else 'shadow s'+str(r-nk)}): {dict(kinds(xs))} -> {sorted(xs)}")
            print(f"  surviving new vertices: {['apex' if v == apex else 's'+str(v-nk) for v in surv_new]}; their degrees in H: {[H.degree(v) for v in surv_new]}")
            print(f"  degrees in H of copy vertices: {sorted((H.degree(v) for v in surv_copy), reverse=True)}")
            print(f"  H restricted to copy = M_{k-1} plus {added} edges; is M_{k-1} copy still an induced subgraph? {added == 0}")
            # does the shadow part of H look like a Mycielskian of something?
        if fam == "hypercube":
            for r in sorted(nontrivial): print(f"    branch set rep {r:0{k}b}: {[format(x, '0'+str(k)+'b') for x in nontrivial[r]]}")
        if fam == "ternary":
            T = H
            root = [v for v in T if T.degree(v) == 3 and all(T.degree(u) >= 2 for u in T[v])]
            ecc = nx.eccentricity(T); center = nx.center(T)
            print(f"  tree: center {center}, radius {nx.radius(T)}, leaves {sum(1 for v in T if T.degree(v)==1)}, max degree {max(d for _, d in T.degree())}; branches at center: {[len(c) for c in nx.connected_components(T.subgraph(set(T)-set(center[:1])))]}")
