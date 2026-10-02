# Independent brute force: does the thesis's Theorem 6.3.8 (better move, premise
# close(q,S) >= open(q, S+r)) fail on cexGraph at k = 6?  And Theorem 6.3.6?
from functools import lru_cache
M = [2201,102,30,13,21,6690,8514,9857,3904,4000,16256,3873,13344,13504]
n, K = 14, 6
assert all(M[i] >> i & 1 for i in range(n))
assert all((M[i] >> j & 1) == (M[j] >> i & 1) for i in range(n) for j in range(n))
FULL = (1 << n) - 1
def N(S):
    r = 0
    for i in range(n):
        if S >> i & 1: r |= M[i]
    return r
pc = lambda x: bin(x).count("1")
def cost(S, q):          # stacks open while q's stack closes after S
    return pc((N(S) | M[q]) & ~S)
@lru_cache(None)
def sol(S):
    if S == FULL: return True
    return any(not S >> q & 1 and cost(S, q) <= K and sol(S | 1 << q) for q in range(n))
def o(c, S): return M[c] & ~N(S)
def opn(c, S): return pc(o(c, S))
def close_unclosed(c, S): return sum(1 for d in range(n) if not S >> d & 1 and o(d, S) & ~o(c, S) == 0)
def close_literal(c, S): return sum(1 for d in range(n) if o(d, S) & ~o(c, S) == 0)
def playable(S, seq):
    for q in seq:
        if cost(S, q) > K: return False
        S |= 1 << q
    return True
res = {}
for name, close in (("unclosed", close_unclosed), ("literal", close_literal)):
    t1 = t2t = t2cp = 0; ex1 = ex2t = ex2cp = None
    for S in range(1 << n):
        if not sol(S): continue
        for q in range(n):
            if S >> q & 1 or not playable(S, [q]): continue
            if close(q, S) >= opn(q, S) and not sol(S | 1 << q):
                t1 += 1; ex1 = ex1 or (bin(S), q)
            for r in range(n):
                if r == q or S >> r & 1 or not playable(S, [r, q]) or not sol(S | 1 << r): continue
                if sol(S | 1 << q): continue
                Sr = S | 1 << r
                if close(q, S) >= opn(q, Sr):
                    t2t += 1; ex2t = ex2t or ([i for i in range(n) if S >> i & 1], r, q, close(q, S), opn(q, Sr))
                if close(q, Sr) >= opn(q, Sr):
                    t2cp += 1; ex2cp = ex2cp or ([i for i in range(n) if S >> i & 1], r, q)
    print(name, "Thm 6.3.6 / CP Thm1 failures:", t1, ex1)
    print(name, "thesis Thm 6.3.8 failures:", t2t, ex2t)
    print(name, "CP09 Thm 2 failures:", t2cp, ex2cp)
