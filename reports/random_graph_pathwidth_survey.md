# Pathwidth (and treewidth) of random graphs: what is known

*Literature survey, 2026-10-17. Reading only: no solver run. The only computation
was evaluating the closed-form bounds in §1.4 and the table in §7(a) on a grid of
`c` (a root-finding script, seconds).*

This complements `paper2/survey_random_extremal.md` (rows R1–R19, B7, M1), which
already covers Gao's random-intersection result, Perarnau–Serra, Do–Erde–Kang,
Mitsche–Perarnau and Kolesnik–Wormald from the MOSP side. This report is aimed at
one decision: **is measuring exact `pw(G(n, c/n))/n` against `c` for `n ≤ 60–100`
aimed at an open question?** Short answer: yes. No sharp constant, no limit
theorem and no exact-pathwidth measurement of `G(n, c/n)` exists in what we found.
But a measurement at `n ≤ 100` can only inform finite-size questions and test
bounds. It cannot settle an asymptotic one (§7(b)).

Labels used throughout:
- **[pub]**: a published statement, read in the source (page or theorem given).
- **[pub, abstract]**: read only in the abstract or metadata.
- **[derived]**: our own short derivation from published facts, written out here
  because we could not find it published. Check it before quoting.
- **UNVERIFIED**: could not be confirmed against a source.

Notation: `G(n,p)`, with `p = c/n` in the sparse case. `pw ≥ tw`, `pw = vs`
(Kinnersley 1992), and `pw ≤ td − 1`. Adding one edge raises `pw` by at most 1.
Removing a vertex lowers `pw` by at most 1.

---

## 1. Sparse Erdős–Rényi `G(n, c/n)`

### 1.1 The linear-width threshold (treewidth, hence pathwidth)

| year | result | parameter | statement |
|---|---|---|---|
| 1994 | **Kloks**, *Treewidth: Computations and Approximations*, LNCS 842, Springer (DOI 10.1007/BFb0045375, from memory, not resolved) | tw | whp `tw ≥ r(d)·n` for `p = d/n`, `d ≥ 2.36` (that is, `m/n > 1.18` in `G(n,m)`), with `r(d) → 1` as `d → ∞`. First moment over balanced partitions. [pub, as restated by Do–Erde–Kang p. 1, Gao p. 6 and Perarnau–Serra p. 9] |
| 2006 | **Gao**, "On the threshold of having a linear treewidth in random graphs", COCOON 2006, LNCS 4112, 226–234, DOI 10.1007/11809678_25 | tw | threshold improved to `d > 2.16` (2.162 in Perarnau–Serra and Lee–Lee–Oum). Gao asks whether `d > 1` suffices. [pub, as restated] |
| 2012 | **Gao**, "Treewidth of Erdős–Rényi random graphs, random intersection graphs, and scale-free random graphs", *Discrete Appl. Math.* 160(4–5):566–578, DOI 10.1016/j.dam.2011.10.013, arXiv 0907.5481 | tw | Thm 1: `G(n,m)` with `m/n ≥ 1.073` (`c ≥ 2.146`) gives `tw > βn` whp for some `β > 0`. He notes that a refined Kloks computation alone gives 1.083. [pub, arXiv p. 2] |
| 2012 | **Lee, Lee & Oum**, "Rank-width of random graphs", *J. Graph Theory* 70(3):339–347, DOI 10.1002/jgt.20620, arXiv 1001.0461 | rank-width, so tw | Thm 1.1(iii): `c > 1` gives `rw ≥ r(c)·n` whp. Cor 1.2: `c > 1` gives rw, clique-width, tw `≥ c′n`, and `c < 1` gives `rw, tw ≤ 2`. **The threshold for linear treewidth is sharp at `c = 1`.** Uses `rw ≤ tw + 1` (Oum 2008) and the expander inside the giant (Benjamini–Kozma–Wormald). [pub, arXiv p. 2] |
| 2014 | **Perarnau & Serra**, "On the tree-depth of random graphs", *Discrete Appl. Math.* 168:119–126, DOI 10.1016/j.dam.2012.10.031, arXiv 1104.2132 | td, tw | A direct proof of linear tw for `c > 1`, with `r′(d) ≥ (αδ)²/(9e³d²)`, where `α, δ` are the implicit expander constants. **Explicit:** `tw(G(n,c/n)) ≥ (1 − f(c))·n` whp for any `f(c) > √(9 ln 3/(2c))`, valid for `c > 9 ln 3/2 ≈ 4.94` (p. 5–6). Cor 4.6: random `d`-regular graphs, `d ≥ 3`, have linear tw and td. [pub] |
| 2024 | **Do, Erde & Kang**, "A note on the width of sparse random graphs", *J. Graph Theory* 106:273–295, DOI 10.1002/jgt.23081, arXiv 2202.06087 (CC BY) | tw, rw | `p = (1+ε)/n` with `ε` a small constant: `tw = Ω(ε³ n / log(1/ε))` (Thm 1.5) and `rw = Ω(ε³ n / log³(1/ε))` (Thm 1.4). Weakly supercritical, `ε = o(1)` with `ε³n → ∞`: `tw, rw = Θ(ε³ n)` (Thm 1.6), and explicitly **`0.02 ≤ tw/(ε³n), rw/(ε³n) ≤ 1.34`** (§5, p. 14). [pub] |
| 2011 | **Wang, Liu, Cui & Xu**, "A note on treewidth in random graphs", COCOA 2011, LNCS 6831, 491–499, DOI 10.1007/978-3-642-22616-8_38 | tw | `p = c/n` gives `tw ≤ t·n` whp for some `t = t(c) < 1`, refuting a conjecture that `tw = n − o(n)` there. `p ≫ 1/n` gives `tw ≥ n − o(n)`. [pub, abstract] |
| 2009 | **Mareček**, "Some probabilistic results on width measures of graphs", arXiv 0908.1772 (workshop GROW 2009) | tw, bw, cw, NLC, rw | `Ω(n)` lower bounds on random graphs, as a caution for FPT on random inputs. [pub, abstract] |

**Consequence for pathwidth [derived, immediate].** `pw ≥ tw` gives `pw = Θ(n)`
whp for every `c > 1`. For `c < 1`, `pw ≤ td − 1 = O(log log n)` (§2). So
**pathwidth also has its linear threshold exactly at `c = 1`**. No source states
this for pathwidth, but it is a one-line corollary of Lee–Lee–Oum and
Perarnau–Serra.

### 1.2 Is a sharp constant known?

**No.** We found no `c` with a known limit or even a known leading constant for
`tw/n` or `pw/n`. The closest things are these:
- Do–Erde–Kang **Question 5.2** (open): in the weakly supercritical window, is
  `tw = (1+o(1)) c_t ε³n`, and what is `c_t`? Known: `0.02 ≤ c_t ≤ 1.34`.
- Do–Erde–Kang **Question 5.1** (open): for constant small `ε`, is
  `tw ≥ c ε³ n` with `c` independent of `ε`?
- The analogous geometric question is also open: Li & Müller's Conjecture 5.3,
  `tw(G(n,r)) = (c(r)+o(1))√n` (§4).

### 1.3 Does the limit `lim pw/n` exist?

**Not known, as far as we found.** Concentration is easy: `pw` and `tw` are
1-Lipschitz under vertex exposure, so Azuma gives `|pw − E pw| = O(√n)` whp.
Do–Erde–Kang note this for tw and rw "for large enough ε" (§5, p. 14), and say
that for small ε it is unclear whether concentration holds at scale `o(ε³n)`.
Whether `E[pw]/n` converges is a different matter. The standard tool for that,
the combinatorial interpolation method of **Bayati, Gamarnik & Tetali (2013)**,
*Ann. Probab.* 41(6):4080–4115, DOI 10.1214/12-AOP816, arXiv 0912.2444, proves
limits for independent set, MAX-CUT, coloring and K-SAT on `G(N, ⌊cN⌋)` and
random regular graphs. It does **not** treat treewidth or pathwidth, and no later
paper we found does. Its super/subadditivity argument relies on objectives that
are additive over local constraints. Width parameters are global min–max
quantities, so the extension is not routine. Related limit results for cut-type
min–max objectives exist only for large `c`: Dembo, Montanari & Sen,
"Extremal cuts of sparse random graphs", *Ann. Probab.* 45(2):1190–1217 (2017),
DOI 10.1214/15-AOP1084, arXiv 1503.03923 (min/max bisection, `c → ∞`).
Gamarnik, "Right-convergence of sparse random graphs", *PTRF* 160:253–278
(2014), arXiv 1202.3123, concerns partition functions, not widths.

### 1.4 Explicit bounds on `pw/n` as functions of `c`

The published explicit bounds are few: Perarnau–Serra's `1 − √(4.944/c)` for tw,
and Do–Erde–Kang's 0.02 and 1.34 in the window. Since none of the published
lower bounds is stated for `pw` directly, here are the bounds one gets by
elementary means. All are **[derived]** unless marked.

**Lower bound, first moment for vertex separation [derived].** Suppose
`vs(G) ≤ k`. Let `a(i)` be the number of prefix vertices with no neighbour in the
suffix at position `i`. It is nondecreasing, and `a(i) ≥ i − k`. At the last `i`
with `a(i) ≤ n − i`, and the next position, one finds disjoint `A, R` with
`|A| = |R| ≥ ⌈(n−k)/2⌉ − 1` and no `A–R` edge. With `a = (1−β)/2`, the expected
number of such pairs in `G(n, c/n)` is `exp(n[H(a, a, 1−2a) − c a²] + o(n))`,
where `H` is the natural-log trinomial entropy. Hence **whp `pw ≥ β*(c)·n`**,
where `β*` is the largest `β` with `H(a,a,1−2a) < c a²` on `[0, β)`. This is
positive iff `c > 4 ln 2 ≈ 2.77`, and it beats Perarnau–Serra's treewidth bound
at every `c` (table §7(a)), because no 1/3–2/3 balancing slack is needed for
layouts. As `c → ∞`, `1 − β* ~ 4 ln c / c`. It is the same method as
Kloks / Perarnau–Serra / Díaz–Petit–Serna–Trevisan. The last of these
(*Discrete Math.* 235:245–253 (2001), DOI 10.1016/S0012-365X(00)00278-8,
Lemma 3 (g5)) proves `VS ≥ (1/2 − ε)n − 1` on mixing graphs, which holds for
`c ≥ 3(1+ln 3)(εγ)^{-2}`. Their own argument gives `(1 − 2ε)n` if the prefix
position `(1−ε)n` is used instead of `n/2`. [pub for the lemma; the improvement
is derived]

*Deterministic core checked by brute force, 2026-10-30
(`reports/scratch/empty_pair/check.py`, per the todo's "check before Lean").*
In checkable form: with `s*(G) = max_A min(|A| − 1, n − |N[A]|)` (a set `A`
with at least `s* + 1` vertices and at least `s*` vertices outside its closed
neighbourhood), **`pw(G) ≥ n − 2 s*(G) − 2`** for every graph on ≤ 9 vertices,
all 288,266 of them, zero violations; tight on 22.5% at `n = 9`. The weaker
rounding stated above (`|A| = |R| ≥ ⌈(n−k)/2⌉ − 1`, i.e. with
`min(|A|, n − |N[A]|)`) also holds everywhere and is never tight: its slack is
at least 1 on every graph to 9 vertices, so `pw ≥ n − 2 s′ − 1` is what the
data suggest for that form (unproved; the sharp form above is the one to
formalise). Pathwidth by a vertex-separation subset DP cross-checked against
`fixed_parameter_algorithm.pathwidth` on every graph to 7 vertices. The other two
deterministic cores of this report were checked the same way
(`check23.py`): §2's tree bound `pw ≤ ⌊log₃(2N+1)⌋` on every tree to 16
vertices (32,547 trees, zero violations, tight for N = 7–12, where the
largest pathwidth is 2) and `pw = h` for the complete ternary trees of height
1, 2, 3 (4, 13 and 40 vertices, the C program with refutations); §3's
`pw ≤ n − α(G)` on every graph to 9 vertices, zero violations, tight on 6.5%
at n = 9.

**Upper bounds** (any graph, applied to `G(n,c/n)`):
- **Cyclomatic number** [derived]: `pw ≤ pw(spanning forest) + (m − n + #components)`.
  The forest term is `O(log n)`. Whp `m − n + κ = n[c/2 − 1 + (x − x²/2)/c] + o(n)`,
  where `x < 1` solves `x e^{−x} = c e^{−c}` (standard component count). This is
  best for `1 < c ≲ 2.2` and tends to 0 as `c ↓ 1`, consistent with Do–Erde–Kang's
  `Θ(ε³n)`.
- **Kneis, Mölle, Richter & Rossmanith (2009)**, "A bound on the pathwidth of
  sparse graphs with applications to exact algorithms", *SIAM J. Discrete Math.*
  23(1):407–427, DOI 10.1137/080715482: **`pw ≤ m/5.769 + O(log n)`** for every
  graph [pub, abstract]. On `G(n,c/n)` this is `pw/n ≤ c/11.54 + o(1)`, best for
  `2.2 ≲ c ≲ 8`. Edwards & McDermid (2015, *Algorithmica* 72(4):940–968,
  DOI 10.1007/s00453-014-9883-7) give a degree-sequence bound that matches
  Fomin et al. up to degree 6 and is smaller beyond. Its closed form was not
  read (UNVERIFIED).
- **Fomin, Gaspers, Saurabh & Stepanov**, "On two techniques of combining
  branching and treewidth", *Algorithmica* 54:181–207 (2009),
  DOI 10.1007/s00453-007-9133-3: `pw ≤ n₃/6 + n₄/3 + 13n₅/30 + n_{≥6} + εn`
  [pub, as quoted in search results; coefficient list not read in the PDF].
- **Independence number** [derived, standard]: bags `(V∖I) ∪ {v}`, `v ∈ I`, give
  `pw ≤ n − α(G)`. Random greedy gives `α ≥ (ln(1+c)/c)·n` whp, so
  `pw/n ≤ 1 − ln(1+c)/c`. (The greedy constant is a classical result; its
  reference was not re-checked.) As `c → ∞`, `α ≈ 2n ln c / c` (Frieze 1990),
  so `1 − pw/n ≥ (2 − o(1)) ln c / c`.

So for large `c`: **`1 − pw/n ∈ [(2 − o(1)) ln c/c, (4 + o(1)) ln c/c]`**
[derived], the order of `n − pw` is `Θ(n log c / c)`, and the constant in front
(between 2 and 4) is open.

---

## 2. Subcritical `c < 1` and the critical window

- **[pub]** `tw ≤ 2` whp for `c < 1` (trees and unicyclic components; Lee–Lee–Oum Cor 1.2).
- **[pub]** Tree-depth (Perarnau–Serra Thm 1.2): `td = Θ(log log n)` for `c < 1`,
  `Θ(log n)` at `c = 1`, `Θ(n)` for `c > 1`. Hence `pw = O(log log n)` and
  `O(log n)`. `paper2/survey_random_extremal.md` R6 records this.
- **[pub]** Critical window (`p = (1 + λn^{-1/3})/n`): `tw = O(1)` and every
  width parameter bounded by a function of tw is `O(1)` (Perarnau–Serra §4.2,
  Do–Erde–Kang p. 2). **Pathwidth is not such a parameter.** Tree pathwidth is
  unbounded.
- **[derived] Subcritical pathwidth is `(1 + o(1)) log₃ log n`.**
  - *Upper bound:* components have at most `(1+o(1)) ln n/(c − 1 − ln c)` vertices
    and are trees or unicyclic. A tree on `N` vertices has `pw ≤ log₃(2N+1)`
    (Scheffler; classical, UNVERIFIED reference), and a unicyclic graph adds 1.
  - *Lower bound:* a fixed tree `T` on `k` vertices appears as a component with
    expectation `≈ n c^{k−1} e^{−ck}/|Aut T|`. This tends to infinity for the
    complete ternary tree with `k = Θ(log n)` vertices, so a whp copy follows by
    second moment. That tree has pathwidth equal to its height,
    `≈ log₃ k = log₃ log n − O(1)`.
  - So in the subcritical phase `pw → ∞` while `tw ≤ 2`, and `pw − tw` is
    unbounded. **Not found published.**
- **[derived] Critical point `c = 1`:** `pw ≤ (2/3) log₃ n + O(1)`, since the
  components have size `O(n^{2/3})` and bounded excess. `pw → ∞`, since every
  fixed tree occurs. The true order (presumably `Θ(log n)`, from the random-tree
  question in §4) is **not known to us**.
- **Weakly supercritical** `ε³n → ∞`: `tw = Θ(ε³n)` [pub, DEK Thm 1.6]. By the
  cyclomatic bound, `pw ≤ (2/3 + o(1)) ε³n + O(log n)` [derived], so
  `pw = Θ(ε³n)` once `ε³n ≫ log n`.

---

## 3. Dense `G(n, p)`, `p` constant

- **[pub]** Perarnau–Serra Thm 1.1: `td(G) = n − O(√(n/p))` for `p ≫ 1/n`, and the
  proof gives the same for tw. So `pw = n − O(√(n/p))`. They write "to our
  knowledge, the tree-width of a dense random graph has not been studied before".
- **[pub, abstract]** Wang–Liu–Cui–Xu (2011): `tw ≥ n − o(n)` for `p ≫ 1/n`.
- **[pub]** Lee–Lee–Oum: `rw = ⌈n/3⌉ − O(1)` for constant `p` (rank-width, not tw).
- **[derived] Sharper, by the same first moment as §1.4:** an empty pair of sizes
  `a, a` has expectation `≤ n^{2a}(1−p)^{a²}`, which vanishes for
  `a > (2+o(1)) log_b n` with `b = 1/(1−p)`. With `pw ≤ n − α` and
  `α = (2+o(1)) log_b n`, this gives
  **`(2 − o(1)) log_b n ≤ n − pw ≤ (4 + o(1)) log_b n`**. For treewidth, the
  balanced-separator version gives `(2 − o(1)) log_b n ≤ n − tw ≤ (6 + o(1)) log_b n`.
  So `n − pw = Θ(log n)`, much tighter than the published `O(√n)`. We did not find
  this stated anywhere. The exact constant (between 2 and 4 for pw) looks open.
  **Check before quoting.**
- For comparison, tree-depth: `n − td = O(√(n/p))` [pub].

---

## 4. Other random models

**Random `d`-regular graphs.**
- [pub] Linear tw and td for every fixed `d ≥ 3` (Perarnau–Serra Cor 4.6, via Kahn–Szemerédi spectral gap).
- [pub] Kolesnik & Wormald, "Lower bounds for the isoperimetric numbers of random
  regular graphs", *SIAM J. Discrete Math.* 28(1):553–575 (2014),
  DOI 10.1137/120891265, arXiv 1311.6555: vertex bisection
  `≥ A_d·(n/2)` with `A_3 = 0.14420`, `A_4 = 0.28966`, …, `A_10 = 0.71371`
  (table reproduced in Díaz, Diner, Serna & Serra 2022, arXiv 2211.03206, Table 2).
  Since `vs ≥ vertex bisection` (the layout prefix at `n/2`), **`pw(G_{n,3}) ≥ 0.0721n`,
  `pw(G_{n,4}) ≥ 0.1448n`, …, `pw(G_{n,10}) ≥ 0.3569n` whp** [derived from pub].
- [pub] Upper bounds: Fomin & Høie (2006), "Pathwidth of cubic graphs and exact
  algorithms", *IPL* 97:191–196, DOI 10.1016/j.ipl.2005.10.012: `pw ≤ n/6 + o(n)`
  for every cubic graph. FGSS above gives `n/3` at `d = 4`.
- For random cubic graphs the whp window is therefore **`0.0721n ≤ pw ≤ 0.1667n`**.
  Fomin–Høie call narrowing the worst-case gap (0.082n to 0.167n) "an interesting
  challenge" (recorded in `paper2/survey_random_extremal.md` B2).
- Edge bisection, for context: `0.103295n ≤ bw(G_{n,3}) ≤ 0.139822n` (Lichev &
  Mitsche, *Electron. J. Combin.* 30 (2023), arXiv 2009.00598).

**Random geometric graphs** `G(n, r)` in `[0, √n]²`.
- [pub] Mitsche & Perarnau, "On treewidth and related parameters of random
  geometric graphs", *SIAM J. Discrete Math.* 31(2):1328–1354 (2017),
  DOI 10.1137/120874448 (STACS 2012): `tw = Θ(log n / log log n)` for constant
  `r < r_c`, and `tw = Θ(r√n)` for `r ≥ c` with `c` large. **The same orders hold
  for pathwidth and tree-depth** (abstract). They conjectured `Θ(r√n)` for all `r > r_c`.
- [pub] Li & Müller, "On the treewidth of random geometric graphs and percolated
  grids", *Adv. Appl. Probab.* 49(1) (2017), DOI 10.1017/apr.2016.78: proves that
  conjecture. The percolated `k × k` grid has `tw = Θ(k)` for `p > 1/2` and
  `Θ(√log k)` for `p < 1/2`. **Open:** Question 5.2, is `tw = (1+o(1)) log n/log log n`,
  even `tw = ω`, subcritically? Conjecture 5.3, a sharp constant `tw = (c(r)+o(1))√n`.
  Conjectures 5.4–5.5, critical exponents `n^{91/192}` and `k^{91/96}`.
- [pub] Layout parameters (vertex separation `Θ(nr)`, bandwidth, cutwidth) on RGGs:
  Díaz, Penrose, Petit & Serna, *CPC* 9:489–511 (2000), DOI 10.1017/S0963548300004454,
  and *J. Algorithms* 39:78–117 (2001), DOI 10.1006/jagm.2000.1149. Penrose,
  *Ann. Appl. Probab.* 10:517 (2000), DOI 10.1214/aoap/1019487353. These carry
  constants as limits in the dense-RGG regime. Detail is in the survey R11
  (read via Díaz–Petit–Serna 2002 only).

**Random trees.**
- No theorem stated directly for pathwidth was found (as the survey's B7 also records).
- [derived] Esparza, Luttenberger & Schlund, "A brief history of Strahler numbers",
  LATA 2014, LNCS 8370:1–13, DOI 10.1007/978-3-319-04921-2_1, state
  `pw(t) − 1 ≤ st(t) ≤ 2·pw(t)` for undirected trees (as quoted by Ganardi &
  Lohrey, arXiv 2512.19060, p. 30; the original was not read).
  Flajolet, Raoult & Vuillemin (1979), *TCS* 9:99–125,
  DOI 10.1016/0304-3975(79)90009-4 [pub, abstract read in the PDF held in
  `literature/`], give the mean register function (Strahler) of uniform binary
  trees with `n` nodes as `log₄ n + D(log₄ n) + o(1)`, with `D` periodic.
  Devroye & Kruszewski (1995), *IPL* 56(2):95–99, DOI 10.1016/0020-0190(95)00114-R,
  is the concentration companion (content UNVERIFIED).
  So **`pw(uniform random binary tree) = Θ(log n)` whp, between about
  `(1/2) log₄ n` and `log₄ n + O(1)`**. The constant is open, and for uniform
  labelled (Cayley) trees nothing was found.

**Random planar graphs.** Nothing found. Only the deterministic `O(√n)` bound
(Lipton–Tarjan) applies. Hyperbolic random graphs: Bläsius, Friedrich & Krohmer,
ESA 2016, DOI 10.4230/LIPIcs.ESA.2016.15: `tw = O(n^{(3−β)/2})`, `O(log² n)`,
`O(log n)` for `2 < β < 3`, `β = 3`, `β > 3` [pub, abstract].
Heterogeneous random graphs: Shang (2022), *Proc. Japan Acad. A* 98,
DOI 10.3792/pjaa.98.015 (tree-depth and tree-width; already in `literature/`).

**Random intersection graphs** (Karoński, Scheinerman & Singer-Cohen 1999,
*CPC* 8:131–159, DOI 10.1017/S0963548398003459; vertex set = customers, each
customer takes each of `m` items with probability `p`. This is the Bernoulli
random MOSP matrix).
- [pub] Gao (2012) Thm 2: `m = n^α`, any `α > 0`, `p = c/m` with `c > 2` gives
  `tw > βn` whp. The proof is a crude first moment over balanced partitions, and
  `c > 2` is an artefact of it.
- [pub] Karoński & Szymkowiak (2001), "On a solution of a randomized three tracks
  variant of the Gate Matrix Layout problem", *Discrete Math.* 236:179–189,
  DOI 10.1016/S0012-365X(00)00441-6 (PDF in `literature/`, read):
  - Thm 1 gives the threshold for the random `n × m` Boolean matrix
    `R(n, m, p)`, `m = n^α`, to be a "yes" instance of **3-GML** (MOSP optimum ≤ 3,
    i.e. `pw ≤ 2` of the RIG). The threshold is `p₃* = m^{−1/4} n^{−1}` for
    `α ≤ 40/21` and `m^{−1/2} n^{−11/21}` for `α ≥ 40/21`.
  - Proof: Kinnersley–Langston's 110 obstructions plus subgraph thresholds.
  - §5 conjectures `p_k*` for every fixed `k` via the largest tree obstructions,
    `t_k = (5·3^{k−1} − 1)/2` vertices.
  - This is the **fixed-`k` regime only**.
- [pub, abstract] KSS (1999) "present an application to gate matrix circuit
  design". Its content was not read (UNVERIFIED).
- Rybarczyk (2011), *RSA* 38: for `m ≥ n³` and monotone properties, `G(n,m,p)`
  is equivalent to `G(n, p̂)` (survey R17). This does not reach `m = Θ(n)`.

---

## 5. Experimental and computational studies

| study | what was measured on random graphs | exact? |
|---|---|---|
| **Gogate & Dechter (2004)**, "A complete anytime algorithm for treewidth", UAI 2004, 201–208, arXiv 1207.4109 (in `literature/`) | Table 1: mean exact tw over 100 `G(n, m)` graphs. `n=25`: m=50/100/150/200 give tw 6.3/11.8/15.1/18 (`c = 4/8/12/16`). `n=50`: m=50/100/150/200/300/400 give 3.6/10.8/17.3/20.34/27.6/33.7 (`c = 2/4/6/8/12/16`). Min-fill is within 2 of the optimum on average. **"Graphs of small (close to 1) and large (close to n) treewidth are easy … intermediate treewidths are harder."** | exact tw (QuickBB) |
| Dow & Korf (2007), "Best-first search for treewidth", AAAI 2007 (saved: `literature/2007-Dow-Korf-Best-First-Search-Treewidth-AAAI.pdf`) | 900 `G(V,E)` graphs, `(V,E) ∈ {25,30,35} × {2V,4V,8V}`. Reports run times only, no width values. | exact tw, values not reported |
| Shoikhet & Geiger (1997), "A practical algorithm for finding optimal triangulations", AAAI 1997 | random graphs as benchmarks (cited by Gogate–Dechter) | exact tw (content not read) |
| Bodlaender & Koster, "Treewidth computations I. Upper bounds", *Inf. Comput.* 208:259–275 (2010), DOI 10.1016/j.ic.2009.03.008; "II. Lower bounds", *Inf. Comput.* 209:1103–1119 (2011), DOI 10.1016/j.ic.2011.04.003 | surveys of heuristics and bounds on benchmark sets. Whether they tabulate `G(n,p)` was not checked. | heuristic |
| Coudert, Mazauric & Nisse, *ACM JEA* 21 (2016), DOI 10.1145/2851494 (in `literature/`) | random **digraphs** `G(N, M)`, `N ≤ 50`, 1,000 per density: run times only (Fig. 2). Exact undirected pw for graphs under 60 nodes is claimed in reasonable time. | exact directed pw, values not reported |
| Kobayashi, Komuro & Tamaki (2014), SEA, DOI 10.1007/978-3-319-07959-2_33 | pathwidth on TreewidthLIB, no random-graph study | exact pw |
| Díaz, Diner, Serna & Serra (2022), arXiv 2211.03206 | heuristic vertex bisection of random regular graphs, `n` from 10⁵ to 6·10⁵ (an upper bound for VB, not for pw) | heuristic |
| Gao (2005), PhD thesis, U. Alberta, "Phase transitions and typical-case complexity", DOI 10.7939/r3-bvfe-3v82 | treewidth thresholds in random CSP context (not read) | — |
| Tensor-network contraction (Markov & Shi 2008, *SICOMP* 38:963; Gray & Kourtis 2021, *Quantum* 5:410) | contraction width (a tw upper bound) of random regular / circuit graphs, heuristic | heuristic |

**Statistical physics.** We found **no** cavity-method or replica prediction for
`tw/n` or `pw/n` of sparse random graphs. arXiv cond-mat searches for treewidth
return only tensor-network papers. This is a real gap: the cavity method predicts
`α`, MAX-CUT, matching and core sizes for `G(n,c/n)`, but apparently not widths.

**Hardness phase transition for computing treewidth.** The only statement found is
Gogate–Dechter's qualitative one above (intermediate width is hardest). The
project's own ridge (`reports/ml_nature.md` §11, §25, §36) is a quantitative
version for pathwidth decisions on random intersection graphs. We found nothing
comparable.

---

## 6. Related parameters

- **Tree-depth**: Perarnau–Serra (above). Dense: `n − O(√(n/p))`. Sparse:
  `Θ(log log n)`, `Θ(log n)`, `Θ(n)`.
- **Rank-width**: Lee–Lee–Oum, Do–Erde–Kang (above).
- **Vertex separation / node search** (= pw, resp. pw + 1): Díaz–Petit–Serna–Trevisan
  (2001) Thm 1. For `p_n = c_n/n` with `c_n ≥ C_{ε,γ} = 3(1+ln 3)(εγ)^{-2}`, *any*
  layout approximates VERTSEP, CUTWIDTH, BANDWIDTH, MINLA, EDGEBIS and VERTBIS
  within a constant w.o.p. (`GAP_VS ≤ (1/2 − ε)^{-1}`). Cheung & Girardet (2020),
  *Open J. Discrete Math.* 10(1) (2020), DOI 10.4236/ojdm.2020.101003, claim factor
  `→ 1` under sparsity conditions [pub, abstract; full text refused].
- **Trap**: "vertex-separating path systems in random graphs" (Lichev &
  Sanhueza-Matamala, *RSA* 2026, arXiv 2408.01816) is a **different** notion, a
  family of paths separating vertices. Search engines conflate it with vertex
  separation number. It has nothing to do with pathwidth.
- **Local treewidth**: Mehta & Reichman, APPROX/RANDOM 2022, arXiv 2204.07827.
  **Layers model**: Feige, Hermon & Reichman, *RSA* (2015), DOI 10.1002/rsa.20597.
  Neither concerns global pathwidth.

---

## 7. Summary for the proposed measurement

### (a) Bounds on `pw/n` (and `tw/n`) for `G(n, c/n)`, by `c`

LB is the best lower bound, UB the best upper bound, both whp as `n → ∞`, with
`o(1)` terms dropped. "PS" is Perarnau–Serra's tw bound `1 − √(9 ln 3/(2c))`, a
lower bound on pw too. "FM" is our pw first moment `β*(c)` (§1.4). UB is the
minimum of cyclomatic, Kneis `c/11.54` and `1 − ln(1+c)/c`. The empirical column
is Gogate–Dechter's exact **tw**/n (a lower estimate of pw/n) at finite `n`.

| `c` | status | LB on pw/n | source | UB on pw/n | source | G–D exact tw/n |
|---|---|---|---|---|---|---|
| < 1 | sublinear | `pw = (1+o(1)) log₃ log n` | derived; `O(log log n)` pub (td) | — | — | — |
| 1 | critical | `pw → ∞`, `≤ (2/3) log₃ n` | derived | — | — | — |
| `1+ε`, `ε → 0`, `ε³n → ∞` | `Θ(ε³n)` | `0.02 ε³` | DEK §5 (tw) | `≈ 0.67 ε³` (pw), `1.34 ε³` (tw, DEK) | derived / DEK | — |
| 1.1 | linear, constant unknown | `r(c) > 0`, implicit | LLO, PS, DEK | 0.0006 | cyclomatic | — |
| 1.5 | " | implicit | " | 0.037 | cyclomatic | — |
| 2 | " | implicit | " | 0.162 | cyclomatic | 0.072 (n=50) |
| 2.5 | " | implicit (Gao: linear for c > 2.146) | Gao 2012 | 0.217 | Kneis | — |
| 3 | " | 0.009 | FM | 0.260 | Kneis | — |
| 4 | " | 0.061 | FM | 0.347 | Kneis | 0.216 (n=50), 0.252 (n=25) |
| 5 | " | 0.118 | FM (PS: 0.006) | 0.433 | Kneis | — |
| 6 | " | 0.171 | FM (PS: 0.092) | 0.520 | Kneis | 0.346 (n=50) |
| 8 | " | 0.263 | FM (PS: 0.214) | 0.693 | Kneis | 0.407 (n=50), 0.472 (n=25) |
| 10 | " | 0.337 | FM (PS: 0.297) | 0.760 | `1 − α_greedy` | — |
| 12 | " | 0.397 | FM (PS: 0.358) | 0.786 | " | 0.552 (n=50), 0.604 (n=25) |
| 16 | " | 0.488 | FM (PS: 0.444) | 0.823 | " | 0.674 (n=50), 0.720 (n=25) |
| 20 | " | 0.554 | FM (PS: 0.503) | 0.848 | " | — |
| 50 | " | 0.761 | FM (PS: 0.686) | 0.921 | " | — |
| 100 | " | 0.857 | FM (PS: 0.778) | 0.954 | " | — |
| `c → ∞` | | `1 − (4+o(1)) ln c/c` | FM | `1 − (2−o(1)) ln c/c` | `α` (Frieze) | — |
| `p` const. | | `n − (4+o(1)) log_b n` | derived (pub: `n − O(√(n/p))`, PS) | `n − (2−o(1)) log_b n` | `n − α` | — |

No sharp constant is known at any `c`. Between `c = 1` and `c ≈ 2.8` there is
**no explicit numerical lower bound at all**, only existence of `r(c) > 0`. The
upper/lower gap is a factor of 2–40 throughout the interesting range `2 ≤ c ≤ 10`.
Gogate–Dechter's finite-`n` treewidths sit inside every interval, and they fall
with `n` (`c = 8`: 0.472 at `n = 25`, 0.407 at `n = 50`), which shows how large
the finite-size effects are at these sizes.

### (b) What exact `pw` at `n ≤ 100` can and cannot inform

**Can inform (genuinely open, and a measurement would be new):**
1. **The first exact-pathwidth curve `E[pw]/n` against `c` for `G(n,c/n)`.** None
   exists. Gogate–Dechter (2004) is the only exact *treewidth* table, at
   `n ≤ 50`, eight cells, means only.
2. **Finite-`n` location of the onset near `c = 1`**, and whether the data follow
   the `ε³n` law of DEK Thm 1.6 for moderate `ε`. A fitted `c_t` would be an
   empirical guess at DEK Question 5.2's constant. At `n = 100`, though,
   `ε³n ≥ 10` needs `ε ≥ 0.46`, so the window is barely resolvable.
3. **Concentration and variance**: whether `Var(pw)` grows like `n` (Azuma scale)
   or stays `O(1)`, as the project already saw for random intersection graphs
   (`reports/ml_nature.md` §12). Nothing is published on the variance.
4. **`pw − tw` on random graphs**: unbounded subcritically (§2, derived), size
   unknown in the linear regime. With exact tw available (`learning/treewidth.py`)
   this is cheap and new.
5. **Which upper-bound mechanism is closest**, cyclomatic or Kneis or `n − α`, and
   a test of the derived first-moment lower bound `β*(c)` against data. If
   measured values fall below `β*(c)` at large `n`, either the derivation is
   wrong or finite-size effects dominate. This is a useful check on §1.4.
6. **Random intersection graph versus `G(n, p̂)` at equal edge density**, at
   `m = Θ(n)`, the regime no equivalence theorem covers (Rybarczyk needs `m ≥ n³`).

**Cannot inform:**
- the existence of `lim pw/n`, or its value at any `c` (finite `n` never decides a limit);
- the sharp threshold or asymptotic order in the critical window (`ε³n` too small at `n ≤ 100`);
- the constant in `n − pw = Θ(log n)` (dense) or in `Θ(ln c / c)` (large `c`), where
  `log n ≤ 4.6` and the effect is a few vertices;
- subcritical `log₃ log n` behaviour (`log₃ log 100 ≈ 1.4`: pw will look constant).
- Finite-size corrections are visibly large: Gogate–Dechter's tw/n drops by 0.04–0.07
  from `n = 25` to `n = 50` at fixed `c`. Any "estimate of the limit" from
  `n ≤ 100` needs an explicit extrapolation model, and the project's own
  §14 lesson (constants calibrated at `n ≤ 40` failed at 125) applies here.

### (c) Has anyone measured exact pathwidth of random intersection graphs?

**Not as such.**
- No paper found computes or tabulates the exact pathwidth of `G_I(n, m, p)` or
  studies it against density. The theory is Gao's `Θ(n)` existence (`c > 2`) and
  Karoński–Szymkowiak's fixed-`k ≤ 3` thresholds (with a conjecture for fixed `k`).
- Implicitly, yes. Every certified MOSP optimum of a randomly generated instance
  is `pw + 1` of a random clique-cover graph. That includes the Chu & Stuckey
  (2009) random classes and the Faggioli–Bentivoglio instances.
  - The MOSP literature never framed these as pathwidths, and never studied them
    as a function of density, item count or `n`.
  - Chu & Stuckey's generator is not the KSS Bernoulli model: it fixes customers
    per product and discards decomposable instances (CLAUDE.md, `reports/ml_nature.md` §2).
- The project's ~44,547 certified instances (`reports/ml_nature.md` §9–§16, §25)
  appear to be the only systematic exact-pathwidth data set on random intersection
  graphs, and on random graphs of any kind, that we could find.

### (d) The pilot measurement (2026-10-18; added 2026-10-26)

*The one computation in this report. The survey above was written before it.*

`reports/scratch/gnp_pilot/pilot.py` drew `G(n, c/n)` for `c ∈ {0.5, 1, 1.5,
2, 3, 4, 6, 8, 10}` and `n ∈ {20, …, 60, 70, …, 120}`, seeds recorded, and sent
each graph to the C program (`pathwidth_solver/cli/pathwidth`, `-l -v`) with a
240 s cap, one hour of wall clock on 14 processes. Result: **6,715 graphs,
6,542 proved exactly**, 173 with only an upper and a lower bound (all at
`n ≥ 80`), 12.4 core-hours of which 11.5 are the 173 timeouts and 0.9 the
6,542 proofs; 137 samples per cell at `n ≤ 60`, 12–13 at
`n ≥ 70`. Proof types among the 6,542: 3,503 refutations, 2,318 closed by the
floor, 721 by a contraction minor. The witness layout of every graph is in
`results.csv` (committed in `8f59cb0e8`). None of these graphs had been solved
before.

**Where exact pathwidth reaches at 240 s.** Every cell to `n = 70` is proved,
almost all in under a second (the slowest cell median is 29 s, at `n = 70,
c = 8`). Above that the solver fails on the dense side first: at `n = 80` for
`c ≥ 6` (5–8 of 12 proved), at `n = 90` for `c ≥ 4` (8 of 13 at `c = 4`, at most
1 of 13 for `c ≥ 6`), at `n = 100` for `c ≥ 4` (2 of 13), at `n = 120` for
`c ≥ 3` (3 of 13 at `c = 3`, none beyond). The sparse cells `c ≤ 2` are proved
at every size to 120 in under a second. The unproved graphs have upper–lower
gaps of 1–3 at `n ≤ 90` and up to 14 at `n = 120, c = 10`. So the full
measurement is cheap for `n ≤ 70` at every `c` and for `c ≤ 2` at every `n`,
and needs a different budget, or no cap, for `n ≥ 80, c ≥ 4`.

**Mean `pw/n` (standard deviation of `pw` in parentheses), proved graphs only.**
Cells with fewer than 10 proved are marked `*`; cells with timeouts are biased
low, since the unproved graphs are the harder, presumably wider, ones.

| `n` | `c = 0.5` | 1 | 1.5 | 2 | 3 | 4 | 6 | 8 | 10 |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 0.051 (0.21) | 0.070 (0.52) | 0.093 (0.58) | 0.121 (0.69) | 0.197 (1.01) | 0.272 (1.01) | 0.393 (0.89) | 0.489 (0.81) | 0.571 (0.79) |
| 30 | 0.035 (0.25) | 0.047 (0.54) | 0.067 (0.64) | 0.096 (0.83) | 0.165 (1.19) | 0.236 (1.16) | 0.350 (1.18) | 0.446 (1.01) | 0.516 (0.97) |
| 40 | 0.026 (0.19) | 0.040 (0.55) | 0.058 (0.71) | 0.084 (1.00) | 0.151 (1.23) | 0.220 (1.18) | 0.334 (1.17) | 0.426 (1.20) | 0.493 (1.07) |
| 50 | 0.021 (0.22) | 0.032 (0.49) | 0.053 (0.77) | 0.074 (1.07) | 0.142 (1.47) | 0.206 (1.43) | 0.325 (1.40) | 0.407 (1.22) | 0.475 (1.10) |
| 60 | 0.018 (0.23) | 0.028 (0.50) | 0.045 (0.75) | 0.071 (1.01) | 0.136 (1.48) | 0.205 (1.53) | 0.313 (1.43) | 0.401 (1.33) | 0.463 (1.20) |
| 70 | 0.014 (0.00) | 0.025 (0.60) | 0.038 (0.75) | 0.074 (0.90) | 0.133 (1.89) | 0.185 (1.61) | 0.301 (1.50) | 0.399 (1.11) | 0.461 (1.64) |
| 80 | 0.016 (0.43) | 0.019 (0.50) | 0.042 (0.85) | 0.058 (1.43) | 0.118 (1.04) | 0.190 (1.72) | 0.300\* | 0.375\* | 0.441\* |
| 90 | 0.013 (0.36) | 0.020 (0.42) | 0.033 (0.68) | 0.062 (1.60) | 0.124 (1.82) | 0.178\* | — | — | — |
| 100 | 0.012 (0.36) | 0.018 (0.36) | 0.028 (0.77) | 0.061 (1.49) | 0.118 (1.52) | 0.180\* | — | — | — |
| 120 | 0.010 (0.36) | 0.017 (0.27) | 0.034 (0.92) | 0.051 (0.92) | 0.100\* | — | — | — | — |

Medians are within one unit of the means everywhere. At `n = 60` the mean
number of components is 45.6, 30.9, 18.5, 10.7, 4.3, 2.0, 1.1, 1, 1 for the
nine values of `c`, so the cells `c ≤ 2` are forests-plus-a-few-cycles and
their pathwidth is that of the largest component, which is why `pw/n` there
tends to 0 (§2).

**Finite-size behaviour, and the test of §1.4 (item 5 of §7(b)).** `pw/n`
falls with `n` at every `c`, as Gogate–Dechter's treewidths did. On the cells
with at least 12 proved graphs, `pw` is linear in `n` to the eye, and a least
squares fit `pw ≈ β_∞ n + γ` gives:

| `c` | `β_∞` (fit) | `γ` | `β*(c)` (§1.4, derived LB) | PS tw LB | best UB (§7(a)) |
|---|---|---|---|---|---|
| 2 | 0.040 | 1.8 | 0 | 0 | 0.162 |
| 3 | 0.099 | 2.1 | 0.009 | 0 | 0.260 |
| 4 | 0.158 | 2.4 | 0.061 | 0 | 0.347 |
| 6 | 0.268 | 2.6 | 0.171 | 0.092 | 0.520 |
| 8 | 0.360 | 2.6 | 0.263 | 0.214 | 0.693 |
| 10 | 0.415 | 3.1 | 0.337 | 0.297 | 0.760 |

(`β*` recomputed here from the definition in §1.4 by a scan in steps of
`10⁻⁴`; it agrees with §7(a).) The fitted slopes sit **above `β*(c)` at every
`c ≥ 3`, by 0.08–0.10**, and below every upper bound by a factor of 1.8–2.6.
Stronger than the mean: at `n = 60`, **no single graph** in any cell has
`pw < β*(c)·n` (the minimum `pw/n` is 0.083, 0.133, 0.267, 0.333, 0.417 at
`c = 3, 4, 6, 8, 10`, against `β*` of 0.009, 0.061, 0.171, 0.263, 0.337). So
the derived first-moment bound passes the data test it was given: nothing
measured falls below it, with a margin that leaves room for the asymptotic
correction. This is consistency, not proof; the fitted `β_∞` are extrapolations
from `n ≤ 70–120` and the §14 lesson of `reports/ml_nature.md` applies to them
exactly (the intercept `γ ≈ 2–3` is the same order as the drift seen there).
Kneis's `c/11.54` is the closer upper bound at `c ≤ 6` and the independence
bound at `c ≥ 8`, but neither is within 0.2 of the fit.

One discrepancy, checked against the paper (2026-10-28): Gogate–Dechter's
**treewidth** means at `n = 50` (§7(a)) are 0.216 at `c = 4` and 0.346 at
`c = 6`, where our pathwidth means at `n = 50` are 0.206 and 0.325, and a
mean treewidth cannot exceed a mean pathwidth on the same distribution. Their
§7.1 (p. 206) generates `G(n, m)`: "we select m edges uniformly at random from
the possible set of n(n − 1)/2 edges", "averages over 100 instances for each
combination of m and n"; the paper has no parameter `c`, and the `c` in §7(a)
is our `2m/n`. Our `G(n, c/n)` has `c(n − 1)/2` edges in expectation, 2% fewer
at `n = 50`: mean `m` 97.3, 148.3, 196.5 in our cells against their fixed 100,
150, 200. Their own neighbouring rows put the slope near `m = 100` at
0.13–0.14 per edge, so the edge deficit accounts for 0.35–0.4 of the 0.52
gap at `c = 4` (10.8 against 10.28) and the rest is one standard error. At
`c = 6` it accounts for 0.1–0.2 of 0.9 (17.3 against 16.27), and there the
printed row is off their own curve: increments per 50 edges at `n = 50` are
+7.2, +6.5, **+3.0**, +3.65/50, and interpolating their `m = 100` and `m = 200`
rows gives 15.6 at `m = 150`, below our 16.27. Dow & Korf (2007, same
generator) report "a discrepancy between the performance reported by Gogate &
Dechter (2004) and the performance of the implementation they made available
to us", disregard QuickBB's anytime answers as non-optimal, and find it unable
to solve 93 of 100 `(35, 140)` graphs in an hour, against the 2004 claim that
every 50-vertex graph was solved in under two hours. So their Table 1 is a
rough finite-`n` reference, not a lower envelope for pathwidth; `c = 4` and
`c = 8` reconcile, `c = 6` does not and the fault is more likely theirs.

**Variance (item 3 of §7(b)).** The variance of `pw` at fixed `c` grows with
`n` for every `c ≥ 1.5`: at `c = 3` it is 1.01, 1.42, 1.52, 2.15, 2.19 for
`n = 20, 30, 40, 50, 60`, and at `c = 4, 6, 8, 10` likewise about doubles over
that range. It is therefore not `O(1)` at these sizes, and it grows more slowly
than `n` (a factor 2.2 while `n` triples). Whether that is a slow approach to
Azuma's linear scale or to a constant cannot be told from `n ≤ 60`. At
`c ≤ 1` the variance is flat (0.04–0.3): the pathwidth is that of the largest
tree component and takes two or three values.

**`pw − tw` (item 4 of §7(b); computed 2026-10-28/29, `pwtw.py`,
`p17_censored.py`, data `pwtw.csv` and `p17_censored.csv`).** Exact treewidth
of the 6,149 proved graphs at `n ≤ 60`, in two passes. First our own
`learning/treewidth.py` (the subset DP at `n ≤ 26`, otherwise the decision
search from the MMD floor with `pw` as a free upper bound, 5 M nodes per call,
20 s per graph): exact on 4,510, 4.4 core-hours, and nothing on the dense cells
at `n ≥ 40, c ≥ 6`, where the lower bound never leaves the MMD floor and
top-down fares no better. Then the 1,639 graphs it left censored went to the
PACE 2017 exact-track winner, Larisch & Salfelder's p17 (`grtd -m 64`, built in
`tools/p17`, see `tools/README.md`), 600 s per graph on 8 niced cores, 72
core-hours: **exact on 1,305 more**, every graph at `n ≤ 50` (the slowest
cell, `n = 50, c = 8`, at a median of 85 s and a maximum of 582 s) and
`n = 60` up to `c = 4`; at `n = 60` it settled 63 of 134 at `c = 6`, 3 of 132
at `c = 8` and none at `c = 10` within the cap. A one-hour cap on those 334
(258 core-hours more) settled 170: `n = 60` now stands at 114 of 134 at
`c = 6`, 66 of 132 at `c = 8` and 56 of 133 at `c = 10`, the solved ones at
a median of 20–40 minutes each; the 164 still open are the hardest of their
cells, so those three cells are biased toward the easier graphs. Its decompositions are all checked valid by `check_td.py`, every
answer lies in our proved interval, and on 120 graphs where both are exact the
two solvers agree. Tamaki's 2016 solver, also in p17 as `tw-exact`, settles
only the sparse censored graphs. **5,985 of 6,149 exact** in all:

| `pw − tw` | 0 | 1 | 2 | ≥ 3 |
|---|---|---|---|---|
| graphs | 4,478 | 1,501 | 6 | 0 |

Mean `pw − tw` and, in parentheses, the share with `pw = tw`; every cell has
135–137 graphs except the three starred, `n = 60` at `c = 6, 8, 10` with 114,
66 and 56 (the easier part of each cell):

| `n` | `c = 0.5` | 1 | 1.5 | 2 | 3 | 4 | 6 | 8 | 10 |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 0.02 (98%) | 0.12 (88%) | 0.11 (89%) | 0.18 (82%) | 0.20 (80%) | 0.29 (71%) | 0.27 (73%) | 0.14 (86%) | 0.15 (85%) |
| 30 | 0.01 (99%) | 0.18 (82%) | 0.22 (78%) | 0.36 (64%) | 0.35 (65%) | 0.29 (71%) | 0.20 (80%) | 0.18 (82%) | 0.20 (80%) |
| 40 | 0.01 (99%) | 0.31 (69%) | 0.36 (64%) | 0.36 (64%) | 0.39 (61%) | 0.36 (64%) | 0.23 (77%) | 0.15 (85%) | 0.12 (88%) |
| 50 | 0.04 (96%) | 0.26 (74%) | 0.45 (55%) | 0.52 (48%) | 0.54 (48%) | 0.40 (61%) | 0.21 (79%) | 0.15 (85%) | 0.14 (86%) |
| 60 | 0.02 (98%) | 0.32 (68%) | 0.45 (55%) | 0.56 (44%) | 0.54 (46%) | 0.33 (67%) | 0.22 (78%)\* | 0.21 (79%)\* | 0.18 (82%)\* |

`pw = tw` on 75% overall and the gap never exceeds 2 (six graphs, at
`n = 40–50`, `c = 2–6`). Two things are visible now that the dense cells are
in. **The gap peaks at `c ≈ 2–3` and falls on the dense side**: at `n = 50`
the share with `pw > tw` is 52% at `c = 2–3`, 39% at `c = 4`, 21% at `c = 6`
and 15% at `c = 8–10`, the same shape at every `n ≥ 30`. The sparse peak is
the regime of trees of cliques with branching, where the project's bound
work already found pathwidth above treewidth (`reports/ml_nature.md` §6);
on the dense side the graph is an expander-like core and the two widths
coincide. **With `n` the gap grows slowly at every `c ≤ 3`** (at `c = 2`
the share with a gap is 18%, 36%, 36%, 52%, 56% for `n = 20, …, 60`; the
pooled mean rises 0.16, 0.22, 0.26, 0.30, 0.36) and is flat at `c ≥ 6`, so
`pw − tw` at these sizes is at most a slowly growing constant and nowhere
near linear. Subcritically (`c ≤ 1`) the derived `pw − tw → ∞` of §2 is
invisible, as §7(b) predicted: `pw = tw` on 96–99% at every `n`, maximum
gap 1. For comparison, the MOSP corpus has `pw > tw` on 48.5–76.3% of its
bound-gap instances and a largest gap of 2 at 10 vertices (§21, §27 there);
random graphs at these sizes sit at the same gap scale. Mean `tw/n` per
cell is in the data; at `n = 50` it is 0.198 at `c = 4`, 0.321 at `c = 6`
and 0.405 at `c = 8`, against Gogate–Dechter's 0.216, 0.346 and 0.407 on
`G(n, m)` with 2% more edges (the discrepancy paragraph above), so the
`c = 6` row of theirs is now 1.2 stacks above a 136-graph exact mean.

**Not measured.** The critical window (item 2; the grid has no points between
`c = 1` and `1.5`), treewidth on the 164 hardest graphs at `n = 60, c ≥ 6`
(an hour each was not enough), and anything at `n ≥ 80, c ≥ 4` beyond bounds.

**What the pilot was for.** It priced the full measurement. Scaling each
cell's mean seconds per proved graph, 1,000 samples per cell over the whole
`c` grid at `n ≤ 70` is about 16 core-hours, three quarters of it in the three
cells `n = 70, c ∈ {6, 8, 10}` (9–24 s per graph; every other cell is under
1.3 s). Above `n = 70` the cost is set by the dense cells, which the cap did
not resolve, and a cap of 240 s there buys nothing but bounds. The decision on running it is the owner's; the todo item
is "The large-n theorem first" (`paper1/todo.md`), which these data test and
cannot prove.

---

## PDFs saved to `literature/` in this session

- `2007-Dow-Korf-Best-First-Search-Treewidth-AAAI.pdf` (AAAI 2007, free from AAAI)
- `2013-Bayati-Gamarnik-Tetali-Interpolation-Method-Scaling-Limits-Sparse-Random-Graphs-AOP-arXiv.pdf` (arXiv 0912.2444)
- `2017-Li-Muller-Treewidth-Random-Geometric-Graphs-Percolated-Grids-AAP-preprint.pdf` (author preprint, math.rug.nl)

Already held and used here: Do–Erde–Kang 2024, Gao 2012, Lee–Lee–Oum 2012,
Perarnau–Serra 2014, Mitsche–Perarnau 2012, Kolesnik–Wormald 2014,
Díaz–Diner–Serna–Serra 2022, Lichev–Mitsche 2023, Díaz–Petit–Serna–Trevisan 2001,
Karoński–Szymkowiak 2001, Gogate–Dechter 2004, Fomin–Høie 2006, Coudert et al. 2016,
Flajolet–Raoult–Vuillemin 1979, Shang 2022.

## Not verified, or not read in full

- Kloks (1994): the DOI is from memory. Constants are taken from three independent restatements.
- Gao (2006) COCOON constant 2.16: from restatements only.
- Wang–Liu–Cui–Xu (2011): abstract only.
- Kneis et al. (2009): abstract only (`m/5.769 + O(log n)`).
- Edwards–McDermid (2015): closed form not read.
- FGSS coefficients: from a search snippet.
- KSS (1999): gate-matrix content not read.
- Devroye–Kruszewski (1995): content.
- Esparza–Luttenberger–Schlund (2014): the pw–Strahler inequality, as quoted secondhand.
- Scheffler's `pw(tree) ≤ log₃(2N+1)`: classical, not re-checked.
- Random greedy `α ≥ ln(1+c)/c · n`: classical, reference not re-checked.
- Cheung–Girardet (2020): abstract only.
- All **[derived]** statements (§1.4, §2, §3 sharpenings) are ours and unrefereed.
