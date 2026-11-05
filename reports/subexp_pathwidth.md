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

## 4. Classes with `O(n)`-bit layouts? Cobipartite, split, maximum degree 3, cocomparability, the clique-tree covers (item 04, 2026-11-04)

*Plan §0.4.3 and §0.5 item 04; the account of what the counting method
needs is §1.3, and the budget it leaves for pathwidth is §1.3.8: an
encoding of "`vs(G) ≤ k`" as a fixed-width CNF on
`N = o(n √log n / (log log n)²)` variables (the verified route) or as a
tensor network with `s = o(n √log n)` wires and constraints of any width
(the paper route). Item 03's finding (§3.2) that no class containing the
cobipartite graphs can be easier than the general case is the starting
point. Code: `learning/subexp_classes.py`; tests
`tests/test_subexp_classes.py` (10); scratch
`reports/scratch/subexp_pathwidth/04_classes/` (`check_atlas7.log`,
`check.json`, README). Every statement below was checked on every graph
of the atlas to 7 vertices — on every cobipartition and every split
partition, not one per graph — before it was written (§4.8).*

### 4.0 What "fits" means here

A class `C` **fits** if, for every `G ∈ C` on `n` vertices and every `k`,
a polynomial-time computable constraint system in the sense of §1.3
(Boolean variables, local factors of bounded degree, R1–R5, or a tensor
network under R6) has a satisfying assignment iff `vs(G) ≤ k`, with
total incidence `o(n √log n)` — the plan's "`O(n)` Boolean variables
under bounded-width constraints" being the stricter form of the same
requirement. The class must be one on which pathwidth is NP-hard,
otherwise the question is moot: a polynomial algorithm *is* `2^{o(n)}`.
Two reference objects set the scale. A layout is an ordering, `n log₂ n`
bits, and the only encodings on record carry it in `Θ(n²)` variables
(§1.3.8). The decision itself is reachability in the lattice
`F_k = {S ⊆ V : |N(S) ∖ S| ≤ k − 1}` by single additions
(`reports/checkpoint_relaxation.md` §10, with the MOSP offset: "`vs ≤ k`"
is "`MOSP ≤ k + 1`"), and the witness of that reachability is a
*chain* `∅ ⊂ S_1 ⊂ … ⊂ S_n = V` — the object every subsection below
finds again, in a class-specific disguise.

So each subsection asks three things: what an optimal layout looks like
on the class (a normal form, proved and checked); whether the decision
is a condition on a smaller object than the layout; and whether that
object, or anything else we could find, fits. The answers are collected
in §4.7. Conventions: `log` in the budgets of §1.3.8 is natural, as in
the paper; bit counts are `log₂`; the numbers below mix the two as
their formulas do.

### 4.1 Cobipartite graphs: one clique first, then a chain on the other side

Let `H` have vertex set `A ∪ B` with `A` and `B` cliques (`|A| = a`,
`|B| = b`, `a + b = n`); write `N_X(S)` for the neighbours of `S ⊆ Y` in
`X`, `{X, Y} = {A, B}`. Pathwidth is NP-hard here and equals treewidth
(Arnborg, Corneil & Proskurowski 1987, not held; Möhring 1996, cited;
§3.1 rows 13–14).

**Theorem 4.1 (normal form).** Some optimal layout of `H` places one of
the two cliques entirely before the other. With `X` first (in any
order) and `Y` laid out by `τ`, the value is

    max( |X| − 1,  max_{0 ≤ t < |Y|} ( t + |N_X(Y^τ_{>t})| ) ),

where `Y^τ_{>t}` is the set of the last `|Y| − t` vertices of `τ`. Hence

    vs(H) = min_{X ∈ {A, B}} max( |X| − 1, chain_X ),
    chain_X = min_τ max_{0 ≤ t < |Y|} ( t + |N_X(Y^τ_{>t})| ).

*Proof.* (The value of an `X`-first layout.) A cut after `i < |X|`
vertices of `X` counts exactly those `i` vertices (each has an unplaced
clique-mate; nothing of `Y` is placed), so at most `|X| − 1`. A cut
after all of `X` and the first `t < |Y|` vertices of `τ` counts the `t`
placed vertices of `Y` (each has an unplaced clique-mate) and those
vertices of `X` with an unplaced neighbour, which are exactly
`N_X(Y^τ_{>t})`: `t + |N_X(Y^τ_{>t})|`. The last cut is empty.

(Every layout is at least as large as some `X`-first layout.) Take a
layout `σ` of value `v`. One clique finishes before the other; call it
`X`, let it finish at position `p`, and let `j` vertices of `Y` precede
`p`; `j < |Y|` because `Y` finishes after `p`. Let `τ` be the order of
`Y` in `σ`. The cut just before `p` has `|X| − 1` placed vertices of `X`
and `j` of `Y`, each with an unplaced clique-mate, so `v ≥ |X| − 1 + j`.
For `t = j` take the cut just after `p` (placed: `X` and the first `j`
vertices of `τ`), and for `j < t < |Y|` the cut after the `t`-th vertex
of `Y`, which lies after `p`; in both all of `X` is placed, and the cut
counts exactly `t + |N_X(Y^τ_{>t})| =: g(t)`; so `v ≥ g(t)` for `t ≥ j`. For `t < j`,
`g(t) ≤ t + |X| ≤ |X| − 1 + j ≤ v`. Hence `v ≥ max(|X| − 1, max_t g(t))`,
which is the value of the layout "`X` in any order, then `τ`". ∎

**Corollary 4.2 (the decision is a one-sided cut condition).** With
`c = k − |Y|`: `vs(H) ≤ k` iff for `X = A` or `X = B`, `|X| − 1 ≤ k` and
there is a chain `∅ = S_0 ⊂ S_1 ⊂ … ⊂ S_{|Y|} = Y`, `|S_s| = s`, with
`|N_X(S_s)| − s ≤ c` for every `1 ≤ s ≤ |Y|` (`S_s` being the suffix set
`Y^τ_{>|Y|−s}`, `s = |Y| − t`; `S_0 = ∅` is unconstrained — the first
draft wrote `s < |Y|`, which the refuter's brute force rejected on 42
cases, e.g. `K₃` with `|A| = 1`, `k = 1`; the corrected range is checked
on every `(partition, k)` to 7 vertices, §4.8). The ordering of `X` is free; the whole decision is a
chain through the one-sided lattice
`L_c(X, Y) = {S ⊆ Y : |N_X(S)| − |S| ≤ c}`.

This answers the item's question about cobipartite graphs: yes, the
decision is a cut condition on one side, and the object it is a
condition on is a chain of subsets of that side.

**The one-sided chain is the general lattice, verbatim.** On the double
`H` of §3.4.1 (`A = B = V(G)`, `a_u ~ b_v` iff `u ∈ N_G[v]`), `N_A(S) =
N_G[S]`, so `|N_A(S)| − |S| = |N_G(S) ∖ S|`, and with `k_H = k + n`,
`c = k`: Corollary 4.2 says `vs(G) ≤ k` iff there is a chain through
`{S ⊆ V(G) : |N(S) ∖ S| ≤ k}`, which is `F_{k+1}` of
`reports/checkpoint_relaxation.md` §10. So the cobipartite decision is
the lattice problem of item 05 with no translation at all, and §3.2's
finding (no class containing the cobipartite graphs is easier than the
general case) is seen from the other side: the general case *is* a
cobipartite one-sided chain.

**Does it fit?** The certificate Corollary 4.2 offers is the chain on
`Y`, i.e. an ordering of `Y`: `|Y| log₂ |Y|` bits, `Θ(n log n)` when the
sides are balanced; its constraints are the `|Y|` cut conditions, each
reading `|N_X(S_s)|` — a threshold of width `Θ(n)` on `Θ(n)` variables,
`Θ(n²)` incidence in any encoding that carries the chain. The cut
widths are not small here: `k ≥ max(a, b) − 1 ≥ n/2 − 1`. The only
freedom the normal form adds over the general case — the order of `X`
costs nothing — saves `|X| log |X|` bits, which is at most the half of
the layout one did not need anyway. §4.6 shows that no certificate that
carries the chain up to local permutations fits either route. **Does
not fit, because** the one-sided decision is `F_k`-reachability
verbatim (through the double), and the only certificate we have for it
is the chain.

**What the normal form buys instead** (a solver remark, not applied
anywhere): the subset DP over prefix sets of `Y` alone computes
`chain_X` in `O*(2^{|Y|})`, so `vs` of a cobipartite graph is exact in
`O*(2^{max(a, b)})` — `O*(2^{n/2})`, base `1.415`, on balanced
cobipartite graphs, against `1.89` in general (§1.1). On the doubles
`max(a, b) = n = |V(G)|`, so nothing is gained on the general problem,
as it must be. We found no statement of this bound in the held papers
and claim no novelty: the treewidth literature on cobipartite graphs
(ACP 1987) is not held.

*Checked* (§4.8): the formula and the "one clique first" claim about
layouts on every cobipartition of every atlas graph (149 graphs, 496
pairs), and the formula on every `A × B` edge set with `a ≤ b`,
`a + b ≤ 8` (108,622 graphs): zero failures.

### 4.2 Split graphs: polynomial, so the question is moot — and a two-vertex certificate

A split graph has a clique `K` (`κ = |K| ≥ 1`) and an independent set
`I = V ∖ K`. Pathwidth is **polynomial** here: Gustedt (1993, held)
Lemma 2.8 gives `pw ∈ {ω − 1, ω}` and Theorem 7.1 with `k = 1` an
`O(n³)` algorithm (split graphs are the 1-starlike graphs); Möhring
(1990, held) p. 46 says the same. The criterion deciding which of the
two is `paper2/polynomial_cases.md` §2.2 (ours, 2026-10-09, proved by
bags): `vs = κ − 1` iff some `x, y ∈ K` (`x = y` allowed) have every
`p ∈ I` non-adjacent to `x` or to `y`. Nothing is new in this
subsection; what it adds is the layout-side proof, in the vocabulary of
§4.1, and the exhaustive check.

**Theorem 4.3 (Gustedt Lemma 2.8, with paper 2's criterion).** For any
split partition `(K, I)` with `κ ≥ 1`: `vs(G) ∈ {κ − 1, κ}`, and
`vs(G) = κ − 1` iff there is `v ∈ K` such that the independent
neighbours of `v` have a common non-neighbour `u ∈ K` (vacuously true
when `v` has none).

*Proof.* `vs ≥ κ − 1` because `K` is a clique. `vs ≤ κ`: lay out `K`
then `I`; cuts inside `K` count at most `κ − 1`; a cut after `K` counts
the clique vertices with an unplaced independent neighbour, at most
`κ`. For the criterion, let `v` be the last vertex of `K` in a layout of
value `κ − 1`. At the cut just before `v`, the other `κ − 1` clique
vertices count, so no independent neighbour of `v` is placed before
`v` (it would count too). At the cut just after `v`, the counted
vertices include every clique vertex adjacent to an unplaced
independent neighbour of `v`, i.e. all of `N(N_I(v)) ∩ K`; so that set
is not all of `K`, and `u` exists (if `v` is the last vertex overall,
`N_I(v) = ∅`). Conversely, given `v, u`: order `K` with `v` last; place
each `p ∈ I ∖ N(v)` immediately after its last clique neighbour (or
first, if it has none), and each `p ∈ N_I(v)` after `v`. Before `v` a
cut counts the placed clique vertices only (every placed independent
vertex has all its neighbours placed), at most `κ − 1`; after `v` it
counts the clique vertices with an unplaced independent neighbour,
which all lie in `N(N_I(v))`, a set missing `u`. ∎

The two criteria are the same statement: `(x, y)` of paper 2 is
`(v, u)` here. The smallest split graph with `vs = ω` is the 3-sun
(`tests/test_subexp_classes.py`).

**Does it fit?** Vacuously, and literally: the certificate is two vertex
names, `2 log₂ n` bits, and the decision is polynomial. But the class
is not NP-hard, so it gives the positive track nothing; and it marks
where the hard object appears, since split graphs are the starlike
graphs with private cliques of size one (§4.5). **Fits, because** the
problem is polynomial; it contributes no class to item 09.

*Checked* (§4.8): the dichotomy and the criterion on every split
partition of every atlas graph (257 graphs, 670 pairs) and on 300
random split graphs on 11 vertices: zero failures.

### 4.3 Graphs of maximum degree 3: the orientation is not a certificate

Pathwidth is NP-hard on planar graphs of maximum degree 3 (Monien &
Sudborough 1988, not held; Díaz, Petit & Serna 2002 Table III, held),
and by §3.4.3 `vs(G°) = cw(G)` on this class, so a fit for subcubic
pathwidth would be a fit for subcubic cutwidth, Bentert et al.'s open
problem. The widths are not small: Fomin & Høie (2006, held) give
`pw ≤ n/6 + εn` on cubic graphs, and cubic expanders have `pw = Θ(n)`
by Harper's bound in its layout form (`EmptyPair.lean`: for every `j`
some `|A| = j` has `|N[A]| ≤ j + pw`, so a graph with `|N[A]| ≥
(1 + δ)|A|` for `|A| ≤ n/2` has `pw ≥ δn/2`).

The class has one natural `O(n)`-bit object: a layout orients every
edge from its earlier endpoint, an **acyclic orientation** of `m ≤ 3n/2`
bits, and conversely every acyclic orientation is induced by its
linear extensions. If the value were a function of the orientation,
"`vs ≤ k`" would be "some orientation of value `≤ k` exists" with `3n/2`
variables. It is not:

| subcubic atlas graphs, 2–7 vertices | count |
|---|---|
| graphs | 252 |
| acyclic orientations (over all graphs) | 20,820 |
| orientations whose linear extensions disagree on the value | 11,486 (55%) |
| orientations attaining `vs` (some extension optimal) | 10,607 |
| … of which not forced (some extension is worse) | 6,791 (64%) |
| graphs with a disagreeing orientation | 199 of 252; largest spread 2 at 7 vertices |

(`learning.subexp_classes.orientation_spread`; the smallest case is two
disjoint edges, whose interleaved and block-wise extensions have values
2 and 1.) What the orientation leaves open is exactly which down-sets of
the induced poset the layout passes through — a chain through the
down-set lattice restricted to `F_k` — so the orientation is a
*relaxation* of the layout, not a certificate, and its residual problem
is the lattice problem again. Nothing else of size `O(n)` presented
itself: a path decomposition of width `k` has `n` bags of `k + 1` names;
an interval supergraph has `2n` endpoints to order; the Fomin–Høie
construction is an upper bound, not a decision. **Does not fit, because**
the one `O(n)`-bit object the class has does not determine the value,
measurably, and its residual is `F_k`-reachability; and §4.6 applies to
every chain-carrying certificate.

### 4.4 Cocomparability and AT-free graphs: the same question as the general case

Both classes contain the cobipartite graphs, have `pw = tw` (Möhring
1996, cited through Bodlaender 1998 Thm 99 and BKKM 1995, as in
`paper2/survey_intersection_classes.md`), and are NP-hard for that
reason. The double of §3.4.1 maps every graph into them at blow-up 2,
and the incidence budget is linear in the vertex count
(`o(2n √log 2n) = o(n √log n)`), so **a class containing the cobipartite
graphs fits iff all graphs fit**: nothing class-specific can help, and
nothing class-specific is needed. The cocomparability ordering
(umbrella-free, computable in polynomial time) is not a layout and
cannot be made one by a polynomial rule, since pathwidth is NP-hard on
the class; the minimal triangulations being interval graphs (Möhring)
says that a *treewidth* certificate — an elimination ordering — is a
layout here, which is `n log₂ n` bits again. **Does not fit, because**
§4.1 does not, and these classes contain it at blow-up 2.

### 4.5 Chordal graphs, starlike graphs and the clique-tree covers of paper 2: twins, units and a `2^{O(√n)}` subclass

The clique-tree covers of paper 2 (`paper2/survey_trees_sparse.md`
§2.2, `paper2/polynomial_cases.md` §1) are the MOSP instances whose
patterns are the maximal cliques of a chordal graph: block graphs
(polynomial, Chou, Ko, Ho & Chen 2008), octopus graphs and weighted
trees (NP-hard, Mihai & Todinca 2009, held; pseudo-polynomial blow-up,
§3.1 row 8), starlike graphs (NP-hard, Gustedt 1993 Cor. 4.3, held;
the "central pattern" row of paper 2's matrix table, 5 corpus
instances) and chordal dominoes (NP-hard, Kloks, Kratsch & Müller 1995,
not held). Chordal graphs in general are NP-hard by Gustedt's
Theorem 4.1, whose construction is the one §3.3 read: the central
clique is `V(G)`, one peripheral clique per edge of `G` with
`|V(G)|` private vertices each.

Every hard construction in this family makes a clique stand for a
weight, and the private vertices of one clique are **twins**. That
observation is a theorem about layouts:

**Theorem 4.4 (twin lemma).** If `N(x) ∖ {y} = N(y) ∖ {x}` (true or
false twins), some optimal layout places `x` immediately before `y`;
hence every twin class (the classes of this equivalence relation; each
is a clique or an independent set and a module) is consecutive in some
optimal layout.

*Proof.* Take an optimal layout with `x` before `y` and move `x` to the
position immediately before `y`. Cuts before the old position of `x` and
at or after the new one see the same placed sets. At a cut strictly
between, `x` was placed and is now not; every other placed `z` is
counted after the move iff it was before, because an unplaced neighbour
`z` lost by the move is `x`, and `z ~ x` implies `z ~ y` with `y`
unplaced at that cut. So each such cut loses the contribution of `x`
(1 if `x` was counted) and gains nothing. The layout stays optimal.
For a class `x_1, …, x_w` in layout order, move `x_{w−1}` to just
before `x_w`, then `x_{w−2}` to just before `x_{w−1}`, and so on down to
`x_1` (in *reverse* layout order: moving `x_1` first and then `x_2`
would strand `x_1`, as the refuter's brute force showed on 4,260
cases); the class becomes consecutive, and no other class is separated,
since each insertion is next to a vertex outside that class. ∎

Twins are interchangeable by an automorphism, so the internal order of a
class is irrelevant, and `vs` is a DP over subsets of classes:
`f(S) = min_{Q ∈ S} max(f(S ∖ Q), cost(∪(S ∖ Q), Q))`, with `cost(P, Q)`
the largest cut while `Q` is placed after `P`. **`vs` is exact in
`O*(2^u)`, `u` the number of twin classes** (`twin_unit_dp`; checked
against `vs` on all 1,252 atlas graphs, where 884 have `u < n`). On the
MOSP side the twin classes of the MOSP graph are the customers with
equal pattern sets, so this is the layout-side justification of the
"equivalent nodes" reduction of Yanasse & Senne (2010), one of the six
pre-processing operations (unimplemented, CLAUDE.md); the lemma is
elementary and we found no prior statement of it in the held papers in
this form, claiming nothing.

**What it says about the hard constructions.** Gustedt's Theorem 4.1
instances from a graph `G` with `n_G` vertices and `m_G` edges have
`n' = n_G + m_G n_G` vertices and `u = n_G + m_G` twin classes; from a
3-regular `G` (VSP stays NP-hard there, as Gustedt notes, p. 239),
`n' = n_G + 3n_G²/2` and `u = 5n_G/2 = O(√n')`. The unit DP solves
them in `2^{O(√n')}`. Gustedt's own Theorem 6.4 is sharper and does
not need the twins: **starlike pathwidth in `O(4^{α₀} r + n)`**, `α₀`
the size of the central clique, `r` the number of peripheral cliques;
on the hardness instances `α₀ = n_G ≤ √(2n'/3)`.

**Corollary 4.5 (an NP-hard class in `2^{O(√n)}`, unconditionally).**
On the class of starlike chordal graphs whose central clique has at
most `√n` vertices, pathwidth is NP-hard (Gustedt Cor. 4.3's instances
from 3-regular graphs lie in it) and computable in `2^{O(√n)} · poly(n)`
(Gustedt Thm 6.4). The same holds for its MOSP form, the central-pattern
instances of paper 2 whose central pattern has at most `√n` customers.

This is plan §0.2's "positive answer on a class where pathwidth is
NP-hard" in letter, and we say plainly why it is not one in spirit. The
class is cut by a size parameter so that the hard core — the centre,
over whose subsets Theorem 6.4's algorithm enumerates — has `√n`
vertices; it is §3.3's quadratic blow-up seen from the algorithm's side
(and the matching upper side of Bonnet's `2^{Ω(√n)}` remark, §1.2); it
uses nothing of the counting theorem; it is not an `O(n)`-bit layout
result; and it is not closed under the maps that make hardness
transfer (the double of a starlike graph is not starlike). It does
settle one thing for item 07: **on chordal and starlike graphs, no
`2^{Ω(n)}` lower bound can come from Gustedt's construction**, since the
instances it produces are solved in `2^{O(√n)}`; a `2^{Ω(n)}` statement
for chordal pathwidth would need private cliques of bounded size — but
that is `k`-starlike, polynomial by Theorem 7.1 — or a construction of
a different kind.

**The object, and whether it fits.** Theorem 6.4's algorithm
enumerates subsets of the centre: the hard object on starlike graphs is
a chain through the subsets of the central clique, `α₀ log₂ α₀` bits,
and the peripheral cliques attach to it by thresholds (the partition
problem GPP of Gustedt §5 in the primitive case). With the `α₀ ≤ √n`
restriction lifted, `α₀ = Θ(n)` is possible with `r = Θ(n)` singleton
private cliques — the split end — or with heavy ones, and then the
chain is `Θ(n log n)` bits again. Block graphs are polynomial (fit
vacuously, like split). Octopus graphs and weighted trees: the weights
are twin cliques, the unit DP runs in `2^{O(u)}` with `u` the number of
weighted-tree nodes, which is `o(n)` on Mihai & Todinca's instances
(their blow-up is pseudo-polynomial, §3.1), and the chain over the
nodes is the hard object. **Does not fit, because** the hard object on
every clique-tree class is a chain over the units (the centre, or the
tree nodes), and where the units are few the problem is `2^{O(u)}`
already, with no certificate smaller than the chain in sight.

*Checked* (§4.8): the twin lemma as a statement about layouts (minimum
over layouts with every class consecutive equals `vs`) and the unit DP,
on every atlas graph to 7 vertices: zero failures.

### 4.6 The gap lemma: no certificate that carries the chain up to local permutations fits

Every subsection ends at the same object. This subsection says, for the
family of certificates that carry it, that no spacing helps — the
checkpoint idea of `reports/checkpoint_relaxation.md` (nested sets at
a few sizes, segments verified between them) seen through §1.3.8's
budget.

**Definition.** A *`g`-coarse chain certificate* for "`vs(G) ≤ k`" is
an assignment to `N` Boolean variables that determines the prefix sets
`S_g ⊂ S_{2g} ⊂ …` (at every multiple of `g`) of some layout of value
`≤ k`, together with a constraint system of §1.3's kind that is
satisfiable iff such a layout exists. (`g = 1` is the layout; `g = n`
is the empty certificate, "a layout exists", which is not a certificate
of anything.)

**Lemma 4.6 (bits).** If the decoding of checkpoints from assignments
is the same for every graph on `n` vertices (a certificate *scheme*,
not one per graph), then `N ≥ log₂ ( n! / (g!)^{n/g} ) − 1 ≥
n log₂ ( n / (e g) ) − 1`.

*Proof.* Distinct checkpoint sequences number the multinomial
`n!/(g!)^{n/g}` (choose which `g` vertices fill each segment). On the
path graph `P_n` with `k = 1` every layout is one of the two monotone
orders, so a scheme that decodes the same way for every graph must
have, for each sequence, an assignment decoding to it or to its
reversal — otherwise some relabelling of `P_n` has no certificate — so
`2^N ≥ ½ · n!/(g!)^{n/g}`; and `n! ≥ (n/e)^n`, `g! ≤ g^g`. (Without
uniformity the lemma fails: a fixed graph may need no bits at all.) ∎

**The verified route.** The CNF must verify each segment: that the `g`
vertices of `S_{(i+1)g} ∖ S_{ig}` admit an order with every cut `≤ k`
given the boundary state. That is "`vs ≤ k` with `S_{ig}` pre-placed"
on `g` vertices, an instance of the same problem, and the only
encodings on record for it (position, nested chain; §1.3.8) cost
`g²` variables per segment (the nested chain's `y[v, t]` on the
segment's `g` vertices and `g` steps), `ng` in all. So
`N ≥ max( n log₂(n/(eg)) − 1, ng )`, and no `g` fits: for
`g ≥ √log n` the second term is `≥ n √log n`, above the budget
`n √log n / (log log n)²` for every `n ≥ 16` (where `(log log n)² ≥ 1`);
for `g < √log n` the first is `≥ n (log₂ n − ½ log₂ log n − 1.45) − 1`,
which at `n = 125` is already `4.4 n` against a budget of `0.89 n` and
grows like `n log n`.
What this does not exclude is a segment encoding smaller than `g²`:
the segment is the same problem with a boundary, so the question is
self-similar, and a fit for the segment would be a fit for the problem.

**The paper route (R6).** A tensor per segment may have width up to
`s^{9/10}` and a brute-force entry. Its ports must determine
`S_{(i+1)g}` given `S_{ig}`, at least `log₂ C(n − ig, g) ≥ g log₂(n/g) −
O(g)` of them on the first segments; and Lemma 4.6 bounds the wire count
`s ≥ N`. This route has its own budget, `s ≤ B_p = n √log n`
(§1.3.8), not the verified one. Taking the smallest `g` whose bit count
meets it, `g = n / (e · 2^{√log n})`, the segment width
`g log₂(n/g) ≈ 1.44 · n √log n · 2^{−√log n}` must be at most
`s^{9/10} ≤ B_p^{9/10}`, i.e. `2^{−√log n} ≤ n^{−1/10} (log n)^{−0.05}`
up to constants, which fails for large `n` since `√log n = o(log n)`
— but only for very large `n`. The arithmetic (`gap_table`; the ratio
is the segment width over `B_p^{9/10}` at the smallest fitting `g`,
with the verified route's `g` beside it for comparison):

| `n` | verified `B_v/n` | its `g/n` | paper `B_p/n` | its `g/n` | segment width | `B_p^{9/10}` | ratio |
|---|---|---|---|---|---|---|---|
| 125 | 0.89 | 0.20 | 2.20 | 0.080 | 36.5 | 157 | 0.23 |
| 10³ | 0.70 | 0.23 | 2.63 | 0.060 | 242 | 1,200 | 0.20 |
| 10⁶ | 0.54 | 0.25 | 3.72 | 0.028 | 1.44 × 10⁵ | 8.19 × 10⁵ | 0.18 |
| 10⁹ | 0.50 | 0.26 | 4.55 | 0.016 | 9.4 × 10⁷ | 4.92 × 10⁸ | 0.19 |
| 10¹⁵ | 0.47 | 0.27 | 5.88 | 0.006 | 4.6 × 10¹³ | 1.56 × 10¹⁴ | 0.29 |
| 10²¹ | 0.46 | 0.27 | 6.95 | 0.003 | 2.5 × 10¹⁹ | 4.6 × 10¹⁹ | 0.55 |
| 10²⁴ | 0.46 | 0.27 | 7.43 | 0.002 | 1.9 × 10²² | 2.4 × 10²² | 0.78 |

So the paper route is excluded for this family **asymptotically only**:
the ratio is below 1 at every `n` up to `10²⁴` and passes it beyond,
so at any size one could write down the arithmetic alone does not
exclude a coarse chain on the paper route — with the caveat that
Theorem D.1's constants are unknown (§1.3.8), so nothing is claimed at
any finite `n` in either direction. (The first draft mixed the routes,
taking `g` from the verified budget and the width against `s = B_p`,
and put the crossover near `10⁹`; the refuter caught the mix.) The
verified budget `B_v` is itself below `n` at every `n` in the table,
which is the same fact: the verified exponent is `o(n)` only in the
limit.

**What the lemma does not cover.** A certificate that is not a coarse
chain at all — one whose satisfying assignments do not determine any
checkpoint of any layout — is untouched. That is the only kind item 05
can look for: an algebraic object (the number of chains as a sum over
orderings, or the common zeros of a sparse system) that witnesses
reachability in `F_k` without naming a path through it.

### 4.7 Verdict: no NP-hard class fits; the positive track is the chain-count attempt only

| class | pathwidth | the object in an optimal layout (proved here or cited) | fits? |
|---|---|---|---|
| cobipartite | NP-hard, `= tw` | one clique first, then a chain through `L_c(X, Y)`; on the doubles it is `F_k` verbatim (Thm 4.1, Cor. 4.2) | **no**: the object is the general lattice chain |
| split | polynomial (Gustedt L. 2.8) | two clique vertices `v, u` (Thm 4.3; paper 2's criterion) | fits vacuously: not NP-hard |
| maximum degree 3 | NP-hard (MS 1988, not held) | the acyclic orientation is a relaxation, not a certificate (55% of orientations disagree, 64% of optimal ones unforced, to 7 vertices); the residual is `F_k` | **no** |
| cocomparability, AT-free | NP-hard, `= tw` | contain the doubles at blow-up 2: fit iff all graphs fit | **no**, by §4.1 |
| chordal, starlike, clique-tree covers | NP-hard (Gustedt 4.1, 4.3); block graphs polynomial | twins consecutive (Thm 4.4), `O*(2^u)`; a chain over the centre; `α₀ ≤ √n` is NP-hard and `2^{O(√n)}` by Gustedt 6.4 (Cor. 4.5) | **no**: the chain over the units; the `√n` subclass is the blow-up, not a certificate |
| any chain-carrying certificate at spacing `g` | — | `N ≥ n log₂(n/(eg)) − 1` (Lemma 4.6) | **no** on the verified route at every `n ≥ 16`; on the paper route asymptotically (crossover beyond `10²⁴`) |

**Plan §0.6, item 04's kill: met.** No class on which pathwidth is
NP-hard has `O(n)`-bit layouts under bounded-width constraints, nor a
certificate within §1.3.8's budget, among the five the item names; and
the one object each class has in place of the layout is a chain through
a lattice — `F_k` itself on cobipartite doubles, a down-set chain on
bounded-degree graphs, a chain over the centre on starlike graphs.
**Item 09 is the chain-count attempt only** (item 05's route), and it
may work on `F_k` for general graphs without loss, since every NP-hard
class examined presents that very object. The one unconditional
positive statement found, Corollary 4.5, is Gustedt's and is the
quadratic blow-up seen from the algorithm's side; it is recorded for
item 07 (no `2^{Ω(n)}` for chordal pathwidth can come from Gustedt's
construction) and for item 10, not as an answer to Q.

Two solver remarks, neither applied: exact pathwidth of a cobipartite
graph in `O*(2^{max(a, b)})` (§4.1); exact vertex separation in
`O*(2^u)` over twin classes (§4.5), which on MOSP instances is the
equivalent-customers reduction with a proof.

### 4.8 The checks

`nice -n 19 python3 -m learning.subexp_classes` (atlas to 7 vertices,
1,252 graphs; 36.5 s on one core under a one-minute load of 32; log
`04_classes/check_atlas7.log`, results `check.json`). `vs` is the
prefix-set DP of §3.5, itself checked against the permutation minimum on
every atlas graph there; claims about *layouts* are checked by
`itertools.permutations` directly.

| check | what is compared | instances | failures |
|---|---|---|---|
| Thm 4.1, the formula | `min_X max(|X| − 1, chain_X)` against `vs` | every cobipartition of every atlas graph: 149 graphs, 496 pairs | **0** |
| Thm 4.1, the layouts | the minimum over layouts with one clique entirely first (all orders of both sides) against `vs` | the same 496 pairs | **0** |
| Cor. 4.2, the decision | the chain condition with the corrected range `1 ≤ s ≤ |Y|` against `vs ≤ k` | the same 496 pairs, every `0 ≤ k ≤ n`: 3,653 decisions | **0** (42 failures with the first draft's range) |
| Thm 4.1 on all patterns | the formula against `vs` on every `A × B` edge set, `a ≤ b`, `a + b ≤ 8` | 108,622 graphs | **0** |
| Thm 4.3, dichotomy | `vs ∈ {κ − 1, κ}` | every split partition of every atlas graph: 257 graphs, 670 pairs | **0** |
| Thm 4.3, criterion | the `(v, u)` criterion against `vs` | the same 670 pairs; 300 random split graphs on 11 vertices | **0** |
| Thm 4.4, layouts | minimum over layouts with every twin class consecutive against `vs` | every atlas graph | **0** |
| Thm 4.4, unit DP | `twin_unit_dp` against `vs` | every atlas graph (884 of 1,252 have `u < n`) | **0** |
| §4.3, orientations | per acyclic orientation, min and max over linear extensions | 252 subcubic atlas graphs, 20,820 orientations | measurement (table in §4.3) |
| Lemma 4.6 | the arithmetic of `gap_table` | five values of `n` | table in §4.6 |

`tests/test_subexp_classes.py` (10 tests) runs the same checks to 5
vertices (patterns to 6, random split graphs on 10) in the gate.

### 4.9 What this does not claim

- That no `O(n)`-bit certificate exists on any of these classes: "we
  found none", with the one `O(n)`-bit object each class offers shown
  not to be one (§4.3) or shown to be the general lattice (§4.1, §4.4,
  §4.5). Lemma 4.6 excludes a *family* (certificates that determine
  checkpoints of a layout), on the verified route at every `n` under
  the segment encodings on record, on the paper route asymptotically
  with unknown constants; it says nothing about certificates of another
  kind, which are item 05's business.
- That Corollary 4.5 answers Q: it is Gustedt's two theorems on a class
  cut to the size of his construction's centre, the blow-up of §3.3 seen
  from above. It is not a layout certificate, not conditional on
  anything, and not new as mathematics.
- That the split criterion, the cobipartite `O*(2^{max(a,b)})` bound or
  the twin lemma are new: the first is on record (Gustedt Lemma 2.8;
  paper 2 §2.2, where the criterion was first stated and proved by bags);
  for the other two "we found no prior statement in the held papers",
  and the cobipartite treewidth literature (ACP 1987) is not held.
- That Monien & Sudborough's hardness for subcubic graphs is as we
  describe it (not held; cited through Díaz et al. 2002), or that
  Kloks–Kratsch–Müller's domino result is (not held).
- That the checks prove anything: they precede the proofs, as TASK.md
  requires; the proofs are the claims. One refuter subagent read the
  four proofs and Corollary 4.5's arithmetic blind to the rest of this
  section, with its own brute force to 6 vertices: Theorems 4.1, 4.3 and
  the single move of 4.4 sound and agreeing with its brute force;
  Corollary 4.2's index range wrong as first written (fixed and now
  checked); the induction of 4.4 wrong in its order (fixed); Lemma 4.6
  needing the uniformity hypothesis (added, with the path-graph
  argument); the constant of the verified route unstated (now `1`); and
  the paper-route table mixing the two budgets (recomputed per route).
  Every point is folded in above. What it did not verify: Gustedt's
  construction and the 3-regular remark, which are read from the held
  paper (pp. 239–241).
- That any of this is in Lean: the item is mathematics; the twin lemma
  and the cobipartite normal form are stated against layouts exactly as
  `VertexSeparation.lean` defines them, so item 08 or the reserve could
  take them as written if a theorem of item 07 needs them.
- That anything was solved, run on an instance, or downloaded:
  `solutions/` is untouched, no instance under `MOSP_Instances/` or the
  pathwidth dataset was touched, and the only compute is the 36.5 s
  check.

### 4.10 Regenerate

    D=reports/scratch/subexp_pathwidth/04_classes
    nice -n 19 python3 -m learning.subexp_classes --nmax 7 --patterns-max 8 > $D/check_atlas7.log
    python3 -m pytest tests/test_subexp_classes.py -q
    python3 -c "from learning.subexp_classes import gap_table; [print(r) for r in gap_table()]"

## 5. The chain count as an algebraic object (item 05, 2026-11-04)

*Code `learning/subexp_chain.py`, tests `tests/test_subexp_chain.py`
(9); scratch `reports/scratch/subexp_pathwidth/05_chain/` (README,
`check_atlas7.log`, `check.json`, `membership_polynomial.csv`,
`split_rank.csv`). Every statement below was checked on every graph of
the atlas to 7 vertices before it was written; §5.8 tabulates the
checks, §5.9 says what is not claimed. One refuter agent read the proofs
and the tables blind to the verdict with its own brute force to 5
vertices; what it found is folded in and listed in §5.9.*

Item 04 ended at one object on every NP-hard class: a chain through the
lattice `L_k = {S ⊆ V : |N(S) ∖ S| ≤ k}` (§4.7). This item takes the
**number** of such chains as the object — the sum over orderings of a
product of cut tests — and asks the item's question in §1.3's currency:
is that number the number of common zeros of a sparse polynomial system
in `o(n²)` variables, and if the system does not fit §1.3.8's budget,
which half of it is the obstacle, the width of the threshold constraint
or the ordering variables. The answer, in one line: **the chain count is
exactly the number of solutions of a sparse bounded-degree system — in
`Θ(n² k)` variables as counted, `Θ(n²)` with a binary adder, and never
fewer than `n (n − 1)`; it is also the number of solutions of a system in
`n ⌈log₂ n⌉` variables with `n` constraints of width `n ⌈log₂ n⌉`; the
threshold's width is not the obstacle (it compiles away at linear cost
per cut, as §1.3.5 said), the ordering is — through the `n − 1` cuts,
each of which reads every vertex.** Plan §0.6's kill is met, with the
parenthetical corrected (§5.7).

### 5.0 Conventions and the object

`G = (V, E)`, `n = |V|`, `m = |E|`. For `S ⊆ V`, `∂S = N(S) ∖ S` is the
outer boundary and `∂_in S = {v ∈ S : N(v) ⊄ S}` the inner one —
Kinnersley's cut of a layout at the prefix `S`. `L_k = {S : |∂S| ≤ k}`;
`∅, V ∈ L_k` for every `k ≥ 0` since both have empty boundary. A layout
`σ = (v_1, …, v_n)` has prefix sets `S_t(σ) = {v_1, …, v_t}` and
`vs(σ) = max_{1 ≤ t ≤ n−1} |∂_in S_t(σ)|`. The **chain count** is

    C_k(G) = Σ_σ Π_{t=1}^{n−1} [S_t(σ) ∈ L_k] = #{maximal chains ∅ ⊂ S_1 ⊂ … ⊂ S_{n−1} ⊂ V in L_k}.

In MOSP vocabulary `L_k` is `F_{k+1}` of `reports/checkpoint_relaxation.md`
§10 (there the bound is `MOSP − 1 = vs`).

**Lemma 5.1 (three equal counts).** For every `G` and `k ≥ 0`,
`C_k(G) = #{σ : vs(σ) ≤ k} = #{σ : |∂_in S_t(σ)| ≤ k, 1 ≤ t ≤ n−1}`, and
in particular `vs(G) ≤ k ⟺ C_k(G) > 0`.

*Proof.* `∂_in S = ∂(V ∖ S)`: a vertex of `S` with a neighbour outside
`S` is a neighbour of `V ∖ S` not in `V ∖ S`, and conversely. So
`vs(σ) ≤ k` iff every suffix set `V ∖ S_t(σ)` lies in `L_k`, and the
suffix sets of `σ` are the prefix sets of the reversed layout `σ^R`.
Reversal is a bijection on layouts. ∎

*Checked* (§5.8): the three counts agree with the literal sums over
`itertools.permutations` (outer-boundary prefixes; Kinnersley's
`vs_of_layout`) on every atlas graph to 7 vertices at every `k`, and
`C_k > 0 ⟺ vs ≤ k` against the item-03 evaluator; `C_k(K_n) = n!` for
`k ≥ n − 1` and `0` below.

### 5.1 The chain count is a `#SAT` — in `Θ(n² k)` variables as counted, never fewer than `n (n − 1)`

**Theorem 5.2.** Let `Φ_{G,k}` be the CNF on the variables `y[v,t]`
(`v ∈ S_t`, `1 ≤ t ≤ n−1`), `x[v,t]`, `o[u,t]`, `b[u,t]` and counter
variables `r[t,i,j]` with the clauses

- (N) `y[v,t−1] → y[v,t]` (nested);
- (X) `x[v,t] ↔ y[v,t] ∧ ¬y[v,t−1]`, with `y[v,0] := false` (the vertex
  new at step `t`);
- (E) exactly one of `x[·,t]` (one new vertex per step);
- (O) `o[u,t] ↔ ∨_{w ∈ N(u)} y[w,t]`; (B) `b[u,t] ↔ ¬y[u,t] ∧ o[u,t]`
  (the boundary bit `[u ∈ ∂S_t]`);
- (C) `r[t,i,j] ↔ (at least j of b[1..i,t])` for `1 ≤ j ≤ k+1`
  (a bidirectional sequential counter) and the unit `¬r[t,n,k+1]` when
  `k + 1 ≤ n` (for `k ≥ n` no cut can exceed `k` and the clause is
  absent).

Then the models of `Φ_{G,k}` are in bijection with the layouts all of
whose prefix sets lie in `L_k`, so **`#models(Φ_{G,k}) = C_k(G)`**.

*Proof.* In a model, (N) makes `S_t := {v : y[v,t]}` nested; (X) and (E)
make `|S_t ∖ S_{t−1}| = 1` for every `t ≥ 1` (with `S_0 = ∅`), so
`|S_t| = t` and the `S_t` are the prefix sets of the layout whose `t`-th
vertex is the one with `x[v,t]`; (O) and (B) force `b[u,t] = [u ∈ ∂S_t]`;
(C) forces `r[t,n,k+1] = [|∂S_t| ≥ k+1]`, which the unit clause makes
false. Conversely every such layout determines the `y`, and every other
variable is defined from earlier ones by an equivalence, so the
assignment extends uniquely. ∎

*Checked* (§5.8): the model count of `Φ_{G,k}` — enumerated by CaDiCaL
with a blocking clause over **all** variables, which also checks that the
auxiliaries are determined — equals `C_k(G)` on every atlas graph to 6
vertices at every `k` and on a sample of 7-vertex graphs: 1,391
counts, zero failures. The clause and variable counts agree with the
closed forms of `cnf_size_formula` on every one.

**As a polynomial system.** Over any field, a clause `l_1 ∨ … ∨ l_w`
is the equation `Π_i (1 − ℓ_i) = 0` with `ℓ_i = x` or `1 − x`, and
`x² − x = 0` keeps the variables Boolean; the common zeros are exactly
the models. Every clause of `Φ_{G,k}` has width `≤ 3` except the
at-least-one clause of (E) (width `n`) and the one of (O) (width
`deg(u) + 1`), which split into width-3 clauses with a linear number of
auxiliaries in the standard way. So **`C_k(G)` is the number of common
zeros in the Boolean cube of a system of equations of degree `≤ 3`,
each with `≤ 8` monomials** — R1, R2 and R5 of §1.3.3 hold; R3 (polylog
occurrences per variable) holds with a ladder at-most-one in (E) and up
to the paper's branching on the high-degree vertices, not with the
pairwise at-most-one as counted, where every `x[v,t]` occurs `n − 1`
times. What fails is the budget alone. Counted as implemented (`cnf_size`, checked against the
formula on every atlas graph):

    variables = 4 n (n − 1) + (n − 1) Σ_{i=0}^{n−1} min(i + 1, k + 1)   ( ≥ n (n − 1) from the `y` alone)
    incidence = Θ(n³ + n² k + n m)   as counted (the pairwise at-most-one of (E) contributes `n²` per level and the counter `n k`; a ladder at-most-one and a binary adder would make it `Θ(n² + n m)`, standard, not implemented, not needed for the verdict, which is a lower-bound statement)

| `n = 125` | `m` | `k` | variables | clauses | incidence | budget `B_v` (§1.3.8, constant 1) |
|---|---|---|---|---|---|---|
| ridge, `pw/n ≈ 0.19` | 250 | 24 | 412,300 | 2,529,598 | 6,165,523 | 111 |
| `pw/n = 0.4` | 500 | 50 | 694,400 | 3,716,774 | 9,441,727 | 111 |
| `pw/n = 0.6` | 1,000 | 75 | 886,600 | 4,606,474 | 11,915,527 | 111 |
| dense, `pw/n = 0.8` | 3,875 | 100 | 1,001,300 | 5,775,174 | 15,303,827 | 111 |

(`m` is realised by regular degrees `2m/n` in the formula; `B_v` is
`n √log n / (log log n)²`, whose unknown constant §1.3.8 carries.) The
`y` variables alone are `n (n − 1) = 15,500`, 140 times the budget's
nominal value. Under the hypothesis `SubexpCount 3`, this system decides
`vs ≤ k` in `2^{O(N (log log N)² / √log N)}` with `N = Θ(n² k)`, i.e.
worse than the `O*(2ⁿ)` subset DP; so the chain count *is* the algebraic
object the item asks about, and the item's "`o(n²)` variables" is the
whole difficulty, as §1.3.8 said of the position encoding.

### 5.2 The threshold constraint as a polynomial, without auxiliaries

The item asks for the cut test written as a polynomial over a field in
the set variables `s_v = [v ∈ S]`, with its degree and sparsity. It is
the composition of the **bare threshold** `T_k(b) = [Σ_u b_u ≤ k]` with
the **boundary bits** `b_u(S) = [u ∉ S ∧ N(u) ∩ S ≠ ∅]`.

**Lemma 5.3 (boundary bit).** For `deg(u) = d ≥ 1`,
`b_u = (1 − s_u) (1 − Π_{w ∈ N(u)} (1 − s_w))` is multilinear of degree
`d + 1` with exactly `2^{d+1} − 2` monomials, the top one
`s_u Π_{w ∈ N(u)} s_w` with coefficient `(−1)^d`.

*Proof.* `(1 − s_u) Π_{w}(1 − s_w)` expands to one monomial `±s_T` for
each `T ⊆ N[u]`, `2^{d+1}` of them, coefficient `(−1)^{|T|}`;
subtracting it from `1 − s_u` cancels exactly the monomials `1` and
`s_u` (coefficients `1 − 1` and `−1 + 1`) and negates the rest. ∎

**Lemma 5.4 (bare threshold).** For `0 ≤ k ≤ n − 1` the multilinear
polynomial of `T_k` on `{0,1}ⁿ` contains `x_1 ⋯ x_n` with coefficient
`(−1)^{n−k} C(n−1, k) ≠ 0`; its degree is `n`. Across any split
`A | B` of the inputs, its communication matrix `[|S_A| + |S_B| ≤ k]`
depends only on `(|S_A|, |S_B|)` and has rank `≤ min(|A|, |B|, k) + 1`.

*Proof.* By Möbius inversion the top coefficient is
`Σ_{S ⊆ [n]} (−1)^{n−|S|} T_k(S) = Σ_{i ≤ k} (−1)^{n−i} C(n, i) =
(−1)^{n−k} C(n−1, k)`, the alternating partial sum
`Σ_{i ≤ k} (−1)^i C(n, i) = (−1)^k C(n−1, k)`. The rank: rows with
equal `|S_A|` are equal, so the rank is that of the
`(|A|+1) × (|B|+1)` staircase `[i + j ≤ k]`, at most `min(|A|, k) + 1`
and at most `|B| + 1`. ∎

So the threshold alone is a **full-degree, exponentially dense**
polynomial in its `n` inputs (R1 fails for it as an equation), yet
across any split it has rank `O(n)` — `O(log n)` crossing wires in a
tensor network, which is the counter circuit §1.3.5 describes: the
width compiles away. The composite `[S ∈ L_k] = T_k(b_1(S), …, b_n(S))`
has no closed form; it is measured.

**Measured** (`membership_polynomial`; all 1,252 atlas graphs, every
`0 ≤ k < n`; the refutation level `k = vs − 1` and the witness level
`k = vs` separately; `essential` = the number of set variables the
indicator depends on; `members = |L_k|`):

| level | rows | degree `= n` over `Q` | over `GF(2)` | mean degree `/ n` | median monomials `/ 2ⁿ` (`Q`) | all `n` variables essential (connected graphs) |
|---|---|---|---|---|---|---|
| `k = vs − 1` | 1,245 | 81.8% | 30.9% | 0.962 | 0.625 | **100%** (995 of 995) |
| `k = vs` | 1,252 | 82.1% | 30.3% | 0.938 | 0.594 | 98.5% (981 of 996) |
| all `k` | 8,475 | 50.0% | 24.5% | 0.664 | 0.508 | 73.1% (4,954 of 6,781) |

By `n` at `k = vs − 1` (degree `= n` over `Q`; median monomials `/ 2ⁿ`; median `|L_k| / 2ⁿ`): `n = 4`: 70%, 0.75, 0.375; `n = 5`: 58%, 0.69, 0.28; `n = 6`: 77%, 0.61, 0.28; `n = 7`: 84%, 0.63, 0.28. At the witness level `|L_k| / 2ⁿ` falls from 0.94 at `n = 4` to 0.66 at `n = 7`; at seven vertices the sparsest refutation-level indicator still has 4 of 128 monomials and the median 80. Over `GF(2)` the degree is full less often (31%) and the median degree is `0.86 n` at `n = 7`.

So the cut test, as one equation in the set variables, has unbounded
degree and exponentially many monomials on most graphs (R1 fails), and
**at the refutation level it depends on every vertex of every connected
graph** to 7 vertices. The first fact is the width, which compiles away
(Theorem 5.2 spends `O(n + Σ deg)` incidence per cut on it, and the
paper does the same for its own thresholds, §1.3.5). The second fact is
what does not: a test that reads `n` bits costs `n` incidence however it
is compiled, and there are `n − 1` of them on `n − 1` distinct sets.

The smallest connected graph on which the refutation-level test has full
degree, every monomial and every variable essential is `K₃` at
`k = 1 = vs − 1`: `L_1 = {∅, V} ∪ {pairs}`, the indicator is
`1 − (s_1 + s_2 + s_3) + 2 (s_1 s_2 + s_1 s_3 + s_2 s_3) − 3 s_1 s_2 s_3`
(degree 3, all 8 monomials, top coefficient `−3`; `check.json`,
`smallest_full`); every chain dies at its first set, since every
singleton has boundary 2.

### 5.3 Fewer variables, wider constraints: ranks and the interval form

The other way to write the sum over orderings is with one integer per
vertex. Let `pos : V → {0, …, n−1}` be a bijection and
`last(v) = max_{w ∈ N[v]} pos(w)`.

**Lemma 5.5 (interval form of the cut).** For `0 ≤ t ≤ n − 2` and
`S_t = {v : pos(v) ≤ t}`, `|∂_in S_t| = #{v : pos(v) ≤ t < last(v)}`.

*Proof.* `v ∈ ∂_in S_t` iff `pos(v) ≤ t` and some neighbour has position
`> t`, iff `pos(v) ≤ t < max_{w ∈ N(v)} pos(w)`; and when that maximum
exceeds `t ≥ pos(v)` it equals `last(v)`, while if `N(v) = ∅` then
`last(v) = pos(v) ≤ t` and `v` is correctly not counted. ∎

This is the interval-thickness form of the complex
(`Complex/IntervalThickness.lean`): every vertex owns the interval
`[pos(v), last(v))`, and the cut at `t` is the number of intervals
containing `t`. As a constraint system: `n ⌈log₂ n⌉` Boolean variables
(the bits of `pos`); `C(n, 2)` all-different constraints of width
`2 ⌈log₂ n⌉`; and **`n − 1` cut constraints each reading every rank**
(`last(v)` reads `N[v]`, the count ranges over all `v`): width
`n ⌈log₂ n⌉`, incidence `Θ(n² log n)`. *Checked*: the count of rank
tuples that are permutations with every interval count `≤ k` equals
`C_k(G)` on every atlas graph to 6 vertices and a sample at 7 (1,538
counts, zero failures).

So the item's dichotomy is a trade-off, not a choice: **positions give
`Θ(n²)` variables under bounded-width constraints; ranks give
`n ⌈log₂ n⌉` variables under `n` constraints of width `n ⌈log₂ n⌉`;
the incidence is `≥ n (n − 1)` either way.** Compiling a rank
constraint into bounded-width factors (comparators `pos(v) ≤ t`, the
maxima `last(v)`, a counter) returns to `Θ(n (n + m) log n)`; in the
tensor form (R6) a single factor of width `n ⌈log₂ n⌉` needs
`s ≥ (n log n)^{10/9}`, which is not `o(n √log n)`.

### 5.4 The exact count needs `n log₂ n` bits

**Lemma 5.6.** If a system of `0/1`-valued factors on `N` Boolean
variables has exactly `C_k(G)` solutions, then `N ≥ log₂ C_k(G)`. For
`K_n` and `k = n − 1`, `C_{n−1}(K_n) = n!`, so `N ≥ log₂ n! ≥ n log₂(n/e)`.

*Proof.* A `0/1` system has at most `2^N` solutions; every layout of
`K_n` has `vs = n − 1`. ∎

| `n` | `log₂ n!` | `/ n` | `B_v` (constant 1) | `/ n` | ranks `n ⌈log₂ n⌉` |
|---|---|---|---|---|---|
| 8 | 15.3 | 1.91 | 21.5 | 2.69 | 24 |
| 10 | 21.8 | 2.18 | 21.8 | 2.18 | 40 |
| 16 | 44.3 | 2.77 | 25.6 | 1.60 | 64 |
| 32 | 117.7 | 3.68 | 38.6 | 1.21 | 160 |
| 64 | 296.0 | 4.62 | 64.3 | 1.00 | 384 |
| 125 | 695.2 | 5.56 | 110.8 | 0.89 | 875 |
| 10³ | 8,529 | 8.53 | 704 | 0.70 | 10,000 |
| 10⁶ | 1.85 × 10⁷ | 18.5 | 5.39 × 10⁵ | 0.54 | 2 × 10⁷ |

(`exact_count_table`.) So, read literally — the chain count *as* the
number of common zeros of an unweighted system — the item's question has
a clean answer: **yes in `o(n²)` variables** (the rank system,
`n ⌈log₂ n⌉`, within a factor `1 + o(1)` of the lower bound), **no
within the verified budget for any `n ≥ 11`**, and the gap grows like
`log n (log log n)² / √log n`. What the lemma does not touch is what the
paper's method also allows (§1.3.6): factors with values in a
`Q`-algebra, where a sum can be large with few variables, and systems
that only *decide* — `Z ≠ 0 ⟺ C_k > 0` without `Z = C_k`. Those are
the only kinds left to item 09, and the lemma says that is where any
attempt must start.

### 5.5 An identity not organised by cuts: the sieve over supports returns the lattice

The one route to an `n`-variable sum that permutation problems are known
to have is inclusion–exclusion over the vertices missed: for Hamiltonian
paths, `Σ_S (−1)^{n−|S|} walks(S)` with `walks(S)` a matrix power on
`|S|` states, `O*(2ⁿ)` in all. The same sieve applies here, and the point
is what it leaves inside.

**Lemma 5.7.** Let `W_k(S)` be the number of sequences `(u_1, …, u_n) ∈ Sⁿ`
(repetition allowed) every one of whose prefix supports
`supp(u_1, …, u_t)`, `1 ≤ t ≤ n`, lies in `L_k`. Then
`C_k(G) = Σ_{S ⊆ V} (−1)^{n−|S|} W_k(S)`.

*Proof.* A sequence of length `n` with support `V` is a permutation, and
its prefix supports are its prefix sets; so `C_k = Σ_{u ∈ Vⁿ} P(u)
[supp(u) = V]` with `P(u)` the prefix condition (`V ∈ L_k` always). Write
`[supp(u) = V] = Σ_{S ⊇ supp(u)} (−1)^{n−|S|}` and exchange the sums. ∎

*Checked* on every atlas graph to 6 vertices and a sample at 7, every
`k` (1,405 identities, zero failures).

**Why it does not reduce the cube.** `W_k(S)` is itself a sum over the
lattice below `S`: a sequence is determined by its strict support chain
`∅ ⊂ T_1 ⊂ … ⊂ T_j ⊆ S` (single additions, all in `L_k`) and by where
its `n − j` stalls fall, a stall at support size `i` having `i` choices,
so

    W_k(S) = Σ_j c_j(S) · h_{n−j}(1, 2, …, j),

`c_j(S)` the number of such chains of length `j` and `h` the complete
homogeneous symmetric polynomial. Möbius inversion over `S` gives
`Σ_S (−1)^{n−|S|} c_j(S) = #{chains of length j with T_j = V} = [j = n] C_k(G)`,
and `h_0 = 1`: the sieve returns `C_k(G) = C_k(G)`. The walk count that
makes the Hamiltonian sieve run is a condition on **consecutive pairs**
(state: the current vertex, `|S|` states); the cut condition is a
condition on the **whole prefix support** (state: the support, `2^{|S|}`
states, `3ⁿ` in all). We found no smaller state and claim none is
impossible; what is shown is that the sieve, the one identity on record
that moves a permutation sum onto the `n`-cube, leaves the lattice sum
intact here.

### 5.6 One cut in the tensor form: the composite is not the threshold

In the tensor form (R6) the currency is wires. For a tensor network
computing the indicator `[S ∈ L_k]` from the `n` set bits, and any
bipartition `A | B` of `V`, the matrix `M_{A|B}[S_A, S_B] = [S_A ∪ S_B ∈ L_k]`
satisfies `rank M_{A|B} ≤ 2^w` with `w` the number of wires crossing any
cut of the network that separates the `A` legs from the `B` legs (the
network is a sum over the `2^w` values on the crossing wires of a
product of an `A`-side and a `B`-side term, so `M` is a sum of `2^w`
rank-one matrices; with `d`-valued wires, as R6 allows, `d^w`). Lemma 5.4 gives `log₂ rank ≤ log₂(n/2 + 1)` for
the bare threshold. Measured for the composite on every connected atlas
graph with `4 ≤ n ≤ 7`, at `k = vs − 1` and `k = vs`, over every
balanced split (`|A| = ⌊n/2⌋`), the minimum over splits of `log₂ rank`
(`split_rank_profile`; `check.json`, `split_rank_summary`):

| `n` | graphs | level | median `min_A log₂ rank` | max over graphs | trivial `⌊n/2⌋` | bare threshold `log₂(min(⌊n/2⌋, k) + 1)` | graphs above the threshold's bound |
|---|---|---|---|---|---|---|---|
| 4 | 6 | `vs − 1` | 1.58 | 1.58 | 2 | ≤ 1.58 | 83% |
| 5 | 21 | `vs − 1` | 1.58 | 2.00 | 2 | ≤ 1.58 | 71% |
| 6 | 112 | `vs − 1` | 2.00 | 2.58 | 3 | ≤ 2.00 | 91% |
| 7 | 853 | `vs − 1` | 2.00 | 2.58 | 3 | ≤ 2.00 | 87% |
| 7 | 853 | `vs` | 2.32 | 3.00 | 3 | ≤ 2.00 | 68% |

The trivial maximum is `⌊n/2⌋`. At `n = 7` and the refutation level the median graph needs 2 wires across its best balanced split against a trivial 3 and the threshold's own 2; 87% of the graphs exceed the bare threshold's rank bound at their best split, and one graph has full rank 8 across every one of the 35 balanced splits at `k = vs = 2`: the 7-cycle `C₇` (`split_rank.csv`). (The first run of this table enumerated only the splits with vertex 0 on the smaller side — 20 of the 35 at `n = 7` — and credited a second graph with full rank; the refuter agent found the bug, and the table is from the corrected enumeration.) At seven vertices
nothing separates `Θ(n)` from `Θ(log n)`, and no asymptotic claim is
made; what the table records is that the composite's crossing cost is
not the threshold's `O(log n)` on these graphs and tracks the boundary
structure instead. The per-cut cost in wires is therefore between
`log₂ rank` (measured) and `O(n + Σ deg)` (the circuit of Theorem 5.2),
and it is paid `n − 1` times.

### 5.7 The obstacle, named; the verdict on plan §0.6's chain-count kill

**The obstacle is the ordering, through its cuts — not the threshold's
width.** The chain count is a sum over orderings of a product of `n − 1`
cut tests. Each test, at the refutation level, is a function of **every**
vertex's side of the cut — a measured premise, not a theorem: all `n`
set variables essential on every connected graph to 7 vertices (§5.2;
the refuter agent's probe adds 704 of 704 random connected graphs at
8–10 vertices). Granting it, a test whose inputs are the `n` set bits of
its cut (positions, nested sets) reads all `n` of them, and one whose
inputs merely determine the `t`-set reads at least `log₂ C(n, t)`
of them, however the threshold inside is compiled; the `n − 1` tests
are on `n − 1` distinct sets; so such systems have incidence
`≥ n (n − 1)` in the first form and `≥ Σ_t log₂ C(n, t) ≈ 0.72 n²` in
the second — `Θ(n²)` either way — and the three on record have `Θ(n³ + n² k + n m)` as counted (`Θ(n² + n m)` with the standard gadgets),
and `Θ(n² log n)` (§5.1, §5.3). The threshold's own width
is real as an equation (full degree and `2^{Θ(n)}` monomials, Lemmas
5.3–5.4 and the table of §5.2) and immaterial as a cost: it compiles to
`O(n + Σ deg)` incidence per cut, and its communication rank is `O(n)`
(Lemma 5.4). Plan §0.6's parenthetical — "threshold constraints of
unbounded width are inherent" — names the half that is **not** the
obstacle; the half that is, is the number of cuts times their support.

The two ways below `n²` are both closed as far as this loop looked:
fewer cuts (a coarse chain) is Lemma 4.6, excluded on the verified route
at every `n` and on the paper route asymptotically; and an identity not
organised by cuts has one instance on record for permutation sums, the
sieve over supports, which returns the lattice sum (Lemma 5.7). The
exact count, moreover, cannot sit below `n log₂ n − 1.44 n` variables in
any unweighted scheme that handles every graph, since it must handle
`K_n` (Lemma 5.6) — above the verified budget from `n = 11`.

**The smallest example.** On `K₃` at `k = vs − 1 = 1` the cut test is
already a full-degree polynomial in all three set variables with all
eight monomials, and every chain dies at its first set. The smallest
connected graph whose refutation needs more than the first cut is the
paw (a triangle with a pendant vertex, `n = 4`, `vs = 2`) at `k = 1`:
one prefix set survives the first cut (the six orderings that start at
the pendant) and dies at the second. At `n = 7` the star `K_{1,6}` with one edge between two
leaves (`vs = 2`) at `k = 1` has forward frontier `1, 4, 6, 4, 1, 0`: the
four free leaves can be placed in any order, every one of those 24
beginnings survives four cuts, and all die at the fifth, where the centre
or an attached leaf must come. The refutation is a statement about the
fifth cut of a seven-vertex layout, and the frontier it has to clear is
binomial in the free vertices — §10's `R_b(n − j) = C(n, j)` seen from
the front. On the record's hard instances the wall sits at `0.46 n`
closed vertices (`reports/checkpoint_relaxation.md` §10), so `Θ(n)` of
the `n − 1` cut tests are consulted before the refutation; which of them
could be dropped is the coarse-chain question, Lemma 4.6's.

**Verdict: plan §0.6's chain-count kill is met**, with the obstacle
restated as above. Items 04 and 05 together leave the positive track
with one object, the lattice chain, and two excluded ways of carrying
it. **What item 09 should attempt**, since the plan gives it the
chain-count attempt: a *weighted* or *decision-only* system
(§5.4's two escapes from Lemma 5.6) that witnesses `C_k > 0` without
testing cuts — concretely, a sum over a cube of `o(n log n)` bits with
factors in a `Q`-algebra whose value is nonzero iff a chain exists — with
the stated kill that if the only identities found are organised by cuts
(positions, nested sets, ranks, coarse chains) or reduce to the sieve,
the attempt is recorded as absent and item 09 closes in one session.

### 5.8 The checks

`nice -n 19 python3 -m learning.subexp_chain` (atlas to 7 vertices,
1,252 graphs; 265.6 s on one core under the owner's load; log `05_chain/check_atlas7.log`,
results `check.json`). `vs` is item 03's subset DP, itself checked
against the permutation minimum on every atlas graph.

| check | what is compared | instances | failures |
|---|---|---|---|
| Lemma 5.1 | `chain_count_dp` (outer) against the literal sum over permutations, against the inner-boundary count, and against the number of layouts with `vs_of_layout ≤ k` | every atlas graph to 7, every `0 ≤ k < n`: 8,475 counts | **0** |
| Lemma 5.1, decision | `C_k > 0` against `vs ≤ k` | the same | **0** |
| `K_n` | `C_k(K_n) = n!` for `k ≥ n − 1`, `0` below | `n ≤ 7` | **0** |
| Theorem 5.2 | CaDiCaL model count of `Φ_{G,k}` (blocking over all variables) against `C_k` | every atlas graph to 6 and a sample at 7, every `k`: 1,391 counts | **0** |
| Theorem 5.2, sizes | `cnf_size` against `cnf_size_formula` | the same | **0** |
| Lemma 5.3 | degree `deg(u) + 1`, `2^{deg(u)+1} − 2` monomials | every vertex of every atlas graph: 8,475 | **0** |
| Lemma 5.4 | the top coefficient against `(−1)^{n−k} C(n−1, k)` | `n ≤ 7`, every `k`: 28 | **0** |
| Lemma 5.5 | the rank/interval count against `C_k` | every atlas graph to 6 and a sample at 7, every `k`: 1,538 | **0** |
| Lemma 5.7 | the sieve against `C_k` | every atlas graph to 6 and a sample at 7, every `k`: 1,405 | **0** |
| §5.2 | degree, monomials, essential variables of `[S ∈ L_k]` | every atlas graph, every `k`: 8,475 rows | measurement |
| §5.6 | `rank M_{A|B}` over every balanced split | connected atlas graphs, `4 ≤ n ≤ 7`, two levels | measurement |

`tests/test_subexp_chain.py` (9 tests) runs the same checks to 4–5
vertices in the gate.

### 5.9 What this does not claim

- That no system within §1.3.8's budget decides `vs ≤ k`: Lemma 5.6
  excludes unweighted exact counts, Lemma 4.6 excludes chain-carrying
  certificates, Lemma 5.7 shows the one sieve on record returns the
  lattice; weighted and decision-only systems are untouched, and "we
  found no identity not organised by cuts" is a statement about this
  session's search, not about existence.
- That the cut test's dependence on every vertex is a theorem: it is
  measured to 7 vertices on connected graphs at `k = vs − 1`; the
  `n (n − 1)` incidence bound of §5.7 holds for systems in which each
  cut is tested on bits that determine its set, and the measured fact is
  its premise at small `n`.
- That the split ranks of §5.6 say anything asymptotic.
- That Theorem 5.2's system is new: it is the nested-chain encoding of
  `reports/checkpoint_relaxation.md` §8 and the position encoding of
  `satisfiability/mosp_encoding.py` with determined auxiliaries, written
  down so that its model count is the chain count; the interval form of
  Lemma 5.5 is the complex's interval thickness (§3.1 row 8); the sieve
  of Lemma 5.7 is the Hamiltonian-path sieve applied to a different
  predicate. "We found no prior statement" of Lemma 5.4's rank bound or
  of the stall reorganisation in §5.5, and no novelty is claimed for
  either.
- That the hypothesis `SubexpCount k` is true, or that anything here
  depends on it: §5.1's conditional runtime is what it would give.
- That the checks prove anything: they precede the proofs, as TASK.md
  requires. One refuter subagent (the only one used) checked every lemma
  with its own code to 5 vertices (Lemma 5.1 on 251 pairs; Theorem 5.2
  on 283 model counts including `k = n`, isolated vertices and `n = 1`;
  Lemma 5.3 on 231 vertices; Lemma 5.4 on 168 splits and all `n ≤ 9`;
  Lemma 5.5 on 1,524 cuts; the stall identity of §5.5, which the module
  does not check, on 6,258 triples and its Möbius sentence on 1,302; the
  table arithmetic of §5.1 and §5.4 exactly). It found: the §5.1
  headline wrong (`Θ(n²)` for a counted `Θ(n² k)`; fixed, with the R3
  sentence); the odd-`n` split enumeration bug of §5.6 (fixed, table
  regenerated, one of the two "full rank" graphs withdrawn); the
  incidence sentence of §5.7 stated as a theorem on a measured premise
  and with a constant the weaker hypothesis does not give (restated);
  the exact-count sentence of §5.7 missing "on `K_n`" (fixed); the unit
  clause of Theorem 5.2 for `k ≥ n` (stated); "one ordering" for "one
  prefix set" (fixed). No lemma was wrong.
- That anything is in Lean: the item is mathematics; Lemma 5.1 is a
  one-line statement against `VertexSeparation.lean` and could be taken
  by item 08 or the reserve if needed.
- That anything was solved, run on an instance, or downloaded:
  `solutions/` is untouched, no instance under `MOSP_Instances/` or the
  pathwidth dataset was touched, and the only compute is the atlas
  check.

### 5.10 Regenerate

    D=reports/scratch/subexp_pathwidth/05_chain
    nice -n 19 python3 -m learning.subexp_chain --nmax 7 > $D/check_atlas7.log
    python3 -m pytest tests/test_subexp_chain.py -q
    python3 -c "from learning.subexp_chain import exact_count_table; [print(r) for r in exact_count_table()]"

## 6. Algorithms from the counting theorem for problems on graphs of linear pathwidth: the crossover (item 06, 2026-11-04)

The item asks, for every problem with a published `c^{pw} · poly` or
`c^{tw} · poly` dynamic program given a decomposition, whether the problem
has a bounded-width CNF with `O(n)` variables in the sense of §1.3 — one
variable per vertex (or per edge), auxiliaries that are functions of those,
total incidence linear — and, for each that does, **the algorithm** (encode,
run the counting machine, read the count), **its running time** in the paper
form and in the verified form, and **the crossover**: the pathwidth above
which the counting bound is below the dynamic program's `c^{pw}`. The
problems are taken from Lokshtanov, Marx & Saurabh (SODA 2011; *ACM TALG*
14(2), 2018, the `[LMS18]` the ETH paper cites), Cygan, Nederlof,
Pilipczuk, Pilipczuk, van Rooij & Wojtaszczyk (FOCS 2011; *ACM TALG* 18(2),
2022, Cut & Count) and Lampis (*The primal pathwidth SETH*, SODA 2025).
**None of the three is held**; the list of problems and the bases are
quoted from their abstracts and from the ETH paper's own §1.1.3 (lines
225–236 of `01_audit/eth.txt`), and item 11 records them in
`literature/MISSING.md`. Everything stated as an algorithm here was checked
by brute force on every graph of the atlas to 7 vertices before it was
stated (§6.5); the independent-set algorithm and the crossover inequality
are in Lean (§6.4).

Code: `learning/subexp_crossover.py` (10 tests in
`tests/test_subexp_crossover.py`). Lean:
`lean/MOSPFormalization/SubexpPathwidth/Crossover.lean`. Scratch:
`reports/scratch/subexp_pathwidth/06_crossover/`.

### 6.0 Two forms of the bound, and what "now void" means

**The two forms.** For a `k`-CNF on `N` variables with `M` clauses the
counting theorem gives (§1.3.2, §1.3.4):

- *paper form*: `(N + M)^{O_k(1)} · 2^{O_k(N log log N / √log N)}`, and
  `2^{O_{k,D}(N / √log N)}` when `M ≤ D N` (Theorem 1.1, lines 56–62);
- *verified form*: `C (L + 1)^d · 2^{A · ρ(N)}`,
  `ρ(N) = N (log log(N + 16))² / √log(N + 16)`, `L` the formula's bit
  length (`SubexpCount k`, §2.2; constants `C, A, d` exist and are not
  given).

Both are `2^{o(N)}`; with `N = a n + b` in the number of vertices, both are
`2^{o(n)}` (`runtimeScale_isLittleO`). A problem "fits" when it has such an
encoding; the encodings below all have `N ≤ 8 n` on every graph, or
`N = O(n + m)`, in which case they fit on graphs with `m = O(n)` edges
(bounded degree, `G(n, c/n)`, the Chu & Stuckey ridge).

**The correction, first.** The item says "beside each: the SETH-tight lower
bound it previously carried, now void". That is right about the *derivation*
and wrong about the *statement*, and the report says so in every row:

1. The lower bounds of `[LMS18]` and of Cut & Count are theorems of the form
   *SETH ⇒ no `(c − ε)^{pw} · poly` algorithm*. If the counting theorem
   stands, SETH is false (SETH ⇒ ETH), so these theorems have a false
   premise and derive nothing. **As SETH consequences they are void.**
2. The statements themselves — "no `(c − ε)^{pw} n^{O(1)}` algorithm" — are
   **not refuted** by anything in this section. The algorithms here run in
   `2^{o(n)} · poly`, which is below `(c − ε)^{pw}` only where `pw` is
   linear; on graphs of small pathwidth they are slower than the dynamic
   program, and the combined algorithm `min(c^{pw}, 2^{o(n)})` is not of
   the form `(c − ε)^{pw} · poly` either. A refutation would need an
   algorithm with that time bound on *every* graph; none is on record and
   none is given here.
3. The ETH paper says exactly this of `[LMS18]` (lines 231–236): "the
   treewidth dependence of Independent Set and Dominating Set also follow
   from the hypothesis that unrestricted CNF-SAT admits no
   `2^{(1−δ)n} poly(n, m)`-time algorithm for any constant `δ > 0`
   [Bri14, RV13, LMS18]. Theorem 1.1 gives a running-time guarantee for
   each fixed clause width `k`, while this hypothesis allows the width to
   grow with `n`." So every row's lower bound **survives as a consequence
   of the unrestricted-CNF-SAT hypothesis** wherever its reduction is from
   CNF-SAT of unbounded width — which, as we read the abstracts, is how
   `[LMS18]` and Cut & Count's lower bounds are proved (they build a path
   decomposition of width about the number of variables of an arbitrary
   CNF).

What the crossover *does* say is the positive statement: on every class of
linear pathwidth, for every base `c > 1`, the counting algorithm's
exponential factor is eventually below the dynamic program's
(`counting_beats_dp_eventually`, §6.3). It is a statement about algorithms,
not about hypotheses.

### 6.1 The catalogue

`n` vertices, `m` edges, `Δ` the maximum degree. "Count-preserving" means the
model count of the formula *is* the number of the combinatorial objects (the
auxiliaries are functions of the primary variables), so the counting machine
returns the count and not only the decision. "Fits" names the condition
under which the variable count is `O(n)`. The last column is the SETH-tight
bound the problem carried, with its status as §6.0 states it (void as a
SETH consequence; not refuted; surviving under the unrestricted-CNF-SAT
hypothesis where the reduction is from unbounded width).

| problem | DP base `c` (given a path decomposition) | encoding (§6.2) | variables `N` | width | count-preserving | fits | lower bound it carried |
|---|---|---|---|---|---|---|---|
| counting independent sets | `2` (folklore; `[LMS18]`) | `¬x_u ∨ ¬x_w` per edge | `n` | 2 | yes | every graph | `(2 − ε)^{pw}` for Independent Set, `[LMS18]` |
| maximum independent set / minimum vertex cover (`α ≥ t`) | `2` | the same + adder-tree threshold `Σ x ≥ t` | `≤ 8 n` (measured `≤ 6.98 n` auxiliaries) | 3 | yes (`#{S : |S| ≥ t}`) | every graph | the same |
| counting proper `q`-colourings; `q`-colourability | `q` | one variable per (vertex, colour); exactly one; `≠` across edges | `q n` | `max(q, 2)` | yes | every graph, fixed `q` | `(q − ε)^{pw}`, `[LMS18]` |
| dominating set (count; `γ ≤ t`) | `3` (`[LMS18]`'s `3^{pw}` DP) | `x_v ∨ ⋁_{u ∈ N(v)} x_u` | `n`, width `Δ + 1`; or `n + 2m` at width 3 by Tseitin | `Δ + 1` / 3 | yes | bounded degree (direct, `k ≥ Δ + 1`); `m = O(n)` (Tseitin) | `(3 − ε)^{pw}`, `[LMS18]` |
| Max-Cut (`≥ t`; count of sides with cut `≥ t`) | `2` | side bit per vertex, XOR per edge, threshold | `n + O(m)` (measured `≤ 5.9 (n + m)`) | 3 | yes | `m = O(n)` | `(2 − ε)^{pw}`, `[LMS18]` |
| odd cycle transversal (`≤ t`) | `3` | deletion bit and side bit per vertex; two width-4 clauses per edge; threshold | `2n + O(n)` | 4 | **no** (decision only: the count is `Σ_D 2^{|D|} 2^{cc(G − D)}`) | every graph | `(3 − ε)^{pw}`, `[LMS18]` |
| partition into triangles | `2` | one variable per triangle, exactly one per vertex | `#triangles + O(n)` | 3 | — | bounded degree only; **not encoded or checked here** | `(2 − ε)^{pw}`, `[LMS18]` |
| Hamiltonian cycle: the parity `#HC mod 2` | Cut & Count `4^{pw}`; `(2 + √2)^{pw}` by Cygan, Kratsch & Nederlof (2013, not held) | edge bit per edge, side bit per vertex, exactly two chosen edges at each vertex, equal sides across chosen edges, `v_0` on side 0 | `m + n + O(m)` (measured `≤ 16.5 (n + m)`) | 3 | yes: `count = Σ_{2-factors X} 2^{cc(X) − 1}` | `m = O(n)` | `(2 + √2 − ε)^{pw}` (Cygan–Kratsch–Nederlof), as above |
| Hamiltonian cycle: the decision | as above | the same with the isolation lemma's weights, as a weighted count | as above, values in `Q[y]/(y^ℓ)`, `ℓ = 2mn + 1` | 3 | — | `m = O(n)`, **paper form only, by the Section 3.1 remark** (§6.2.7); randomized | as above |
| Steiner tree, feedback vertex set, connected vertex cover, connected dominating set (Cut & Count) | `3, 3, 3, 4` | the same recipe: a local part with an `O(n + m)`-variable encoding and a side bit per vertex | `O(n + m)` | 3 | — | `m = O(n)`, paper form, randomized; **listed, not encoded or checked here** | `(3 − ε)^{pw}`, `(3 − ε)^{pw}`, `(3 − ε)^{pw}`, `(4 − ε)^{pw}` (Cygan et al. 2011) |
| SAT parameterised by primal pathwidth | `2` (the standard DP) | the formula itself | its `n` variables | its width | yes | every `k`-CNF, fixed `k` | Lampis's pw-SETH, "no `(2 − ε)^{pw}` for SAT", SODA 2025 (not held; stated, as we read the abstract, for unbounded width) |

Three remarks on the table.

- **Every row with one variable per vertex fits on every graph; every row
  whose constraints read edges fits at `m = O(n)`.** Dominating set at
  width `Δ + 1` is the one row where the *width* is the obstacle in the
  verified form (`SubexpCount k` needs `k ≥ Δ + 1`); its Tseitin form moves
  the cost to the variable count, `n + 2m`, which is the general pattern
  of §1.3.5: a wide constraint costs its width in incidence and nothing
  more.
- **The ordering problems are absent**, as item 05 said they must be
  (§5.4, Lemma 5.6): a permutation witness is `n log₂ n` bits and no row
  here has one. The SAT row is the degenerate case — the problem *is* a
  CNF — and is the cleanest instance of the crossover (§6.3).
- **Counting is free where the encoding is count-preserving.** Corollary
  1.3 states independent sets and colourings; the threshold, dominating-set
  and Max-Cut rows are the same statement with an auxiliary circuit whose
  gate values are determined, which the paper's Corollary 1.2 proof uses for
  the same purpose (lines 86–91).

### 6.2 The algorithms, with proofs

Throughout, `F` is a CNF on `N` variables of width `≤ k`; **the algorithm**
is: build `F` from `G` (polynomial time), run the counting machine of
`SubexpCount k` on `encodeCNF F`, read the count tape (or the answer bit);
**the time** is `C (L + 1)^d · 2^{A ρ(N)}` in the verified form with
`L = formulaBitLength F = O((N + M) · N)` in the collection's unary literal code (polynomial, which is all that matters), and
`(N + M)^{O(1)} 2^{O(N log log N / √log N)}` in the paper form,
`2^{O(N / √log N)}` when `M = O(N)`. With `N ≤ a n + b` every one of these is
`2^{o(n)} · poly`. What is specific to each problem is the encoding and its
correctness, which is what is proved.

**6.2.1 Counting independent sets** (`indepCNF`, Lean). `F` has one variable
per vertex and the clause `¬x_u ∨ ¬x_w` per edge: `N = n`, `M = m`, width 2.
*Lemma 6.1* (`indepCNF_eval_iff`, `count_indepCNF`): an assignment satisfies
`F` iff `{v : x_v = 1}` is independent, so `#F` is the number of independent
sets. *Proof.* A clause `¬x_u ∨ ¬x_w` fails exactly when `x_u = x_w = 1`
with `uw ∈ E`. ∎ *Theorem 6.1* (`indepCount_subexp`): under `SubexpCount 2`
one primitive machine writes the number of independent sets of every graph
on its count tape within `C (L + 1)^d 2^{A ρ(n)}` steps, `L` the bit length
of `encodeCNF (indepCNF G)`; `A ρ(n) = o(n)`. This is Corollary 1.3's first
sentence as a consequence of the comparator statement.

**6.2.2 Maximum independent set, minimum vertex cover** (`indep_atleast_cnf`).
Add to `F` the constraint `Σ_v x_v ≥ t` compiled as a circuit: a **binary
adder tree** summing the `n` input bits (ripple-carry adders with full
adders built from two XORs, two ANDs and an OR), then a comparator against
the constant `t`, every gate Tseitin-encoded (`z ↔ a ⊕ b` in four clauses
of width 3, `z ↔ a ∧ b` and `z ↔ a ∨ b` in three), the output asserted by a
unit clause. *Lemma 6.2 (size).* The tree has at most `n − 1` additions; the
additions at level `j` number at most `n / 2^{j+1}` and add numbers of
`j + 1` bits at `≤ 5` auxiliaries per bit, so the auxiliaries total at most
`5 n Σ_{j ≥ 0} (j + 1) / 2^{j+1} = 10 n`, plus `2 ⌈log₂ n⌉ + 1` for the
comparator and the constant; measured, `≤ 6.98 n` for every `n ≤ 200` and
every `t ∈ {1, ⌈n/2⌉, n}` (`threshold_aux_ratio`). Width 3 throughout.
*Lemma 6.3 (correctness, count-preserving).* Every auxiliary is defined by
an equivalence with its inputs, so each assignment to `x` extends in exactly
one way to the auxiliaries; the adder tree's output is the binary value of
`Σ x_v` (ripple-carry adders add; induction over the tree), and the
comparator's output bit is `[Σ x_v ≥ t]` (from the least significant bit,
`ge_i = (b_i ∧ ge_{i−1})` where `t_i = 1` and `(b_i ∨ ge_{i−1})` where
`t_i = 0`, `ge_{−1} = 1`). Hence `#F = #{S independent : |S| ≥ t}`, and `F`
is satisfiable iff `α(G) ≥ t`. ∎ **The algorithm**: binary search on `t`
(`⌈log₂ n⌉` counting calls), a witness by the standard self-reduction (`n`
calls); vertex cover is the complement. Checked: every `(G, t)` with `G` in
the atlas to 7 vertices and `0 ≤ t ≤ n + 1`, 10,979 formulas, count and
satisfiability both right (§6.5). This is Warners's linear-size encoding of
linear constraints (Warners 1998, *IPL* 68(2), not held) in the form the
ETH paper uses for its own thresholds (lines 86–91: "a Boolean circuit with
at most two inputs per gate and size `O(n)` tests whether an assignment
satisfies at least `b` sampled clauses").

**6.2.3 Counting proper `q`-colourings** (`coloring_cnf`; Lean `coloringCNF`, `count_coloringCNF`, `coloringCount_subexp`). Variables
`x_{v,c}`, `v ∈ V`, `c ∈ [q]`: `N = q n`; for each `v` one clause
`⋁_c x_{v,c}` (width `q`) and `C(q, 2)` clauses `¬x_{v,c} ∨ ¬x_{v,c'}`; for
each edge `uw` and colour `c`, `¬x_{u,c} ∨ ¬x_{w,c}`. *Lemma 6.4.* The models
are in bijection with the proper `q`-colourings (`v ↦` the unique `c` with
`x_{v,c} = 1`). ∎ This is Corollary 1.3's second sentence; the time is
`2^{o(q n)} = 2^{o(n)}` at fixed `q` (`runtimeScale_mul_isLittleO`), and the
answer bit decides `q`-colourability (`coloringCount_subexp`). Checked for `q = 2, 3` on the whole
atlas and `q = 4` to 6 vertices (2,712 counts).

**6.2.4 Dominating set** (`domset_cnf`, `domset_atmost_cnf`). Direct form:
the clause `x_v ∨ ⋁_{u ∈ N(v)} x_u` per vertex, `N = n`, width `Δ + 1`,
models = dominating sets. Tseitin form: the same OR as a chain of binary
ORs with `deg(v)` auxiliaries per vertex, `N = n + 2m`, width 3,
count-preserving (each OR auxiliary is determined). Minimum dominating set:
`Σ x_v ≤ t` by Lemma 6.2 applied to the negated bits. The direct form fits
the verified statement at `k ≥ Δ + 1`, i.e. on graphs of bounded degree;
the Tseitin form fits at `m = O(n)`. Checked: 1,252 counts in each form and
9,727 decisions `γ ≤ t`.

**6.2.5 Max-Cut** (`maxcut_cnf`). A side bit per vertex, an XOR auxiliary
`y_e ↔ x_u ⊕ x_w` per edge, `Σ_e y_e ≥ t` by Lemma 6.2: `N = n + O(m)`,
width 3, `#F = #{sides : cut ≥ t}`, satisfiable iff `maxcut(G) ≥ t`. Fits at
`m = O(n)`; binary search on `t`. (In the paper form the same can be read
off the weighted count `Σ_x Π_e (1 + (y − 1)[x_u ≠ x_w])` in `Q[y]/(y^{m+1})`,
the cut polynomial; the factor count is `m`, so R2 asks `m = O(n)` as well.)
Checked: 14,846 counts and decisions.

**6.2.6 Odd cycle transversal** (`oct_cnf`), decision only. A deletion bit
`d_v` and a side bit `c_v` per vertex; per edge `uw` the clauses
`d_u ∨ d_w ∨ c_u ∨ c_w` and `d_u ∨ d_w ∨ ¬c_u ∨ ¬c_w` (width 4; "not both
deleted ⇒ different sides"); `Σ d_v ≤ t`. Satisfiable iff some set of at
most `t` vertices leaves a bipartite graph. Not count-preserving: a model is
a pair (deletion set, 2-colouring of the rest) with the side bits of the deleted vertices free, `Σ_D 2^{|D|} 2^{cc(G − D)}` in all (the refuter's correction; the first draft omitted the `2^{|D|}`).
`N = 2n + O(n)`; fits on every graph (the edge clauses have no
auxiliaries). Checked: 9,727 decisions.

**6.2.7 Hamiltonian cycle, by Cut & Count** (`hamcycle_cutcount_cnf`). The
Cut & Count method (Cygan et al. 2011) replaces connectivity by a *count*:
pairs (solution candidate `X`, consistent cut of `X`) number `2^{cc(X)}`,
so modulo a power of two only the connected candidates survive; the
isolation lemma makes the count odd when a solution exists. The counting
theorem replaces the `c^{pw}` dynamic program that evaluates the count. For
Hamiltonian cycles: a bit `e` per edge, a bit `s_v` per vertex; at every
vertex exactly two incident edge bits are set (two thresholds, Lemma 6.2,
`O(deg)` auxiliaries each); for every edge `e = uw`, `e → (s_u ↔ s_v)` (two
clauses of width 3); `s_{v_0} = 0`. `N = m + n + O(m)`, width 3.
*Lemma 6.5.* The models are the pairs `(X, σ)` with `X` a 2-regular spanning
subgraph (a 2-factor) and `σ` a side assignment constant on each component
of `X` with `v_0` on side 0, so `#F = Σ_X 2^{cc(X) − 1}`. *Lemma 6.6.* For
`n ≥ 3`, a 2-factor with one component is a Hamiltonian cycle and
conversely; hence `#F ≡ #HC (mod 2)`. ∎ **Unconditional consequence
(verified form, deterministic)**: *the parity of the number of Hamiltonian
cycles of a graph with `m = O(n)` edges is computed in `2^{o(n)} · poly`
under `SubexpCount 3`.* Checked: parity on all 1,249 atlas graphs with
`n ≥ 3`, and the exact value `Σ_X 2^{cc(X) − 1}` against two-factor
enumeration on the 1,209 with `m ≤ 15`.

*The decision needs weights.* With independent uniform edge weights
`w_e ∈ [1, 2m]`, the minimum-weight Hamiltonian cycle is unique with
probability `≥ 1/2` (the isolation lemma: Mulmuley, Vazirani & Vazirani
1987; Cygan et al. 2011, Lemma 2.1, not held), and then in
`Z(y) = Σ_X 2^{cc(X) − 1} y^{w(X)} ∈ Q[y]/(y^ℓ)`, `ℓ = 2mn + 1`, the
coefficient of `y^{w_min}` is odd; any odd coefficient is a certificate that
a Hamiltonian cycle exists (the even contributions come from `cc ≥ 2`).
`Z` is the sum of products of §1.3.1 with one further factor
`(1 − e) + e · y^{w_e}` per edge, degree 1 in its variable, values in the
commutative `Q`-algebra `Q[y]/(y^ℓ)`. **Where this stands with respect to
the paper**: the counting routine of Section 3 "also works with coefficients
in any commutative `Q`-algebra `A`" (line 1162), and `ℓ` is polynomial, so
the Section 3–5 route (the `ρ(N)` exponent) carries algebra-valued factors
by the paper's own remark; but Theorem 2.2 is *stated* for counts of common
zeros over `F_2`, and Theorem D.1 (the tensor form, the sharper exponent)
takes entries in `(Z/2^{P_0})[V]/(V^ℓ)` **with `ℓ ≤ C s`**, which
`ℓ = 2mn + 1` violates at `m = O(n)` (`s = O(n)`), and replacing the
integer weights by free gated variables (a weight `2^w` as `w` free
variables) costs `Σ_e w_e = Θ(m²)` variables, and a threshold `Σ_e w_e x_e ≤ W` on the weight through binary adders costs `Θ(m log m)` gates — both over the `O(n)` budget. So the Hamiltonian-cycle
*decision* in `2^{o(n)}` on sparse graphs rests on the Section 3.1 remark
and is not a theorem the paper states; it is marked so in the table, and
the verified `SubexpCount k` (integer counts only) does not give it.
Checked: the weighted decision with one random weight vector per graph is
sound on all 1,249 graphs and decides "yes" on 435 of the 443 graphs with a
cycle (the isolation lemma promises `≥ 1/2`).

**6.2.8 The other Cut & Count problems.** Steiner tree, feedback vertex set,
connected vertex cover and connected dominating set have the same shape —
a local part (a vertex or edge selection with degree or cover constraints;
for feedback vertex set the marker trick, which adds a threshold on
`|E(X)| − |X|`) and a side bit per vertex with the consistency clauses — so
each has an `O(n + m)`-variable width-3 encoding whose count is
`Σ_X 2^{cc(X) − 1}` over the candidates, and the same remark about weights
applies. We state this as the recipe and **encode and check none of them**;
each would need its own lemma 6.5.

**6.2.9 SAT by primal pathwidth.** For a `k`-CNF the formula is its own
encoding: `N = n`, and the counting theorem's `2^{o(n)}` stands beside the
`2^{pw} · poly` dynamic program over a path decomposition of the primal
graph (Lampis's `pw`). This row needs no proof and no check.

### 6.3 The crossover proposition

**Proposition 6.7** (`rpow_le_of_crossover`, `crossoverThreshold_eventually_lt`,
`counting_beats_dp_eventually`). Let `E(n)` be the counting bound's exponent
(`A ρ(n)` in the verified form; `O(n / √log n)` or
`O(n log log n / √log n)` in the paper form) and `c > 1` the dynamic
program's base. Then

    2^{E(n)} ≤ c^{pw}    ⟺    pw ≥ pw*(n) := E(n) / log₂ c,

and `pw*(n) = o(n)`: for every `β > 0` and every `A`, `pw*(n) < β n` for
all large `n`. Hence **on every class of linear pathwidth
(`pw(G) ≥ β n`), for every base `c > 1`, the counting bound's exponential
factor is at most the dynamic program's for all large `n`** — the
polynomial factors and the constants `A`, `C`, `d` aside, which are
outside the statement here as they are in the paper. *Proof.* Take
logarithms base 2; `ρ = o(n)` is `runtimeScale_isLittleO`. ∎

**The table** (`crossover_table`; constants 1 in both exponents — the true
`A` is unknown, and so is the paper form's `O_k`):

| `c` | `n` | paper (fixed density `M = O(N)`): `pw* = n / (log₂ c · √ln n)` | `pw*/n` | verified: `pw* = ρ(n) / log₂ c` | `pw*/n` |
|---|---|---|---|---|---|
| 2 | 10² | 47 | 0.466 | 111 | 1.115 |
| 2 | 10³ | 380 | 0.380 | 1,423 | 1.423 |
| 2 | 10⁴ | 3,295 | 0.330 | 16,245 | 1.625 |
| 2 | 10⁵ | 29,472 | 0.295 | 175,964 | 1.760 |
| 2 | 10⁶ | 269,040 | 0.269 | 1,854,972 | 1.855 |
| 3 | 10² | 29 | 0.294 | 70 | 0.703 |
| 3 | 10³ | 240 | 0.240 | 898 | 0.898 |
| 3 | 10⁴ | 2,079 | 0.208 | 10,250 | 1.025 |
| 3 | 10⁵ | 18,595 | 0.186 | 111,021 | 1.110 |
| 3 | 10⁶ | 169,745 | 0.170 | 1,170,357 | 1.170 |
| 4 | 10² | 23 | 0.233 | 56 | 0.557 |
| 4 | 10³ | 190 | 0.190 | 711 | 0.711 |
| 4 | 10⁴ | 1,648 | 0.165 | 8,123 | 0.812 |
| 4 | 10⁵ | 14,736 | 0.147 | 87,982 | 0.880 |
| 4 | 10⁶ | 134,520 | 0.135 | 927,486 | 0.927 |

Three things the table shows that the proposition does not. **The verified
exponent is `o(n)` only in the limit**: with constant 1, `ρ(n) / n =
(ln y)² / √y` with `y = ln(n + 16)` is below 1 for `n ≤ 49`, *above 1 from `n = 50` to `y ≈ 5,504`, i.e. `n ≈ e^{5,504}`*, with its
maximum `16/e² ≈ 2.17` near `n ≈ 10^{23.7}` (the refuter's correction of a first
draft that said "until `e^{5,600}`"), and it rises through the table (1.1 → 1.9 for
`c = 2`); for
`c = 2` the verified crossover lies beyond every `n` in the table, and for
`c = 4` it is at `pw ≈ 0.93 n` at `n = 10⁶`. **The paper form's crossover is
at a constant fraction that falls slowly**: `pw*/n = 1 / (log₂ c · √ln n)`,
from 0.47 at `n = 100` to 0.27 at `n = 10⁶` for `c = 2`, and a factor
`log₂ c` lower for larger bases. So "beats the DP once `pw > n / (log₂ c
√log n)`" is the paper form with constant 1, exactly as the item phrases
it, and the verified form says the same thing only asymptotically. The paper
column is Theorem 1.1's *fixed-density* bound; on dense graphs (`indepCNF` with
`m = Θ(n²)`) the applicable paper bound carries the extra `log log n`.

**The table is in the variable count, which equals the vertex count only for
the independent-set count** (the refuter's gap). The exponent is in `N`, and
the other encodings have `N = a n` with the constants of §6.5 — `a = q` for
`q`-colouring, `≈ 8` for the threshold, `≈ 13` for Max-Cut at `m = n`, `≈ 33`
for Hamiltonian cycle at `m = n` — so with the same constant-1 convention the
threshold ratio becomes `a / (log₂ c · √ln(a n))`:

| encoding, `N = a n` | DP base `c` | `pw*/n` at `n = 10²` | at `10⁴` | at `10⁶` |
|---|---|---|---|---|
| counting proper 3-colourings | 3 | 0.79 | 0.59 | 0.49 |
| counting proper 4-colourings | 4 | 0.82 | 0.61 | 0.51 |
| maximum independent set (`a ≈ 8`) | 2 | 3.09 | 2.38 | 2.01 |
| Max-Cut at `m = n` (`a ≈ 13`) | 2 | 4.85 | 3.79 | 3.21 |
| Hamiltonian cycle at `m = n` (`a ≈ 33`, base `2 + √2`) | 3.41 | 6.54 | 5.23 | 4.48 |

Only the colouring counts have a crossover inside the table at constant 1;
the threshold, Max-Cut and Hamiltonian-cycle encodings have none at any
`n ≤ 10⁶`. This is the convention, not a measurement: the true constants are
unknown in both columns, and Proposition 6.7 is unchanged (every `a n` is
still `o(n)` in the exponent).

**The classes on the far side** (linear pathwidth, `m = O(n)` so every row
of §6.1 fits in its fixed-density form):

- **`G(n, c/n)`**: `pw ≥ β*(c) n` with high probability, with
  `β*(c) = 0.0087, 0.061, 0.171, 0.263, 0.337` at `c = 3, 4, 6, 8, 10`,
  proved (`FirstMomentAsymptotics.lean`, Theorem A of
  `reports/random_graph_first_moment.md`; the exact values are where the
  first-moment rate vanishes, `reports/separator_moment.md` §0). For
  `c = 10` the far side (`β = 0.337`) is above the paper-form threshold of
  the independent-set count (`a = 1`) for `c_{DP} = 2` from `n ≈ 10⁴` on and for `c_{DP} ≥ 3` from `n = 100`;
  for `c = 3` (`β = 0.0087`) it is not reached in the table at any base.
- **Bounded-degree expanders**: `pw ≥ tw ≥ Ω(n)` (every balanced separator
  is `Ω(n)`, and a graph of treewidth `k` has one of size `k + 1`; standard,
  Robertson & Seymour, not held; `tw ≤ pw` is `Sandwich.lean`). The
  constant depends on the expansion and is not computed here.
- **The Chu & Stuckey ridge**: the MOSP graphs of the 125-customer classes
  have `pw/n` (`= (optimum − 1)/n`) from 0.19 at density 2 to 0.82 at
  density 10 (`CLAUDE.md`, the scale-test paragraph), with `m/n ≈ 3` at
  density 2. At `n = 125` the paper-form thresholds with constant 1 are
  `pw*/n = 0.455, 0.287, 0.228` for `c = 2, 3, 4`: the density-2 ridge
  (0.18–0.29) sits below the `c = 2` line and at the `c = 3–4` lines, the
  dense classes above all three. Nothing follows for any run: the constants
  are unknown and `n = 125` is not asymptotic.

### 6.4 Lean

`lean/MOSPFormalization/SubexpPathwidth/Crossover.lean`, imported by
`MOSPFormalization.lean`; `lake build` clean; no `sorry`, no `axiom`; every
declaration on `[propext, Classical.choice, Quot.sound]` or fewer
(`06_crossover/axiom_check.log`, 24 declarations).

| name | statement |
|---|---|
| `edgeClause u w`, `indepCNF G` | the clause `¬x_u ∨ ¬x_w`; Corollary 1.3's formula as a `SAT.CNF (Fin n)` |
| `indepCount G` | the number of independent sets (Mathlib's `IsIndepSet`) |
| `indepCNF_width` | `WidthAtMost 2 (indepCNF G)` |
| `indepCNF_eval_iff` | `(indepCNF G).eval a = true ↔ G.IsIndepSet {v ∣ a v = true}` |
| `count_indepCNF` | `SAT.count (indepCNF G) = indepCount G` |
| `indepCount_subexp` | `SubexpCount 2 →` a primitive machine, constants `C, A > 0`, `d > 0`, with `A ρ(n)` a subexponential exponent, such that on `encodeCNF (indepCNF G)` it halts with `countWord (indepCount G)` on its count tape and `decide (0 < indepCount G)` as its answer within `C (L + 1)^d 2^{A ρ(n)}` steps, for every `G` on `n` vertices |
| `colVar v c`, `aloClause v`, `coloringCNF G q` | `x_{v,c}` as `finProdFinEquiv (v, c) : Fin (n * q)`; `⋁_c x_{v,c}`; Corollary 1.3's colouring formula |
| `coloringCount G q` | the number of proper colourings `Fin n → Fin q` |
| `coloringCNF_width` | `WidthAtMost (max q 2) (coloringCNF G q)` |
| `coloringCNF_eval_iff` | a model has exactly one colour at each vertex and no equal colours across an edge |
| `count_coloringCNF` | `SAT.count (coloringCNF G q) = coloringCount G q` |
| `runtimeScale_mul_isLittleO`, `isSubexpExponent_runtimeScale_mul` | `ρ(n q) = o(n)` at fixed `q` |
| `coloringCount_subexp` | `SubexpCount (max q 2) →` a machine counts the proper `q`-colourings of every `G` and decides `q`-colourability within `C (L + 1)^d 2^{A ρ(n q)}` steps |
| `crossoverThreshold A c n` | `A ρ(n) / log₂ c` |
| `rpow_le_of_crossover` | `1 < c → crossoverThreshold A c n ≤ pw → 2^{A ρ(n)} ≤ c^{pw}` (real powers) |
| `crossoverThreshold_eventually_lt` | `1 < c → 0 < β → ∀ᶠ n, crossoverThreshold A c n < β n` |
| `counting_beats_dp_eventually` | `1 < c → 0 < β → ∀ᶠ n, ∀ G : SimpleGraph (Fin n), β n ≤ pathwidth G → 2^{A ρ(n)} ≤ c^{pathwidth G}` |

`indepCount_subexp` is proved by unpacking `SubexpCount 2` at `indepCNF G`
(width by `indepCNF_width`), projecting the located trace to the plain step
(`Trace.config_of_locatedStep`) and rewriting the count by
`count_indepCNF`; the time bound is `runtimeBound_eq`. The machine
composition fact of §2.1 is not needed because the theorem is stated on
the CNF input; that `G ↦ indepCNF G` is polynomial-time is prose. The
crossover theorems use `pathwidth` only through `β n ≤ pathwidth G`; they
are inequalities about the exponents, which is what the proposition is.

### 6.5 The checks

`python -m learning.subexp_crossover` (119 s, `06_crossover/check_atlas7.log`,
`check.json`): on every graph of the atlas to 7 vertices (1,252), **129,761
evaluations, zero failures** —

| encoding | checked against | evaluations |
|---|---|---|
| `indep_cnf` | subset enumeration; width 2; `N = n`, `M = m` | 1,252 × 3 |
| `indep_atleast_cnf`, every `0 ≤ t ≤ n + 1` | `#{S : |S| ≥ t}`; `sat ↔ α ≥ t`; width 3 | 10,979 × 3 |
| `coloring_cnf`, `q = 2, 3` (4 to 6 vertices) | `q^n` enumeration; width; closed-form sizes | 2,712 × 3 |
| `domset_cnf`, direct and Tseitin | subset enumeration; width `Δ + 1` / 3 and `N ≤ n + 2m + 1` | 1,252 × 4 |
| `domset_atmost_cnf`, every `t` | `sat ↔ γ ≤ t` | 9,727 |
| `maxcut_cnf`, every `0 ≤ t ≤ m + 1` | `#{sides : cut ≥ t}`; `sat ↔ maxcut ≥ t`; width 3 | 14,846 × 3 |
| `oct_cnf`, every `t` | `sat ↔ oct ≤ t` (bipartiteness after deletion); width 4 | 9,727 × 2 |
| `hamcycle_cutcount_cnf` | `#F ≡ #HC (mod 2)` (cycles by permutations); width 3; `N ≤ 20 (n + m) + 1` | 1,249 × 3 |
| the same, `m ≤ 15` | `#F = Σ_X 2^{cc(X) − 1}` by two-factor enumeration | 1,209 |
| weighted decision, one random weight vector | sound (yes ⇒ a cycle exists); complete on 435 of 443 | 1,249 |

plus the threshold circuit's auxiliaries per input to `n = 200` (`≤ 6.98`,
width 3), the size constants (variables over `n + m`: 1.0, 6.6, 3.0, 1.75,
5.9, 16.5 for the six measured encodings) and the crossover table.
`tests/test_subexp_crossover.py`: 10 tests, including `C₅` by hand (11
independent sets, 30 proper 3-colourings, one Hamiltonian cycle) and `K₄`
(three).

One refuter subagent (the only one used, 1 of 4) read the Lean file and
the encodings blind to this section with its own brute force to 6
vertices; its report is `06_crossover/refuter.md` and its findings are
folded in below (§6.7).

### 6.6 What this does not claim

- That `SubexpCount k` holds for any `k`; every algorithm here is
  `SubexpCount k → …` (Lean) or "under the counting theorem" (prose), and
  the paper-form times quote the paper.
- That any SETH-tight lower bound is *refuted*: §6.0. "Void" means the
  SETH derivation is void; the statements stand open and follow from the
  unrestricted-CNF-SAT hypothesis by the paper's own §1.1.3.
- That the crossover says anything at a specific `n`: the constants `A`
  (verified) and the paper's `O_k`, `O_{k,D}` are unknown; the table is at
  constant 1 and is an illustration of the shapes.
- That the Hamiltonian-cycle *decision* (and the other Cut & Count
  problems) is a theorem of the paper: it rests on the Section 3.1 remark
  about `Q`-algebra-valued factors (§6.2.7) and is randomized; the tensor
  form's `ℓ ≤ Cs` does not accommodate the isolation weights. The parity
  is unconditional on the hypothesis.
- That the three source papers were read: none is held; the problems, the
  bases and the lower bounds are quoted from abstracts and from the ETH
  paper's §1.1.3, and item 11 records them as missing. Partition into
  triangles and the four Cut & Count problems other than Hamiltonian cycle
  are listed and neither encoded nor checked.
- That the Lean file formalises maximum independent set: it formalises
  the *counts* of independent sets and of proper `q`-colourings (Corollary
  1.3's statements) and the crossover inequality; the threshold circuit of
  §6.2.2 is proved on paper and checked by brute force; the dynamic program
  is not modelled (the crossover compares exponents, not machines).
- That the crossover table measures anything: both columns are at constant
  1, in the variable count, and the fixed-density paper bound.
- That the machine composition fact of §2.1 holds; it is not used, because
  `indepCount_subexp` is stated on the CNF input.
- Any pathwidth was computed: nothing here runs on an instance; the far-side
  classes are named by proved or recorded bounds.

### 6.7 Refuter findings

One refuter subagent (1 of 4) read `Crossover.lean` (before the colouring
theorems were added) and `subexp_crossover.py` blind to this section, with
its own enumerators to 6 vertices (209 graphs; 88,744 fixed-input extension
checks of the threshold circuit; 615 weighted Cut & Count trials): zero
disagreements with any count, decision or parity. It found **two wrong
sentences and two gaps, no wrong theorem and no wrong verdict**, all folded
in above: (1) the odd-cycle-transversal count is `Σ_D 2^{|D|} 2^{cc(G − D)}`,
not `Σ_D 2^{cc(G − D)}` (`P₃` at `t = 1`: 18 models against 10 claimed; the
decision was right); (2) `ρ(n)/n` at constant 1 is below 1 for `n ≤ 49`, peaks
at `16/e² ≈ 2.17` near `n ≈ 10^{23.7}` and crosses 1 at `n ≈ e^{5,504}`, not
"above 1 until `e^{5,600}`"; (3) the crossover table is in the variable
count, so at constant 1 the threshold, Max-Cut and Hamiltonian-cycle
encodings have no crossover at any `n ≤ 10⁶` (the paragraph and table now in
§6.3); (4) the paper column is the fixed-density bound. It confirmed that
`indepCount_subexp` says what its docstring says (`#check` on the built
`olean`, `n` the vertex count), that the framing of §6.0 is right with the
qualification that the lower bounds' *premise* is gone while their
conclusions stand on the unrestricted-CNF-SAT hypothesis, and that the
Hamiltonian-cycle decision rests on one remark of the paper and is uncovered
by Lean (as §6.2.7 and §6.6 say). Its editorial points (the stale README
numbers, a docstring naming a constant that does not exist, `L = Θ(mn)`
from the unary code) are applied. Report: `06_crossover/refuter.md`.

### 6.8 Regenerate

    cd ~/dev/MOSP
    D=reports/scratch/subexp_pathwidth/06_crossover
    nice -n 19 python3 -m learning.subexp_crossover --nmax 7 --out $D > $D/check_atlas7.log
    python3 -m learning.subexp_crossover --table
    python3 -m pytest tests/test_subexp_crossover.py -q
    cd lean && lake build && lake env lean ../$D/axiom_check.lean | tee ../$D/axiom_check.log
    python3 Ralph_Loops/loop0014/gate.py
