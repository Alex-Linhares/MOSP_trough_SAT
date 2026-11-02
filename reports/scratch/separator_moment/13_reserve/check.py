"""Brute-force check, before the Lean statement is written (loop0011 item 13):

(1) the per-pair product identity behind Theorem Cl's independence step —
    for every disjoint ordered pair (A, R) of an n-vertex set, with
    S = V ∖ (A ∪ R),

      Σ_{G : (A, R) closed in G} p^{|E(G)|} (1 − p)^{C(n,2) − |E(G)|}
        = (1 − p)^{|A||R|} · ((1 − (1 − p)^{|A|}) (1 − (1 − p)^{|R|}))^{|S|},

    in exact rationals at p = 1/2 and 1/3, every labelled graph, every pair,
    n = 1..5 in full and 80 random pairs at n = 6;
(2) the two finset lemmas the Lean proof goes through, on random instances:
    the split lemma (T = B ⊔ T', predicate P(F ∩ B) ∧ Q(F ∩ T')) and the
    product-over-blocks lemma (pairwise disjoint blocks B_i ⊆ T, predicate
    ∀ i, P_i(F ∩ B_i)), with random monotone-or-not predicates given as
    explicit subsets of the powerset.

Closed = disjoint ∧ empty ∧ every v ∈ S has a neighbour in A and in R
(`isClosedPair_iff_sees_both`, Lean).
"""
from __future__ import annotations
import itertools, random, sys, time
from fractions import Fraction
from itertools import combinations

sys.path.insert(0, "/home/al/dev/MOSP")
from learning.separator_moment import _labelled_graphs  # noqa: E402


def closed_weight(n, A, R, p):
    """Σ over labelled graphs on n vertices in which (A, R) is closed."""
    q = 1 - p
    Cn = n * (n - 1) // 2
    S = [v for v in range(n) if v not in A and v not in R]
    maskA = sum(1 << a for a in A)
    maskR = sum(1 << r for r in R)
    total = Fraction(0)
    for adj, e in _labelled_graphs(n):
        if any(adj[a] & maskR for a in A):
            continue
        if all((adj[v] & maskA) and (adj[v] & maskR) for v in S):
            total += p ** e * q ** (Cn - e)
    return total


def product_form(n, a, r, p):
    q = 1 - p
    s = n - a - r
    return q ** (a * r) * ((1 - q ** a) * (1 - q ** r)) ** s


def check_pairs(n, p, pairs):
    bad = 0
    for A, R in pairs:
        lhs = closed_weight(n, A, R, p)
        rhs = product_form(n, len(A), len(R), p)
        if lhs != rhs:
            bad += 1
            print(f"  VIOLATION n={n} p={p} A={A} R={R}: {lhs} != {rhs}")
    return bad


def all_disjoint_pairs(n):
    for lab in itertools.product(range(3), repeat=n):
        A = tuple(i for i in range(n) if lab[i] == 0)
        R = tuple(i for i in range(n) if lab[i] == 1)
        yield A, R


def weight(F, T, p):
    return p ** len(F) * (1 - p) ** (len(T) - len(F))


def subsets(T):
    T = list(T)
    for k in range(len(T) + 1):
        for c in combinations(T, k):
            yield frozenset(c)


def check_split(rng, trials, p):
    bad = 0
    for _ in range(trials):
        m = rng.randint(0, 7)
        T = list(range(m))
        B = frozenset(x for x in T if rng.random() < 0.5)
        Tp = frozenset(T) - B
        PB = {F for F in subsets(B) if rng.random() < 0.6}
        QT = {F for F in subsets(Tp) if rng.random() < 0.6}
        lhs = sum(weight(F, T, p) for F in subsets(T) if (F & B) in PB and (F & Tp) in QT)
        rhs = sum(weight(F, B, p) for F in PB) * sum(weight(F, Tp, p) for F in QT)
        if lhs != rhs:
            bad += 1
            print("  split VIOLATION", T, B, PB, QT)
    return bad


def check_blocks(rng, trials, p):
    bad = 0
    for _ in range(trials):
        m = rng.randint(0, 8)
        T = list(range(m))
        nb = rng.randint(0, 3)
        lab = [rng.randint(-1, nb - 1) if nb else -1 for _ in T]
        blocks = [frozenset(x for x in T if lab[x] == i) for i in range(nb)]
        preds = [{F for F in subsets(Bi) if rng.random() < 0.6} for Bi in blocks]
        lhs = sum(weight(F, T, p) for F in subsets(T)
                  if all((F & Bi) in Pi for Bi, Pi in zip(blocks, preds)))
        rhs = Fraction(1)
        for Bi, Pi in zip(blocks, preds):
            rhs *= sum(weight(F, Bi, p) for F in Pi)
        if lhs != rhs:
            bad += 1
            print("  blocks VIOLATION", T, blocks, preds)
    return bad


def main():
    t0 = time.time()
    rng = random.Random(13)
    total_bad = 0
    for p in (Fraction(1, 2), Fraction(1, 3)):
        for n in range(1, 6):
            pairs = list(all_disjoint_pairs(n))
            bad = check_pairs(n, p, pairs)
            total_bad += bad
            print(f"(1) n={n} p={p}: {len(pairs)} pairs x {2 ** (n * (n - 1) // 2)} graphs, violations {bad}")
        pairs6 = rng.sample(list(all_disjoint_pairs(6)), 80)
        bad = check_pairs(6, p, pairs6)
        total_bad += bad
        print(f"(1) n=6 p={p}: 80 random pairs x 32768 graphs, violations {bad}")
        b1 = check_split(rng, 300, p)
        b2 = check_blocks(rng, 300, p)
        total_bad += b1 + b2
        print(f"(2) p={p}: split lemma 300 trials violations {b1}; blocks lemma 300 trials violations {b2}")
    print(f"TOTAL VIOLATIONS {total_bad}; {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
