#!/usr/bin/env python3
"""Brute-force check of every statement of `lean/MOSPFormalization/ObstructionCertificate.lean`
on every graph to 8 vertices (loop0013 item 09; the `reports/scratch/empty_pair/check.py`
pattern). "State before you prove, and check before you state": nothing is stated in Lean
that this script has not found true on all 13,598 graphs (nauty-geng, 1..8 vertices), and
one statement the item's text gives is found false here and corrected before it is stated.

Pathwidth is the vertex-separation subset DP (`vs`, as in the empty-pair check); the Lean
definitions are transcribed on bit masks (`contract_edge`, `isolate`, `apply_seq`,
`closed_nbhd`, `degree_in`, `min_degree_in`).

Statements checked (Lean name — what is counted):

  (i)   pathwidth_ge_of_forall_closedNbhd / pathwidth_ge_of_no_small_closedNbhd:
        for every j <= n and every k: (forall A, |A| = j -> j + k < |N[A]|) -> k + 1 <= pw.
        Equivalently f(j) - j <= pw with f(j) = min_{|A|=j} |N[A]| (Harper 1966). Counted:
        graphs, levels, violations; tight levels. Also the form with j > n is checked to be
        FALSE (vacuous hypothesis), which is why the Lean theorem carries `j <= n`.
  (ii)  pathwidth_ge_of_minor_minDegree: for a legal contraction sequence and any set S,
        minDegreeIn (applySeq G seq) S <= pw G. Random legal sequences per graph (contractions
        and deletions), S = the surviving vertices and random S; violations counted.
        The item's own phrasing, `(forall v not removed, d <= degree v) -> d <= pw`, is
        checked and found FALSE when the minor is empty (vacuous), so the Lean statement
        carries a nonempty-minor hypothesis (pathwidth_ge_of_minor_forall_degree).
  (iii) checkSeq G seq = true <-> IsContractionSeq G seq (the Bool checker and the Prop agree
        on every sequence tried, legal and illegal), and minorOf's degrees equal degreeIn on
        the survivors (the degree form and the minDegreeIn form agree).
  (iv)  the two concrete instances decided in Lean: the 8-vertex graph `octGraph` with its
        3-step sequence (min degree of the 5-vertex minor, its pathwidth, the exact pw of
        the graph) and the 7-vertex `k34` (= K_{3,4}) at level j = 1 with k = 2.
  (v)   the Lean model of a contraction sequence against the record's semantics: on random
        legal sequences the Lean minor (survivors of applySeq) equals the replay the
        certificates use (every pair an edge of the current graph; u keeps its label).

    python3 check.py --max-n 8 --workers 8 --seqs 20 --seed 0
"""
import argparse, collections, random, subprocess, sys, time
from multiprocessing import Pool


def parse_g6(line):
    b = line.strip().encode(); n = b[0] - 63; bits = []
    for ch in b[1:]:
        v = ch - 63; bits += [(v >> i) & 1 for i in range(5, -1, -1)]
    adj = [0] * n; k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]: adj[i] |= 1 << j; adj[j] |= 1 << i
            k += 1
    return n, adj


def vs(n, adj):
    """Pathwidth = vertex separation, subset DP over prefixes."""
    if n == 0: return 0
    full = (1 << n) - 1
    nb = [0] * (1 << n); f = [0] * (1 << n)
    for S in range(1, 1 << n):
        low = S & -S; v = low.bit_length() - 1
        nb[S] = nb[S ^ low] | adj[v]
        b = bin(nb[S] & ~S & full).count("1")
        best = n; T = S
        while T:
            low = T & -T; T ^= low
            c = f[S ^ low]
            if c < best: best = c
        f[S] = best if best > b else b
    return f[full]


def popcount(x): return bin(x).count("1")


# ---- the Lean definitions on masks -------------------------------------------------------

def closed_nbhd(adj, A):
    out = A
    for v in range(len(adj)):
        if A >> v & 1: out |= adj[v]
    return out


def profile(n, adj):
    """f(j) = min_{|A| = j} |N[A]| for j = 0..n, by enumeration of all 2^n sets."""
    f = [n + 1] * (n + 1)
    for A in range(1 << n):
        j = popcount(A); c = popcount(closed_nbhd(adj, A))
        if c < f[j]: f[j] = c
    return f


def contract_edge(adj, u, v):
    """Lean's contractEdge G u v: Adj x y iff x != y, x != v, y != v and
    (G.Adj x y or (x = u and G.Adj v y) or (y = u and G.Adj v x))."""
    n = len(adj); out = [0] * n
    for x in range(n):
        if x == v: continue
        row = adj[x]
        if x == u: row |= adj[v]
        row &= ~(1 << v) & ~(1 << x)
        out[x] = row
    # symmetry: y = u and G.Adj v x  <=>  x in N(v), y = u: handled by the row of u above and
    # by making x's row contain u when x in N(v)
    for x in range(n):
        if x != v and x != u and (adj[v] >> x & 1): out[x] |= 1 << u
    out[v] = 0
    return out


def isolate(adj, v):
    out = [row & ~(1 << v) for row in adj]; out[v] = 0
    return out


def step_valid(adj, step):
    v, u = step
    return True if u is None else bool(adj[u] >> v & 1)


def apply_step(adj, step):
    v, u = step
    return isolate(adj, v) if u is None else contract_edge(adj, u, v)


def is_contraction_seq(adj, seq):
    for s in seq:
        if not step_valid(adj, s): return False
        adj = apply_step(adj, s)
    return True


def check_seq_bool(adj, seq):
    """The Bool checker, written as the Lean `checkSeq` is (recursion with `&&`)."""
    if not seq: return True
    s, rest = seq[0], seq[1:]
    v, u = s
    ok = True if u is None else bool(adj[u] >> v & 1)
    return ok and check_seq_bool(apply_step(adj, s), rest)


def apply_seq(adj, seq):
    for s in seq: adj = apply_step(adj, s)
    return adj


def removed(seq): 
    m = 0
    for v, _ in seq: m |= 1 << v
    return m


def degree_in(adj, S, v): return popcount(adj[v] & S)


def min_degree_in(adj, S):
    if S == 0: return 0
    return min(degree_in(adj, S, v) for v in range(len(adj)) if S >> v & 1)


def induced(adj, S):
    """The minor as its own graph: survivors relabelled 0..m-1 in increasing order."""
    verts = [v for v in range(len(adj)) if S >> v & 1]
    pos = {v: i for i, v in enumerate(verts)}
    out = [0] * len(verts)
    for v in verts:
        for w in verts:
            if adj[v] >> w & 1: out[pos[v]] |= 1 << pos[w]
    return len(verts), out


# ---- the record's replay semantics (own 15 lines; the certificates' rule) -----------------

def replay_record(n, adj, seq):
    """Pairs (v, u): contract v into u (u keeps its label), every pair an edge of the current
    graph; (v, None): delete v. Returns alive mask and adjacency, or None if illegal."""
    alive = (1 << n) - 1; cur = list(adj)
    for v, u in seq:
        if not (alive >> v & 1): return None
        if u is None:
            for w in range(n): cur[w] &= ~(1 << v)
            cur[v] = 0; alive &= ~(1 << v); continue
        if not (alive >> u & 1) or not (cur[u] >> v & 1): return None
        nv = cur[v] & ~(1 << u)
        cur[u] |= nv; cur[u] &= ~(1 << v)
        for w in range(n):
            if nv >> w & 1: cur[w] |= 1 << u
            cur[w] &= ~(1 << v)
        cur[v] = 0; alive &= ~(1 << v)
    return alive, cur


def random_legal_seq(rng, n, adj, length):
    seq = []; cur = adj
    for _ in range(length):
        edges = [(v, u) for u in range(n) for v in range(n) if cur[u] >> v & 1]
        alive = [v for v in range(n) if not (removed(seq) >> v & 1)]
        choices = []
        if edges: choices.append("c")
        if alive: choices.append("d")
        if not choices: break
        if rng.choice(choices) == "c":
            v, u = rng.choice(edges); seq.append((v, u))
        else:
            seq.append((rng.choice(alive), None))
        cur = apply_step(cur, seq[-1])
    return seq


def one(args):
    line, seqs, seed = args
    n, adj = parse_g6(line)
    rng = random.Random(seed ^ hash(line))
    k = vs(n, adj)
    f = profile(n, adj)
    out = collections.Counter()
    out["graphs"] += 1
    # (i) Harper at every level 0..n; tightness
    best = 0
    for j in range(n + 1):
        out["levels"] += 1
        if f[j] - j > k: out["viol_i"] += 1
        best = max(best, f[j] - j)
    if best == k: out["tight_i"] += 1
    # the j > n form is vacuous: no set has |A| = n + 1, so the hypothesis holds for every k while
    # the conclusion k + 1 <= pw fails at k = pw; counted as the reason for the Lean `j <= n`
    out["false_without_j_le_n"] += 1
    # (ii), (iii), (v) random legal sequences
    for _ in range(seqs):
        seq = random_legal_seq(rng, n, adj, rng.randint(0, n))
        out["seqs"] += 1
        assert is_contraction_seq(adj, seq)
        if check_seq_bool(adj, seq) != is_contraction_seq(adj, seq): out["viol_iii_bool"] += 1
        H = apply_seq(adj, seq); R = removed(seq); S = ((1 << n) - 1) & ~R
        # removed vertices are isolated in applySeq
        if any(H[v] for v in range(n) if R >> v & 1): out["viol_isolated"] += 1
        d = min_degree_in(H, S)
        if d > k: out["viol_ii"] += 1
        # random S too
        S2 = rng.randrange(1 << n)
        if min_degree_in(H, S2) > k: out["viol_ii_anyS"] += 1
        # the item's phrasing without the nonempty hypothesis: with S empty, forall v in S is
        # vacuous, so "d <= pw" would be claimed for d = k + 1
        if S == 0: out["empty_minor"] += 1
        # the degree form: every survivor has degree >= d, so d <= pw (needs S nonempty)
        if S and all(degree_in(H, S, v) >= d for v in range(n) if S >> v & 1) and d > k:
            out["viol_ii_forall"] += 1
        # pw(minor) between min degree and pw(G); the minor's pw by the DP
        m, Hm = induced(H, S)
        pwH = vs(m, Hm)
        if pwH > k: out["viol_minor_pw"] += 1
        if d > pwH: out["viol_mindeg_pw_minor"] += 1
        # (v) the Lean minor equals the record's replay
        rec = replay_record(n, adj, seq)
        if rec is None:
            # the record refuses deletion of a non-isolated vertex? no: it deletes any alive
            # vertex; it refuses a step on a removed vertex, which random_legal_seq never emits
            out["record_refused"] += 1
        else:
            alive, cur = rec
            if alive != S or any((cur[v] & S) != (H[v] & S) for v in range(n) if S >> v & 1):
                out["viol_v_replay"] += 1
        # an illegal sequence: both sides say no
        if seq:
            bad = list(seq); i = rng.randrange(len(bad)); v, u = bad[i]
            # retarget to a non-neighbour at that step
            cur = apply_seq(adj, bad[:i])
            non = [w for w in range(n) if w != v and not (cur[v] >> w & 1)]
            if non:
                bad[i] = (v, rng.choice(non))
                out["illegal_tried"] += 1
                if check_seq_bool(adj, bad) != is_contraction_seq(adj, bad): out["viol_iii_bool"] += 1
                if check_seq_bool(adj, bad): out["illegal_accepted"] += 1
    return n, out


def concrete():
    """The two instances decided in Lean (iv): checked here by the same oracle."""
    # octGraph: the 8-cycle 0-1-...-7-0, pathwidth 2. Five contractions into 0 leave the
    # triangle {0, 1, 2}: min degree 2, so pw >= 2, tight (the item's "3-vertex min-degree-2 minor").
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (0, 7)]
    n = 8; adj = [0] * n
    for a, b in edges: adj[a] |= 1 << b; adj[b] |= 1 << a
    seq = [(7, 0), (6, 0), (5, 0), (4, 0), (3, 0)]
    assert is_contraction_seq(adj, seq)
    H = apply_seq(adj, seq); S = ((1 << n) - 1) & ~removed(seq)
    d = min_degree_in(H, S); m, Hm = induced(H, S)
    print(f"octGraph: n={n} edges={len(edges)} pw={vs(n, adj)} seq={seq} survivors={[v for v in range(n) if S>>v&1]} "
          f"minor_min_degree={d} minor_pw={vs(m, Hm)} degrees={[degree_in(H,S,v) for v in range(n) if S>>v&1]}")
    # k34 = K_{3,4}: parts {0,1,2} and {3,4,5,6}
    n = 7; adj = [0] * n
    for a in range(3):
        for b in range(3, 7): adj[a] |= 1 << b; adj[b] |= 1 << a
    f = profile(n, adj)
    print(f"k34: pw={vs(n, adj)} profile f(j)={f} harper max_j f(j)-j = {max(f[j]-j for j in range(n+1))} "
          f"at j=1: f(1)={f[1]} so forall |A|=1, 1+2 < |N[A]| holds: {f[1] > 3}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=8); ap.add_argument("--min-n", type=int, default=1)
    ap.add_argument("--workers", type=int, default=8); ap.add_argument("--seqs", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    t0 = time.time()
    concrete()
    total = collections.Counter()
    for n in range(a.min_n, a.max_n + 1):
        lines = subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True).stdout.splitlines()
        with Pool(a.workers) as p:
            res = p.map(one, [(l, a.seqs, a.seed) for l in lines], chunksize=64)
        c = collections.Counter()
        for _, out in res: c.update(out)
        total.update(c)
        viol = {k: v for k, v in c.items() if k.startswith("viol") or k == "illegal_accepted"}
        print(f"n={n} graphs={c['graphs']} levels={c['levels']} tight_i={c['tight_i']} seqs={c['seqs']} "
              f"false_without_j_le_n={c['false_without_j_le_n']} "
              f"empty_minor={c['empty_minor']} illegal_tried={c['illegal_tried']} violations={viol}", flush=True)
    viol = {k: v for k, v in total.items() if k.startswith("viol") or k == "illegal_accepted"}
    print(f"TOTAL graphs={total['graphs']} levels={total['levels']} tight_i={total['tight_i']} seqs={total['seqs']} "
          f"empty_minor={total['empty_minor']} illegal_tried={total['illegal_tried']} violations={viol} "
          f"({time.time()-t0:.0f} s)")
    print("the item's phrasing of (ii) without a nonempty-minor hypothesis is vacuous on the "
          f"{total['empty_minor']} sequences that remove every vertex: there it would claim pw >= d for any d, "
          "false; the Lean statement carries the hypothesis")
    return 0 if not any(viol.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
