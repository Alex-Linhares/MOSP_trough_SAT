/-
Axiom audit for paper 3 (Section 8, "The statement in our Lean"): every declaration the
paper cites from our companion Lean, printed with the axioms it depends on. The two files are
`lean/MOSPFormalization/SubexpPathwidth/PrimitiveMachine.lean` (the verbatim copy of the
comparator's machine model, definitions only) and `lean/MOSPFormalization/SubexpPathwidth/
Frame.lean` (the restatement `SubexpCount` and the lemmas about it). The owner's decision of
2026-11-05 (`paper3/ETH_AMBIGUOUS.MD`, S3 resolved) keeps the files where loop0014 wrote them.

Expected: `[propext, Classical.choice, Quot.sound]` on every line that names a theorem, and
nothing beyond those three on any line; `sorryAx` on none. The `def`s (`SubexpCount`,
`ExactCountAndSat`, `IsSubexpExponent`, and the copied `runtimeScale`, `runtimeBound`) are
printed to show that they elaborate against the built library; a `def` of a `Prop` is not a
claim, and none of them is proved here. Unlike `paper1/axiom_check.lean` there is no control
line that must show `sorryAx`: the acceptance rule of this paper is that every line is on the
three standard axioms, and the committed log is `paper3/lean/axiom_check.log`.

    cd lean && lake env lean ../paper3/lean/axiom_check.lean > ../paper3/lean/axiom_check.log

Not under `lean/MOSPFormalization/`, so `lake build` does not see it. Nothing of the OpenAI
collection is imported: `MOSPFormalization` is our library, and the `OAI.…` names below are
the copied definitions inside it.
-/
import MOSPFormalization

open MOSPFormalization.SubexpPathwidth

-- The copied definitions the statement rests on (PrimitiveMachine.lean, the verbatim copy).
#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLog.Statement.runtimeScale
#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLog.Statement.runtimeBound
#print axioms OAI.Algorithms.SubexponentialSAT.SAT.count
#print axioms OAI.Algorithms.SubexponentialSAT.Encoding.encodeCNF
#print axioms OAI.Algorithms.SubexponentialSAT.Encoding.formulaBitLength
#print axioms OAI.Algorithms.SubexponentialSAT.Computation.PrimitiveMachine.step
#print axioms OAI.Algorithms.SubexponentialSAT.Computation.Trace
#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.countWord
#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.locatedStep
#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.visitedSpace

-- The restatement (Frame.lean): two `Prop`s, never proved, never axioms.
#print axioms SubexpCount
#print axioms ExactCountAndSat

-- What is proved about them (Frame.lean).
#print axioms SubexpCount.anti
#print axioms ExactCountAndSat.subexpCount
#print axioms IsSubexpExponent
#print axioms runtimeBound_eq
#print axioms tendsto_log_sq_div_sqrt
#print axioms runtimeScale_isLittleO
#print axioms isSubexpExponent_runtimeScale
#print axioms LocatedCfg.monitor_config
#print axioms Trace.config_of_locatedStep
