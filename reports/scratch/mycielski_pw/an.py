import pickle, collections
rows=pickle.load(open('rows.pkl','rb'))
def chk(name,f):
    bad=[r for r in rows if not f(r)]
    print(f"{name}: {len(bad)} violations of {len(rows)}", bad[:5])
chk("pw(mu)<=2pw+2",lambda r:r[5]<=2*r[3]+2)
chk("pw(mu)<=2pw+1",lambda r:r[5]<=2*r[3]+1)
chk("pw(mu)<=2pw (edge)",lambda r:r[2]==0 or r[5]<=2*r[3])
chk("pw(mu)>=pw+1",lambda r:r[5]>=r[3]+1)
chk("pw(mu)>=pw+2 (edge)",lambda r:r[2]==0 or r[5]>=r[3]+2)
chk("tw(mu)<=2tw+2",lambda r:r[6]<=2*r[4]+2)
chk("tw(mu)<=2tw+1",lambda r:r[6]<=2*r[4]+1)
chk("tw(mu)>=tw+1",lambda r:r[6]>=r[4]+1)
chk("pw(mu)<=n", lambda r:r[5]<=r[1])
chk("pw(mu)<=pw+n?", lambda r:r[5]<=r[3]+r[1])
# distribution of pw(mu)-pw by pw, edges>0
d=collections.Counter((r[3],r[5]) for r in rows); print(sorted(d.items()))
d=collections.Counter((r[4],r[6]) for r in rows); print("tw",sorted(d.items()))
# connected only
import networkx as nx
con=[r for r in rows if nx.is_connected(nx.from_graph6_bytes(r[0].encode()))]
print("connected",len(con),sorted(collections.Counter((r[1],r[3],r[5]) for r in con).items()))
