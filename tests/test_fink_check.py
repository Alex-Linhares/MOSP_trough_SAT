"""paper1/fink_check.py: Fink (2012) Teorema 1 fails on finkGraph and not on cexGraph."""
from paper1.fink_check import CEX_EDGES, FINK_EDGES, K, failures


def test_cexgraph_does_not_refute_fink_under_any_labelling():
    assert failures(14, CEX_EDGES, K, best_labelling=True) == []


def test_finkgraph_refutes_fink_as_labelled():
    assert ([2, 3], 14, [0, 4], 2) in failures(15, FINK_EDGES, K, best_labelling=False)


def test_finkgraph_is_cexgraph_plus_a_twin():
    sw = {0: 14, 14: 0}
    back = {tuple(sorted((sw.get(a, a), sw.get(b, b)))) for a, b in FINK_EDGES}
    assert back == set(CEX_EDGES) | {(0, 14), (2, 14)}
