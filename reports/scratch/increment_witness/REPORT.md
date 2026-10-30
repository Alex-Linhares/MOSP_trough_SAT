# Increment witnesses for recursive graph families (2026-10-30)

*Experiment for `reports/closed_formula_families_plan.md`. Everything here was
computed in this directory with the C program `pathwidth_solver/cli/pathwidth`
(graph6 on stdin, `nice -n 19`, at most 8 processes beside the owner's 24-core
run). Every pathwidth stated for a new graph is the C program's proved value
(`refutation`, `minor` or `bound`); every witness is saved as graph6 with the C
output (`*.g6`, `*.cert.txt`) and its contraction sequence in original labels.
Known values (Q_1..Q_6, M_2..M_7, T_1..T_4) were not recomputed, with two
exceptions: the full graphs were run once each as the C program's own
minor-certificate baseline (`baseline.py`, 7 s in all; needed to read its
certificate), and the tooling was sanity-checked on Q_3 and the Grötzsch graph
(milliseconds). In the dense survey, Kneser(n, 2) for n = 5..10, L(K_n) and the
complete multipartite graphs turned out to be already in
`paper2/survey_products_structured.md`; they cost 1 s in total and are reported
as confirmations, not results.*

**Indexing.** Mycielski graphs as networkx indexes them: M_2 = K_2, M_3 = C_5,
M_4 = Grötzsch (11 vertices), M_5 (23), M_6 (47), M_7 (95 = DIMACS myciel6),
M_8 (191 = DIMACS myciel7). Known pathwidths M_2..M_7 = 1, 2, 5, 10, 20, 38.
(The task text lists six graphs under the five indices 2..6; this report uses
six indices.) Hypercube Q_d on 0..2^d − 1, bit i = coordinate i; the copy of
Q_{d−1} is the set with top bit 0. Ternary tree T_h = `balanced_tree(3, h)`;
the copy of T_{h−1} is the subtree of the root's child 1.

A step `(v, u)` contracts v into u (u keeps its label, N(u) := N(u) ∪ N(v) −
{u, v}, exactly the C program's `_contract`); `(v, −1)` deletes v. Deletions
were offered in the `_del` runs and never accepted. "G_k ⊆ H" is by
construction: no step removes a copy vertex, so the copy survives as a
subgraph (possibly with added edges).

## 0. Summary

- **Hypercubes have no small witness.** Q_3 and Q_5 are *contraction-critical*
  for pathwidth: contracting any edge drops the pathwidth (4 → 3, 13 → 12; one
  test each suffices, Q_d being edge-transitive). Q_4 and Q_6 admit exactly
  one and two contractions (15 and 62 vertices), then none (all rejections
  proved). Deleting a vertex drops the pathwidth at d = 3..6; deleting an edge
  never does at d = 4..6. **Contraction drops the pathwidth for odd d and
  keeps it for even d** (d = 3..6), a parity pattern, conjectural beyond 6.
  So the lower bound is not carried by minors; it is carried by Harper's
  isoperimetric peak: with Φ_d(i) = min_{|S|=i} |N[S]| − i, max_i Φ_d(i) =
  Σ_{j<d} C(j, ⌊j/2⌋) for d = 1..8 (brute force confirms the profile at
  d = 3, 4), with peak increments exactly C(d−1, ⌊(d−1)/2⌋), the peak
  attained strictly inside a layer and never at |S| = 2^{d−1}.
- **Mycielski witnesses are a dense fold, not an attachment.** Best witnesses
  6, 14, 27, 57 vertices for M_4..M_7 (of 11, 23, 47, 95: 0.55–0.6 n), local
  minima of a greedy under several orders and seeds (M_5: 14 reached by 8 of
  30+ seeds, never below; M_6: 27 once, 29–32 otherwise). M_4 contracts to
  **K_6**. Every witness uses one operation only: a shadow s_i folded onto an
  adjacent original j ∈ N(i), with a third to a half of the shadows and the
  apex kept; the folds add 5, 10, 31, 180 edges inside the copy of M_k, which
  is never induced in the witness. **The witnesses do not nest**: the M_k
  witness sequence applied inside M_{k+1} drops the pathwidth in all three
  cases (10 → 7, 20 → 14, 38 → 29).
- **Trees (control)** behave exactly as the branch lemma says: the greedy
  finds the extremal trees, 7, 22, 67 vertices for T_2..T_4, three equal
  branches at the centre (2/2/2, 7/7/7, 22/22/22), sizes w(h+1) = 3w(h) + 1 =
  `treeBound(h) + 1` of `TreeBound.lean`; the nested runs reach the same
  trees.
- **No recurrence fit survives the spare-term rule** (spare ≥ 2) on any
  value, increment or witness-size sequence. Two zero-spare fits are worth
  recording because they can be tested: the order-2 degree-1 holonomic fit to
  the Mycielski values with K_1 first is a recurrence of **A001629** (checked
  to i = 79) and predicts 71 for myciel7 and 130 for myciel8; the same-shape
  fit to the hypercube values predicts 539/13 for Q_7 against the formula's
  43 and is wrong. Both are numerology by the rule.
- **Dense families** (213 new graphs, all proved, 164 by the degeneracy
  bound): for dense G with complement Ḡ the deficit n − pw lies in
  [ω(Ḡ), Δ(Ḡ) + 1] (independence bound above, degeneracy below); it sits at
  the bottom for complete multipartite graphs and Kneser(n, 2), at the top
  for co-path and co-cycle (pw = n − 3), and strictly between for L(K_n),
  where pw = 7, 10, 14, 18, 23, 28, 34 (n = 5..11) matches the theorem of
  Harvey & Wood 2015 / Fabila-Monroy et al. 2025 (`survey_products_structured.md`
  row L(K_n)) — n = 8..11 are new confirmations of a known formula.
- **Q_7**: Harper's simplicial layout (by Hamming weight, then within a layer
  the set holding the smaller element of the symmetric difference first; in
  integer terms *descending*) has vertex separation **43** on Q_7, checked in
  Python with no code shared with the C (`q7_attempt.py`); the upper bound
  pw(Q_7) ≤ 43 is thereby verified. A one-CPU-hour attempt to refute 42 on the
  full graph is recorded in §6. A contraction-minor certificate for 43 cannot
  exist below 127 vertices if the parity pattern holds (Q_7 would be
  contraction-critical), and costs as much as Q_7 itself in any case.

## 1. Witness table

| family | G_{k+1} | n, m | pw | C program's own certificate (`baseline.py`) | best witness H: |V|, |E| | G_k ⊆ H | structure |
|---|---|---|---|---|---|---|---|
| hypercube | Q_3 | 8, 12 | 4 | refutation, no minor | **8, 12** = Q_3 | yes | contraction-, vertex- and edge-critical |
| hypercube | Q_4 | 16, 32 | 7 | refutation, no minor | **15, 31** | yes | one contraction (any edge), then none; degrees 6^1 4^14 |
| hypercube | Q_5 | 32, 80 | 13 | refutation, no minor | **32, 80** = Q_5 | yes | contraction-critical |
| hypercube | Q_6 | 64, 192 | 23 | refutation, no minor (7 s) | **62, 190** | yes | two contractions along one coordinate (0→1, 6→7; protected run 32→0, 35→3), then none among 180 candidates, all rejections proved `refutation 22`; degrees 10^2 6^60. Level-2 census (`q6_level2.log`): after 0→1, exactly 15 of 191 edges keep 23, all coordinate-0 edges {x0, x1} with x of even weight in the quotient Q_5 |
| mycielski | M_4 | 11, 20 | 5 | minor 10/11 (min-d) | **6, 15 = K_6** | yes | every shadow folded onto an original (8→0, 5→1, 6→2, 9→3, 7→4), apex kept |
| mycielski | M_5 | 23, 71 | 10 | minor 17/23 | **14, 58** (other minima 14/60, 14/61, 15, 16) | no: 9 of 11 copy vertices | 4 shadows + apex kept, 10 edges added in the copy |
| mycielski | M_6 | 47, 236 | 20 | minor 35/47 | **27, 206** (seed 15; also 29, 30, 31, 32 from 16 other runs) | no: 12 of 23 | 14 shadows + apex kept, 18 edges added in the copy |
| mycielski | M_7 | 95, 755 | 38 | minor 60/95 (the record's: 58) | **57, 690** (also 57/693, 58/693) | no: 40 of 47 | 16 shadows + apex kept, 180 edges added |
| ternary | T_2 | 13, 12 | 2 | minor 11/13 | **7, 6** | yes | spider: centre + three paths of length 2 |
| ternary | T_3 | 40, 39 | 3 | minor 38/40 | **22, 21** | yes | centre + three copies of the 7-vertex witness |
| ternary | T_4 | 121, 120 | 4 | refutation | **67, 66** | yes | centre + three copies of the 22-vertex witness |

Files: `shrink_<family>_<k>_<mode>_<free|prot>_s<seed>[_del].{g6,cert.txt,json,log}`
(json holds the sequence and every tested candidate with its proved width),
`baseline_*.{g6,cert.txt}` + `baseline.json`, `nested_*.{g6,cert.txt,json}`,
`analyze.log` (branch sets of every best witness), `hyper_ops.json`.

Single minor operations on Q_d (`hyper_ops.json`; one test per operation is
exhaustive by vertex- and edge-transitivity):

| d | pw(Q_d) | − vertex | − edge | / edge |
|---|---|---|---|---|
| 3 | 4 | 3 | 3 | 3 |
| 4 | 7 | 6 | 7 | 7 |
| 5 | 13 | 12 | 13 | 12 |
| 6 | 23 | 22 | 23 | 23 |

## 2. The shape across k, and the induction step each family suggests

**Trees.** H_{h+1} = a vertex with three branches, each a copy of H_h: the
branch lemma (Fellows & Langston 1987 Lemma 4.3; `Sandwich.lean`,
`TreeBound.lean`), recovered by the greedy without being told. The nested
runs (apply the T_{h−1} witness inside the child-1 subtree of T_h, keep
shrinking) end at the same 22- and 67-vertex trees.

**Hypercubes.** The witness is the whole cube up to a slack of 0 (odd d) or
one or two parallel contractions (even d). The increment C(d, ⌊d/2⌋) is
therefore not a local attachment; the smallest certificate of pw(Q_{d+1}) is
Q_{d+1} itself for d + 1 odd, and nothing below 2^{d+1} − 2 vertices was found
for d + 1 even. The induction the data supports is isoperimetric:

> *Peak recurrence.* Φ_d(i) = min_{|S| = i} |N[S]| − i over S ⊆ V(Q_d). Then
> max_i Φ_{d+1}(i) = max_i Φ_d(i) + C(d, ⌊d/2⌋), and every layout of Q_d has
> vertex separation ≥ max_i Φ_d(i), because its prefix of size i is such an S.

Checked (`harper.log`): Harper's theorem gives Φ_d from the simplicial order;
the peaks are 1, 2, 4, 7, 13, 23, 43, 78 for d = 1..8, so the recurrence
holds for d = 1..7, and the simplicial profile equals the brute-force profile
over all 2^n subsets at d = 3 and 4. The peak is attained at |S| ∈ {8, 9, 11,
12} in Q_5 and {14, 15, 17, 18, 24, 25, 27, 28} in Q_6, inside a layer, never
at the half-cube: an induction on d must carry the whole profile, not one
prefix size. This is Chandran & Kavitha's route, not a new one; the Lean
target in the plan (`Hypercube.lean`) is exactly this.

A first version of `harper.py` used ascending integer order within a layer.
That is *not* Harper's order: its profile exceeds the formula (14 at Q_5, 25 at
Q_6, 50 at Q_7) and disagrees with brute force at Q_4. Recorded because the
same mistake would make a Q_7 seed layout of width 50 instead of 43.

*Conjecture (parity), untested beyond d = 6:* Q_d is contraction-critical for
pathwidth iff d is odd. The even case has slack, and the census on Q_6
(`q6_level2.py`: all 382 directed second steps after the WLOG first step 0→1,
0 undecided) shows exactly what it is: the second contraction must be another
coordinate-0 edge {x0, x1} with x in the same bipartition class of the quotient
Q_5 as the first (even weight: C(5,2) + C(5,4) = 15 edges), every other edge
drops the width to 22, and after two such edges no third step exists in either
orbit of second steps (`q6_level3.log`: weight-4 orbit, 380 directed third
steps, all proved 22, 0 undecided; the greedy runs cover the weight-2 orbit).
So the maximum number of contractions Q_6 survives is exactly 2, given the
first step is WLOG by edge-transitivity. Contracting all coordinate-0 edges gives Q_5 (pw 13), so the
fold Q_6 → Q_5 loses width only from its third edge on. Testing d = 7 means proving
pw(Q_7 / e) ∈ {42, 43} on 127 vertices, the cost of Q_7 itself.

**Mycielski.** H_{k+1} = M_k ∪ {apex} ∪ S, S a set of roughly n_k/3 shadows,
the other shadows folded onto adjacent originals (each fold s_i → j adds the
edges j — N(i)). No fixed attachment: |S| = 1, 4, 14, 16, added edges 5, 10,
18, 180, both scaling with n_k; the best M_6 witness keeps only 12 of the 23
copy vertices. A randomised search for clique minors (`hadwiger.py`, 3,000 and
500 trials) found no K_11 in M_5 (best 52 of 55 edges on 11 vertices) and no
K_21 in M_6 (177 of 210), so beyond M_4 the witnesses are not cliques. The copy of M_k is never induced in H_{k+1},
and the natural nesting fails. The one clean fact is at the bottom: pw(M_4) =
5 because the Grötzsch graph has a K_6 minor (five folds). The only general
statements the data supports were tested on random graphs (§5):
pw(M(G)) ≤ 2 pw(G) + 1 held on all 244 (the trivial construction, every bag
doubled plus the apex, gives only 2 pw(G) + 2), while pw(M(G)) ≥ 2 pw(G) fails
on 92 of 244 and already at M_7 (38 < 40). The plan's conjecture reads
pw(M_k) = pw(M_{k−1}) + pw(M_{k−2}) + F_{k−1} (A001629's recurrence; checked
on the six values); nothing in the witnesses says where a Fibonacci number
would come from, and I state no lemma for it.

## 3. Recurrence fits (`recurrences.py`, `recurrences.log`)

Accounting: a constant-coefficient recurrence of order r has P = r parameters
(r + 1 with a constant term) and E = N − r equations from N terms; a holonomic
recurrence of order r with polynomial coefficients of degree d has P =
(r + 1)(d + 1) − 1. spare = E − P; spare < 2 is numerology. Hold-out: refit on
N − 1 terms and predict the last.

| sequence | N | fits found (every one has spare ≤ 1) | verdict |
|---|---|---|---|
| pw(Q_d), d = 1..6: 1, 2, 4, 7, 13, 23 | 6 | linear order 3 (P 3, E 3, spare 0): a_n = a_{n−1} + 2a_{n−2} − a_{n−3}; holonomic (1,2), spare 0 | numerology; they predict 42 and 539/13 for Q_7 against the formula's 43: **wrong** |
| with Q_0 = K_1: 0, 1, 2, 4, 7, 13, 23 | 7 | linear order 3 (spare 1, hold-out passes); holonomic (2,1), spare 0 | numerology; the holonomic fit predicts 539/13 at Q_7: wrong |
| hypercube increments 1, 2, 3, 6, 10 | 5 | linear order 2 + const (spare 0) | numerology; the true sequence C(i, ⌊i/2⌋) is P-recursive of order 2, degree 1, and the partial sums need ≥ 9–12 terms to be found honestly |
| pw(M_k), k = 2..7: 1, 2, 5, 10, 20, 38 | 6 | linear order 3 (spare 0): a_n = 12/5 a_{n−1} − 2a_{n−3} | numerology; predicts 356/5, not an integer: wrong |
| with M_1 = K_1: 0, 1, 2, 5, 10, 20, 38 | 7 | holonomic (2,1), spare 0: (1−i)a_i + i a_{i−1} + (i+1)a_{i−2} = 0 | numerology by the rule, but it is a recurrence of **A001629** (holds for i ≤ 79) and predicts 71 (myciel7), 130 (myciel8): the plan's conjecture rederived, still a conjecture |
| Mycielski increments 1, 3, 5, 10, 18 | 5 | linear order 2 + const (spare 0) | numerology |
| pw(T_h) = 1, 2, 3, 4 | 4 | a_n = a_{n−1} + 1 (spare 1, hold-out passes) | numerology by the rule; a theorem (`TreeBound.lean`) |
| tree witness sizes 7, 22, 67 | 3 | a_n = 3a_{n−1} + 1 (spare 0) | a theorem through `treeBound` |
| Mycielski witness sizes 6, 14, 29, 57 | 4 | nothing exact at order ≤ 1 | greedy local minima, ≈ 0.6 n |

Closed forms checked with sympy: Σ_{i<d} C(i, ⌊i/2⌋) = 0, 1, 2, 4, 7, 13, 23,
43, 78; x²/(1 − x − x²)² = x² + 2x³ + 5x⁴ + 10x⁵ + 20x⁶ + 38x⁷ + 71x⁸ + 130x⁹ +
235x¹⁰ + …; A001629(n) = ((n−1)F_n + 2nF_{n−1})/5.

## 4. Dense families (`dense.py`, `dense.json`, `dense_next.json`, `dense_analysis.log`)

213 graphs on 4–55 vertices, all proved (none `upper`): 164 by the degeneracy
bound, 49 by refutation; α exact as the clique number of the complement.

| family | members | pw | deficit n − pw | (n − α) − pw | status |
|---|---|---|---|---|---|
| complete multipartite K_{p×q} | 41, n ≤ 40 | n − q | q = α | **0** | known (join lemma; survey row 27) |
| co-matching K_{m×2} | n = 6..40 | n − 2 | 2 = α | **0** | special case of the above |
| co-path | n = 6..40 | n − 3 | 3 = α + 1 | 1 | new |
| co-cycle | n = 6..40 | n − 3 | 3 = α + 1 | 1 | new |
| Kneser(n, 2), n = 6..10 | 15..45 vertices | C(n−1, 2) = n_v − α | n − 1 | **0** (Petersen: 5, one below) | already in the survey (row 51) |
| L(K_n), n = 5..11 | 10..55 vertices | 7, 10, 14, 18, 23, 28, 34 | 3, 5, 7, 10, 13, 17, 21 | 1, 2, 4, 6, 9, 12, 16 | theorem (survey row 47); n = 8..11 confirm it |
| cycle powers C_n^k, k = 2..5 | 65, n ≤ 40 | 2k = degeneracy | n − 2k | large | new, trivial |
| circulants, six connection sets | 40, n = 10..40 | = degree once n ≳ 3·max S | n − degree | large | new, trivial |

For dense G with complement Ḡ: pw(G) ≥ n − 1 − Δ(Ḡ) (degeneracy) and pw(G) ≤
n − ω(Ḡ) (`IndependenceBound.lean`), so **n − pw ∈ [ω(Ḡ), Δ(Ḡ) + 1]**. The
data (`dense_analysis.log`, last block): deficit = ω(Ḡ) on all 41 multipartite
graphs and 5 of 6 Kneser graphs (where Ḡ = L(K_n): ω = n − 1 against Δ + 1 =
2n − 3), deficit = Δ(Ḡ) + 1 on all 36 co-paths and co-cycles (and on all 65
cycle powers, where it is the degeneracy bound), and strictly between on
every L(K_n) (Ḡ = Kneser(n, 2): 3 ∈ [2, 4], …, 21 ∈ [5, 37]). The L(K_n)
values equal ⌊n²/4⌋ + ⌊(n−3)/2⌋, which is Harvey & Wood's ((n−1)/2)² + n − 2
(n odd), (n−2)n/4 + n − 2 (n even), term by term. So for the dense families
tried, what n − pw depends on is which end of the sandwich the complement's
structure forces: a complement that is a disjoint union of cliques, or a line
graph of K_n, forces the independence end; a complement of maximum degree 2
forces the degeneracy end; Kneser complements (L(K_n)) do neither.

## 5. Candidate Mycielskian lemmas on random graphs (`myc_lemma_test.py`, `.log`)

244 connected random graphs G on 4..11 vertices (G(n, p), p ∈ {0.25, …, 0.9}),
pw(G) and pw(M(G)) both proved by the C program:

| candidate | result |
|---|---|
| L1: pw(M(G)) ≤ 2 pw(G) + 1 | **0 violations** of 244; also holds on M_3..M_7 (38 ≤ 41). Equality on 56 (e.g. K_{1,3}: 1 → 3) |
| L1′: pw(M(G)) ≤ 2 pw(G) | 56 violations |
| L2: pw(M(G)) ≥ 2 pw(G) | 92 violations (e.g. K_4: 3 → 5); fails at M_7 too |
| L3: pw(M(G)) ≥ pw(G) + 1 | 0 violations (trivial) |
| pw(M(G)) − pw(G) ≤ n − α(G) | 0 violations of 244 (equality on 62); not a theorem I can prove, recorded as data |

Distribution of pw(M(G)) − 2 pw(G): −6 … +1, mode 0 (96 of 244). So the
Mycielskian roughly doubles pathwidth on small graphs, with a spread the
construction does not explain; L1 is the one candidate that survived and
would be the upper-bound half of an induction, if anyone wanted one.

## 6. The Q_7 by-product attempt

Seed: Harper's simplicial layout, vertex separation 43 verified in Python
(`Q7_harper_closing.txt`, the reversed layout as the C's closing order);
`-L 42` (directs the descent only: the C refutes 42 itself), minor ladder off
(`-m min_vertices=1000`), `-t 3600`, one core. Result: see the end of this
file. A first launch used the wrong within-layer order (width 50) and was
stopped after 2 minutes.

## 7. Not done, and caveats

- No global minimality claim for any witness: the shrink is greedy (first
  acceptable step in min-degree, least-common-neighbour or random order;
  deletions offered in the `_del` runs, never accepted), and different orders
  reached different local minima for the Mycielski graphs (14–16, 29–32,
  57–58). The hypercube statements are exhaustive only where symmetry makes
  one test exhaustive (Q_3, Q_5, the single-operation table, the first step
  on Q_6).
- Nesting H_k ⊆ H_{k+1} was tested only through the natural copy of G_k; other
  embeddings were not searched (minor containment is hard in general).
- The parity conjecture is untested at d ≥ 7.
- Nothing was run on myciel7 (M_8) and nothing under `reports/scratch/myciel7_*`
  was touched. A witness search on M_8 would be a greedy shrink of 191
  vertices with each acceptance test a refutation of 70 on a ≥ 110-vertex
  minor; the witnesses at k ≤ 7 are ≈ 0.6 n and do not nest, so there is no
  shortcut from M_7's witness, and the one-hour cap would not cover a single
  round.
- Kneser(n, 2), L(K_n) and the complete multipartite graphs were already in
  `paper2/survey_products_structured.md`; I ran them (1 s in all) before
  finding that, and the report labels them as confirmations.
- No Lean, no `lake build`, nothing committed.

## 8. Results of the pending runs

- **Q_7, one CPU-hour** (`Q7_attempt.out/err`): `pathwidth 43 upper`,
  5.02 × 10⁹ nodes in 3,600 s, 42 not refuted. The C re-checked the seed
  layout at width 43, so pw(Q_7) ≤ 43 stands verified twice (Python and C);
  43 remains unproved by us. The owner's 97-minute default run of 2026-10-18
  wrote nothing either. At the node rate observed (1.4 M nodes/s) and with
  Q_6's refutation at 7 s against Q_5's 0.03 s (×230 per dimension), the full
  refutation of 42 on Q_7 is not an hours-scale job on one core; and a minor
  certificate cannot help if the parity pattern holds (Q_7 would be
  contraction-critical), while every minor of Q_6 with two or more
  contractions off one colour class already lost width.
- **Q_6 contraction census** (§2): exactly two contractions survive, both
  orbits of second step checked, 0 undecided calls.
- **Mycielski seeds** (30 on M_5, 20 on M_6): M_5 min 14 (8 times), M_6 min
  27 (once); `seeds_more.err`, `shrink_mycielski_*_random_free_s1*.log`.
- One run (`search.py mycielski 7 random 0 2`) was still finishing when this
  was written; its files appear beside the others.

## 9. What I would do next

1. **Hypercube, Lean**: the peak recurrence of §2 is the induction step the
   plan's `Hypercube.lean` needs; the prefix-is-an-S half is already
   `EmptyPair.lean`'s Harper-in-layout-form. The missing piece is Harper's
   theorem (compression) or a direct proof that max_i Φ_{d+1}(i) =
   max_i Φ_d(i) + C(d, ⌊d/2⌋); the brute-force profiles at d = 3, 4 and the
   simplicial ones to d = 8 are in `harper.log` as test data.
2. **Parity conjecture**: a cheap partial test is Q_7 / e against a *lower*
   bound only — if `-L 42` on Q_7 / e (127 vertices) refutes 41 quickly the
   conjecture survives a weak test; it does not need the 42 refutation.
3. **Mycielski**: stop looking for a minor induction; the witnesses say the
   bound is global. The one fact worth a lemma is L1, pw(M(G)) ≤ 2 pw(G) + 1,
   which held on all 244 random graphs and all M_k: a layout proof should be
   short (interleave each shadow right after its original and put the apex
   last), and it is one better than the obvious 2 pw(G) + 2.
4. **myciel7**: nothing here changes the picture; a 71-layout search is still
   the right side to work, as the plan says.
5. **Dense**: co-path and co-cycle at pw = n − 3 (degeneracy end) are
   trivial but new; the sandwich [ω(Ḡ), Δ(Ḡ)+1] is the right frame for
   "what the deficit depends on", and L(K_n) is the family that sits inside
   it — worth a note in `paper2/survey_products_structured.md` only.
