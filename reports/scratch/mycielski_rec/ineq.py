import pandas as pd, numpy as np, warnings
from fractions import Fraction as Fr
warnings.filterwarnings('ignore')
from chains import chains
R=chains(); T=[]
for s,p in R.items():
    for j in range(len(p)-2): T.append((s,j,p[j],p[j+1],p[j+2]))
t=pd.DataFrame(T,columns=['seed','j','a','b','c'])
t=t[~t.seed.isin(['g3','K2','P2'])]   # the M chain itself (K2) is held out entirely
train=t[t.j==0]; test=t[t.j>=1]
M=[(1,2,5),(2,5,10),(5,10,20),(10,20,38),(20,38,72)]
xs=[Fr(k,4) for k in range(0,13)]; ys=[Fr(k,4) for k in range(-8,9)]
lows=[];ups=[]
for x in xs:
    for y in ys:
        r=train.c-float(x)*train.b-float(y)*train.a
        zl=r.min(); zu=r.max()
        rt=test.c-float(x)*test.b-float(y)*test.a
        okl=(rt>=zl-1e-9).all(); oku=(rt<=zu+1e-9).all()
        okMl=all(c-float(x)*b-float(y)*a>=zl-1e-9 for a,b,c in M); okMu=all(c-float(x)*b-float(y)*a<=zu+1e-9 for a,b,c in M)
        pred_l=float(x)*72+float(y)*38+zl; pred_u=float(x)*72+float(y)*38+zu
        lows.append((pred_l,str(x),str(y),zl,okl,okMl)); ups.append((pred_u,str(x),str(y),zu,oku,okMu))
lows=[l for l in lows if l[4] and l[5]]; ups=[u for u in ups if u[4] and u[5]]
lows.sort(reverse=True); ups.sort()
print('train',len(train),'test',len(test))
print('best surviving lower bounds  c >= x b + y a + z  (pred for M9):'); [print(' ',l) for l in lows[:8]]
print('best surviving upper bounds  c <= x b + y a + z:'); [print(' ',u) for u in ups[:8]]
