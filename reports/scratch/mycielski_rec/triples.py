import pandas as pd, glob
def chains():
    rows=[]
    for fn in ['data_all7.csv','data_named.csv','data_c8.csv']:
        d=pd.read_csv(fn); d=d[d.pw.notna()]
        for s,g in d.groupby('seed'):
            p=dict(zip(g.j,g.pw)); n=dict(zip(g.j,g.n)); niso=int(g[g.j==0].niso.iloc[0]); m0=int(g[g.j==0].m.iloc[0])
            rows.append((fn,s,[p[j] for j in sorted(p) if all(i in p for i in range(j+1))],int(n[0]),m0,niso))
    return rows
if __name__=='__main__':
    R=chains(); T=[]
    for fn,s,p,n,m,niso in R:
        for j in range(len(p)-2): T.append((s,j,n,m,niso,p[j],p[j+1],p[j+2]))
    t=pd.DataFrame(T,columns=['seed','j','n0','m0','niso','a','b','c'])
    t['fib']=t.c-t.b-t.a; t['conv']=t.c-2*t.b+t.a
    print(len(t)); print('min fib by a'); print(t.groupby('a').fib.agg(['min','count']).to_string())
    print(t.sort_values('fib').head(15).to_string())
    print('conv',t.conv.min()); print(t.sort_values('conv').head(10).to_string())
