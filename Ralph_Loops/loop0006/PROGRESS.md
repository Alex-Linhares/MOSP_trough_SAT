# loop0006 progress

Plan: `paper2/plan.md` section 4 (phase B) and the complex (phase A); items in
`iterations.md`; rules in `TASK.md`. Gate: `python3 Ralph_Loops/loop0006/gate.py`.

Current: 5/13 SOLVED

## Setup — 2026-09-30

- Baseline: loop0005 complete (Table 1 in `lean/MOSPFormalization/Complex/`);
  one `sorry` in code (`Sandwich.lean`, the §24 conjecture); 1,234 tests.
- New Lean for phase B goes in `lean/MOSPFormalization/Search/` (empty).
- Why these two: they are the two open items from `~/dev/pathwidth`'s to-do
  list (`pathwidth_solver/TODO.md`) that loop0005 did not cover. Pebbling is a
  candidate thirteenth member of the complex. The soundness of the pruning rules
  is what every certified refutation rests on; two `better_move` bugs broke it
  and were caught only by testing.

## Iteration 1 — 2026-09-30

### Completed
- **01 Pebbling census**, written as the new section "Pebbling (loop0006 item 01: the census)" at
  the end of `paper2/equivalences.md` (P.1–P.6). Sources read: Lengauer (1981) §1–4 and KP (1986)
  §1 and §3. Games are quoted with page numbers. The VSG positivity condition is `≤` on the page
  image; pdftotext reads it as `<`.
- **Verdict: pebbling is an exact member of the complex**, with an offset that depends on the graph:
  - KP Thm 3.1 with Thm 4.1: `mpb = mpbw = vs + 1 = pw + 1` on every nonempty graph (proposed row
    13a, offset +1 on G itself, `= Z`).
  - Lengauer Thm 2: `pbw(D) = pw(D_u) + 1` on every nonempty dag (13b). This also equals `Z(M_D)`,
    the MOSP value of the matrix whose column v is `N⁻[v]`, because D_u is that matrix's MOSP graph.
  - Lengauer Thm 3: `pbw(G_d) = pw(G) + 2` for G with an edge (13c).
  - Unrestricted BWP is **not** a member: `bw(G_d) ≤ 3` (Lengauer p. 469).
- **Edge cases and source faults found:**
  1. KP Thm 3.1's `mpb = ns` is false on edgeless nonempty graphs (`ns = 0`, `mpb = 1`).
  2. Lengauer Thm 2's instance form fails at K = 1 on edgeless dags, because VSG requires K ≥ 1.
     It holds with vs.
  3. Thm 3's instance form holds for every K ≥ 0 with vs. Only the number form needs an edge.
  4. Lengauer's p. 467 remark that recomputation does not help on directed trees is refuted for
     out-trees by KP's own ternary-tree example. It can only mean in-trees.
  5. KP's proof of `ns ≤ mpbw` asserts "no recontamination" without argument. The claim is true:
     a vertex loses its pebble only after all its neighbours have received one ([9]'s Lemma).
- **Observations the sources do not make:**
  - The undirected graphs of the form D_u are exactly the chordal graphs, which is why Thm 3 needs
    G_d.
  - `mpb = mpbw = pw + 1` has direct proofs (a layout orientation for ≤, pebble intervals for ≥)
    that avoid LaPaugh and node monotonicity.
  - KP's mpbw half is Lengauer's Thm 2 plus the lemma `min_D pw(D_u) = pw(G)`.
- **Spot check** (a throwaway `/tmp` script, not item 02's deliverable), all with zero failures:
  - Thm 2 as a number on 1,100 labelled dags with ≤ 5 vertices.
  - Lengauer's rules and KP's automatic turning give equal demand on the same dags.
  - Thm 3 as a number on 461 graphs with |V| ≤ 5 and |V| + |E| ≤ 9.
  - `mpb = mpbw = vs + 1` on 1,099 nonempty graphs with ≤ 5 vertices.
- Gate: `lake build` ok; sorry 1 of limit 1; 1231 passed, 2 skipped, 1 xfailed; GATE PASS.
  No Lean or Python changed this iteration.

### Blockers
- None. Cook & Sethi (1976) is not held, so BWP is taken as Lengauer states it (p. 466), as TASK.md asks.

### Next
- Item 02: build the progressive BW pebbling solver in `paper2/complex_check.py` and check P.5's
  eight statements. The naive state space is 4^n, so G_d is limited by |V| + |E|. Statement 8
  needs a repebbling black-game solver on a 13-vertex tree.
- Item 03 route (P.6): Thm 2 specialised to the depth-1 dag G_d, whose `G_u` is
  `Complex.triangleGraph`, then `isPositiveVSG_iff_triangleGraph`. State with `vertexSeparation`,
  not `vsg`.

## Iteration 2 — 2026-09-30 21:50

### Completed
- **02 Pebbling brute force.** Added to `paper2/complex_check.py`:
  - Four games, written from the source wording and decided exactly by search
    over positions with a pebble budget:
    - progressive black-white under Lengauer's rules (optional turning) and
      under KP's (automatic turning);
    - progressive black;
    - unrestricted BWP (rule (iii));
    - unrestricted black with repebbling.
  - The constructions `lengauer_u`, `lengauer_d`, `pebble_matrix`,
    `acyclic_orientations` and `is_chordal`.
  - A live-position check of P.3's recontamination lemma.
  - `run_pebbling`, run with `python -m paper2.complex_check --pebbling`: 279 s
    on 32 cores; writes `paper2/data/pebbling_check.json`.
- **Every statement of P.5 holds, with zero counterexamples**, on:
  - all 33,868 labelled dags with ≤ 6 vertices, plus 20,000 random dags on 7;
  - all 299 atlas graphs with `|V| + |E| ≤ 14` for G_d;
  - all 1,252 atlas graphs on ≤ 7 vertices with every directive;
  - all 4,394 rooted trees with ≤ 11 vertices;
  - 359,744 live play positions for the lemma.
  The results are written up as P.7 in `paper2/equivalences.md`; P.3 and P.4
  now point to it.
- **Finding:** Lengauer's p. 467 remark, read for out-trees, first fails at
  **7 vertices**: the spider with three legs of length 2 has pbw = pb = 3 and
  bw = b = 2. KP's 13-vertex tree is not the smallest counterexample, and no
  out-tree on ≤ 6 vertices fails. Over all rooted trees to 11 vertices the
  out-tree gap is 1 on 1,559 of them and 0 on the rest, never more. On
  in-trees, repebbling never helps in either game.
- **Named values:** `pbw(G_d(K_n)) = n + 1` for n = 2, 3, 4, while `bw = b = 3`,
  so statement 7's gap grows. KP's star gives 5 against mpb = 2.
- Tests: `tests/test_pebbling_check.py` has 20 tests, covering:
  - eight hand-computed dags under all four games;
  - exactness one pebble below the demand;
  - the rule that a white pebble is never removed;
  - `(G_d)_u = G_du`;
  - M_D and Z;
  - directives of C₄, P₄ and K₁,₄;
  - chordality against networkx;
  - the lemma;
  - a quick run with zero failures.
  The only error found was in one of my hand values (the in-spider's demand is
  4, not 3). The solver was right.
- Gate: `lake build` ok; sorry 1 of limit 1; 1251 passed, 2 skipped, 1 xfailed;
  GATE PASS. No Lean changed.

### Blockers
- None. Limits of coverage: dags are exhaustive only to 6 vertices (7 is
  sampled), G_d to `|V| + |E| ≤ 14`, and ns to 6 vertices.
- `paper2/problem_transformations.md` is unchanged. Its new §1.x, with the
  proofs, belongs with items 03 and 04, where the proofs are written.

### Next
- Item 03: Lengauer Thm 3 in Lean (`Complex/Pebbling.lean`), by the P.6 route.
  Define PBWP by per-vertex (received, lost) times or by move lists, check
  against `progressive_bw_within`, specialise Thm 2 to the depth-1 dag G_d,
  and finish with `isPositiveVSG_iff_triangleGraph`. State with
  `vertexSeparation`.

## Iteration 3 — 2026-09-30 22:08

### Completed
- **03 Lengauer Theorem 3 in Lean.** New file
  `lean/MOSPFormalization/Complex/Pebbling.lean`, imported from the root. It has
  no `sorry`, and its axioms are `propext`, `Classical.choice` and `Quot.sound`
  only; the new lines in `paper2/axiom_check.lean` check this.
  - **Definitions.** Under (iii') each vertex is pebble-free, then white, then
    black, then cleared, entering each phase once:
    - `PebblePhase` holds the four phases;
    - `PebbleMove` holds the three moves, place, turn and remove;
    - `PebbleMove.Legal` encodes Lengauer's rules (iv)–(vi), with an optional
      turn;
    - `PebblesWithin D K` means reachable through positions holding at most
      `K` pebbles. `IsPositivePBWP` adds `0 < K`, and `pbw` is the least `K`.
    This is the machine of item 02's `progressive_bw_within(rules="lengauer")`.
    `lengauerD G` is G_d on `V ⊕ G.edgeSet`, and it has depth one
    (`lengauerD_no_path_two`).
  - **Proved:**
    - `pebblesWithin_lengauerD_iff`: `PebblesWithin (G_d) (K+2) ↔ vs(G) ≤ K`
      for every graph and every K ≥ 0;
    - `isPositiveVSG_iff_isPositivePBWP_lengauerD`: Lengauer's statement, for
      K > 0;
    - `pbw_lengauerD` and its `_eq_pathwidth` and `_eq_vsg` forms:
      `pbw(G_d) = vs + 2 = pw + 2 = VSG + 2` if G has an edge;
    - `pbw_lengauerD_of_edgeless`: `pbw(G_d) = 1` if G is edgeless and
      nonempty. This is item 02's edge case.
  - **Route: direct on G_d, not the P.6 plan** (Thm 2 on G_d and then Thm 4).
    The development's vs counts the outer boundary, so both directions are
    short:
    - (⇐) clear the vertices in layout order. For each vertex v, blacken
      N[v], pass a pebble through each edge vertex at v, then remove v.
    - (⇒) lay the vertices out in the order they lose their pebble. At each
      cut, look at the moment the *last* cut edge turns. The edge vertex, its
      cleared endpoint and the whole active suffix are pebbled together
      (`outerBoundary_card_le`).
    Thm 2 is untouched, so item 04 still has to prove it.
  - About 900 lines. Every new lemma compiled on its first or second try except
    for heartbeat timeouts in `tauto`, which were replaced by explicit terms.
- **Python.** Added to `paper2/complex_check.py`:
  - `replay_progressive`, the Lean legality move by move;
  - `gd_layout_strategy`, the (⇐) construction;
  - `removal_layout`, the (⇒) layout;
  - `vs_outer_of_layout`, the Lean convention;
  - `run_pebbling_strategy`, run with
    `python -m paper2.complex_check --pebbling-strategy` (9 s, writes
    `paper2/data/pebbling_strategy_check.json`).

  It covers every layout of every atlas graph on 1–7 vertices, 1,252 graphs
  and 5,378,453 plays, with **zero failures**. The checks are:
  - the play is legal;
  - it stays within `vs(layout)+2` pebbles (1 if edgeless);
  - the removal layout satisfies the (⇒) bound;
  - an edge forces 3 pebbles;
  - the best layout attains `vs+2`.

  `tests/test_pebbling_check.py` has five new tests, 25 in total.
- **Docs.**
  - `paper2/problem_transformations.md`: new problem §1.13 (progressive
    black-white pebbling), transformation (E10) in §2.1, and the (E10) proof
    in §3, formal and then *In plain English*.
  - `paper2/equivalences.md`: new P.8, and row 13c of P.4 marked as proved.
- Gate: `lake build` ok; sorry 1 of limit 1 (the §24 conjecture); 1256 passed, 2 skipped, 1 xfailed; GATE PASS.

### Blockers
- None. The Python check of the (⇒) direction covers only the plays the (⇐)
  strategy produces. All plays were covered for the *statement* in item 02
  (P.7), not for the proof's construction. The Lean proof covers every play.

### Next
- Item 04: Lengauer Thm 2 (`pbw(D) = vs(D_u) + 1`, D nonempty) in
  `Complex/PebblingGu.lean`, and KP Thm 3.1 (`mpb = mpbw = vs + 1`, G
  nonempty). Reuse from this file: the game; `exists_seq_of_reflTransGen`,
  `seq_rank_mono` and `seq_exists_turn`, for time arguments on a play; and
  `exists_layout_of_injective`, for the removal-order layout.
  - (⇒) of Thm 2 is Lengauer's removal-time layout, in the outer convention.
  - (⇐) needs the four-step simulation, or a direct strategy in the style of
    `pebblesWithin_of_layout`.
  - For KP, the orientation-by-layout strategy with black pebbles gives `≤`,
    and `min_D` is P.3's lemma.
  - Then extend §1.13, (E10) and the master table with 13a and 13b.

## Iteration 4 — 2026-09-30 22:45

### Completed
- **04 Lengauer Theorem 2 and KP Theorem 3.1.** New file
  `lean/MOSPFormalization/Complex/PebblingGu.lean` (about 1,150 lines), imported from the
  root. No `sorry`; axioms `propext`, `Classical.choice`, `Quot.sound` only (new lines in
  `paper2/axiom_check.lean`).
  - **Definitions**:
    - `lengauerU D` (D_u, Def. 1a);
    - KP's progressive black game (`BlackMove`, `BlackPebblesWithin`, `pb`);
    - `IsDirective G D` (acyclic orientation), with `mpb` and `mpbw`;
    - `pebbleMatrix D` (M_D, column v = N⁻[v]).
  - **Lengauer Thm 2**:
    - `pebblesWithin_iff_lengauerU`: `PebblesWithin D (K+1) ↔ vs(D_u) ≤ K`, every digraph,
      every K ≥ 0;
    - `isPositivePBWP_iff_isPositiveVSG_lengauerU`: the stated form, for K ≥ 2;
    - `isPositivePBWP_one_not_isPositiveVSG_zero`: the K = 1 failure on arc-free D;
    - `pbw_eq_{vertexSeparation,pathwidth}_lengauerU_add_one`: `pbw(D) = vs(D_u) + 1 =
      pw(D_u) + 1`, D nonempty;
    - `pbw_eq_vsg_lengauerU_add_one`: the same with VSG, given an arc;
    - `mospGraph_pebbleMatrix` and `pbw_eq_mospValue_pebbleMatrix`: `pbw(D) = Z(M_D)`.
  - **KP Thm 3.1**, as item 01 settled it:
    - `mpb_eq_mpbw` and `mpb/mpbw_eq_{vertexSeparation,pathwidth}_add_one`: `mpb = mpbw =
      vs + 1 = pw + 1`, G nonempty;
    - `mpb_eq_nodeSearch`: the stated `mpb = ns = mpbw`, G with an edge;
    - `mpb_ne_nodeSearch_of_edgeless`: the false edge case, `mpb = mpbw = 1`, `ns = 0`.
  - **Finding (a strengthening, not a fault)**: Theorem 2 holds for the game on *any*
    digraph. Acyclicity is never used in either direction. It is checked by exact search on
    all 66,067 digraphs with at most 4 vertices, loops included.
  - **Routes**:
    - Thm 2 (⇒) is Lengauer's removal-order layout with his three cases
      (`outerBoundary_lengauerU_card_le`).
    - Thm 2 (⇐) is his four steps, recast as one invariant on positions (`guPos`: the outer
      boundary of the cleared set, black exactly where it has a cleared predecessor), in
      `reach_guPos_insert`.
    - KP (≥) is `G ≤ D_u` for every directive, plus Thm 2 (⇒) and a new
      `vertexSeparation_mono`.
    - KP (≤) orients along the reverse of an optimal layout and pebbles black in layout
      order. The live pebbles are exactly `Narrowness.lean`'s shack (`card_shackAfterPut`).
      This uses no node search, no LaPaugh and no monotonicity. `mpb = ns` then needs only
      `NodeMonotonicity.lean`.
  - Every lemma compiled within two or three attempts. No proof was abandoned.
- **Python**: a new section in `paper2/complex_check.py` with `digraph_pred`,
  `lengauer_u_general`, `gu_layout_strategy`, `replay_black`, `black_to_bw`,
  `kp_black_strategy` and `run_pebbling_gu`. Run it with
  `python -m paper2.complex_check --pebbling-gu` (9 s on 32 cores); it writes
  `paper2/data/pebbling_gu_check.json`. **Zero failures** on:
  - Thm 2's strategy over every layout of D_u, for 66,067 digraphs (≤ 4 vertices) and
    1,024 dags on 5. It checks legality, the `vs(layout)+1` bound, the (⇒) bound of the
    removal layout, optimality, and the statement by exact search.
  - KP's black strategy over every layout of the 1,252 atlas graphs on ≤ 7 vertices,
    5,378,453 plays. It checks black legality, the shack bound, legal replay as a
    black-white play with the same count, and optimality.

  Tests: `tests/test_pebbling_check.py` has 16 new tests, 41 in total, including a
  mutation test (dropping step 3 of Lengauer's four steps makes the play illegal) and the
  cyclic cases.
- **Docs**:
  - `paper2/problem_transformations.md`: §1.13 extended with D_u = G_{M_D}, the black game
    and mpb/mpbw; new (E11) (Thm 2) and (E12) (KP Thm 3.1) in §2.1; the edge cases added to
    (F3); proofs of (E11) and (E12) in §3, formal and then *In plain English*.
  - `paper2/equivalences.md`: master table row 13 (pebbling; not a Table 1 row) with a
    tally note; P.4 rows 13a and 13b marked as proved; new section P.9.
- Gate: `lake build` ok; sorry 1 of limit 1 (the §24 conjecture); 1272 passed, 2 skipped,
  1 xfailed; GATE PASS.

### Blockers
- None. Coverage limits of the Python check: digraphs are exhaustive only to 4 vertices,
  dags to 5, and graphs to 7. The Lean proofs cover all sizes.

### Next
- Phase A is done: rows 13a, 13b and 13c are all proved. The figure
  `paper2/figures/equivalence_chain.dot` does not yet show pebbling. Adding it is item 12's
  (assemble) job, not item 05's.
- Item 05, the search stated: write `paper2/search_soundness.md` §1–2 from
  `satisfiability/customer_search.py`, `customer_search.c` (`dominance_filter`) and
  `learning/search_certificate.py`, quoting the code lines, in the fixed order
  `definite_move → subset_rule → better_move`, citing standing candidates only.


## Iteration 5 — 2026-09-30 22:41

### Completed
- **05 The search, stated.** New `paper2/search_soundness.md` §1–2, with no
  Lean. Sources: `satisfiability/customer_search.py` (the reference),
  `customer_search.c` (`dominance_filter`, `subset_pass`, `better_move_pass`,
  `inherit_old_moves`, `search`), `learning/search_certificate.py` (the
  emitter and the checker), and Chu & Stuckey (2009), cited by preprint PDF
  page. Code is quoted with line numbers at `8d824d034`.
  - **§1, the model.** Covers:
    - `O(T)`, `fin(X)`, `o`, `open`, `close`;
    - the step cost `|O(T∪{c}) ∖ T|`;
    - free-closed states `cl(T) = fin(O(T))`. `O(cl T) = O(T)`, which is
      why the memo may key on the closed set;
    - `Sol_k` on states;
    - Lemma F (free moves), under `|O(T)∖T| ≤ k`, which holds at every node;
    - a full order's cost is `outNarrowness` (`Complex/Narrowness.lean`,
      `outShackBeforeMove`), so `min cost = narrowness = pw + 1 = MOSP`. This
      is the connection item 07 must prove;
    - the node procedure step by step.
  - **§2, the rules.** For each rule: the premise and conclusion exactly as
    coded, the code lines, the order, why it is acyclic, and what Cert
    checks. The rules are the free move, the definite move (first `q` in
    index order; `close` counts `R(S)`, including `q` and `Q`), the subset
    rule (dominators range over all of `R(S)`, including `Q`, with an index
    tie-break and an all-dominated fallback), the corrected better move, the
    old move and the memo. For the better move:
    - its inputs are the subset survivors in index order;
    - an earlier-index `q` among the first `L` may cover `r`;
    - playability is measured in the paper's measure;
    - the close count skips customers `r` finishes;
    - the proof sketch goes through Thm 1 at `cl(S∪{r})` and the swap.

    Node soundness is stated as a covering condition: every chain from a
    discarded playable candidate ends in `L` or `Q`. That is Cert's step 5.
    The two bad forms (Bug A, the close count; Bug B, the cross-rule cycle)
    are located in the C variant bits.
  - **§2.9, the claim.** Every flag setting with `restrict`, `expansion_prune`
    and the variant bits off, and the order `free → memo → Q → cost cut →
    definite → subset → better`, answers `unsat` only if `¬Sol_k(∅)`. The
    table there shows the five configurations that produced refutations
    (Python reference, C default, `csearch`, `recertify`, Cert `memo`) as
    instances of it.
- **Findings (stated, not yet proved):**
  1. **Every production refutation ran old move and the memo together.**
     `decide()` defaults to both and routes to the C, which is the path of
     `csearch`, `recertify` and the harness's `default`. That combination is
     the one the Python refuses and Cert declines to check. §2.7 argues it is
     **sound**, by induction on subtree completion order: a node's `Q` entries
     rest only on refutations that are already complete, so they are genuine.
     If so, the Python docstring's stated reason ("could refute a state that
     some other path would not") is not a soundness argument, and only
     Cert's local-checkability point stands. This is recorded as a claim for
     item 11, not a finding.
  2. The C comment at `customer_search.c:178` ("only the cheapest few q")
     is inaccurate. The dominator loop takes the first `L` subset survivors
     *by index*, because sorting by cost happens after the filter. This does
     not affect soundness. The code is not changed.
  3. Chu & Stuckey's old-move/better-move "synergy" (PDF p. 7) is
     implemented nowhere.
- **Spot check before stating** (a throwaway `/tmp` script, not item 06's
  deliverable). `Sol_k` was computed by DP over closed sets, on 300 random
  graphs with 2–8 vertices at every k, 1,461 `(graph, k)` pairs. Checked:
  - Lemma F;
  - the definite move's conclusion `Sol(S) ⇒ Sol(S·q)`;
  - the subset rule's `Sol(S·r) ⇒ Sol(S·d)` for every pair;
  - the corrected better move's `Sol(S·r) ⇒ Sol(S·q)` for every pair.

  There were **zero failures**.
- **Test.** `tests/test_search_soundness_doc.py` has 3 tests. They check that
  every quoted `Py:`/`C:` code line (54 lines in 7 blocks) is still in the
  cited source, with indentation, `...` and the document's `/* */`
  annotations ignored, and that the C runs `subset_pass` before
  `better_move_pass`. A mutation (a bogus quoted line) is caught.
- Gate: `lake build` ok; sorry 1 of limit 1 (the §24 conjecture); 1275 passed,
  2 skipped, 1 xfailed; GATE PASS. No Lean changed.

### Blockers
- None. The spot check covers only graphs with ≤ 8 vertices, and it did not
  simulate old move or the memo, because they depend on the path. Item 06 is
  the exhaustive check. The claim in §2.7 that old move plus the memo is
  sound rests on an argument and on the existing harness counts, not on a
  check made here.

### Next
- Item 06: `paper2/search_check.py`. Implement §2's rules exactly as stated,
  including the index-order dominator loop with `L`, the subset fallback, and
  `Q` inheritance, and check node soundness in the covering form of §2.0 on
  every graph with ≤ 7 vertices at every k:
  - each rule singly;
  - the composition;
  - Bug A and Bug B, which should fail. Bug A may need more than 11 customers
    (`better_move_bug.md` §7), so search larger random sparse instances if it
    does not fail at 7;
  - old move with the memo, run by a full tree search against `Sol_k`. This
    tests the §2.7 claim.
- Item 07's connecting lemma: a full order's cost equals `outNarrowness`
  (`outShackBeforeMove`), then `outNarrownessGraph_eq_narrowness` and
  `narrowness_eq_pathwidth_add_one`.
