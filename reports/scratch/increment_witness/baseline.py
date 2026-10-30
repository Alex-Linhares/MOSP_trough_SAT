"""C program's own minor certificates on each G_{k+1}, forced onto the minor
route (probe off, min_vertices 4, ladder from 0.1 n), replayed and re-proved."""
import iw, json, sys, time
from concurrent.futures import ThreadPoolExecutor

JOBS = [("hypercube", d) for d in range(2, 7)] + [("mycielski", k) for k in range(3, 8)] + [("ternary", h) for h in range(2, 5)]
EXTRA = ["-m", "probe_nodes=0", "-m", "min_vertices=4", "-m", "start_fraction=0.1", "-m", "step_fraction=0.05", "-m", "max_fraction=0.95"]

def job(fam, k):
    build, known, copy_of = iw.FAMILIES[fam]
    G = build(k); w = known[k]
    r = iw.run_c(G, t=300, layout=True, extra=EXTRA)
    out = dict(family=fam, k=k, n=G.number_of_nodes(), m=G.number_of_edges(), known=w,
               width=r["width"], status=r["status"], seconds=round(r["seconds"], 2), stderr=r["stderr"], minor_line=r["minor_line"])
    if r["minor_line"]:
        parts = r["minor_line"].split()
        i = parts.index("contractions")
        seq = [tuple(int(x) for x in p.split(",")) for p in parts[i + 1:]]
        refuted = int(parts[2]); size = int(parts[4]); rule = parts[6]
        H, branch = iw.apply_seq(G, seq)
        assert H.number_of_nodes() == size, (H.number_of_nodes(), size)
        copy = copy_of(k)
        width, status, r2 = iw.proved_width(H, t=300)
        out.update(cert_refuted=refuted, cert_size=size, cert_rule=rule, seq=seq,
                   H_nodes=H.number_of_nodes(), H_edges=H.number_of_edges(), H_width=width, H_status=status,
                   H_seconds=round(r2["seconds"], 2), preserves_copy=iw.preserves_copy(seq, copy),
                   describe=iw.describe(H, copy))
        iw.save(f"baseline_{fam}_{k}", H, seq, r2, extra=f"# C certificate line on G_{k}: {r['minor_line']}")
    return out

if __name__ == "__main__":
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(lambda j: job(*j), JOBS))
    with open("baseline.json", "w") as f:
        json.dump(results, f, indent=1, default=list)
    for r in results:
        print(r["family"], r["k"], f"n={r['n']}", f"known={r['known']}", f"C: {r['width']} {r['status']} {r['seconds']}s",
              ("| minor H: |V|=%d |E|=%d refuted %d rule %s; H proved %s %s in %ss; preserves copy %s" % (
                  r["H_nodes"], r["H_edges"], r["cert_refuted"], r["cert_rule"], r["H_width"], r["H_status"], r["H_seconds"], r["preserves_copy"])) if r.get("seq") else "| no minor certificate")
    print("total", round(time.time() - t0), "s")
