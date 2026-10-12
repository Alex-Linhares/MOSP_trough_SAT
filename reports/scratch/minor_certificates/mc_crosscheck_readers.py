"""Cross-check only: the independent readers of mc_graph give the same labelled
graphs as the project's readers (pathwidth_solver/bench/readers.read_any and
customer_inter.customer_graph.build_customer_graph). Run from the repo root."""
import sys
sys.path.insert(0, "."); sys.path.insert(0, "pathwidth_solver/bench"); sys.path.insert(0, "reports/scratch/minor_certificates")
import networkx as nx
from readers import read_any, HERE
from mosp.instance import MOSPInstance
from customer_inter.customer_graph import build_customer_graph
from mc_graph import read_dgf, read_mosp_customer_graph, edges

def nxedges(G):
    G = nx.convert_node_labels_to_integers(G); G.remove_edges_from(nx.selfloop_edges(G))
    return sorted(tuple(sorted(e)) for e in G.edges())
for g in ("myciel6", "myciel7"):
    assert nxedges(read_any(HERE / "coloring" / f"{g}.dgf")) == edges(read_dgf(HERE / "coloring" / f"{g}.dgf")); print(g, "same")
CS = "benchmarks/instances/MOSP_Instances/Chu_Stuckey/"
for f, fmt, i in [(CS + "Random-125-125-2-3.txt", "A", 0), (CS + "Random-125-125-2-1.txt", "A", 0),
                  (CS + "Random-125-125-6-1.txt", "A", 0), ("benchmarks/instances/ChallengeInstances2005/Wilson/sp4.txt", "B", 3)]:
    inst = MOSPInstance.from_benchmark_file(f)[i]
    assert nxedges(build_customer_graph(inst)) == edges(read_mosp_customer_graph(f, fmt, i)); print(f, i, "same")
