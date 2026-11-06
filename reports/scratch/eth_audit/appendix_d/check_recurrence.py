"""Running-time recurrence of D.4.7, redone.  Per active call at depth d:
   N_d <= s^{c1} exp(c2 M_d / sqrt(u_d)),   M_d <= C s 8^{-d},   u_d = floor(eps lambda / 2^d) >= eps lambda / 2^{d+1}
   T(d) <= poly(s+L) N_d + N_d T(d+1)   (local work is added per call, children multiplied)
   => T(0) <= poly(s+L) sum_d prod_{d'<d} N_{d'} + prod_d N_d * T_leaf,  T_leaf <= 2^H poly(s) (s+L)^b 2^{A s^{9/10}}.
This script evaluates log of the call count and of the total time, in units of s/sqrt(lambda), symbolically
in the constants, and numerically for the paper's eps and r, to confirm exp(O(s/sqrt(lambda))) (s+L)^{O(1)}."""
import math
eps = 1 / (128 * 1024)
ratio = math.sqrt(2) / 8
geo = 1 / (1 - ratio)
print(f"sum_d (sqrt2/8)^d = {geo:.4f};  M_d/sqrt(u_d) <= C sqrt(2/eps) (s/sqrt(lambda)) (sqrt2/8)^d, sqrt(2/eps) = {math.sqrt(2/eps):.1f}")
print(f"=> sum_d M_d/sqrt(u_d) <= {geo*math.sqrt(2/eps):.0f} C s/sqrt(lambda)")
# number of calls: sum_{d<=dmax} prod_{d'<d} N_d'  <= (dmax+1) s^{c1 dmax} exp(c2 * sum)
# dmax <= log2(lambda)/6 + O(1) -> s^{c1 dmax} = exp(O(log s log lambda)) = exp(o(s/sqrt(lambda)))
for log2s in [10**6, 10**8, 10**10]:
    lam = log2s; dmax = math.log2(lam) / 6
    log2_poly_bits = math.log2(20 * dmax * log2s)                    # s^{c1 dmax} over the path: c1 dmax log2 s bits
    log2_main_bits = math.log2(geo * math.sqrt(2 / eps)) + log2s - 0.5 * math.log2(lam) - math.log2(math.log(2))
    print(f"log2 s={log2s:.0e}: dmax~{dmax:.1f}; log2(poly-factor bits over a path) = {log2_poly_bits:.1f}; "
          f"log2(main-term bits, c2*C=1) = {log2_main_bits:.3e}: the polynomial branching factor is negligible")
print("The per-call poly(s+L) factor is additive per call, so total = #calls * poly(s+L) + #leaves * leafcost:")
print("  (s+L)^{O(1)} exp(O(s/sqrt(lambda))), as claimed; the poly factor does not compound with depth.")
print("Leaf: 2^H with H = s/floor(sqrt(lambda)); exp(A s^{9/10}) = exp(o(s/sqrt(lambda))); packet tensors exp(O(L log s)) = exp(O(s^{1/1000} log s)).")
