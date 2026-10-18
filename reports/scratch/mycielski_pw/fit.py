import itertools, sympy as sp
from fractions import Fraction as Fr
K=list(range(2,9)); A=[1,2,5,10,20,38,72]; a=dict(zip(K,A))
n={k:3*2**(k-2)-1 for k in K}; n[9]=383
# edges of M_k: e2=1, e_{k+1}=3e_k+n_k
e={2:1}
for k in range(2,9): e[k+1]=3*e[k]+n[k]
print("n",[n[k] for k in K],"e",[e[k] for k in K])
print("n-pw",[n[k]-a[k] for k in K], "2a-a'",[2*a[k]-a[k+1] for k in K[:-1]])
print("a-a1-a2",[a[k]-a[k-1]-a[k-2] for k in K[2:]])
print("ratios",[round(a[k+1]/a[k],4) for k in K[:-1]],"pw/n",[round(a[k]/n[k],4) for k in K])
# --- linear models: a(k) = sum_j c_j * phi_j(k), exact rational fit on p terms, test on others
k=sp.symbols('k')
basis={'1':lambda k:1,'k':lambda k:k,'k2':lambda k:k*k,'2^k':lambda k:2**k,'k2^k':lambda k:k*2**k,
 'n':lambda k:n[k],'e':lambda k:e[k],'3^k':lambda k:3**k,'fib':lambda k:sp.fibonacci(k),'kfib':lambda k:k*sp.fibonacci(k),
 'lucas':lambda k:sp.lucas(k),'(-1)^k':lambda k:(-1)**k,'2^k/k':lambda k:sp.Rational(2**k,k), 'phi^k':None}
basis.pop('phi^k')
def fit(cols, ks):
    M=sp.Matrix([[basis[c](kk) for c in cols] for kk in ks]); b=sp.Matrix([a[kk] for kk in ks])
    try: return M.solve(b)
    except Exception: return None
surv=[]
names=list(basis)
for p in (1,2,3):
  for cols in itertools.combinations(names,p):
    # fit on first p terms after allowing leave-out: fit on the first 7-2=5? use exactly p terms (minimal), from earliest; hold out the rest
    # leave-out test: fit on every p-subset among the 7 terms? Use: fit on last p terms of the first 5, test k=7,8 and also all
    for ks in [K[5-p:5]]:
      c=fit(cols,ks)
      if c is None: continue
      f=lambda kk: sum(ci*basis[cn](kk) for ci,cn in zip(c,cols))
      if all(f(kk)==a[kk] for kk in K): surv.append((cols,list(c),f(9)))
print("closed-form linear-basis survivors (exact on all 7, fitted on <=3):",surv)
# near misses with floor/round of a single scaled basis element
for cn in ['n','2^k','e','k2^k','2^k/k']:
  for r in [Fr(p,q) for q in range(1,40) for p in range(1,q*3)]:
    for rnd,name in [(lambda x:sp.floor(x),'floor'),(lambda x:sp.ceiling(x),'ceil'),(lambda x:sp.floor(x+sp.Rational(1,2)),'round')]:
      for off in range(-3,4):
        if all(rnd(sp.Rational(r.numerator,r.denominator)*basis[cn](kk))+off==a[kk] for kk in K):
          print("FLOOR-FORM", name, r, cn, off, rnd(sp.Rational(r.numerator,r.denominator)*basis[cn](9))+off)
# --- integer recurrences a(k)=sum c_i a(k-i) + c0 (+ c1*k), check on all terms where defined
rec=[]
for order in (1,2,3):
  for cs in itertools.product(range(-2,3),repeat=order):
    if cs[-1]==0: continue
    for c0 in range(-4,5):
      for c1 in range(-2,3):
        ok=True; cnt=0
        for kk in K[order:]:
          if sum(ci*a[kk-i-1] for i,ci in enumerate(cs))+c0+c1*kk!=a[kk]: ok=False;break
          cnt+=1
        if ok: rec.append((cs,c0,c1,cnt,sum(ci*a[9-i-1] for i,ci in enumerate(cs))+c0+c1*9))
print("integer recurrences fitting all terms:",rec)
# rational recurrence fits with leave-out: order r + const, params r+1, need r+1 eqs, uses r+1+r terms
for order in (1,2):
  for withk in (False,True):
    p=order+1+withk
    eqk=K[order:]
    if len(eqk)-p<1: continue
    cs=sp.symbols(f'c0:{p}')
    def row(kk): return [a[kk-i-1] for i in range(order)]+[1]+([kk] if withk else [])
    M=sp.Matrix([row(kk) for kk in eqk[:p]]); b=sp.Matrix([a[kk] for kk in eqk[:p]])
    try: c=M.solve(b)
    except Exception as ex: print(order,withk,"singular"); continue
    pred={kk:(sp.Matrix([row(kk)])*c)[0] for kk in eqk}
    print(f"rational rec order {order} k-term {withk}: coeffs {list(c)}; held-out", {kk:(pred[kk],a[kk]) for kk in eqk[p:]})
