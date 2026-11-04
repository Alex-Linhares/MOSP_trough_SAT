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

## 3. The reduction catalogue: every reduction into pathwidth or vertex separation on record, with its blow-up (item 03, 2026-11-04)

The question of this section is plan §0.4.2: which problems `X` reduce to
pathwidth (equivalently vertex separation, Kinnersley 1992) with a target
graph whose vertex count is **linear in the size of the source instance**,
so that a `2^{o(n)}` algorithm for pathwidth would give `2^{o(N)}` for `X`.
Every reduction found in the held papers is listed with its source problem,
its target, its blow-up and the status of the source after ETH; every one
claimed linear is implemented in `learning/subexp_reductions.py` and checked
against brute-force vertex separation on every graph to 7 vertices (§3.5).
Three of the linear ones are ours, found while checking what the literature
supplies; each comes with a proof (§3.4) and was checked before it was
stated.

### 3.0 What was read, and how

- The held papers, extracted with `pdftotext -layout` to
  `reports/scratch/subexp_pathwidth/03_reductions/` (git-ignored, regenerate
  per `README.md` there) and read at the reduction: Lengauer 1981 (§3,
  Theorem 7, pp. 473–474); Megiddo, Hakimi, Garey, Johnson & Papadimitriou
  1988 (Theorem 1, pp. 20–22); Gustedt 1993 (§4, Theorem 4.1, Lemma 4.2,
  Corollary 4.3; Definition 2.6); Mihai & Todinca 2009 (§3, Theorems 3–4);
  Kinnersley 1992 (Theorem 3.1, Corollary 3.2); Linhares & Yanasse 2002
  (Propositions 1–2, Table 1); Fellows & Langston 1987 (Lemma 4.1); Ohtsuki
  et al. 1979 (§III); Möhring 1990 (§4, Theorems 4.1–4.4); Díaz, Petit &
  Serna 2002 (§4, Table III; Lemma 2.4); Bodlaender 1997 (p. 2), 1998;
  Bodlaender & Kloks 1996 (§1, §7); Kloks, Kratsch & Spinrad 1997 (§1);
  Bodlaender, Kloks, Kratsch & Müller 1995 (§1); Bodlaender 2024 (Theorem
  7 and its proof, p. 13); Groenland, Joret, Nadara & Walczak 2021 (§1);
  Bansal & Katzelnick 2023 (§1); Petit 2011.
- **Scanned and unreadable** (no text layer, no OCR tool on the machine):
  Ellis, Sudborough & Turner 1994; Bodlaender, Gilbert, Hafsteinsson & Kloks
  1991 (WG); Kloks & Bodlaender 1992 (TR); Bodlaender & Möhring 1990; Kloks
  & Kratsch 1992. For these the catalogue uses what the repository recorded
  when they were read on paper (`paper1/equivalences.md` §7 for EST Theorem
  2.2) or what a held secondary source states.
- **Not held**: Kashiwabara & Fujisawa 1979 (`literature/MISSING.md` says
  so: 1979 IEEE ISCAS proceedings, never digitised); Arnborg, Corneil &
  Proskurowski 1987; Monien & Sudborough 1988; Makedon, Papadimitriou &
  Sudborough 1985; Möhring 1996; Bonnet 2024/2025; Goldberg, Golumbic,
  Kaplan & Shamir 1995; Kloks, Bodlaender, Müller & Kratsch 1993; Müller &
  Wagner 1989; Bodlaender & Thilikos 1995. Each is cited here only as a
  held paper cites it, and its blow-up is marked unknown.
- The repository's own chain: `lean/MOSPFormalization/Complex/`
  (loop0005), `MOSPGraph.lean`, `VSEquivPW.lean`, and `paper1/equivalences.md`,
  which records every Table 1 equivalence with the graph it is stated on.

### 3.1 The catalogue

`N` is the size parameter of the source instance named in the row (vertices
of the source graph, customers of the MOSP instance, nets of the matrix);
`n`, `m`, `Δ` are the source graph's vertices, edges and maximum degree. A
reduction is **linear** when the target has `O(N)` vertices. "Status after
ETH" is whether any hypothesis *on record in a held paper* supports a
`2^{Ω(N)}` lower bound for the source once ETH is voided (plan §0.1).

| # | source problem `X` (size `N`) | target | construction | target vertices | linear? | exact relation | source of the reduction | held? | status of `X` after ETH |
|---|---|---|---|---|---|---|---|---|---|
| 1 | vertex separation (`n`) | pathwidth | the same graph | `n` | **1** | `vs = pw` | Kinnersley 1992 Thm 3.1 | yes; Lean `VSEquivPW.lean` | the same problem |
| 2 | gate matrix layout cost, interval thickness, narrowness, one-dimensional logic tracks, monotone/full node search, multiple PLA folding (`N` nets or vertices) | pathwidth | the same graph or matrix (the net graph) | `N` | **1** | each `= pw + 1` | Fellows & Langston 1987 Lemma 4.1; Kinnersley 1992 Cor. 3.2; Kirousis & Papadimitriou 1986; Möhring 1990; Linhares & Yanasse 2002 Table 1 | yes; Lean `Complex/*` (loop0005) | the same problem under another name |
| 3 | MOSP (`N` customers) | pathwidth of the MOSP graph | customers as vertices, a clique per pattern | `N` | **1** | `mosp = pw + 1` | Yanasse 1997a Prop. 5; Linhares & Yanasse 2002 Prop. 2 | yes; Lean `MOSPGraph.lean` | the same problem (converse, pathwidth → MOSP: `n` customers, `m` patterns, §3.5 row 7) |
| 4 | edge search number (`n`) | vertex separation | the 2-expansion, every edge subdivided twice | `n + 2m` | linear in `n + m`; in `n` at bounded degree | `es(G) = vs(G'')` | Ellis, Sudborough & Turner 1994 Thm 2.2 | held, scanned; recorded in `equivalences.md` §7, checked there on 181 graphs | `es` is within `+2` of `vs` on the same graph (Lean `Complex/EdgeSearch*.lean`): no independent hardness |
| 5 | modified min-cut linear arrangement MMCLA (`N` vertices) | vertex separation (VSG) | each vertex an `(N+1)`-clique; edge `v_i v_j` becomes `v_i(j) v_j(i)` | `N (N + 1)` | **quadratic** | `vs(G') = mcw(G) + N` | Lengauer 1981 Thm 7 | yes; checked here to `N = 4` | MMCLA ← Simple Max Cut (Garey & Johnson [3]), blow-up not stated there; no post-ETH support |
| 6 | minimum cut into equal-sized subsets (bisection; `n`, degree `d`) | edge search number | `n + 1` cliques of size `M = 6 n (n + 2)(d + K)`, `nN` edges between every pair, `+N` to the special clique, `+3` per edge of `G` | `(n + 1) · 6n(n+2)(d+K) = Θ(n³ (d + K))` | **cubic** | `s(H) ≤ s ⟺` bisection `≤ K` | Megiddo et al. 1988 Thm 1, p. 20 | yes | bisection has no `2^{Ω(n)}` support on record after ETH; target is edge search, not `vs` exactly |
| 7 | vertex separator problem VSP = balanced complete bipartite subgraph of the complement (`n`, `m`; NP-hard on 3-regular graphs, Müller & Wagner 1989) | pathwidth of starlike chordal graphs | central clique `V`, a peripheral clique `{u, w} ∪ n` private vertices per edge | `n + n m` | **quadratic** on 3-regular (`Θ(n²)`), cubic in general | `pw(φ(G)) = n + opt_VSP − 1` (Lemma 4.2) | Gustedt 1993 Thm 4.1 | yes | VSP has no `2^{Ω(n)}` support on record after ETH |
| 8 | balanced system of 0,1-linear equations (matrix `A`, integers polynomially bounded) | pathwidth of octopus graphs / node-weighted trees | cliques of size given by the integers | the sum of the integers: polynomial, **not linear** in the matrix | pseudo-polynomial | yes/no preserved | Mihai & Todinca 2009 Thms 3–4, from Monien & Sudborough's problem | yes | strongly NP-hard; no `2^{Ω(N)}` support on record |
| 9 | cutwidth, modified cutwidth on planar graphs of maximum degree 3 (`n`) | vertex separation on planar graphs of maximum degree 3 | not held | unknown | unknown | — | Monien & Sudborough 1988, via Díaz et al. 2002 Table III | no | the cutwidth chain is where Bonnet locates the `√n` loss (§1.2) |
| 10 | 3-SAT (`N` variables) | treewidth | "simple, self-contained" | linear in the formula size by the statement `2^{Ω(n)}` | linear (claimed) | — | Bonnet 2024/2025, abstract | no | ETH: voided if the counting theorem stands; whether the graphs have `pw = tw` is unknown to us |
| 11 | minimum cut into equal-sized subsets (as the literature recalls it) | treewidth of cobipartite graphs | not held | unknown | unknown | — | Arnborg, Corneil & Proskurowski 1987, via Kloks, Kratsch & Spinrad 1997 §1, BKKM 1995 §1, Möhring 1990 §4, Bodlaender 1997 p. 2 | no | bisection: see row 6 |
| 12 | interval graph augmentation with minimum clique number (`n`) | pathwidth | the same graph | `n` | **1** | `θ = pw + 1` | Kashiwabara & Fujisawa 1979 (the original NP-completeness), cited by Ohtsuki et al. 1979 §III and Gustedt 1993 | **missing** | the same problem |
| 13 | treewidth on cobipartite (or any AT-free) graphs (`n`) | pathwidth on the same class | the same graph | `n` | **1** | `pw = tw` | Möhring 1996; stated in BKKM 1995 Thm 2.2, Bodlaender 1998 Thm 99 | no (secondary held); checked here on every cobipartite graph to 7 vertices and on every double of §3.4 | treewidth on cobipartite graphs: NP-complete (row 11); no `2^{Ω(n)}` support on record after ETH |
| 14 | pathwidth on all graphs (`n`) | pathwidth = treewidth on **cobipartite** graphs | the **closed-neighbourhood double** `H`: cliques `A = B = V`, `a_u ~ b_v` iff `u = v` or `uv ∈ E` | `2n` | **linear** | `vs(H) = vs(G) + n` | **ours** (§3.4.1); we found no prior statement in the held papers | proved, checked | the same problem: so pathwidth on cobipartite graphs is exactly as hard as in general, at blow-up 2 |
| 15 | pathwidth on all graphs (`n`), additive gap `c` | pathwidth | the lexicographic product `G[K_c]` | `c n` | **linear** at fixed `c` | `pw(G[K_c]) + 1 = c (pw(G) + 1)` | **ours** for pathwidth (§3.4.2); the treewidth form is Bodlaender, Gilbert, Hafsteinsson & Kloks (Bodlaender 2024 Thm 7) | proved, checked | amplification: `2^{o(n)}` for pathwidth within additive `c − 1` gives `2^{o(n)}` exact |
| 16 | **cutwidth on graphs of maximum degree 3** (`n`), planar or not | vertex separation on graphs of maximum degree 3, planarity preserved | the **degree-clique expansion** `G°`: a port per (vertex, incident edge), the ports of a vertex a clique, the two ports of an edge joined | `2m + #isolated ≤ 3n` | **linear** | `vs(G°) = cw(G)` when `Δ ≤ 3`; `cw(G) ≤ vs(G°) ≤ cw(G) + ⌊Δ/2⌋ − 1` in general | **ours** (§3.4.3); the natural reading of row 9, which we cannot confirm | proved, checked | cutwidth: `O*(2ⁿ)` is the best algorithm and beating it "an explicit open problem for a long time" (Bentert et al. 2025, §1.1); NP-complete on planar max-degree-3 graphs (row 9, not held); no `2^{Ω(n)}` support on record after ETH |

Rows 1–3, 12–13 are blow-up 1 (the same object under another name or on a
subclass); rows 14–16 are the linear reductions with a genuine
construction; rows 5–8 are the classical NP-completeness reductions, all
superlinear; rows 9–11 are the reductions we could not read.

### 3.2 The best `X` with a linear reduction

**Three candidates, in order of what a transfer theorem would say.**

1. **`X = cutwidth on graphs of maximum degree 3`** (row 16). The
   reduction `G ↦ G°` is linear (`≤ 3n` vertices), exact (`cw(G) = vs(G°)`
   for `Δ ≤ 3`), preserves planarity and maximum degree 3, and is proved
   below. A `2^{o(n)}` pathwidth algorithm — even one for subcubic planar
   graphs — would give a `2^{o(n)}` algorithm for cutwidth on subcubic
   planar graphs, the class on which cutwidth is NP-complete (Monien &
   Sudborough 1988, not held; Díaz et al. 2002 Table III). This is the `X`
   for item 07: it is the only row whose source is a *different* problem
   with its own open exponential-time question (Bentert et al. 2025 call
   beating `O*(2ⁿ)` for cutwidth a long-standing explicit open problem;
   their §1.1 says the `O*(2ⁿ)` DP remains the best known even for
   constant-factor approximation). What it does not do: name a surviving
   *hypothesis*. No held paper supports `2^{Ω(n)}` for cutwidth on subcubic
   graphs by anything other than ETH, and the chain from 3-SAT to cutwidth
   on degree-3 graphs is not held and, by Bonnet's account (§1.2), loses a
   square root somewhere.
2. **`X = treewidth on cobipartite (hence AT-free, co-comparability)
   graphs`** (rows 13–14). Blow-up 1 by Möhring's `pw = tw` on AT-free
   graphs (not held; checked here on every cobipartite graph to 7 vertices
   and on every double). The converse, row 14, is the finding that matters
   for item 04: **pathwidth on cobipartite graphs is as hard as pathwidth on
   all graphs at blow-up 2**, so no class containing the cobipartite graphs
   (AT-free, co-comparability, the "`pw = tw`" classes of
   `paper2/survey_intersection_classes.md`) can be an easier class for the
   positive track, and a positive result on cobipartite graphs would be a
   positive result in general. In the frame of §2:
   `PathwidthSubexpOn cobipartite → PathwidthSubexp` is a consequence of
   `vs(H) = vs(G) + n` and the composition `Prop` of §2.1, with `f(2n) =
   o(n)` from `f = o(n)`.
3. **`X = MOSP` and the rest of the complex** (rows 1–3, 12): blow-up 1,
   already in Lean; they say nothing new (the same problem).

**What is not on record.** We found no linear reduction *from a problem
with a surviving post-ETH lower bound* into pathwidth: no reduction from
`k`-SAT, Orthogonal Vectors, Set Cover, Hamiltonian Path or Max Cut into
pathwidth or vertex separation appears in any held paper, and the two that
the literature attributes to such sources (Bonnet from 3-SAT into
treewidth, row 10; ACP from bisection into cobipartite treewidth, row 11)
are not held. The bisection chain of §1.2 (3-SAT → Max Cut → bisection →
cobipartite treewidth = pathwidth) therefore stays a candidate with one
unverified step, row 11. Item 07's theorem is accordingly a transfer to
cutwidth on subcubic graphs (and to cobipartite pathwidth), not to a
hypothesis; plan §0.6's "item 03 lowers item 07's ambition" applies in
this form: **the transfer theorem exists and is linear, but its `X` carries
no hypothesis of its own.**

### 3.3 What the superlinear reductions lose, and where

- **Lengauer** (row 5) needs the offset `N` to make every clique's `N`
  pebble-free vertices dominate the count while one clique is entered,
  so that an edge contributing to `width(v_i)` contributes a vertex to the
  cut; the clique size is the vertex count, hence `N(N + 1)`. Checked here
  to `N = 4` (§3.5).
- **Megiddo et al.** (row 6) need `M = 6n(n+2)(d+K)` so that the special
  clique's `M − 1` searchers (Lemma 1) dominate every other term; the
  `nN` edges between every pair of cliques force the balanced split, and
  the three edges per edge of `G` carry the cut. Cubic in `n` at best.
- **Gustedt** (row 7) adds `|V(G)|` private vertices to every peripheral
  clique so that every normalized path decomposition has the central
  clique in one bag and the peripheral cliques on two sides; `n · m`.
- **Mihai & Todinca** (row 8) build cliques whose sizes are the integers of
  a strongly NP-hard equation system, so the vertex count is the sum of
  the (polynomially bounded) integers: polynomial, not linear in the matrix.

So every classical NP-completeness reduction into pathwidth or its
equivalents is superlinear in the vertices, by construction and not by
accident: each uses clique size to simulate a weight or an offset. That is
the mechanism behind Bonnet's `2^{Ω(√n)}` remark (§1.2): a quadratic step
in the chain costs exactly a square root in the exponent.

### 3.4 The three linear constructions, with proofs

Throughout, a layout is an ordering `σ` of `V`; `vs_σ(t)` is the number of
vertices among the first `t` with a neighbour among the rest; `vs(G) = min_σ
max_t vs_σ(t)`. Every statement here was checked on every graph to 7
vertices (§3.5) before it was written, and one refuter subagent read the
six proof directions blind to the rest of the section: all six sound; it
asked for the cut at position `p` to be named explicitly in 3.4.1 (done)
and for the isolated vertices to be placed in 3.4.3 (done).

**3.4.1 The closed-neighbourhood cobipartite double.** For `G = (V, E)`
with `|V| = n`, let `H` have vertex set `A ∪ B`, `A = {a_v}`, `B = {b_v}`,
`A` and `B` cliques, and `a_u b_v ∈ E(H)` iff `u = v` or `uv ∈ E`.

*Theorem.* `vs(H) = vs(G) + n`.

*Proof.* (`≤`) Take `σ` optimal for `G` and lay out `H` as `a_{σ(1)}, …,
a_{σ(n)}, b_{σ(1)}, …, b_{σ(n)}`. A cut inside `A` counts at most `n − 1`.
After all of `A` and the first `t < n` vertices of `B`: the `t` placed
`b`'s count (they have unplaced clique-mates), and `a_u` counts iff `u` has
an unplaced closed neighbour, i.e. `u ∈ N_G[S_{>t}]` where `S_{>t}` is the
suffix of `σ`; `|N[S_{>t}]| = (n − t) + vs_σ(t)`. So the cut is `n +
vs_σ(t) ≤ n + vs(G)`.
(`≥`) Take a layout of `H` of value `k`. One of the two cliques finishes
first; by the symmetry of `H` assume it is `A`, at position `p`, with `j`
vertices of `B` before `p` (`j < n`). Let `τ` be the order of `V` in which
the `b`'s appear. At the cut just before position `p`, `n − 1` vertices of
`A` and `j` of `B` are placed and every one of them has an unplaced
clique-mate, so `k ≥ n − 1 + j`. At the cut at position `p` (all of `A`
and the first `j` of `B` placed) and at the cut after the `t`-th `b` for
every `t > j` (all after `p`), the placed `b`'s count — there are `t ≥ j`
of them, each with an unplaced clique-mate while `t < n` — and `a_u`
counts iff `u ∈ N[S^τ_{>t}]`, so `k ≥ t + (n − t) + vs_τ(t) = n + vs_τ(t)`
for every `t ≥ j`. For `t < j`, `vs_τ(t) ≤ t ≤ j − 1 ≤ k − n`. Hence `k ≥
n + max_t vs_τ(t) ≥ n + vs(G)`. ∎

`H` is cobipartite, so by Möhring (1996) `tw(H) = pw(H)`; checked on every
double to 7 source vertices (§3.5). The map is computable in `O(n²)` time
and has `2n` vertices.

**3.4.2 The clique blow-up.** `G[K_c]` replaces every vertex by a `c`-clique
and every edge by a complete join.

*Theorem.* `vs(G[K_c]) + 1 = c (vs(G) + 1)`.

*Proof.* (`≤`) Lay out the blocks in an optimal order `σ` of `G`, each
block consecutively. At a block boundary after `t` blocks the count is
`c · vs_σ(t)`. Inside block `v` with `i < c` copies placed, the vertices
counted are the copies of earlier vertices with a neighbour at or after
`v`, at most `c · vs_σ(t − 1)` of them (`v` itself is a later neighbour of
such a vertex), plus the `i ≤ c − 1` placed copies of `v`; so at most `c ·
vs(G) + c − 1`.
(`≥`) Take a layout of `G[K_c]` of value `k` and let `τ` order `V` by the
position of the *last* copy. For `2 ≤ t ≤ n`, at the cut just before the
last copy of `v_t`: every `u` earlier in `τ` with a neighbour `w` at or
after `v_t` in `τ` has all `c` copies counted (`w` has an unplaced copy,
adjacent to every copy of `u`), and the `c − 1` placed copies of `v_t`
count; the first set contains the `vs_τ(t − 1)` vertices with a neighbour
after `v_{t−1}`, so `k ≥ c · vs_τ(t − 1) + c − 1` for every cut of `τ`,
i.e. `k + 1 ≥ c (vs(G) + 1)`. (`n = 1`: `vs(K_c) = c − 1`.) ∎

**3.4.3 The degree-clique expansion.** `G°` has a port `(v, e)` for every
vertex `v` and incident edge `e`; the ports of `v` form a clique `K_v`; the
two ports of an edge are joined; isolated vertices are kept. `|V(G°)| = 2m
+ #isolated`, maximum degree `Δ(G°) ≤ Δ(G)` (a port of `v` has `deg(v) − 1`
clique-mates and one matching edge), and for `Δ(G) ≤ 3` the
expansion of a planar graph is planar (each vertex is blown into a
point, an edge or a triangle in the rotation order; for `Δ ≥ 4` the
clique `K_Δ` on the ports is not a face boundary and planarity is not
claimed).

*Theorem.* `cw(G) ≤ vs(G°)` for every graph, and `vs(G°) ≤ cw(G) +
max(0, ⌊Δ/2⌋ − 1)`; in particular **`vs(G°) = cw(G)` when `Δ(G) ≤ 3`**.

*Proof.* (`cw ≤ vs(G°)`) Take a layout of `G°` of value `k` and order `V`
by the position of the last port of each vertex (`τ`; isolated vertices
have no port and go anywhere, contributing to neither side). For a cut of `τ`
after `v_i`, every crossing edge `uw` (`u` complete before `w`) contributes
a distinct counted port at the `G°`-cut at the last port of `v_i`: if the
port `(w, uw)` is unplaced, the placed port `(u, uw)` has it as an
unplaced neighbour; if it is placed, it has an unplaced clique-mate since
`K_w` is incomplete. So `cw_τ ≤ k`.
(`vs(G°) ≤ cw + …`) Take a cutwidth layout of `G` of value `k`, lay out the
cliques in that order, and within `K_v` place first the `a` ports whose
edges go left, then the `b` ports whose edges go right. Let `c` be the
edges passing over `v`; `c + a ≤ k` and `c + b ≤ k`. While the left ports
are placed the count is `c + a` (a left endpoint leaves the cut exactly
when its port enters it); while the `j`-th right port is placed the count
is `c + a + j` for `j < b` (the left ports still have an unplaced
clique-mate) and `c + b` at `j = b`. So the maximum is `c + max(a, b) +
max(0, min(a, b) − 1) ≤ k + max(0, ⌊Δ/2⌋ − 1)`, and for `a + b ≤ 3` the
excess is zero. ∎

The excess is real: for `K_{1,4}`, `vs(G°) = cw + 1` (the test
`test_degree_clique_expansion_exceeds_cutwidth_at_degree_four`), and §3.5
records the measured excess by `Δ`. Degree 3 is therefore the boundary of
this construction, which is where the literature's hardness for vertex
separation sits (planar, maximum degree 3: row 9); we take this as the
likely shape of Monien & Sudborough's reduction without being able to
confirm it.

### 3.5 The checks

`python -m learning.subexp_reductions` (every graph of the networkx atlas,
1 to 7 vertices, 1,252 graphs; `nice -n 19`; log
`reports/scratch/subexp_pathwidth/03_reductions/check_atlas7.log`, results
`check.json`). Two exact evaluators of vertex separation are used — the
literal minimum over permutations and a prefix-set DP (`vs_subset_dp`,
numpy, to about 20 vertices) — and the DP is checked against the
permutations on every atlas graph first. MOSP values come from a DP over
*pattern* subsets that shares no code with the layout evaluators.

| check | what is compared | instances | failures |
|---|---|---|---|
| the DP evaluator | `vs_subset_dp` against the minimum over all permutations | every atlas graph, 1,252 | **0** |
| row 14, the double | `vs(H) = vs(G) + n`, `H` on `2n ≤ 14` vertices by the DP | 1,252 | **0** |
| row 13 on the doubles | `tw(H) = vs(H)` (`learning.treewidth.treewidth_exact`, the C subset DP) | 1,252 | **0** |
| row 13 on the atlas | `tw(G) = vs(G)` on every cobipartite atlas graph | 149 | **0** |
| row 15, `c = 2` | `vs(G[K_2]) + 1 = 2 (vs(G) + 1)`, 14 vertices | 1,252 | **0** |
| row 15, `c = 3` | `vs(G[K_3]) + 1 = 3 (vs(G) + 1)`, 15 vertices | all graphs to 5 vertices, 52 | **0** |
| row 16, lower bound | `cw(G) ≤ vs(G°)` (`cutwidth_dp` of `paper1/complex_check.py`) | every atlas graph with `2m + #isolated ≤ 20`, 696 | **0** |
| row 16, `Δ ≤ 3` | `cw(G) = vs(G°)` | every atlas graph of maximum degree ≤ 3 (all have ≤ 20 ports), 253 | **0** |
| row 16, `Δ ≥ 4` | the excess `vs(G°) − cw(G)` against the proved `⌊Δ/2⌋ − 1` | 443: `Δ = 4`: 0 on 118, 1 on 193; `Δ = 5`: 0 on 42, 1 on 72; `Δ = 6`: 0 on 2, 1 on 10, 2 on 6 | within the bound on all; the bound is attained at every `Δ` |
| row 3, graph → instance | `mosp(instance(G)) = vs(G) + 1` by the pattern DP | every atlas graph with ≤ 14 patterns, 1,169 | **0** |
| row 3, instance → graph | `mosp(M) = vs(M Mᵀ-graph) + 1` | every nonzero 3 × 4 0/1 matrix, 4,095 | **0** |
| the pattern DP | `mosp_subset_dp` against the literal minimum over pattern orders | 300 random 4 × 6 matrices | **0** |
| row 5, Lengauer | `vs(G') = mcw(G) + N`, `G'` on `N(N+1) ≤ 20` vertices | every graph to 4 vertices, 18 | **0** |

38.6 s on one core under a one-minute load of 25.

`tests/test_subexp_reductions.py` (8 tests) runs the same checks to 5
vertices in the gate.

### 3.6 What this does not claim

- That rows 9–11 are what their papers say: Monien & Sudborough 1988,
  Arnborg, Corneil & Proskurowski 1987 and Bonnet 2025 are not held; their
  constructions and blow-ups are "unknown", not "superlinear". If ACP's
  construction is linear, the bisection chain of §1.2 is a linear
  ETH-chain into cobipartite pathwidth, and §3.2 changes only in that the
  hypothesis at its top is ETH, the one already voided.
- That `X = cutwidth on subcubic graphs` carries a surviving hypothesis.
  It carries an open problem (Bentert et al. 2025) and an NP-completeness
  we have not read.
- That the three constructions of §3.4 are new: "we found no prior
  statement in the held papers" (the treewidth form of 3.4.2 is on record;
  3.4.3 is the natural reading of row 9; 3.4.1 may well be how ACP or
  Möhring's readers argued). Nothing is claimed "first".
- That Möhring's `pw = tw` on AT-free graphs is verified: it is checked on
  cobipartite graphs to 7 vertices and on the doubles to 14, and cited
  from secondary sources.
- That any reduction here is in Lean: that is item 08's work. The
  statements of §3.4 are stated against layouts exactly as
  `VertexSeparation.lean` defines them so that item 08 can take them as
  written.
- That the checks to 7 vertices prove anything: they precede the proofs, as
  TASK.md requires, and the proofs are the claim.

### 3.7 Regenerate

    D=reports/scratch/subexp_pathwidth/03_reductions
    # the extracts (git-ignored): see $D/README.md for the full list
    nice -n 19 python3 -m learning.subexp_reductions --nmax 7 > $D/check_atlas7.log
    python3 -m pytest tests/test_subexp_reductions.py -q
    python3 $D/explore.py 6     # the exploration that preceded §3.4 (not the deliverable)
