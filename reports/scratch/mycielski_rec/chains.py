"""All gathered chains: seed -> list of exact pw(mu^j(G)), j = 0, 1, ... (stops at first non-exact)."""
import pandas as pd, glob, re
FILES=['data_all7.csv','data_named.csv','data_c8.csv','data_c8_mu3.csv','data_extra.csv','data_deep.csv','data_deep_named.csv','data_kn.csv','data_seeddeep.csv']
def load_rows():
    out=[]
    for fn in FILES:
        try: d=pd.read_csv(fn)
        except FileNotFoundError: continue
        d['file']=fn
        m=d.seed.str.extract(r'^(.*)@(\d+)$')
        off=pd.to_numeric(m[1]).fillna(0).astype(int); d['seed']=m[0].fillna(d.seed); d['j']=d.j+off
        out.append(d)
    d=pd.concat(out,ignore_index=True)
    d=d.sort_values('status').drop_duplicates(['seed','j'])  # exact statuses sort before 'upper'
    return d
def chains():
    d=load_rows(); d=d[d.pw.notna()]
    R={}
    for s,g in d.groupby('seed'):
        p=dict(zip(g.j,g.pw)); seq=[]
        j=0
        while j in p: seq.append(int(p[j])); j+=1
        R[s]=seq
    return R
