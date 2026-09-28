# The sandwich in Lean: tables

Regenerate: `python -m learning.sandwich`. Every table below is written by that command; `reports/ml_nature.md` §26 quotes them.

## Brute force over every labelled graph on 1–5 vertices

1099 graphs in 1.0 s. Each column counts graphs where the statement holds.

|   n |   graphs |   degeneracy = core_number |   degeneracy = ordering_degeneracy |   vertex_separation = pathwidth_solver |   degeneracy ≤ pw |   pw ≤ bandwidth |   degeneracy = pw |   pw = bandwidth |   both tight |
|----:|---------:|---------------------------:|-----------------------------------:|---------------------------------------:|------------------:|-----------------:|------------------:|-----------------:|-------------:|
|   1 |        1 |                          1 |                                  1 |                                      1 |                 1 |                1 |                 1 |                1 |            1 |
|   2 |        2 |                          2 |                                  2 |                                      2 |                 2 |                2 |                 2 |                2 |            2 |
|   3 |        8 |                          8 |                                  8 |                                      8 |                 8 |                8 |                 8 |                8 |            8 |
|   4 |       64 |                         64 |                                 64 |                                     64 |                64 |               64 |                64 |               60 |           60 |
|   5 |     1024 |                       1024 |                               1024 |                                   1024 |              1024 |             1024 |               994 |              919 |          889 |

## The corpus (`learning/data/instances.csv`)

`g_degeneracy` is networkx's core number (the Lick–White form formalised as `degeneracy`); `bw_rcm` is the bandwidth of the reverse Cuthill–McKee layout (`bandwidthOfLayout`, one layout, so `pathwidth_le_bandwidthOfLayout` is the theorem it checks).

| band   |   instances |   degeneracy+1 ≤ optimum |   optimum ≤ bw_rcm+1 |   lower tight |   upper tight |   ends coincide |
|:-------|------------:|-------------------------:|---------------------:|--------------:|--------------:|----------------:|
| ≤10    |        1614 |                     1614 |                 1614 |          1340 |          1292 |            1143 |
| 11–20  |        2508 |                     2508 |                 2508 |          1278 |          1314 |            1115 |
| 21–30  |        1816 |                     1816 |                 1816 |           585 |           614 |             511 |
| 31–40  |         197 |                      197 |                  197 |            61 |            55 |              51 |
| 41–75  |         151 |                      151 |                  151 |            21 |             2 |               1 |
| 76–134 |          90 |                       90 |                   90 |             8 |             2 |               2 |
| all    |        6376 |                     6376 |                 6376 |          3293 |          3279 |            2823 |

## Lean: `lake build` and `#print axioms`

`lake build`: passed in 2 s.

| theorem                                                    | role           | axioms                                         | uses_sorry   |
|:-----------------------------------------------------------|:---------------|:-----------------------------------------------|:-------------|
| vertexSeparation_le_bandwidth                              | proved         | propext, Classical.choice, Quot.sound          | False        |
| pathwidth_le_bandwidth                                     | proved         | propext, Classical.choice, Quot.sound          | False        |
| pathwidth_le_bandwidthOfLayout                             | proved         | propext, Classical.choice, Quot.sound          | False        |
| degeneracy_le_orderingDegeneracy                           | proved         | propext, Classical.choice, Quot.sound          | False        |
| orderingDegeneracy_le_vertexSeparation                     | proved         | propext, Classical.choice, Quot.sound          | False        |
| degeneracy_le_vertexSeparation                             | proved         | propext, Classical.choice, Quot.sound          | False        |
| degeneracy_le_pathwidth                                    | proved         | propext, Classical.choice, Quot.sound          | False        |
| degeneracy_le_pathwidth_le_bandwidth                       | proved         | propext, Classical.choice, Quot.sound          | False        |
| MOSPInstance.degeneracy_add_one_le_mospValue               | proved         | propext, Classical.choice, Quot.sound          | False        |
| MOSPInstance.mospValue_le_bandwidth_add_one                | proved         | propext, Classical.choice, Quot.sound          | False        |
| MOSPInstance.mospValue_eq_pathwidth_add_one                | proved         | propext, Classical.choice, Quot.sound          | False        |
| MOSPInstance.mospValue_le_pathwidth_add_one                | proved         | propext, Classical.choice, Quot.sound          | False        |
| MOSPInstance.pathwidth_add_one_le_mospValue                | proved         | propext, Classical.choice, Quot.sound          | False        |
| degeneracy_deleteVertex_le                                 | proved         | propext, Classical.choice, Quot.sound          | False        |
| exists_layout_maxLaterDegree_le_degeneracy                 | proved         | propext, Classical.choice, Quot.sound          | False        |
| orderingDegeneracy_le_degeneracy                           | proved         | propext, Classical.choice, Quot.sound          | False        |
| orderingDegeneracy_eq_degeneracy                           | proved         | propext, Classical.choice, Quot.sound          | False        |
| pathGraph_isTree                                           | proved         | propext, Classical.choice, Quot.sound          | False        |
| pathGraph_induce_interval_connected                        | proved         | propext, Classical.choice, Quot.sound          | False        |
| PathDecomposition.toTreeDecomposition_width                | proved         | propext, Classical.choice, Quot.sound          | False        |
| treewidth_le_pathwidth                                     | proved         | propext, Classical.choice, Quot.sound          | False        |
| PathDecomposition.exists_mem_bag_of_connected              | proved         | propext, Classical.choice, Quot.sound          | False        |
| PathDecomposition.exists_bag_subset_of_le_pathwidth_induce | proved         | propext, Classical.choice, Quot.sound          | False        |
| branch_lemma                                               | proved         | propext, Classical.choice, Quot.sound          | False        |
| branch_lemma_treewidth                                     | proved         | propext, Classical.choice, Quot.sound          | False        |
| MOSPInstance.treewidth_add_one_le_mospValue                | proved         | propext, Classical.choice, Quot.sound          | False        |
| pathwidth_bot_fin4                                         | proved         | propext, Classical.choice, Quot.sound          | False        |
| old_branch_statement_false                                 | proved         | propext, Classical.choice, Quot.sound          | False        |
| conjecture_sqrt_tw_f6                                      | stated (sorry) | propext, sorryAx, Classical.choice, Quot.sound | True         |

Verdict: every proved theorem is free of `sorryAx`, every stated one carries it.
