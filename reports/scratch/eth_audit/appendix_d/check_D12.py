"""(D.12): for integer zeta (e=1), check W_xy(T) == [C(T)/(C'(0)(T-y0+x))] * sum_{b<P-1} (2^{i+1} j /(T-y0+x))^b  mod 2^P
for crossing pairs (bit_i(x) == bit_i(y)), T = t + alpha*zeta, i = v2(t), and that the
coefficient of the b-th term has valuation >= b+1 (= weight), and v2(t - y0 + x) <= i."""
from fractions import Fraction as Fr
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_lemma_D5 import v2
def Wval(T, x, y, S, Cp0):
    num = Fr(1)
    for q in S:
        if q != y - x: num *= (T - q)
    return num / Cp0
for a in [2, 3, 4]:
    L = 2 ** a; alpha = 2 ** (a + 1); S = list(range(-L, L))
    Cp0 = Fr(1)
    for q in S:
        if q != 0: Cp0 *= Fr(-q)
    P = 12; bad = 0; checked = 0; minw = []
    for t in S:
        if t == 0: continue
        i = v2(t)
        for zeta in [0, 1, 3, -2]:
            T = t + alpha * zeta
            for x in range(L):
                for y in range(L):
                    if ((x >> i) & 1) != ((y >> i) & 1): continue   # local pair, skip
                    y0 = y % (2 ** (i + 1)); j = y // (2 ** (i + 1))
                    assert v2(t - y0 + x) <= i
                    base = Wval(T, x, y0, S, Cp0)      # C(T)/(C'(0)(T - y0 + x))
                    assert v2(base) >= a + 1 - i
                    ratio = Fr(2 ** (i + 1) * j, T - y0 + x) if j else Fr(0)
                    assert j == 0 or v2(ratio) >= 1
                    ser = sum(base * ratio ** b for b in range(P - 1))
                    for b in range(P - 1):
                        coef = base * Fr(2 ** (i + 1), T - y0 + x) ** b
                        minw.append(v2(coef) - (b + 1))
                    exact = Wval(T, x, y, S, Cp0)
                    d = exact - ser
                    checked += 1
                    if d != 0 and v2(d) < P: bad += 1
    print(f"a={a}: crossing entries checked={checked}, (D.12) failures mod 2^{P}: {bad}; "
          f"min (v2(coef of Z) - weight) = {min(minw)} (>=0 required)")
