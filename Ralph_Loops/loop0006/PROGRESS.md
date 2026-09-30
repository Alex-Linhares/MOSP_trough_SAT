# loop0006 progress

Plan: `paper2/plan.md` section 4 (phase B) and the complex (phase A); items in
`iterations.md`; rules in `TASK.md`. Gate: `python3 Ralph_Loops/loop0006/gate.py`.

Current: 3/13 SOLVED

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
