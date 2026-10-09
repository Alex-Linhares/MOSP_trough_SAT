# Independent brute force for Fink (2012) Teorema 1 (pp. 27-28), the definite move
# restated with f(j, S) = {i : i, j not in S, i < j, o(i, S) ⊆ o(j, S)} and the premise
# |f(j, S)| >= open(j, S).  Shares no code with the solvers.  Run:
#     python3 -m paper1.fink_check
# 1. On cexGraph (14 customers, k = 6) it never fails, under any labelling: a failure
#    needs at least open(q, S) dominated unclosed customers other than q, and the best
#    labelling puts all of them before q, so the test is closeCount - 1 >= open.
# 2. On finkGraph (cexGraph plus a third twin of 3 and 4, labels 0 and 14 swapped) it
#    fails at S = {2, 3}, q = 14, as labelled.  Lean: fink_theorem1_false
#    (lean/MOSPFormalization/Search/ChuThesis.lean).
from functools import lru_cache

CEX_EDGES = [(0, 3), (0, 4), (0, 7), (0, 11), (1, 2), (1, 5), (1, 6), (2, 3), (2, 4),
             (5, 9), (5, 11), (5, 12), (6, 8), (6, 13), (7, 9), (7, 10), (7, 13), (8, 9),
             (8, 10), (8, 11), (9, 10), (9, 11), (10, 11), (10, 12), (10, 13), (12, 13)]
FINK_EDGES = [(0, 2), (0, 14), (1, 2), (1, 5), (1, 6), (2, 3), (2, 4), (3, 14), (4, 14),
              (5, 9), (5, 11), (5, 12), (6, 8), (6, 13), (7, 9), (7, 10), (7, 13), (7, 14),
              (8, 9), (8, 10), (8, 11), (9, 10), (9, 11), (10, 11), (10, 12), (10, 13),
              (11, 14), (12, 13)]
K = 6


def failures(n, edges, k, best_labelling):
    """Every (S, q) where a solution extends S, Fink's premise holds, and none extends S + q."""
    nb = [1 << i for i in range(n)]
    for a, b in edges:
        nb[a] |= 1 << b
        nb[b] |= 1 << a
    full = (1 << n) - 1
    pc = lambda x: bin(x).count("1")
    opened = [0] * (1 << n)
    for S in range(1, 1 << n):
        low = S & -S
        opened[S] = opened[S ^ low] | nb[low.bit_length() - 1]
    cost = lambda S, c: pc((opened[S] | nb[c]) & ~S)

    @lru_cache(None)
    def sol(S):
        return S == full or any(not S >> c & 1 and cost(S, c) <= k and sol(S | 1 << c)
                                for c in range(n))

    out = []
    for S in range(1 << n):
        if not sol(S):
            continue
        for q in range(n):
            if S >> q & 1 or cost(S, q) > k or sol(S | 1 << q):
                continue
            oq = nb[q] & ~opened[S]
            dom = [d for d in range(n) if d != q and not S >> d & 1
                   and (nb[d] & ~opened[S]) & ~oq == 0 and (best_labelling or d < q)]
            if len(dom) >= pc(oq):
                out.append(([i for i in range(n) if S >> i & 1], q, dom, pc(oq)))
    return out


def main():
    f1 = failures(14, CEX_EDGES, K, best_labelling=True)
    print(f"cexGraph, k = {K}, any labelling: {len(f1)} failures")
    f2 = failures(15, FINK_EDGES, K, best_labelling=False)
    print(f"finkGraph, k = {K}, as labelled: {len(f2)} failures")
    for S, q, dom, op in f2:
        print(f"  S = {S}, q = {q}, f(q, S) = {dom}, open(q, S) = {op}")
    assert not f1 and ([2, 3], 14, [0, 4], 2) in f2


if __name__ == "__main__":
    main()
