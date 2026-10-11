"""Is pw(myciel6) <= k? A vertex-separation SAT encoding, solved by pysat.

myciel6 (Mycielski M7, 95 vertices, 755 edges) has pathwidth 38: Coudert,
Mazauric & Nisse (2016) prove it in about ten minutes, and our customer search
had not refuted 37 after 25 minutes (bench/results/myciel6_bettermove.log).
Started 2026-10-11 to see whether SAT does better.

Encoding (pathwidth = vertex separation, Kinnersley 1992), positions t = 0..n-1:
  x[v,t]  vertex v is at position t (a permutation: exactly one per row and column)
  y[v,t]  v is placed at a position <= t        (y[v,t] <-> y[v,t-1] or x[v,t])
  s[v,t]  v is placed by t and has a neighbour not placed by t ("open" after t)
          (not y[v,t]) or y[u,t] or s[v,t], for every edge uv
  at most k of s[., t] for every t   (sequential counter)
Only the forcing direction of s is needed: s may be true spuriously, which can
only make the bound harder to meet. Every auxiliary variable comes from one
IDPool, which avoids the collision bug of satisfiability/encoding.py.
Symmetry: none is broken, so the refutation needs no symmetry argument.

`python bench/myciel6_sat.py K SOLVER` (SOLVER: cadical195, kissat404, ...);
appends one line to bench/results/myciel6_sat.log.
"""
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from readers import HERE, read_any  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402
from pysat.formula import CNF, IDPool  # noqa: E402
from pysat.solvers import Solver  # noqa: E402


def encode(G, k):
    V = sorted(G.nodes())
    n = len(V)
    pool = IDPool()
    x = lambda v, t: pool.id(("x", v, t))
    y = lambda v, t: pool.id(("y", v, t))
    s = lambda v, t: pool.id(("s", v, t))
    cnf = CNF()
    for v in V:  # each vertex at exactly one position
        cnf.append([x(v, t) for t in range(n)])
        cnf.extend(CardEnc.atmost([x(v, t) for t in range(n)], 1, vpool=pool, encoding=EncType.seqcounter).clauses)
    for t in range(n):  # each position holds exactly one vertex
        cnf.append([x(v, t) for v in V])
        cnf.extend(CardEnc.atmost([x(v, t) for v in V], 1, vpool=pool, encoding=EncType.seqcounter).clauses)
    for v in V:  # y is the prefix closure of x
        for t in range(n):
            prev = [y(v, t - 1)] if t else []
            cnf.append([-y(v, t), x(v, t)] + prev)
            cnf.append([-x(v, t), y(v, t)])
            if t:
                cnf.append([-y(v, t - 1), y(v, t)])
    for t in range(n - 1):
        for u, v in G.edges():
            cnf.append([-y(v, t), y(u, t), s(v, t)])
            cnf.append([-y(u, t), y(v, t), s(u, t)])
        cnf.extend(CardEnc.atmost([s(v, t) for v in V], k, vpool=pool, encoding=EncType.seqcounter).clauses)
    return cnf, pool, V, x


def main():
    k = int(sys.argv[1])
    name = sys.argv[2] if len(sys.argv) > 2 else "cadical195"
    gname = sys.argv[3] if len(sys.argv) > 3 else "myciel6"
    G = read_any(HERE / "coloring" / f"{gname}.dgf")
    t0 = time.monotonic()
    cnf, pool, V, x = encode(G, k)
    enc_s = time.monotonic() - t0
    log = Path(__file__).resolve().parent / "results" / "myciel6_sat.log"
    with log.open("a") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} start {gname} pw<={k} {name}: {pool.top} vars, "
                f"{len(cnf.clauses)} clauses, encoded in {enc_s:.0f}s\n")
    t1 = time.monotonic()
    with Solver(name=name, bootstrap_with=cnf.clauses) as S:
        ok = S.solve()
        order = None
        if ok:
            m = set(l for l in S.get_model() if l > 0)
            order = [v for t in range(len(V)) for v in V if x(v, t) in m]
    secs = time.monotonic() - t1
    with log.open("a") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} done {gname} pw<={k} {name}: "
                f"{'SAT' if ok else 'UNSAT'} in {secs:.0f}s" + (f" order={order}" if order else "") + "\n")


if __name__ == "__main__":
    main()
