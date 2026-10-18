import subprocess, networkx as nx, sys
from run_helpers import masks, myc
out=subprocess.run(['nauty-geng','-qc','8'],capture_output=True,text=True).stdout.split()
gs=[nx.from_graph6_bytes(s.encode()) for s in out]
inp=[]
for G in gs:
    for H in (G,myc(G)):
        m=masks(H); inp.append(f"{len(m)} "+" ".join(map(str,m)))
res=subprocess.run(['nice','-n','19','./pwonly'],input="\n".join(inp)+"\n",capture_output=True,text=True).stdout.split()
import pickle
rows=[(out[k],int(res[2*k]),int(res[2*k+1]),gs[k].number_of_edges()) for k in range(len(gs))]
pickle.dump(rows,open('rows8.pkl','wb'))
