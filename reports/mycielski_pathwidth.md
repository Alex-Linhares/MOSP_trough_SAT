# Pathwidth of the Mycielskian: bounds and the search for a formula

2026-10-18. No solver runs: every value below is either from the project's
certified record (M_2..M_8) or computed by an exact subset DP of our own on
graphs of at most 17 vertices (`reports/scratch/mycielski_pw/pwtw.c`, vertex
separation and treewidth by subset DP). No Lean in this round (owner's change of
plan).

Notation: μ(G) has vertices V ∪ V' ∪ {w}; G's edges, v'_i v_j for v_i v_j ∈ E,
and w v'_i for all i. M_2 = K_2, M_{k+1} = μ(M_k), n_k = 3·2^(k−2) − 1.

| k | n_k | edges | pw(M_k) (ours, certified) | tw(M_k) (Tamaki 2017) |
|---|---|---|---|---|
| 2 | 2 | 1 | 1 | 1 |
| 3 | 5 | 5 | 2 | 2 |
| 4 | 11 | 20 | 5 | 5 |
| 5 | 23 | 71 | 10 | 10 |
| 6 | 47 | 236 | 20 | 19 |
| 7 | 95 | 755 | 38 | 35 |
| 8 | 191 | 2360 | 72 | open in 2017; upper bound 66 quoted there |

## 1. Literature

Nothing found that states a bound on the pathwidth, treewidth, vertex
separation, bandwidth or cutwidth of μ(G) in terms of the same parameter of G.
Searches: arXiv, Google Scholar-style web queries, ISGCI. What exists:

- **Tamaki, H.** (2019). Positive-instance driven dynamic programming for
  treewidth. *J. Comb. Optim.* 37, 1283–1311 (journal details UNVERIFIED); ESA 2017, LIPIcs 87, 68;
  arXiv:1704.05286. **Already held** (`literature/2017-Tamaki-...`). Table:
  tw(myciel2..6) = 2, 5, 10, 19, 35 (5, 11, 23, 47, 95 vertices; myciel6 newly
  solved there, 419 s); myciel7 (191 vertices) unsolved, lower bounds 22/31/35
  at 1 s/1 min/30 min, previous bounds 52 and 66. (The 52 lower bound in the
  "previous" column is as printed; verify against the source before quoting.)
- **SageMath** `vertex_separation` documentation: vs(MycielskiGraph(5)) = 10
  (23 vertices), agreeing with ours. Software documentation, not a paper.
- **Rihm (2012)**, already held: pw(Myciel3) = 5, lower bound 10 on Myciel4.
- ISGCI (graphclasses.org, class gc_1215) lists bandwidth, pathwidth and
  treewidth of Mycielski graphs as unknown to it.
- Papers on Mycielskians studied other parameters only (connectivity, boxicity:
  Kamibeppu, arXiv:1308.2368; general position; distinguishing number); none
  touches width parameters.

No PDF was saved: the one relevant open paper (Tamaki) is already held.
OEIS: 1, 2, 5, 10, 20, 38, 72 and 1, 2, 5, 10, 19, 35 match no entry about
graphs (the second matches only A065613, unrelated).

## 2. Bounds: what is proved and what is checked

Checked by exhaustive enumeration over **all 1,252 graphs on ≤ 7 vertices**
(nauty geng, pw and tw of G and μ(G)) and **all 11,117 connected graphs on 8
vertices** (pw only, μ(G) on 17 vertices).

**(a) pw(μ(G)) ≤ 2 pw(G) + 2.** Holds. Proof: bags B ∪ B' ∪ {w}. The same
argument gives **tw(μ(G)) ≤ 2 tw(G) + 2** for tree decompositions.

**(b) pw(μ(G)) ≤ 2 pw(G) + 1.** Holds on every graph checked, and is a
**theorem** with a short proof (ours; not found in the literature):

> Let v_1, …, v_n be a layout of G of vertex separation p, with A_i the active
> set of the prefix {v_1..v_i}. Lay out μ(G) as w, v_1, v'_1, v_2, v'_2, ….
> At the prefix ending in v'_i the active originals are A_i, the active shadows
> lie in A'_i (w is already placed), and w: at most 2p + 1. At the prefix ending
> in v_i (before v'_i): if v_i ∈ A_i, originals ⊆ A_{i−1} ∪ {v_i} (≤ p + 1) and
> shadows ⊆ (A_i ∖ {v_i})' (≤ p − 1), plus w; if v_i ∉ A_i, v_i is inactive
> (all its neighbours and their shadows are placed), originals ⊆ A_{i−1},
> shadows ⊆ A'_i: ≤ 2p + 1 either way.

The per-layout inequality vs_μ(layout) ≤ 2 vs_G(L) + 1 was also checked on
20,000 random graphs (n ≤ 11) with random layouts L: never violated, often
tight (`lay.py`). Tight cases exist for every pw ≤ 4 at n ≤ 8 (pw 1 → 3, 2 → 5,
3 → 7, 4 → 9).

**Pathwidth and treewidth separate here.** **tw(μ(G)) ≤ 2 tw(G) + 1 is false**:
9 counterexamples on ≤ 7 vertices; the smallest is the **3-sun** (graph6
`EElw`: triangle 345 with a degree-2 vertex on each edge: 03 04 13 15 24 25 34
35 45), tw = 2, pw = 3, tw(μ) = pw(μ) = 6 = 2·tw + 2. So (a) is tight for
treewidth and (b) is a pathwidth-only statement.

**Pathwidth on M_k**: 2·pw + 1 − pw(M_{k+1}) = 1, 0, 1, 1, 3, 5 for k = 2..7:
the bound is tight only at C_5 → Grötzsch and the slack grows.

**(c) Lower bounds.**
- **pw(μ(G)) ≥ pw(G) + 1 for V ≠ ∅** (and tw likewise): a proof. Contract
  every shadow into w; w becomes adjacent to every non-isolated vertex of G, so
  G + an apex over its non-isolated vertices is a minor, of pathwidth pw(G) + 1.
  (A direct proof for Lean, without the minor machinery: restrict P to the hull
  J of the bag intervals of w and the shadows; every bag of J holds w or a
  shadow, so drops by one; isolated v of G ride on v'∩w.) Tight for pw ≤ 1
  (37 graphs, e.g. K_2 → C_5).
- **pw(μ(G)) ≥ pw(G) + 2 when pw(G) ≥ 2**: conjecture, **no violation** on all
  graphs ≤ 7 vertices and all connected graphs on 8. Not proved. Tight on K_n.
  For treewidth the analogue **fails**: tw(μ(K_3)) = 3 = tw + 1 (30 failures
  on ≤ 7 vertices).
- **No bound pw(μ(G)) ≥ 2 pw(G) − c holds for any constant c** (proved):
  deleting V from μ(K_n) leaves a star, so pw(μ(K_n)) ≤ n + 1 = pw(K_n) + 2
  (exact for n ≤ 8 by computation). In general pw(μ(G)) ≤ n + 1 by the same
  deletion. On the M_k chain 2·pw − pw(next) = 0, −1, 0, 0, 2, 4, also
  growing.
- Best lower bound in pw(G) alone that survives: pw + 2 (pw ≥ 2), since K_n
  attains it. The minimum of pw(μ) at fixed pw over n ≤ 8 is exactly pw + 2
  for pw = 2..7.

Consequences for M_9 (383 vertices): **proved 73 ≤ pw(M_9) ≤ 145**;
conjecturally ≥ 74.

## 3. Closed formulas (sympy/scipy, `fit.py`, `fit2.py`)

Seven terms; every p-parameter fit used at most 5 terms and was tested on the
rest.

- **Linear combinations** of up to 3 of {1, k, k², 2^k, k2^k, 3^k, n_k, e_k,
  F_k, kF_k, L_k, (−1)^k, 2^k/k}, fitted on 3 consecutive terms: **no
  combination reproduces all seven.**
- **floor/ceil/round(r · x) + c** for x ∈ {n_k, 2^k, e_k, k2^k, 2^k/k},
  r = p/q with q < 40, c ∈ [−3, 3]: **none fits all seven.**
- **Integer linear recurrences** a(k) = Σ c_i a(k−i) + c_0 + c_1 k, order ≤ 3,
  |c_i| ≤ 2, |c_0| ≤ 4, |c_1| ≤ 2: **none fits.** In particular
  a(k) = 2a(k−1) − c fails (c = 0, −1, 0, 0, 2, 4) and
  a(k) = a(k−1) + a(k−2) + f(k) gives f = 2, 3, 5, 8, 14: Fibonacci to the
  fourth term, then 14 instead of 13 (the refuted A001629 guess, 71 vs 72).
- **Rational recurrences fitted on the earliest terms**: order 1 + const
  predicts 14, 29, 59, 113 for k = 5..8 (wrong); order 2 + const, fitted on
  k = 4..6, gives 38.75 and 73.75 (wrong); order 2 + const + k, fitted on
  k = 4..7, gives 71.5 (wrong).
- **Smooth growth laws** (A·b^k + B, A·n^γ + B, A·n/k^γ + B, A·2^k k^γ + B,
  A·n/log n^γ): fitted on k = 4..6 every one predicts k = 7, 8 off by up to 8;
  fitted on k = 6..8 they back-predict the earlier terms within 0.4–1.4 and
  extrapolate to **136–138 for M_9**. That is curve extrapolation, not a
  formula: the forward test fails for all of them. The ratio pw/n falls
  0.4545, 0.4348, 0.4255, 0.400, 0.377 from k = 4, and the growth ratio
  2.0, 2.0, 1.9, 1.89, i.e. sub-2^k growth, consistent with but not evidence for
  a 2^k/k^γ law (γ ≈ 0.4–0.5 on the last terms).
- Other derived sequences, none recognisable: n_k − pw = 1, 3, 6, 13, 27, 57,
  119; (n_{k−1} + 1) − pw = 1, 1, 2, 4, 10, 24.

**Verdict: nothing natural survives the hold-out tests.** Seven terms with an
irregular start (K_2 and C_5 are degenerate) do not determine a formula, and
any formula that matches all seven now has to be read as a fit.

## 4. What remains

- Prove pw(μ(G)) ≥ pw(G) + 2 for pw(G) ≥ 2 (or find a counterexample on 9+
  vertices or disconnected 8-vertex graphs, which were not checked).
- Lean (deferred): (a), (b) via the layout above and `pathwidth_le_vertexSeparation`,
  and the pw + 1 lower bound by the direct restriction argument.
- M_9 is open: 73 ≤ pw ≤ 145 proved.

Scripts: `reports/scratch/mycielski_pw/` (`pwtw.c`, `run.py`, `run8.py`,
`an.py`, `lay.py`, `fit.py`, `fit2.py`).
