# The first moment on random clique covers: the Chu & Stuckey classes (started 2026-10-31)

The G(n, c/n) theorem of `reports/random_graph_first_moment.md` redone for the model the
benchmark generators actually use: each pattern is an independent random set of customers,
and the MOSP graph is the union of those cliques. The deterministic step is unchanged
(`EmptyPair.lean`), the union bound over pairs holds for any distribution, and a pair (A, R)
is empty iff no pattern meets both sides, which factorises over the independent patterns.

**What the files are.** `benchmarks/instances/MOSP_Instances/Chu_Stuckey/Random-n-m-d-k.txt`
holds patterns × pieces (first line `m n`). The pattern sizes are *not* fixed at d: for d = 2
they run from 2 to 9 with mean 2.7, for d = 10 from 3 to 24 with mean 10, every *pattern* has at
least two customers and customers with a single pattern are common (the repository's generator
note "exactly d customers per pattern" is not what the files show; an earlier version of this
README had the padding the wrong way round — corrected after `REPORT_generator.md` §0). So the model used here takes each class's *empirical* pattern sizes
as given and assumes the customer sets are uniform given their sizes; the finite bound is
rigorous in that model, and its empirical check is that no certified optimum falls below it.

**Finite bound** (`finite_bound_cs.py`, `.log`): for each of the 200 instances, with
t = ⌈(n − k)/2⌉ and q(s) = [C(n−t,s) + C(n−t+1,s) − C(n−2t+1,s)] / C(n,s),

    P(pw ≤ k) ≤ C(n,t)·C(n−t,t−1)·∏_j q(s_j),

the largest k with bound < 1 and < 0.01 gives a floor on the optimum (pw + 1). **Zero of the
200 certified optima lie below the 0.01 floor.** Class means at 125 × 125: optimum 22.8, 53.0,
78.4, 93.6, 103.2 for d = 2, 4, 6, 8, 10 against floors (< 1) of 15.2, 44.4, 70.8, 88.4, 99.6 —
within 3.5% of the optimum at d = 10, 16% at d = 4, and a third short at d = 2. For comparison,
the solver's deterministic floor (`_lower_bound`) on `Random-125-125-8-5_0` is 47 against an
optimum of 91 (CLAUDE.md, bounds section); the probabilistic floor for that class is 88.

**Asymptotic constant** (`asymptotic_cs.py`, `.log`): with m = μn and pattern size s,
g(a) = H(a, a, 1−2a) + μ·E_s ln(2(1−a)^s − (1−2a)^s), and pw ≥ (1 − 2a*)n whp where g < 0
above a*. For fixed size d at μ = 1: β* = 0, 0.286, 0.513, 0.661, 0.757 at d = 2, 4, 6, 8, 10;
with the empirical sizes slightly more (0.098, 0.321, 0.530, 0.670, 0.762 at 125 × 125). The
certified opt/n at 125 × 125 is 0.182, 0.424, 0.627, 0.749, 0.826: the same 0.06–0.10 margin
as on G(n, c/n). **At μ = 1 the constant is positive iff d > 2.003**: at d = 2 exactly the
balanced bipartition is borderline (g(1/2) = ln 2 + ln(1/2) = 0), so the first moment is
vacuous asymptotically on precisely the density class that is the hardness ridge of
`reports/ml_nature.md` §11 — where certification takes days, the cheapest lower-bound
argument says nothing.

## What this is not

A certificate. It bounds the optimum of a *random* instance of the class with high
probability; for a given instance only the deterministic empty-pair / Harper bound applies,
which the solver already computes (`satisfiability/expansion_bound.py`) and which was measured
a net loss as a search floor.

## Next steps

1. ~~Settle the generator~~ **done**, `REPORT_generator.md`: Chu & Stuckey 2009 §4.2 describe
   Bernoulli entries at the density giving d customers per pattern and rejection of disconnected
   instances; the files add "every customer ≥ 1 pattern, every pattern ≥ 2 customers"; that
   generator fits all 40 classes (mean z² 2.0). Under it, padding and rejection make empty pairs
   *rarer* than the uniform model (ratio 1.0 → 0.6), so the bound stays valid; 7,200 fresh
   instances at 30–40 customers, zero below the 0.01 floor. Measured, not proved.
2. ~~Lean~~ **done the same day**, `lean/MOSPFormalization/CliqueCoverMoment.lean`:
   `prob_coversOfPathwidthLe_le` / `prob_coversOfMospValueLe_le`, exactly the inequality of
   `finite_bound_cs.py`, in MOSP vocabulary (`coverInstance`), sorry-free, standard axioms,
   checked by enumeration of every cover at n ≤ 6, m ≤ 3 first (1,604 cases). One correction
   found by that check: with ℕ subtraction the term `C(n − 2t + 1, s)` is wrong at 2t = n + 1
   (k = 0, n odd); the Lean states `avoidCount n a r s = C(n−a,s) + C(n−r,s) − C(n−(a+r),s)`.
   The Python uses integer arithmetic and is unaffected.
3. Paper: a table of the class floors against the certified optima (Section 5 or Appendix E) —
   the generator's parameters predict the benchmark table to within a few percent at d ≥ 6.
4. ~~The threshold~~ **closed form** (`REPORT_generator.md` §3): g(1/2) = ln 2·(1 + μ(1 − d)), so
   β* > 0 iff μ(d − 1) > 1, i.e. *excess* > 1; the ridge of `ml_nature.md` §25 (generated
   ensembles) is excess 2.3–2.5. **Correction 2026-10-31 (loop0010 planning):** the Chu & Stuckey
   d = 2 classes that cost thousands of core-hours have excess 1.66–1.78 by the files, not 2–2.5
   (an earlier version of this README, the coordinator's messages and the paper's Appendix E said
   2–2.5; the paper is corrected). Also: excess 1 is edges = vertices of the incidence graph, not a
   forest; the incidence graph's giant component appears at excess ≈ 0.62 when m = n
   (`reports/excess_phase_plan.md` §0). Gao 2012's Theorem 2 is the same first moment with a factor
   dropped between two lines of its proof (harmless for m = o(n), not at m = Θ(n)); the
   restored condition at m = n is c > 2.46, not 2. Why the ridge sits at excess 2 is open.
