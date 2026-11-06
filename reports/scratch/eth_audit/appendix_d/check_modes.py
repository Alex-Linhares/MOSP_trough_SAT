"""(D.15): number of exponent tuples with sum_Z w_Z beta_Z < P, when there are n = 6M/D
variables of each weight w = 1, 2, ..., P-1, against the bound exp((1+pi^2) sqrt(M P / D))
derived from the generating-function argument, and the partition asymptotic exp(pi sqrt(2 n P/3))."""
import math
def count(n, P):
    # number of multisets: coefficient sum of prod_{w>=1} (1-x^w)^{-n} for total < P
    c = [0] * P; c[0] = 1
    for w in range(1, P):
        for _ in range(n):          # n copies of weight w
            for k in range(w, P):
                c[k] += c[k - w]
    return sum(c)
for (M, D, P) in [(8, 2, 20), (16, 4, 40), (32, 8, 60), (64, 8, 100), (24, 2, 60)]:
    n = 6 * M // D
    N = count(n, P)
    gf = math.exp((1 + math.pi ** 2) * math.sqrt(M * P / D))
    part = math.exp(math.pi * math.sqrt(2 * n * P / 3))
    print(f"M={M} D={D} P={P} n=6M/D={n}: exact count={N:.3e}  (D.15) bound={gf:.3e}  "
          f"{'OK' if N <= gf else 'VIOLATED'}   (coloured-partition asymptotic {part:.3e})")
