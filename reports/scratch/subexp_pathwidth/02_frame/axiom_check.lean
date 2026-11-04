/-
Axiom audit of loop0014 item 02 (`lean/MOSPFormalization/SubexpPathwidth/Frame.lean`):
every theorem of the frame, printed with the axioms it depends on. Expected:
`[propext, Classical.choice, Quot.sound]` or fewer on every line; the two `Prop`s are
`def`s and print no axioms of their own (they are printed to show they elaborate).

    cd lean && lake env lean ../reports/scratch/subexp_pathwidth/02_frame/axiom_check.lean
-/
import MOSPFormalization

open MOSPFormalization.SubexpPathwidth

#print axioms SubexpCount
#print axioms ExactCountAndSat
#print axioms PathwidthSubexpOn
#print axioms PathwidthSubexp
#print axioms SubexpCount.anti
#print axioms ExactCountAndSat.subexpCount
#print axioms runtimeBound_eq
#print axioms tendsto_log_sq_div_sqrt
#print axioms runtimeScale_isLittleO
#print axioms isSubexpExponent_runtimeScale
#print axioms LocatedCfg.monitor_config
#print axioms Trace.config_of_locatedStep
#print axioms encodeGraph_length
#print axioms PathwidthSubexpOn.mono
#print axioms pathwidthSubexp_iff
#print axioms decide_pathwidth_le_eq
#print axioms pathwidthSubexpOn_iff_vertexSeparation
