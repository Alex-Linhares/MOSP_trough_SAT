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

## `ForestCover.lean` against item 03's record (`reports/scratch/forest_check/record_check.csv`)

(L2) `pw(G_M) + 1 ≤ (pw(B) + 1) ω` on the rows where both pathwidths are exact; (L4) `pw(G_M) + 1 ≤ ω (tb(n + m) + 1)` on every row with `pw(G_M)` exact (every record row's incidence graph is a forest); `tb` is `treeBoundInv` as Lean defines it, equal to the least `k` with `N ≤ treeBound k` for every `N < 3001` (checked).

| family                  |   rows |   both exact (L2) |   L2 violations |   L2 slack min |   pw exact (L4) |   L4 violations |   L4 slack min |   tb(n+m) max |
|:------------------------|-------:|------------------:|----------------:|---------------:|----------------:|----------------:|---------------:|--------------:|
| caterpillar of cliques  |     24 |                24 |               0 |              2 |              24 |               0 |              4 |             5 |
| clique tree (extension) |     18 |                11 |               0 |             10 |              11 |               0 |             16 |             5 |
| clique tree (grid)      |     29 |                29 |               0 |              2 |              29 |               0 |              4 |             5 |
| forest on record        |   3448 |              3448 |               0 |              1 |            3448 |               0 |              3 |             4 |
| random block tree       |    900 |               898 |               0 |              5 |             898 |               0 |              9 |             5 |
| all                     |   4419 |              4410 |               0 |              1 |            4410 |               0 |              3 |             5 |

## Lean: `lake build` and `#print axioms`

`lake build`: passed in 2 s.

| theorem                                                    | role   | axioms                                | uses_sorry   |
|:-----------------------------------------------------------|:-------|:--------------------------------------|:-------------|
| vertexSeparation_le_bandwidth                              | proved | propext, Classical.choice, Quot.sound | False        |
| pathwidth_le_bandwidth                                     | proved | propext, Classical.choice, Quot.sound | False        |
| pathwidth_le_bandwidthOfLayout                             | proved | propext, Classical.choice, Quot.sound | False        |
| degeneracy_le_orderingDegeneracy                           | proved | propext, Classical.choice, Quot.sound | False        |
| orderingDegeneracy_le_vertexSeparation                     | proved | propext, Classical.choice, Quot.sound | False        |
| degeneracy_le_vertexSeparation                             | proved | propext, Classical.choice, Quot.sound | False        |
| degeneracy_le_pathwidth                                    | proved | propext, Classical.choice, Quot.sound | False        |
| degeneracy_le_pathwidth_le_bandwidth                       | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.degeneracy_add_one_le_mospValue               | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.mospValue_le_bandwidth_add_one                | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.mospValue_eq_pathwidth_add_one                | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.mospValue_le_pathwidth_add_one                | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.pathwidth_add_one_le_mospValue                | proved | propext, Classical.choice, Quot.sound | False        |
| degeneracy_deleteVertex_le                                 | proved | propext, Classical.choice, Quot.sound | False        |
| exists_layout_maxLaterDegree_le_degeneracy                 | proved | propext, Classical.choice, Quot.sound | False        |
| orderingDegeneracy_le_degeneracy                           | proved | propext, Classical.choice, Quot.sound | False        |
| orderingDegeneracy_eq_degeneracy                           | proved | propext, Classical.choice, Quot.sound | False        |
| pathGraph_isTree                                           | proved | propext, Classical.choice, Quot.sound | False        |
| pathGraph_induce_interval_connected                        | proved | propext, Classical.choice, Quot.sound | False        |
| PathDecomposition.toTreeDecomposition_width                | proved | propext, Classical.choice, Quot.sound | False        |
| treewidth_le_pathwidth                                     | proved | propext, Classical.choice, Quot.sound | False        |
| PathDecomposition.exists_mem_bag_of_connected              | proved | propext, Classical.choice, Quot.sound | False        |
| PathDecomposition.exists_bag_subset_of_le_pathwidth_induce | proved | propext, Classical.choice, Quot.sound | False        |
| branch_lemma                                               | proved | propext, Classical.choice, Quot.sound | False        |
| branch_lemma_treewidth                                     | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.treewidth_add_one_le_mospValue                | proved | propext, Classical.choice, Quot.sound | False        |
| pathwidth_bot_fin4                                         | proved | propext, Classical.choice, Quot.sound | False        |
| old_branch_statement_false                                 | proved | propext, Classical.choice, Quot.sound | False        |
| PathDecomposition.middle_bag_false_linked                  | proved | propext, Classical.choice, Quot.sound | False        |
| branch_lemma_linked                                        | proved | propext, Classical.choice, Quot.sound | False        |
| branch_lemma_separator                                     | proved | propext, Classical.choice, Quot.sound | False        |
| branch_lemma_separator_treewidth                           | proved | propext, Classical.choice, Quot.sound | False        |
| induce_singleton_connected                                 | proved | propext, Classical.choice, Quot.sound | False        |
| branch_lemma_of_separator                                  | proved | propext, Classical.choice, Quot.sound | False        |
| conjecture_sqrt_tw_f6                                      | proved | propext, Classical.choice, Quot.sound | False        |
| PathDecomposition.mem_bag_of_meet                          | proved | propext, Classical.choice, Quot.sound | False        |
| isEmptyPair_anti                                           | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.incidence                                     | proved | propext                               | False        |
| MOSPInstance.one_le_maxPatternSize_iff                     | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.blowUp                                        | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.blowUp_width_add_one_le                       | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.pathwidth_mospGraph_add_one_le                | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.mospValue_le_maxPatternSize_mul               | proved | propext, Classical.choice, Quot.sound | False        |
| le_treeBound_treeBoundInv                                  | proved | propext, Classical.choice, Quot.sound | False        |
| treeBound_lt_of_lt_treeBoundInv                            | proved | propext, Classical.choice, Quot.sound | False        |
| pathwidth_le_treeBoundInv_of_isAcyclic                     | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.mospValue_le_of_incidence_isAcyclic           | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.mospGraph_mono                                | proved | propext, Classical.choice, Quot.sound | False        |
| MOSPInstance.mospValue_mono                                | proved | propext, Classical.choice, Quot.sound | False        |
| coverGraph_mono                                            | proved | propext, Classical.choice, Quot.sound | False        |
| isEmptyPair_coverGraph_of_subset                           | proved | propext, Classical.choice, Quot.sound | False        |
| pathwidth_coverGraph_mono                                  | proved | propext, Classical.choice, Quot.sound | False        |
| layerDecomposition                                         | proved | propext, Classical.choice, Quot.sound | False        |
| pathwidth_le_layerWidth                                    | proved | propext, Classical.choice, Quot.sound | False        |
| vertexSeparation_le_layerWidth                             | proved | propext, Classical.choice, Quot.sound | False        |
| isLayering_dist                                            | proved | propext, Classical.choice, Quot.sound | False        |
| pathwidth_le_layerWidth_dist                               | proved | propext, Classical.choice, Quot.sound | False        |

Verdict: every proved theorem is free of `sorryAx`, every stated one carries it.
