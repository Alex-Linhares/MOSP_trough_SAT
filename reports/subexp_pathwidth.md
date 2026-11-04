# Pathwidth after ETH: a subexponential exact algorithm, or what its absence would cost

*Ralph loop0014, plan `reports/subexp_pathwidth_plan.md`, items in
`Ralph_Loops/loop0014/iterations.md`. Started 2026-11-04. Every statement
conditional on OpenAI's counting theorem is conditional on a named `Prop`
that restates it and is never asserted (plan §0.4.1). Scratch under
`reports/scratch/subexp_pathwidth/<item>/`.*

## 0. Summary

*Written by item 11 when the loop ends. Until then, the state of the
question is §1.4 (the kill check: not killed) and the budget in §1.3.8.*

## 1. The audit and the kill check (item 01, 2026-11-04)

### 1.0 What was read, and how

- **The ETH paper**, *The Exponential Time Hypothesis is False* (OpenAI,
  17 October 2026, revised 25 October 2026; 64 pages), from the read-only
  clone `~/dev/untrusted/openai-math/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf`,
  extracted once with `pdftotext -layout` to
  `reports/scratch/subexp_pathwidth/01_audit/eth.txt` (3,814 lines;
  git-ignored, regenerable by the command in that directory's `README.md`).
  Read in full: Section 1 (lines 31–349), Section 2 (350–1148), Section 3.5
  (1393–1450), Lemma 4.8 (1921–1992), Section 5 (1993–2249), Section 6
  (2250–2518), Appendix C (2905–3000), Appendix D through D.4.2
  (3001–3330). Skimmed: Sections 3.1–3.4, 4.1–4.6, Appendices A and B.
  Nothing in the clone was built or run. A second reading of the same
  extract by one subagent, blind to this section, was used to cross-check
  §1.3: it agrees on every point (`01_audit/second_reading.md`), and adds
  that at general density the clause network of Appendix D has `n + m`
  wires, so the `n`-only exponent needs `m ≤ Dn`.
- **The formally verified statement**: `lean/ComparatorChallenges/SubexponentialSAT.lean`
  in the same clone (220 lines, read with `cat`), theorem
  `exact_count_and_sat`, proved in `lean/OAI/Algorithms/SubexponentialSAT/`
  (the comparator file itself carries the statement with a `sorry`; the
  proof is linked from `lean/formalization.yaml` and `lean/docs/378.md`).
  What it says, exactly: for each `k ≥ 2` there is one fixed primitive
  multi-tape machine and constants `C, A, S > 0`, `d, e ≥ 1`, such that on
  every CNF `F` on `n` variables with every clause of size `≤ k`, in
  OpenAI's canonical encoding of bit length `L`, the machine halts with the
  exact count on one tape and the decision bit on another in time
  `≤ C (L + 1)^d · 2^{A · n (log log(n + 16))² / √log(n + 16)}`, having visited
  at most `S (L + 1)^e` tape cells at every step. **The exponent in the
  verified statement is the weaker one, `ρ(n) = n (log log n)² / √log n`
  (the paper's Proposition 6.4); the sharper `n log log n / √log n` and the
  fixed-density `n / √log n` of Theorem 1.1 are proved on paper only
  (Appendix D) and are not in the Lean library** (`lean/docs/378.md` says
  so). Item 02 restates the verified form.
- **Held papers** (`literature/`), extracted to the same scratch directory:
  Suchan & Villanger (2009), Kitsunai, Kobayashi, Komuro, Tamaki & Tano
  (2016), Bodlaender, Fomin, Koster, Kratsch & Thilikos (2006 TR; 2012
  note), Kobayashi & Nakahata (2021), Bentert, Fomin, Inamdar & Saurabh
  (ITCS 2025), Bansal & Katzelnick (2023), Fomin & Høie (2006), Bodlaender
  (2024 survey), Kaneda, Kobayashi & Tamaki (2026), Bonnet's twin-width HDR
  (2024). Each was grepped for `ETH`, `SETH`, `subexponential`, `2^{o(n)}`
  and read where the grep hit.
- **The repository's own record**: `literature/pathwidth_solvers_README.md`
  §2, `reports/pathwidth_lower_bounds_survey.md`,
  `paper2/survey_intersection_classes.md`, `paper2/polynomial_cases.md`,
  `literature/MISSING.md`, and the OpenAlex candidate titles already on
  disk in `paper1/data/openalex_candidates.json` (the "citation graph" of
  the brief; nothing was fetched).

### 1.1 (a) The best published exact algorithms, with their bases

`n` is the number of vertices throughout; `O*` hides polynomial factors.

| parameter | best time on record | space | source | held? |
|---|---|---|---|---|
| pathwidth = vertex separation | `O(1.89ⁿ)` | exponential | Kitsunai, Kobayashi, Komuro, Tamaki & Tano, *Algorithmica* 75 (2016), for directed pathwidth; undirected is the special case (their §1: replace each edge by two arcs) | yes |
| pathwidth | `O*(1.9657ⁿ)` | exponential | Suchan & Villanger, IWPEC 2009 — the first `c < 2`; also `opt + τ` in `O*(1.89ⁿ)` | yes |
| pathwidth | `O*(2ⁿ)` / `O*(4ⁿ)` | exponential / polynomial | Bodlaender, Fomin, Koster, Kratsch & Thilikos, *Theory Comput. Syst.* 50 (2012), §5.3: Held–Karp over vertex subsets | yes |
| treewidth | `O(1.7549ⁿ)` | exponential | Fomin & Villanger, *Combinatorica* 32 (2012), via potential maximal cliques (cited as [3, 6] by Kobayashi & Nakahata 2021 for this base) | no |
| treewidth | `O(1.7347ⁿ)` *(as we recall; to be verified)* | exponential | Fomin, Todinca & Villanger, *SIAM J. Comput.* 44 (2015), the improved count of potential maximal cliques | no |
| treewidth | `O*(2ⁿ)` DP; `O*(4ⁿ)` and `O*(2.9512ⁿ)` polynomial space | — | BFKKT, TR UU-CS-2006-032 (held) = *ACM Trans. Algorithms* 9 (2012); the TR's abstract gives all three | yes (TR) |
| cutwidth, modified cutwidth, directed variants | `O*(2ⁿ)` / `O*(4ⁿ)` | exponential / polynomial | BFKKT 2012 note §5.5; **no `c < 2` is on record** — Bentert et al. (ITCS 2025) §1: "For all of the above except Pathwidth, the `O*(2ⁿ)`-time dynamic programming remains the best known algorithm — even including constant-factor approximations", and whether Cutwidth can be solved faster than `O*(2ⁿ)` is "an explicit open problem for a long time" | yes |
| bandwidth | base below 5 (`4.383`, as we recall) | exponential | Cygan & Pilipczuk, *Theoret. Comput. Sci.* 411 (2010), "Exact and approximate bandwidth" (reference [12] of Bentert et al.); Feige's `O*(10ⁿ)` (SWAT 2000) before it; the base is quoted from memory and must be verified when the paper is held | no |
| linearwidth | `O*(2ⁿ)` | exponential | Kobayashi & Nakahata (2021), from the trivial `O*(2ᵐ)` | yes |
| branchwidth | `O(3.293ⁿ)` graphs, `O*(4ⁿ)` hypergraphs | exponential | Kaneda, Kobayashi & Tamaki (2026) | yes |
| directed pathwidth, factor 2 | `O*(1.66ⁿ)` | exponential | Bentert et al. (ITCS 2025), Table 1 — an *approximation*, listed because it is the only sub-`1.89` figure for any pathwidth variant | yes |

Two readings of this table matter for the loop. First, **no `2^{o(n)}`
exact algorithm for any of these parameters is on record**, and the field
states the opposite expectation explicitly: Bentert et al. (2025) call
beating `O*(2ⁿ)` for vertex-ordering problems "challenging", and Bonnet
(JACM 2025, abstract on disk, paper not held) writes "There are
`2^{O(n)}`-time algorithms to compute the treewidth of `n`-vertex graphs,
but the Exponential-Time Hypothesis (ETH) was only known to imply that
`2^{Ω(√n)}` time is required" and then proves `2^{Ω(n)}` under ETH (§1.2).
Second, every base below 2 was obtained by the same move — Suchan &
Villanger's and Kitsunai et al.'s algorithms restrict the Held–Karp
recursion to *committed* or *balanced* vertex sets, i.e. they shrink the
state lattice of `reports/checkpoint_relaxation.md` §10 by a constant
factor in the exponent, which is exactly what §10 measured our search to
be already near the floor of. None of them changes the parameter from
`n`; a `2^{o(n)}` algorithm would be a different kind of object.

What this table is not: it does not list FPT algorithms (`pw ≤ k` in
`2^{O(k²)} n` or `f(k) n`, Bodlaender & Kloks 1996, held), because for
`k = Θ(n)` those are worse than `2ⁿ`; and it does not list our own solvers.

### 1.2 (b) ETH- and SETH-conditional lower bounds on computing these parameters

The question is lower bounds on *computing the width*, as a function of
the number of vertices. Lower bounds on problems *parameterised by* a
width (Independent Set in `(2 − ε)^{tw}`, Dominating Set in `(3 − ε)^{pw}`,
the `k`-Clique / CSP bounds of Marx 2010, the primal-pathwidth SETH of
Lampis, SODA 2025, which is on disk as an OpenAlex title) are a different
family; they are the subject of item 10 and are only named here.

| parameter | conditional bound | hypothesis | reduction it rests on | vertex blow-up | source | held? |
|---|---|---|---|---|---|---|
| treewidth | no `2^{o(n)}` exact algorithm | ETH | "a simple, self-contained reduction from 3-SAT to Treewidth" | **linear** in the formula size by the statement `2^{Ω(n)}` (the abstract gives no explicit figure; the paper is not held) | Bonnet, *Treewidth inapproximability and tight ETH lower bound*, arXiv 2406.11628 (2024), *J. ACM* (2025); abstract in `paper1/data/openalex_candidates.json`; the survey Bodlaender (2024, held) states its approximation form as Theorem 9 | no |
| treewidth | `δ`-approximation needs `2^{Ω(n / logᶜ n)}` for some `δ > 1`, `c > 0`; the survey quotes it as `2^{n^{1−o(1)}}` | ETH | the same reduction | quasi-linear | Bonnet 2025, via Bodlaender 2024 §5 Theorem 9 | survey held |
| treewidth | `1.00005`-approximation is NP-hard | P ≠ NP | the same reduction | — | Bonnet 2025 | no |
| treewidth, pathwidth | before Bonnet: only `2^{Ω(√n)}` under ETH, because "all the known hardness constructions use Cutwidth or Pathwidth on bounded-degree graphs as an intermediate step in a long chain of reductions, for which neither inapproximability nor sharp ETH lower bound is known" | ETH | the classical chain (3-SAT → … → cutwidth / pathwidth on bounded degree → treewidth) | quadratic somewhere in the chain (hence the `√n`) | Bonnet 2025, abstract | no |
| treewidth, pathwidth | no polynomial-time constant-factor approximation | Small Set Expansion hypothesis | from SSE | not an exponential-time statement | Wu, Austrin, Pitassi & Liu (2014), via Bodlaender 2024 Theorem 8 | survey held |
| pathwidth, cutwidth, bandwidth | **none found** of the form "no `2^{o(n)}` unless ETH/SETH fails" in any held paper or any title on disk | — | — | — | — | — |

Notes on the table.

- **Pathwidth specifically.** We found no published sentence of the form
  "pathwidth has no `2^{o(n)}` algorithm unless ETH fails" in the held
  papers or on-disk titles. The NP-hardness sources held are Lengauer
  (1981, vertex separation via pebbling), Megiddo, Hakimi, Garey, Johnson &
  Papadimitriou (1988, search number), and, secondarily, Arnborg, Corneil &
  Proskurowski (1987, treewidth of cobipartite graphs; not held, recorded in
  `paper2/to_fetch.md`) with Möhring (1996, AT-free graphs have `pw = tw`;
  not held), which together make pathwidth NP-hard on cobipartite graphs.
  Whether Bonnet's construction yields graphs with `pw = tw` — which would
  transfer his linear ETH bound to pathwidth at blow-up 1 — cannot be
  decided from the abstract. **This is the first thing item 03 must
  settle**, and it changes what item 07 can prove: if the only linear
  reduction into pathwidth is from 3-SAT, then a `2^{o(n)}` pathwidth
  algorithm refutes ETH and nothing else, and ETH is the hypothesis the
  counting theorem already refutes. The surviving hypotheses a `2^{o(n)}`
  pathwidth algorithm could touch are then only those with their own linear
  reduction into pathwidth, and none is on record.
- **The classical chain is where the quadratic loss sits.** Bonnet's
  abstract says the `√n` of the pre-2024 bound comes from the chain through
  cutwidth or pathwidth on bounded-degree graphs. Item 03 catalogues that
  chain step by step with each blow-up (Monien & Sudborough's cutwidth
  hardness on maximum degree 3, the Kashiwabara–Fujisawa / Lengauer
  vertex-separation hardness, and the ACP cobipartite construction).
- **Bisection route, as a candidate linear chain for cobipartite
  treewidth = pathwidth** (to be verified in item 03, nothing here is
  checked): 3-SAT → Max Cut on sparse graphs (linear, with sparsification)
  → Minimum Bisection (linear: add isolated vertices) → treewidth of a
  cobipartite graph (ACP 1987; blow-up unverified) = pathwidth (Möhring
  1996). If every step is linear, ETH alone already gave a linear bound for
  pathwidth on cobipartite graphs before Bonnet; Bonnet's abstract suggests
  this was not on record, which makes us suspect the ACP step is not
  linear. Either way the hypothesis at the top is ETH.
- **SETH-conditional bounds on computing a width**: none found. SETH
  bounds in the width literature are about problems parameterised by
  width (Lokshtanov, Marx & Saurabh 2018; the ETH paper's own §1.1.3 names
  exactly these and says they "also follow from the hypothesis that
  unrestricted CNF-SAT admits no `2^{(1−δ)n}` algorithm", which Theorem 1.1
  does not touch because it is for fixed `k`).

**Papers this item needs and does not hold** (for item 11's
`literature/MISSING.md`): Bonnet 2024/2025 (arXiv 2406.11628); Fomin &
Villanger 2012; Fomin, Todinca & Villanger 2015; Cygan & Pilipczuk 2010;
Arnborg, Corneil & Proskurowski 1987; Möhring 1996; Monien & Sudborough
1988; Lampis, *The primal pathwidth SETH*, SODA 2025 (arXiv 2403.07239).

### 1.3 (c) What the counting method needs from a problem — in our words

This is the account every later item cites in place of the paper. Line
numbers refer to `01_audit/eth.txt`.

**1.3.1 The object.** The method computes one thing: a sum over the
Boolean cube of a product of local factors,

    Z = Σ_{x ∈ {0,1}ⁿ} Π_{f ∈ F} Φ_f(x|_{I_f}),

where each factor `Φ_f` reads the variables in its scope `I_f ⊆ [n]` and
takes values in a commutative `Q`-algebra or, in the tensor form, in
`(Z/2^P Z)[V]/(V^ℓ)` (lines 1155–1181, 3007–3014). For a `k`-CNF the
factors are the clause satisfaction polynomials and `Z = #F` (376–391).
Everything else in the paper is machinery for evaluating this sum faster
than `2ⁿ`.

**1.3.2 The parameter.** The exponent is in `n`, the dimension of the cube
summed over — the number of declared Boolean variables — never the number
of clauses or the input length, which enter polynomially (Theorem 1.1,
56–62; Theorem 2.2, 1129–1136). In the tensor-contraction form (Theorem
D.1, 3017–3028) the parameter is `s`, the number of **wires**: a bipartite
tensor network has one Boolean bit per edge and one tensor per vertex, the
contraction sums over all `2^{|E|}` wire assignments the product of the
vertex entries, and the time is `(s + L)^{O(1)} 2^{O(s / √log s)}` when the
network has at most `Cs` edges. For a formula, a clause is a vertex with
one port per variable and a variable occurring `d` times is a tree of `d−2`
trivalent equality tensors (3045–3056), so **the number of wires is the
total variable–constraint incidence, `Σ_f |I_f|`**, up to a constant; for a
`k`-CNF with `m` clauses that is `O(n + km)`, which is `O(n)` only at fixed
density `m ≤ Dn` — hence the two bounds of Theorem 1.1. **The quantity a
problem is charged for is its total incidence**, not its number of
variables and not its clause width.

**1.3.3 The requirements**, as the proofs use them.

- *R1, Boolean variables with bounded-degree local factors.* Each factor is
  a polynomial of degree `≤ k` in its inputs, with `k` fixed (the
  satisfaction polynomial of a clause of width `k` has degree `k`;
  Theorem 2.2 takes equations of degree `≤ k` with polylogarithmically many
  monomials, 1129–1136).
- *R2, linear total degree.* The product of all factors must have total
  degree `d = O(n)` in the variables (392–393, 1179–1181, 2127): the Taylor
  recovery needs `q = ⌊dR/Q⌋ = o(n)` coefficients per point, and the cost
  `Σ_{j ≤ q} 2^j C(n, j)` is `2^{o(n)}` only when `q = o(n)` (651–700). With
  `m` clauses of width `k` this is `d ≤ km`, so **the number of constraints
  must be `O(n)`** — either by assumption (fixed density) or by the parity
  tests of Section 6, which replace `Bn` clauses by `O(n)` tests each reading
  polylogarithmically many clauses and keep the degree linear by the
  truncation trick of Lemma 5.2 (2056–2115).
- *R3, bounded incidence per variable after branching.* Each variable may
  lie in at most `b = (log n)^{O(1)}` factor scopes and each scope may have
  at most `w = (log n)^{O(1)}` variables (Lemma 4.8, 1930–1947). The paper
  reaches this by branching on the `≤ n/√log n` most frequent variables
  (2176–2192, "at most `2^{n/√λ}` branches"), which costs exactly the
  exponent it can afford; so a problem may have a few high-degree variables
  but not many.
- *R4, the groups must be separable by few measurements.* The construction
  partitions the variables into `r = Θ(√log n / (log log n)²)` groups of
  size `2n/r`, assigns each factor to a group, and arranges that a factor's
  dependence on every other group passes through `≤ 2τn` integer linear
  measurements with coefficient sum `≤ D` (Definition 2.1, 463–489;
  Definition 3.1, 1186–1208). This is supplied by the paper's own
  construction for *any* scopes satisfying R3 (Section 4); the problem
  contributes nothing here and cannot break it.
- *R5, exact arithmetic over a ring where "positive count" is readable.*
  Counts are recovered modulo `2^{n+1}` (2015, 3057–3060); a problem whose
  answer is not an integer count or a sum over such a ring is not covered.
- *R6 (tensor form only), the local tensors may be large and expensive.*
  Theorem D.1 allows a vertex of degree up to `⌈s^{9/10}⌉`, polynomially
  many vertices, and **an entry-evaluation time of `(s + L)^b 2^{A s^{9/10}}`**
  (3017–3028). So a single constraint may read `s^{9/10}` wires and its
  truth table may be computed by brute force over its ports. The budget is
  the wire count, not the width of any one constraint.

**1.3.4 Where `2^{n/√log n}` comes from.** Three costs multiply (2.11,
658–667; 3.16, 1437–1441): the Taylor data `Σ_{j ≤ q} 2^j C(n, j)`, with
`log` of order `n (R/Q) log(2Q/R)`; the measurement tuples
`(2D + 1)^{2τn}`; and the assignments inside one group, `2^{2n/r}`. Under
the choice `r = Θ(√log n / (log log n)²)`, `Q = Θ(log n / log log n)`,
`R = Θ(√log n)`, `τ = 1/(r log n)`, `D = r^{2Q} ≤ (2n)^{1/128}` (2.10,
641–648; 4.17, 1930–1940) all three are `O(n (log log n)² / √log n)`
(687–700), i.e. they are balanced, and the group term `2n/r` is the one
that names the shape: the method enumerates assignments to groups of
`2n/r = Θ(n (log log n)² / √log n)` variables, and the price of making the
groups independent is the other two terms. The parameter `R` must be much
smaller than `Q` (few Taylor coefficients) and much larger than `√Q` (few
measurements, by the binomial tail `2 exp(−R²/8Q)`, 842–855), which is why
`R = Θ(√log n)` and `Q = Θ(log n)` up to log-log factors, and why the gain
is `√log n` and not more. The sharper Appendix D bound replaces the single
global Taylor step by a recursion on wires whose exponents sum
geometrically to `O(s / √log s)` (3029–3040).

**1.3.5 What breaks when the width is not fixed.** The clause width `k`
enters in three places: the per-clause degree (R1–R2); the sparsification
occurrence bound `B = O_k((σ⁻¹ log(2/σ))^{k−1})` of Lemma 6.3 (2460–2472),
which must stay `(log n)^{O(1)}` for Lemma 4.8 and is `(log n)^{Θ(k)}`;
and the degree `R = (β + 3)⌈√λ⌉` of the replacement rows, whose constant
`β` is the exponent of `log n` bounding scope and incidence (1930–1940),
so that the final exponent is `O_β(ν²/√λ)` with the constant growing with
`β` (4.18, 1944–1947). With `k` growing with `n`, none of these is
controlled, and the paper says so: "Theorem 1.1 gives a running-time
guarantee for each fixed clause width `k`, while this hypothesis
[unrestricted CNF-SAT needs `2^{(1−δ)n}`] allows the width to grow with
`n`" (235–236). **But width is not what a width problem is short of.** A
cardinality constraint "at most `t` of these `w` bits" has unbounded clause
width as a CNF, yet costs only `O(w)` auxiliary variables and clauses when
compiled to a linear-size circuit and then to 3-CNF — the paper does this
itself for the threshold in Corollary 1.2 (86–91) and for "exactly one
selected edge meets each vertex" in Corollary 1.3 (116–119) — and in the
tensor form it is a single vertex of degree `w ≤ s^{9/10}` with a
polynomial-time entry (R6). So threshold constraints cost their width in
*incidence*, and that is the whole cost. The obstacle for a width
parameter is R2–R3 read together: **the sum of the widths of all
constraints must be `O(n)` for a `2^{O(n/√log n)}`-type bound, and
`o(n √log n)` for any `2^{o(n)}` bound at all.**

**1.3.6 Counting, deciding, witnesses, weights.** The method is a counting
method whose count decides existence: "Testing `#F > 0` also decides
satisfiability" (48); a satisfying assignment is found by the standard
self-reduction, and an exactly uniform one by choosing each bit by the two
conditional counts (68–71); uniform sampling of preimages likewise
(2994–2996). It handles weighted sums: the factors may take values in any
commutative `Q`-algebra (1161–1163) or in `(Z/2^P)[V]/(V^ℓ)` (3021), so
generating polynomials truncated at degree `ℓ` and counts of structured
objects (all `q`-colourings, all perfect matchings, Corollary 1.3) are
within reach at no extra exponent. It does not optimise directly;
"`pw ≤ k`?" would be decided for each `k` separately, which is a
polynomial factor. So **the method decides structured existence** —
anything whose witnesses are the accepting assignments of a system
satisfying R1–R5 (or a network satisfying R6) — and the counting is never
the obstacle; the encoding size is.

**1.3.7 The paper's own caveats, verbatim.** "Note that runtime bounds of
the form `2^{o(n)}` do not transfer under general polynomial-time
reductions (`2^{n^{o(1)}}` would be needed for this), so our result does
not imply that general NP problems admit subexponential time algorithms"
(95–98). "To obtain a faster algorithm for a target problem from our SAT
algorithm, we need a reduction in the other direction, from that problem to
fixed-width SAT, that controls the number of variables" (237–238), with
Set Splitting (one variable per element) as the worked example
(239–243). The paper says nothing about permutation or ordering problems,
nor about any width parameter; its Corollary 1.3 covers exactly the
problems with one variable per vertex (independent sets) or `q` per vertex
(colourings) or one per edge with a linear-size checking circuit (perfect
matchings). This agrees with plan §0.2.

**1.3.8 The budget for pathwidth, stated once.** Let `G` have `n` vertices.
By the verified statement, an encoding of "`vs(G) ≤ k`" as a `k₀`-CNF
(`k₀` fixed) on `N` variables, satisfiable iff the answer is yes, decides
it in `2^{O(N (log log N)² / √log N)} · poly`; by the paper-only Theorem
D.1, an encoding as a bipartite tensor network with `s` wires, polynomial
vertex count, degrees `≤ s^{9/10}` and `2^{O(s^{9/10})}`-time entries decides
it in `2^{O(s / √log s)} · poly`. Hence `2^{o(n)}` needs

    N = o(n √log n / (log log n)²)   (verified route)   or   s = o(n √log n)   (paper route),

with unknown constants. The two encodings on record are far outside: the
position encoding `x[v, t]` has `N = Θ(n²)` variables and `Θ(n²)`-width
cardinality constraints (incidence `Θ(n³)` before auxiliary variables, `Θ(n²k)`
with totalizers); the nested-chain encoding of
`reports/checkpoint_relaxation.md` §8 has `2n²` variables. A permutation
carries `n log₂ n` bits, so **any encoding whose Boolean variables determine
the layout has `N ≥ n log₂ n`, which already exceeds the verified budget
by a factor `(log log n)² · √log n`** — not a proof of absence, since the
accepting assignments need not determine a layout (a certificate of
"`vs ≤ k`" may be a different object), but the reason items 04, 05 and 09
look for a witness *other than* the ordering: nested sets, a chain in the
lattice `F_k`, or a class-specific `O(n)`-bit object. That is the
precise form of plan §0.4.3's "`O(n)`-bit layouts under bounded-width
local constraints": **total incidence `o(n √log n)`, with constraints of
any width.**

### 1.4 The kill check (plan §0.6)

- **Is a `2^{o(n)}` exact pathwidth algorithm on record?** No. The best
  bases are `1.89` (Kitsunai et al. 2016) and `1.9657` (Suchan & Villanger
  2009); the 2025 sources (Bentert et al.; Bonnet) treat `2^{Ω(n)}` as the
  expected truth, Bonnet proving it for treewidth under ETH. Nothing in the
  OpenAI collection concerns pathwidth, vertex separation, layouts or
  minors (`CONTENTS.md` grepped for treewidth, pathwidth, bandwidth,
  cutwidth, vertex separation, linear arrangement: the hits are families
  089 and the Weisfeiler–Leman witnesses, both *bounded* treewidth as a
  hypothesis, not its computation).
- **Does the method demonstrably fail on every NP-hard width problem?**
  Not demonstrated. The method applies to any NP-hard problem with an
  existence-preserving encoding of total incidence `o(n √log n)` in the
  problem's own size parameter (§1.3.8); the paper exhibits such encodings
  for independent sets, colourings, perfect matchings and Set Splitting.
  For width parameters no such encoding is on record and none is excluded:
  the only general obstruction we can state is the `n log₂ n`-bit size of a
  layout, which applies to encodings that *determine* the layout and not to
  certificates of width in general. The kill criterion asks for a
  demonstration; there is none in either direction.

**Verdict: the loop is not killed.** What items 02–09 must do has sharpened:
item 02 restates the *verified* `ρ(n)` statement (not Appendix D); item 03
starts from Bonnet's reduction and the question whether its graphs have
`pw = tw`; items 04–05 look for a certificate of "`vs ≤ k`" with total
incidence `o(n √log n)` on an NP-hard class, with constraint width free;
item 06's measurement of `|F_k|` and `|R_f|` is the empirical side of the
same question (is the chain object ever `2^{o(n)}` on such a class).

### 1.5 What this does not claim

- It does not assert the counting theorem, and nothing in this section
  depends on its truth; §1.3 reports what the paper *states* it needs.
- "No `2^{o(n)}` algorithm is on record" is a statement about the held
  papers, the titles on disk and the collection's index on 2026-11-04,
  not about the literature; and "we found no ETH-conditional bound for
  pathwidth" likewise.
- The bases marked "as we recall" (treewidth `1.7347`, bandwidth `4.383`)
  are not verified against a held copy and must not be quoted from here.
- The bisection chain of §1.2 is a candidate, unchecked; the blow-up of
  the Arnborg–Corneil–Proskurowski step is unknown to us.
- The budget of §1.3.8 carries the paper's unknown constants; it says what
  order an encoding must have, not that an encoding of that order would
  run.
- No reduction or encoding was stated in this item, so the brute-force
  check to 7 vertices required of every reduction (TASK.md) has nothing to
  check here; `01_audit/README.md` says so and records the regenerate
  commands.

### 1.6 Regenerate

    pdftotext -layout ~/dev/untrusted/openai-math/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf \
        reports/scratch/subexp_pathwidth/01_audit/eth.txt
    for f in <held PDFs listed in 01_audit/README.md>; do pdftotext -layout literature/$f.pdf reports/scratch/subexp_pathwidth/01_audit/$f.txt; done
    grep -n -i -E 'exponential time hypothesis|\bETH\b|SETH|subexponential|2\^\{o\(n\)' reports/scratch/subexp_pathwidth/01_audit/*.txt
    cat ~/dev/untrusted/openai-math/lean/ComparatorChallenges/SubexponentialSAT.lean

## 2. The formal frame: `SubexpCount`, `PathwidthSubexp`, `PathwidthSubexpOn` (item 02, 2026-11-04)

Two files under `lean/MOSPFormalization/SubexpPathwidth/`, both imported by
`lean/MOSPFormalization.lean`, `lake build` clean, no `sorry`, no `axiom`,
every declaration on `[propext, Classical.choice, Quot.sound]`
(`reports/scratch/subexp_pathwidth/02_frame/axiom_check.log`). Every
later item of the loop states its theorems against the three `Prop`s
defined here.

### 2.1 The decision: the machine model is copied verbatim

The item asked whether to copy OpenAI's `PrimitiveMachine` model or to use
an abstract "decidable predicate with a time function". **Copied, verbatim,
into its own file.** `PrimitiveMachine.lean` is lines 1–190 and 220 of
`lean/ComparatorChallenges/SubexponentialSAT.lean` in the clone
(commit `4eaee875`, 2026-10-29; file SHA-256 `4183b205…76685`), i.e. every
definition of the comparator file — the CNF syntax and `count`, the
canonical encoding `encodeCNF` and `formulaBitLength`, `PrimitiveMachine`
(a multi-tape machine over Mathlib's `Turing.TM0.Stmt` and `Turing.Tape`,
one scanned tape per state, halting into a `Bool`), `Trace`, the located
configuration that monitors visited cells, `runtimeScale` and
`runtimeBound` — with the namespaces unchanged, under an Apache-2.0 header
naming the origin, and **without** lines 191–219, the theorem
`exact_count_and_sat` and its `sorry`. The copy was checked byte for byte
when made (`02_frame/README.md`); it compiles unchanged on our Mathlib
(`1192d624`, toolchain `v4.34.0-rc2` against their `v4.34.1`). The clone
itself was read with `cat` only and nothing in it was built or run.

Why copy and not abstract:

1. **Fidelity.** With the model copied, `SubexpCount k` is the comparator's
   statement *character for character* (`02_frame/body_diff.log`: the 23
   lines of the body are identical after stripping indentation and the
   theorem's `:= by`). An abstract notion would be our translation of the
   theorem into another model, and the translation — "their machine is
   polynomially equivalent to this notion" — would be one more thing to
   trust, with nothing in Lean to check it against.
2. **Non-vacuity.** Without a cost model, "`∃ f` computing the count and
   `∃ T` subexponential with `time ≤ T`" is provable outright (take the
   mathematical `count` and any `T`): the hypothesis would be a theorem and
   every conditional result empty. An abstract notion that is not vacuous
   must carry its own cost axioms — more assumptions, not fewer.
3. **No proof is copied.** The copied file contains definitions only. A
   definition cannot be false, only inapposite, and whether
   `PrimitiveMachine` is the right notion of "algorithm" is visible on the
   page (it is an ordinary multi-tape Turing machine with a unary-framed
   input; `TASK.md`'s "never import it into our `lean/`" is honoured, the
   text is ours now under the licence).
4. **The price**, recorded so that items 07–09 budget for it: a transfer
   theorem `SubexpCount k → PathwidthSubexpOn C` is a statement about one
   machine model, so it needs no translation between models, but it does
   need a **composition fact** — a polynomial-time primitive machine that
   writes `encodeCNF F` from `encodeGraph G k`, run before the counting
   machine, with the time bounds adding — which the comparator does not
   state and the collection proves, if at all, inside its own library. In
   this development it would be a further named `Prop` (`MachineCompose`
   or the like), in the pattern of `CubicPathwidthBound τ`. The same fact
   is needed on the negative side (`PathwidthSubexp → X ∈ 2^{o(N)}`). So
   every transfer theorem of this loop will read
   `SubexpCount k → ⟨composition⟩ → ⟨the encoding's correctness and size⟩ → …`,
   and the encoding's correctness is the only part that is *about
   pathwidth*; it is the part items 08 and 09 prove.

Licensing: Apache-2.0 permits the copy with attribution and notice; the
header carries both, `literature/MISSING.md` records the origin, and the
rest of the development stays MIT.

### 2.2 The hypothesis, exactly

```lean
def SubexpCount (k : ℕ) : Prop :=
  ∃ (machine : Computation.PrimitiveMachine)
    (countTape answerTape : Fin machine.tapeCount) (C A S : ℝ) (d e : ℕ),
    0 < C ∧ 0 < A ∧ 0 < S ∧ 0 < d ∧ 0 < e ∧
    ∀ (n : ℕ) (F : SAT.CNF (Fin n)), SAT.WidthAtMost k F →
      ∃ (time : ℕ) (final : LocatedCfg machine),
        Trace (locatedStep machine) time (locatedInit machine (encodeCNF F)) final ∧
        ⟨count tape = countWord (count F)⟩ ∧ ⟨answer tape = decide (0 < count F)⟩ ∧
        final.config.state = Sum.inl (decide (0 < SAT.count F)) ∧ … ∧
        (time : ℝ) ≤ runtimeBound C A d (formulaBitLength F) n ∧
        ⟨every prefix visits ≤ S (L + 1)^e cells⟩

def ExactCountAndSat : Prop := ∀ k : ℕ, 2 ≤ k → SubexpCount k
```

`runtimeBound C A d L n = C (L + 1)^d · 2^(A · ρ(n))` with
`ρ(n) = n (log log(n + 16))² / √log(n + 16)` (`runtimeBound_eq`, by `rfl`).
This is the **verified** statement and its weaker exponent (§1.0); the
paper's `n log log n / √log n` and the fixed-density `n / √log n` are not
in the collection's Lean library and are not restated. Neither `Prop` is
proved, and `allowed_sorries.txt` is still empty: the gate counts `sorry`
and `axiom` and finds none.

Proved: `SubexpCount.anti` (`SubexpCount k → k' ≤ k → SubexpCount k'`, the
same machine, since a width-`≤ k'` formula has width `≤ k`) and
`ExactCountAndSat.subexpCount`. So a theorem that needs `SubexpCount 3`
may assume `SubexpCount k` for any `k ≥ 3`, and the comparator gives all
of them.

### 2.3 The target, in the same model

```lean
abbrev GraphClass := ∀ n : ℕ, SimpleGraph (Fin n) → Prop

noncomputable def encodeGraph (G : SimpleGraph (Fin n)) (k : ℕ) : List Bool :=
  encodeNat n ++ encodeNat k ++ ⟨the n² adjacency bits, row by row⟩
-- encodeGraph_length : (encodeGraph G k).length = (n + 1) + (k + 1) + n * n

def IsSubexpExponent (f : ℕ → ℝ) : Prop := f =o[atTop] (fun n : ℕ => (n : ℝ))

def PathwidthSubexpOn (C : GraphClass) : Prop :=
  ∃ (machine : PrimitiveMachine) (c : ℝ) (d : ℕ) (f : ℕ → ℝ),
    0 < c ∧ IsSubexpExponent f ∧
    ∀ (n : ℕ) (G : SimpleGraph (Fin n)) (k : ℕ), C n G →
      ∃ (time : ℕ) (final : machine.Cfg),
        Trace machine.step time (machine.init (encodeGraph G k)) final ∧
        final.state = Sum.inl (decide (pathwidth G ≤ k)) ∧
        (time : ℝ) ≤ c * ((encodeGraph G k).length + 1) ^ d * 2 ^ (f n)

def PathwidthSubexp : Prop := ⟨the same, over every G⟩
```

The choices, each deliberate:

- **The parameter is `n`, the number of vertices.** `f = o(n)` is
  `Asymptotics.IsLittleO` against `n`, so `2^(f n)` is `2^{o(n)}` in the
  standard sense (quasi-polynomial time qualifies, `2^{εn}` for a fixed
  `ε > 0` does not; `O*(2ⁿ)` and the `1.89ⁿ` of §1.1 do not). The
  polynomial factor is in the input length `L = n² + n + k + 2`, never the
  exponent, which is what `TASK.md`'s "every statement names its
  parameter" asks: on dense graphs `L = Θ(n²)` and `2^{o(L)}` would be
  trivial.
- **The input is canonical and the model is the comparator's.** `n` and
  `k` in the collection's unary code (`encodeNat`), then the adjacency
  matrix; the decision is read off the halting state, as the comparator
  reads its answer bit; the step is the plain `machine.step` (no space
  monitoring, no space bound: this is a time statement).
- **`pathwidth` is `Pathwidth.lean`'s**, the minimum width of a
  `PathDecomposition`; by Kinnersley (`vertexSeparation_eq_pathwidth`) the
  decision bit equals `decide (vertexSeparation G ≤ k)`
  (`decide_pathwidth_le_eq`), and `pathwidthSubexpOn_iff_vertexSeparation`
  restates the `Prop` with `vertexSeparation`, for item 08, whose
  statements are made against `VertexSeparation.lean`. Decidability of the
  comparisons is classical (`Classical.propDecidable`), as a `Prop` may be.
- **A class is `∀ n, SimpleGraph (Fin n) → Prop`.** The item's
  `C : SimpleGraph → Prop` is not a type (`SimpleGraph` takes a vertex
  type). Nothing requires a class to be closed under isomorphism; a
  theorem about an isomorphism-closed class (cobipartite, cubic, …) states
  the closure itself if it needs it.
- **`k` is unrestricted.** For `k ≥ n − 1` the answer is always `true`; a
  machine may use that or not. Since `L` contains `k`, the polynomial
  factor is `poly(n² + k)`, not `poly(n)`; harmless (a machine answers
  `true` once it has read `n + 1` ones of `k`'s code), and a theorem that
  prefers `poly(n)` may restrict to `k < n`.
- **Single-machine form.** One machine and one `f = o(n)` for every
  input, as in the comparator; Impagliazzo & Paturi's negation of ETH is
  the weaker `∀ ε > 0 ∃ machine in 2^{εn}`. The source hypothesis is
  single-machine, so a transfer from it lands in the single-machine form,
  which implies the `∀ ε ∃` form; a theorem that starts from the `∀ ε ∃`
  form would need the predicate restated.

Proved: `PathwidthSubexpOn.mono` (a machine for `C` is a machine for every
subclass) and `pathwidthSubexp_iff` (`PathwidthSubexp ↔
PathwidthSubexpOn (fun _ _ => True)`), the two lemmas the item asked for,
each by unpacking the existential.

### 2.4 Glue between the two: the verified bound has the target's shape

Two further lemmas, so that a transfer theorem can move from the
comparator's bound to the target's without analysis of its own:

- `Trace.config_of_locatedStep`: a trace of the located step projects to a
  trace of the plain step on the underlying configurations
  (`LocatedCfg.monitor_config : (c.monitor x).config = x`, then induction
  on the trace). So `SubexpCount`'s `time` is a bound on `machine.step`,
  the step `PathwidthSubexpOn` uses.
- `runtimeScale_isLittleO`: `ρ(n) = o(n)`; hence
  `isSubexpExponent_runtimeScale A : IsSubexpExponent (fun n => A * ρ n)`
  for every `A`. The analytic content is `tendsto_log_sq_div_sqrt`,
  `(log y)² / √y → 0`, from Mathlib's `isLittleO_log_rpow_rpow_atTop`
  (`(log y)^2 = o(y^{1/2})`), composed with `log(n + 16) → ∞`.

With these, `SubexpCount k` already has the form "a primitive machine
counts, on canonical CNF input, in time `c (L + 1)^d 2^(f n)` with
`f = o(n)`" — the same form as `PathwidthSubexpOn`, with the CNF's
variable count in place of the vertex count. **That substitution is the
whole question of the loop**: a transfer needs an encoding whose variable
count is `o(n √log n / (log log n)²)` (§1.3.8), and §1.3.8's reason that
no encoding on record comes close stands.

### 2.5 What a transfer theorem will look like, given this frame

For the record, the shape items 08–09 would prove, so that the frame is
seen to be sufficient. Positive direction (item 09), on a class `C`:

    SubexpCount k →
    MachineCompose →                                   -- the named composition Prop of §2.1
    (∃ enc : (n : ℕ) → (G : SimpleGraph (Fin n)) → ℕ → CNF (Fin (N n G)),
       (∀ n G k, C n G → WidthAtMost k (enc n G k) ∧ (0 < count (enc n G k) ↔ pathwidth G ≤ k)) ∧
       (fun n => A · ρ (N n)) = o(n) ∧ ⟨enc computable in polynomial time by a primitive machine⟩) →
    PathwidthSubexpOn C

The middle hypothesis is the one about pathwidth — the encoding's
correctness (`sat ↔ pw ≤ k`, checked to 7 vertices before it is stated,
proved against `VertexSeparation.lean`) and its size — and is where all of
the loop's mathematics sits. Negative direction (items 07–08), for a
problem `X` with instances of size `N` and a reduction `red` to pathwidth:

    PathwidthSubexp →
    MachineCompose →
    (∀ I, X I ↔ pathwidth (red I) ≤ k I) ∧ (vertices of red I ≤ a · N(I) + b) ∧ ⟨red polynomial-time⟩ →
    XSubexp

with `XSubexp` defined for `X` in the style of `PathwidthSubexp` when item
07 fixes `X`. The linearity condition "vertices `≤ a N + b`" is what makes
`f(a N + b) = o(N)` from `f = o(n)`; a quadratic reduction gives
`f(N²) = o(N²)`, which is nothing (plan §0.4.2).

### 2.6 Checks

- `lake build`: clean, both files imported by `MOSPFormalization.lean`
  (the gate's import check).
- Axiom audit: 17 declarations, all `[propext, Classical.choice, Quot.sound]`
  (`02_frame/axiom_check.lean`, `.log`).
- Textual fidelity of the hypothesis: `02_frame/body_diff.log` (identical).
- One refuter subagent read both files blind to this section, looking
  for a vacuous or trivially refutable `PathwidthSubexp` (a zero-step
  trace, a degenerate machine, a loophole in the bound, the `k`
  parameter, the decidability instances): none found. It confirmed in
  Lean that `machine.init` never sits in a halting state, so `Trace.refl`
  closes no loophole, and that `#print SubexpCount` with full names
  resolves every constant to the copied `OAI.*` namespaces; the only
  provable instances of `PathwidthSubexpOn` it could build are the
  expected degenerate ones (the empty class; finite classes by lookup).
  Its two referee points are folded into §2.3 (the `k` in `L`; the
  single-machine form).
- Verbatim copy: `diff` empty when made; regenerate per `02_frame/README.md`.
- No reduction or encoding of pathwidth is stated here, so the brute-force
  check to 7 vertices has nothing to apply to; `encodeGraph_length` is the
  one computation and is proved.
- `python3 Ralph_Loops/loop0014/gate.py`: see PROGRESS.md for the run.

### 2.7 What this does not claim

- That `SubexpCount k` holds for any `k`, or that `ExactCountAndSat` holds:
  both are `def`s of `Prop`s with no proof and no axiom behind them. That
  the collection's proof of `exact_count_and_sat` is correct is not
  examined and not relied on.
- That `PathwidthSubexp` or any `PathwidthSubexpOn C` holds; nothing here
  is an algorithm.
- That the `PrimitiveMachine` model is robust (that it simulates a RAM or
  a standard multi-tape machine with polynomial overhead): plausible for
  an ordinary multi-tape Turing machine, not proved, not needed by any
  statement of this item.
- That `SubexpCount` restates the *paper's* Theorem 1.1: it restates the
  verified comparator, whose exponent is weaker (§1.0).
- That the composition fact of §2.1 holds: it is not yet even stated; item
  07 or 09 states it as a named `Prop` when first needed.
- That `encodeGraph` is the input format any later encoding must use; it
  is the canonical input of the *decision*, and a transfer theorem may
  compute any other input from it under the composition fact.

### 2.8 Regenerate

    cd lean && lake build
    lake env lean ../reports/scratch/subexp_pathwidth/02_frame/axiom_check.lean
    cd .. && cat reports/scratch/subexp_pathwidth/02_frame/README.md   # the two diffs
    python3 Ralph_Loops/loop0014/gate.py
