"""Direct check of Lemma D.4: W_xy(t + alpha z) in Z_(2)[z] for all x,y in [0,L), t in S."""
from fractions import Fraction as Fr
import sys
sys.path.insert(0, '.')
from check_lemma_D5 import polymul, polyshift, v2, v2min

for a in [1, 2, 3, 4]:
    L = 2 ** a; alpha = 2 ** (a + 1); S = list(range(-L, L))
    Cp0 = Fr(1)
    for t in S:
        if t != 0: Cp0 *= Fr(-t)
    bad = []
    for x in range(L):
        for y in range(L):
            num = [Fr(1)]
            for t in S:
                if t != (y - x): num = polymul(num, [Fr(-t), Fr(1)])
            W = [c / Cp0 for c in num]
            for t in S:
                jet = polyshift(W, t)
                jet = [c * Fr(alpha) ** k for k, c in enumerate(jet)]
                m = v2min(jet)
                if m < 0: bad.append((x, y, t, m))
            # also W(0) = I
            W0 = W[0]
            assert W0 == (1 if x == y else 0), (x, y, W0)
    print(f"a={a} L={L}: W(0)=I ok; non-integral (x,y,t,minval): {bad[:10]} count={len(bad)}")
