# TODO

*Transferred on 2026-09-30 from `~/dev/pathwidth`; see `TRANSFER.md`. Its Lean items are done in Ralph loop0005
(`lean/MOSPFormalization/Complex/`; the dominance-rule stretch item was not in it), and the current paper plan is `paper2/plan.md`.*

Decisions recorded 2026-09-28: the tiered "cluster" framing stands (Tier A exact, Tier B sandwiches,
Tier C variant-dependent); all Lean statements are to compile sorry-free in due time, not necessarily for
the first submission; venue to be chosen later (JEA / INFORMS JoC are the candidates).

## Literature
- [ ] **Re-read Lengauer 1981** (`literature/lengauer_1981_black_white_pebbles_graph_separation.pdf` in the MOSP repository).
      Table 1 of Linhares & Yanasse labels it "edge separation [14]", but the paper is about the vertex
      separator game (VSG) and progressive black-white pebbling (PBWP), Theorems 2–4 with K−1 shifts.
      Pin down: what quantity Table 1 means by "edge separation", which theorem gives it, the exact shift
      to pathwidth, and which tier (A or B) it belongs to. Also check whether Kirousis–Papadimitriou 1986
      Thm 3.1 (mpb = ns) supersedes it for the paper.
- [ ] Read Möhring 1990 §2 on PLA folding: which variants (block / restricted folding) are in the cluster.
- [ ] Kirousis–Papadimitriou 1986 Thm 2.5: define G_e precisely (es(G) = ns(G_e) − 1).
- [ ] Fraire-Huacuja et al. 2016 (last item on the wanted list; minor).

## Lean (order from CLUSTER_PAPER_PLAN.md §3)
- [ ] Gate matrix layout = MOSP theorem under renaming.
- [ ] Narrowness = pw + 1 (Kornai–Tuza Prop 3.1).
- [ ] Interval thickness = pw + 1 (interval graphs not in Mathlib).
- [ ] Node search number = pw + 1 (monotone strategies ↔ layouts).
- [ ] Sandwiches: pw ≤ sb ≤ pw + 1; ns − 1 ≤ es ≤ ns + 1.
- [ ] Pebbling (Lengauer; KP 1986 §3).
- [ ] Stretch: soundness of the search's dominance rules.
- [ ] Clear the 3 sorries in `Sandwich.lean`; drop `Reduction.lean` (agreement graph) from the paper.

## Solver / benchmarks (PLAN.md)
- [ ] Phase 7.1: certified-minor lower bound (Tamaki 2022 Lift) — the tool for the remaining misses.
- [ ] Phase 7.2: component push (Kitsunai et al. Lemma 2).
- [ ] Phase 5: preprocessing (pendants, twins, tree components via Ellis–Sudborough–Turner).
- [ ] Gate matrix layout instances through both solvers.
- [ ] Longer runs on the open cases: myciel6/7, anna, queen13–16, cages, le450.

## Paper
- [ ] Corrected Table 1 (construction, shift, source theorem, Lean name per entry).
- [ ] Refresh the OpenAlex popularity study; add a solver-literature cut.
- [ ] Draft §§1–3, 5.
- [ ] Choose venue.
