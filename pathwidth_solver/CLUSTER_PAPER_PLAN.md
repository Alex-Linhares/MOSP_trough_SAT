# Paper plan: "Pathwidth is a cluster of problems"

*Transferred on 2026-09-30 from `~/dev/pathwidth`; see `TRANSFER.md`. Superseded: its Lean items are done in Ralph
loop0005 (`lean/MOSPFormalization/Complex/`), and the current paper plan is `paper2/plan.md`. "This repo" below is now `pathwidth_solver/`.*

Draft 2026-09-28, for evaluation. Assets referred to: `~/dev/MOSP/paper2/` (Table 1 corpus, popularity
study, `table1.bib`), `~/dev/MOSP/lean/` (Lean 4 development), this repo (solver, benchmarks, literature).

## 1. Thesis

Twelve problems from operations research, VLSI design and graph theory, collected in Table 1 of
Linhares & Yanasse (2002), are one problem. The paper makes three claims and backs each with a
different kind of evidence:

| Claim | Evidence | Status |
|---|---|---|
| **C1. One cluster, one dominant name.** The twelve names denote the same quantity up to a stated constant; "pathwidth" is where the literature has gone. | Bibliometrics (OpenAlex): pathwidth 1,609 works, 27× MOSP, more than the other eleven together. *(Superseded 2026-09-29: relevant works, pathwidth 1,213 and MOSP 58; `paper2/popularity.md`.)* | Done (`paper2/popularity.md`), needs a refresh and a solver-literature cut. |
| **C2. The equivalences are theorems, and here they are, machine-checked.** For each entry: the published statement, the exact graph construction, the exact shift, and a Lean 4 proof. | The twelve source papers (11 held in full; Kashiwabara–Fujisawa 1979 unobtainable); Lean: vs = pw and MOSP = pw + 1 already sorry-free. | Partly done; the rest is §3. |
| **C3. One algorithm solves all of them.** An exact solver for any member is an exact solver for every member; concretely, Chu & Stuckey's closing-order search for MOSP, run on graphs, is the strongest exact pathwidth solver published. | Node-for-node identity with the MOSP implementation; benchmarks vs Coudert et al. (JEA 2016) and Kobayashi et al. (SEA 2014). | Done here for the plain Chu & Stuckey search; §4 lists the remaining runs. |

The MOSP repository also holds a *variant* of the search (learned branching, expansion prune, portfolio
bounds). **This paper tests only the plain Chu & Stuckey rules**; the variant is a separate paper.

## 2. The equivalence map, as the sources actually state it

Table 1 says "equivalent up to ±1". Reading the twelve sources gives three tiers, and the paper should
say so: it is the corrected Table 1.

**Tier A — exact equalities, all provable from one graph.** With `pw` the pathwidth and `G_M` the
graph of a 0/1 matrix `M` (rows adjacent iff they share a column: the MOSP graph / net graph):

| Problem | Statement | Source (held) | Lean |
|---|---|---|---|
| Vertex separation | vs(G) = pw(G) | Kinnersley 1992, Thm 3.1 | **done** `VSEquivPW.lean` |
| MOSP | MOSP(M) = pw(G_M) + 1 | Yanasse 1997a Prop 5; Fellows–Langston 1987 Lemma 4.1 | **done** `MOSPGraph.lean` |
| Gate matrix layout | tracks(M) = pw(G_M) + 1 | Fellows–Langston 1989 Thm 7; Möhring 1990 Thm 3.2 | same theorem, nets = rows: instantiate |
| One-dimensional logic | tracks = clique number of a min interval augmentation = pw + 1 | Ohtsuki et al. 1979 | via interval thickness below |
| Interval thickness θ | θ(G) = pw(G) + 1 | Kashiwabara–Fujisawa 1979 (not held); Möhring 3.4/3.5; Bodlaender 1998 | to do: interval graphs are not in Mathlib |
| Node search number | ns(G) = θ(G) (KP 1985); ns(G) = vs(G) + 1 (KP 1986 Thm 4.1) | Kirousis–Papadimitriou 1985 Thm; 1986 Thm 4.1 | to do: monotone search strategies ↔ layouts |
| Narrowness ν | ν(G) = pw(G) + 1 | Kornai–Tuza 1992 Prop 3.1 | to do: short, definitional |
| Black-white pebbling | mpb(G) = ns(G) (progressive) | Kirousis–Papadimitriou 1986 Thm 3.1; Lengauer 1981 Thms 2–4 (VSG ↔ PBWP with K−1) | to do; Lengauer's exact reading still to be pinned down |

**Tier B — sandwiches, not equalities.** The value is pinned to two consecutive numbers:

| Problem | Statement | Source |
|---|---|---|
| Split bandwidth sb | pw(G) ≤ sb(G) ≤ pw(G) + 1 (and sb = ib = m₁, the helicopter search number) | Fomin 1998 Thms 3, 6, 8 |
| Edge search number es | ns(G) − 1 ≤ es(G) ≤ ns(G) + 1; exactly, es(G) = ns(G_e) − 1 for a derived graph G_e | Kirousis–Papadimitriou 1986 §2, Thm 2.5 |

For Tier B a pathwidth solver gives a two-value interval directly, and the exact value by one further
computation (for es, run the solver on G_e). The paper states this rather than "equivalent".

**Tier C — variant-dependent.** *PLA folding*: Möhring 1990 §2 says the equivalence holds "for certain
variants" (block folding / restricted folding); general PLA folding is not in the cluster. Table 1's entry
needs qualification. To be read in full from the chapter obtained 2026-09-27.

Deliverable of §2: a table in the paper with, per entry, the construction, the shift, the source theorem
number, and the Lean theorem name. This is the "corrected Table 1" and is new: nobody has laid the twelve
side by side with exact shifts.

## 3. Lean work, in order of value per effort

Existing (`~/dev/MOSP/lean/MOSPFormalization/`, Mathlib master): `LinearLayout`, `VertexSeparation`,
`PathDecomposition`, `Pathwidth`, both directions of vs = pw (`VSEquivPW`, sorry-free), MOSP graph and
MOSP = pw + 1 (`MOSPGraph`, sorry-free), `Sandwich` (3 sorries: bandwidth/degeneracy bounds),
`Reduction` (4 sorries, the deprecated agreement-graph route — drop it from the paper).

1. **Gate matrix layout / one-dimensional logic = MOSP** — restatement: rows of `M` are nets, columns
   are gates; `tracks(M) = pw(G_M) + 1` is `MOSPGraph`'s theorem under renaming. Half a day.
2. **Narrowness = pw + 1** — Kornai–Tuza's in-sequence definition is a layout with a boundary count;
   Prop 3.1 is a rephrasing of vs = pw. One to two days.
3. **Interval thickness = pw + 1** — define interval supergraphs as `V → Set.Icc`-style intervals over a
   linear order; pw + 1 ≤ θ from a path decomposition read as intervals (each bag index is a point), θ ≤
   pw + 1 from maximal cliques of an interval graph ordered by left endpoint (Möhring 3.4). This is the
   central missing link; most Tier A entries route through it. One to two weeks.
4. **Node search number = pw + 1** — formalise monotone (progressive) node-search strategies as
   sequences of searcher sets; strategy ↔ layout (KP 1986 Thm 4.1's two constructions). Recontamination
   monotonicity (KP 1986 Thm 2.3, LaPaugh) is a real theorem; we only need the monotone version if we
   *define* ns via monotone strategies and cite non-monotone equivalence — decide with the user. Two weeks.
5. **Fomin's sandwich** pw ≤ sb ≤ pw + 1 and **KP's** ns − 1 ≤ es ≤ ns + 1 — statements plus one
   direction each are cheap; full proofs one week each. Optional for a first submission.
6. **Pebbling** (Lengauer, KP 1986 §3) — lowest priority; the definitions are the longest.
7. Stretch: **soundness of the search's dominance rules** (definite move = Tamaki's Commitment Lemma,
   depth 1; subset rule; old move). *Corrected 2026-10-03 (MOSP loop0008 item 03): only the repaired
   definite move is the Commitment Lemma, at depth close(q, S); depth 1 is the case open ≤ 1; the
   published rule is false. Done in `paper2/revised_algorithm.md` §4.3, §4.7.*. The MOSP repo's loop0004 already has "a proof object for the
   customer search". Would let the paper say the solver is verified, not just tested.

Sorry-free targets for submission: items 1–4. Everything else stated with citations.

## 4. Algorithmic work remaining (this repo)

Done: phases 1–3, 6, 6b; benchmark sweep (coloring, named, VSPLIB, Rome) with published comparisons.

1. Finish the multiword rerun (`bench/results/*_w.csv`, running) and fold it into the tables.
2. **Gate matrix layout instances** — the VLSI literature's small standard examples (Wing et al. 1985,
   Möhring's examples; the `v4470`/`w`-series used by Linhares 2002 and Faggioli & Bentivoglio) — as
   matrices they are MOSP files; run through both the MOSP and the graph solvers, report identical values.
3. **Node search / interval thickness demonstration** — no separate instances exist; report pw + 1 on
   the named graphs (Petersen, cages, Mycielski) as ns and θ, citing Tier A.
4. **Hard open cases** to try with more budget or better move: myciel6/7, anna, queen13–16, the cages.
   Report as open, with the certified bounds.
5. Reproducibility package: `bench/` + CSVs + instance manifests; note Rome and VSPLIB URLs and the
   TreewidthLIB archive that is no longer online.

## 5. Paper outline

1. Introduction: twelve names, one number; Table 1 revisited; contributions C1–C3.
2. The cluster: definitions, the corrected Table 1 with tiers A/B/C, proofs sketched, Lean references.
3. How popular is each name: the OpenAlex study (method, caveats, the "dead names").
4. One algorithm: closing-order search on the MOSP graph = vertex-separation search; the rules as
   commitments (Tamaki) and dominances (Chu & Stuckey); what the pathwidth solvers lacked (better move,
   old move) and what MOSP lacked (nothing; the depth-1 commitment was already there). *Corrected 2026-10-03: what MOSP
   had was a commitment with its interior condition dropped, which is false (`paper2/revised_algorithm.md` §4.7).*
5. Experiments: identity with the MOSP implementation; Rome 97.0 % vs 95.6 %; TreewidthLIB Table 4
   parity and speedups; VSPLIB parity plus grids 12–13 and 202-node trees; fpsol2.i.1 in 6 s vs 323 s;
   new exact values (queen11_11 = 87, queen12_12 = 103); open cases.
6. What the cluster view buys each community (MOSP gets pathwidth's lower bounds and FPT theory; VLSI
   gets a solver; graph searching gets instances and exact values).
7. Conclusion; PACE track proposal.

Venue: ACM JEA (first choice), INFORMS Journal on Computing (second); SEA/ALENEX for a short version.

## 6. Risks and open questions for evaluation

- **Tier B/C weakens the slogan.** "Twelve equivalent problems" becomes "eight exact, two within one, one
  variant-dependent, one duplicate". I think that is a *better* paper (it corrects the record), but the
  title should not overclaim. Decide: keep "cluster", and define it as "determined by pathwidth up to a
  constant, exactly for Tier A".
- **Kashiwabara–Fujisawa 1979** cannot be obtained; cite via Möhring/Bodlaender for interval thickness.
- **Lean scope.** Items 3–4 of §3 are the bulk of the formal work (interval graphs, search strategies
  are not in Mathlib). Decide whether the first submission needs them sorry-free or stated + cited.
- **Lengauer's entry.** Table 1 says "edge separation [14]"; Lengauer's paper is about the *vertex*
  separator game and black-white pebbling, with K−1 shifts. Needs a careful read; possibly Table 1 misnames it.
- **Novelty of C3.** The algorithm is Chu & Stuckey's; the paper's contribution is the recognition, the
  commitment analysis, the identity test, and the benchmarks. Say so plainly.
- **The MOSP variant.** Kept out of this paper on purpose; one sentence pointing to it.

## 7. Immediate next steps (proposed order)

1. Read Lengauer 1981 and Möhring §2 (PLA) to pin Tier A/C entries (1 day).
2. Lean items 1–2 (gate matrix layout, narrowness) (2–3 days).
3. Gate matrix layout instances through both solvers (1 day).
4. Lean item 3, interval thickness (1–2 weeks) — the paper's formal centrepiece.
5. Draft §§1–3 and 5 while item 4 runs.
