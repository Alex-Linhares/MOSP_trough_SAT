# loop0006 progress

Plan: `paper2/plan.md` section 4 (phase B) and the complex (phase A); items in
`iterations.md`; rules in `TASK.md`. Gate: `python3 Ralph_Loops/loop0006/gate.py`.

Current: 12/13 SOLVED

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

## Iteration 6 — 2026-09-30 23:55

### Completed
- **06 Brute-force soundness check.** New `paper2/search_check.py`, which
  implements §1–2 of `paper2/search_soundness.md` from the document. It shares
  no code with `satisfiability/` or `learning/`. It has four parts:
  - an exact `Sol_k`/`P_k` oracle;
  - `node_filter`, which records a covering link for every discard;
  - `search_decide`, the whole §1.5 search with old move, inheritance and the
    memo;
  - five variants: `fixed`, `old_close` (Bug A), `old_order` (Bug B),
    `prefix` (both) and `bm_first`.

  Run it with `python -m paper2.search_check`: 1,030 s on 30 cores, writing
  `paper2/data/search_check.json`. The write-up is the new §3 of
  `paper2/search_soundness.md`.
- **Checks** at every `k`:
  - Lemma F;
  - node soundness at every free-closed state, over 46 filter configurations
    (every rule subset, better move with `L ∈ {0,1,2}`, every variant) and
    over families of genuinely refuted `Q`;
  - every cited link `Sol(S·r) ⇒ Sol(S·c)`;
  - every rule's premise ⇒ conclusion over *all* pairs;
  - the covering condition (Cert step 5);
  - the whole search in 184 flag combinations against the oracle;
  - the same runs through the C, where answer **and node count** must agree.
- **Instances:**
  - every labelled graph on 1–6 vertices (33,867);
  - every graph on 7 vertices × 25 labellings (26,100);
  - 6,000 random sparse graphs and Chu & Stuckey-shaped matrices at 8–16
    vertices;
  - the three pinned counterexamples.
- **Result: the rules as §2 states them have zero failures of any kind.** The
  totals are 557 M node checks, 2.9 G cited links, 1.9 G pair applications,
  83.5 M tree runs and 862 M Lemma F cases. That covers every rule singly and
  every composition, including **old move together with the memo** (§2.7):
  7.1 M tree runs at ≤ 7 vertices and 240 k at 8–16, all agreeing with the
  oracle. This is evidence for item 11's claim, not a proof of it.
- **The port equals the C, node for node, on all 4,418,084 runs**, the bad
  variants included. So §2 is a faithful statement of the code, and the
  failures below are the C's.
- **Both bad forms fail, each in its own way:**
  - **Bug A** (close count) makes the rule's own conclusion false. Its pairs
    fail 496 times in 1.54 G applications, the first at 12 vertices, and none
    at ≤ 11. It loses the last solution at a node only above 12 vertices. It
    gives a false refutation only on the pinned 17 × 9, and on none of the
    6,000 random instances.
  - **Bug B** (rule order) never has a false link at any size checked. It
    forms cycles from **6 vertices** (exhaustive), loses the last solution at
    a node from **8 vertices**, and gives a false refutation from **10
    vertices** on its own.
  - The pinned instances reproduce the record exactly:
    - 17 × 9 falls to `old_close` and `prefix`;
    - 10 × 13 falls only to `prefix` at the tree level, but already to
      `old_order` at a node;
    - drawn 10 × 20 falls to `old_order` and `prefix`.
- **New small witnesses for Bug B**, pinned in the tests as candidates for
  item 10's Lean counterexample:
  - a node on 8 vertices: masks `[139,59,12,15,178,242,224,241]`, `k = 4`,
    `S = {2}`, `P = [0,3,6]`. Better move drops 3 citing 0, the subset rule
    drops 0 citing 3, and `L = [6]` is dead;
  - a 10-vertex false refutation by Bug B alone: masks
    `[523,519,678,73,16,548,72,388,384,551]`, optimum 3.
- `bm_first` (`BM_SUBSET_RESTRICTED`) never fails anywhere. This supports the
  C comment's argument, and it is not claimed.
- **A planted fault is caught**: better move with any candidate as cover (the
  Warwick cycle) but with the C's keep-if-empty guard. It is clean to 5
  vertices and fails on 60 of 32,768 labelled graphs on 6.
- **Tests.** `tests/test_search_check.py` has 14 tests:
  - the oracle against literal permutation minima;
  - all rules clean on every graph to 4 vertices;
  - the port against the C node for node;
  - Bug A on the 17 × 9, as a false conclusion;
  - Bug B on the 10 × 13, as a cycle of true premises;
  - the covering-condition unit test;
  - the subset fallback;
  - the planted mutation;
  - the two new Bug B witnesses;
  - a round trip.
- Gate: `lake build` ok; sorry 1 of limit 1 (the §24 conjecture); 1289
  passed, 2 skipped, 1 xfailed; GATE PASS. No Lean changed.

### Blockers
- None. Coverage limits:
  - graphs on 7 vertices are covered under 25 labellings, not all 5,040;
  - `Q` families are sampled when more than 4 children are refuted;
  - the random family runs only better-move configurations with `L = 0` at
    `k ≥ n/5`;
  - Bug A lives at ≥ 12 customers, so it was reached only by sampling.

### Next
- Item 07: `Search/Basic.lean`, covering closed sets, `O`, `fin`, `cl`, the
  step cost, `Sol_k`, Lemma F, and the connection from a full order's cost to
  `outNarrowness` (`outShackBeforeMove`), then to
  `outNarrownessGraph_eq_narrowness` and `narrowness_eq_pathwidth_add_one`.
- For item 10, the 8-vertex Bug B node is the smallest witness found for the
  Lean counterexample to the old order. For Bug A the smallest pair failure
  seen has 12 vertices; a node-level counterexample can use a single state of
  the 17 × 9.

## Iteration 7 — 2026-09-30 23:24

### Completed
- **07 Search model in Lean.** New file `lean/MOSPFormalization/Search/Basic.lean`
  (about 600 lines, namespace `MOSPFormalization.Search`), imported from the root.
  No `sorry`; axioms `propext`, `Classical.choice`, `Quot.sound` only (new lines in
  `paper2/axiom_check.lean`).
  - **Definitions**, on arbitrary closed sets, following `search_soundness.md` §1:
    - `nbhd`, `opened` (O), `finished` (fin), `cl`, `stepCost`;
    - `orderCost` (the maximum step cost along a list), `IsClosingOrder`;
    - `Solvable G k T` (P_k: some ordering of V \ T after T costs ≤ k);
    - `SearchSol G k S` (Sol_k), an inductive predicate whose children are
      `cl (insert c S)`, as the code recurses. It is not defined via `Solvable`.
  - **Proved:**
    - `solvable_mono`: `T ⊆ T'` and `O(T') ⊆ O(T)` give `P_k(T) → P_k(T')`.
    - **Free move**: `solvable_insert_of_free` (no hypothesis), with its converse
      `solvable_insert_iff_of_free` under the node invariant `|O(S) \ S| ≤ k`;
      also `solvable_cl` and `solvable_cl_iff`.
    - **Lemma F**: `solvable_iff_searchSol_cl`, `P_k(T) ↔ Sol_k(cl T)` under the
      invariant. The (→) half, `searchSol_cl_of_solvable`, needs no hypothesis.
      At the root, `solvable_empty_iff`.
    - **Cost = narrowness**: `orderCost_ofFn_eq_outNarrowness` (the closing order
      of a layout τ costs `outNarrowness G τ`, step by step via
      `stepCost_orderOfLayout`), `orderCost_ofFn_eq_vertexSepOfLayout_add_one`
      (`= vs(τ) + 1`), and `exists_orderOfLayout` (every full closing order is
      one of these).
    - **The search decides pathwidth and MOSP**:
      - `solvable_empty_iff_narrowness_le`;
      - `searchSol_empty_iff_{narrowness_le, vertexSeparation_add_one_le,
        pathwidth_add_one_le}`;
      - `searchSol_mospGraph_iff_mospValue_le`: `Sol_k(∅)` on `mospGraph M` iff
        `mospValue M ≤ k`, given one requirement.

      So `¬ Sol_k(∅)` means `mospValue > k`.
  - The whole file compiled after one round of fixes: four local tactic errors,
    no proof abandoned.
- **Check before stating.** `python -m paper2.search_check --model` is a new
  section of `paper2/search_check.py` that transcribes the Lean definitions
  literally. It runs in 48 s on 30 cores and writes
  `paper2/data/search_model_check.json`. It covers every labelled graph on 0–6
  vertices and every atlas graph on 7 (34,912 graphs), with every layout and
  every k. **Zero failures** across:
  - 29.0 M layouts (`orderCost = outNarrowness = vs + 1`);
  - 91.5 M monotonicity pairs;
  - 33.0 M free moves;
  - 18.2 M Lemma F cases.

  The invariant is needed: without it, Lemma F's (←) fails in 3.55 M cases and
  the free move's converse in 3.76 M. The smallest case is K₂ with one customer
  closed at k = 0. `tests/test_search_check.py` has four new tests (18 in all):
  - a quick run with no failures;
  - hand values on P₃ and K₁,₃;
  - the K₂ case;
  - a mutation (a step cost that forgets the closed customer breaks `= vs + 1`).
- **Docs.** New §4.1 in `paper2/search_soundness.md` gives:
  - a definition table from §1 to Lean;
  - every theorem with its proof idea;
  - modelling notes: inactive customers, where the invariant matters, and what
    is not yet modelled;
  - the check table.
- Gate: `lake build` ok; sorry 1 of limit 1 (the §24 conjecture); 1293 passed, 2 skipped,
  1 xfailed; GATE PASS.

### Blockers
- None. What is not modelled yet: `Q`, the dominance filter, the memo and the
  node procedure (items 08–11). The final theorem is stated on `mospGraph`,
  which keeps customers with no product as isolated vertices. The search drops
  them; the argument that this changes nothing is in §4.1.3, and the Lean
  statement on the active subgraph is item 12's.

### Next
- Item 08: `Search/DefiniteMove.lean`. Chu & Stuckey Thm 1 in the code's form
  (§2.2: the first `q` in index order with `open(q) ≤ close(q)`, `close`
  counting unfinished `d` with `o(d) ⊆ o(q)`). State it on a free-closed state
  `S` under the invariant, as
  `Solvable G k S → cost(S, q) ≤ k ∧ Solvable G k (cl (insert q S))`.
  - Reuse `solvable_mono`, `solvable_cl_iff`, `exists_first_move` and
    `solvable_of_solvable_insert`.
  - The swap argument moves `q` to the front of an optimal order. The customers
    `d` with `o(d) ⊆ o(q)` become free after `q`, which is what
    `solvable_mono` covers.

## Iteration 8 — 2026-10-01 00:30

### Completed
- **08 Definite move. FINDING: Chu & Stuckey's Theorem 1 is FALSE, both as the paper
  states it and as the C and Python implement it.** At a node the definite move can discard
  the last solution. New file `lean/MOSPFormalization/Search/DefiniteMove.lean`, 422 lines,
  imported from the root. No `sorry`; axioms `propext`, `Classical.choice`, `Quot.sound`
  only (new lines in `paper2/axiom_check.lean`).
  - **The counterexample in Lean** is `definiteMove_counterexample`, on `cexGraph`: 14
    customers, 26 edges. At the free-closed state `S = {2}`, with `k = 6`:
    - the invariant holds, and `q = 0` is playable with `close = open = 3`;
    - `q = 0` is first in index order, and the port of the C filter keeps it alone;
    - `Solvable` and `SearchSol` hold at `S`;
    - neither holds at the child `{0,2,3,4}`.

    The mechanism: `3` and `4` share the single new stack `0`, so closing them first gains
    two stacks for one. The paper's proof counts them as "extra stacks closed" even when
    `U′` had already closed them.

    The negative half is `not_solvable_of_invariant`, applied to the 7 states reachable
    within 6 stacks, which `decide +kernel` checks in about 30 s.

    A second, independent slip: the literal `S ++ [q] ++ …` is not a solution even where
    the theorem holds, because free customers stay open. The smallest case has 4 customers.
  - **The repair, proved sound.** Write `X` for `cl(S ∪ {q})`. The repaired premise,
    `IsHereditarilyDefinite`, asks `b(X) ≤ b(B)` for all `B` with `S ⊆ B ⊆ X` and
    `q ∉ B`, where `b(T) = |O(T) ∖ T|`. The code's premise is the case `B = S`
    (`isDefinite_iff`).
    - `solvable_cl_insert_of_hereditarilyDefinite` and
      `searchSol_cl_insert_of_hereditarilyDefinite` prove it sound.
    - The proof is by uncrossing, from `openStacks_submodular` (`b` is submodular).
    - Sufficient conditions: `open ≤ 1`, and a matching of `open − 1` customers of
      `X ∖ S ∖ {q}` to distinct new stacks (`isHereditarilyDefinite_of_matching`). By
      Hall with deficiency the matching form is equivalent to the repair; that is checked,
      not proved.
  - **Does the C implement the right one? No.** `customer_search.c:313–330` and
    `Py:404–412` use the unsound `close ≥ open`. So does every production configuration
    (§2.9). The solver is unchanged; the owner decides. The repair costs one small
    bipartite matching per candidate that passes the current test.
  - **Consequences.** §2.9's composition claim is false at the node level whenever
    `definite_move` is on. No wrong answer on a whole instance was found:
    - a port of the search (free moves, definite move, memo) run at the optimum gave zero
      false refutations on 600,000 random graphs at 10–18 vertices and on 90,000 gadget
      graphs at 12–17;
    - both pinned instances answer correctly.

    It is open whether a whole instance can be refuted falsely. Item 12 must either state
    its theorem for the repaired rule or name this gap.
- **Search.** The throwaway C checks, now committed as `paper2/definite_hunt.c` and
  `definite_hunt_gen.py`, found:
  - no loss on any graph to 9 vertices (exhaustive), nor on the 88,802 connected graphs on
    10 vertices with at most 14 edges;
  - losses only at 14–16 vertices, in a "gadget" family built from the failed proof;
  - after minimisation by deletion, 14 vertices, never fewer;
  - under the repair and its matching form, zero losses in 2.05 G checks (all graphs on 8
    vertices, 60,000 random graphs), plus 272 M checks on gadget graphs.
- **Python.** `python -m paper2.search_check --definite` takes 16 s and writes
  `paper2/data/search_definite_check.json`. It covers 36,911 graphs (labelled graphs to 6,
  the atlas at 7, 2,000 random graphs at 10–13) with zero failures across:
  - 72.7 M submodularity cases;
  - 35.7 M cases each of `isDefinite_iff`, repair ⇔ matching, and repair ⇒ code premise;
  - 29.1 M repair-soundness cases.

  On these graphs the code's rule fires without the repair 20,857 times and never loses a
  solution. The two pinned counterexamples (`DEFINITE_CEX`) do lose one.
  `tests/test_search_check.py` has 7 new tests, 25 in total, including a mutation (the
  code's premise in place of the repair gets caught).
- **Docs.** `paper2/search_soundness.md`:
  - a finding box at the top;
  - a finding and the repair in §2.2;
  - the §2.9 claim marked false as stated;
  - a new §4.2 (definitions, theorems, why the paper's proof cannot be patched locally,
    and the check).
- Gate: `lake build` ok; sorry 1 of limit 1 (the §24 conjecture); 1300 passed, 2 skipped, 1 xfailed; GATE PASS.

### Blockers
- None for the item. Open: a whole-instance false refutation from the definite move (none
  found), and a Lean proof of the matching ⇔ repair converse (Hall).

### Next
- Item 09, the subset rule. Check before stating: the rule cites dominators over all of
  `R(S)`, including `Q`, with an index tie-break. Its pair conclusion may have the same
  collision weakness. Item 06 saw no failure to 16, but the definite move also passed
  item 06 and failed at 14. Run `definite_hunt`-style exact checks of
  `Sol(S·r) ⇒ Sol(S·d)` on gadget families first.
- Items 10–12 must build on the repaired definite move, and item 12's composition theorem
  must say which rule it covers.

## Iteration 9 — 2026-10-01 00:20

### Completed
- **09 Subset rule. It is sound as coded, on its own and after the repaired definite move.
  FINDING: the index tie-break is needed for soundness, not only for acyclicity.** New file
  `lean/MOSPFormalization/Search/SubsetRule.lean`, 391 lines, imported from the root. No
  `sorry`; axioms `propext`, `Classical.choice`, `Quot.sound` only (new lines in
  `paper2/axiom_check.lean`). Customers carry a `LinearOrder`, which is the index order.
  - **Definitions:**
    - `Dominates` (`d ≠ r`, `o(d) ⊆ o(r)`, strict or `d < r`);
    - `IsSubsetDominated` (dominators over all of `V ∖ S`, `Q` included, as the code does);
    - `playable` (the cost cut);
    - `subsetKept` and `subsetFilter` (with the all-dominated fallback);
    - `definiteThenSubset D` (the least `q` meeting `D` alone, else the subset filter);
    - `codeFilter` and `repairedFilter` at a node `(S, Q)`;
    - `WeakDominates` and `weakSubsetFilter` (no tie-break).
  - **Proved:**
    - `searchSol_cl_insert_of_newlyOpened_subset`, the covering: if `o(d,S) ⊆ o(r,S)` and
      `r` is playable, then `Sol_k(S·r) → Sol_k(S·d)`. It holds at *every* `S`, with no
      invariant and no tie-break. The proof: `d ∈ S·r`, `S·d ⊆ S·r`, and `(S·d)·r = S·r` at
      no greater cost. Unlike Theorem 1, the paper's argument is right as it stands.
    - `not_dominates_self` and `Dominates.trans`: a strict order.
    - `exists_undominated`: take the least `m` by `(|o(m)|, m)`. One covering step reaches
      a survivor, so no chain argument is needed.
    - `subsetFilter_sound`: node soundness with any family `Q` of refuted old moves.
      `subsetKept_nonempty`: the fallback never fires when a solution exists.
    - `definiteThenSubset_sound`: for any definite premise sound at `S`, the composition is
      node-sound. `repairedFilter_sound` instantiates it with item 08's repair, under the
      invariant.
    - `codeFilter_counterexample`: with the code's premise, the composition keeps `{0}` on
      `cexGraph` and loses the solution. The loss is the definite move's; the subset rule
      does not run at that node.
    - **`noTieBreak_counterexample`**, on `tieGraph`, 7 customers and 8 edges. At `S = {2}`
      with `k = 3`, the twins `0` and `3` (`o = {3,6}`) dominate each other and both go.
      `5` survives, so the fallback does not fire. The filter keeps `{5}`, and `{2}·5` has
      no solution while `{2}` has one. With the tie-break, `subsetFilter = {0, 5}`.
  - **Does the C implement the right form? Yes.** `Py:417–428` and `C:151–164` both break
    ties by `d < r`, and so does Cert:617–627. The paper's own form (`d < r` required
    always) is also sound; it is checked, not stated in Lean.
- **Check before stating.** `python -m paper2.search_check --subset` takes 80 s on 30 cores
  and writes `paper2/data/search_subset_check.json`. Graphs:
  - every labelled graph on 1–6, checked at every set;
  - atlas graphs on 7, and 1,500 random graphs at 10–13, at the search's states;
  - 2,000 relabelled gadget graphs at 12–16, at `k ∈ {opt−1, opt, opt+1}`.

  **Zero failures** across:
  - 837 M pair facts;
  - 533 M covering cases;
  - 184 M transitivity triples;
  - 78 M undominated queries;
  - 12.6 M nodes where the Lean filter equals item 06's port of the code, with the definite
    move on and off;
  - 8.5 M nodes each for node soundness, the repaired composition and the paper's form.

  The no-tie-break form loses the last solution at 4,730 nodes. None has ≤ 6 vertices; the
  first are at 7. The code's composition lost nothing outside the pinned definite
  counterexamples. `tests/test_search_check.py` has five new tests, 30 in total, including
  a mutation (removing the tie-break gets caught) and the Lean graph with its certificates.
- **Docs.** `paper2/search_soundness.md`:
  - the §4 bullet at the top;
  - an item 09 paragraph in §2.3;
  - a note in §2.9 that the subset rule is not what breaks the claim;
  - new §4.3 (definitions, theorems, what Cert checks, the check table).
- Gate: `lake build` ok; sorry 1 of limit 1 (the §24 conjecture); 1305 passed, 2 skipped,
  1 xfailed; GATE PASS.

### Blockers
- None. The paper's literal form of the rule is checked only, not proved in Lean. It is a
  subrelation with the same covering, so it would be a small addition if item 12 wants it.

### Next
- Item 10, the better move. Build on `definiteThenSubset` and `subsetFilter`. The node
  filter becomes `definite → subset → better`, where better move cites only earlier
  subset survivors among the first `L`.
- Prove the covering for the corrected premise with the close count skipping customers `r`
  finishes. A route: Theorem 1 at `cl(S∪{r})` and the swap. Since Theorem 1 is false as
  coded (item 08), the better move's proof must not go through the unrepaired Theorem 1.
  Check first whether the corrected better move itself is sound; it is Theorem 1 applied at
  `S·r`, and may inherit the same collision weakness at ≥ 14 customers. Run a
  `definite_hunt`-style exact check on gadget graphs before stating.
- Counterexamples for Bugs A and B: the 8-vertex Bug B node from item 06, and a state of
  the 17 × 9 for Bug A.

## Iteration 10 — 2026-10-01 00:50

### Completed
- **10 Better move. FINDING: the *corrected* better move is still unsound as a pairwise
  rule, and the C runs it.** Its premise 4 is exactly the code's definite-move premise for
  `q` at the child `cl(S ∪ {r})`, so it inherits item 08's falsity of Theorem 1. No node where
  it loses the last solution has been found. New file
  `lean/MOSPFormalization/Search/BetterMove.lean`, about 500 lines, imported from the root.
  No `sorry`; axioms `propext`, `Classical.choice`, `Quot.sound` only (new lines in
  `paper2/axiom_check.lean`, above the control).
  - **Definitions:**
    - `betterOpen`, `betterClose` (the corrected count) and `betterCloseOld` (Bug A);
    - `IsBetter` (premises 3 and 4), `IsBetterOld` and `IsRepairedBetter`;
    - `withinLimit` (premise 1, `L`) and `betterCite`;
    - `betterFilterBy`, the pass, which like the C does not consult whether `q` survives;
    - `fullFilter` (`definite → subset → better` for any premises), `codeFullFilter`,
      `repairedFullFilter` and `oldOrderFilter` (Bug B's order).
  - **Proved:**
    - `isBetter_iff`: `IsBetter ↔ stepCost (S∪{r}) q ≤ k ∧ IsDefinite (cl(S∪{r})) q`.
    - **`betterMove_counterexample`**, on item 08's `cexGraph` at the root with `k = 6`:
      the definite move does not fire, and `0` and `2` survive the subset rule. The code
      drops `2` citing `0` under the corrected premise, and the repaired premise fails.
      `S·2 = {2}` has a solution; `S·0 = {0}` has none, shown by an invariant family of 18
      states. `betterMove_counterexample_node`: the filter still keeps `1`, which has a
      solution, so this is a false link, not a lost node.
    - **The repair**, `IsRepairedBetter`, is premise 3 plus `q` hereditarily definite at the
      child. `solvable_cl_insert_of_repairedBetter` and
      `searchSol_cl_insert_of_repairedBetter` prove `Sol_k(S·r) → Sol_k(S·q)` for `r`
      playable, by the paper's route: the repaired Thm 1 at the child, then the swap. `q`'s
      playability is not needed. Also proved: `IsRepairedBetter.isBetter` and
      `isRepairedBetter_of_openCount_le_one`.
    - **The composition**: `betterFilterBy_sound` (the least member of `W` with a solution
      is never dropped, so no chain argument is needed and `L` does not matter),
      `fullFilter_sound`, and **`repairedFullFilter_sound`**: with both repairs,
      `definite → subset → better` is node-sound under the invariant, for any `L` and any
      refuted `Q`.
    - **`bugA_counterexample`**: 12 customers, root, `k = 4`, `r = 6`, `q = 4`. The old
      premise holds and the corrected one does not; `S·6` has a solution and `S·4` has
      none. It was found by the new `paper2/better_hunt.c` (`MODE=1`).
    - **`bugB_counterexample`**: item 06's 8-customer node, `S = {2}`, `k = 4`. The old
      order keeps `{6}`, a dead child, while the fixed order keeps `{3, 6}`. Every premise
      is the corrected one; the fault is the cycle `3 → 0 → 3`.
  - Two compile rounds, three local fixes, no proof abandoned.
- **Does the C implement the right form? No.** `customer_search.c:213–251` tests premises 3
  and 4, which is the unsound form. It runs whenever `better_move` is on: `csearch` on sparse
  instances, and `recertify` always. The certificate checker (Cert:628–637) accepts the false
  link. The solver is unchanged; the owner decides.
- **Python.**
  - `python -m paper2.search_check --better` takes 187 s on 30 cores and writes
    `paper2/data/search_better_check.json`. It covers 36,411 graphs (labelled to 6, atlas 7,
    1,500 random at 10–13) plus 2,000 augmented definite counterexamples at 14–17. **Zero
    failures** across 513 M pairs (`isBetter_iff`, repair ⇒ code), 169 M repaired
    applications, and 20.4 M nodes: the Lean filters equal item 06's port in both orders,
    and the repaired composition is node-sound.
  - The code's premise gives 681 false links, all on augmented graphs, and loses no node
    through the better move. The definite move loses 1,810 nodes, Bug A gives 8,371 false
    links, and Bug B loses 4,135 nodes.
  - `paper2/better_hunt.c` and `paper2/better_hunt_gen.py`: 25,300 graphs at 12–18 gave 798
    false links and no lost node. The repair (`MODE=2`) gave nothing on 11,200 graphs.
  - `tests/test_search_check.py` has seven new tests, 37 in total, including a mutation (the
    code's premise used as the repair gets caught) and the hunter run on `cexGraph`.
- **Docs.** `paper2/search_soundness.md`:
  - a finding box at the top;
  - an item 10 paragraph in §2.4, where the "why" fails exactly at its appeal to §2.2;
  - an item 10 note in §2.9;
  - new §4.4, covering definitions, theorems, the C, what Cert checks, and the check table.
- Gate: `lake build` ok; sorry 1 of limit 1 (the §24 conjecture); 1312 passed, 2 skipped,
  1 xfailed; GATE PASS.

### Blockers
- None for the item. Open: whether the better move (or the definite move) ever loses a node,
  or a whole instance, under the code's premises. No case has been found.

### Next
- Item 11, the memo and old move (`Search/Memo.lean`).
- Item 12 must state its theorem for `repairedFullFilter` (proved node-sound here) or name
  two gaps: the definite move and the better move as coded. It must also say which premise
  the certificate checker certifies, since Cert accepts the false link of
  `betterMove_counterexample`.

## Iteration 11 — 2026-10-01 00:56

### Completed
- **11 Memo and old move. RESULT: each is sound, and they are sound together. This settles
  §2.7's claim: the C has always run old move with the memo, and so has every production
  refutation. The Python's reason for refusing the combination is not a soundness argument.**
  New file `lean/MOSPFormalization/Search/Memo.lean`, 380 lines, imported from the root. No
  `sorry`, no stated gap (`allowed_sorries.txt` unchanged); axioms `propext`,
  `Classical.choice`, `Quot.sound` only (ten new lines in `paper2/axiom_check.lean`). The
  general part needs only `DecidableEq`.
  - **Old move (Thm 3)**:
    - `searchSol_reinsert` is the one-step form, under the code's inheritance test
      `stepCost (insert q S) c ≤ k`: `Sol_k(cl(q·cl(c·S))) → Sol_k(cl(q·S))`. It holds at
      every set, with no invariant. Both routes reach `cl(S ∪ {q,c})`
      (`cl_insert_cl_insert_comm`). If `q` made `c` free, the step vanishes; otherwise
      `stepCost_cl_le` applies.
    - `searchSol_reinsert_path` iterates it and `not_searchSol_of_oldMove` is the rule. The
      ancestor invariant of §2.6 is the iterate of the one-step form; it does not have to
      be carried along the path.
    - **`reinsert_needs_test`**: the test is necessary. On the path `4–0–2–1–3` with
      `S = ∅`, `q = 2`, `c = 3`, `k = 2`, the lemma fails without it. This is the smallest
      such graph, exhaustive to 5 vertices.
  - **Memo**: `solvable_iff_of_cl_eq` says two sets with the same free closure are equally
    solvable under the invariant.
  - **Together**:
    - `Exec G k F M S Q o M′` is a big-step semantics of completed `false` runs with an
      abstract filter. It has four constructors: a memo hit; a node (`Q ← Q ∖ S`, any
      enumeration of `F S (Q∖S)`, record or not); an empty loop; and a child run with *any*
      subset of the `seen` entries that pass the test, after which the child joins `seen`.
      Old move off, memo off, `memo_limit` and every child order are special cases.
    - **`Exec.sound`**: for a node-sound, playable `F`, a genuine memo and genuine old moves
      give a genuine memo after the run, and every `false` answer is `¬ Sol_k(S)`. The proof
      is by induction on the run, i.e. on completion order. It is the §2.7 argument,
      mechanised.
    - `exec_root_sound`: from the root, `¬ Solvable G k ∅`.
    - **`exec_repairedFullFilter_sound`**: the whole search is sound — free moves, memo,
      old move, and `definite → subset → better` with both repairs in the code's order, for
      any `L`.
  - **Why the Python refuses** (`exec_fake_oldMove`). With one isolated customer, `k = 1`,
    `Q = {0}` and no pruning, the root run answers `false` and records the solvable state
    `∅`. So a node's run *on its own* is not a refutation. Soundness rests on `Q` being
    refuted earlier in the same run, which is a property of the run, not of the node. The
    combination therefore costs local checkability of memo entries (Cert:526–528's reason)
    and not soundness.
  - First compile: four local errors (anonymous-constructor parsing, a lemma behind
    `LinearOrder`, an instance argument, `fin_cases` unavailable). All were fixed in three
    rounds; no proof was abandoned.
- **Check before stating.** `python -m paper2.search_check --memo` takes 9 s on 28 cores and
  writes `paper2/data/search_memo_check.json`. Graphs: labelled graphs on 1–6 at every set,
  atlas 7 at the states, 400 random graphs at 8–11, and both `DEFINITE_CEX`. **Zero
  failures** in:
  - 76.3 M commutation cases;
  - 385 M reinsertion cases;
  - 7.8 M inheriting path steps;
  - 3.18 M memo-key groups;
  - 2.98 M instrumented search runs with old move and memo, under the 12 code filters
    (`fixed`, `L ∈ {0,1}`). Every answer equals the oracle, and the `Exec` invariant holds
    at every node entry and every record.

  Mutations:
  - without the test, the lemma's conclusion fails in 20.1 M cases;
  - inheriting every `seen` entry gives 257 false `unsat` in 248 k runs, the smallest on
    6 vertices (`INHERIT_ALL_CEX`).

  `tests/test_search_check.py` has five new tests, 42 in total, including a checker
  mutation (`inherit` → keep all is caught).
- **Docs.** `paper2/search_soundness.md`:
  - a result box at the top and the §4 bullet;
  - item 11 notes in §2.6, §2.7 (the claim is now proved) and §2.9;
  - new §4.5, covering definitions, theorems, what this does not cover, what Cert checks,
    and the check table.
- Gate: `lake build` ok; sorry 1 of limit 1 (the §24 conjecture); 1317 passed, 2 skipped,
  1 xfailed; GATE PASS.

### Blockers
- None for the item. What `Exec.sound` does not cover: the code's filter is not node-sound
  (items 08 and 10). For the code as it runs, the theorem is conditional: if its filter never
  loses the last solution at a node of the run, the answer is sound.

### Next
- Item 12 (`Search/Decide.lean`). Most of the abstract search now exists as `Exec`, and
  `exec_repairedFullFilter_sound` is its theorem for the repaired filter. What remains:
  - the MOSP and pathwidth corollaries via `searchSol_mospGraph_iff_mospValue_le` and
    `searchSol_empty_iff_pathwidth_add_one_le`; the active-subgraph remark of §4.1.3 if
    wanted;
  - for the code's filter, a named `Prop` (e.g. "the code's filter is node-sound at every
    node of the run") used as a hypothesis, with `Exec.sound` doing the rest;
  - §5 of `search_soundness.md`: the theorem, the Lean names, and the Cert premise table.
    Cert's `better` step certifies the code's premise, which `betterMove_counterexample`
    shows can be false.

## Iteration 12 — 2026-10-01 01:20

### Completed
- **12 Assemble. RESULT: the repaired search is proved sound end to end. A refutation means
  `mospValue > k` and `pw > k − 1`. For the code as it stands, the gap is a named `Prop`, used
  as an explicit hypothesis. There is also a checkable per-node condition under which the
  code's refutations are proved sound. FINDING: the code's own runs do reach nodes where its
  filter loses the last solution (58 of 570,206 runs, always at a satisfiable `k`), and every
  one still answered correctly.** New file `lean/MOSPFormalization/Search/Decide.lean`, about
  450 lines, imported from the root. No `sorry`, no new line in `allowed_sorries.txt`; axioms
  `propext`, `Classical.choice`, `Quot.sound` only (23 new lines in `paper2/axiom_check.lean`).
  - **The repaired search:**
    - `exec_repairedFullFilter_narrowness`: `k < narrowness`;
    - `exec_repairedFullFilter_pathwidth`: `k ≤ pw`;
    - `exec_repairedFullFilter_mospValue`: `k < mospValue M` on `mospGraph M`;
    - `exec_repairedFullFilter_mospGraph_pathwidth`.

    The chain is `Exec.sound` → Lemma F at the root → `narrowness_eq_pathwidth_add_one` →
    `mospValue_eq_pathwidth_add_one`.
  - **The code (`codeFullFilter`):**
    - `ExecOn N` is `Exec` with every expanded node satisfying `N`. `ExecOn.sound` needs
      node soundness (`NodeSoundAt`) only at the run's nodes.
    - The gap is named `CodeRunSound G k L M′`: the run expands only nodes where the code's
      filter keeps a solution. `codeExec_sound_of_runSound` and its pathwidth and MOSP
      corollaries are proved under it.
    - The instance-wide form is `CodeFilterSound`. `not_codeFilterSound_cexGraph` (via
      `codeFullFilter_cex`, every `L`) shows it is false on `cexGraph` at `k = 6`.
    - The checkable condition is `CodeNodeRepaired`: if the definite move fires, its pick is
      hereditarily definite; if not, every better-move drop has some repaired earlier
      citation. `nodeSoundAt_codeFullFilter_of_repaired` proves it gives node soundness, and
      `codeExec_sound_of_repaired` / `codeExec_mospValue_of_repaired` lift it to the run.
  - **Cert's node check:**
    - `Covered`, an inductive for chains of cited links that end in a child or `Q`.
    - `nodeSoundAt_of_covering`: sound links plus every candidate covered give node
      soundness. This is Cert's step 5.
    - `definite_link`: the definite move's links `Sol(S·r) → Sol(S·q)` under the repaired
      premise.
  - Compile: two heartbeat timeouts (fixed with explicit `(N := …)`), one `Covered`
    parameter error. No proof abandoned.
- **`paper2/search_soundness.md` §5:**
  - the theorem table;
  - the named gap and the conditional theorems;
  - why the run-local hypothesis is vacuous at refutations. Every expanded node is reachable
    by playable moves, so `¬Sol(∅)` makes every node sound, and a false refutation needs
    `Sol(∅)` plus a loss on every solution branch;
  - **the Cert premise table**: each of Cert's six checks mapped to its Lean lemma.
    **Two checks, definite (Cert:602–616) and better (Cert:628–640), verify the code's
    premise, not the repaired one the lemma needs.** A Cert verdict is a full proof only for
    certificates whose definite and better steps meet the repaired premises;
  - the check, and a summary for the paper.

  New result box at the top and an updated §5 bullet. Cert is not changed: the owner's fix
  decision covers it.
- **Python.** `python -m paper2.search_check --decide` takes 152 s on 28 cores and writes
  `paper2/data/search_decide_check.json`. It covers:
  - labelled graphs to 6, with pw by layouts to 5;
  - atlas 7;
  - 3,000 random graphs at 8–12;
  - 4,000 augmented definite counterexamples at 14–17;
  - `DEFINITE_CEX`.

  **Zero failures** across:
  - the repaired search answer against the oracle (570,206 runs);
  - `k < pw + 1` on 6,132 refutations;
  - `CodeNodeRepaired ⇒ NodeSoundAt` (1,781,000 nodes);
  - the `ExecOn` invariant in every run with no lost node;
  - the pinned Lean claims.

  The code's search gave zero wrong answers. It reaches a lost node in 58 runs (29 augmented
  graphs × 2 `L`, the smallest with 14 customers, pinned as `RUN_LOST_CEX`), all at
  `k = opt`, all recovered. In 26 of them the false `seen` entry cascaded to 83 nodes with a
  non-refuted `Q`, with no effect on the answer. `tests/test_search_check.py` has 5 new tests
  (47 collected), including a checker mutation (vacuous `CodeNodeRepaired` gets caught).
- Gate: `lake build` ok; sorry 1 of limit 1 (the §24 conjecture); 1322 passed, 2 skipped,
  1 xfailed; GATE PASS.

### Blockers
- None for the item. Not formalised:
  - the active-subgraph remark (customers with no product), argued in §4.1.3;
  - that Cert's Python computes the quantities the table names. That is a reading, backed by
    item 06's node-for-node agreement with the C, not a proof.

  Open, as before: whether the code ever gives a whole-instance false refutation.

### Next
- Item 13 (reserve). Candidates, best first:
  1. Hall's converse, matching ⇔ repair, in Lean (item 08's open half). It would make the
     cheap matching test a proved equivalent of `IsHereditarilyDefinite`, which is what the
     solver fix and a strengthened Cert would compute.
  2. A hunt for a whole-instance false refutation by the code, seeded by `RUN_LOST_CEX` and the
     58 lost-node runs: perturb these until the recovering branch also loses.
  3. Pebbling in `paper2/figures/equivalence_chain.dot` (item 04's note).
