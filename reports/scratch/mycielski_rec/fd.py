import pandas as pd, itertools, sys
def load(fn):
    d=pd.read_csv(fn)
    P=d.pivot_table(index='seed',columns='j',values='pw')
    b=d[d.j==0].set_index('seed').copy(); b['p1']=P[1]
    return b
def fd_search(b,feats,target='p1',maxk=3,top=15):
    out=[]
    for k in range(1,maxk+1):
        for S in itertools.combinations(feats,k):
            g=b.groupby(list(S))[target].nunique()
            bad=(g>1).sum(); cells=len(g)
            # rows in conflicting cells
            out.append((bad,cells,S))
    out.sort()
    return out[:top]
if __name__=='__main__':
    b=load(sys.argv[1])
    feats=['pw','tw','tight','lastmin','firstmin','nlast_opt','n','m','maxdeg','mindeg','degen','alpha','omega','ncomp','niso']
    for r in fd_search(b,feats): print(r)
