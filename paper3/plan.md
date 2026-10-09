# Paper 3: MOSP on structured instances (plan)

Draft plan, 2026-10-09. Built from the four surveys in this folder:
- `survey_trees_sparse.md`;
- `survey_products_structured.md`;
- `survey_intersection_classes.md`;
- `survey_random_extremal.md`.

It follows paper 2, *The pathwidth complex*, which proved MOSP = pathwidth + 1
(with the rest of the Linhares–Yanasse table) and built an exact search and a
certified dataset. Paper 3 asks what that equivalence buys on the instances
that have structure.

## Working title

*Open stacks on structured instances: exact layers, formula benchmarks, and
random MOSP* (to be shortened).

## The question

**When does an open-stacks instance have structure that makes its optimum
computable without search, provable by formula, or predictable in
expectation, and what do the pathwidth results for special graph classes say
about MOSP?**

There are three answers, one per part. The audience is OR first, since MOSP is
the application, and graph theory second, since the classes and formulas come
from there. Every graph result is translated into MOSP vocabulary.

## Part 1. Exact layers before search

A MOSP graph that falls in a known class is solved exactly, fast, before any
search.
- **Interval graphs:** the optimum is ω, the largest clique (Bodlaender 1998,
  Thm 29). Verified on all 2,524 interval instances of the corpus.
- **Cographs:** pw = tw, given by the join formula pw(G×H) =
  min(pw(G)+|H|, pw(H)+|G|) (Bodlaender & Möhring 1990, Lemma 3.4). Verified on
  all 2,573 cograph instances.
- **The complement-split rule.** If the complement of the MOSP graph has pieces
  G_i, then MOSP = min_i (MOSP(G_i) + n − |V_i|). This is an exact
  preprocessing step that is not among Yanasse & Senne's six. It applies to
  4,250 of 6,376 corpus instances (33 of them Chu & Stuckey), and on 1,609
  distinct graphs it shrinks the hardest piece. For example,
  `Random-50-100-10-2` goes from 50 customers to 6.
- **AT-free graphs:** pw = tw (Möhring 1996), so treewidth solvers apply. In the
  corpus, every one of the 375 instances with pw > tw has an asteroidal triple,
  and tw + 1 = optimum on all 2,830 AT-free instances with exact treewidth.
- **Block graphs:** polynomial (Chou et al. 2008, read second-hand). Our
  observation: an instance whose customer–pattern incidence graph is a forest
  has a block graph as its MOSP graph. That is the "trees of cliques" family
  that defeats every lower bound in `_lower_bound` (`reports/ml_nature.md` §6).
- **Circular-arc graphs:** O(n²) (Suchan & Todinca 2007), even though pw ≠ tw.
- **Trees and unicyclic graphs:** linear time and O(n log n) (Ellis,
  Sudborough & Turner 1994; Markov).

**The hardness side**, in MOSP vocabulary:
- chordal graphs, which Möhring's reduction makes into a MOSP instance with one
  pattern per maximal clique;
- bipartite, cobipartite, cocomparability and distance-hereditary graphs;
- planar graphs of maximum degree 3;
- weighted trees and octopus graphs (Mihai & Todinca 2009).

Hardness with at most two products per customer is **not new**: it is
Linhares (2001) Prop. 2.1, which is Linhares & Yanasse (2002) Prop. 1.

**Deliverables:**
- the layers implemented in front of the customer search;
- the complement-split rule proved, on paper and in Lean;
- the speed-up measured on the corpus, in nodes and seconds;
- the honest negative stated: the 24 industrial SCOOP instances are mostly
  outside the easy classes.

## Part 2. Formula-certified benchmarks

Instances whose optimum is proved by a formula, at sizes no search reaches.
- **Hypercubes:** pw(Q_d) = Σ_{m<d} C(m, ⌊m/2⌋) (Chandran & Kavitha 2006,
  Thm 2), and H(t,2,n) (Wang et al. 2026).
- **Grids:** 2D and 3D grids, and even tori (Otachi & Suda 2011; Ellis & Warren
  2008).
- **Rook graphs and line graphs of complete graphs** (Clarke, Messinger & Power
  2019; Harvey & Wood 2015).
- **Complete multipartite graphs and wheels** (the join formula); caterpillars;
  complete ternary trees (pathwidth = height); and Ellis–Sudborough–Turner's
  smallest trees of pathwidth k.
- **Products as MOSP matrices** (*ours*, to prove). The Kronecker product
  M₁ ⊗ M₂ has MOSP graph G₁ ⊠ G₂, and [M₁ ⊗ I, I ⊗ M₂] has G₁ □ G₂. With
  Kaul (2026), that gives MOSP(M₁ ⊗ M₂) ≥ MOSP(M₁) · MOSP(M₂). This is a
  generator of large instances with a known lower bound and, for grids and
  hypercubes, a known optimum.

**Deliverables:**
- a benchmark set with the formula, the instance (in `.mosp` format) and a
  witness layout for each;
- every formula checked against the exact solver where it reaches; about 190
  graphs so far, no disagreement (`products_checks/`);
- a stress test of heuristics and lower bounds at sizes where the optimum is
  known but search is hopeless.

**New values to state or prove:**
- Kneser K(n,2): pw = C(n−1,2) for n = 6…10, one above tw;
- Hamming K₃³ = 13, K₄³ = 31, K₃⁴ = 34, which are open in the literature;
- king graphs P_n ⊠ P_n: n + 1;
- C_m ⊠ C_n: 2m + 2;
- generalized Petersen G(n,k): 2k + 2 for k ≤ 3;
- Otachi & Suda's 4D conjecture, confirmed at P₃⁴ = 21;
- Harper's (isoperimetric) bound exact on all 19 symmetric graphs tried.

## Part 3. Random MOSP, where the theory runs out

A random MOSP instance is a random intersection graph, the model Karoński,
Scheinerman & Singer-Cohen (1999) introduced *with an application to gate
matrix layout*.
- **What is proved:** opt = Θ(n) for m = n^α and p ≥ 2/m (Gao 2012); Θ(ε³n)
  treewidth just above the giant threshold (Do, Erde & Kang 2024); dense
  scaling n − O(√(n/p)) (Perarnau & Serra 2014); cubic graphs at most
  (1/6 + ε)n (Fomin & Høie 2006).
- **What is not proved:**
  - the slope of E[opt]; our fitted law has a 27/(D + 27) term
    (`reports/ml_nature.md` §12, §14);
  - concentration;
  - the hardness ridge at cover excess ≈ 2–2.4 (§25, §36, §37).
- **Explained, not discovered:** the q in our fitted formula is Rybarczyk's
  equivalent edge probability.

**Deliverables:**
- **The data the theory lacks:** 44,000+ certified optima (corpus plus the
  generated ensembles, `learning/data/ensemble/`). They fit the constants in
  the proved Θ(n) and Θ(ε³n) laws, and test the conjectured sharp threshold
  for linear width at m = Θ(n) ((mp)(np) > 1, *ours*, to state carefully).
- **The random cubic constant**, an experimental answer to Fomin & Høie's open
  window [0.072n, 0.167n]. A MOSP instance where each product has two
  customers is any graph. The lower end is *ours*, from Kolesnik–Wormald plus
  Harper, and needs checking.
- **Random trees:** E[pw] up to 10⁶ vertices with the Ellis–Sudborough–Turner
  algorithm, with no published limit law yet. Counting sequences go to OEIS.

## Claims to verify before use

The surveys label their own derivations *ours*. None has been checked by a
second reader or the solver, unless noted.
- [ ] The complement-split rule. The arithmetic was checked in session; the
      proof needs writing, and Lean.
- [ ] The Kronecker and cartesian MOSP-matrix identities. Four pairs were
      checked by isomorphism; the proof needs writing.
- [ ] MOSP(M₁ ⊗ M₂) ≥ MOSP(M₁) · MOSP(M₂), which rests on Kaul (2026), an
      arXiv preprint. Read the proof.
- [ ] Forest incidence graph ⇒ block-graph MOSP graph. Check the block-graph
      algorithm's source (Chou et al. 2008), not yet read first-hand.
- [ ] opt ≤ n − α + 1. One-line proof, checked in session; α here is the
      largest set of customers with pairwise disjoint product sets.
- [ ] The random-cubic lower bound 0.0721n, from Kolesnik–Wormald and Harper.
- [ ] The sharp-threshold conjecture: state it as a conjecture unless proved.
- [ ] Every result marked "read second-hand" or "abstract only" in the
      surveys: obtain the source and read it.

## Data and code

- **The corpus and its classes:** `class_scan.py`, `class_scan.json`.
- **The product checks:** `products_checks/`.
- **The exact solvers:** `satisfiability/customer_search.py` (MOSP) and
  `pathwidth_solver/` (graphs).
- **Certified ensembles:** `learning/data/ensemble/`, with `learning/upward.py`
  for 50–75.
- **New code:** the class layers, a product-instance generator, an
  Ellis–Sudborough–Turner implementation (`pathwidth_solver/TODO.md` phase 5),
  and a random-cubic and random-tree campaign.

## Venue

To decide after Part 1 is measured.
- Part 1 is applied and OR-shaped: *Computers & Operations Research*, *EJOR*.
- Parts 2–3 are more discrete-mathematics: *Discrete Applied Mathematics*.
- An arXiv preprint in any case: cs.DS with math.CO cross-listed.

## Kill criteria

- **Part 1:** if the class layers and the complement-split rule save under 5%
  of total nodes on the hard corpus instances (Chu & Stuckey 75–125), keep
  them as a remark in paper 2 and drop Part 1 as a contribution. Most hard
  instances may sit outside the easy classes, as SCOOP does.
- **Part 2:** if the benchmark adds nothing that existing VSPLIB grids and trees
  do not, fold it into Part 1.
- **Part 3:** if the fitted constants do not stabilise with n (as §14 found for
  some laws), report the data and no constant.

## Remaining work, in order

1. **Obtain the papers.** About 70 are listed in `literature/MISSING.md` under
   "Paper 3 survey (2026-10-09)". Many are free but bot-blocked, so fetch them in
   a browser: Gustedt 1993; Kloks, Kratsch & Spinrad 1997; Ellis & Warren 2008;
   Harper 1966; Karoński & Szymkowiak 2001. Karoński, Scheinerman &
   Singer-Cohen 1999 is paywalled.
2. **Part 1, implemented and measured.** Prove the complement-split rule (Lean)
   and run the layers on the corpus. This decides whether the paper is worth
   writing.
3. **The claims to verify** above.
4. **Part 2:** the benchmark set, and proofs or conjectures for the new values.
5. **Part 3:** the campaigns (random cubic, random trees, constant fits).
6. **The draft.**

Paper 2 comes first. None of this should delay it, except possibly the
complement-split rule, which could appear there as a remark.
