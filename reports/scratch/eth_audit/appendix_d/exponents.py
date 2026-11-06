"""Exponent arithmetic for Appendix D, and the 'sufficiently large n' thresholds.
Run: python3 -I exponents.py"""
import math
from decimal import Decimal, getcontext
getcontext().prec = 60

def lam(n): return math.ceil(math.log2(n))
def nu(n): return math.ceil(math.log2(lam(n)))

print('== (4) s = n*nu: ratio (s/sqrt(ln s)) / (n ln ln n / sqrt(ln n)) ==')
for e in (2, 3, 5, 10, 20, 50, 100, 1000, 10000):
    # n = 10^e via logs: ln n = e ln 10; lambda ~ log2 n; nu = ceil(log2 lambda)
    ln_n = e * math.log(10); l = math.ceil(ln_n / math.log(2)); v = math.ceil(math.log2(l))
    ln_s = ln_n + math.log(v)
    ratio = (v / math.sqrt(ln_s)) / (math.log(ln_n) / math.sqrt(ln_n))   # s/sqrt(ln s) divided by n lnln n/sqrt(ln n), per n
    print(f'n=1e{e}: lambda={l} nu={v}  ratio={ratio:.3f}')
print('   (ratio bounded: nu <= log2 log2 n + 1 <= 1.45 ln ln n + 1.5, and ln s >= ln n)')

print('\n== clause-network branch, m <= n*nu: s = n(1+nu); (s/sqrt(ln s)) / (n lnln n/sqrt(ln n)) ==')
for e in (2, 5, 10, 100, 1000):
    ln_n = e * math.log(10); l = math.ceil(ln_n / math.log(2)); v = math.ceil(math.log2(l))
    ln_s = ln_n + math.log(1 + v)
    print(f'n=1e{e}: ratio={((1+v)/math.sqrt(ln_s))/(math.log(ln_n)/math.sqrt(ln_n)):.3f}')

print('\n== fixed density: m <= Dn, s <= (1+D)n: (s/sqrt(ln s)) <= (1+D) n/sqrt(ln n) trivially; '
      'for the single algorithm the input takes the clause branch once nu >= D, i.e. n >= n0(D): ==')
for D in (1, 2, 4, 8, 16):
    # nu(n) >= D  iff  ceil(log2 n) > 2^(D-1)  iff  n > 2^(2^(D-1))
    print(f'D={D}: clause branch for every m <= Dn once n > 2^(2^{D-1}); below that the parity branch gives the first bound, O_D(1) overhead')

print('\n== (3) degree hypothesis of Theorem D.1 in Lemma D.2: n^(3/4) lambda^C <= ceil((n nu)^(9/10)) ==')
print('   variable-group incidences <= ceil(n/J) * D*, D* <= (c k lambda^c + 1)(sqrt(lambda)+1), with a <= c n, scope <= k lambda^c')
for (k, c) in [(3, 1), (3, 2), (3, 6), (2, 6), (3, 10)]:
    # find smallest exponent E (n = 2^E) at which the bound holds and stays (check monotone-ish over a range)
    def ok(E):
        n = 2.0 ** E; l = E; v = math.ceil(math.log2(l)); s = n * v
        J = math.ceil(n ** 0.25)
        Dstar = (c * k * l ** c + 1) * (math.sqrt(l) + 1)
        vg = math.ceil(n / J) * Dstar
        tg = math.ceil(c * n / J) * k * l ** c
        return max(vg, tg) <= math.ceil(s ** 0.9)
    E0 = None
    for E in range(5, 20000):
        if ok(E) and all(ok(E2) for E2 in range(E, min(E + 200, 20000))): E0 = E; break
    print(f'k={k} c={c}: holds for all n >= 2^{E0}  (n0 ~ 1e{E0 * math.log10(2):.0f})')

print('\n== the arrays count: J^2 log2(K+1) vs sqrt(n) ln n, K = k(a + 2n), a = c n ==')
for e in (2, 5, 10, 50):
    n = 10 ** e; J = math.ceil(n ** 0.25); K = 3 * (6 * n + 2 * n)
    print(f'n=1e{e}: J^2 log2(K+1) = {J*J*math.log2(K+1):.3e}, sqrt(n) ln n = {math.sqrt(n)*math.log(n):.3e}, '
          f'n nu/sqrt(lambda) = {n*nu(n)/math.sqrt(lam(n)):.3e}')

print('\n== exhaustive search for n < n0 within the bound: need 2^n <= 2^(C n lnln n/sqrt(ln n)), i.e. C >= sqrt(ln n)/lnln n ==')
for E in (20, 100, 400, 1000, 5000):
    ln_n = E * math.log(2)
    print(f'n = 2^{E}: C >= {math.sqrt(ln_n)/math.log(ln_n):.2f}  (fixed density route: C >= sqrt(ln n) = {math.sqrt(ln_n):.1f})')
