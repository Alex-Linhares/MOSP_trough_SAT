# The sandwich in Lean: tables

Regenerate: `python -m learning.sandwich`. Every table below is written by that command; `reports/ml_nature.md` §26 quotes them.

## Lean: `lake build` and `#print axioms`

`lake build`: passed in 4 s.

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
| PathDecomposition.middle_bag_false_linked                  | proved         | propext, Classical.choice, Quot.sound          | False        |
| branch_lemma_linked                                        | proved         | propext, Classical.choice, Quot.sound          | False        |
| branch_lemma_separator                                     | proved         | propext, Classical.choice, Quot.sound          | False        |
| branch_lemma_separator_treewidth                           | proved         | propext, Classical.choice, Quot.sound          | False        |
| induce_singleton_connected                                 | proved         | propext, Classical.choice, Quot.sound          | False        |
| branch_lemma_of_separator                                  | proved         | propext, Classical.choice, Quot.sound          | False        |
| conjecture_sqrt_tw_f6                                      | stated (sorry) | propext, sorryAx, Classical.choice, Quot.sound | True         |

Verdict: every proved theorem is free of `sorryAx`, every stated one carries it.
