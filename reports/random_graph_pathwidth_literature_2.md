# Pathwidth of random graphs: literature, second pass

*2026-11-01. Reading only; the one computation is evaluating closed-form
degree bounds on Poisson degree distributions (a Python script of a few
seconds, reproduced in §3.3). Written in the `appendix-picture` worktree, not
in the tree the running loop owns. Nothing was added to `literature/`; the
fetched texts are under `/tmp/lit_random/` with a URL list in
`/tmp/lit_random/URLS.txt`, and §5 says what should be filed.*

This pass goes wider and deeper than `reports/random_graph_pathwidth_survey.md`
(2026-10-17, "the survey" below) on six gaps the survey left: statements made
*directly* for pathwidth, vertex separation or node search on any random
model; the layout-problems literature read in full; the degree-based
deterministic bounds read in the PDFs rather than in abstracts; explicit
layouts analysed on random graphs; concentration; and graph searching. It does
not re-survey the linear-treewidth thresholds, the critical window, random
intersection graphs or the project's own derived bounds (survey §1–§4,
`reports/random_graph_first_moment.md` §4), and it does not touch the
separator and bisection literature that loop0011 item 01 is reading now
(balanced vertex separators, minimum bisection of `G(n, c/n)`, bisection of
random regular graphs, large deviations of the giant); where a finding here
borders that work it says so.

Labels as in the survey: **[pub]** read in the source at the page given;
**[pub, abstract]** read in abstract or metadata only; **[derived]** our own
short consequence of published facts; **UNVERIFIED** not confirmed against a
source. The owner's rule holds throughout: "we found no prior statement",
never "first". Constants are compared with `β*(c) = 0.0087, 0.1706, 0.3371` at
`c = 3, 6, 10` (the project's first-moment lower bound), with the pilot's
fitted slopes `0.040, 0.099, 0.158, 0.268, 0.360, 0.415` at
`c = 2, 3, 4, 6, 8, 10` (survey §7(d)), and with the upper constructions of
`reports/excess_phase_diagram.md` §7.

---

## 1. Verdict

**No explicit lower-bound constant for the pathwidth (or vertex separation,
node search number, interval thickness or gate matrix layout cost) of
`G(n, c/n)` at constant `c` is published, in anything read or found.** The
three sources that state vertex separation of `G(n, p)` directly all work
polynomially above `p = c/n` or with a vacuous constant: Turner (1986) for
bandwidth at fixed `p` and at `p = c ln n / n`; Díaz–Petit–Serna–Trevisan
(2001) Lemma 3 (g5), `vs ≥ (1/2 − ε) n − 1` on mixing graphs, vacuous below
`c ≈ 227`; and Cheung–Girardet (2017 arXiv, 2020 journal), read in full for
the first time here, whose Lemma 12 gives **`vs(G(n, p_n)) ≥ (1 − o(1)) n`
whp for every `p_n = Ω(n^{−c})`, `c < 1`** by the same empty-pair argument
with the prefix at `(1 − n^{−s}) n` — the "prefix at `(1 − ε) n`" variant
that `reports/random_graph_first_moment.md` §4 recorded as derived is
therefore published, though still with nothing at `p = c/n`. **For random
cubic graphs no pathwidth or vertex-separation statement exists either**:
the whp window remains the survey's derived `0.0721 n ≤ pw(G_{n,3}) ≤ n/6`
(Kolesnik–Wormald's vertex bisection below, Fomin–Høie's deterministic
Theorem 5 above); the only cubic *lower* bound stated for pathwidth is
Fomin–Høie's worst-case `0.082 n` from Ramanujan bisection, whose transfer
step is not written out. **For random trees there is now a typical-value
result, one step removed**: Brandenberger, Devroye & Reddad (EJP 2021) prove
that the Horton–Strahler number of a critical finite-variance Galton–Watson
tree conditioned on size `n` is `(1/2 + o(1)) log₂ n` in probability, and
Esparza–Luttenberger–Schlund (2014) state `pw(t) − 1 ≤ S(t) ≤ 2 pw(t)` for
trees; together **`pw(T_n) / log₂ n ∈ [1/4 − o(1), 1/2 + o(1)]` whp** for
uniform labelled (Cayley), uniform binary and uniform plane trees, against
the sharp worst case `log₃((6N + 3)/5) ≈ 0.63 log₂ N` of `TreeBound.lean`.
Nothing was found for random recursive trees or binary search trees. **The
most consequential single finding is on the upper side**: Edwards & McDermid
(2015), read in the accepted manuscript, prove
`pw(G) ≤ Σ_{d ≥ 3} g_{1/6}(d) · n_d + o(n)` with an explicit recurrence for
`g_{1/6}`, and on Poisson(`c`) degrees this gives **`pw/n ≤ 0.183, 0.458,
0.656` at `c = 3, 6, 10`**, below every upper bound in the survey's §7(a)
table (0.260, 0.520, 0.760) at every `c` from 2 to about 32, and within a
factor 1.6–1.85 of the fitted slopes. On the clique-cover cells of
`reports/excess_phase_diagram.md` §7 the same bound, evaluated crudely, is
below the project's analysed `β⁺` by 0.05–0.27 at every cell with excess
`e ≤ 3`, the ridge included. Concentration of pathwidth is written nowhere;
Do–Erde–Kang state it for tree- and rank-width in a remark. No theorem on
the node search number or any searching parameter of a random graph was
found (the only random-graph searching result located concerns the *fast*
search number, a different parameter).

---

## 2. Every statement found

Constants at `c = 3 / 6 / 10` are on `pw/n` for `G(n, c/n)` unless the model
column says otherwise; "cubic" means random 3-regular. "—" means the source
says nothing at that parameter or the statement is vacuous there.

| # | source | model | statement (where) | at c = 3 / 6 / 10, or cubic | held? | label |
|---|---|---|---|---|---|---|
| 1 | Turner 1986, *SIAM J. Comput.* 15(2):561–580, DOI 10.1137/0215041 | `G(n, p)`, `p` fixed; `p = c ln n / n`; planted `Γ_n(β, p)` | Thm 2.1 `bw > n − 4 log_b n`; Thm 2.2 `bw ≥ (1 − ε) n` for `p = c ln n / n`; Thm 2.3, 3.1, 3.2 and the Conjecture on the planted model (§3.1 below) | — (nothing at `p = c/n`) | text in `reports/scratch/first_moment/lit/turner1986.txt` (main tree) | [pub] |
| 2 | Díaz, Petit, Serna & Trevisan 2001, *Discrete Math.* 235:245–253, DOI 10.1016/S0012-365X(00)00278-8 | `G(n, c_n/n)`, `c_n ≥ 3(1 + ln 3)(εγ)^{−2}`, `ε < 1/6` | Lemma 3 (g5) `MINVS ≥ (1/2 − ε) n − 1` on mixing graphs; Thm 1 every layout problem within a constant w.o.p. (pp. 250–252) | vacuous below `c ≈ 227` | yes | [pub] |
| 3 | Díaz, Petit & Serna 2002, *ACM Comput. Surv.* 34(3):313–356, DOI 10.1145/568522.568523 | as 2 | §8.1 Thm 8.1 restates 2; "BANDWIDTH can be approximated within a constant on binomial random graphs; see Bollobás [1985 page 374] and Turner [1986]" (p. 334); §8.3 Thms 8.4–8.6 for RGGs | — | yes | [pub] |
| 4 | Cheung & Girardet, arXiv 1710.10339 (2017); *Open J. Discrete Math.* 10(1):13–30 (2020), DOI 10.4236/ojdm.2020.101003 | `G(n, p_n)`, `p_n = Ω(n^{−c})`, `c < 1` | Lemma 12 `P[MINVS(G_n) ≥ (1 − δ) n − 1] > 1 − ε` for large `n`; Thm 11 `GAP_VS < 1 + δ` whp; the same for vertex bisection and for DAGs (Thms 13ff.); cutwidth and edge bisection need `c < 1/2` (Thms 5, 9) | — (needs `p ≥ n^{−1+ε}`) | fetched, arXiv text | [pub] |
| 5 | Petit 2011, *Bull. EATCS* addenda to 3 | — | "It does not cover: … new results on random graphs" (p. 2) | — | yes | [pub] |
| 6 | Mareček 2009, arXiv 0908.1772 | `G(n, 1/2)` only | Thm 2 rank-width `Ω(n)` a.a.s.; Cor 1–5 rw, tw, branchwidth, clique-width, NLC-width `Θ(n)`; no pathwidth, no constant | — | fetched | [pub] |
| 7 | Gao 2012, *DAM* 160:566–578, DOI 10.1016/j.dam.2011.10.013 | `G(n, m)`; RIG; Barabási–Albert | Thm 1 `m/n ≥ 1.073`; Thm 2 RIG with `m = n^α`, **`p ≥ 2/m`**; **Thm 3 BA with `m ≥ 12` edges per new vertex: `tw > βn` whp**, `β` implicit (arXiv p. 3); remark that tw of `G(n, m)` for `1/2 < m/n < 1` "is unknown" (p. 3; settled by Lee–Lee–Oum) | implicit | yes | [pub] |
| 8 | Fomin & Høie 2006, *IPL* 97:191–196, DOI 10.1016/j.ipl.2005.10.012 | every graph of max degree 3 | Thm 5 `pw ≤ (1/6 + ε) n` for `n > n_ε`; Lemma 4; Thm 2 (Monien–Preis) bisection `(1/6 + ε) n`; §5 "the result of Bezrukov et al. also yields the lower bound `0.082n` for pathwidth of graphs with maximum degree three" (p. 195) | cubic: `≤ 1/6` | yes | [pub] |
| 9 | Monien & Preis, MFCS 2001, LNCS 2136:524–536; *J. Discrete Algorithms* 4:475–498 (2006), DOI 10.1016/j.jda.2005.12.009 | every large cubic graph | bisection width `≤ (1/6 + ε) n` (as restated in 8, Thm 2) | cubic | no | [pub, as restated] |
| 10 | Bezrukov, Elsässer, Monien, Preis & Tillich 2004, *TCS* 320:155–174, DOI 10.1016/j.tcs.2004.03.059 | Ramanujan cubic graphs; random cubic (restating Kostochka–Melnikov) | bisection width `≥ 0.082n` for 3-regular Ramanujan graphs (p. 157, §1); restates "Kostochka and Melnikov showed that the bisection width is at least `n/4.95 ≈ 0.202n` for almost all 3-regular random graphs" (p. 157) — **inconsistent with 11**, see §3.2 | — | yes | [pub] |
| 11 | Lichev & Mitsche 2023, *Electron. J. Combin.* 30(2), arXiv 2009.00598 | random cubic | Thm 1.1 `0.103295 n ≤ bw(G(n, 3)) ≤ 0.139822 n` a.a.s.; history: Bollobás `n/11`, Kostochka–Melnikov `0.10101 n` (p. 1–2) | cubic edge bisection | yes | [pub] |
| 12 | Kolesnik & Wormald 2014, *SIAM J. Discrete Math.* 28(1):553–575, DOI 10.1137/120891265 | random `d`-regular | Thm 1 vertex isoperimetric number `i_V(d) ≥ A_d(1/2) = 2 s_d`, `s_d` the smallest positive root of `(2d − 1) s = 2^{d/2 + s − 1} (1 − 2s)^{1/2 − s} s^s`; Table 2 `A_3 = 0.14420`, `A_4 = 0.28966`, `A_6 = 0.50190`, `A_10 = 0.71371`; Cor 2 `A_d = 1 − 2/d + O(log d / d²)` (pp. 5, 24) | cubic: `pw ≥ 0.0721 n` [derived, survey] | yes | [pub] |
| 13 | Díaz, Diner, Serna & Serra 2022, arXiv 2211.03206 | random `d`-regular | Table 2 vertex bisection: lower `0.14420` (from 12), upper `0.27964` (`d = 3`, from Monien–Preis), `0.58103` (`d = 4`, DEM) — upper bounds on vertex bisection, **not** on pw (p. 15) | — | yes | [pub] |
| 14 | Perarnau & Serra 2014, *DAM* 168:119–126 | random `d`-regular, configuration model | Cor 4.6 linear tw and td for fixed `d ≥ 3`, via `tw ≥ (α(d)(n − 1) − 3)/(α(d) + 3)` with `α(d) = (d − O(√d))/2` from Friedman–Kahn–Szemerédi, constant not made explicit (pp. 11–12) | implicit | yes | [pub] |
| 15 | Kneis, Mölle, Richter & Rossmanith 2009, *SIAM J. Discrete Math.* 23(1):407–427, DOI 10.1137/080715482 | every graph | `pw ≤ m/5.769 + O(log n)`; `m/5.217 + 3` with all bags sharing a large common set (abstract, read through Crossref; `13/75 = 1/5.769` confirmed by 17 p. 19) | 0.260 / 0.520 / 0.867; cubic 0.260 | no (closed) | [pub, abstract] |
| 16 | Fomin, Gaspers, Saurabh & Stepanov 2009, *Algorithmica* 54:181–207, DOI 10.1007/s00453-007-9133-3 | every graph, `n > n_ε` | Lemma 1 **`pw ≤ n₃/6 + n₄/3 + 13n₅/30 + 23n₆/45 + n_{≥7} + εn`** (preprint p. 5; the survey's `n_{≥6}` was wrong); Lemma 2 `tw ≤ (m − n)/3 + εn` for connected `G` with `m/n ∈ [1.5, 2]` | 0.196 / 0.605 / 0.926; cubic 1/6 | yes | [pub] |
| 17 | Edwards & McDermid 2015, *Algorithmica* 72(4):940–968, DOI 10.1007/s00453-014-9883-7 | every graph | Cor 5.2 **`pw(G) ≤ Σ_{d ≥ 3} g_{1/6}(d) n_d + o(n)`**, `g_{1/6}(2) = 0`, `g_{1/6}(3) = 1/6`, `n g(n) = (n − 2) g(n − 1) + g(n − 2) + 1`; Thm 5.3 for average degree `d` (connected or `d ≥ 5`) `pw ≤ (g_{1/6}(d) + o(1)) n = (1 − (7/2)/(d + 1) + O(d^{−3})) n`; restates Golovnev–Kutzkov: `pw ≤ (1 − 4ε ln d / d) n` for `d_ε ≤ d ≤ n/(1 + ε)` (pp. 19–20, 6) | **0.183 / 0.458 / 0.656**; cubic 1/6 | fetched (accepted manuscript) | [pub] |
| 18 | Golovnev & Kutzkov 2014, *TCS* 526:18–27, DOI 10.1016/j.tcs.2014.01.010 | every graph of average degree `d ≥ d_ε` | as restated in 17: `pw ≤ (1 − 4ε ln d / d) n`, `d_ε = O(exp(1/ε))` | large `c` only | no | [pub, as restated] |
| 19 | Díaz, Penrose, Petit & Serna 2001, *J. Algorithms* 39:78–116, DOI 10.1006/jagm.2000.1149; read in Petit's thesis (UPC 2001, ALCOM-FT TR-01-157) | RGG, `n` uniform points in `[0, 1]²`, radius `r_n → 0`, `n r_n² / log n → ∞` | thesis Thm 5.13: **`minvs(G_n) / (n r_n) → 1` a.s.**, likewise bandwidth and vertex bisection; Thm 5.10 `minvs ≥ (1 − 6√ε) n r_n` on `ε`-good graphs; the projection layout attains it (pp. 148–152) | RGG: sharp constant 1 | thesis fetched | [pub, thesis version] |
| 20 | Díaz, Penrose, Petit & Serna 2000, *CPC* 9:489–511; Penrose 2000 | RGG subcritical / supercritical, `n r_n² → λ` | thesis Thm 5.17 `vs = Θ(log n / log log n)` for `λ < λ_c`; Thm 5.5 (Penrose) `minvs = Θ(n r_n)` for `λ > λ_c` (pp. 131, 172) | — | thesis fetched; survey R11 | [pub] |
| 21 | Mitsche & Perarnau 2012/2017 | RGG | Remark p. 5: pathwidth has the same order as tw and td "since the pathwidth is bounded from below by the treewidth and bounded from above by the treedepth" | — | yes | [pub] |
| 22 | Brandenberger, Devroye & Reddad 2021, *Electron. J. Probab.* 26:1–29, DOI 10.1214/21-EJP678, arXiv 2010.08613 | critical Galton–Watson trees, offspring variance `σ² ∈ (0, ∞)`, conditioned on size `n` | **`H(T_n) / log₂ n → 1/2` in probability** (p. 2 and Thm 4–5), `H` with leaves at 0; covers Cayley, Catalan, plane and `k`-ary trees; `k`-ary register function `~ log₂ log₂ n / log₂(k/2)` | trees | fetched | [pub] |
| 23 | Devroye & Kruszewski 1995, *IPL* 56:95–99, DOI 10.1016/0020-0190(95)00114-R | uniform binary (Catalan) trees | `E S_n = log₄ n + O(1)`; Thm 4 `P(|S_n − log₄ n| > x) ≤ D/4^x` (abstract, p. 95) | trees | fetched | [pub] |
| 24 | Esparza, Luttenberger & Schlund 2014, LATA, LNCS 8370:1–13, DOI 10.1007/978-3-319-04921-2_1 | every tree | "We can show that for any tree `t`: `pathwidth(t) − 1 ≤ S(t) ≤ 2 · pathwidth(t)`", `S` the minimum over roots (p. 11; **stated, no proof**) | trees | fetched | [pub, stated without proof] |
| 25 | Fomin & Høie 2006 citing Ellis, Sudborough & Turner 1994 | every tree on `n ≥ 3` vertices | Thm 3 `pw(T) ≤ log₃ n` (p. 193) | trees | yes | [pub] |
| 26 | Do, Erde & Kang 2024, *JGT* 106:273–295 | `G(n, (1 + ε)/n)` | §5 p. 14: "For large enough `ε`, the fact that rank- and tree-width are vertex-Lipschitz functions imply that these parameters are tightly concentrated about their mean, for example using the Azuma–Hoeffding inequality … for smaller `ε` it is not clear if these parameters are concentrated in a range of values of size `o(ε³ n)`" | — | yes | [pub] |
| 27 | Nikoletseas, Raptopoulos & Spirakis 2008, *TCS* 381 | RIG `G(n, m, p)`, `mp = α log n`, `m ≥ n` | Thm 9: greedy independent set `≥ (1 − β) n / (np)`, `(1 − β) n (1 − e^{−b})`, `(1 − β) n` as `np → ∞`, `→ b`, `→ 0` | RIG: `pw ≤ n − α` [derived] | yes | [pub] |
| 28 | Liu, Wang & Xu 2015, *J. Comb. Optim.* 29(3):531–540, DOI 10.1007/s10878-013-9704-y | sparse random `k`-uniform hypergraphs | "large hypertree width" whp; threshold and constants not read | — | no | [pub, abstract] |
| 29 | Tavakoli 2012, M.Sc. thesis, Memorial University (hdl 20.500.14783/2131) | `G(n, p)`, `p` fixed | fast search number of almost all graphs: upper `(9/20 + ε) m` (Def. 3.4, §3.3), lower via `s_fast ≥ |V_odd|/2` (Thm 3.9–3.10, OCR unclear); nothing on node or edge search of random graphs | — (different parameter) | fetched | [pub, OCR] |
| 30 | Bollobás 1985, *Random Graphs*, Academic Press, p. 374 | `G(n, p)` | cited by 3 for bandwidth; **not obtained again** (archive.org item `randomgraphs0000boll` is lending-only; Google Books quota exhausted) | — | no | UNVERIFIED |

Not found, after searching for them specifically: any theorem on the
pathwidth, vertex separation or node search number of random cubic or random
`d`-regular graphs; of random recursive trees, binary search trees or random
tries; of uniform random planar graphs or random planar maps; of preferential
attachment graphs beyond Gao's Theorem 3; any published concentration
statement for pathwidth; any searching-number theorem on `G(n, p)` other than
29; any cavity or replica prediction for a width.

---

## 3. Notes by topic

### 3.1 Vertex separation of `G(n, p)` stated directly

**Turner 1986** (read in full; §2 and §3). The random-graph part is Theorems
2.1–2.2 for bandwidth, both by the empty-pair count of Lemma 2.2,
`P(bw ≤ n − 2k) ≤ [(en/k)(1 − p)^{k/2}]^{2k}`; the survey and the first-moment
report already record them. What this pass adds is the heuristics part. Turner
leaves `G(n, p)` at once: "even the most trivial algorithms (for example, the
algorithm that always outputs the identity layout) can produce layouts having
bandwidth close to `β(G)` as `n` gets large. If one is to make meaningful
distinctions among algorithms based on their probable performance, some other
probability distribution is required" (p. 4), and moves to the planted model
`Γ_n(β, p)` (graphs with a planted layout of bandwidth `≤ β`, each eligible
edge present with probability `p`). There: Theorem 2.3 `bw > β − 4 log_b β`
a.a.s. for `ln n ≪ β < n`; the Conjecture "`bw = β`" for `c ln n ≤ β ≤ n − c ln n`;
Theorem 3.1 the Cuthill–McKee level algorithms give `LEVEL(G) < (1 + ε)(3 − p) bw`;
Theorem 3.2 the *modified* level algorithms give `2 bw + O(log n)`; §4 a specific
one (MLA1) within `1 + ε`. **None of this is about `G(n, c/n)`, and none of it
is about vertex separation.** It is the only analysis of a BFS-type layout on a
random model that this pass found, and it is for bandwidth on a planted model.

**Díaz–Petit–Serna–Trevisan 2001** (read in full). The quoted core, p. 252:
"in a `(ε, γ, c_n)`-mixing graph, it is the case that `δ(i, φ, G) ≥ i − εn`
for every `εn < i < (1 − ε)n`. This is because there cannot be `εn` vertices
on the left of `i` and `εn` vertices on the right of `i` without any
connection. Thus `VS(φ, G) ≥ δ(⌊n/2⌋, φ, G) ≥ ⌊n/2⌋ − εn ≥ (1/2 − ε)n − 1`."
The mixing condition needs `c_n ≥ 3(1 + ln 3)(εγ)^{−2}` with `ε < 1/6`
(Definition 2, p. 248), so the bound is vacuous below `c ≈ 227` as the
first-moment report says. The paper's own summary of its content, p. 247:
"any algorithm computing a feasible layout, no matter how good or bad, will
perform rather well on random graphs, pointing out that such an evaluation
may be unworthy for layout problems." The survey (DPS 2002 §8.1, p. 334) repeats
that sentence and adds the Luczak–McDiarmid `ln 4` threshold for edge
bisection; **Petit's 2011 addenda explicitly exclude new random-graph results**
(p. 2), so the ACM survey's §8 is the last word of that group on `G(n, p)`.

**Cheung & Girardet** (arXiv 1710.10339, read in full; journal version
*Open J. Discrete Math.* 10(1):13–30, 2020, Crossref-resolved, not read). The
survey had this at [pub, abstract] with "full text refused". The content:
for cutwidth and edge bisection they need `p_n = Ω(n^{−c})` with `c < 1/2`
(Theorem 5, Lemma 6 `MINCW ≥ n² p_n (1 − δ)/4`), and for vertex separation and
vertex bisection `c < 1` (Theorem 11). Lemma 12, p. 10, is the statement:

> Let `p_n` satisfy `p_n = Ω(n^{−c})`, `c < 1` … Then for all `ε > 0, δ > 0`
> there exists an `N` such that for all `n ≥ N`,
> `P[MINVS(G_n) ≥ (1 − δ)n − 1] > 1 − ε`.

The proof sets `ε_n = n^{−s}` with `0 < s < 1 − c`, takes the prefix of a
layout at position `(1 − ε_n) n`, bounds by Hoeffding the number of prefix
vertices with no neighbour among the `ε_n n` suffix vertices, and unions over
the `C(n, ε_n n)` prefixes. It is the empty-pair first moment with the prefix
moved from `n/2` to `(1 − ε_n) n`, which is exactly the variant the
first-moment report §4 attributes to "their own argument with the prefix at
`(1 − ε)n`" as a derivation. **So that variant is published; the sentence in
`reports/random_graph_first_moment.md` §4 should cite Cheung–Girardet for it.**
What remains unpublished is unchanged: at `p = c/n` the union over
`C(n, ε n)` prefixes costs `H(ε) n` nats against a gain of `c ε (1 − ε) n`,
which is why their argument needs `p n → ∞` and says nothing at constant `c`;
the entropy count with `H(a, a, 1 − 2a) − c a²`, the threshold `4 ln 2`, and
`β*(c)` are not there. Their Theorem 11 is the approximation statement
(`GAP_VS < 1 + δ` whp, because `MAXVS ≤ n − 1`). Note the direction of the
information: **`pw(G(n, p)) = (1 − o(1)) n` whp for every `p ≥ n^{−1+ε}`** is a
published theorem (Lemma 12), stronger in range than Perarnau–Serra's
`n − O(√(n/p))` for tree-depth but weaker than the survey's Theorem B
(`n − (4 + ε) log_b n` at constant `p`) in the second-order term.

**Mareček 2009** (fetched, read): the model is `G(n, 1/2)` only (p. 4); Theorem 2
gives rank-width `Ω(n)` a.a.s. from the Blömer–Karp–Welzl rank bound on random
`GF(2)` matrices, and Corollaries 2–5 transfer to tree-, branch-, clique- and
NLC-width via the standard inequalities. Pathwidth is not mentioned, no
constant is given, and the author notes Kloks (treewidth) and Johansson
(NLC-width) as the only prior random-graph width results he knows.

**Gao 2012** (held): beyond the three theorems, the paper's remark on p. 3
records that in 2012 "the treewidth of the random graph `G(n, m)` with
`1/2 < m/n < 1` is unknown"; Lee–Lee–Oum settled it the same year. His
Hoeffding–Azuma argument (Lemma 3.3, p. 10) is a tail bound on a weighted count
of small tree components inside a balanced partition, not a concentration
statement for the width itself.

### 3.2 Random regular and random cubic graphs

Three facts and one unresolved number.

1. **Upper, deterministic, applies to random cubic.** Fomin–Høie Theorem 5
   (p. 193): "For any `ε > 0`, there exists an integer `n_ε` such that for
   every graph `G` with maximum vertex degree at most three and with
   `|V(G)| > n_ε`, `pw(G) ≤ (1/6 + ε)|V(G)|`", proved from the Monien–Preis
   bisection (their Theorem 2) and Lemma 4 (`pw ≤ max{|X|, n/3 + 1 + (2/3) log₃ n + 1}`
   for any vertex subset `X` in a graph of maximum degree 3). Edwards–McDermid
   recover it as `g_{1/6}(3) = 1/6` and use it as the base case of their
   reduction; Kneis et al. give `1.5 n / 5.769 = 0.260 n` for cubic graphs,
   worse. **Nothing better than `n/6` is published for *random* cubic
   graphs**, although the random case is where one would expect it: the
   edge bisection of random cubic graphs is at most `0.139822 n` (Lichev–Mitsche
   Thm 1.1) against Monien–Preis's `n/6` worst case, and Fomin–Høie's
   construction turns a bisection of size `b` into a path decomposition of
   width about `b + o(n)` (the proof of Theorem 5 goes through `|∂(V_i)| ≤
   (1/6 + ε/2) n`, i.e. the number of boundary *vertices*, which for cubic
   graphs is at most the number of cut edges). So **`pw(G_{n,3}) ≤ 0.1399 n + o(n)`
   whp [derived: Lichev–Mitsche's bisection fed through Fomin–Høie's
   construction]**, and the non-rigorous Monte Carlo upper bound Lichev–Mitsche
   report would give less. Check before quoting: it needs the Fomin–Høie
   argument with a balanced but not exactly equal bipartition, which Lemma 4
   allows (`|V_i| ≤ n/2 + 1` enters only through the `n/3` term), and
   Lichev–Mitsche's bisection is exact (`||V_1| − |V_2|| ≤ 1`).
2. **Lower, whp.** The survey's `pw(G_{n,3}) ≥ 0.0721 n` from Kolesnik–Wormald's
   `A_3(1/2) = 0.14420` (vertex isoperimetric number at `u = 1/2`, Theorem 1 and
   Table 2, pp. 5 and 24; read) stands; it is the only explicit constant and it
   is derived, not stated by them. The edge-bisection route is weaker: an active
   prefix vertex of a cubic graph has at most 3 suffix neighbours, so
   `pw ≥ bw/3 ≥ 0.0344 n` from Lichev–Mitsche [derived].
3. **Perarnau–Serra Corollary 4.6** (pp. 11–12) gives linear tw for random
   `d`-regular graphs with `tw ≥ (α(d)(n − 1) − 3)/(α(d) + 3)` and
   `α(d) = (d − O(√d))/2` from the Friedman–Kahn–Szemerédi eigenvalue bound;
   with the explicit `λ₂ ≤ 2√(d − 1) + o(1)` one could make `α(3)` numeric, but
   `(d − 2√(d−1))/2 = (3 − 2.83)/2 = 0.086` and then `α/(α + 3) · (1/3)` from
   the balance is about `0.009`, below Kolesnik–Wormald by a factor 8
   [derived, rough]. Not worth pursuing.
4. **The unresolved number.** Fomin–Høie's concluding remark (p. 195):
   "Bezrukov et al. [3] … showed that there are 3-regular graphs with the
   bisection width at least `0.082n`. … It can be shown that the result of
   Bezrukov et al. also yields the lower bound `0.082n` for pathwidth of graphs
   with maximum degree three. It is an interesting challenge to reduce the gap
   between `0.082n` and `0.167n`." The step from a bisection width `b` to
   `pw ≥ b` is not written there, and for a general cubic graph the elementary
   argument gives only `pw ≥ b/3` (item 2). If a factor-1 transfer holds for
   every cubic graph, Lichev–Mitsche would give **`pw(G_{n,3}) ≥ 0.1033 n` whp**,
   above Kolesnik–Wormald's `0.0721`. **UNVERIFIED**, and the right question for
   whoever reads Bezrukov et al. §5 (held) in full: their `0.082n` is a bound on
   the *bisection* width via the level structure of a bisection (p. 157), and
   the pathwidth claim is Fomin–Høie's. Beside it, a misprint to record:
   Bezrukov et al. p. 157 attribute to Kostochka–Melnikov a random-cubic
   bisection bound of `n/4.95 ≈ 0.202n`, while Lichev–Mitsche (p. 1), who
   improve that bound, give it as `0.10101 n`; `0.202` is twice `0.101`, so
   one of the two counts edges differently or one is a misprint. This bisection
   history is loop0011 item 01's territory; it is recorded here only because
   the pathwidth transfer depends on it.

For random `d`-regular graphs in general: lower `A_d/2` from Kolesnik–Wormald
(`0.1448, 0.2510, 0.3569` at `d = 4, 6, 10`), upper `g_{1/6}(d)` from
Edwards–McDermid (`1/3, 23/45 = 0.511, 0.685`) [both derived from pub], and no
source states either for pathwidth.

### 3.3 Degree-based deterministic bounds, read and evaluated

**Kneis, Mölle, Richter & Rossmanith 2009.** Closed at SIAM, no repository
copy (Unpaywall, Semantic Scholar, CORE checked); the WG 2005 version
("Algorithms based on the treewidth of sparse graphs", LNCS 3787:385–396) is
closed too. The abstract via Crossref: "We present a bound of `m/5.769 + O(log n)`
on the pathwidth of graphs with `m` edges. Respective path decompositions can
be computed in polynomial time. … If we agree to accept a slightly larger
bound of `m/5.217 + 3`, we even obtain path decompositions with a rather
simple structure: all bags share a large set of common nodes." Edwards–McDermid
(p. 19) restate it as `(13/75 + o(1)) m + O(log n)` and attribute the same
`13/75` for *treewidth* to Scott & Sorkin (arXiv cs/0604080, open). `13/75 =
1/5.769`. On `G(n, c/n)`: `c/11.538`.

**Fomin, Gaspers, Saurabh & Stepanov 2009**, Lemma 1 (preprint p. 5, read):
`pw(G) ≤ n₃/6 + n₄/3 + 13n₅/30 + 23n₆/45 + n_{≥7} + εn` for `n > n_ε`, with a
polynomial-time decomposition. **The survey's §1.4 has the coefficient list
wrong** (`n_{≥6}` with coefficient 1): degree 6 carries `23/45` and only degree
`≥ 7` carries 1. Lemma 2 (p. 6) is a treewidth bound, `tw ≤ (m − n)/3 + εn`
for connected graphs with `m/n ∈ [1.5, 2]`, which on `G(n, c/n)` would read
`(c/2 − 1)/3` for `3 ≤ c ≤ 4` if the giant component were the whole graph; it
is not, and the bound is for treewidth, so it is not entered in the table.

**Edwards & McDermid 2015** (accepted manuscript, read; the only one of the
three not already partly in the survey). Their function `g_α` is defined by
`g_α(2) = 0`, `g_α(3) = α`, `n g_α(n) = (n − 2) g_α(n − 1) + g_α(n − 2) + 1`,
extended by linear interpolation (p. 6); properties 2–4 (p. 6): `g_α(d) =
1 − (4 − 3α)/(d + 1) + O(d^{−3})`, non-decreasing for `α ≤ 1/2`, with
non-increasing increments for `1/6 ≤ α ≤ 3/10` (so concave on the integers).
At `α = 1/6`: `1/6, 1/3, 13/30, 23/45, 359/630, 1553/2520, …` — the first four
are FGSS's coefficients, which is their point: "each constant `β_d` [of
Gaspers's computer search to degree 17] is an approximation to `g_{1/6}(d)`"
(p. 19). The statements:

> **Corollary 5.2** Let `G` be a graph, and `r(G)` be the reduced graph of `G`.
> Then `pw(G) ≤ Σ_{v ∈ V(r(G))} g_{1/6}(d_{r(G)}(v)) + τ(|V(G)|) + O(log |V(G)|)
> = Σ_{d ≥ 3} g_{1/6}(d) n_d + o(|V(G)|)`.
>
> **Theorem 5.3** Let `G` be a graph of average degree `d ≥ 2`, with `n`
> vertices and `m` edges. Then if `G` is connected, or `d ≥ 5`,
> `pw(G) ≤ (g_{1/6}(d) + o(1)) n = (2 g_{1/6}(d)/d + o(1)) m = (1 − (7/2)/(d + 1) + O(1/d³)) n`.

(`r(G)` removes degree-0/1 vertices, suppresses degree-2 vertices and
parallel edges until the minimum degree is 3 or the graph is empty, p. 7;
`τ(n) = o(n)` is Fomin–Høie's error term.) Since reduction never raises a
surviving vertex's degree and `g_{1/6}` is non-decreasing, the sum over `r(G)`
is at most the sum over the degree histogram of `G` itself, which is how the
displayed equality is meant. They also note (p. 20) that Golovnev & Kutzkov's
results give `pw ≤ (1 − 4ε ln d / d) n` for `d_ε ≤ d ≤ n/(1 + ε)`, "for very
large average degrees … a better bound" — a published `1 − Θ(ln d / d)`
pathwidth upper bound, which the survey's §1.4 reached only through `n − α`.

**Evaluation on `G(n, c/n)`** [derived; the script is reproduced at the end of
this subsection]. The degree distribution of `G(n, c/n)` is Poisson(`c`) in
the limit and `g_{1/6} ≤ 1`, so `pw/n ≤ Σ_d P_c(d) g_{1/6}(d) + o(1)` whp. By
concavity this is below Theorem 5.3's `g_{1/6}(c)` (Jensen), which is why the
histogram form is the one to use:

| `c` | E–M Cor 5.2 (Poisson) | E–M Thm 5.3 `g(c)` | FGSS Lemma 1 | Kneis `c/11.54` | `1 − ln(1+c)/c` | cyclomatic | **survey §7(a) UB** | fitted slope (§7(d)) | `β*(c)` |
|---|---|---|---|---|---|---|---|---|---|
| 1.1 | 0.022 | — | — | 0.095 | 0.326 | **0.0006** | 0.0006 | — | 0 |
| 1.5 | 0.045 | — | — | 0.130 | 0.389 | **0.037** | 0.037 | — | 0 |
| 2 | **0.085** | 0 (not applicable) | 0.086 | 0.173 | 0.451 | 0.162 | 0.162 | 0.040 | 0 |
| 2.5 | **0.132** | 0.083 (n/a) | 0.138 | 0.217 | 0.499 | 0.343 | 0.217 | — | 0 |
| 3 | **0.183** | 0.167 (n/a) | 0.196 | 0.260 | 0.538 | 0.554 | 0.260 | 0.099 | 0.0087 |
| 4 | **0.285** | 0.333 (n/a) | 0.329 | 0.347 | 0.598 | — | 0.347 | 0.158 | 0.0613 |
| 5 | **0.378** | 0.433 | 0.470 | 0.433 | 0.642 | — | 0.433 | — | 0.1175 |
| 6 | **0.458** | 0.511 | 0.605 | 0.520 | 0.676 | — | 0.520 | 0.268 | 0.1706 |
| 8 | **0.576** | 0.616 | 0.813 | 0.693 | 0.725 | — | 0.693 | 0.360 | 0.2628 |
| 10 | **0.656** | 0.685 | 0.926 | 0.867 | 0.760 | — | 0.760 | 0.415 | 0.3371 |
| 12 | **0.711** | 0.732 | 0.975 | 1.040 | 0.786 | — | 0.786 | — | 0.3973 |
| 16 | **0.782** | 0.795 | 0.998 | — | 0.823 | — | 0.823 | — | 0.4882 |
| 20 | **0.826** | 0.834 | 1 | — | 0.848 | — | 0.848 | — | 0.5535 |
| 30 | 0.884 | 0.887 | 1 | — | **0.886** | — | — | — | — |
| 50 | 0.930 | 0.931 | 1 | — | **0.921** | — | 0.921 | — | 0.7606 |

("n/a" marks `c < 5` where Theorem 5.3 needs connectivity, which `G(n, c/n)`
lacks; Corollary 5.2 has no such condition. The `c = 2` Theorem 5.3 entry is
`g(2) = 0`, a reminder that the average-degree form is meaningless there.)

What the table says:

- **Edwards–McDermid is the best published upper bound at every `c` from 2
  to about 32**, by 0.08–0.10 over the survey's best at `c = 3–6` and by
  0.10–0.12 at `c = 8–10`; `1 − ln(1 + c)/c` takes over where
  `ln(1 + c) > 3.5 c/(c + 1)`, i.e. `c ≳ 32`, and asymptotically E–M's
  `1 − 3.5/c` loses to the independence bound's `1 − 2 ln c / c` and to
  Golovnev–Kutzkov's `1 − 4ε ln c / c`. Below `c = 2` the cyclomatic bound is
  still better (0.0006 and 0.037 against 0.022 and 0.045).
- **Against the fitted slopes** the ratio upper/slope falls from the survey's
  1.8–2.6 to **1.85, 1.80, 1.71, 1.60, 1.58** at `c = 3, 4, 6, 8, 10`; the
  absolute gap above the slope (0.08, 0.13, 0.19, 0.22, 0.24) is now of the
  same order as the gap below it to `β*` (0.09, 0.10, 0.10, 0.10, 0.08). The
  slope sits at 46–48% of the way from `β*` to the E–M bound at every
  `c ≥ 4`, and at 52% at `c = 3`.
- **Against `β*`**, the provable sandwich at `c = 3, 6, 10` is now
  `[0.009, 0.183]`, `[0.171, 0.458]`, `[0.337, 0.656]`; the upper/lower ratio
  is 21, 2.7, 1.9 where the survey's table had 30, 3.0, 2.3.
- FGSS Lemma 1 beats Kneis at `c ≤ 4` and loses from `c = 5`; neither is ever
  the best once E–M is in. For **random cubic graphs** all three degree bounds
  collapse to `1/6`.

**Evaluation on the clique-cover cells of `reports/excess_phase_diagram.md`
§7.5** [derived, crude]. In the uniform model a customer lies in
Poisson(`μd`) patterns of size `d`, so its MOSP-graph degree is at most
`(d − 1)` times that count (equality when its patterns share no other
customer); since `g_{1/6}` is non-decreasing, `Σ_k P_{μd}(k) g_{1/6}((d − 1)k)`
is an upper bound on E–M's bound for the cell, and the true E–M value is
lower by the overlap. Beside the analysed `β⁺ = min(β⁺_BFS, 1 − α⁺_pc)` and
`β*` of §7.5:

| `(d, μ)` | `e` | E–M (crude) | `β⁺` (§7.5) | `β*` | E–M − `β⁺` | certified slope `b` |
|---|---|---|---|---|---|---|
| (2, ½) | 0.5 | 0.017 | 0.000 | 0.000 | +0.017 | 0.005 |
| (3, ½) | 1.0 | 0.190 | 0.429 | 0.000 | **−0.239** | 0.048 |
| (4, ½) | 1.5 | 0.409 | 0.566 | 0.072 | **−0.157** | 0.151 |
| (6, ½) | 2.5 | 0.696 | 0.716 | 0.244 | −0.020 | 0.323 |
| (8, ½) | 3.5 | 0.831 | 0.802 | 0.398 | +0.029 | 0.463 |
| (10, ½) | 4.5 | 0.898 | 0.855 | 0.522 | +0.043 | 0.585 |
| (2, 1) | 1.0 | 0.085 | 0.296 | 0.000 | **−0.211** | 0.038 |
| (3, 1) | 2.0 | 0.425 | 0.596 | 0.140 | **−0.171** | 0.200 |
| (4, 1) | 3.0 | 0.660 | 0.709 | 0.286 | −0.049 | 0.348 |
| (6, 1) | 5.0 | 0.861 | 0.830 | 0.513 | +0.031 | 0.577 |
| (8, 1) | 7.0 | 0.928 | 0.889 | 0.661 | +0.039 | 0.706 |
| (10, 1) | 9.0 | 0.957 | 0.922 | 0.757 | +0.035 | 0.795 |
| (2, 2) | 2.0 | 0.285 | 0.551 | 0.121 | **−0.266** | 0.167 |
| (3, 2) | 4.0 | 0.686 | 0.731 | 0.355 | −0.045 | 0.409 |
| (4, 2) | 6.0 | 0.839 | 0.821 | 0.525 | +0.018 | 0.568 |
| (6, 2) | 10.0 | 0.937 | 0.904 | 0.724 | +0.033 | 0.755 |
| (8, 2) | 14.0 | 0.967 | 0.940 | 0.825 | +0.027 | 0.847 |
| (10, 2) | 18.0 | 0.980 | 0.959 | 0.880 | +0.021 | 0.894 |

A published bound with no construction of ours in it is **below the
project's analysed upper constant on every cell with `e ≤ 3`** (by 0.16–0.27
on the ridge and the sparse flank: `(3, ½)`, `(4, ½)`, `(2, 1)`, `(3, 1)`,
`(2, 2)`), level with it at `e = 2.5–3`, and 0.02–0.04 above it at `e ≥ 3.5`,
where the pattern-count greedy of §7.3 remains the best provable construction.
On the ridge cell `(2, 1)` the provable sandwich around the certified slope
0.038 becomes `[0, 0.085]` instead of `[0, 0.296]`; at `(3, 1)` it is
`[0.140, 0.425]` around 0.200. The §7.6 finding 2 sentence "the analysed
constructions are informative — within 0.1 of the truth's bracket — only at
`e ≥ 14`" is therefore about *our* constructions; a literature bound is
informative on the ridge too. With the overlap correction (the exact degree
distribution of the uniform model's MOSP graph, which `learning/first_moment.py`
or the §7.2 recursion can supply) the E–M numbers would fall further.

*Script (seconds):*

```python
from math import exp, log, lgamma
N = 2500; g = [0.0]*(N+1); g[3] = 1/6
for n in range(4, N+1): g[n] = ((n-2)*g[n-1] + g[n-2] + 1)/n        # Edwards–McDermid g_{1/6}
pois = lambda lam, k: exp(k*log(lam) - lam - lgamma(k+1))
em_gnp  = lambda c: sum(pois(c, d)*g[d] for d in range(3, 200))      # Cor 5.2 on Poisson(c) degrees
em_cell = lambda d, mu: sum(pois(mu*d, k)*g[(d-1)*k] for k in range(1, 250) if (d-1)*k >= 3)
fgss    = lambda c: sum(pois(c, d)*w for d, w in ((3, 1/6), (4, 1/3), (5, 13/30), (6, 23/45))) + sum(pois(c, d) for d in range(7, 200))
```

### 3.4 Random geometric graphs: a sharp constant exists

The survey had the RGG results through the ACM survey's Theorems 8.4–8.6 only
("factor arbitrarily close to 1" for BANDWIDTH and VERTSEP). Petit's thesis
(the ALCOM-FT TR-01-157 PDF is the thesis; the journal version is Díaz,
Penrose, Petit & Serna, *J. Algorithms* 39:78–116, 2001) states the constant.
Theorem 5.13 (p. 152): for `r_n → 0` with `n r_n² / log n → ∞` and `n`
independent uniform points in `[0, 1]²`, with probability 1,

> `lim minbw(G_n)/(n r_n) = 1`, `lim minvs(G_n)/(n r_n) = 1`, `lim minvb(G_n)/(n r_n) = 1`,

with `minsc/(n² r_n) ∈ [5/6, 1]` and `mincw/(n² r_n³) ∈ [3/(8√2), 1]` in the
limit. The lower bound is Theorem 5.10 (p. 149), `minvs(G) ≥ (1 − 6√ε) n r_n`
on `ε`-good graphs (every `γ r_n × γ r_n` box holding `(1 ± γ) γ² a n` points),
by an isoperimetric inequality on the dissection; the upper bound is the
*projection* layout, ordering points by `x`-coordinate, whose vertex
separation is the number of points in a vertical strip of width `r_n`. So on
dense RGGs **vertex separation is asymptotically a strip count, the sharp
constant is 1, and a BFS-free geometric layout attains it** — the one random
model in this literature where `vs` has a limit theorem. Subcritically Theorem
5.17 (p. 172) gives `vs = Θ(log n / log log n)` with implicit constants. The
MOSP side is unaffected (customer graphs are not geometric), but Appendix E's
"what is known" should say that the sharp-constant question is answered for
RGGs and open for `G(n, c/n)`.

### 3.5 Random trees: typical pathwidth is between `(1/2) log₄ n` and `log₄ n`

Three published pieces and one short derivation.

- **Brandenberger, Devroye & Reddad 2021** (read): for a critical
  Galton–Watson tree with offspring variance `σ² ∈ (0, ∞)` conditioned to
  have `n` vertices, the Horton–Strahler number of the root (leaves at 0)
  satisfies `H(T_n)/log₂ n → 1/2` in probability (p. 2; Theorems 4 and 5 are
  the two halves). The class contains uniform labelled trees (Poisson(1)
  offspring), uniform binary trees (Catalan), uniform plane trees (geometric
  offspring) and uniform `k`-ary trees; the paper lists the earlier Catalan
  results of Flajolet–Raoult–Vuillemin, Kemp, Meir et al. (`log₄ n + O(1)`)
  and Drmota–Prodinger (`t`-ary trees, concentrated around `log₄ n`).
- **Devroye & Kruszewski 1995** (read): Catalan trees, `E S_n = log₄ n + O(1)`
  and `P(|S_n − log₄ n| > x) ≤ D/4^x` (Theorem 4); this settles the survey's
  "content UNVERIFIED" entry.
- **Esparza, Luttenberger & Schlund 2014**, p. 11 (read): "For trees, the
  search number coincides with the better known pathwidth … let the Strahler
  number `S(t)` of an undirected tree be the minimal Strahler number of all
  the directed trees obtained by choosing a node as root … We can show that
  for any tree `t`: `pathwidth(t) − 1 ≤ S(t) ≤ 2 · pathwidth(t)`." No proof is
  given and the leaf convention is not stated; the inequality checks on the
  complete binary tree of height `h` (`S = h`, `pw = ⌈h/2⌉`), the complete
  ternary tree (`S = h`, `pw = h`), a path and `K_{1,3}`.
- **[derived]** Re-rooting changes the Strahler number by at most 1: a
  complete binary tree of height `h` embedded at root `r` has two root
  branches of height `h − 1`, and a new root `r'` lies in at most one of them,
  so `H_{r'} ≥ h − 1`; hence `H(T_n) − 1 ≤ S(T_n) ≤ H(T_n)`. With the ELS
  inequality, **whp `(H − 1)/2 ≤ pw(T_n) ≤ H + 1`, i.e.
  `pw(T_n)/log₂ n ∈ [1/4 − o(1), 1/2 + o(1)]`**, or between `(1/2) log₄ n`
  and `log₄ n` up to `O(1)`, for every conditioned critical finite-variance
  Galton–Watson family. This extends the survey's binary-tree remark to Cayley
  trees and plane trees and rests on a stated-not-proved inequality
  (UNVERIFIED proof, checked on examples). Against the sharp worst case
  `tb(N) = ⌊log₃((6N + 3)/5)⌋ ≈ 0.631 log₂ N` of `TreeBound.lean`, the typical
  pathwidth of a random tree is at most `0.5 log₂ n`, so random trees sit
  20–60% below the extremal ternary trees. The constant inside `[1/4, 1/2]` is
  open; the lower end is what the ternary-subtree argument of survey §2 also
  gives.
- **Random recursive trees, binary search trees, random tries**: nothing on
  pathwidth, vertex separation or Strahler number was found (Devroye–Kruszewski
  1996 treat the Strahler number of random *tries*, `H_n/log n → 1/log(1/min(p, 1−p))`
  in probability, a different model). The height of these trees is
  `Θ(log n)`, so `pw = O(log n)`, and `pw → ∞` since every fixed tree occurs;
  the constant is not in the literature we found.

### 3.6 Scale-free, intersection, hypergraph and planar models

- **Barabási–Albert.** Gao's Theorem 3 (p. 3): "Let `G_S(n, m)` be the
  Barabási–Albert random graph. For any `m ≥ 12`, there is a constant `β > 0`
  such that `lim P{tw(G_S(n, m)) > βn} = 1`"; the proof (§5) is a first moment
  over balanced triples with the attachment probabilities, `β` implicit, and
  `m ≥ 12` an artefact (numerical constant `0.9425` on p. 20). Nothing for
  `m < 12` and nothing for pathwidth; Katona's "width of a scale-free tree"
  (*J. Appl. Probab.* 42:839–850, 2005) is the profile width `n/√(π log n)`,
  not a width parameter.
- **Random intersection graphs.** Gao's Theorem 2 reads `p ≥ 2/m` for
  `m = n^α`, any `α > 0` (the survey's "`p = c/m`, `c > 2`"). Nikoletseas,
  Raptopoulos & Spirakis (held) give greedy independent sets of size
  `(1 − β) n/(np)`, `(1 − β) n (1 − e^{−b})`, `(1 − β) n` according as
  `np → ∞`, `→ b`, `→ 0`, under `mp = α log n`, `m ≥ n` (Theorem 9), so
  `pw ≤ n − α(G)` is explicit there [derived]; the regime `m = Θ(n)`,
  `p = Θ(1/n)` of the MOSP generators is not theirs.
- **Random hypergraphs.** Liu, Wang & Xu 2015 prove "large hypertree width"
  whp for sparse random `k`-uniform hypergraphs (abstract only; closed). The
  related *Phase transition of tractability in CSP and Bayesian network
  inference* (arXiv 1212.2485) treats the treewidth of the clique graph of a
  random `d`-uniform hypergraph — the random clique-cover graph the MOSP side
  cares about — with a linear-treewidth threshold in `m/n` and a lower
  threshold `1/(d(d − 1))` below which the clique graph has treewidth `≤ d + 1`;
  read in a search snippet only, UNVERIFIED, and worth reading beside
  `reports/excess_phase_diagram.md` §0.2's three lines.
- **Random planar graphs and maps.** Nothing found on treewidth or pathwidth
  whp; the deterministic `O(√n)` is all. Hyperbolic random graphs as in the
  survey.

### 3.7 Concentration

No published statement that the pathwidth of `G(n, p)` concentrates. Do,
Erde & Kang's §5 remark (p. 14, quoted in table row 26) is the only written
form for tree- and rank-width, and it is a remark, not a theorem: vertex
exposure plus Azuma–Hoeffding gives `|pw − E pw| = O(√n)` whp since removing a
vertex changes `pw` by at most 1, and the same for edge exposure since adding
an edge changes it by at most 1. The survey's §1.3 says this already; this
pass confirms that nobody has written it down for pathwidth, that the
`o(ε³ n)` window question is open (DEK), and that the pilot's variance growth
(survey §7(d): 1.0 → 2.2 from `n = 20` to `60` at `c = 3`) has no theory to
compare with.

### 3.8 Graph searching on random graphs

Searched for: search number, node search number, mixed search, connected
search, sweeping, "searchers" with `G(n, p)`, Erdős–Rényi, "almost all
graphs". Found: nothing for the node or edge search number. The one
random-graph searching result is Tavakoli's 2012 M.Sc. thesis on the *fast*
search number (a searcher may traverse each edge once; Dyer, Yang & Yaşar
2008), with an upper bound `(9/20 + ε) m` for almost all `G(n, p)` at fixed
`p` and a lower bound from `s_fast ≥ |V_odd|/2`; its Theorem 3.10 is garbled
in the OCR and is recorded as [pub, OCR]. Since `ns = pw + 1` (Kinnersley;
Ellis–Sudborough–Turner), every pathwidth statement above is a node-search
statement, and the searching literature has not stated any of them for a
random model. Esparza et al.'s "for trees, the search number coincides with
the better known pathwidth" is the only sentence in that direction found
outside the project.

---

## 4. What changes

**`reports/random_graph_pathwidth_survey.md`.**

- §7(a), the UB column: replace at every `c` from 2 to 20 by the
  Edwards–McDermid Poisson value with source "E–M Cor 5.2": `c = 2`: 0.162 →
  **0.085**; 2.5: 0.217 → **0.132**; 3: 0.260 → **0.183**; 4: 0.347 →
  **0.285**; 5: 0.433 → **0.378**; 6: 0.520 → **0.458**; 8: 0.693 → **0.576**;
  10: 0.760 → **0.656**; 12: 0.786 → **0.711**; 16: 0.823 → **0.782**;
  20: 0.848 → **0.826**. Rows `c ≤ 1.5` (cyclomatic) and `c ≥ 50`
  (independence) stand. The sentence "The upper/lower gap is a factor of 2–40
  throughout the interesting range" becomes a factor of about 2–20, and the
  `c → ∞` row gains Golovnev–Kutzkov's published `1 − 4ε ln c / c` beside the
  derived `1 − (2 − o(1)) ln c/c`.
- §1.4 upper bounds: correct FGSS's coefficients (`23n₆/45 + n_{≥7}`, not
  `n_{≥6}`); add Edwards–McDermid's closed form (removing the "closed form was
  not read (UNVERIFIED)"); Kneis et al. stays [pub, abstract] but the abstract
  is now read through Crossref and the `13/75` is confirmed by E–M.
- §7(d): the comparison line "below every upper bound by a factor of 1.8–2.6"
  becomes 1.6–1.85, and "Kneis's `c/11.54` is the closer upper bound at
  `c ≤ 6` and the independence bound at `c ≥ 8`, but neither is within 0.2 of
  the fit" becomes: E–M is the closer bound at every `c`, within 0.08 at
  `c = 3` and 0.24 at `c = 10`.
- §7(e)'s table of upper bounds on the pilot graphs should gain an E–M column
  (per-graph, from the actual degree histogram); not computed here, since it
  needs the pilot's graphs and the rule is no computation beyond closed forms.
- §4 random regular: unchanged window `0.0721 n ≤ pw(G_{n,3}) ≤ n/6`; add the
  derived `≤ 0.1399 n` via Lichev–Mitsche through Fomin–Høie (check before
  quoting), the `0.082n` transfer question, and the Kostochka–Melnikov
  discrepancy.
- §4 random trees: replace "No theorem stated directly for pathwidth was
  found" by the BDR + ELS window `[1/4, 1/2] log₂ n` for all conditioned
  critical GW families, Devroye–Kruszewski now read, ELS now read (inequality
  stated without proof).
- §4 RGG: add the sharp constant `minvs/(n r_n) → 1` (Theorem 5.13) and that
  the projection layout attains it.
- §3 dense: add Cheung–Girardet Lemma 12 as the published
  `pw = (1 − o(1)) n` for every `p ≥ n^{−1+ε}`.
- §6 related parameters: Cheung–Girardet from [pub, abstract; full text
  refused] to [pub], with the statement.
- "Not verified": Kneis (still abstract), Edwards–McDermid (now read),
  Devroye–Kruszewski (now read), Esparza et al. (now read, proof absent),
  Cheung–Girardet (now read), Bollobás p. 374 (still unobtainable; the
  archive.org scan `randomgraphs0000boll` is borrowable with an Open Library
  account, which is a route a person can take).

**`reports/random_graph_first_moment.md` §4.** The sentence "Their own
argument gives `(1 − 2ε)n` if the prefix position `(1 − ε)n` is used instead
of `n/2`" should credit Cheung & Girardet (2017/2020), Lemma 12, who do exactly
that with `ε = n^{−s}` and reach `(1 − o(1)) n` for `p = Ω(n^{−c})`, `c < 1`.
The list of what is not published (entropy form, any `β(c)` at `p = c/n`, the
`4 ln 2` threshold, the asymptotics) is unchanged by anything found here.

**The paper's Appendix E, "What is checked, and what is known".** Three
sentences change. (i) The best *published* upper bound on `pw(G(n, c/n))/n` is
Edwards–McDermid's degree-sequence bound, `0.183, 0.458, 0.656` at
`c = 3, 6, 10`, not the edge-count bound; the sandwich around the measured
slopes is `[β*, E–M]` with the slope near its midpoint. (ii) A sharp constant
for vertex separation is known for one random model, dense random geometric
graphs (`vs ~ n r_n`), and for none of `G(n, c/n)`, random regular graphs or
random clique covers. (iii) For random trees the typical pathwidth is
`Θ(log n)` with the constant in `[1/4, 1/2]` (base 2), against the worst case
`0.63`; the extremal trees of `TreeBound.lean` are atypical by a constant
factor. The closing claim "we found no prior statement of an explicit
lower-bound constant at `p = c/n`" survives this pass.

**The loops.** For loop0011 (separator first moment), items 05–07 and 12: the
figure "`β` against `c`" and the cover grid should carry the Edwards–McDermid
upper bound as a published line, because on the ridge and the sparse flank it
is the tightest provable upper constant there is (`(2, 1)`: 0.085 against
`β⁺ = 0.296`), and item 12's paragraph on where the sandwich is loose should
say the upper side is now a literature bound at `e ≤ 3` and a project
construction at `e ≥ 3.5`. The crude cell numbers above need the overlap
correction before they go in a figure (one line of the §7.2 recursion). Item
01's bisection reading should resolve the Kostochka–Melnikov `0.101` versus
`0.202` discrepancy in passing, since the pathwidth transfer of §3.2 item 4
depends on which it is. For `reports/excess_phase_diagram.md` §7.6 finding 2,
the qualifier "analysed constructions" should be read as "our analysed
constructions".

---

## 5. To fetch

In the style of `literature/MISSING.md`; nothing was added to `literature/`.

- **Edwards, K. & McDermid, E.** (2015). A general reduction theorem with
  applications to pathwidth and the complexity of Max 2-CSP. *Algorithmica*,
  72(4), 940–968. DOI 10.1007/s00453-014-9883-7. **Accepted manuscript is
  open** at the Dundee repository (`/ws/portalfiles/portal/6880233/edwmcd_2_.pdf`;
  the `/files/...` URL returns 403), saved as `/tmp/lit_random/em2.pdf`.
  Should be filed: it is the best published upper bound on `pw(G(n, c/n))`
  and the source of the `g_{1/6}` recurrence.
- **Kneis, J., Mölle, D., Richter, S. & Rossmanith, P.** (2009). A bound on
  the pathwidth of sparse graphs with applications to exact algorithms.
  *SIAM J. Discrete Math.*, 23(1), 407–427. DOI 10.1137/080715482 — SIAM
  paywall; no repository copy (Unpaywall, CORE, Semantic Scholar). WG 2005
  version LNCS 3787:385–396, DOI 10.1007/11604686_34, also closed. Abstract
  held via Crossref.
- **Brandenberger, A.M., Devroye, L. & Reddad, T.** (2021). The
  Horton–Strahler number of conditioned Galton–Watson trees. *Electron. J.
  Probab.*, 26, 1–29. DOI 10.1214/21-EJP678. Open (EJP, arXiv 2010.08613);
  saved as `/tmp/lit_random/bdr_2010.08613.pdf`.
- **Devroye, L. & Kruszewski, P.** (1995). A note on the Horton–Strahler
  number for random trees. *IPL*, 56(2), 95–99. DOI 10.1016/0020-0190(95)00114-R.
  Open on the author's page; saved.
- **Esparza, J., Luttenberger, M. & Schlund, M.** (2014). A brief history of
  Strahler numbers. LATA 2014, LNCS 8370, 1–13. DOI 10.1007/978-3-319-04921-2_1.
  Open on the authors' page; saved. The 2016 revised version
  (`latarevised16.pdf`, same server) was not read and may contain the proof
  of the pathwidth inequality.
- **Cheung, K.K.H. & Girardet, P.D.** (2020). Improved approximation of
  layout problems on random graphs. *Open J. Discrete Math.*, 10(1), 13–30.
  DOI 10.4236/ojdm.2020.101003. arXiv 1710.10339 saved; the journal version
  (open access) was not read.
- **Díaz, J., Penrose, M.D., Petit, J. & Serna, M.** (2001). Approximating
  layout problems on random geometric graphs. *J. Algorithms*, 39(1), 78–116.
  DOI 10.1006/jagm.2000.1149 — Elsevier paywall; the statements were read in
  Petit's thesis (UPC, 2001; ALCOM-FT TR-01-157, open, saved as
  `/tmp/lit_random/dpps_rgg_tr.pdf`).
- **Golovnev, A. & Kutzkov, K.** (2014). New exact algorithms for the
  2-constraint satisfaction problem. *TCS*, 526, 18–27. DOI 10.1016/j.tcs.2014.01.010
  — paywall; read as restated by Edwards–McDermid.
- **Kostochka, A.V. & Melnikov, L.S.** (1992). On bounds of the bisection
  width of cubic graphs. *Proc. 4th Czechoslovakian Symp. on Combinatorics,
  Graphs and Complexity*, 151–154; and (1993) On a lower bound for the
  isoperimetric number of cubic graphs, *Probabilistic Methods in Discrete
  Math.*, 251–265. Not online; needed only to settle the `0.101`/`0.202`
  discrepancy (loop0011 item 01).
- **Monien, B. & Preis, R.** (2006). Upper bounds on the bisection width of
  3- and 4-regular graphs. *J. Discrete Algorithms*, 4(4), 475–498.
  DOI 10.1016/j.jda.2005.12.009 — paywall; the MFCS 2001 version LNCS 2136.
  The root of Fomin–Høie's `n/6`.
- **Bollobás, B.** (1985). *Random Graphs*, Academic Press, p. 374. Still not
  obtained: archive.org holds a lending-only scan (`randomgraphs0000boll`),
  borrowable with an Open Library account; Google Books API quota exhausted
  again. By its citation context (DPS 2002 p. 334, beside Turner) it is
  Turner's bandwidth statement for `p ≫ 1/n`.
- **Liu, T., Wang, C. & Xu, K.** (2015). Large hypertree width for sparse
  random hypergraphs. *J. Comb. Optim.*, 29(3), 531–540.
  DOI 10.1007/s10878-013-9704-y — Springer paywall; abstract only.
- **Gao, Y.** (2012), **Tavakoli, Y.** (2012) and **Mareček, J.** (2009) are
  held or saved; Tavakoli's PDF (20 MB, OCR) is in `/tmp/lit_random/`.

---

## 6. Not verified, or not read in full

- Kneis et al. 2009: abstract only (Crossref); `13/75` confirmed only through
  Edwards–McDermid's restatement.
- Esparza–Luttenberger–Schlund's `pw − 1 ≤ S ≤ 2 pw`: stated in the paper
  without proof or leaf convention; checked here on four small families only.
  The random-tree window of §3.5 rests on it.
- The re-rooting step `|H_r − H_{r'}| ≤ 1` and the random-cubic upper bound
  `0.1399 n` via Fomin–Høie's construction: [derived], unrefereed.
- Fomin–Høie's "`0.082n` for pathwidth" from Ramanujan bisection: the transfer
  is asserted, not written; the consequence for random cubic graphs via
  Lichev–Mitsche is UNVERIFIED.
- Kostochka–Melnikov's random-cubic bisection constant: `0.10101 n`
  (Lichev–Mitsche) against `n/4.95 ≈ 0.202 n` (Bezrukov et al.); not resolved.
- Edwards–McDermid Corollary 5.2's displayed equality `Σ_{r(G)} = Σ_{d ≥ 3} g n_d + o(n)`:
  read as "at most", justified in §3.3 by monotonicity of `g`; the paper's
  own `n_d` is not defined on that line.
- The Poisson evaluation of E–M and FGSS assumes the degree histogram of
  `G(n, c/n)` converges in `L¹` to Poisson(`c`), standard; the cover-cell
  evaluation ignores pattern overlaps and is an upper bound on the bound.
- Cheung–Girardet: arXiv v1 read; the 2020 journal version may differ.
- Tavakoli 2012: OCR text; Theorem 3.10's statement not legible.
- Golovnev–Kutzkov, Monien–Preis, Kostochka–Melnikov: as restated by others.
- Phase transition of tractability (arXiv 1212.2485): search snippet only.
- Bollobás 1985 p. 374: not obtained.
- Random recursive trees, binary search trees, random planar graphs, node
  search on random graphs: absence of results is absence in what was searched
  (arXiv, Semantic Scholar, DBLP, Google Scholar snippets, the held PDFs), not
  a proof of absence.
