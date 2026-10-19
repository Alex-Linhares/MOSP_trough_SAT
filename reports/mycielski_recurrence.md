# Is there a recurrence for pw(M_k)? Sampling the map G ↦ μ(G)

2026-10-19. Follows `reports/mycielski_pathwidth.md`, which tested formulas on the
seven certified terms 1, 2, 5, 10, 20, 38, 72 and found that none survived. This
round samples the map itself: exact pw(μ^j(G)) for 12,623 seeds and up to six
iterates. Scripts and data are in `reports/scratch/mycielski_rec/`. Nothing here
is committed.

**Verdict.** No recurrence survives. Nothing computable from G, or from the
previous terms of a chain, determines pw(μ(G)), and that holds even along
Mycielski chains, where the previous values do not fix the next one. Three
things do survive. (i) A lower-bound conjecture of Fibonacci type,
pw(μ²G) ≥ pw(μG) + pw(G) + 1. If it holds, pw(M_9) ≥ 111. (ii) Exact linear laws
pw(μ^j(K_n)) = A_j n + B_j for j ≤ 5. They contain the M chain as n = 2, and they
predicted M_4..M_7 out of sample. (iii) A new proved upper bound,
**pw(M_9) ≤ 138**. **Proved: 73 ≤ pw(M_9) ≤ 138. Conjectured: pw(M_9) ≥ 111.
No point prediction survives.**

Notation: μ(G) = V ∪ V′ ∪ {w}. p_j = pw(μ^j(G)). The slack is
s_j = 2p_j + 1 − p_{j+1}. M_2 = K_2, so M_{k} = μ^{k−2}(K_2).

## Data (what was computed)

| set | seeds | iterates | largest graph solved | method |
|---|---|---|---|---|
| all graphs on 1–7 vertices (incl. disconnected) | 1,252 | j ≤ 3 (all), j ≤ 5 (n ≤ 4) | 95 v | own subset DP ≤ 22 v (`dp.c`), C program above |
| all connected graphs on 8 vertices | 11,117 | j ≤ 2 (all); j = 3 for a random 1,500 | 71 v | same |
| named families (K_n ≤ 10, C_n, P_n ≤ 12, stars, K_{a,b} ≤ 6, wheels, grids, Petersen, Q3, Q4, Heawood, dodecahedron, Chvátal, all trees on 8–10 v) | 254 | while ≤ 160 v | 287 v (μ⁵(K_8)) | same |
| counterexample search: G(n,p) n = 9–12, p ∈ [0.3,1]; K_a ∪ K_b; K_n − matching; K_n + isolated; complete multipartite | 1,565 | j ≤ 2 | 51 v | same |

The total is 40,926 exact values (statuses dp, bound, refutation, minor), forming
31,448 consecutive pairs (p_j, p_{j+1}) and 17,260 triples. 13 runs timed out and
are kept as upper bounds only. Every row stores a layout of the stated width.

Compute: about 3.1 core-hours. That is 2.16 h of solver time, summed from the
`sec` columns, plus about 0.7 h of annealing and about 0.2 h of DP and lattice
runs. Everything ran under `nice -n 19` with at most 7 of my processes at once.
No M_k was solved or re-certified. The certified values were inserted for
graphs isomorphic to M_5..M_8 (`gather.py`, `KNOWN`). The previous agent's pw of
μ(G) for G ≤ 7 vertices and for connected 8-vertex graphs was recomputed, in
seconds, because those rows had not been saved.

Regenerate:
```
cd reports/scratch/mycielski_rec && gcc -O2 -march=native -o dp dp.c && gcc -O2 -o lattice lattice.c && gcc -O2 -o pairdp pairdp.c && gcc -O2 -o anneal anneal.c -lm
for n in 1 2 3 4 5 6 7; do nauty-geng -q $n; done | awk '{print "g"NR, $1}' > seeds_all7.txt
python3 gather.py seeds_all7.txt data_all7.csv 63 120          # 4 min on 8 cores
python3 gather.py seeds_c8.txt data_c8.csv 35 60                # seeds: nauty-geng -cq 8
python3 gather.py seeds_named.txt data_named.csv 100 60
NPROC=4 python3 gather.py seeds_deep_named.txt data_deep_named.csv 160 180
NPROC=4 python3 gather.py seeds_le4.txt data_deep.csv 100 300
python3 gather.py seeds_c8_mu2_sample.txt data_c8_mu3.csv 71 60
NPROC=4 python3 gather.py seeds_extra.txt data_extra.csv 51 120
NPROC=4 TMO=900 python3 kn_deep.py 5:5 6:5 7:5 8:5 3:6 4:6 5:6 6:6
NPROC=4 TMO=600 python3 seed_deep.py K3_3:5 K2_3:5 K4_4:4 K5_5:4 K2_4:4 K3_4:4 K2_5:4 K2_6:4
```
`chains.py` merges every CSV into chains seed → [p_0, p_1, …].

## Finding 1. The previous values do not determine the next, even on Mycielski chains

Over all chains in the data (`chains.py`), the next value after each pair or
triple of previous values:

| previous (p_{j}, p_{j+1}) | next p_{j+2} observed | M chain |
|---|---|---|
| (1, 2) | 5 (64) | 5 |
| (2, 5) | 10 (215), 11 (1,051) | 10 |
| (5, 10) | 17, 18, 19, 20, 21 | 20 |
| (20, 38) | **74** (μ⁵(K_{3,3})) | **72** |
| (1, 2, 5) | 10 (3), 11 (57) | 10 |
| (2, 5, 10) | 19 (8), 20 (78), 21 (11) | 20 |

Hence **no recurrence p_{k+1} = f(p_k, p_{k−1}) or f(p_k, p_{k−1}, p_{k−2}) is
valid for Mycielski chains in general**. The chains of K_{3,3}
(3, 6, 11, 20, 38, **74**) and of K_2 (…, 10, 20, 38, **72**) share two
consecutive values and then diverge. A recurrence fitted to the seven terms can
only be a fact about the M chain itself, and seven terms cannot test that. The
M chain is atypically low: after (1, 2, 5), 57 of 60 chains continue with 11 and
M continues with 10.

## Finding 2. pw(μ(G)) is not a function of the invariants

Explanatory variables were computed for every seed. Exact ones, by subset DP:
pw, tw, and `tight`, the minimum over optimal layouts of the number of prefixes
at width pw. Per-vertex ones: the vs of layouts forced to end (`lastmin`) or to
start (`firstmin`) at each vertex, and the number of vertices at which an
optimal layout can end (`nlast_opt`). Simple ones: n, |E|, Δ, δ, degeneracy, α,
ω, components and isolated vertices. Derived graphs: pw(μ(G) − w),
pw(G × K_2), pw(G □ K_2).

- Functional-dependency search over every subset of ≤ 3 of the 15 basic
  variables, by the minimum number of errors any lookup table on them must make:
  at least 162 of 1,252 graphs ≤ 7 v and 1,759 of 11,117 connected 8-v graphs
  (15.8%). No set comes close to a function.
- Hold-out: a table learned on ≤ 7 v and applied to 8 v is 63% accurate on
  (pw, tight) and 43% on pw alone.
- (pw, pw(μ(G) − w)), (pw, pw(G×K_2)) and (pw, pw(G□K_2)) leave 127, 432 and
  254 conflicting graphs respectively (`derived.py`).
- In the opposite direction, pw(μ(H)) ≥ pw(H) + pw(H − N[x]) + 1 *fails*
  (`nbhd.py`, 4 short on a 7-vertex graph). For H = μ(G) and x = w it would be
  the conjecture of Finding 3; it does not extend to arbitrary x.

What does organise the small cases is structural, and none of it is a formula.
For pw(G) = 1, pw(μ(G)) = 2 if every component of G is a star and 3 otherwise:
P_4 is the unique minimal witness, checked on all graphs ≤ 7 v. For pw 2, the
minimal graphs with pw(μ) = 5 = 2pw + 1 are C_5, C_6, C_7, the net and three
more.

## Finding 3 (conjecture). A Fibonacci-type lower bound

> **(F)** For every graph G with at least one vertex,
> pw(μ(μ(G))) ≥ pw(μ(G)) + pw(G) + 1.

Data: holds on all **17,260 triples** (p_j, p_{j+1}, p_{j+2}). That is 14,185 at
j = 0, which includes all graphs ≤ 7 v, all connected 8-v graphs and 1,565
graphs on 9–12 v aimed at dense and near-complete cases, plus 3,001 at j = 1 and
74 at j ≥ 2. The least slack p_{j+2} − p_{j+1} − p_j − 1 is 0 at j = 0, 1 at
j = 1, 3 at j = 2 and 4 at j = 3. It is **tight for every K_n** (n − 1, n + 1,
2n + 1) and for edgeless graphs. Tightness on the infinite family K_n is why
this inequality is taken seriously and the grid-fitted ones below are not. On
the M chain the slack is 1, 2, 4, 7, 13.

**Consequence: pw(M_9) ≥ 38 + 72 + 1 = 111** (if F holds; proved: 73).

A possible route to a proof, not carried out: μ²(G) contains three induced
copies of μ(G) sharing V, namely V ∪ V′ ∪ {w}, V ∪ V^s ∪ {z} and
V ∪ V′^s ∪ {w}, where x^s is the shadow of x in μ(μ(G)) and z the new apex. Two
of them meet only in V and are joined by the edges v^s u′ (u ∈ N(v)). A minor
argument through a join is ruled out for sparse G by edge counting.

Also on all data, and both weaker for M_9:
- **convexity**, p_{j+2} − p_{j+1} ≥ p_{j+1} − p_j (tight on edgeless G),
  giving pw(M_9) ≥ 106;
- pw(μ(G)) ≥ pw(G) + 2 when pw(G) ≥ 2 (the earlier conjecture), now on 31,186
  pairs.

Fitted inequalities, a caution (`ineq.py`). Over a grid of
p_{j+2} ≥ x p_{j+1} + y p_j + z with x, y in steps of 1/8, with z fitted on
j = 0 graphs ≤ 8 v and tested on everything else:
- **With z free**, the frontier implies pw(M_9) ≥ 140–150. These are valid on all
  17,000 small triples and are **refuted by the width-138 layout of M_9**, for
  example p_{j+2} ≥ p_{j+1} + 2p_j − 8, which implies 140.
- **With z = 0**, the top two grid choices fail the hold-out. The survivors, for
  example p_{j+2} ≥ (13/8) p_{j+1}, imply 117–118, but they are post-hoc picks
  from a grid. If any G had slack 0 and a tight (F) at once, they would fail.

Small-graph data does not constrain the scale of M_9. Only (F), which is
homogeneous and tight on an infinite family, is put forward.

## Finding 4. Exact linear laws on the K_n family, through the M chain at n = 2

pw(μ^j(K_n)), exact unless marked. K_2 is the M chain (certified values):

| j | n=1 | n=2 (M_{j+2}) | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | law (n ≥ 2) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | n − 1 |
| 1 | 1 | 2 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | n + 1 (n ≥ 3; C_5 is the exception) |
| 2 | 2 | 5 | 7 | 9 | 11 | 13 | 15 | 17 | 19 | 21 | 2n + 1 |
| 3 | 5 | 10 | 14 | 18 | 22 | 26 | 30 | 34 | 38 | 42 | 4n + 2 |
| 4 | 11 | 20 | 26 | 32 | 38 | 44 | 50 | 56 | 62 | | 6n + 8 |
| 5 | 21 | 38 | 50 | 62 | 74 | 86 | 98 | 110 | | | 12n + 14 |
| 6 | | 72 | ≤ 95 | ≤ 118 | ≤ 141 | ≤ 163 | | | | | none established |

`famfit.py` fits each law with sympy on n = 3, 4 only. Every other n agrees,
including **n = 2, the M chain, held out for j = 2..5** (5, 10, 20, 38). μ⁵(K_8)
has 287 vertices and was proved by the C program's minor step in 0.3 s. For
j ≤ 5 these graphs are easy for n ≥ 3 and hard only at n = 2. At j = 6, 900 s and
600 s runs give upper bounds 95, 118, 141 and 163. With 72 at n = 2 the first
three lie on 23n + 26, but 163 < 164, so either the line or those bounds are not
exact.

The coefficients A_j = 1, 1, 2, 4, 6, 12 and B_j = −1, 1, 1, 2, 8, 14 follow no
uniform recurrence. Step by step:
- f_1 = f_0 + 2;
- f_2 = 2f_1 − 1;
- f_3 = 2f_2;
- f_4 = 2f_3 − (2n − 3);
- f_5 = 2f_4 − 2.

The slack is n − 2, 2, 1, 2n − 3, 3, and then n + 3 if the j = 6 line holds;
at n = 2 that last value is the certified slack 5 of M_7 → M_8. Predicting M_9
from this family needs pw(μ⁷(K_3)) at 511 v and pw(μ⁷(K_4)) at 639 v, which
were not attempted.

**The second family through M, K_{a,a} (K_{1,1} = K_2), breaks.** Laws
a, 2a, 3a + 2, 5a + 5 and 9a + 11 (j = 0..4, exact for a = 1..5, with a = 1 the M
chain) hold. At j = 5, a = 1, 2, 3 give 38, 57, 74, which is not linear. So these
small-parameter linear laws can break at the next iterate, and the K_n laws
carry that risk at j = 6.

Other families saturate: their slack becomes 0. P_n (n ≥ 5) gives 1, 3, 7, 15,
i.e. 2^{j+1} − 1; stars K_{1,r} give 1, 2, 5, 11, 23 for every r; C_n (n ≥ 7)
gives 2, 5, 11, 23 for every n, then 45 at n = 8. The slack grows only along
dense or compact chains (K_n, C_5 = M_3, K_{a,a}, Petersen).

## Finding 5. Layout structure: doubling one order is within 1

`lattice.c` computes U(L, L′), the best width of a layout of μ(G) whose
originals appear in order L and whose shadows appear in order L′, with w
anywhere. It is an O(n²) lattice DP, cheap at 191 vertices. `pairdp.c` gives
the exact value over all (X, Y) prefix pairs.

- **min_L U(L, L) ∈ {pw(μ(G)), pw(μ(G)) + 1} on all 1,252 graphs ≤ 7 v.** It is
  exact on 1,160 of them, and the minimum is always attained by some optimal
  layout L of G (`test_same.py`). Taking the shadows in reverse order is worse:
  exact on 977, up to +2.
- Placing w first is optimal on all but 4 of the 1,252. Placing w last is almost
  never optimal. Shadows trailing their originals (Y ⊆ X) is exact on 91.9%,
  +1 otherwise (`pairdp_all7.csv`).
- On the M chain the doubling is not exact with the stored layouts. Doubling the
  width-38 layout of M_7 gives 77 (truth: 72). The width-72 layout of M_8
  places its M_7 originals in an order of width 40, which is not optimal for
  M_7, with an unrelated shadow order. So optimal layouts of μ(G) do not come
  from optimal layouts of G in any simple way.

## M_9 (383 vertices)

- **Proved: 73 ≤ pw(M_9) ≤ 138.** The upper bound is new; the previous one was
  145. It comes from a C program run with `-t 1800 -l`. The run ended at
  status `upper` (the search did not finish, so 138 is not proved optimal). The
  layout was re-checked here by an independent vertex-separation computation
  and is saved as `M9_layout_w138.txt`, in the input order of `M9.g6`. A
  120-second run gave 139.
- Other constructions were weaker. Doubling the width-72 M_8 layout with the
  best lag gives 144. Annealing over (L, L′), eight runs of a few minutes each
  starting from 144 and from 139, found nothing better.
- **Conjectural: pw(M_9) ≥ 111 by (F).** Nothing gives a point value.
  Extrapolation from the K_n family needs j = 7 data, and the previous report's
  growth-law fits (136–138) remain curve fits.

## Caveats

- Exactness: values marked `minor` rest on the C program's contraction-minor
  refutation, and `refutation` on its closing-order search. Both are proved
  sound per `pathwidth_solver/cli/README.md`. DP values come from our own
  subset DP; on 200 sampled DP rows (14–22 v) the C program gives the same value.
- Seed names overlap: K1 = g1 and K2 = P2 = g3 are the same graph. Duplicates
  are harmless for the "for all" checks and were excluded from the fitted
  inequalities.
- Only 74 triples at j ≥ 2. Evidence for (F) on deep iterates is thin, and the
  growing minimum slack (0, 1, 3, 4) is the most that can be said.
- The j = 6 values for K_3..K_6 are upper bounds, not exact.
- The same-order result is for n ≤ 7 only; 8! orders per graph was not run.
