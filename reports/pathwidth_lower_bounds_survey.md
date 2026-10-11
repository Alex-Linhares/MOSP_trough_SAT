# Lower bounds for pathwidth: a survey, and the bound that closes myciel6

*2026-10-11. Scratch code and raw output: `reports/scratch/pw_lower_bounds/`.
Every computation was run on one or two cores while the machine was loaded
(load average 30–65 on 32 cores), so the wall-clock times are noisy. Node
counts are not affected.*

## 0. Summary

1. **There is a cheap pathwidth bound that certifies myciel6 exactly: the
   exact pathwidth of a contracted minor.** Pathwidth is minor-monotone. We
   contract myciel6 (95 vertices, pathwidth 38) down to 58 vertices, always
   contracting a minimum-degree vertex into its minimum-degree neighbour (the
   min-d rule). The search in `pathwidth_solver` then refutes pathwidth ≤ 37
   on the minor in 21,108 nodes, well under a second. That proves
   `pw(myciel6) ≥ 38`.
   - Our current bound is 25, and on the full graph the refutation of 37 had
     not finished after 1.7 × 10⁹ nodes.
   - On the 60-vertex minor the refutation holds with every dominance rule
     switched off (182,655 nodes, memo only), on the Python reference path,
     and under the published rules. On the 58-vertex minor CaDiCaL refutes it
     independently. Section 4.1 gives the details.
   - The idea is not new. Bodlaender, Koster and co-authors use "contract, then
     solve exactly" as a lower bound for treewidth (BK 2010 TR §5, p. 10;
     BFKKT 2006). Tamaki (2022) certifies treewidth by minors. The MOSP side of
     this repository already has it as `satisfiability/relaxation.py`.
   - What is new here is the measurement. For pathwidth the method is *not*
     capped by treewidth: tw(myciel6) = 35, and the minor proves 38. On
     myciel6 it also turns a refutation that does not finish into one that
     takes a fraction of a second.
2. **Every other family is capped below 38 on myciel6.**
   - Treewidth bounds are capped at 35, the exact treewidth (Tamaki 2017,
     Table 4). The best published treewidth lower bound is 29 (LBP+,
     Bodlaender–Wolle–Koster 2006, Table 19).
   - Harper's isoperimetric bound, the one pathwidth argument we had, is at
     most 34 at any depth: local search found sets of every size with smaller
     boundary.
   - The spectral and LP bounds give 3–11.
3. **Coudert, Mazauric & Nisse used no lower bound at all for myciel6**
   (Section 3). Their branch and bound prunes only on the current prefix cost
   reaching the upper bound. It wins through its prefix table:
   - 10,497,628 stored prefixes of length up to 40, solved in 10 minutes;
   - 14 minutes with prefixes up to length 30;
   - no answer after one month with prefixes up to length 20 (JEA 2016 §4.3,
     PDF p. 17).

   There is nothing Mycielski-specific in their method. They close by asking
   for "lower bounds for pathwidth that are not lower bounds for treewidth"
   (p. 19), which is what the minor bound is.
4. **Recommendation** (Section 6). Put a minor-refutation step into the
   `pathwidth_solver` descent, and offer the same step to `_lower_bound` on the
   MOSP side.
   - Before refuting `UB − 1` on the full graph, contract to a sequence of
     sizes (about n/2, growing by 5–10% per step) with min-d and least-c.
   - On each minor, refute `UB − 1` under a node budget that grows with the
     minor's size.
   - A refutation on any minor ends the descent with proof "bound". On
     myciel6 the whole step costs under a second.
   - On the MOSP corpus the same step closes four of the seven weakest
     instances tried, in 1–80 s each (Section 5):
     - Random-125-125-2-1_0, recorded at 1.6 × 10¹¹ nodes;
     - Random-125-125-2-3_0, recorded at 1,128 core-hours;
     - Random-125-125-6-1_0;
     - SP4.

     It brings two more within 1–3 of the optimum. It does not help the open
     Random-125-125-2-2_0.
5. **myciel7** (M8, open in CMN at pw ≤ 72) gets a new proved lower bound:
   pw ≥ 71, from a 110-vertex minor in 2.3 M nodes and 3 s (Section 4.2).
   So pw(myciel7) ∈ {71, 72}.
6. **An independent check of the myciel6 certificate.** A SAT refutation of
   width 37 on the 58-vertex minor took 1,459 s and shares no code with the
   search (Section 4.1).

---

## 1. The landscape

"tw" means the bound is a lower bound on treewidth, and therefore capped by
treewidth: on any graph with `pw > tw` it cannot be tight. "pw" means it is a
genuine pathwidth (vertex separation) argument. All values are in pathwidth
units (MOSP = pw + 1). The two right-hand columns are for myciel5 (47 vertices,
236 edges, pw 20, tw 19) and myciel6 (95 vertices, 755 edges, pw 38, tw 35).
"ours" marks a value computed in this sweep; anything else is quoted from the
source given.

| # | name | statement | source (page) | tw / pw | cost | myciel5 (20) | myciel6 (38) |
|---|---|---|---|---|---|---|---|
| 1 | clique | pw ≥ ω − 1 | folklore; Yanasse 1997a Cor. 2 | tw | NP-hard exact, time-boxed | 1 | 1 (triangle-free) |
| 2 | δ, δ₂, γ_R | tw ≥ γ_R ≥ δ₂ ≥ δ, where γ_R is the minimum over non-adjacent pairs of the larger degree | BK 2010 TR §3.1 Lemma 7, p. 5; Ramachandramurthi 1997 | tw | linear | 5 (δ) | 6 (δ) |
| 3 | degeneracy (MMD) | max over subgraphs of δ | BK TR §4.1 Lemma 13, p. 6; = Yanasse et al. 1999 LB4 | tw | linear | 8 (ours) | 12 (ours) |
| 4 | contraction degeneracy (MMD+) | max over minors of δ, by heuristic | BK TR §5 Alg. 3, p. 9; BWK 2006; = Yanasse et al. 1999 LB5 | tw | O(n³) | 14 (ours) | **25** (ours; our current bound) |
| 5 | minor-min-width | MMD+ variant | Gogate & Dechter 2004, §4, Table 4 | tw | O(n³) | 14 | 23 |
| 6 | MCSLB / MCSLB+ | max visited neighbours in an MCS order, optionally with contractions | Lucena 2003; BK TR §7 Thm 21, p. 11 | tw | O(n·m) per order | 8 / 14 (ours) | 13 / 25 (ours) |
| 7 | LBN / LBP (+) | improved graph: if `v, w` have ≥ k+1 common neighbours (or disjoint paths), adding `vw` keeps tw ≤ k | Clautiaux et al. 2003; BK TR §8 Thm 25–26, pp. 12–14; BWK 2006 Table 19, p. 49 | tw (the common-neighbour lemma also holds for pw, §2.1) | seconds to minutes | 16 (LBP+(MD)) | **29** (LBP+(MD), 1.9 s) |
| 8 | girth + average degree | tw ≥ max(d̄/2, (d̄−1)^⌊(g−1)/2⌋/(4e(g+1)) − 2) | Chandran & Subramanian 2005; BK TR Thm 8, p. 5 | tw | polynomial | ≈5 | ≈7 |
| 9 | spectral (treewidth) | tw ≥ 3nλ₂/(4Δ+8λ₂) − 1; improved to nλ₂/(Δ+λ₂) − 1 | Chandran & Subramanian 2003; Gima et al. 2025 eq. (2), p. 2 | tw | one eigenvalue | 3 / 6 (ours) | 5 / 9 (ours) |
| 10 | brambles (heuristic) | layered bramble of order min(c+1, β−α) | Bodlaender, Grigoriev & Koster 2008; BK TR §9, pp. 15–17 | tw | flows | not computed; poor on dense non-planar graphs (BK TR Table 1, p. 20) | not computed |
| 11 | exact treewidth | tw itself | Tamaki 2017 Table 4, p. 18 (PID, 419 s on myciel6); Gogate–Dechter Table 4 | tw (the ceiling) | exponential | 19 | **35** |
| 12 | spectral vertex separator applied to layouts | at each cut, \|X\| ≥ 4λ₂\|A\|\|B\|/(Δn − λ₂\|A∪B\|) | Mohar & Poljak 1993, via Díaz–Petit–Serna 2002 Thm 9.4, p. 339 | **pw** | one eigenvalue | 8 (ours) | 11 (ours) |
| 13 | spectral edge bisection | vs ≥ ⌈EB/Δ⌉ with EB ≥ λ₂n/4, or the stronger bounds of Bezrukov et al. | DPS 2002 Thm 9.2, p. 339; Bezrukov et al. 2004 Thm 1 | **pw** | one eigenvalue | 3 | 3 |
| 14 | isoperimetric (Harper) | pw ≥ max_s b_v(s, G), the minimum boundary of an s-set | Harper 1966; Chandran & Kavitha 2006 Thm 1, p. 361; our `expansion_bound.py` | **pw** | exact b_v is NP-hard; ours computes f(t) exactly to t ≤ 10 | 13 (ours, t ≤ 10); **at most 18** at any depth (ours, local search) | 14 (ours, t ≤ 10); **at most 34** at any depth |
| 15 | expansion (treewidth form) | tw ≥ N_min(G, s) − 1, over sets of size s/2..s | Chandran & Subramanian 2005; BK TR §10.3 Thm 30, p. 17 | tw | polynomial for fixed s | ≤ row 14 | ≤ row 14 |
| 16 | LP / MIP relaxations | linear-ordering MIP; position- and set-based MIPs have LP bound 0 | Mallach 2018, Table 1, p. 163 | **pw** | LP solves, seconds to minutes | 6.875 → 7 | not reported |
| 17 | cut-vertex branch rule / Lemma A | three branches of pw ≥ k at a cut vertex or separator force k+1 | Fellows & Langston 1987 L. 4.3; Kinnersley 1992 Cor. 4.2; ours, `ml_nature.md` §38 | **pw** | recursion over separators | no cut vertex (connectivity 5) | no cut vertex (connectivity 6) |
| 18 | blockages | blockage of order n ⇔ pw > n (exact duality, no algorithm) | Bienstock, Robertson, Seymour & Thomas 1991 (2.1), p. 2 | **pw** | certificate only | — | — |
| 19 | obstruction sets | forbidden minors; known for pw ≤ 2 (110 graphs) and for acyclic obstructions | Kinnersley & Langston 1994; Takahashi, Ueno & Kajitani 1994 | **pw** | only small k | — | — |
| 20 | search games | node search = pw + 1, edge search between vs and vs + 2 | Kirousis & Papadimitriou 1986; Ellis, Sudborough & Turner 1994; ours, `Complex/` | **pw** (equalities, not bounds) | as hard as pw | — | — |
| 21 | special families | exact pw for trees (Ellis et al. 1994), grids and tori (Ellis & Warren 2008), hypercubes (Chandran & Kavitha 2006) | see `paper2/survey_*.md` | **pw** | closed form | — | — |
| 22 | **exact pw of a contracted minor** | pw(H) ≤ pw(G) for every minor H; contract greedily, solve H exactly | BK TR §5 "Contraction with exact algorithms", p. 10, and BFKKT 2006 (for tw); Tamaki 2022 (certified minors, tw); Chu & Stuckey relaxation (MOSP, `relaxation.py`) | **pw** | one exact solve on a smaller graph | **20** at 35 vertices (0.0 s) | **38** at 58 vertices (21,108 nodes) |

Notes on the table:

- Row 4: BWK 2006 Table 9 (p. 40) reports 24–26 for MMD+ on myciel6, depending
  on the contraction strategy.
- Rows 9, 12 and 13: the spectral bounds are weak on Mycielski graphs because
  the hub has degree n/2: λ₂ = 5.68 and Δ = 47 on myciel6. Deleting the hub
  first does not help: removing the hub (pw drops by at most 1) leaves Δ = 46
  and the bound goes down, to 9 on myciel6.
- Row 11: tw(myciel7) is at least 52 (BWK Table 19) and at most 54 (QuickBB,
  Gogate–Dechter Table 4).
- Row 14: the "at most" values are upper bounds on the full isoperimetric value
  max_s b_v(s), found by simulated annealing over all s
  (`harper_ceiling.py`, `harper_peak.py`). They mean no implementation of
  Harper's method can exceed them, at any depth.
- Row 22: section 4.1 gives the size sweep. The source of the min-d and least-c
  rules is BWK 2006.

### 1.1 What the families have in common

- **Degree-based (rows 1–8, 10, 11, 15).** These are all treewidth arguments:
  they bound the degree, a bramble or a balanced three-way separator of a
  *tree* decomposition. The project already showed (`ml_nature.md` §6, §24)
  that they cannot pass `tw + 1`.
  - The improved-graph rule (row 7) is the strongest of them in the
    literature, and it reaches 29 on myciel6.
  - Its key lemma transfers to pathwidth (§2.1), but the bound it drives
    (MMD+, MCSLB) is still a treewidth bound.
- **Spectral (rows 9, 12, 13).** Rows 12 and 13 are genuine pathwidth
  arguments: a prefix cut is a two-way separator, not a three-way one.
  - They measure global expansion through λ₂/Δ, and on graphs with a
    high-degree hub (Mycielski) or sparse random structure (the Chu & Stuckey
    corpus) that ratio is small.
  - They give single digits here. Bezrukov et al. (2004) sharpen the edge
    bisection bound for regular, expanding graphs; neither condition holds on
    our graphs.
- **Isoperimetric (rows 14, 15).** Harper's argument is the strongest
  single-cut pathwidth bound: every layout has a prefix of every size, and
  b_v(s) is the cheapest boundary any s-set can have.
  - It is exact on symmetric graphs (`paper2/survey_products_structured.md`
    §6).
  - On myciel6 it cannot exceed 34: the local search exhibits, for every s,
    a set whose boundary is at most 34.
  - The pathwidth layout must *nest* its prefixes, and a single-cut argument
    ignores nesting. Nesting is what lifts 34 to 38.
- **LP / MIP (row 16).** Mallach proves that the classical position- and
  set-assignment MIPs have LP bound 0 on every graph. His linear-ordering MIP
  gets 6.875 on myciel5. CMN cite Solano & Pióro for "the Mycielski graph is
  considered as a hard instance for integer programming formulations" (JEA
  2016, p. 15). No SDP bound specific to vertex separation was found. The
  Feige–Hajiaghayi–Lee SDP (held) bounds balanced vertex separators, which is a
  row-12/14 kind of bound, with an O(√log n) gap.
- **Branching and structure (rows 17–21).** These are exact theories (trees,
  grids, blockages, obstructions) or recursions over cut vertices and
  separators. The project tested three branching candidates in
  `learning/bound_harness.py` (§38), and they beat nothing. Mycielski graphs
  have connectivity 5–6 and diameter 2, so they have no small separators to
  recurse on.
- **Minors plus an exact solver (row 22).** This is the only family that is a
  pathwidth argument (pathwidth is minor-monotone), sees nested structure (it
  *is* pathwidth, on a smaller graph), and is cheap. Its cost is one exact
  search on the minor, so it inherits whatever makes our search fast on graphs
  of 50–75 vertices.

## 2. Notes on individual bounds

### 2.1 The improved-graph lemma holds for pathwidth

Clautiaux et al.'s lemma states: if `v` and `w` are non-adjacent and have at
least `k + 1` common neighbours, then `tw(G) ≤ k ⇔ tw(G + vw) ≤ k` (BK TR Lemma
24, p. 12). The same holds for pathwidth.

Take a path decomposition of width `k`. The bags containing `v` form an
interval `I_v`, and those containing `w` form an interval `I_w`. If they were
disjoint, say `I_v` left of `I_w`, then every common neighbour `x` needs a bag
meeting `I_v` and a bag meeting `I_w`. So `x` is in every bag between them,
including the last bag of `I_v`. That bag would then hold `v` and all `k + 1`
common neighbours, which is `k + 2` vertices: a contradiction. So `I_v ∩ I_w ≠
∅`, and adding `vw` costs nothing.

LBN therefore has a pathwidth form, LBN_pw(X), driven by any pathwidth bound X.
`expansion_bound.md` §1 reports that LBN+ with MMD+ gains nothing on the
corpus. With a pathwidth X, such as the minor bound of row 22, the improved
graph could make minors denser at the same size. This is untested.

### 2.2 Harper's bound is capped below pw on both Mycielski graphs

`reports/scratch/pw_lower_bounds/harper_ceiling.py` and `harper_peak.py` do the
following:

1. For every s, seed with the best prefix of 200 greedy layouts.
2. Anneal for 6,000 moves.
3. Near the peak, anneal from random starts for 150,000 moves × 4.

The best boundary found for each s caps `b_v(s)` from above.

| | pw | max_s (best boundary found) | at s | our exact expansion bound, t ≤ 10 |
|---|---|---|---|---|
| myciel5 | 20 | **18** | 31–33 | 13 |
| myciel6 | 38 | **34** | 62–68 | 14 |

So deepening the expansion cap, the only lever `expansion_bound.md` §5 left
open, cannot reach the optimum on these graphs. In the corpus terms of
`expansion_bound.md` §4a: Mycielski graphs behave like the sparse density-2/4
instances.

### 2.3 Spectral

These are cheap (one eigenvalue) and weak wherever the maximum degree is far
above λ₂.
- Myciel6 has λ₂ = 5.68, Δ = 47 and λ_n = 48.7.
- Gima et al. (2025) give the best treewidth version, nλ₂/(Δ+λ₂) − 1 = 9.25.
- The pathwidth version through Mohar–Poljak (row 12, maximised over the cut
  position, `spectral_mcs.py`) gives 11.

Not worth a code path.

## 3. Pathwidth-specific bounds in the exact solvers

| solver | lower bound it uses | source |
|---|---|---|
| Coudert, Mazauric & Nisse, BAB-GPP (SEA 2014, JEA 2016; SageMath `vertex_separation`) | **none.** The search prunes when ν(P) ≥ UB, keeps a prefix table (Lemma 7, PDF p. 9) and greedy steps (Lemma 6, p. 9). SageMath's BAB accepts a caller-supplied `lower_bound` only to stop early. Default prefix length min(n/3, 50) in the paper (p. 13); SageMath's default `max_prefix_length=20`, `max_prefix_number=10⁶` | JEA 2016 §3.2, Alg. 3 (p. 14); SageMath docs |
| Kobayashi, Komuro & Tamaki (SEA 2014) | none: descend from a greedy upper bound with commitments and a failure table; TreewidthLIB treewidth lower bounds are quoted only as context | SEA 2014 §5, p. 396 |
| Kitsunai et al. (Algorithmica 2016) | none (exact DP over commitments) | — |
| Bannach & Berndt, PID for node search (WADS 2019; Algorithms 2022) | **bottom-up**: start at k = 1 and increase; PID is "especially suited to compute lower bounds" because refutations are its cheap side | Algorithms 2022, p. 8 |
| Lodha, Ordyniak & Szeider SAT (2017) | bottom-up from ω = 0; a time-out at ω gives ω − 1 as a lower bound | SAT 2017, §6 |
| Biedl et al. ILP/SAT (GD 2013) | "obvious lower bounds in O(n)", then iterate upward | GD 2013, §4 |
| Mallach MIP (2018) | the LP relaxation of the linear-ordering MIP (row 16) | JDA 2018 |
| Fraire-Huacuja et al. ILP + B&B (2016) | not held | — |
| Ours, `pathwidth_solver` | max(degeneracy, MMD+), `pathwidth/bounds.py` | — |

So **no published exact pathwidth solver uses a pathwidth lower bound beyond
the trivial**. The two families split as follows:
- top-down solvers (B&B, ours) prove optimality by an exhaustive refutation at
  `UB − 1`;
- bottom-up solvers (PID, SAT/ILP iteration) prove the lower bound by
  refutations at every value below the answer.

CMN end their paper by asking for exactly what is missing (JEA 2016 §5, p. 19):
"lower bounds for pathwidth that are not lower bounds for treewidth would be
very interesting".

### 3.1 How CMN proved myciel6

This is from JEA 2016 §4.3 (PDF pp. 15–17) and RR-8470 §4.4. Their names are
shifted by one from DIMACS: their M6 is our myciel5, and their M7 is our
myciel6.

- **No lower bound, no Mycielski-specific rule.** BAB-GPP is the generic
  algorithm: greedy steps (Lemma 6), branching in increasing ν(P′v), and
  pruning by the prefix table.
- **The prefix table is the whole story.**
  - On M6 (47 vertices), Table 2 (p. 17) shows the prefix-length cap decides
    everything:

    | max prefix length | time | visited nodes | stored prefixes |
    |---|---|---|---|
    | 1 | 2,226 s | 1.26 × 10⁹ | 44 |
    | 5 | 145 s | 8.2 × 10⁷ | — |
    | 10 | 1.07 s | 664,677 | — |
    | 15 | 0.77 s | 496,482 | 65,252 |

  - On M7, quoting p. 17: "While the algorithm was not able to return a
    solution after one month of computation when restricting the size of the
    prefixes to 20, we got the optimal solution in 14 minutes storing
    10 496 595 prefixes of size up to 30, and in 10 minutes storing 10 497 628
    of size up to 40." The default cap min(n/3, 50) = 31 for n = 95.
- **What that implies for us.** Their table is a memo keyed on the prefix *set*
  (Lemma 7), the same object as our failure memo of closed sets. Our C memo
  holds at most `memo_limit` = 4 × 10⁶ states by default (`native.py`, the
  `memo_limit` default; `closing_search_w.c` `memo_add` stops admitting when
  full), and admits states first-come in post-order.
  - We measured how much the cap matters on the myciel6 minors. Refuting
    pw ≤ 37 on the 75-vertex minor takes 7.46 / 7.24 / 6.53 / 6.27 million
    nodes with memo limits 0.1 / 1 / 4 / 20 million states.
  - On the 80-vertex minor it takes 64.3 / 63.9 / 61.4 million nodes.
  - So the cap is a 5–20% effect at those sizes, not the factor of 10⁴ that
    separates CMN's 10 minutes from our > 90.
  - We did not identify the remaining difference: tie-breaking, which CMN show
    matters a great deal (p. 18), or admission by prefix length. The
    minor-bound route makes it moot for myciel6. For graphs where no small
    minor certifies, the measurement worth making is a memo that admits only
    `|S| ≤ L`, which is CMN's policy.
- Their M8 (our myciel7, 191 vertices) is open: pw ≤ 72 (Table 1, p. 15).

## 4. Mycielski graphs

**Known values.** No closed form for the treewidth or pathwidth of Mycielski
graphs was found, and the targeted searches (Section 7) turned up no theorem.
Computed values:

| DIMACS name | Mₖ | n | m | tw | pw | source |
|---|---|---|---|---|---|---|
| myciel3 | M4 | 11 | 20 | 5 | 5 | Tamaki 2017 Table 4; CMN Table 1 |
| myciel4 | M5 | 23 | 71 | 10 | 10 | same |
| myciel5 | M6 | 47 | 236 | 19 | 20 | Tamaki; Yuan; CMN |
| myciel6 | M7 | 95 | 755 | 35 | 38 | Tamaki (419 s); CMN (10 min) |
| myciel7 | M8 | 191 | 2360 | 52–54 (66 in other sources) | **71–72** (this report: ≥ 71) | BWK 2006 Table 19 (tw ≥ 52); Gogate–Dechter (tw ≤ 54); CMN (pw ≤ 72); §4.2 |

**pw − tw = 3 on myciel6.** The census in `ml_nature.md` §27 found no graph
with `pw − tw = 3` on 11 or fewer vertices. Myciel6 is a 95-vertex example, and
the gap grows along the family (0, 0, 1, 3, and at least 5 at M8, at least 17 if tw(M8) ≤ 54). So every
treewidth-type bound, LBP+, exact treewidth and `tw + 1` alike, is at least 3
short on myciel6.

**Why degree bounds fail.** The graphs are triangle-free (ω = 2) and have
diameter 2. The hub has degree n/2, and the degree distribution is wide
(myciel6: minimum 6, median 13, maximum 47, mean 15.9). Pathwidth is 0.4n,
about 2.4 times the average degree. Degeneracy (12) and MMD+ (25) are tied to
the average degree, the same saturation `expansion_bound.md` §1 found on the
dense corpus. Treewidth itself is 2.2 times the average degree, which is why
even LBP+ stops at 29.

**A bound that sees them** is the exact pathwidth of a minor (Section 4.1).
Contracting low-degree vertices removes the "padding": cheap vertices whose
orderings multiply the search tree but do not raise the width. What remains is
a dense core of about 60 vertices whose pathwidth is already 38.

### 4.1 The minor bound on myciel5 and myciel6

`reports/scratch/pw_lower_bounds/minor_exact.py` and `minor_myciel7.py` contract
greedily to `m` vertices: at each step a minimum-degree vertex is contracted
into either its minimum-degree neighbour (min-d) or the neighbour sharing
fewest neighbours with it (least-c). The minor is then solved with
`pathwidth.solve`. In the table, "=" means proved exactly, and "≤" means the
budget ran out.

| graph | m | min-d: pw(minor) | nodes | least-c: pw(minor) | nodes |
|---|---|---|---|---|---|
| myciel5 (pw 20) | 25 / 30 / 35 / 40 | 18 / 19 / **20** / 20 | instant | 17 / 18 / **20** / 20 | instant |
| myciel6 (pw 38) | 40 | 32 | instant | 30 | instant |
| | 50 | 35 | instant | 34 | instant |
| | 52 / 54 / 56 | 36 / 36 / 37 | 1.3k / 2.4k / 6.1k | 35 / 36 / 37 | 1.9k / 2.8k / 6.9k |
| | **58** | **38** | **21,108** | 37 | 13,611 |
| | 60 / 62 / 65 | 38 / 38 / 38 | 40k / 70k / 178k | 37 / 38 / 38 | — / 72k / 184k |
| | 75 | 38 | 6.5 M (5.7 s) | 38 | 6.5 M (4.7 s) |
| | 80 | 38 | 61 M (51 s) | 38 | 61 M (52 s) |
| | 85 | ≤ 38 (budget 180 s) | > 106 M | ≤ 38 | > 86 M |
| | 95 (the graph) | — | > 1.7 × 10⁹ (25 min, open) | | |

The refutation cost grows by about a factor of 10 per 5 vertices, and the
bound saturates at 58. The useful window is therefore wide, roughly 58–80
vertices, and the cheapest point is its bottom.

**Soundness of the 58- and 60-vertex certificates** (`minor_verify.py`,
`minor_sat.py`):

- The 60-vertex minor is checked structurally: 60 connected branch sets
  partition V(myciel6), and every minor edge is realised by a graph edge.
  The edge list and branch sets are in `myciel6_minor60.json`. The 58-vertex
  edge list is in `myciel6_minor58_edges.json`.
- pw ≤ 37 is refuted on the 60-vertex minor under every configuration tried:
  - the default (40,080 nodes);
  - `better_move` (39,191);
  - the published rules (40,080);
  - no old move (111,254);
  - no subset rule and no old move (117,755);
  - no definite move and no old move (167,504);
  - **every dominance rule off, memo only (182,655 nodes)**, which is sound
    without any dominance theorem, because a failed closed set fails by any
    path;
  - the Python reference implementation (42,631 nodes).
- pw ≤ 38 is satisfiable on both minors, so 38 is the minor's exact pathwidth.
  The SAT encoding of `pathwidth_solver/bench/myciel6_sat.py` (no symmetry
  breaking) confirms pw ≤ 38 on the 58-vertex minor in 61 s.
- **The same encoding refutes pw ≤ 37 on the 58-vertex minor in 1,459 s**
  with CaDiCaL 1.9.5 (60,935 variables, 196,310 clauses). This shares no
  code with the search. So `pw(myciel6) = 38` now has two independent
  certificates: a dominance-free memoised search and a SAT refutation, each
  on a minor, plus CMN's layout for the upper side. A DRAT log of that call
  would make it third-party checkable (`tools/drat-trim`).

### 4.2 myciel7

Myciel7 has 191 vertices and 2,360 edges. CMN Table 1 gives pw ≤ 72. Our
own run (`bench/results/coloring_w.csv`) has lower bound 42 and upper 72, with
the budget exhausted.

| m | min-d: pw(minor) | nodes | least-c: pw(minor) | nodes |
|---|---|---|---|---|
| 80 | 62 | 4.5 k | 58 | 2.7 k |
| 100 | 70 | 199 k | 67 | 159 k |
| **110** | **71** | **2.28 M (2.6 s)** | 70 | 1.77 M |
| 115 / 125 | ≤ 71 (pw ≤ 71 satisfiable in 9 k / 0.7 k nodes) | | same | |
| 120 | 71 | 77 M (130 s) | 71 | 89 M |
| 130 / 140 / 150 | width 72 found; refuting 71 out of budget (300 s probes) | 1.6–2.4 × 10⁸ | same | 1.5–2.4 × 10⁸ |

So **pw(myciel7) ≥ 71**, certified by the 110-vertex min-d minor. Its branch
sets are in `myciel7_minor110_branch_sets.json`. The refutation of pw ≤ 70
holds in the default configuration, with `better_move`, and under the
published rules (2.22–2.28 M nodes). With CMN's upper bound this gives
**pw(myciel7) ∈ {71, 72}**, against a previously published lower bound of 52
(the treewidth bound LBP+, BWK 2006 Table 19). The best treewidth upper bound we found is 54 (QuickBB, Gogate–Dechter 2004
Table 4). Tamaki 2017 and BWK 2006 list 66. So pw − tw ≥ 5 on myciel7, and
pw − tw ≥ 17 if the 54 is right.

Settling 71 against 72 needs a refutation of pw ≤ 71 on a minor of 130 or
more vertices. Those minors cost more than 10⁸ nodes, and the 300 s probes did
not finish. This is a good target for a longer single run.

## 5. The weakest corpus instances

`reports/scratch/pw_lower_bounds/corpus_minor.py` builds the MOSP graph
(`customer_inter.customer_graph`) and contracts it to 40/50/60/70/80% of the
customers with min-d and least-c. Each minor is solved with `pathwidth.solve`
under a 60 s budget. The table compares the result with what the project
already had, in MOSP units (pw + 1):
- MMD+ + 1 (the main component of `_lower_bound`);
- the expansion bound at cap 8;
- the stored `relaxation` lower bound in `solutions/*.json`, which comes from
  the customer-merging relaxation of `satisfiability/relaxation.py`.

A sweep up to 96% followed (`corpus_minor.py 90 0.84,0.88,0.92,0.96`). The
two instances that were open, or recently re-opened, were run with
`open_minor.py`: refute `value − 1` on minors of 70–105 customers, 120 s each.

| instance | n | optimum | MMD+ +1 | expansion (t = 8) | stored relaxation lb | **minor bound** | at m (rule) | time |
|---|---|---|---|---|---|---|---|---|
| Random-125-125-2-1_0 | 125 | 24 | 14 | 7 | 16 | **24 = opt** | 87 (min-d) | 46 s, 58 M nodes |
| Random-125-125-2-3_0 | 125 | 21 | — | — | 13 | **21 = opt** | 70 (least-c) | 1 s, 757 k nodes |
| Random-125-125-2-2_0 | 125 | ≤ 25 (open) | — | — | 16 | none: every minor ≤ 95 is satisfiable at 24; 100–105 out of budget | — | — |
| Random-125-125-4-1_0 | 125 | 57 | 27 | 26 | 46 | 54 | 100 (min-d) | 39 s; 105–120 out of budget |
| Random-125-125-6-1_0 | 125 | 81 | 40 | 63 | 71 | **81 = opt** | 120 (both) | 28 s |
| Random-125-125-8-2_0 | 125 | 93 | 52 | 84 | — | 92 | 115–120 | 1 s |
| SP4 | 100 | 53 | 27 | 37 | 47 | **53 = opt** | 96 (both) | 8 s |

For 2-1_0 the "time" column gives the time inside `corpus_minor.py`; the same
refutation takes 58,007,927 nodes and 80 s in the default configuration, and
45,692,798 nodes and 42 s with `better_move`.

Four of the seven are certified exactly by a minor. That includes the two
density-2 ridge instances that cost the project the most:

- **Random-125-125-2-1_0.** It was re-certified on 2026-09-25 with
  **162,268,751,357 nodes** (`solutions/Random-125-125-2-1_0.json`).
  - The 87-customer minor refutes 23 in **58 million nodes** (80 s, default
    configuration), a factor of about 2,800.
  - The minor was checked structurally: 87 connected branch sets that
    partition the customers, with every edge realised (`corpus_verify.py`).
  - The refutation holds with and without `better_move`.
  - With every dominance rule off, the memo-only refutation did not finish in
    900 s (2.2 × 10⁹ nodes). For this instance the certificate therefore rests
    on the same rules as the original refutation. Only the problem is smaller.
- **Random-125-125-2-3_0.** It was re-certified on 2026-10-09 by the root
  split: **4.25 × 10¹² nodes, 1,127.8 core-hours** (its solution file;
  `paper1/solver_fix_split.py`).
  - A 70-customer least-c minor refutes 20 in **757,009 nodes and about one
    second**.
  - The minor was checked structurally (70 connected branch sets, every edge
    realised).
  - The refutation holds in the default configuration (757,009 nodes),
    with `better_move` (680,839), and **with every dominance rule off, memo
    only: 6,932,452 nodes, 2 s.** MOSP ≤ 21 is satisfiable on the minor.
  - So the optimum 21 of Random-125-125-2-3_0 now has a certificate that
    needs no dominance theorem at all. It rests only on minor monotonicity,
    `MOSPGraph.lean`, and a plain memoised exhaustive search.

### 5.1 Independent SAT check of the corpus certificates

`corpus_sat.py` ran the graph SAT encoding with CaDiCaL 1.9.5, no symmetry
breaking, on the 70-vertex minor of 2-3_0 at width 19. It **did not finish in
the 60-minute cap**, and the 87-vertex minor of 2-1_0 was never reached. The
SAT path is therefore not yet an independent check for the corpus minors.

What stands:
- for 2-3_0, the dominance-free memoised refutation above;
- for 2-1_0, refutations under two rule configurations.

The next instruments to try:
- the §32 search certificate (`learning/search_certificate.py`), which handles
  graphs of this size;
- the direct MOSP SAT encoding on the *contracted instance*. Merging customers
  yields a MOSP instance with 70 customers and the original products.

The minor bound is a different object from `relaxation.py`, even though both
contract edges of the MOSP graph:
- relaxation.py merges by Chu & Stuckey's F(c) ranking, whose paper reports
  low-degree-first as "clearly worse";
- here plain min-degree-first (min-d, or least-c) contraction followed by an
  exact solve beats every stored relaxation bound: 24 vs 16, 21 vs 13, 54 vs
  46, 81 vs 71, 53 vs 47.

One caution on that comparison: the stored relaxation bounds came from the
fixed-target `lower_bound` driver at the sizes chosen then, so part of the
difference may be the size and not the merge rule.

Where the minor does not reach the optimum (4-1_0 at 54 of 57, 8-2_0 at 92 of
93), the gap is still much smaller than every other bound we hold. The cost
wall on the sparse 4-1_0 sits at about 100 customers, where
`relaxation.md` §4 found its knee too.

## 6. Recommendation

**Put the minor bound into the `pathwidth_solver` descent first, as a
budgeted refutation step rather than a stand-alone bound.**

`solve_masks` already ends with proof "bound" when the lower bound reaches the
width. The step:

1. After the upper bound `UB` is found, set `target = UB − 1`.
2. For `m` from about `max(target + 2, 0.5 n)` upward, in steps of
   `max(2, 0.05 n)`, and for each rule in min-d and least-c:
   - contract to `m`;
   - call `decide(minor, UB)` with a node budget `B_m`. `decide(masks, k)`
     asks whether pathwidth ≤ k − 1, so this asks whether the minor has
     pathwidth ≤ `target`;
   - on `unsat`, set `lower = UB` and return proof "bound".
3. Stop the step when the cumulative minor budget reaches a fixed fraction
   (say 5–10%) of the main refutation's budget, or when `m` reaches 0.85 n.

The node budget should grow geometrically with `m`, because the cost grows
about 10× per 5 vertices on myciel6.

Each minor refutation also yields a valid bound `pw(G) ≥ (the minor's refuted
value + 1)`, so a failed step can still raise `lower` for reporting, but the
descent only gains when the bound equals `UB` (`expansion_bound.md` §6). The
certificate is checkable without trusting our dominance rules: the branch sets
plus a memo-only refutation of the minor, or a SAT/DRAT refutation, since
minors of 58–75 vertices are within reach of the SAT path.

**Expected effect.**
- **myciel6**: closed. The upper bound reaches 38 quickly (the existing runs
  start at 39 and find 38). The minor step then certifies 38 at m = 58 in
  about 21,000 nodes, against a refutation on the full graph that had not
  finished after 1.7 × 10⁹ nodes.
- **myciel7**: see Section 4.2. The step will not close it, but it raises the
  proved lower bound.
- **The hard corpus** (Section 5): four of the seven weakest instances tried
  are closed outright by a minor, in 1–80 s each:
  - 2-1_0, against 1.6 × 10¹¹ nodes recorded;
  - 2-3_0, against 1,128 core-hours recorded;
  - 6-1_0;
  - SP4.

  Two more come within 1–3 of the optimum. The open Random-125-125-2-2_0 is
  not helped: every minor up to 95 customers is satisfiable at 24, so either
  its optimum is 25 and the certifying minor is larger than 100, or its
  optimum is 24. This is the strongest evidence in the project that the
  descent should try minors before the full refutation, on the MOSP side as
  well. **Before anything is recorded as certified, the two density-2
  certificates should be re-run through an independent path.** Candidates are
  the SAT path with DRAT on the minor, or the §32 search certificate on the
  minor. The graph SAT encoding refuted width 37 on the 58-vertex myciel6
  minor in 25 minutes. The corpus minors are larger (70 and 87 vertices) but
  the widths are smaller (19 and 22). Section 5.1 reports the attempt.

**For `_lower_bound` on the MOSP side**, the graph-contraction minor is a
different object from `relaxation.py`'s customer merging. relaxation.py merges
customers inside the MOSP instance, guided by the witness. Section 5 compares
the two. If the graph minor is stronger, the cheap change is to compute it on
the MOSP graph with the `pathwidth_solver` engine. It is sound by minor
monotonicity plus the `MOSPGraph.lean` equality, the same footing as
contraction degeneracy. It is a correctness dependency, as `lower_bounds.md` §5
insists, so it must be validated over the certified corpus before it goes in.
On the old evidence it shortens a proof only when it equals the optimum, so
it belongs in the same budgeted "try to close by a minor" step, not in the
always-on bound.

**Not recommended:**
- **exact treewidth** in `_lower_bound`: capped at 35 on myciel6, and on the
  131 corpus instances of `ml_nature.md` §6;
- **a deeper expansion cap**: capped at 34 on myciel6 by §2.2;
- **spectral and LP bounds**: single digits;
- **LBN/LBP with treewidth inner bounds**: at most 29 on myciel6.

**Worth a follow-up:**
- LBN with a *pathwidth* inner bound (§2.1);
- choosing minors guided by the upper-bound layout. relaxation.py's
  unmerge-by-witness idea fits here: split the branch set the witness layout
  survives worst;
- CMN's prefix-length memo admission, for graphs where no small minor
  certifies.

## 7. Literature searched

These are not held, or held only as a technical report. The fetch list with
DOIs and search links is in `literature/MISSING.md`, under "Pathwidth lower
bounds (2026-10-11)". Downloaded today:

- the Bodlaender–Koster survey (as TR UU-CS-2010-022);
- Bodlaender–Wolle–Koster (JGAA 2006, open access);
- Gogate–Dechter (UAI 2004, arXiv);
- Gima et al. (arXiv; IPL 2025);
- the TR versions of BFKKT 2006 (exact algorithms; contract-and-solve),
  Bodlaender–Grigoriev–Koster (brambles), Koster–Wolle–Bodlaender (degree
  bounds) and Bodlaender–Koster (MCS).

Web searches for "pathwidth Mycielski" and "treewidth Mycielskian" returned no
result on width parameters of Mycielski graphs. The numbers above come from
the experimental treewidth and pathwidth papers.

## 8. Reproduction

```bash
cd ~/dev/MOSP
python reports/scratch/pw_lower_bounds/basic.py            # rows 3, 4, 9, 14 (exact f to t<=10): ~5 s
python reports/scratch/pw_lower_bounds/spectral_mcs.py     # rows 6, 12, Gima: ~1 min
python reports/scratch/pw_lower_bounds/harper_ceiling.py   # §2.2 profile: ~10 s
python reports/scratch/pw_lower_bounds/harper_peak.py      # §2.2 peak: ~5 min
python reports/scratch/pw_lower_bounds/minor_exact.py 60   # §4.1 first sweep: seconds
python reports/scratch/pw_lower_bounds/minor_verify.py     # §4.1 certificate checks: ~1 min
python reports/scratch/pw_lower_bounds/minor_sat.py        # §4.1 SAT check on the 58-vertex minor
python reports/scratch/pw_lower_bounds/minor_myciel7.py 180  # §4.1 size sweep + §4.2
python reports/scratch/pw_lower_bounds/corpus_minor.py 60  # §5, 40-80%
python reports/scratch/pw_lower_bounds/corpus_minor.py 90 0.84,0.88,0.92,0.96 Random-125-125-8-2_0,Random-125-125-6-1_0,SP4,Random-125-125-4-1_0
python reports/scratch/pw_lower_bounds/open_minor.py 120   # §5, 2-3_0 and 2-2_0
python reports/scratch/pw_lower_bounds/corpus_verify.py Random-125-125-2-3_0 benchmarks/instances/MOSP_Instances/Chu_Stuckey/Random-125-125-2-3.txt 0 70 least-c 900
python reports/scratch/pw_lower_bounds/corpus_verify.py Random-125-125-2-1_0 benchmarks/instances/MOSP_Instances/Chu_Stuckey/Random-125-125-2-1.txt 0 87 min-d 900
python reports/scratch/pw_lower_bounds/myciel7_verify.py 600 115,125       # §4.2 certificate + probes
python reports/scratch/pw_lower_bounds/corpus_sat.py       # §5.1 (did not finish in 60 min)
```

Raw outputs are the `*.out` files next to the scripts. Nothing was written to
`solutions/`, the solver code or the paper.
