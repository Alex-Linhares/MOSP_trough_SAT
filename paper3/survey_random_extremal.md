# Paper 3 survey: asymptotic, probabilistic and extremal results on pathwidth / vertex separation / MOSP

*2026-10-09. Literature survey for a possible paper on the applied mathematics
of pathwidth on special graph classes. Nothing here changes code, `solutions/`
or paper2. Every statement in the table was read from the paper itself, at the
theorem and page given, unless it is marked **abstract only** or **via
survey**. "Ours" marks a one-line derivation made in this survey from read
statements. It is not a published result, and each one is proved in the text.*

Conventions: `pw` = pathwidth = vertex separation `vs` (Kinnersley 1992);
`opt(I) = pw(G_I) + 1` for the MOSP graph `G_I` (`MOSPGraph.lean`). A MOSP
instance whose products are drawn at random is a **random intersection
graph**: customers are the vertices, products are the "features", and two
customers are adjacent iff they share a product. This is the model
`G_I(n, m, p)` of Karoński, Scheinerman & Singer-Cohen (1999), and Gao (2012)
states it as "the primal graph of a random hypergraph" (arXiv p. 6).
**The model was introduced partly *for* gate matrix layout**, which is
MOSP. That is the central finding of this survey.

---

## 1. Results table

PDF page numbers are the page of the held file. The journal page is added where the
file is the published version.

### 1a. Random graphs: G(n, p), random intersection, random regular, random geometric

| # | Setting | Result | Type | Source, theorem, page | Held? file |
|---|---|---|---|---|---|
| R1 | **Random intersection graph** `G_I(n, m, p)`, `m = n^α`, any `α > 0` | If `p ≥ 2/m` (i.e. each vertex has ≥ 2 features on average, more precisely `p = c/m` with `c > 2` in the proof), then there is `β > 0` with `P{tw(G_I) > βn} → 1`. Proof: first moment over balanced `βn`-separators, with `P{no feature meets both sides} = [(1−p)^{a} + (1−p)^{b} − (1−p)^{(1−β)n}]^m` (eq. 4.22). | theorem | Gao (2012) DAM 160; arXiv 0907.5481, Thm 2 p. 3, proof §4 pp. 16–17 | yes, `2012-Gao-Treewidth-Erdos-Renyi-Random-Intersection-Scale-Free-Random-Graphs-DAM-arXiv.pdf` |
| R2 | same paper | Gao states the motivation in his own words: Karoński et al. "discussed the application of this model in the average-case analysis of algorithmic problems in gate matrix circuit design". His Thm 2 "complements an observation in [16] on the average case behavior of the gate matrix layout problem" | context | Gao, §2.2 p. 6 and abstract p. 1 | yes (same) |
| R3 | `G(n, m)` Erdős–Rényi | `m/n ≥ 1.073` ⇒ `tw > βn` whp (Kloks: 1.18) | theorem | Gao, Thm 1 p. 2 | yes (same) |
| R4 | `G(n, c/n)` | `c > 1` ⇒ rank-width, clique-width and tree-width ≥ `c′n` whp; `c < 1` ⇒ tw ≤ 2 | theorem | Lee, Lee & Oum (2012) JGT 71, Cor 1.2 p. 2 (via Benjamini–Kozma–Wormald expansion of the giant) | yes, `2012-Lee-Lee-Oum-Rank-Width-Random-Graphs-JGT-arXiv.pdf` |
| R5 | `G(n, p)`, `p ≫ 1/n` (dense) | `td(G) = n − O(√(n/p))` a.a.s. They say "our proof of Theorem 1.1 provides the same result for tree-width". **Ours:** since `tw ≤ pw ≤ td`, **`pw(G(n,p)) = n − O(√(n/p))`**. | theorem (pw: corollary) | Perarnau & Serra (2014) DAM 168; arXiv 1104.2132, Thm 1.1 p. 2 | yes, `2014-Perarnau-Serra-Tree-Depth-Random-Graphs-DAM-arXiv.pdf` |
| R6 | `G(n, c/n)` | `td = Θ(log log n)` for `c < 1`, `Θ(log n)` at `c = 1`, `Θ(n)` for `c > 1`. So `pw` is `O(log log n)`, `O(log n)` and `Θ(n)` respectively. | theorem | Perarnau & Serra, Thm 1.2 p. 2 | yes (same) |
| R7 | `G(n, (1+ε)/n)`, `ε` constant small | `tw = Ω(ε³ n / log(1/ε))`, `rw = Ω(ε³ n / log³(1/ε))`, by direct proofs via a spanning tree of the giant (Łuczak–McDiarmid technique) | theorem | Do, Erde & Kang (2024) JGT; arXiv 2202.06087, Thms 1.4–1.5 p. 3 | yes, `2024-Do-Erde-Kang-Note-Width-Sparse-Random-Graphs-JGT-arXiv.pdf` |
| R8 | weakly supercritical `ε = o(1)`, `ε³n → ∞` | **`tw = Θ(ε³ n)`** and `rw = Θ(ε³ n)`. The upper bound holds because "tree-width of a graph is at most the number of excess edges", and the giant has `Θ(ε³n)` excess. Open: Question 5.1, is `tw ≥ cε³n` for constant `ε`? | theorem + open question | Do, Erde & Kang, Thm 1.6 p. 4; Q 5.1 p. 14 | yes (same) |
| R9 | Binomial `G(n, c_n/n)`, `c_n ≥ C_{ε,γ} = 3(1+ln 3)(εγ)^{-2}` | Bandwidth, MinLA, cutwidth, sum cut, **vertex separation**, edge and vertex bisection are approximable within a factor `O(ε+γ)` w.o.p. The survey's gloss: "any algorithm computing a feasible layout, no matter how good or bad, will perform rather well on random graphs" | theorem | Díaz, Petit, Serna & Trevisan (2001) *Discrete Math.* 235, **via survey**: Díaz, Petit & Serna (2002) ACM CSUR 34, Thm 8.1, p. 334 (PDF p. 22) | survey held (`diaz_petit_serna_2002_survey_graph_layout_problems.pdf`); original **to obtain** |
| R10 | Random geometric `G(n, r)` in the unit square | subcritical `r ≤ c₁`: `tw, td = Θ(log n / log log n)`; supercritical `r ≥ c₂`: `tw, td = Θ(r√n)`. The authors' remark: **pathwidth has the same order**, being sandwiched between tw and td | theorem | Mitsche & Perarnau (STACS 2012; SIDMA 2017), Thms 2–3 and Remark, p. 3 | yes, `2012-Mitsche-Perarnau-Treewidth-Related-Parameters-Random-Geometric-Graphs-STACS.pdf` |
| R11 | Random geometric, `nr² → λ > λ_c` | `MINVS(G(n;r)) = Θ(nr)`, `MINBW = Θ(nr)`. For `nr²/log n → ∞` the vertex separation can be approximated arbitrarily close to 1 (isoperimetric lower bounds plus projection/dissection heuristics) | theorem | Díaz, Penrose & Petit, **via survey** DPS 2002, Thms 8.5–8.6, pp. 336–337 | survey held; originals to obtain |
| R12 | Random `d`-regular `G_{n,d}`, vertex isoperimetric number at `u = 1/2` | `i_V(d) ≥ A_d(1/2) = 2s_d`, where `s_d` is the smallest positive root of `(2d−1)^s = 2^{d/2+s−1}(1−2s)^{1/2−s}s^s`. Table: `A_3 = 0.14420`, `A_4 = 0.28966`, `A_5 = 0.40859`, …, `A_10 = 0.71371`. Cor 2: `i_V(d) ≥ 1 − 2/d + O(log d/d²)` | theorem | Kolesnik & Wormald (2014) SIDMA 28; arXiv 1311.6555, Thm 1 & Cor 2 p. 3, Table 1 | yes, `2014-Kolesnik-Wormald-Lower-Bounds-Isoperimetric-Numbers-Random-Regular-Graphs-SIDMA-arXiv.pdf` |
| R13 | **Ours, from R12** | For any layout, the last `⌊n/2⌋` vertices `U` give `vs ≥ |∂_V U| ≥ i_V(d)⌊n/2⌋`. Hence a.a.s. **`pw(G_{n,3}) ≥ 0.0721 n`**, `pw(G_{n,4}) ≥ 0.1448 n`, and `pw(G_{n,d}) ≥ (1/2 − 1/d − o(1)) n` as `d → ∞`. This is Harper's vertex-isoperimetric argument, which is our expansion bound (`reports/expansion_bound.md` §4). | bound (derived) | this survey, from Kolesnik–Wormald | — |
| R14 | Random `d`-regular, vertex bisection upper bounds | Upper bounds from a greedy algorithm analysed by the differential-equation method, with experiments, beside the KW lower bounds. For `d = 3` they note the edge-bisection bounds `0.103295n ≤ bw(G_{n,3}) ≤ 0.139822n` (Lichev–Mitsche) | bound + experiment | Díaz, Diner, Serna & Serra (2022) arXiv 2211.03206, Table 2 p. 16 | yes, `2022-Diaz-Diner-Serna-Serra-Vertex-Bisection-Width-Random-Regular-Graphs-arXiv.pdf` |
| R15 | Random cubic, edge bisection | a.a.s. `0.103295n ≤ bw(G(n,3)) ≤ 0.139822n` | theorem | Lichev & Mitsche (2023) EJC 30; arXiv 2009.00598, Thm 1.1 p. 2 | yes, `2023-Lichev-Mitsche-Minimum-Bisection-Random-3-Regular-Graphs-EJC-arXiv.pdf` |
| R16 | Random intersection graph `G_{n,m,p}`, `m = n^α`, `α ≠ 1`, `p²m = c/n` | Giant component: `(1+o(1))(1−ρ)n` for `α > 1, c > 1`, and `(1+o(1))(1−ρ)√(cmn)` for `α < 1, c > 1`, with `ρ = exp(c(ρ−1))`. Logarithmic or `√(n/m) ln m` below. **The case `α = 1` (our `m = Θ(n)`) is excluded.** | theorem | Behrisch (2007) EJC 14 #R17, Thm 1 p. 2 | yes, `2007-Behrisch-Component-Evolution-Random-Intersection-Graphs-EJC.pdf` |
| R17 | `G(n,m,p)` against `G(n, p̂)` | Equivalent for all properties when `p = o(1/√(n³m))`, and for **monotone** properties when `m = n^α`, `α ≥ 3`, with `p̂ = 1 − exp(−mp²(1−p)^{n−2})`. "pw ≤ k" is monotone, so at `m ≥ n³` random-MOSP pathwidth thresholds are those of `G(n, p̂)` | theorem | Rybarczyk (2011) RSA 38; arXiv 0910.5311, Thms 1–2 pp. 3–4 | yes, `2011-Rybarczyk-Equivalence-Random-Intersection-Graph-Gnp-RSA-arXiv.pdf` |
| R18 | `G_I(n,m,p)` (the model's introduction) | "A new model of random graphs — random intersection graphs — is introduced … thresholds for the appearance and disappearance of small induced subgraphs. **An application to gate matrix circuit design is presented.**" | theorem (content unread) | Karoński, Scheinerman & Singer-Cohen (1999) CPC 8:131–159, **abstract only** | **to obtain** |
| R19 | **Randomized 3-GML** (`k = 3` tracks, i.e. MOSP `opt ≤ 3`) on random Boolean matrices | Finds "thresholds for the appearance of matrices which are 'yes' instances for a randomized 3-GML problem" | theorem (content unread) | Karoński & Szymkowiak (2001) *Discrete Math.* 236:179–189, **abstract only** (search-engine snippet; ScienceDirect refused the download) | **to obtain** (Elsevier open archive, needs a browser) |

### 1b. Bounded degree, sparse, trees

| # | Setting | Result | Type | Source, theorem, page | Held? file |
|---|---|---|---|---|---|
| B1 | Every graph of max degree ≤ 3 | `pw ≤ (1/6 + ε)n` for `n > n_ε`, constructively. The proof uses the Monien–Preis bisection (≤ `(1/6+ε)n` edges) and Ellis et al. `pw(T) ≤ log₃ n` | theorem | Fomin & Høie (2006) IPL 97, Thm 5 p. 4 (journal p. 194) | yes, `2006-Fomin-Hoie-Pathwidth-Cubic-Graphs-Exact-Algorithms-IPL.pdf` (author copy) |
| B2 | Cubic graphs, lower side | "Bezrukov et al. … showed that there are 3-regular graphs with the bisection width at least 0.082n … also yields the lower bound 0.082n for pathwidth … an interesting challenge to reduce the gap between 0.082n and 0.167n" | bound + open problem | Fomin & Høie, §5 p. 5 | yes (same) |
| B3 | Every graph, degree profile | `pw ≤ n₃/6 + n₄/3 + 13n₅/30 + 23n₆/45 + n_{≥7} + εn` | theorem | Fomin, Gaspers, Saurabh & Stepanov (2009) Algorithmica 54, Lemma 1 p. 5 | yes, `2009-Fomin-Gaspers-Saurabh-Stepanov-Two-Techniques-Combining-Branching-Treewidth-Algorithmica-preprint.pdf` |
| B4 | Sparse graphs, by edges | `pw ≤ m/5.769 + O(log n)` | theorem | Kneis, Mölle, Richter & Rossmanith (2009) SIDMA 23, **not read**; the constant is from memory and is **not to be quoted** until read | **to obtain** |
| B5 | Trees | `pw(T) ≤ log₃ n` for `n ≥ 3` (Ellis et al.) | theorem | quoted as Thm 3 in Fomin & Høie p. 3; Ellis–Sudborough–Turner 1994 held | yes |
| B6 | Trees (Scheffler) | `pw(T) ≤ "3 log(2n+1)"` in the arboretum's text extraction (read as `log₃(2n+1)`); complete binary tree of depth `k`: `pw = ⌈k/2⌉`; complete ternary tree: `pw = height` (Kirousis–Papadimitriou) | theorem | Bodlaender (1998) TCS 209, Thms 66–68 p. 30 | yes |
| B7 | **Random trees** | **No theorem found** for the pathwidth of a uniform random labelled tree or of a conditioned Galton–Watson tree. The nearest known results are Horton–Strahler (register function) asymptotics for random binary trees, about `log₄ n` (Flajolet, Raoult & Vuillemin 1979, not read), and Biedl (2021): Horton–Strahler number = rooted pathwidth (abstract only). | gap | — | — |

### 1c. Pathwidth against treewidth, extremal, obstructions

| # | Setting | Result | Type | Source, theorem, page | Held? file |
|---|---|---|---|---|---|
| E1 | Every graph | `pw = O(tw · log n)`; quoted with explicit constant as `tw ≤ pw ≤ (tw+1) log₂ n` | theorem | Bodlaender (1998), Cor 24 p. 10; constant form in Groenland et al. (2021) p. 2 | yes |
| E2 | Every graph | **treewidth `t−1` ⇒ `pw ≤ th + 1` or a subdivision of the complete binary tree of height `h+1`**; tight up to a constant | theorem | Groenland, Joret, Nadara & Walczak (2021/23) TALG, Thm 1.1 p. 2 | yes |
| E3 | Gap examples | complete binary tree: tw = 1, pw = `⌈k/2⌉` (B6). Ours: 10-vertex `pw − tw = 2` graph (`reports/ml_nature.md` §21, §27) | theorem / census | Bodlaender Thm 67 | yes |
| E4 | Obstructions, `pw ≤ 1` (2-GML) | obstruction set `{K₃, S(K_{1,3})}`; connected yes-instances are the caterpillars | theorem | Kinnersley & Langston (1994) DAM 54, p. 4 | yes |
| E5 | Obstructions, `pw ≤ 2` (3-GML) | **exactly 110** minor-minimal obstructions | theorem | Kinnersley & Langston (1994), abstract p. 1 and §8 | yes |
| E6 | Acyclic obstructions, general `k` | number of tree obstructions for `pw ≤ k` grows super-exponentially in `k` | theorem | Takahashi, Ueno & Kajitani (1994) *Discrete Math.* 127, **not read** | **to obtain** |
| E7 | Excluding a forest | `F`-minor-free ⇒ `pw ≤ |V(F)| − 2` | theorem | Bienstock, Robertson, Seymour & Thomas (1991) JCTB 52, **not read** | **to obtain** |
| E8 | Edge extremal, **ours** | `pw(G) ≤ k` ⇒ `|E| ≤ kn − k(k+1)/2`, tight for `k`-paths. Proof: in a layout of vs ≤ k, the earlier neighbours of `v_i` lie among the ≤ `min(i−1, k)` active vertices, and summing gives the bound. For MOSP: an instance with optimum `k+1` has a MOSP graph of at most `kn − k(k+1)/2` edges | elementary (proved here) | — | — |
| E9 | Lower bound by isoperimetry | `pw(G) ≥ b_v(s, G)` (minimum vertex boundary of an `s`-set) for every `s`; exact for hypercubes | theorem | Chandran & Kavitha (2006) *Discrete Math.* 306, Thm 1 p. 3 (journal p. 361) | yes |
| E10 | **Ours**, upper bound by independence | `pw(G) ≤ n − α(G)`: take bags `(V∖I) ∪ {v}` for `v` in a maximum independent set `I`. For MOSP: **`opt ≤ n − α(G_I) + 1`**, where `α` is the largest set of customers with pairwise disjoint product sets | elementary (proved here) | — | — |

### 1d. MOSP-specific asymptotics

| # | Setting | Result | Type | Source | Held? |
|---|---|---|---|---|---|
| M1 | Expected optimum of random MOSP, linear regime | **No theorem found.** Searched OpenAlex, arXiv, Crossref and the web for "open stacks" and "gate matrix layout" with random, average-case or asymptotic, and checked the citers of Karoński et al. through Gao. The literature on random GML treats only the **fixed-`k` threshold regime** (R18, R19). What exists for `m = n^α` is `Θ(n)` without a constant (R1, by `opt = pw+1 ≥ tw+1`). | gap | — | — |
| M2 | Concentration of the optimum | No theorem for MOSP/pw. The standard route would be vertex-exposure martingale/Azuma: `pw` is 1-Lipschitz under changing one customer's row, giving `σ = O(√n)` (ours, not checked against a source) | gap | — | — |

---

## 2. Literature theorems against our empirical laws

Our laws: `reports/ml_nature.md` §11–§14, §25, §35–§37 (n ≤ 40 campaign,
50–100 extension, 125 corpus).

| Our empirical law | Nearest theorem | Verdict |
|---|---|---|
| **§12: `E[opt]` is linear in `n` above the giant-component threshold**, r² ≥ 0.999 in all 17 fixed-degree series | R1 (Gao): `tw(G_I) ≥ βn` whp when mean features per vertex `mp > 2`, any `m = n^α`; R4/R6/R7 for `G(n,p)`: `Θ(n)` exactly above `c = 1` | **Agree in order** (`Θ(n)`), **no theorem for the constant**. Gao's condition `c > 2` is a proof artefact, sufficient only. The `G_I` analogue of Lee–Lee–Oum ("linear iff supercritical") is **not proved** at `m = Θ(n)`, and Behrisch even excludes `α = 1` for the giant. |
| **§12: sublinear below the threshold** (γ ≈ ⅓, mean 4.3 at n = 40) | R6: below threshold `pw ≤ td = O(log log n)` for `G(n,p)`; components of size `O(log n)` give `pw = O(log n)` trivially; R16 gives `O(ln n)` components for `G_I` at `α > 1` | **Agree qualitatively.** Our `n^{1/3}` fit over 15–40 cannot be told from a log law at these sizes, and the theorems say it must be logarithmic or smaller asymptotically. Read γ ≈ ⅓ as finite-size behaviour. |
| **§12 formula**: `E[opt] ≈ 2.1(1−q) + n[1 − √(1−q)·27/(D+27)]`, slope `D/(D+27)` in the sparse limit, `q = 1−(1−p²)^m` | Rybarczyk R17: `p̂ = 1 − exp(−mp²(1−p)^{n−2})`, the same edge probability as our `q` to first order. R5 dense limit: `n − pw = O(√(n/p))` for `G(n,p)`, i.e. a deficit `O(n/√D)`. E10: deficit `≥ α(G) − 1` | **No theorem for the constant 27 or the form.** Consistency: our deficit `≈ 27n/D` is inside Perarnau–Serra's `O(n/√D)`. For `G(n,p)`-like graphs `α ≈ 2n ln D/D` would force deficit `≳ n ln D/D`, which our form undercuts only for `D > e^{13.5}`, far outside the data. Our `q` is the theorem-backed edge probability, so its appearance in the fit is explained, not discovered. |
| **§12: CV → 0, σ between constant and √n** | none found (M2) | **No theorem**; consistent with an Azuma `O(√n)` bound |
| **§25/§36: hardness ridge at cover excess `(n_ones − m)/n ≈ 2–2.4`, i.e. `col_mean ≈ 1 + 2.4n/m`; not a percolation threshold** | Do–Erde–Kang R8: near criticality the width is `Θ(excess of the giant) = Θ(ε³n)`. Gao's `c > 2` (R1) is "2 features per vertex" | **No theorem about search hardness**: every result found is about width, not about the cost of deciding width. The one structural coincidence: in `G(n,p)` the *excess* (cyclomatic number) of the giant governs treewidth near criticality (R8), and our ridge coordinate is an excess too, of the incidence graph. But it sits far into the supercritical regime (giant 1.5–6× lower, §25), where R8 does not apply. Gao's `mp > 2` at `m = n` means about 2 customers per product, below our `m = n` ridge at about 3, so it does not coincide either. |
| **§11/§35: refutation nodes exponential on the ridge, ~doubling every 3 customers** | none | **No theorem** (algorithmic). Nothing in the pathwidth literature corresponds to the SAT/CSP easy–hard–easy literature. |
| **§12/§6: pw > tw certified on ~10% at 2–2.5 customers/product, by at most 2** | E1, E2: `pw ≤ (tw+1)log₂ n`; Groenland et al. say a pw/tw gap needs a large subdivided complete binary tree | **Agree in mechanism.** E2 is the theorem behind our "trees of cliques with branching" family (CLAUDE.md, bounds section): the gap needs binary-tree-like branching, which random instances near 2 customers per product supply in small amounts only. No theorem on the *random* `pw − tw`. |
| Expansion bound = Harper vertex-isoperimetric (`reports/expansion_bound.md` §4) | E9 (Chandran–Kavitha Thm 1), R12/R13 (Kolesnik–Wormald) | **Agree, already recorded.** R13 gives an explicit a.a.s. constant for random regular graphs. |

**Bottom line:** the literature proves the *order* `Θ(n)` of random MOSP
optima (through treewidth, Gao 2012) and nothing about the slope. It has no
formula for `E[opt]` and no result on hardness. The only random-MOSP-specific
theorems are fixed-`k` thresholds (Karoński et al. 1999; Karoński &
Szymkowiak 2001), not yet read.

---

## 3. Applied-mathematics opportunities

1. **Prove the random-MOSP linear-width theorem at `m = Θ(n)`, and test its
   constant on the corpus.** Claim: for `G_I(n, m, p)` with `m = μn`, `opt =
   Θ(n)` whp iff the incidence branching factor `(mp)(np) > 1`, and `opt =
   O(log n)` below. Route: the incidence graph `B` of the instance satisfies
   `tw(B) ≤ tw(G_I) + 1` (standard primal/incidence inequality; to be cited).
   `B` is a random bipartite graph, so a Krivelevich/Do–Erde–Kang argument (R7,
   R8) on its giant should give `tw(B) = Ω(n)` exactly above branching 1. This would
   upgrade Gao's `c > 2` (R1) to the sharp threshold and is the `G_I`
   counterpart of Lee–Lee–Oum. Near the threshold R8 predicts **`opt ≈ Θ(ε³n)`**.
   The 37,800-instance ensemble (§10) and the 50–75 campaign (§16, all
   `m/n ∈ {⅛ … 2}`) already contain the certified optima to fit
   `opt/n` against `ε = (mp)(np) − 1` and check the cube. This is the closest
   available theorem to our §12 law, and the corpus would supply what the theory
   lacks: the constant.

2. **Random cubic (and `d`-regular) pathwidth: estimate the open constant.**
   A MOSP instance whose products each have 2 customers *is* an arbitrary graph
   (Yanasse 1997a Prop 5), so `pw(G_{n,3})` is a random MOSP. Fomin & Høie
   (B2) leave the gap `0.082n`–`0.167n` for cubic graphs as an "interesting
   challenge". For *random* cubic graphs the a.a.s. window is `0.0721n ≤ pw ≤
   (1/6+ε)n` (R13 + B1). Our exact solver (`pathwidth_solver/`, and the customer
   search) certifies optima at 40–100 vertices. A Díaz–Diner–Serna-style
   experiment (R14) with certified rather than heuristic values would place
   `lim pw(G_{n,d})/n` for `d = 3…10` between the KW lower bounds and the
   Fomin–Gaspers et al. upper bounds (B3). It is publishable as an experimental
   companion to an open problem, and it takes light CPU at 40–60 vertices.

3. **Test the two elementary bounds and the dense-regime deficit on the
   certified corpus.** (a) `opt ≤ n − α(G_I) + 1` (E10) as an upper bound,
   and `opt ≥` its isoperimetric dual (E9). (b) The deficit `n − opt` against
   `n/D` (our fit), `n/√D` (Perarnau–Serra R5) and `n ln D/D` (independence
   number): the ensemble's dense cells (`col_mean` 6–20, §12) decide which
   scaling holds on unions of cliques. A clean deficit law with a proof of
   the upper side via E10 and the Kolesnik–Wormald-style first moment for the
   lower side would be the first theorem-shaped statement about the *slope*
   of `E[opt]`. Also: (c) Karoński–Szymkowiak's 3-GML thresholds (R19) can be
   checked exactly against the ensemble's smallest-optimum cells once the
   paper is in hand, using `opt ≤ 3` ⇔ none of the 110 obstructions of E5 as
   a minor.

Where the corpus tests a conjecture: Do–Erde–Kang's Question 5.1 (`tw ≥ cε³n`
for constant `ε`) has a MOSP analogue measurable on the ensemble cells
just above the giant threshold (§36 computed those thresholds). The census
(§27) and Groenland et al. (E2) give a falsifiable prediction: random
instances with `pw − tw ≥ 2` should contain a subdivided binary tree of height
≥ 3 in the MOSP graph's minor structure.

---

## 4. Papers to obtain

DOIs were retrieved from OpenAlex/Crossref unless marked otherwise; page ranges are omitted where not seen.

| Paper | DOI | Why | Route |
|---|---|---|---|
| Karoński, Scheinerman & Singer-Cohen (1999), On random intersection graphs: the subgraph problem, *CPC* 8:131–159 | 10.1017/S0963548398003459 | introduces `G_I` with a gate matrix layout application: the root of random MOSP | paywalled; Singer-Cohen's 1995 JHU thesis *Random intersection graphs* may hold it |
| Karoński & Szymkowiak (2001), randomized three tracks variant of GML, *Discrete Math.* 236:179–189 | 10.1016/S0012-365X(00)00441-6 | the only random-MOSP threshold theorem found | Elsevier open archive (bronze); the download is refused to curl, so use a browser |
| Díaz, Petit, Serna & Trevisan (2001), Approximating layout problems on random graphs, *Discrete Math.* | 10.1016/S0012-365X(00)00278-8 | R9 at source | Elsevier open archive, browser |
| Kneis, Mölle, Richter & Rossmanith (2009), A bound on the pathwidth of sparse graphs, *SIDMA* | 10.1137/080715482 | B4 | paywalled; RWTH tech report version likely |
| Takahashi, Ueno & Kajitani (1994), Minimal acyclic forbidden minors for bounded path-width, *Discrete Math.* 127 | 10.1016/0012-365X(94)90092-2 (DOI from memory, unverified) | E6 | open archive, browser |
| Bienstock, Robertson, Seymour & Thomas (1991), Quickly excluding a forest, *JCTB* | 10.1016/0095-8956(91)90068-U | E7 | open archive, browser |
| Kloks & Bodlaender (1992), Only few graphs have bounded treewidth | 10.1007/BFb0045380 | counting and random graphs | Utrecht dspace 1874/16678 (direct link failed) |
| Böttcher, Pruessmann, Taraz & Würfl (2010), Bandwidth, expansion, treewidth, separators and universality for bounded-degree graphs, *European J. Combin.* | 10.1016/j.ejc.2009.10.010 | equivalence of sublinear bandwidth/treewidth/separators for bounded degree | open archive, browser |
| Gao (2006), On the threshold of having a linear treewidth in random graphs, COCOON | 10.1007/11809678_25 | earlier form of R1/R3 | Springer |
| Fill, Scheinerman & Singer-Cohen (2000), *RSA* 16 | DOI not retrieved | `G_I` vs `G(n,p)` equivalence at `m ≫ n⁶` | Wiley |
| Lagerås & Lindholm (2008), *Electron. J. Combin.* 15 | DOI not retrieved | giant of `G_I` at `m = Θ(n)` (the case Behrisch excludes) | open access |
| Shang (2022), Tree-depth and tree-width in heterogeneous random graphs, *Proc. Japan Acad. A* 98 | 10.3792/pjaa.98.015 | possible route to opportunity 1 | open access (Project Euclid refused curl) |
| Nikoletseas, Raptopoulos & Spirakis (2008), Large independent sets in general random intersection graphs, *TCS* | 10.1016/j.tcs.2008.06.047 | `α(G_I)` for opportunity 3(a) | open archive, browser |
| Łuczak & McDiarmid (2001), Bisecting sparse random graphs, *RSA* 18 | 10.1002/1098-2418(200101)18:1<31::AID-RSA3>3.0.CO;2-1 | technique of R7 | Manchester repository |
| Flajolet, Raoult & Vuillemin (1979), The number of registers required for evaluating arithmetic expressions, *TCS* 9 | 10.1016/0304-3975(79)90009-4 | random-tree Strahler number (B7) | open archive, browser |
| Biedl (2021), Horton–Strahler number, rooted pathwidth and upward drawings of trees, *IPL* | 10.1016/j.ipl.2021.106230 | B7 | arXiv version likely |
| Bezrukov, Elsässer, Monien, Preis & Tillich (2004), New spectral lower bounds on the bisection width of graphs, *TCS* | DOI not retrieved | source of the 0.082n in B2 | open archive |

Downloaded but **not kept** as off-topic after reading the abstract: Lee &
Sidiropoulos (2013), *Pathwidth, trees, and random embeddings* (metric
embeddings), and Alecu et al. (2024), *The treewidth and pathwidth of graph
unions* (unions of two bounded-width graphs; its `tw ≤ k + 3ℓ + 1` gluing
bound, abstract p. 1, is noted for completeness).

## 5. Search log

OpenAlex (title/abstract search, about 25 queries, until rate-limited with
HTTP 429), arXiv API, Unpaywall, Semantic Scholar and Crossref (both also
rate-limited during this session), and web search. Citation trail: Gao (2012) →
Karoński et al. (1999) → Karoński & Szymkowiak (2001); Do–Erde–Kang →
Lee–Lee–Oum, Perarnau–Serra, Kloks; Díaz–Diner–Serna → Kolesnik–Wormald,
Lichev–Mitsche; Fomin–Høie → Fomin–Gaspers–Saurabh–Stepanov, Bezrukov et al.
OpenAlex was rate-limited before the citer lists of Karoński et al. (216
citers) could be swept for further GML applications, so that sweep remains
to be done.
