# loop0006 — pebbling, and the soundness of the customer search: items

Phase A: pebbling joins the complex. Phase B: every pruning rule of Chu &
Stuckey's search is proved never to discard the last solution. Then
assembly and a reserve.

- [x] **01 Pebbling census.** Read Lengauer (1981) §1-2 and Kirousis &
  Papadimitriou (1986) §3 and write down, in `paper2/equivalences.md` (a new
  section "Pebbling"): the black-white pebble game and its progressive
  version exactly as each source defines them (quoted, page and number), the
  graphs involved (dags; Lengauer's G_u and G_d, Def. 1; KP's D for a graph),
  the numbers (PBWP, pbw, mpb, mpbw), and the exact relations proved:
  Lengauer Thm 2 (PBWP on G vs VSG on G_u, K − 1) and Thm 3 (VSG on G vs PBWP
  on G_d, K + 2); KP Thm 3.1. Say which relate pebbling to vertex separation
  exactly, on which graph, with which offset, and whether pebbling belongs in
  the complex as an exact member. No Lean.

- [x] **02 Pebbling brute force.** Extend `paper2/complex_check.py` with an
  exhaustive progressive black-white pebbling solver for small dags, from the
  source's definition, and check every relation item 01 wrote on all dags
  (and all G_d, G_u constructions) small enough, reporting agreement or
  counterexamples in `paper2/equivalences.md`. Tests on hand-checked dags.

- [x] **03 Lengauer Theorem 3 in Lean.** `Complex/Pebbling.lean`: define the
  (progressive) black-white pebble game on a finite dag and prove Lengauer's
  Thm 3, VSG on G ↔ PBWP on G_d with K + 2, reusing the VSG of
  `Complex/EdgeSeparation.lean`. Hence the pebbling number of G_d equals
  vs(G) + 2 (with the edge-case hypotheses item 02 found).

- [x] **04 Lengauer Theorem 2 and KP Theorem 3.1.** `Complex/PebblingGu.lean`:
  prove Lengauer's Thm 2 (PBWP on G ↔ VSG on G_u, K − 1), and KP Thm 3.1 as
  item 01 settled it, or the part of it within reach. Then add pebbling to
  `paper2/problem_transformations.md` (problem §1.13, its transformations
  among the equalities or bands, and their proofs in both registers) and the
  master table of `paper2/equivalences.md`.

- [x] **05 The search, stated.** Write `paper2/search_soundness.md` §1-2:
  the customer search as a mathematical object (states = closed sets S;
  opened set O(S) = ∪ N[c]; a move closes c; its cost; the decision question
  "is there a closing order of cost ≤ k from S?"), and each rule as it is
  implemented in the fixed code: the free move, the definite move (Thm 1),
  the subset rule, the better move (Thm 2, corrected close count and the
  "standing candidates only" composition), the old move (Thm 3), and the
  memo. For each: the exact premise, the exact conclusion ("some optimal
  completion from S begins with ..." or "no completion is lost by skipping
  ..."), and the order in which the code applies it. Quote the code lines.
  Say explicitly what composition of rules is being claimed sound. No Lean.

- [x] **06 Brute-force soundness check.** `paper2/search_check.py`:
  implement the rules exactly as item 05 states them and, on every instance
  small enough (every graph to 7 vertices; all k), check for each state that
  every rule's conclusion holds: for the pruned moves, at least one surviving
  move still has a completion of cost ≤ k whenever any move did. Check the
  rules singly and in the code's composition, and check that the two known
  bad forms of `better_move` (`reports/better_move_bug.md` §7) fail. Tests.

- [x] **07 Search model in Lean.** `Search/Basic.lean`: closed sets, the
  opened set, the cost of a closing order, the decision predicate
  `Solvable G k S` ("some ordering of V \ S after S has cost ≤ k"), and the
  lemma connecting it to `vertexSeparation` and `narrowness` (a full closing
  order's cost is the narrowness of the sequence, item 04 of loop0005). Prove
  that the free move is sound (closing a customer with N[c] ⊆ O(S) never
  hurts).

- [x] **08 Definite move.** `Search/DefiniteMove.lean`: Chu & Stuckey Thm 1
  (the move whose closing opens no more than it closes can be taken first),
  in the form the code uses.

- [x] **09 Subset rule.** `Search/SubsetRule.lean`: the subset rule with its
  index tie-break, sound on its own and after the definite move.

- [x] **10 Better move.** `Search/BetterMove.lean`: Chu & Stuckey Thm 2 in
  its corrected form, sound in the composition `definite_move →
  subset_rule → better_move` citing only standing candidates. Prove Lean
  counterexamples to the two wrong forms item 06 confirmed (the uncorrected
  close count, and the cross-rule cycle).

- [x] **11 Memo and old move.** `Search/Memo.lean`: the memo (a state refuted
  once is refuted whatever path reached it) and the old move (Thm 3), each
  sound, and the reason the Python never combines them. Stated gaps allowed
  here only as named `Prop`s.

- [x] **12 Assemble.** `Search/Decide.lean`: an abstract search (the tree of
  states, pruned by the rules of items 07-11 in the code's order) returns
  "unsat" only if `¬ Solvable G k ∅`, so a refutation implies MOSP > k and,
  by `MOSPGraph.lean`, pw > k − 1. Finish `paper2/search_soundness.md` with
  the theorem, the Lean names, and a table mapping each premise the
  certificate checker (`learning/search_certificate.py`) verifies to the
  Lean lemma that justifies it.

- [ ] **13 Reserve.** The best remaining gap from items 03-12, one session.
