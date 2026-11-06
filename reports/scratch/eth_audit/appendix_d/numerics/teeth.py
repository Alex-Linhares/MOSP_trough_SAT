"""Negative control for recursion_identity.py: for non-trivial (t, zeta) cases, lower the
tuple budget in (D.16) from P-1 downwards and report the first budget at which the
congruence mod 2^P fails.  A failure proves the test can fail; the gap between P-1 and
the first failing budget measures the slack in the text's weight w_Z = b+1 (each mode
coefficient actually has valuation b + 1 + (a - i) at these parameters).

Run: python3 -I teeth.py [seed] [r] [P]
"""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recursion_identity import Toy
from qpoly import v2

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
r = int(sys.argv[2]) if len(sys.argv) > 2 else 2
P = int(sys.argv[3]) if len(sys.argv) > 3 else 7
rng = random.Random(seed)
a = 2
done = 0
for trial in range(6):
    n_rows, n_cols = rng.randint(2, 3), rng.randint(2, 3)
    M = rng.randint(4, 6)
    edges = [(rng.randrange(n_rows), rng.randrange(n_cols)) for _ in range(M)]
    toy = Toy(r, a, n_rows, n_cols, edges, rng)
    for t in (-1, 1, -3, 3, -2, 2):
        for zeta in (1, 3):
            ok, ntup, neff, lhs, rhs, nontriv = toy.check_D16(t, zeta, P)
            if not nontriv or not ok:
                continue
            i = int(v2(t))
            print(f"trial {trial} M={M} t={t} (i={i}) zeta={zeta}: full budget P-1={P-1}: ok, lhs-rhs has v2={v2(lhs-rhs)}")
            for shift in range(1, P):
                ok_s, ntup_s, _, lhs_s, rhs_s, _ = toy.check_D16(t, zeta, P, budget_shift=shift)
                print(f"    budget {P-1-shift:2d} ({ntup_s:5d} tuples): v2(lhs-rhs) = {v2(lhs_s-rhs_s)}  -> {'ok' if ok_s else 'FAILS'}")
                if not ok_s:
                    break
            done += 1
            if done >= 4:
                sys.exit(0)
