"""Recurrence guessing with honest parameter accounting.
A fit of order r, polynomial degree d uses P = (r+1)(d+1) - 1 free parameters
(one normalisation) and has E = N - r equations from N terms; spare = E - P.
Constant-coefficient linear recurrences are the d = 0 case with the leading
coefficient fixed to 1 (P = r, or r + 1 with a constant term).  A fit with
spare < 2 is numerology and is labelled so.  Hold-out: refit on N-1 terms and
predict the last."""
import sympy as sp
from sympy import Matrix, Rational, binomial, floor, symbols, rsolve, Function, fibonacci
from fractions import Fraction

n = symbols('n', integer=True)

def fit_linear(seq, r, const=False):
    """a_n = sum_{j=1..r} c_j a_{n-j} (+ c0).  Return (coeffs, spare, holdout_ok) or None."""
    N = len(seq)
    P = r + (1 if const else 0)
    E = N - r
    spare = E - P
    def solve(terms):
        rows, rhs = [], []
        for i in range(r, len(terms)):
            rows.append([terms[i - j] for j in range(1, r + 1)] + ([1] if const else []))
            rhs.append(terms[i])
        A, b = Matrix(rows), Matrix(rhs)
        try:
            sol = A.solve_least_squares(b) if A.rows > A.cols else A.solve(b)
        except Exception:
            return None
        if any((A * sol - b)[i] != 0 for i in range(A.rows)):
            return None
        return list(sol)
    if E < P:
        return dict(ok=False, reason="underdetermined", spare=spare, P=P, E=E)
    sol = solve(seq)
    if sol is None:
        return dict(ok=False, reason="inconsistent", spare=spare, P=P, E=E)
    # hold-out
    sol2 = solve(seq[:-1]) if (N - 1 - r) >= P else None
    pred = None
    if sol2 is not None:
        pred = sum(sol2[j - 1] * seq[N - 1 - j] for j in range(1, r + 1)) + (sol2[-1] if const else 0)
    return dict(ok=True, coeffs=sol, spare=spare, P=P, E=E, holdout_pred=pred, holdout_ok=(pred == seq[-1]) if pred is not None else None)

def fit_holonomic(seq, r, d):
    """sum_{j=0..r} p_j(n) a_{n-j} = 0 with deg p_j <= d, nontrivial.  Index n starts at 0."""
    N = len(seq)
    P = (r + 1) * (d + 1) - 1
    E = N - r
    spare = E - P
    def nullspace(terms):
        rows = []
        for i in range(r, len(terms)):
            row = []
            for j in range(r + 1):
                for e in range(d + 1):
                    row.append(Rational(i) ** e * terms[i - j])
            rows.append(row)
        A = Matrix(rows)
        return A.nullspace()
    if E < P:
        return dict(ok=False, reason="underdetermined", spare=spare, P=P, E=E)
    ns = nullspace(seq)
    if len(ns) != 1:
        return dict(ok=False, reason=f"nullspace dim {len(ns)}", spare=spare, P=P, E=E)
    vec = ns[0]
    # hold-out: nullspace from N-1 terms must be 1-dim and predict the last
    pred = None
    if (N - 1 - r) >= P:
        ns2 = nullspace(seq[:-1])
        if len(ns2) == 1:
            v = ns2[0]
            i = N - 1
            coef = lambda j: sum(v[j * (d + 1) + e] * Rational(i) ** e for e in range(d + 1))
            c0 = coef(0)
            if c0 != 0:
                pred = -sum(coef(j) * seq[i - j] for j in range(1, r + 1)) / c0
    polys = []
    for j in range(r + 1):
        polys.append(sp.expand(sum(vec[j * (d + 1) + e] * n ** e for e in range(d + 1))))
    return dict(ok=True, polys=polys, spare=spare, P=P, E=E, holdout_pred=pred, holdout_ok=(pred == seq[-1]) if pred is not None else None)

def report(name, seq, max_r=4, max_d=2):
    print(f"\n== {name}: {seq}  (N={len(seq)} terms)")
    for r in range(1, max_r + 1):
        for const in (False, True):
            f = fit_linear(seq, r, const)
            tag = f"linear order {r}{' + const' if const else ''}: P={f['P']} E={f['E']} spare={f['spare']}"
            if f["ok"]:
                label = "FIT" if f["spare"] >= 2 else "numerology (spare < 2)"
                print(f"  {tag}: coeffs {f['coeffs']}  holdout {f['holdout_pred']}->{f['holdout_ok']}  [{label}]")
            else:
                print(f"  {tag}: {f['reason']}")
    for r in range(1, max_r + 1):
        for d in range(1, max_d + 1):
            f = fit_holonomic(seq, r, d)
            tag = f"holonomic order {r} degree {d}: P={f['P']} E={f['E']} spare={f['spare']}"
            if f["ok"]:
                label = "FIT" if f["spare"] >= 2 else "numerology (spare < 2)"
                print(f"  {tag}: polys {f['polys']}  holdout {f['holdout_pred']}->{f['holdout_ok']}  [{label}]")
            else:
                print(f"  {tag}: {f['reason']}")

if __name__ == "__main__":
    hyper = [1, 2, 4, 7, 13, 23]                         # pw(Q_d), d = 1..6
    hyper0 = [0] + hyper                                  # with Q_0 = K_1, pw 0
    hyper_inc = [hyper[i + 1] - hyper[i] for i in range(5)]
    myc = [1, 2, 5, 10, 20, 38]                           # pw(M_k), k = 2..7 (networkx index; M_2 = K_2)
    myc0 = [0] + myc                                      # with M_1 = K_1
    myc_inc = [myc[i + 1] - myc[i] for i in range(5)]
    tern = [1, 2, 3, 4]
    report("hypercube pw(Q_d), d=1..6", hyper)
    report("hypercube pw(Q_d), d=0..6", hyper0)
    report("hypercube increments", hyper_inc)
    report("mycielski pw(M_k), k=2..7", myc)
    report("mycielski pw(M_k), k=1..7 (K_1 first)", myc0)
    report("mycielski increments", myc_inc)
    report("ternary tree pw(T_h)", tern)
    # formula checks
    print("\nhypercube formula sum_{i<d} C(i, floor(i/2)):", [sum(binomial(i, i // 2) for i in range(d)) for d in range(0, 9)])
    print("A001629 from g.f. x^2/(1-x-x^2)^2:", sp.series(symbols('x') ** 2 / (1 - symbols('x') - symbols('x') ** 2) ** 2, symbols('x'), 0, 11).removeO())
    print("A001629 closed form ((n-1)F_n + 2n F_{n-1})/5:", [((k - 1) * fibonacci(k) + 2 * k * fibonacci(k - 1)) / 5 for k in range(0, 11)])
    # The two spare-0 holonomic fits, tested against the formulas beyond the data.
    # Mycielski (K_1 first, index i: a_i = pw(M_{i+1})): (1-i) a_i + i a_{i-1} + (i+1) a_{i-2} = 0
    A = lambda m: ((m - 1) * fibonacci(m) + 2 * m * fibonacci(m - 1)) / 5   # A001629(m)
    bad = [i for i in range(2, 80) if (1 - i) * A(i + 1) + i * A(i) + (i + 1) * A(i - 1) != 0]
    print("\nMycielski order-2 degree-1 fit holds on A001629 for i=2..79 except:", bad,
          "; it predicts a_7 =", sp.Rational(7 * 38 + 8 * 20, 6), "(myciel7 would be 71) and a_8 =", sp.Rational(8 * 71 + 9 * 38, 7))
    # Hypercube (Q_0 first): (2 - 3i/4) a_i + (3i/4 - 5/2) a_{i-1} + (i - 3/2) a_{i-2} = 0  -> predicts a_7
    i = 7; a6, a5 = 23, 13
    pred = -((sp.Rational(3 * i, 4) - sp.Rational(5, 2)) * a6 + (i - sp.Rational(3, 2)) * a5) / (2 - sp.Rational(3 * i, 4))
    print("Hypercube order-2 degree-1 fit predicts pw(Q_7) =", pred, "=", float(pred), "; the formula gives 43 -> the fit is wrong")
    # Linear order-3 fit a_n = a_{n-1} + 2 a_{n-2} - a_{n-3} on the hypercube predicts
    print("Hypercube linear order-3 fit predicts pw(Q_7) =", 23 + 2 * 13 - 7, "; formula 43 -> wrong")
    print("Mycielski linear order-3 fit a_n = 12/5 a_{n-1} - 2 a_{n-3} predicts pw(M_8) =", sp.Rational(12 * 38, 5) - 2 * 10, "-> not an integer, wrong")
