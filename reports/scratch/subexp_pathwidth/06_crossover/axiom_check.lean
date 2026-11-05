/-
Axiom audit of loop0014 item 06 (`lean/MOSPFormalization/SubexpPathwidth/Crossover.lean`):
every declaration, printed with the axioms it depends on. Expected:
`[propext, Classical.choice, Quot.sound]` or fewer on every line.

    cd lean && lake env lean ../reports/scratch/subexp_pathwidth/06_crossover/axiom_check.lean
-/
import MOSPFormalization

open MOSPFormalization.SubexpPathwidth

#print axioms edgeClause
#print axioms indepCNF
#print axioms indepCount
#print axioms edgeClause_card_le
#print axioms indepCNF_width
#print axioms edgeClause_eval
#print axioms indepCNF_eval_iff
#print axioms count_indepCNF
#print axioms indepCount_subexp
#print axioms crossoverThreshold
#print axioms rpow_le_of_crossover
#print axioms crossoverThreshold_eventually_lt
#print axioms counting_beats_dp_eventually
#print axioms colVar
#print axioms aloClause
#print axioms coloringCNF
#print axioms coloringCNF_width
#print axioms coloringCNF_eval_iff
#print axioms modelColoring
#print axioms coloringCount
#print axioms count_coloringCNF
#print axioms runtimeScale_mul_isLittleO
#print axioms isSubexpExponent_runtimeScale_mul
#print axioms coloringCount_subexp
