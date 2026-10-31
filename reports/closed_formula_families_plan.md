# Closed formulas for the pathwidth of recursive graph families (plan, 2026-10-18)

**Idea (owner, 2026-10-18).** Compute exact pathwidths of the small members of
a recursively defined family, guess a closed formula (sympy fitting, the OEIS),
then prove it by induction on the construction, and formalise it in Lean as
`Grid.lean` did for grids. New where the family's exact pathwidth is open.

**Why families and not random graphs.** Induction needs an object built from a
smaller copy of itself. G(n, p) at n + 1 is not built from G(n, p) in any way
pathwidth respects, so fitting E[pw] through the n ≤ 11 exact values would be
curve fitting. One random exception: P(pw(G(n, p)) ≤ 1) = P(forest of
caterpillars), countable exactly (labelled caterpillars), probably with a
known closed form; check before claiming.

## Pipeline

1. **Compute** exact pw of the first members with the C program
   (`pathwidth_solver/cli/pathwidth`, never the Python solver; nice 19). New
   graphs only, unless the owner asks.
2. **Guess** a formula: sympy fits, finite differences, the OEIS. A guess
   needs more members than parameters, and a check on a member not used to
   fit it.
3. **Literature check** before any proof: is the sequence, or a bound, known?
4. **Upper bound by construction:** a layout of member k + 1 built from one
   of member k, whose width follows the formula.
5. **Lower bound by induction:** the hard direction (it must defeat every
   layout). Tools we have: minor monotonicity (Theorem 4.11, Lean
   `pathwidth_gt_of_minorOf`) when member k is a minor of member k + 1; the
   vertex-isoperimetric bound (Harper; `satisfiability/expansion_bound.py`);
   the first-prefix argument of `Grid.lean`.
6. **Lean**, as `Grid.lean`; brute-force check every intermediate statement on
   small members first (two earlier `sorry`s hid false statements).

## Candidate families, in order

1. **Mycielski graphs** M_k (M_2 = K_2, M_3 = C_5, M_4 = Grötzsch, ...).
   Built by a fixed construction from the previous one, ideal for induction.
   Known to us: pw(M_6) = myciel6 = 38, pw(M_7) ∈ {71, 72}. No exact formula
   known to us. Also the generalised Mycielskians.
2. **Hypercubes** Q_d: pw = Θ(2^d/√d) (Chandran & Kavitha 2006); whether an
   exact value is proved is to be checked first. The isoperimetric argument is
   the natural lower bound tool (Harper).
3. **Products:** tori C_m × C_n, Hamming graphs K_q^d, P_m × K_n, P_m × P_n × P_k.
   Grids were the easiest product; these are next.
4. **MOSP-side families** with uniform product structure, where a formula
   says something about open stacks too.

## Risks

Guessing is cheap and proving is hard; the lower bound is the hard part. The
grid lower bound took a careful argument and Mycielski graphs are much less
regular. A formula that fits five members can fail at the sixth: compute as
far as the solver reaches before guessing.

## First step

Exact pathwidth of M_2 ... M_6 (M_7 is the running myciel7 portfolio) and of
Q_1 ... Q_d as far as the solver reaches; look the sequences up. Scheduled
for 2026-10-18, after the G(n, c/n) pilot.

## First results (2026-10-18)

**Hypercubes** (computed now in C, all proved): pw(Q_1..Q_6) = 1, 2, 4, 7, 13, 23,
which is OEIS A036256, `Σ_{i=0}^{d-1} C(i, ⌊i/2⌋)`, the partial sums of central
binomial coefficients. This is almost certainly the known vertex-separation
value of the hypercube from Harper's isoperimetric theory (listed in the
graph-layout surveys); **literature check before anything is claimed.** It
predicts pw(Q_7) = 43 (not computed: a known value is not an unsolved problem).

**Mycielski graphs** (no compute: values already proved in
`pathwidth_solver/bench/results/coloring*.csv`): DIMACS myciel2..myciel6
(C_5, Grötzsch, 23, 47, 95 vertices) have pw 2, 5, 10, 20, 38; with K_2 (pw 1)
before them the sequence 1, 2, 5, 10, 20, 38 matches **OEIS A001629**, the
self-convolution of the Fibonacci numbers, `Σ_k F(k) F(n−k)`, g.f.
`x²/(1 − x − x²)²`, on every known term. Its next term is **71**, inside our
interval 71 ≤ pw(myciel7) ≤ 72, and the one after is 130 for myciel8
(383 vertices). A conjecture from six terms, not a result; if true,
**refuting 71 on myciel7 can never succeed**, and the right search is for a
width-71 layout. No formula for the pathwidth of Mycielski graphs is known to
us; literature check first.

## First Lean target: the hypercube (2026-10-18)

`pw(Q_d) = Σ_{i=0}^{d-1} C(i, ⌊i/2⌋)` (A036256; matches our exact values
Q_1..Q_6). Known mathematics (Harper's vertex-isoperimetric theorem), so the
contribution is the formalisation, not the theorem.

- **Upper bound, by induction on d:** Harper's simplicial order (by Hamming
  weight, then lexicographic) has vertex separation equal to the formula;
  passing from Q_d (two copies make Q_{d+1}) adds the middle layer C(d, ⌊d/2⌋).
- **Lower bound:** Harper's theorem (Hamming balls minimise the vertex boundary
  among k-sets, proved by compression), plus "every layout has a prefix of
  every size, so vs ≥ max_k min-boundary(k)", i.e. our expansion bound.
  Mathlib has UV-compressions and Kruskal–Katona
  (`Mathlib.Combinatorics.SetFamily.*`); whether it has Harper's vertex
  version is to be checked.
- Assigned to a Lean agent, 2026-10-18 (`lean/MOSPFormalization/Hypercube.lean`).

## Second results: increment witnesses (2026-10-31, one agent, 4.6 h; `reports/scratch/increment_witness/REPORT.md`)

The question was whether the lower-bound half of an induction can be carried
by a *minor*: for each consecutive pair, the smallest contraction minor of
member k + 1 whose width the C program proves equal to the member's. 78
witnesses saved as graph6 with the C output and contraction sequence; every
rejection in the searches proved; three claims spot-checked independently by
the coordinator (Q_5/e = 12, the Grötzsch witness is K_6, the Q_7 layout has
vertex separation 43).

- **Trees** (control): the greedy recovers the extremal trees of 7, 22, 67
  vertices, a centre with three copies of the previous witness: the branch
  lemma, found without being told.
- **Hypercubes: no small witness.** Q_3 and Q_5 are contraction-critical
  (any one contraction drops the width; one test is exhaustive by
  edge-transitivity); Q_4 and Q_6 allow one and two parallel contractions and
  then none (a full census of second steps on Q_6: 15 of 382 keep 23, all
  parallel to the first in the same colour class). Deleting a vertex drops
  the width at d = 3..6, deleting an edge never does. *Parity conjecture,
  untested beyond 6*: Q_d is contraction-critical iff d is odd. So the
  increment C(d, ⌊d/2⌋) is not an attachment; the only induction the data
  supports is Harper's profile, max_i Φ_{d+1}(i) = max_i Φ_d(i) + C(d, ⌊d/2⌋),
  checked to d = 8, with the peak attained inside a layer and never at the
  half-cube, so the induction must carry the whole profile. Trap recorded:
  "weight, then ascending integer order" is *not* Harper's order (widths
  14/25/50 on Q_5/6/7 instead of 13/23/43); the within-layer order is the
  set containing the smaller element of the symmetric difference first.
- **Q_7 ≤ 43 verified**: Harper's layout has vertex separation 43, checked
  in Python with no shared code and re-checked by the coordinator. One
  CPU-hour from that layout with floor 42 did not refute 42 (5.0 × 10⁹
  nodes). A minor certificate cannot help if the parity conjecture holds.
  The route to Q_7 = 43 is Harper's theorem in Lean, as planned.
- **Mycielski: the witnesses are a dense fold and do not nest.** Best
  witnesses 6 (= K_6), 14, 27, 57 vertices for M_4..M_7 (networkx indexing;
  0.55–0.6 n), every one made by folding shadow vertices onto adjacent
  originals; the copy of M_k is never induced and increasingly not intact;
  the M_k witness applied inside M_{k+1} drops the width every time
  (10 → 7, 20 → 14, 38 → 29). No K_11 minor in M_5, no K_21 in M_6 found.
  **No structural induction step is supported.** The agent also tested
  pw(M(G)) ≤ 2·pw(G) + 1 on 244 random graphs with both widths proved
  (equality on 56) and found pw(M(G)) ≥ 2·pw(G) false (and false at M_7:
  38 < 40). **The upper inequality is already a theorem of this repository**,
  `lean/MOSPFormalization/Mycielski.lean`, `pathwidth_mycielskian_le`
  (2026-10-18, sorry-free; the layout puts each shadow immediately before its
  original, apex last), with `pathwidth_add_one_le_mycielskian` as the lower
  companion; neither the agent nor the coordinator checked the file before
  calling it data (corrected 2026-10-31).
- **Recurrences: nothing survives the spare-term rule** (≥ 2 spare terms)
  on any value, increment or witness-size sequence; six or seven terms are
  too few. The zero-spare holonomic fit to the Mycielski values is a
  recurrence of A001629 (predicting 71 for myciel7), the plan's conjecture
  rederived and still a conjecture; the same shape fitted to the hypercubes
  predicts a non-integer for Q_7, which is the right warning.
- **Dense structured families** (213 new graphs, all proved): with Ḡ the
  complement, n − pw ∈ [ω(Ḡ), Δ(Ḡ) + 1] (independence bound above,
  degeneracy bound below); at the bottom for complete multipartite graphs
  and Kneser(n, 2), at the top for co-paths, co-cycles and cycle powers,
  strictly between for L(K_n), where the values to n = 11 match the known
  formula ⌊n²/4⌋ + ⌊(n − 3)/2⌋ (Harvey & Wood 2015; Fabila-Monroy et al.
  2025; `paper2/survey_products_structured.md`). Nothing new about the
  dense deficit beyond this frame.

**Verdict on the method.** Minor-carried induction works exactly where the
increment is an attachment (trees) and fails where it is global (hypercubes:
the whole graph is the certificate; Mycielski: a fold that does not nest).
For the two open families the lower bound is isoperimetric or unknown, not
operational. Next, if resumed: Harper's profile recurrence in Lean for the
hypercube; a layout proof of pw(M(G)) ≤ 2·pw(G) + 1; the parity conjecture
tested on Q_7/e with floor 41.
