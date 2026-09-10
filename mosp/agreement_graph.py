"""Build the MOSP agreement graph from a MOSP instance.

The MOSP graph (also called the agreement graph or intersection graph):
  - Nodes = patterns (products), indexed 0..m-1
  - Edge between patterns i and j iff they share at least one common customer
    (i.e., there exists a customer k such that M[k][i] = 1 and M[k][j] = 1)

This is equivalent to the intersection graph of the column supports of M.

Key theorem: optimal MOSP value = pathwidth(G) + 1
             where G is this agreement graph.
"""

from __future__ import annotations

import networkx as nx
import numpy as np

from mosp.instance import MOSPInstance


def build_agreement_graph(instance: MOSPInstance) -> nx.Graph:
    """Build the MOSP agreement graph from a MOSP instance.

    Args:
        instance: A MOSPInstance with binary matrix M[customers x patterns].

    Returns:
        A NetworkX Graph where nodes are pattern indices and edges connect
        patterns that share at least one customer.
    """
    G = nx.Graph()
    m = instance.n_patterns
    G.add_nodes_from(range(m))

    # Compute M^T @ M: entry (i,j) counts the number of shared customers
    # between patterns i and j. An edge exists iff this count > 0 and i != j.
    overlap = instance.matrix.T @ instance.matrix

    for i in range(m):
        for j in range(i + 1, m):
            if overlap[i, j] > 0:
                G.add_edge(i, j)

    return G
