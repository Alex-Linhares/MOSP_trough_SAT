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

-- control: the baseline sorry, expected to show sorryAx
#print axioms conjecture_sqrt_tw_f6
