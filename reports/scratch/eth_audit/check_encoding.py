"""Emulate the comparator's encodeCNF (SubexponentialSAT.lean lines 55-79) and runtimeScale (132-134)."""
import math, random, sys

def encodeNat(n): return [True]*n + [False]
def frame(bits):
    out=[]
    for b in bits: out += [True, b]
    return out + [False]
def encodeList(enc, xs):
    out=[]
    for a in xs: out += [True] + frame(enc(a))
    return out + [False]
def literalCode(var, pos): return 2*var + (1 if pos else 0)
def encodeCNF(n, clauses):  # clauses: set of frozensets of (var,pos)
    cnums = sorted({tuple(sorted({literalCode(v,p) for v,p in C})) for C in clauses})
    return encodeNat(n) + encodeList(lambda C: encodeList(encodeNat, list(C)), cnums)

def L_bound(n,m,k): return n + 2 + m*(2*k*(4*n+1) + 4)

random.seed(1)
print("n m k  L  bound  (8k+7)*(n+m+1)^2")
for n,m,k in [(3,2,2),(10,30,3),(50,200,3),(125,500,4),(1000,4000,3)]:
    cl=set()
    while len(cl)<m:
        cl.add(frozenset((random.randrange(n), random.random()<0.5) for _ in range(k)))
    L=len(encodeCNF(n,cl))
    assert L<=L_bound(n,m,k)
    print(n,m,k,L,L_bound(n,m,k),(8*k+7)*(n+m+1)**2)
# duplicates collapse
A={frozenset([(0,True),(1,False)])}
print("dup clause collapses:", len(encodeCNF(2,A))==len(encodeCNF(2,set(A))))
# tautological + empty clause allowed
print("empty clause L:", len(encodeCNF(1,{frozenset()})), "taut:", len(encodeCNF(1,{frozenset([(0,True),(0,False)])})))

def scale(n): x=math.log(n+16); return n*math.log(x)**2/math.sqrt(x)
print("\nn, runtimeScale(n)/n")
for n in [1,20,100,1000,10**6,10**12,10**100,10**1000]:
    print(f"{n:>8g}" if n<1e300 else f"10^{round(math.log10(n))}", scale(n)/n if n<1e300 else None)
# crossover with A=1: runtimeScale(n)/n < 1  <=>  (log x)^2 < sqrt(x), x = log(n+16)
def f(x): return math.log(x)**2 - math.sqrt(x)
lo,hi=10.0,20000.0
for _ in range(200):
    mid=(lo+hi)/2
    if f(mid)>0: lo=mid
    else: hi=mid
print("crossover x=log(n+16)=",lo," i.e. n ~ e^%.0f"%lo, " (log10 n ~ %.0f)"%(lo/math.log(10)))
# max of (log x)^2/sqrt x : derivative zero at log x = 4 -> x=e^4
x=math.e**4; print("max ratio at n~e^(e^4):", math.log(x)**2/math.sqrt(x))
