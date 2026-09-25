"""Guards on `learning.canonical`, the isomorphism-class study.

The invariants must be exactly that: unchanged by renaming customers and
products, and different when the graph is different. The audit must catch a
class whose optima disagree, because that is the one thing it exists to see.
"""

import numpy as np
import pandas as pd
import pytest

from learning.canonical import (
    HAVE_NAUTY,
    audit_optima,
    canonical_record,
    class_tables,
    matrix_digest,
    mosp_graph_adjacency,
    wl_hash,
)
from mosp.instance import MOSPInstance

# Three customers on a path: 0-1 share product 1, 1-2 share product 2.
PATH = [[1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1]]
# The same instance with the customers renumbered (rows reversed). Reversing
# the products as well would give PATH back, since it is centrally symmetric.
PATH_PERMUTED = [[1, 1, 0, 0],
                 [0, 1, 1, 0],
                 [0, 0, 1, 1]][::-1]
# A triangle as one product of three customers ...
TRIANGLE_ONE_PRODUCT = [[1], [1], [1]]
# ... and the same triangle covered by three pairwise products.
TRIANGLE_THREE_PRODUCTS = [[1, 1, 0],
                           [1, 0, 1],
                           [0, 1, 1]]


def _inst(matrix, name):
    return MOSPInstance.from_matrix(matrix, name=name)


def test_adjacency_is_the_customer_graph():
    adj = mosp_graph_adjacency(_inst(PATH, "path"))
    assert adj == {0: [1], 1: [0, 2], 2: [1]}


def test_wl_hash_invariant_under_permutation_and_sensitive_to_structure():
    a = wl_hash(mosp_graph_adjacency(_inst(PATH, "a")))
    b = wl_hash(mosp_graph_adjacency(_inst(PATH_PERMUTED, "b")))
    tri = wl_hash(mosp_graph_adjacency(_inst(TRIANGLE_ONE_PRODUCT, "t")))
    assert a == b
    assert a != tri


def test_matrix_digest_sees_the_permutation():
    assert matrix_digest(_inst(PATH, "a")) != matrix_digest(_inst(PATH_PERMUTED, "b"))
    assert matrix_digest(_inst(PATH, "a")) == matrix_digest(_inst(PATH, "c"))


@pytest.mark.skipif(not HAVE_NAUTY, reason="pynauty not installed")
def test_nauty_levels_separate_matrix_from_graph():
    ra = canonical_record(_inst(PATH, "a"))
    rb = canonical_record(_inst(PATH_PERMUTED, "b"))
    assert ra["graph_cert"] == rb["graph_cert"]
    assert ra["bipartite_cert"] == rb["bipartite_cert"]
    assert ra["aut_order"] == 2.0  # the path on three vertices has one flip

    one = canonical_record(_inst(TRIANGLE_ONE_PRODUCT, "one"))
    three = canonical_record(_inst(TRIANGLE_THREE_PRODUCTS, "three"))
    # Same MOSP graph (K3), different clique cover: level 3 agrees, level 2 not.
    assert one["graph_cert"] == three["graph_cert"]
    assert one["bipartite_cert"] != three["bipartite_cert"]
    assert one["aut_order"] == 6.0
    assert one["graph_cert"] != ra["graph_cert"]


@pytest.mark.skipif(not HAVE_NAUTY, reason="pynauty not installed")
def test_bipartite_certificate_never_maps_customers_to_products():
    # 2 customers x 3 products versus its transpose, 3 customers x 2 products:
    # as uncoloured bipartite graphs they are the same; as instances they are not.
    m = [[1, 1, 0], [0, 1, 1]]
    a = canonical_record(_inst(m, "a"))
    b = canonical_record(_inst(np.array(m).T.tolist(), "b"))
    assert a["bipartite_cert"] != b["bipartite_cert"]


def _frame():
    rows = []
    for i, (matrix, coll) in enumerate([(PATH, "x"), (PATH_PERMUTED, "y"),
                                        (TRIANGLE_ONE_PRODUCT, "x"),
                                        (TRIANGLE_THREE_PRODUCTS, "x")]):
        rec = canonical_record(_inst(matrix, f"i{i}"))
        rec.update(instance_name=f"i{i}", source_file=f"f{i}", collection=coll,
                   optimum=2 if matrix in (PATH, PATH_PERMUTED) else 3)
        rows.append(rec)
    return pd.DataFrame(rows)


def test_audit_is_silent_when_optima_agree_and_loud_when_they_do_not():
    frame = _frame()
    assert audit_optima(frame, column="wl_hash").empty
    frame.loc[1, "optimum"] = 3  # the permuted path now claims a wrong optimum
    bad = audit_optima(frame, column="wl_hash")
    assert len(bad) == 1
    assert bad.loc[0, "opt_min"] == 2 and bad.loc[0, "opt_max"] == 3
    assert "i0" in bad.loc[0, "members"] and "i1" in bad.loc[0, "members"]


def test_class_tables_count_distinct_classes():
    tables = class_tables(_frame())
    corpus = tables["corpus"].iloc[0]
    assert corpus["instances"] == 4
    assert corpus["classes: identical matrix"] == 4
    assert corpus["classes: WL hash (not complete)"] == 2
    if HAVE_NAUTY:
        assert corpus["classes: isomorphic matrix"] == 3
        assert corpus["classes: isomorphic MOSP graph"] == 2
        residue = tables["graph classes with several matrix classes"].iloc[0]
        assert residue["with >1 matrix class"] == 1
    shared = tables["classes shared across collections"]
    assert shared["instances"].sum() == 2  # the two paths, in collections x and y
