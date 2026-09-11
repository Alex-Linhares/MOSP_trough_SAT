"""Build the customer intersection graph from a MOSP instance.

The customer intersection graph:
  - Nodes = customers (orders), indexed 0..n-1
  - Edge between customers i and j iff they share at least one common pattern
    (i.e., there exists a pattern k such that M[i][k] = 1 and M[j][k] = 1)

This is equivalent to the intersection graph of the row supports of M.

Key theorem: optimal MOSP value = pathwidth(customer_graph) + 1
"""

from __future__ import annotations

import networkx as nx
import numpy as np

from mosp.instance import MOSPInstance


def build_customer_graph(instance: MOSPInstance) -> nx.Graph:
    """Build the customer intersection graph from a MOSP instance.

    Args:
        instance: A MOSPInstance with binary matrix M[customers x patterns].

    Returns:
        A NetworkX Graph where nodes are customer indices and edges connect
        customers that share at least one pattern.
    """
    G = nx.Graph()
    n = instance.n_customers
    G.add_nodes_from(range(n))

    # Compute M @ M^T: entry (i,j) counts the number of shared patterns
    # between customers i and j. An edge exists iff this count > 0 and i != j.
    overlap = instance.matrix @ instance.matrix.T

    for i in range(n):
        for j in range(i + 1, n):
            if overlap[i, j] > 0:
                G.add_edge(i, j)

    return G
