"""Parameter bookkeeping of D.4.2: (D.4)-(D.6), depth bound, u >= lambda^{4/5}, and the
exponent sum of D.4.7.  Both readings of D_arr are tested: the paper's r*2^a and the
number of ordered pair labels r^{2a} that Lemma D.3's proof actually needs."""
import math
r = 64; eps = 1.0 / (128 * 1024)

def params(log2s, C=1.0):
    lam = math.ceil(log2s)
    rows = []
    d = 0
    a_prev = 0
    while True:
        u = math.floor(eps * lam / 2 ** d)
        a = a_prev + 2 * u
        L = 2.0 ** a
        log2M_max = math.log2(C) + log2s - 3 * d      # upper bound Cs 8^{-d}
        log2H = log2s - math.log2(math.floor(math.sqrt(lam)))
        active = log2M_max > log2H
        rows.append(dict(d=d, u=u, a=a, log2L=a, log2Darr_paper=math.log2(r) + a,
                         log2Darr_true=2 * a * math.log2(r), active=active,
                         u_ge_lam45=(u >= lam ** 0.8), u_ge_1=(u >= 1)))
        if not active: break
        a_prev = a; d += 1
    return lam, None, rows

for log2s in [20, 60, 1000, 10**5, 10**7]:
    lam, H, rows = params(log2s)
    last = rows[-1]
    print(f"log2 s = {log2s:>9}: lambda={lam}, eps*lambda={eps*lam:.3g}, depths active={len(rows)-1}, "
          f"u_0={rows[0]['u']}, a_max={last['a']}, log2 L={last['log2L']}, "
          f"log2 D_arr(paper)={last['log2Darr_paper']:.1f}, log2 D_arr(true r^2a)={last['log2Darr_true']:.1f}, "
          f"1/1000 log2 s={log2s/1000:.1f}, 0.9 log2 s={0.9*log2s:.1f}")
    print("   u >= 1 at all active depths:", all(x['u_ge_1'] for x in rows[:-1] or rows),
          "; u >= lambda^(4/5) at all active depths:", all(x['u_ge_lam45'] for x in rows[:-1] or rows))

# thresholds
lam_needed_45 = (1 / eps) ** 5
print(f"\n u_0 = eps*lambda >= lambda^(4/5) needs lambda >= (1/eps)^5 = {lam_needed_45:.3e}, i.e. s >= 2^{lam_needed_45:.3e}")
lam_needed_1 = 1 / eps
print(f" u_0 >= 1 needs lambda >= 1/eps = {lam_needed_1:.0f}, i.e. s >= 2^{lam_needed_1:.0f}")
# the real need in (D.11) is 2^u >> lambda^{O(1)}: u >= c log2(lambda); say c = 3
for lam in [2**17, 2**20, 2**24, 2**30]:
    u0 = math.floor(eps * lam)
    print(f" lambda=2^{int(math.log2(lam))}: u_0={u0}, 2^u_0 vs lambda^3.5*u_0: {u0 - 3.5*math.log2(lam) - math.log2(max(u0,1)):+.1f} bits")

# (D.6) with the true D_arr = r^{2a}: 2 D^2 Delta <= H ?  worst case a = 4 eps lambda
print("\n(D.6) margins with D_arr = r^{2a} (exponents of s):")
for a_over_lam in [4 * eps]:
    print(f"  log_s(2 D^2 Delta) ~ 2*12*{a_over_lam:.2e} + 0.9 = {24*a_over_lam + 0.9:.5f} < 1 - o(1)  (H ~ s/sqrt(lambda))")
    print(f"  log_s(L D) ~ {a_over_lam + 12*a_over_lam:.5f}; log_s(2L) ~ {a_over_lam:.5f} < 0.9")

# exponent sum of D.4.7
tot = sum((math.sqrt(2) / 8) ** d for d in range(200))
print(f"\nsum_d (sqrt2/8)^d = {tot:.6f}  (geometric, ratio {math.sqrt(2)/8:.4f})")
print("sum_{j>=1} j^2/2^j =", sum(j * j / 2 ** j for j in range(1, 200)))
print("pi^2/6 =", math.pi ** 2 / 6)
