"""loop0012 item 03: the exact statements of `DegreeBound/Weights.lean`, checked in
exact rationals before they were stated in Lean (`reports/edwards_mcdermid.md` §3).

    python3 reports/scratch/edwards_mcdermid/03_weights/check.py   # writes check.log

Item 02 checked W1–W5 to n = 40; this re-checks them to n = 200 in the exact form
Lean proves them — the coupled invariant of Lemma 8.3, the `g'` recurrence and
sandwich of Lemma 8.4, property 6, the closed form of Lemma 8.1 and Lemma 8.5 —
plus the Lean recursion itself (the four-case pattern) against the Python `g`.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from learning.edwards_mcdermid import g, g_prime, g_closed_form  # noqa: E402

N = 200
out = []


@lru_cache(maxsize=None)
def g_lean(n: int) -> Fraction:
    """`g` exactly as `Weights.lean` defines it: cases 0, 1, 2, 3 and `n + 4`."""
    if n == 0 or n == 1 or n == 2:
        return Fraction(0)
    if n == 3:
        return Fraction(1, 6)
    m = n - 4
    return ((m + 2) * g_lean(m + 3) + g_lean(m + 2) + 1) / (m + 4)


def gp(n: int) -> Fraction:
    """`g'` as Lean defines it: `g n − g (n − 1)` with truncated subtraction."""
    return g_lean(n) - g_lean(max(n - 1, 0))


for n in range(N + 1):
    assert g_lean(n) == g(n), n                                             # the transcription
    assert gp(n) == g_prime(n), n
# g_table
table = {4: "1/3", 5: "13/30", 6: "23/45", 7: "359/630", 8: "1553/2520", 9: "14827/22680"}
for d, s in table.items():
    assert g_lean(d) == Fraction(s), d
ptable = {3: "1/6", 4: "1/6", 5: "1/10", 6: "7/90", 7: "37/630", 8: "13/280"}
for d, s in ptable.items():
    assert gp(d) == Fraction(s), d
out.append(f"g table to d = 9 and g' table to d = 8 agree with report §0's notation paragraph")
# the coupled invariant of Lemma 8.3 (g_mono_aux): 0 ≤ g n ≤ g (n+1) ≤ (1 + g n)/2, g n < 1
for n in range(N):
    assert 0 <= g_lean(n) <= g_lean(n + 1) <= (1 + g_lean(n)) / 2, n
    assert g_lean(n) < 1, n
out.append(f"coupled invariant 0 ≤ g(n) ≤ g(n+1) ≤ (1 + g(n))/2 and g(n) < 1 for n ≤ {N - 1}")
# W1 as Lean states it: (m+4) g(m+4) = (m+2) g(m+3) + g(m+2) + 1
for m in range(N - 3):
    assert (m + 4) * g_lean(m + 4) == (m + 2) * g_lean(m + 3) + g_lean(m + 2) + 1, m
out.append(f"W1 (g_recurrence) for 4 ≤ n ≤ {N}")
# g'_recurrence: n g'(n) = (n − 3) g'(n − 1) + g'(n − 2), n ≥ 5
for n in range(5, N + 1):
    assert n * gp(n) == (n - 3) * gp(n - 1) + gp(n - 2), n
out.append(f"g'_recurrence for 5 ≤ n ≤ {N}")
# the sandwich of Lemma 8.4 (g'_antitone_aux): g'(n)/3 ≤ g'(n+1) ≤ g'(n), n ≥ 3
for n in range(3, N):
    assert gp(n) / 3 <= gp(n + 1) <= gp(n), n
out.append(f"sandwich g'(n)/3 ≤ g'(n+1) ≤ g'(n) for 3 ≤ n ≤ {N - 1}; g'(3) = g'(4) = 1/6 (equality at the base)")
# W4: 1 − g(n) = (n − 1) g'(n) + g'(n − 1), n ≥ 4
for n in range(4, N + 1):
    assert 1 - g_lean(n) == (n - 1) * gp(n) + gp(n - 1), n
out.append(f"W4 (one_sub_g_eq) for 4 ≤ n ≤ {N}")
# W5: 0 ≤ g' ≤ 1/6 everywhere, g' ≤ g, g' = 0 below 3
for n in range(N + 1):
    assert 0 <= gp(n) <= Fraction(1, 6), n
    assert gp(n) <= g_lean(n), n
    assert (gp(n) == 0) == (n <= 2), n
out.append(f"W5: 0 ≤ g'(n) ≤ 1/6, g'(n) ≤ g(n), g'(n) = 0 iff n ≤ 2, for n ≤ {N}")
# Lemma 8.1 closed form with A(0) = 0, A(n+1) = (n+1)! − A(n)
A = [Fraction(0)]
fact = [1]
for n in range(1, N + 1):
    fact.append(fact[-1] * n)
    A.append(fact[-1] - A[-1])
for n in range(2, N + 1):
    rhs = Fraction(7, 2) * A[n] / fact[n] + Fraction(3, 2) * (-1) ** n / fact[n] - Fraction(5, 2)
    assert rhs == g_lean(n) == g_closed_form(n), n
out.append(f"Lemma 8.1 closed form (7/2) A(n)/n! + (3/2)(−1)^n/n! − 5/2 for 2 ≤ n ≤ {N}, A(0) = 0, A(n+1) = (n+1)! − A(n)")
# Lemma 8.5: g(n)/n strictly decreasing from 5 (and NOT from 4: g(4)/4 < g(5)/5)
assert g_lean(4) / 4 < g_lean(5) / 5
for n in range(5, N):
    assert g_lean(n + 1) / (n + 1) < g_lean(n) / n, n
out.append(f"Lemma 8.5: g(n+1)/(n+1) < g(n)/n for 5 ≤ n ≤ {N - 1}; false at n = 4 (1/12 < 13/150)")
# the auxiliary fact the Lean proof of 8.5 uses: g(n) ≥ 1/2 for n ≥ 6, g(n) > n/(2n+1) there
for n in range(6, N + 1):
    assert g_lean(n) >= Fraction(1, 2) and g_lean(n) > Fraction(n, 2 * n + 1), n
out.append(f"g(n) ≥ 1/2 > n/(2n+1) for 6 ≤ n ≤ {N} (the step of Lemma 8.5 in Lean); g(5) = 13/30 < 5/11, so n = 5 is a base case")

log = Path(__file__).with_name("check.log")
log.write_text("\n".join(out) + "\nall checks passed\n")
print("\n".join(out)); print("all checks passed")
