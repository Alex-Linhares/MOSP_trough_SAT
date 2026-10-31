"""The finite first-moment bound of finite_bound_cs.py as importable functions (same formulas)."""
import math
lg = math.lgamma
def lchoose(a, b):
    if b < 0 or b > a: return -math.inf
    return lg(a + 1) - lg(b + 1) - lg(a - b + 1)
def lq(n, t, s):
    terms = [lchoose(n - t, s), lchoose(n - t + 1, s)]
    neg = lchoose(n - 2 * t + 1, s)
    m = max(terms)
    val = math.exp(terms[0] - m) + math.exp(terms[1] - m) - (math.exp(neg - m) if neg > -math.inf else 0.0)
    if val <= 0: return -math.inf
    return m + math.log(val) - lchoose(n, s)
def log_pairs(n, t):
    return lchoose(n, t) + lchoose(n - t, t - 1)
def log_bound(n, sizes, k):
    t = (n - k + 1) // 2
    if t < 1 or 2 * t - 1 > n: return math.inf
    return log_pairs(n, t) + sum(lq(n, t, s) for s in sizes)
def floors(n, sizes):
    """(floor at bound < 1, floor at bound < 0.01) on the optimum = pw + 1."""
    k1 = max((k for k in range(n) if log_bound(n, sizes, k) < 0), default=-1)
    k2 = max((k for k in range(n) if log_bound(n, sizes, k) < math.log(0.01)), default=-1)
    return k1 + 2, k2 + 2
