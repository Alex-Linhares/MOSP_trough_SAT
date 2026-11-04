# loop0014 item 02 — the formal frame (2026-11-04)

Lean item: `lean/MOSPFormalization/SubexpPathwidth/PrimitiveMachine.lean`
(verbatim copy of OpenAI's machine model and CNF encoding, Apache-2.0) and
`lean/MOSPFormalization/SubexpPathwidth/Frame.lean` (ours). The report
section is `reports/subexp_pathwidth.md` §2. No reduction or encoding of
pathwidth is stated in this item, so TASK.md's brute-force check to 7
vertices has nothing to check; the two checks that apply are below.

- `axiom_check.lean`, `axiom_check.log` — `#print axioms` of every
  declaration of `Frame.lean`: all on `[propext, Classical.choice, Quot.sound]`.
- `body_diff.log` — the body of `SubexpCount` diffed line by line against
  lines 195–217 of the comparator theorem `exact_count_and_sat`
  (leading whitespace and the theorem's trailing `:= by` normalised):
  identical, 23 lines.
- The verbatim copy itself was verified byte for byte when it was made
  (`diff` of comparator lines 1–190 and 220 against the copy after its
  header: empty); regenerate as below.

Regenerate:

    cd ~/dev/MOSP
    F=~/dev/untrusted/openai-math/lean/ComparatorChallenges/SubexponentialSAT.lean
    sha256sum $F                      # 4183b205…76685
    diff <(sed -n 1,190p $F; sed -n 220p $F) \
         <(sed -n '/^Everything after this comment block is the copy/,$p' lean/MOSPFormalization/SubexpPathwidth/PrimitiveMachine.lean | tail -n +3)
    diff <(sed -n 195,217p $F | sed 's/^ *//; s/ := by$//') \
         <(sed -n '/^def SubexpCount/,/^def ExactCountAndSat/p' lean/MOSPFormalization/SubexpPathwidth/Frame.lean | sed -n '2,24p' | sed 's/^ *//')
    (cd lean && lake build && lake env lean ../reports/scratch/subexp_pathwidth/02_frame/axiom_check.lean)
    python3 Ralph_Loops/loop0014/gate.py
