# loop0006 progress

Plan: `paper2/plan.md` section 4 (phase B) and the complex (phase A); items in
`iterations.md`; rules in `TASK.md`. Gate: `python3 Ralph_Loops/loop0006/gate.py`.

Current: 1/13 SOLVED

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
