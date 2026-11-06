"""Lemma D.3: E sum_gamma (X_gamma - M/D)^2 <= 2 M Delta, exactly, for tiny r, a,
with D read as the paper's r*2^a and as the number of ordered pair labels r^{2a}.
Labels: each vertex gets an independent uniform element of [r]^a.
The exact expectation = sum over ordered edge pairs (P(same pair label) - 1/D)
+ (#labels - D)(M/D)^2 correction if D != #labels (we compute it from scratch)."""
import itertools, random
from fractions import Fraction as Fr

def exact_expectation(edges, nrow, ncol, r, a, D):
    nlab = r ** a
    # brute force over all labelings (tiny cases only)
    tot = Fr(0); count = 0
    for rowlab in itertools.product(range(nlab), repeat=nrow):
        for collab in itertools.product(range(nlab), repeat=ncol):
            X = {}
            for (i, j) in edges:
                X[(rowlab[i], collab[j])] = X.get((rowlab[i], collab[j]), 0) + 1
            M = len(edges)
            s = sum((x - Fr(M, D)) ** 2 for x in X.values())
            s += (nlab * nlab - len(X)) * Fr(M, D) ** 2   # labels with X_gamma = 0
            tot += s; count += 1
    return tot / count

random.seed(0)
for (r, a) in [(2, 1), (2, 2), (3, 1)]:
    for M in [2, 3, 4]:
        # a matching: M disjoint edges, Delta = 1
        edges = [(i, i) for i in range(M)]
        Dp = r * 2 ** a; Dt = r ** (2 * a)
        Ep = exact_expectation(edges, M, M, r, a, Dp)
        Et = exact_expectation(edges, M, M, r, a, Dt)
        print(f"r={r} a={a} matching M={M} Delta=1: paper D=r2^a={Dp}: E={float(Ep):.3f} (bound 2MDelta={2*M}) "
              f"{'OK' if Ep <= 2*M else 'VIOLATED'};  true D=r^2a={Dt}: E={float(Et):.3f} {'OK' if Et <= 2*M else 'VIOLATED'}")

# Closed form for a matching (Delta = 1): E sum_gamma (X_gamma - M/D)^2 over all N = r^{2a}
# ordered pair labels = M - M/N + M^2 (N - D)^2 / (N D^2).  With D = N this is < M <= 2M Delta.
print("\nClosed form, paper's r = 64, matching (Delta = 1):")
for a in [1, 2, 3]:
    N = 64 ** (2 * a); Dp = 64 * 2 ** a
    coef = Fr((N - Dp) ** 2, N * Dp * Dp)
    Mstar = 0
    while Mstar - Fr(Mstar, N) + coef * Mstar * Mstar <= 2 * Mstar: Mstar += 1
    print(f"  a={a}: N=r^2a={N}, D_arr(paper)=r2^a={Dp}: E = M - M/N + {float(coef):.4f} M^2; "
          f"exceeds 2 M Delta once M >= {Mstar}  (the proof needs M > H ~ s/sqrt(lambda) >> Delta)")
