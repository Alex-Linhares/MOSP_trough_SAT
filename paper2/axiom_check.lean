/-
Axiom check for section 3 (`paper2/equivalences.md`): every Lean theorem the
master table, the chain figure and the gap inventory name, printed with the
axioms it depends on. Expected: `[propext, Classical.choice, Quot.sound]` on
every line except the last, a control that must show `sorryAx`.

    cd lean && lake env lean ../paper2/axiom_check.lean

Not under `lean/MOSPFormalization/`, so `lake build` does not see it.
-/
import MOSPFormalization

open MOSPFormalization MOSPFormalization.Complex

#print axioms cutwidth_unbounded
#print axioms edgeSearch_le_vertexSeparation_add_two
#print axioms intervalSearch_chain
#print axioms intervalThickness_eq_pathwidth_add_one
#print axioms isPositiveVSG_triangleGraph_counterexample
#print axioms kirousisPapadimitriou_claim2_false
#print axioms LogicArray.tracks_eq_intervalThickness
#print axioms LogicArray.tracks_eq_pathwidth_add_one
#print axioms modCutwidth_unbounded
#print axioms monotoneNodeSearch_eq_intervalThickness
#print axioms monotoneNodeSearch_eq_vertexSeparation_add_one
#print axioms monotoneNodeSearch_ne_vertexSeparation_add_one_of_edgeless
#print axioms MOSPInstance.mospValue_eq_pathwidth_add_one
#print axioms narrowness_eq_pathwidth_add_one
#print axioms NetGateMatrix.foldTracks_eq_pathwidth_add_one
#print axioms NetGateMatrix.foldTracks_eq_tracks
#print axioms NetGateMatrix.tracks_eq_mospValue
#print axioms NetGateMatrix.tracks_eq_nodeSearch_of_monotonicity
#print axioms NetGateMatrix.tracks_eq_pathwidth_add_one
#print axioms nodeSearch_eq_intervalThickness_of_monotonicity
#print axioms nodeSearch_eq_vertexSeparation_add_one_of_monotonicity
#print axioms nodeSearch_le_vertexSeparation_add_one
#print axioms nodeSearch_ne_intervalThickness_of_edgeless
#print axioms pathwidth_le_splitBandwidth_le_pathwidth_add_one
#print axioms plaTracks_idMatrix_five
#print axioms plaTracks_idMatrix_unbounded
#print axioms plaTracks_pathMatrix_unbounded
#print axioms tracks_ne_monotoneNodeSearch_one
#print axioms vertexSeparation_eq_pathwidth
#print axioms vertexSeparation_le_edgeSearch_of_monotonicity
#print axioms vertexSeparation_le_progressiveEdgeSearch_le_add_two
#print axioms vertexSeparation_triangleGraph
#print axioms vsg_eq_max
-- item 14: the full games
#print axioms nodeSearchMonotonicity
#print axioms nodeSearch_eq_vertexSeparation_add_one
#print axioms nodeSearch_eq_pathwidth_add_one
#print axioms nodeSearch_eq_intervalThickness
#print axioms nodeSearch_chain
#print axioms NetGateMatrix.tracks_eq_nodeSearch
#print axioms exists_monotone_chain
#print axioms vertexSeparation_le_edgeSearch_le_add_two
#print axioms pathwidth_le_edgeSearch_le_add_two
#print axioms nodeSearch_sub_one_le_edgeSearch_le_add_one
#print axioms edgeSearch_le_progressiveEdgeSearch_le_add_two

-- loop0006 item 03: Lengauer (1981) Theorem 3
#print axioms pebblesWithin_lengauerD_iff
#print axioms isPositiveVSG_iff_isPositivePBWP_lengauerD
#print axioms pbw_lengauerD_eq_pathwidth
#print axioms pbw_lengauerD_of_edgeless

-- loop0006 item 04: Lengauer (1981) Theorem 2, Kirousis & Papadimitriou (1986) Theorem 3.1
#print axioms pebblesWithin_iff_lengauerU
#print axioms isPositivePBWP_iff_isPositiveVSG_lengauerU
#print axioms isPositivePBWP_one_not_isPositiveVSG_zero
#print axioms pbw_eq_pathwidth_lengauerU_add_one
#print axioms pbw_eq_vsg_lengauerU_add_one
#print axioms pbw_eq_mospValue_pebbleMatrix
#print axioms mpb_eq_mpbw
#print axioms mpb_eq_pathwidth_add_one
#print axioms mpbw_eq_pathwidth_add_one
#print axioms mpb_eq_nodeSearch
#print axioms mpb_ne_nodeSearch_of_edgeless

-- loop0006 item 07: the customer search model (Search/Basic.lean)
#print axioms MOSPFormalization.Search.solvable_mono
#print axioms MOSPFormalization.Search.solvable_insert_of_free
#print axioms MOSPFormalization.Search.solvable_insert_iff_of_free
#print axioms MOSPFormalization.Search.solvable_iff_searchSol_cl
#print axioms MOSPFormalization.Search.orderCost_ofFn_eq_outNarrowness
#print axioms MOSPFormalization.Search.orderCost_ofFn_eq_vertexSepOfLayout_add_one
#print axioms MOSPFormalization.Search.searchSol_empty_iff_pathwidth_add_one_le
#print axioms MOSPFormalization.Search.searchSol_mospGraph_iff_mospValue_le
#print axioms MOSPFormalization.Search.openStacks_submodular
#print axioms MOSPFormalization.Search.isDefinite_iff
#print axioms MOSPFormalization.Search.solvable_cl_insert_of_hereditarilyDefinite
#print axioms MOSPFormalization.Search.searchSol_cl_insert_of_hereditarilyDefinite
#print axioms MOSPFormalization.Search.isHereditarilyDefinite_of_openCount_le_one
#print axioms MOSPFormalization.Search.isHereditarilyDefinite_of_matching
#print axioms MOSPFormalization.Search.not_solvable_of_invariant
#print axioms MOSPFormalization.Search.definiteMove_counterexample
#print axioms MOSPFormalization.Search.not_isHereditarilyDefinite_cex

-- loop0006 item 09: the subset rule (Search/SubsetRule.lean)
#print axioms MOSPFormalization.Search.searchSol_cl_insert_of_newlyOpened_subset
#print axioms MOSPFormalization.Search.cl_insert_cl_insert_of_newlyOpened_subset
#print axioms MOSPFormalization.Search.Dominates.trans
#print axioms MOSPFormalization.Search.exists_undominated
#print axioms MOSPFormalization.Search.subsetKept_nonempty
#print axioms MOSPFormalization.Search.subsetFilter_sound
#print axioms MOSPFormalization.Search.definiteThenSubset_sound
#print axioms MOSPFormalization.Search.repairedFilter_sound
#print axioms MOSPFormalization.Search.codeFilter_counterexample
#print axioms MOSPFormalization.Search.noTieBreak_counterexample

-- loop0006 item 10: the better move (Search/BetterMove.lean)
#print axioms MOSPFormalization.Search.isBetter_iff
#print axioms MOSPFormalization.Search.IsRepairedBetter.isBetter
#print axioms MOSPFormalization.Search.isRepairedBetter_of_openCount_le_one
#print axioms MOSPFormalization.Search.solvable_cl_insert_of_repairedBetter
#print axioms MOSPFormalization.Search.searchSol_cl_insert_of_repairedBetter
#print axioms MOSPFormalization.Search.betterFilterBy_sound
#print axioms MOSPFormalization.Search.fullFilter_sound
#print axioms MOSPFormalization.Search.repairedFullFilter_sound
#print axioms MOSPFormalization.Search.betterMove_counterexample
#print axioms MOSPFormalization.Search.betterMove_counterexample_node
#print axioms MOSPFormalization.Search.bugA_counterexample
#print axioms MOSPFormalization.Search.bugB_counterexample

-- loop0006 item 11: the memo and the old move (Search/Memo.lean)
#print axioms MOSPFormalization.Search.cl_insert_cl_insert_comm
#print axioms MOSPFormalization.Search.searchSol_reinsert
#print axioms MOSPFormalization.Search.searchSol_reinsert_path
#print axioms MOSPFormalization.Search.not_searchSol_of_oldMove
#print axioms MOSPFormalization.Search.solvable_iff_of_cl_eq
#print axioms MOSPFormalization.Search.Exec.sound
#print axioms MOSPFormalization.Search.exec_root_sound
#print axioms MOSPFormalization.Search.exec_fake_oldMove
#print axioms MOSPFormalization.Search.reinsert_needs_test
#print axioms MOSPFormalization.Search.exec_repairedFullFilter_sound

-- loop0006 item 12: the search assembled (Search/Decide.lean)
#print axioms MOSPFormalization.Search.filterSound_iff
#print axioms MOSPFormalization.Search.Exec.execOn
#print axioms MOSPFormalization.Search.ExecOn.exec
#print axioms MOSPFormalization.Search.ExecOn.mono
#print axioms MOSPFormalization.Search.ExecOn.of_nodeSound
#print axioms MOSPFormalization.Search.ExecOn.sound
#print axioms MOSPFormalization.Search.execOn_root_sound
#print axioms MOSPFormalization.Search.nodeSoundAt_of_covering
#print axioms MOSPFormalization.Search.definite_link
#print axioms MOSPFormalization.Search.exec_repairedFullFilter_narrowness
#print axioms MOSPFormalization.Search.exec_repairedFullFilter_pathwidth
#print axioms MOSPFormalization.Search.exec_repairedFullFilter_mospValue
#print axioms MOSPFormalization.Search.exec_repairedFullFilter_mospGraph_pathwidth
#print axioms MOSPFormalization.Search.codeFullFilter_playable
#print axioms MOSPFormalization.Search.nodeSoundAt_codeFullFilter_of_repaired
#print axioms MOSPFormalization.Search.codeExec_sound_of_runSound
#print axioms MOSPFormalization.Search.codeExec_sound_of_codeFilterSound
#print axioms MOSPFormalization.Search.codeExec_sound_of_repaired
#print axioms MOSPFormalization.Search.codeExec_pathwidth_of_runSound
#print axioms MOSPFormalization.Search.codeExec_mospValue_of_runSound
#print axioms MOSPFormalization.Search.codeExec_mospValue_of_repaired
#print axioms MOSPFormalization.Search.codeFullFilter_cex
#print axioms MOSPFormalization.Search.not_codeFilterSound_cexGraph

#print axioms MOSPFormalization.Search.card_opened_union_eq
#print axioms MOSPFormalization.Search.hall_of_isHereditarilyDefinite
#print axioms MOSPFormalization.Search.exists_matching_of_isHereditarilyDefinite
#print axioms MOSPFormalization.Search.isHereditarilyDefinite_iff_hasDefiniteMatching

-- The published Theorems 1 and 2, refuted as stated (Search/PublishedTheorems.lean)
#print axioms MOSPFormalization.Search.chuStuckey_theorem1_false
#print axioms MOSPFormalization.Search.chuStuckey_theorem1_false_literal
#print axioms MOSPFormalization.Search.chuStuckey_theorem2_false
#print axioms MOSPFormalization.Search.chuStuckey_theorem2_false_literal

-- loop0008 item 02: Chu (2011) thesis Theorems 6.3.6 and 6.3.8, refuted as stated (Search/ChuThesis.lean)
#print axioms MOSPFormalization.Search.chuThesis_theorem636_false
#print axioms MOSPFormalization.Search.chuThesis_theorem636_false_literal
#print axioms MOSPFormalization.Search.chuThesis_theorem638_false
#print axioms MOSPFormalization.Search.chuThesis_theorem638_false_literal
#print axioms MOSPFormalization.Search.chuThesis_theorem638_literal_witness
#print axioms MOSPFormalization.Search.fink_theorem1_false

-- loop0008 item 03: the search in pathwidth language; Tamaki's commitment lemma (Search/Layout.lean)
#print axioms MOSPFormalization.Search.opened_sdiff_eq_boundary
#print axioms MOSPFormalization.Search.openStacks_eq_card_boundary
#print axioms MOSPFormalization.Search.stepCost_eq_card_boundary_add_one
#print axioms MOSPFormalization.Search.mem_cl_iff
#print axioms MOSPFormalization.Search.solvable_of_isCommittable
#print axioms MOSPFormalization.Search.isHereditarilyDefinite_iff_isCommittable
#print axioms MOSPFormalization.Search.solvable_cl_insert_of_hereditarilyDefinite'
#print axioms MOSPFormalization.Search.isDefinite_iff_endpoint
#print axioms MOSPFormalization.Search.isCommittable_insert_iff
#print axioms MOSPFormalization.Search.isGreedyStep_iff
#print axioms MOSPFormalization.Search.cex_isDefinite_not_isCommittable
#print axioms MOSPFormalization.Search.exists_isCommittable_of_isDefinite
#print axioms MOSPFormalization.Search.cex_isCommittable_234

-- loop0008 item 09: the root split (Search/Split.lean), and every remaining theorem the
-- LaTeX draft (paper2/latex/) cites; the draft's definitions need no axiom line
#print axioms MOSPFormalization.Search.Exec.union_memo
#print axioms MOSPFormalization.Search.ExecSplit.exec
#print axioms MOSPFormalization.Search.ExecSplit.exec_root
#print axioms MOSPFormalization.Search.execSplit_repairedFullFilter_sound
#print axioms MOSPFormalization.Search.execSplit_repairedFullFilter_mospValue
#print axioms MOSPFormalization.PathDecomposition.exists_bag_of_isClique
#print axioms MOSPFormalization.star_mospValue
#print axioms MOSPFormalization.star_pathwidth_agreementGraph
#print axioms MOSPFormalization.star_refutes_pattern_graph_bound
#print axioms MOSPFormalization.Search.cexFamily_closed
#print axioms MOSPFormalization.Search.closeCount_eq
#print axioms MOSPFormalization.MOSPInstance.encodes_iff_mospValue_le

-- paper3/wavefront.md: maximum wavefront (Kumfert & Pothen 1997) = pathwidth + 1 (Complex/Wavefront.lean)
#print axioms MOSPFormalization.Complex.wavefront_eq_insert_activeSuffix
#print axioms MOSPFormalization.Complex.card_wavefront
#print axioms MOSPFormalization.Complex.maxWavefront_eq_vertexSepOfLayout_add_one
#print axioms MOSPFormalization.Complex.minMaxWavefront_eq_vertexSeparation_add_one
#print axioms MOSPFormalization.Complex.minMaxWavefront_eq_pathwidth_add_one
#print axioms MOSPFormalization.Complex.minMaxWavefront_of_isEmpty
#print axioms MOSPFormalization.Complex.wavefront_eq_outShackBeforeMove
#print axioms MOSPFormalization.Complex.wavefront_eq_shackAfterPut_reverse
#print axioms MOSPFormalization.Complex.minMaxWavefront_eq_narrowness

-- control: the baseline sorry, expected to show sorryAx
#print axioms conjecture_sqrt_tw_f6
