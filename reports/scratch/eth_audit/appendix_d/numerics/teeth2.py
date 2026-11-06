"""Teeth for the (D.16) test.  For a toy network and a node (t, zeta):
  1. compute v0 = v2(F(T) - [local part only, i.e. tuple budget 0]) : the valuation of the
     total crossing contribution;
  2. set P = v0 + 2 and check (D.16) at full budget P-1 (must hold), at budget 0 (must
     FAIL since v0 < P), and find the largest budget at which it fails.
Run: python3 -I teeth2.py [seed] [r] [maxcases] [offset]   (P = v0 + offset, default 2)
"""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recursion_identity import Toy
from qpoly import v2

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
r = int(sys.argv[2]) if len(sys.argv) > 2 else 2
maxcases = int(sys.argv[3]) if len(sys.argv) > 3 else 3
offset = int(sys.argv[4]) if len(sys.argv) > 4 else 2
rng = random.Random(seed)
a = 2
done = 0
summary = []
for trial in range(8):
    n_rows, n_cols = rng.randint(2, 3), rng.randint(2, 3)
    M = rng.randint(4, 6)
    edges = [(rng.randrange(n_rows), rng.randrange(n_cols)) for _ in range(M)]
    toy = Toy(r, a, n_rows, n_cols, edges, rng)
    for t in (-1, 3, 1, -3):
        for zeta in (1, 3):
            T = t + toy.alpha * zeta
            lhs = toy.F_at(T)
            # local-only value: budget 0 at any P gives the same rhs (only the zero tuple)
            _, _, neff, _, rhs0, _ = toy.check_D16(t, zeta, 3, budget_shift=2)
            v0 = v2(lhs - rhs0)
            if v0 == float("inf") or v0 > 12:
                continue
            P = int(v0) + offset
            ok_full, ntup, neff, _, rhs_full, nontriv = toy.check_D16(t, zeta, P)
            ok_0, _, _, _, _, _ = toy.check_D16(t, zeta, P, budget_shift=P - 1)
            first_fail = None
            for shift in range(1, P):
                ok_s, ntup_s, _, lhs_s, rhs_s, _ = toy.check_D16(t, zeta, P, budget_shift=shift)
                if not ok_s:
                    first_fail = (P - 1 - shift, ntup_s)
                    break
            print(f"trial {trial} M={M} packets={len(toy.packets)} t={t} zeta={zeta}: crossing contribution has v2={int(v0)}; "
                  f"P={P}: full budget ok={ok_full} ({ntup} tuples, {neff} eff. modes); budget 0 ok={ok_0}; "
                  f"largest failing budget={first_fail}", flush=True)
            summary.append((ok_full, not ok_0))
            done += 1
            if done >= maxcases:
                break
        if done >= maxcases:
            break
    if done >= maxcases:
        break
print(f"summary: {sum(1 for a_, b_ in summary if a_)}/{len(summary)} full-budget checks hold; "
      f"{sum(1 for a_, b_ in summary if b_)}/{len(summary)} budget-0 controls fail as required")
