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
