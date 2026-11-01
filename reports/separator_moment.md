# Counting events, not witnesses: the separator first moment

*Ralph loop0011, executing `reports/separator_moment_plan.md`, started
2026-11-01. The loop asks whether the first-moment lower bound on the
pathwidth of random graphs and on the optimum of random MOSP instances
moves when the count runs over the **event** a narrow layout forces
instead of over the **witnesses** of that event. Sections are the items,
in order; each states its size range, its regenerate command, its kill
verdict and what it does not claim. §0 (the summary) is written by item
12.*

## The three events, and the notation

A layout of vertex separation `≤ k` on `n` vertices gives, at the prefix of
size `t = ⌈(n − k)/2⌉`, a prefix `A`, an inactive suffix `R` and an active
suffix `S` with no `A–R` edge (`EmptyPair.lean`,
`exists_empty_pair_of_layout`). Padding `S` to exactly `k` vertices from
`R`:

    |A| = t,   |R| = N − t,   |S| = k,   N = n − k,   A ∪ R ∪ S = V,   no A–R edge.

Three counts, three events, in this document's words:

1. **The pair count** (on record): the number `X` of ordered pairs `(A, R)`
   of the forced sizes with no `A–R` edge. `P(pw ≤ k) ≤ E[X]`
   (`FirstMoment.lean`, `weightedSum_graphsOfPathwidthLe_le`;
   `CliqueCoverMoment.lean`, `prob_coversOfMospValueLe_le`). Its constant
   is `β*(c)` on `G(n, c/n)` and `β*(d, μ)` on random clique covers.
2. **The separator count**: the number of `k`-sets `S` such that `G − S`
   has a *balanced empty bipartition*, `E_bip = {the components of G − S
   can be grouped into two sides of sizes t and N − t}`. Its relaxation is
   `E_relax = {no component of G − S has more than max(t, N − t) vertices}`,
   which `E_bip` implies and which is strictly weaker (plan §0, correction
   3). `P(pw ≤ k) ≤ C(n, k) · P_N(E_bip) ≤ C(n, k) · P_N(E_relax)`, with
   `P_N` the law of `G(N, p)`.
3. **The closed-pair count**: pairs with `S = N(A) ∩ N(R)`, the
   minimal-separator form, sides at least the forced sizes, `|S| ≤ k`.
4. **The weighted count**: `Y = Σ_P 1[P empty] / Z(P)` for any `Z ≤ X`,
   so that `Y ≥ 1[X > 0]`.

Throughout, `q(x) = 1 − e^{−cx}` is the probability that a vertex of
`G(n, c/n)` has a neighbour in a set of `xn` vertices (asymptotically);
`c′ = c(1 − β)` is the mean degree of `G − S` when `k = βn`, so that
`G − S` is `G(N, c′/N)` exactly; `H` is the entropy in nats; a "nat per
vertex" is a rate on the scale of `n` unless the scale `N` is named.
Conversion: the pair exponent's slope at `β*` is `3.3–3.4` per unit of `β`
at `c = 6–10` (3.9 at `c = 4`, 5.5 at `c = 3`; `rate_preview.log`), so a gain
of `g` nats per vertex of `n` is `g / 3.3` in `β` there.

---

## 1. Literature: who counts separators, and what the inner probability is known to be (item 01, 2026-11-01)

**Question (G of the brief).** Has anyone counted balanced *vertex*
separators (or bisections, or cuts) of sparse random graphs with an inner
probability finer than the product over edges, for pathwidth or any width
or cut parameter? What is the large-deviation rate for the giant
component's lower tail and for the cluster sizes of `G(N, c/N)`? Did a
representative or locally optimal count ever move a first-moment cut
constant, and by how much?

**Stop rule (the item's one).** *No held or fetched paper states the
separator first moment for pathwidth or vertex separation of `G(n, c/n)`
with an exact inner probability and a constant.* The nearest things are
three, and items 05–06 compare against all three rather than re-derive
them: (i) Do, Erde & Kang (2024) count separators `S` of a spanning tree's
vertex set and bound the number of balanced separations per `S` by
`2^{Δ(T)|S|}` — the separator count with a *deterministic* inner bound and
no component law, used to reach the threshold `c = 1` with a constant
`Ω(ε³/log(1/ε))`, not to sharpen a constant (§1.3, row DEK); (ii) Kolesnik
& Wormald (2014) count, in the pairing model of random `d`-regular graphs,
sets `U` *together with* their vertex boundary `sn` and edge boundary `yn`,
with the inner count exact up to `n^{O(1)}` (a coefficient extracted by a
saddle point), and say it is "best possible for a direct application of
the first moment method" — the exact inner probability for a *single*
vertex cut, no bipartition of the rest, no `G(n, c/n)` (row KW); (iii) the
inner probability of the *relaxed* event `E_relax` is known exactly at the
exponential scale, as a corollary of the large-deviation principle for the
largest component of `G(N, c′/N)` (O'Connell 1998, restated and extended by
Puhalskii 2005 and by Andreis, König & Patterson 2021), and nobody we found
has put it into a width or cut first moment (§1.4). So the brief's
one-line description — "a better estimate of the inner probability, not a
new object" — is half right: the object (count `S`, bound the bipartitions
of `G − S`) is in print once, with a crude inner bound; the inner
probability of the relaxed event is in print as a large-deviation rate,
with no width application; the inner probability of `E_bip` itself, and
the closed-pair and weighted counts for widths, we found nowhere (§1.5).

**Size range.** Not applicable (reading). The one computation is a check
of a quoted formula (§1.4, `rate_check.py`) and a preview for item 06
computed from that quotation alone (`rate_preview.py`), both asymptotic,
both superseded by items 05–06.

**Regenerate.** None. The text extracts in
`reports/scratch/separator_moment/lit/*.txt` are `pdftotext -layout` of the
PDFs in `literature/` named in §1.1; the check and the preview:

    nice -n 19 python3 -I reports/scratch/separator_moment/rate_check.py   > reports/scratch/separator_moment/rate_check.log
    nice -n 19 python3 -I reports/scratch/separator_moment/rate_preview.py > reports/scratch/separator_moment/rate_preview.log

### 1.1 What was read, what was fetched, what was not obtained

Held before this item and read in full (the `literature/` file names are
the item's): Díaz–Diner–Serna–Serra 2022 (arXiv 2211.03206; published as
*J. Comput. System Sci.* 2024, DOI 10.1016/j.jcss.2024.103550, "On minimum
vertex bisection of random d-regular graphs", Crossref), Lichev–Mitsche
2023 (*Electron. J. Combin.*, DOI 10.37236/11085; 26,000 words, read in
full for §§1–3 and the first-moment sections §§4–5, the upper-bound §6
skimmed), Coja-Oghlan–Cooley–Kang–Skubch 2017 (*Theory Comput.*, DOI
10.4086/toc.2017.v013a008), Perarnau–Serra 2014 (*Discrete Appl. Math.*,
DOI 10.1016/j.dam.2012.10.031), Lee–Lee–Oum 2012 (*J. Graph Theory*, DOI
10.1002/jgt.20620), Do–Erde–Kang 2024 (*J. Graph Theory*, DOI
10.1002/jgt.23081), Bezrukov–Elsässer–Monien–Preis–Tillich 2004 (*Theoret.
Comput. Sci.*, DOI 10.1016/j.tcs.2004.03.059), Feige–Hajiaghayi–Lee 2008
(*SIAM J. Comput.*, DOI 10.1137/05064299X; introduction and definitions,
for the vocabulary), Behrisch 2007 (*Electron. J. Combin.*, DOI
10.37236/935), Lagerås–Lindholm 2008 (*Electron. J. Combin.*, DOI
10.37236/885), Díaz–Petit–Serna–Trevisan 2001 (*Discrete Math.*, DOI
10.1016/S0012-365X(00)00278-8), Kolesnik–Wormald 2014 (*SIAM J. Discrete
Math.*, DOI 10.1137/120891265; **arXiv 1311.6555**, not 1109.0689 as the
item says — that number is a paper on online payment systems), Gao 2012
(*Discrete Appl. Math.*, DOI 10.1016/j.dam.2011.10.013; §§1–3), the
two-page previews of Gao 2006 (COCOON, DOI 10.1007/11809678_25) and of
Kloks 1994 (LNCS 842, DOI 10.1007/BFb0045375 — **the held preview is
chapter 12, on cocomparability graphs of bounded dimension, and contains
nothing about random graphs**; his first moment is cited here only as
restated by Do–Erde–Kang p. 1, Gao 2006 p. 226, Gao 2012 §3 and
Perarnau–Serra p. 4 and 9), and `reports/scratch/first_moment/lit/turner1986.txt`
(Turner 1986, *SIAM J. Comput.* 15, read by the checker of
`reports/random_graph_first_moment.md` §4; its Lemmas 2.1–2.2 re-read here).

Fetched into `literature/` this item (open copies; nothing executed from
a download; text extracted with `pdftotext`):

| file | what it is | DOI of the published version (Crossref) |
|---|---|---|
| `2017-Dembo-Montanari-Sen-Extremal-Cuts-Sparse-Random-Graphs-AOP-arXiv.pdf` | arXiv 1503.03923v2 | *Ann. Probab.* 45(2), 10.1214/15-AOP1084 |
| `2021-Andreis-Konig-Patterson-LDP-All-Cluster-Sizes-Sparse-Erdos-Renyi-Graph-RSA-preprint.pdf` | the authors' revision of 19 August 2020, from W. König's WIAS page | *Random Structures Algorithms* 59(4) 522–553, 10.1002/rsa.21007 |
| `2005-Puhalskii-Stochastic-Processes-Random-Graphs-AOP-arXiv.pdf` | arXiv math/0402183v1 (59 pp.) | *Ann. Probab.* 33(1) 337–412, 10.1214/009117904000000784 — **the item's venue "Stochastic Processes and their Applications" is wrong** |
| `2003-Diaz-Serna-Wormald-Computation-Bisection-Width-Random-d-Regular-Graphs-ALCOMFT-TR-03-44.pdf` | the ALCOM-FT technical report (Aarhus mirror, PostScript converted), the preprint of the 2007 paper; its analysis is explicitly "not rigorous" and sketches how to make it so | *Theoret. Comput. Sci.* 382(2) 120–130 (2007), 10.1016/j.tcs.2007.03.003 — the journal version is **not held** (Elsevier, blocked) |
| `2012-Lampis-Local-Improvement-Gives-Better-Expanders-arXiv.pdf` | arXiv 1211.0524v1; not in the brief, fetched because Kolesnik–Wormald cite it as the locally-optimal count that improves Bollobás, which is what the brief attributes to Díaz–Serna–Wormald (§1.6) | no journal version found in Crossref |

Not obtained, recorded in `literature/MISSING.md`: **O'Connell 1998**
(*Probab. Theory Related Fields* 110, 277–285, DOI 10.1007/s004400050149;
Springer paywall — Semantic Scholar lists a "bronze" PDF at the publisher
that the publisher does not serve without a login; cited here only through
Puhalskii's and Andreis–König–Patterson's restatements), **Luczak &
McDiarmid 2001** (*Random Structures Algorithms* 18(1) 31–38, DOI
10.1002/1098-2418(200101)18:1<31::AID-RSA3>3.0.CO;2-1; Wiley paywall; the
LSE repository record 17554 says "full text not available"; cited through
Lichev–Mitsche p. 2, Coja-Oghlan et al. p. 4, Dembo–Montanari–Sen p. 1 and
Do–Erde–Kang §1.3), **Bollobás 1988** (*European J. Combin.* 9(3) 241–244,
DOI 10.1016/S0195-6698(88)80014-3; Elsevier, blocked; its content is
restated in detail by Kolesnik–Wormald §§1, 2, 7 and Lampis §§1, 3, which
re-derive its bound), **Díaz–Serna–Wormald 2007** (journal version; the
2003 report is held), and **the random-graph chapter of Kloks 1994**.

### 1.2 Table A — who counts what

"Inner probability" is the probability, for one fixed object, that it is
what is counted; "count" is what the union bound runs over. Page numbers
are of the held file.

| source | parameter; random model | object counted | count | inner probability | constant obtained | where |
|---|---|---|---|---|---|---|
| Turner 1986 | bandwidth; `G(n, p)`, `p` fixed | empty pair `(V₁, V₂)`, `|V₁| = |V₂| = k` (Lemma 2.1: `bw ≤ n − 2k` forces one) | `(en/k)^{2k}` | product over edges, `(1 − p)^{k²}` exact | `bw > n − 4 log_b n` a.s. (Thm 2.1); nothing at `p = c/n` | lines 109–142 of the extract |
| Díaz–Petit–Serna–Trevisan 2001 | vertex separation, vertex bisection; `G(n, c_n/n)` | pairs `(A, B)`, `|A|, |B| ≥ εn`, with `e(A, B)` far from its mean ("mixing", Def. 2) | `3^n` | two-sided Chernoff on `e(A, B)` (Lemma 2, pp. 249–250) | `MINVS ≥ (½ − ε)n − 1` for `c ≥ 3(1 + ln 3)(εγ)^{-2}` (Lemma 3 (g5), p. 252); vacuous below `c ≈ 227` as stated | pp. 248–252 |
| Kloks 1994 (as restated) | treewidth; `G(n, d/n)` | balanced `k`-partition `(A, S, B)`, `|S| = k + 1`, `⅓ ≤ |A|, |B| ≤ ⅔` of the rest | over triples | product over edges `(1 − p)^{|A||B|}` (as restated) | linear tw for `d ≥ 2.36` (`m/n > 1.18`), `r(d) → 1` | DEK p. 1; Gao 2006 p. 226; PS p. 4, 9; chapter not held |
| Gao 2006 (preview) | treewidth; `G(n, m)` | "a new combinatorial construct to make better use of the first moment" and a model with replacement | — | — | `m/n > 1.081` (`c > 2.162`) | p. 227; the construct is not in the two held pages |
| Gao 2012 | treewidth; `G(n, m)` with replacement | **`d`-rigid** balanced partitions: no connected set of `≤ d` vertices of the larger side `B` is a component of `G[B]` (Def. 3.2; Lemma 3.1: tw `≤ l` forces a balanced partition that is rigid or nearly equal-sided) | over triples, split into `J₁` (near-equal) and `J₂` (rigid) | product over edges `φ₁(t) = (1 − 2t + 2t² + 2tβ)^{cn}` **times** `P(d-rigid | partition) ≤ e^{−r(1 + g)n/c}` by Hoeffding–Azuma on a weighted count of small tree components of `G[B]` (Thm 4, §3.1) | `m/n ≥ 1.073` (`c ≥ 2.146`); the plain count "more refined" gives 1.083 | pp. 3, 7–8, 13–15 |
| Gao 2012, Thm 2 | treewidth; random intersection graph `G_I(n, m, p)` | balanced partitions | over triples | product over the `m` items, `[(1−p)^{|A|} + (1−p)^{|B|} − (1−p)^{|A|+|B|}]^m` (his (4.22)), the clique-cover count; a factor dropped in the next line (`REPORT_generator.md` §3.2) | linear tw for `p ≥ 2/m` | §4 |
| Perarnau–Serra 2014 | treewidth; `G(n, c/n)` | balanced `k`-partitions (Kloks's Lemma 2.1) | `3^n` | product over edges, `(1 − p)^{|A||B|} ≤ (1 − p)^{2f²n²/9}` | `tw ≥ (1 − f(c))n` for `f > √(9 ln 3/(2c))`, `c > 4.94` (pp. 5–6); and, by a different argument, linear tw for every `c > 1` with `(αδ)²/(9e³c²)` (§4.3) | pp. 4–6, 9–11 |
| Lee–Lee–Oum 2012 | rank-width, hence treewidth; `G(n, c/n)`, `c > 1` | **not a first moment**: the `α`-edge-expander `H` of linear order `δn` inside the giant (Benjamini–Kozma–Wormald, Thm 4.1), a balanced partition of `H` (Lemma 2.1), `rank ≥ (#ones)/M²` (Lemma 4.3) | — | — | `rw ≥ αδ n/(6M²)`, constants implicit | §4, pp. 6–9 |
| **Do–Erde–Kang 2024** | treewidth, rank-width; `p = (1 + ε)/n` | **separators `S` of `G[V(T)]`** for a spanning tree `T` of a linear-size tree component, with the balanced separations per `S` bounded deterministically: "any subset `S ⊆ V(T)` splits `T` into at most `Δ(T)|S|` components, and hence there are at most `2^{Δ(T)|S|}` separations whose separator is `S`" (§1.3, p. 4; §3) — the technique of Luczak–McDiarmid 2001 | over `S` | a fixed partition of `V(T)` is a balanced separation with exponentially small probability, by sprinkling | `tw = Ω(ε³n/log(1/ε))` (Thm 1.5), `rw = Ω(ε³n/log³(1/ε))` (Thm 1.4); every `c > 1`; `tw, rw = Θ(ε³n)` in the weakly supercritical window (Thm 1.6, by a 3-regular kernel) | pp. 3–4, §3 |
| **this repository** | pathwidth; `G(n, c/n)` | empty pairs at exact sizes `t`, `t − 1` | trinomial `C(n, t)C(n − t, t − 1)` | product over edges `(1 − p)^{t(t−1)}` exact | `β*(c)`: 0.0087, 0.061, 0.171, 0.263, 0.337 at `c = 3, 4, 6, 8, 10`; threshold `4 ln 2`; Lean | `random_graph_first_moment.md`; `FirstMoment.lean`, `FirstMomentAsymptotics.lean` |
| this repository | MOSP; random clique covers of given sizes | empty pairs | trinomial | product over patterns of `avoidCount(s)/C(n, s)` exact | `β*(d, μ)`; threshold excess 1 | `CliqueCoverMoment.lean`; `clique_cover_moment/` |
| Bollobás 1988 (as restated by KW §§1, 2, 7 and Lampis §3) | edge isoperimetric number `i_E(d)`; random `d`-regular, pairing model | sets `U`, `|U| = un`, with `|∂_E U| = yn` | `C(n, un)` | **configuration-model exact**: `C(dun, yn)C(dn − dun, yn)(yn)! M(dun − yn)M(dn − dun − yn)/M(dn)` (KW (23), "essentially contained in [5]") | `i_E(d) ≥ d/2 − √(d ln 2)` for large `d`; `i_E(3) > 2/11`, `i_E(4) > 11/25`, `i_E(5) > 18/25` | KW pp. 3–4, 18–19 |
| **Kolesnik–Wormald 2014** | vertex isoperimetric number `i_V(d)` and, at `u = ½`, vertex bisection; random `d`-regular, pairing model | sets `U`, `|U| = un`, **with** `|∂_V U| = sn` and `|∂_E U| = yn` | `C(n, un)C(n − un, sn)` | **configuration-model exact up to `n^{O(1)}`**: the number `C_{n,s,y}` of ways to pick `yn` points in `sn` groups of `d` with each group hit, estimated by `x^{−yn}((x+1)^d − 1)^{sn}` at the saddle point `x₀` of (7), which "leads to just as good final results as using the precise formula" ((5)–(8), pp. 7–8); the union bound over `O(n²)` values of `(s, y)` | Thm 1: `i_V(d) ≥ A_d(½) = 2s_d`, `s_d` the least positive root of `(2^d − 1)s = 2^{d/2+s−1}(1 − 2s)^{½−s}s^s`; `A_d(½) = 0.144, 0.290, 0.409, 0.502, 0.575, 0.632, 0.677, 0.714` at `d = 3, …, 10` (Table 2); Cor. 2: `i_V(d) ≥ 1 − 2/d + O(log d/d²)`; "best possible for a direct application of the first moment method" (after Lemma 6, p. 10) | pp. 7–17 |
| Lampis 2012 | edge expansion of random `Δ`-regular | **locally optimal** sets (swapping one vertex across cannot lower the expansion, so every vertex has at most `Δ/2` neighbours across) with their out-degree profiles `(s, s′)` | `C(n, u)` times the profiles | configuration-model exact per profile (§3, `P(s, s′)`), maximised over profiles (Lemma 2: the maximiser is binomial) | improved `i_E(Δ)` for `Δ ≥ 4`, Table 1 (§1.4 here); Thm 2: Bollobás's `√(ln 2)` is not the right coefficient | pp. 3–8 |
| Lichev–Mitsche 2023 | bisection width of random 3-regular; configuration model | minimum bisections with a structural characterisation (2-cores, forbidden winning sets, two types), then **graphs** containing such a bisection, divided by an overcounting factor (Lemma 5.6; "we may divide by the corresponding overcounting factor", p. 4) | over skeletons and labellings | configuration-model exact | `0.103295n ≤ bw ≤ 0.139822n` (Thm 1.1); type-one bisections `≤ 0.1069n` excluded by the plain structural count (§4), the overcount division is what the binding type-two case needs (§5) | pp. 1–4, 24–38 |
| Díaz–Serna–Wormald 2003/2007; Díaz–Diner–Serna–Serra 2022/2024 | bisection width; vertex bisection width; random `d`-regular | **not first moments**: priority-greedy and ball-growing algorithms analysed by the differential-equation method | — | — | upper bounds; bisection `b/n = 0.5028, 0.6674, 0.8502, 1.0386, 1.2317, 1.4278` at `d = 5, …, 10` (DSW Table 1); vertex bisection `α` (fraction of the red half with a neighbour across) `0.581, 0.610, 0.657, 0.656, 0.720, 0.881, 0.838` by the DEM and `0.466, 0.559, 0.626, 0.679, 0.721, 0.754, 0.778` experimentally at `d = 4, …, 10`, against KW's `0.290, 0.409, 0.502, 0.575, 0.632, 0.677, 0.714` (DDSS Table 2, p. 16) | DSW pp. 7–9; DDSS pp. 15–17 |
| Coja-Oghlan–Cooley–Kang–Skubch 2017 | bisection width; planted bisection `G(n, p₊, p₋)`, `d₊ − d₋ ≥ c√(d₊ ln d₊)` | **not a first moment**: `n^{−1} bis(G) → φ(p*)`, the skewed fixed point of Warning Propagation on a two-type Galton–Watson tree (Thm 1.1) | — | — | the exact constant, as a fixed point | pp. 3–5 |
| Dembo–Montanari–Sen 2017 | min/max bisection, max-cut; `G(n, [γn])` and `γ`-regular, `γ → ∞` | **not a first moment**: interpolation to the Sherrington–Kirkpatrick model | — | — | `mcut/n = γ/2 − P*√(γ/2) + o_γ(√γ)` (Thm 1.2; `γ/4 − P*√(γ/4)` regular, Thm 1.5), `P* = 0.76321 ± 0.00003` by Parisi's formula | pp. 1–4 |
| Bezrukov et al. 2004 | bisection width; deterministic (level structure of a bisection, Laplacian `λ₂`) | — | — | — | `bw ≥ 0.082n` for 3-regular and `0.176n` for 4-regular Ramanujan graphs; no random-graph statement (it misquotes Kostochka–Melnikov's `i_E(3) ≥ 1/4.95` as a bisection width `0.202n`, p. 158; Lichev–Mitsche give the bisection form `0.10101n`) | pp. 156–158 |
| Feige–Hajiaghayi–Lee 2008 | vocabulary only | a vertex separator is a triple `(A, B, S)`, balanced if `|A|, |B| ≤ 2|V|/3`; its sparsity `π(S)/(min(π(A), π(B)) + π(S))` | — | — | `O(√log n)` approximation; treewidth `O(k√log k)` | pp. 1–3 |

Two counts that *are* over separators, for the record: Do–Erde–Kang's,
above, and the deterministic reduction every treewidth count rests on —
Robertson & Seymour's `tw ≥ sep_{½}(G) − 1`, where a `(k, ½)`-separator is
a `k`-set `S` with **every component of `G − S` of size at most half of
`|V ∖ S|`** (DEK Lemma 2.1, with Lemma 2.2 turning it into a `⅓–⅔`
balanced partition). That is exactly this loop's relaxed event `E_relax`,
in the treewidth literature since 1986 as the thing a separator must
satisfy; what is counted there is still the partition.

### 1.3 Table B — the rates

| statement | rate function, hypotheses | where | the corollary this loop needs |
|---|---|---|---|
| **The largest component of `G(n, c_n/n)`, `c_n → c > 0`, satisfies an LDP at scale `n`** on `[0, 1]`: `P(β^n/n ≈ u) = e^{−n I_c^β(u)(1+o(1))}`, with `I_c^β` a good rate function. In the form O'Connell gives it (Puhalskii's remark after Cor. 2.5): `I_c^β(u) = k K_c(u) + L_c(ku)` for `u ∈ [x_k, x_{k−1}]`, `x₀ = 1`, `x_k` the root of `x/(1 − e^{−cx}) = 1 − kx`, `K_ρ(u) = u log(ρu/(1 − e^{−ρu})) − ρu²/2`, `L_c(u) = (1 − u) log(1 − u) + (c − log c)u − cu²/2` (his (2.13)–(2.14)); `I_c^β(0) = L_c((1 − 1/c)⁺)`. Not convex. The most probable configuration with largest component `nu`: one giant if `u ≥ 1 − 1/c`, otherwise `⌊(1 − 1/c)/u⌋` components of size `≈ nu` plus one more. | Puhalskii 2005, Cor. 2.4(3) (p. 8 of the arXiv version), attributed to O'Connell 1998 Thm 3.1 "which has a misprint"; Thm 2.1 is the joint LDP for the number of components, all giant sizes and their excess edges; Cor. 2.2 the LDP for the sequence of giant sizes `U^n/n` in `S₁` with `I_c^U(u) = Σ K_c(u_i) + L_c(1 − (1/c) ∨ Σ u_i)` | **Yes, with the exact statement**: `[0, ½]` is closed, so `lim sup (1/N) log P(largest component of G(N, c′/N) ≤ N/2) ≤ −inf_{u ≤ ½} I_{c′}^β(u)`. Checked numerically on the quoted formula (`rate_check.log`): `I` vanishes at the law-of-large-numbers point `u* = 1 − ρ` to `10⁻¹⁶` at every `c` tried, and `inf_{u ≤ ½} I = I(½) > 0` **iff `c′ > 2 ln 2`** (`u* = ½` exactly at `c′ = 2 ln 2 = 1.3863`). Values of `I_{c′}^β(½)`: `0.036, 0.144, 0.183, 0.380, 0.595, 0.832, 1.316, 1.810` at `c′ = 2, 2.772, 3, 4, 4.98, 6, 8, 10`. So **the relaxed separator count has threshold `2 ln 2`**, as the plan predicted conditionally on this result — now a cited one, not a conjecture, up to the LDP being asymptotic |
| **All cluster sizes**: the pair (microscopic empirical measure `Mi^{(N)}`, macroscopic point measure `Ma^{(N)}`) of `G(N, t_N/N)`, `t_N → t`, satisfies an LDP at speed `N` with rate `I(Λ, α; t) = I_Mi(Λ; t) + I_Ma(α; t) + (1 − c_Λ − c_α)(t/2 − log t)`, `I_Mi(Λ; t) = Σ_k λ_k log(k! t λ_k/(e k^{k−2})) + c_Λ(1 + t/2 − log t)`, `I_Ma(α; t) = ∫ [x log(x/(1 − e^{−tx})) + (t/2)x(1 − x)] α(dx)` (Thm 1.1); contractions: the microscopic part (Cor. 1.2; always optimal to put the rest in one giant), the macroscopic part (Cor. 1.3), the mesoscopic total mass `J_Me(c; t) = (1 − c) log((1 − c)t) − (1 − c)t/2 + t/2 − log t` (Cor. 1.4), the total-mass phase transition with `J_Mi(c; t)` explicit and `J_Ma(c; t) = J_Mi(1 − c; t)` (Thm 1.5) | Andreis–König–Patterson 2021, §1.2–1.3 (pp. 4–8 of the preprint); §1.4 says O'Connell's two LDPs are contractions of theirs and that Puhalskii covers the macroscopic part by a different route, "it would require some work to analytically check that it is identical to ours" | The event `E_bip` is a variational problem over `(Λ, α)` under the constraint that the atoms of `α` plus the microscopic mass can be grouped into sides of sizes `t` and `N − t`; with microscopic components of sizes 1 and 2 at positive density under the tilt (the minimiser's `Λ*` is Borel, (1.13)) the exact-size grouping should cost nothing at the exponential scale once no atom exceeds `½` — **a plausible reading, not a theorem, and item 06's job**. If it holds, the rate of `E_bip` equals that of `E_relax` |
| Random intersection graphs: with `m = βn` auxiliary vertices and incidence probability `γ/n` (`α = 1`), mean degree `μ = βγ²`; `μ > 1` gives a unique giant of size `(1 − ρ + o_p(1))n`, `ρ` the least root of `ρ = g(ρ)`, `g(s) = exp(βγ(e^{γ(s−1)} − 1))` (compound Poisson offspring), second largest `O(log n)` (Thm 2); with `m = n^α`, `α ≠ 1`, `c = p²mn`: giant `(1 − ρ)n` for `α > 1`, `(1 − ρ)√(cmn)` for `α < 1`, `ρ = e^{c(ρ−1)}` (Behrisch Thm 1) | Lagerås–Lindholm 2008 pp. 2–3; Behrisch 2007 pp. 2–3 | **Laws of large numbers only; no LDP for the giant of a random intersection graph or of a random clique cover was found.** Item 07 has the giant's typical size (the onset line) from these, and must derive or compute the lower tail itself |
| Bisection width of `G(n, c/n)` is `0` whp for `c < ln 4` and `Ω(n)` for `c > ln 4`: the giant exceeds `n/2` iff `c > 2 ln 2` | Luczak–McDiarmid 2001 (not held), as restated by Lichev–Mitsche p. 2, Coja-Oghlan et al. p. 4, Dembo–Montanari–Sen p. 1 | the same threshold as the relaxed separator count's, for the same reason; their technique (a spanning tree bounds the cuts per separator) is the one Do–Erde–Kang reuse |

### 1.4 Table C — representative and locally optimal counts, and what they bought

| source | what is merged / restricted | parameter, model | constant before → after | in the units of the gap to the truth or to the best upper bound |
|---|---|---|---|---|
| Gao 2012 | `d`-rigid balanced partitions: partitions from which no small component of the larger side can be moved (Def. 3.2, Lemma 3.1); the rigidity probability by Hoeffding–Azuma on a weighted tree-component count (Thm 4) | treewidth threshold, `G(n, m)` | `m/n`: 1.18 (Kloks) → 1.083 (the same count, refined analysis) → **1.073**; in `c = 2m/n`: 2.166 → 2.146 | the truth is `c = 1` (Lee–Lee–Oum): the rigidity restriction moved the threshold by 0.020 of a gap of 1.166, **1.7%** |
| Lampis 2012 | locally optimal sets: every vertex has at most `Δ/2` neighbours across, so the out-degree profiles are truncated (§4) | edge expansion `i_E(Δ)`, random `Δ`-regular | Bollobás → Lampis (Table 1): `Δ = 4`: 0.440 → 0.444; 5: 0.730 → 0.7475; 6: 1.041 → 1.056; 7: 1.372 → 1.4035; 8: 1.716 → 1.740; 9: 2.0655 → 2.1105; 10: 2.430 → 2.465; 20: 6.320 → 6.4; 30: 10.47 → 10.59; 40: 14.74 → 14.9 — "modest (of the order of 10⁻² for Δ ≤ 10 and 10⁻¹ for somewhat larger Δ)" and growing with `Δ` (p. 8); Thm 2: the asymptotic coefficient of `√Δ` is strictly below Bollobás's `√(ln 2) = 0.833`, not computed | against the best upper bounds `i_E ≤ 2b(G)` from DDSW 2003 / DSW 2007 (`2/3, 1.0056, 1.3348, 1.7004` at `Δ = 4, 5, 6, 7`, KW p. 5): **1.8%, 6.3%, 5.1%, 9.6%** of the gap; asymptotically the truth is `Δ/2 − P*√Δ` with `P* = 0.7632` (Dembo–Montanari–Sen) against Bollobás's 0.833, and how much of that 0.07 Lampis's `α < 2 ln 2` recovers is not stated |
| Lichev–Mitsche 2023 | structure of a minimum bisection (2-cores, no winning sets, two types) and, for the binding type, counting *graphs* rather than bisections by dividing by the number of bisections of the same size one auxiliary graph yields (Lemma 5.6) | bisection width of random 3-regular | plain first moment (Bollobás) `n/11 = 0.0909n` → Kostochka–Melnikov `0.10101n` (edge weighting, not a first moment) → **`0.103295n`**; the type-one structural count alone reaches `0.1069n` on its own case, the type-two case with the division is what sets the constant | against their upper bound `0.139822n`: **25%** of the gap over the plain first moment, **6%** over Kostochka–Melnikov; the truth is unknown (the Zdeborová–Boettcher conjecture would put it at the max-cut complement, which "our paper does not shed light on", p. 2) |
| Do–Erde–Kang 2024 | separators `S` of a spanning tree's vertex set, `≤ 2^{Δ(T)|S|}` balanced separations each | treewidth threshold, `G(n, c/n)` | 2.146 (Gao) → **every `c > 1`**, i.e. the whole of the threshold gap, with the constant `Ω(ε³/log(1/ε))` | the only count in this table that reached the true threshold; it buys the threshold and not a constant |
| Kolesnik–Wormald 2014 | nothing merged: the direct first moment with the exact inner count; they note it is best possible for a direct application (p. 10) | vertex isoperimetric number, random `d`-regular | — | the gap it leaves at `d = 4`: lower 0.290 against upper 0.466 (experimental) / 0.581 (DEM); DDSS p. 17: "the union bound involved in the computation is likely to weaken the strength of the lower bounds, which we believe have room for improvement" |
| Gao 2006 | "a new combinatorial construct" | treewidth threshold | 2.36 → 2.162 | the construct is not in the held two pages; not read |

Summary of the column that matters: where a representative or restricted
count was applied to a first-moment cut constant, it moved the constant by
**1.7% of the gap** (rigidity, treewidth threshold), **2–10%** (local
optimality, edge expansion at `Δ = 4–7`, growing with `Δ`), and **6–25%**
(a full structural characterisation plus an overcount division, cubic
bisection, against a loosely known truth). The one count that closed a gap
entirely — Do–Erde–Kang's separator count — closed a *threshold*, by a
deterministic bound on the bipartitions per separator, and gave up the
constant to do it.

### 1.5 The brief's question, in the brief's terms

*"The new idea is a better estimate of the inner probability, not a new
object" — is that so, or does someone already have the exact inner
probability for a cut-type first moment?* Both halves need qualifying.
The **object** — sum over separators `S`, with the bipartitions of
`G − S` counted inside — is in Do, Erde & Kang (2024), following Luczak &
McDiarmid, with the inner count bounded by `2^{Δ(T)|S|}` and the inner
probability by sprinkling; it is not new, and it is in print as a device
for thresholds. The **exact inner probability** for a cut-type first
moment is in Kolesnik & Wormald (2014) for a single vertex cut in the
configuration model (the set, its vertex boundary and its edge boundary
counted exactly up to polynomial factors), and in Bollobás (1988) for
edge cuts; neither is a probability about the *rest* of the graph, and
neither is on `G(n, c/n)`. The inner probability of this loop's *relaxed*
event, `P(G(N, c′/N) has no component above N/2)`, is known exactly at the
exponential scale as a corollary of the LDP for the largest component
(O'Connell 1998; Puhalskii 2005 Cor. 2.4(3); Andreis–König–Patterson 2021
Cor. 1.3), and we found no width or cut first moment that uses it. The
inner probability of the bipartition event `E_bip`, the closed-pair count
and the weighted count, for pathwidth or any width, we found no statement
of. So: the object is known with a crude inner bound; the relaxed inner
rate is known in a different literature; their combination, and the finer
events, are what the loop computes. "We found no prior statement" is the
wording, and it is the strongest allowed.

### 1.6 What items 05–08 take from this

1. **Compare, do not re-derive, the relaxed count's rate.** Item 05's
   `O(N²)` DP for `E_relax` to `N = 400` has an exact asymptotic answer to
   check against: `I_{c′}^β(½)` from the quoted formula, zero iff
   `c′ ≤ 2 ln 2`. If the DP's fitted rate disagrees with the LDP's by more
   than the finite-size correction the DP itself shows, one of the two is
   wrong, and the quoted formula carries a known misprint risk
   (Puhalskii says O'Connell's Theorem 3.1 has one; the form used here is
   Puhalskii's restatement, checked only by its zero at the
   law-of-large-numbers point, `rate_check.log`).
2. **The planner's two routes were both the wrong route** (plan §0,
   correction 3). At `c = 6`, `c′ = 4.98`, the plan bracketed the rate of
   `E_relax` by the fixed-bipartition route `c′/4 = 1.245` and the global
   thinning route `1.19`; the LDP says the rate is **0.595**, half of
   either, and above the pair count's own `c′/4 − ln 2 = 0.552` as it must
   be. The cheapest way for `G(N, 4.98/N)` to have no component above
   `N/2` is neither a planted bipartition nor uniform thinning but the
   large-deviation tilt the rate function describes (Puhalskii: for
   `u < 1 − 1/c` the most probable configuration has several giants of
   size `≈ nu`). Items 05–06 should not fit a rate to those two routes.
3. **A preview of `β_relax(c)`, from the quotation alone, to be replaced
   by item 06** (`rate_preview.log`; the relaxed separator count
   `P(pw ≤ βn) ≤ C(n, βn) e^{−(1−β) I_{c(1−β)}^β(½) n + o(n)}`, root of
   `H(β) − (1 − β) I_{c(1−β)}^β(½)`): `β_relax = 0.0056, 0.0185, 0.0279,
   0.0368, 0.0827, 0.1328, 0.1817, 0.2690, 0.3409, 0.3998, 0.5542` at
   `c = 2, 2.5, 2.772, 3, 4, 5, 6, 8, 10, 12, 20`, against
   `β* = 0, 0, 0, 0.0087, 0.0613, 0.1175, 0.1706, 0.2628, 0.3371, 0.3973,
   0.5535`: gains of **+0.028 at `c = 3`, +0.021 at 4, +0.011 at 6, +0.004
   at 10, +0.0007 at 20**, and a positive constant for every `c > 2 ln 2`.
   This is an asymptotic statement resting on a cited LDP's upper bound
   and on the relaxed event; it is below the brief's kill of 0.02 at
   `c = 6` and `10` and above it at `c ≤ 4`; it sits inside the planner's
   bracket `[0.009, 0.056]` at `c = 3` and at the top of the planner's
   `+0.004–0.010` at `c = 6–10`. `E_bip` can only be rarer than `E_relax`,
   so `β_sep ≥ β_relax` if the LDP is used as an upper bound on the inner
   probability; whether it is strictly larger is item 06's question.
4. **For covers (item 07) there is no LDP to quote.** Behrisch and
   Lagerås–Lindholm give the giant's typical size for Bernoulli-incidence
   random intersection graphs (the onset line, in their coordinates); the
   lower tail of the giant of a random clique cover with fixed pattern
   sizes has to be computed (the isolated-customer generating function the
   plan proposes) or derived from the AKP machinery, which is for `G(N,p)`.
5. **What representative counts have bought elsewhere** is 2–25% of a
   gap (§1.4). The brief's kill of `0.02` in `β` is, at `c = 6`, 0.02 of a
   gap of `0.268 − 0.171 = 0.097` to the fitted slope, i.e. 21%; at
   `c = 10`, 26% of `0.078`. By the literature's track record that is at
   the top of what a representative count has ever delivered, and item 09
   (the weighted count) should know it is aiming above the record.
6. **The exact inner count of Kolesnik–Wormald is the model for item 07's
   inclusion–exclusion**: the vertex boundary and the edge boundary of the
   counted set enter the first moment as separate variables with an exact
   count per profile, and the union bound runs over `O(n²)` profiles at no
   exponential cost. The closed-pair count (`S = N(A) ∩ N(R)`) is a
   vertex-boundary condition of the same kind on `G(n, c/n)`.

### 1.7 Where the record corrects the item

- Kolesnik & Wormald's arXiv number is **1311.6555** (the held file says
  so); the item's 1109.0689 is a different paper. The item's Puhalskii
  venue is wrong (*Ann. Probab.*, not *Stochastic Processes and their
  Applications*).
- "**Díaz–Serna–Wormald's locally optimal bisections**" do not exist: the
  2003/2007 paper is a priority-greedy *upper* bound by the
  differential-equation method, with no first moment and no local
  optimality. The locally optimal count the item has in mind is
  **Lampis 2012**, cited by Kolesnik–Wormald as the improvement on
  Bollobás "by investigating subsets which are, in a certain sense,
  locally optimal" (p. 5); fetched and tabulated above.
- The held **Kloks 1994 preview is chapter 12** (cocomparability graphs)
  and contains no random-graph statement; the item's instruction "do not
  assert his inner probability from memory" is followed, and the chapter
  is now on the missing list by name.
- Díaz–Diner–Serna–Serra 2022 is published (JCSS 2024, DOI above); cite
  the journal version.
- Bezrukov et al. 2004 is deterministic and spectral; it belongs in no
  column of Table A but the vocabulary one, and its one random-graph
  sentence misquotes Kostochka–Melnikov by a factor of two (§1.2).

### 1.8 Kill verdict, and what this does not claim

**Kill verdict: none** (the item has no kill criterion); the stop rule
did not fire (no prior separator first moment with an exact inner
probability for pathwidth or vertex separation of `G(n, c/n)`), so items
05–06 derive, and compare against the three nearest results named at the
top of this section.

Nothing here is a theorem of ours, and no number here is a result of the
loop:

- The threshold `2 ln 2` for the relaxed separator count, and the values
  of `β_relax(c)`, rest on a quoted rate function that has a documented
  misprint history, checked only by its zero at the typical point and
  by its sign; they are asymptotic (an LDP upper bound for a closed set),
  not finite-`n` inequalities, and they concern `E_relax`, not `E_bip`.
  Item 06 owns them.
- That the rate of `E_bip` equals that of `E_relax` is a reading of the
  AKP minimiser, not a proof.
- Priority is claimed for nothing. The strongest statement made is that
  (a) and (b) of the item were done and the combination was not found.
- Bollobás 1988, O'Connell 1998, Luczak–McDiarmid 2001 and the journal
  Díaz–Serna–Wormald 2007 were not read; every statement attributed to
  them is from the restatements named beside it.
- Lichev–Mitsche's §6 (the upper bound) and the middle of their §§3–5
  were skimmed, not read line by line; the numbers quoted are from their
  Theorem 1.1, §1.2 and the ends of §§4–5.
- The fractions of a gap in §1.4 use the best *upper bounds* where the
  truth is unknown (edge expansion at small `Δ`, cubic bisection), so they
  are lower bounds on the fraction of the true gap.

---

## 2. The deterministic lemmas: balanced separator, its relaxation, the closed pair (item 02, 2026-11-01)

**Question (A of the brief).** Exactly which structures does
`pw(G) ≤ k < n` force, in a form a first moment can count once per
separator? Three, each one line from `exists_empty_pair_of_layout`
(`EmptyPair.lean`), and each checked by brute force before being called a
lemma: on every graph on 1–9 vertices from `nauty-geng` (288,266 graphs),
on 20,000 random `G(n, p)` graphs at `n = 10, 11, 12` and on 2,000 random
clique covers at 4–10 customers (§2.4). **Zero counterexamples.** The
kill criterion (a counterexample to L1, L1′ or L2) is **not met**.

Notation, for the whole section: `G` is a graph on the vertex set `V`,
`|V| = n`; `N[X] = X ∪ N(X)` is the closed neighbourhood and
`N(X) = N[X] ∖ X` the *outer* boundary of `X`; a pair `(A, R)` of disjoint
sets is **empty** when no edge joins `A` to `R`, equivalently
`R ∩ N[A] = ∅`; `k` is an integer with `pw(G) ≤ k < n`,
`N = n − k`, `t = ⌈N/2⌉`, so that `t ≥ N − t ≥ 0` and `t ≥ 1`. Nothing in
this section is probabilistic.

### 2.1 L1 — the balanced separator at exact sizes

**Lemma L1.** If `pw(G) ≤ k < n`, there are pairwise disjoint `A, R, S`
with `A ∪ R ∪ S = V`, `|A| = t`, `|R| = N − t`, `|S| = k` and no `A–R`
edge.

*Proof.* (Layout step) By `vertexSeparation_eq_pathwidth` there is a
layout `σ` with `vs(σ) = pw(G) ≤ k`. (Prefix step) Apply
`exists_empty_pair_of_layout` at position `i = t − 1`, which is `< n`
because `t ≤ N ≤ n`: the prefix `A` of size `t` and the inactive suffix
`R₀` are disjoint, no edge joins them, and
`n ≤ |A| + |R₀| + vs(σ) ≤ t + |R₀| + k`, i.e. `|R₀| ≥ N − t`
(`card_inactiveSuffix`). (Shrink step) Take `R ⊆ R₀` with `|R| = N − t`;
the edge condition is universally quantified over `R₀`, so it holds on
`R`, and `R ⊆ R₀` is disjoint from `A`. (Complement step)
`S = V ∖ (A ∪ R)` has `n − t − (N − t) = k` vertices and is disjoint from
both. ∎

*Remarks.* (i) The sizes are exact: `|R| = N − t = ⌊N/2⌋`, which is the
item's `n − t − k`. The Lean corollary `exists_empty_pair` rounds it to
`|R| ≥ t − 1`, which coincides with `N − t` for `N` odd and is one less
for `N` even; the count on record (`FirstMoment.lean`,
`card_emptyPairIndices`) uses `|R| = t − 1`, and plan §0 correction 2 is
about this rounding. L1 is the sharper form and is what §2.4 checks.
(ii) `S` is the active suffix at position `t − 1` padded to exactly `k`
vertices with vertices of `R₀`; which vertices are moved is immaterial,
and the lemma says nothing about `S` beyond its size — that is what L2
adds.

### 2.2 L1′ — the separator events `E_bip` and `E_relax`

For a `k`-set `S ⊆ V` write `G − S` for the subgraph induced on
`V ∖ S` (which has `N` vertices) and define two events:

    E_bip(S):   the components of G − S can be grouped into two classes
                whose vertex counts are t and N − t;
    E_relax(S): no component of G − S has more than t vertices.

**Lemma L1′.** (a) If `pw(G) ≤ k < n`, some `k`-set `S` satisfies
`E_bip(S)`. (b) For every `k`-set `S`, `E_bip(S)` implies `E_relax(S)`.
(c) For every `k`-set `S`, `E_bip(S)` holds iff `G` has an exact-size
empty pair `(A, R)` (`|A| = t`, `|R| = N − t`, no `A–R` edge) with
`V ∖ (A ∪ R) = S`. Hence *"some `k`-set is in `E_bip`"* and *"an
exact-size empty pair exists"* are the same event; the two counts `X₂`
(separators) and `X₁` (pairs) count it differently. (d) The inclusion in
(b) is strict: on the graph `3K₂` (six vertices, edges `03, 14, 25`) with
`k = 0`, `S = ∅` satisfies `E_relax` (components of sizes `2, 2, 2 ≤ t = 3`)
and not `E_bip` (no sub-family of `{2, 2, 2}` sums to `3`). This is the
first graph on six vertices in `nauty-geng` order with a `k`-set in
`E_relax ∖ E_bip` (`check.log`, first line); its pathwidth is `1`, so at
`k = pw` the two events agree on it.

*Proof.* (a) Take `A, R, S` from L1. (Connectivity step) A component `C`
of `G − S` is connected and lies in `A ∪ R`; if it met both `A` and `R`,
some edge of `C` — a path inside `C` from a vertex of `A` to a vertex of
`R` has a first `A–R` edge — would join `A` to `R`, contradicting
emptiness. So `C ⊆ A` or `C ⊆ R`. (Grouping step) The components inside
`A` partition `A` and sum to `t`; those inside `R` sum to `N − t`.
(b) Each component lies in a class of size `t` or `N − t ≤ t`.
(c, ⇒) Let `A` be the union of the class of size `t` and `R` the union
of the other; they partition `V ∖ S`, have the right sizes, and an edge
of `G − S` joins two vertices of one component, hence of one class, so
no edge joins `A` to `R` (an `A–R` edge of `G` would have both ends
outside `S`, so it would be an edge of `G − S`). (c, ⇐) is (a)'s
argument applied to the given pair. (d) is checked directly. ∎

*Remark.* `E_relax` is the Lean-cheap and LDP-shaped form (plan §0,
correction 3; §1.6): it is a statement about component sizes only, and
`P_N(E_relax)` on `G(N, p)` is the lower tail of the largest component.
`E_bip` is the event the pair count actually witnesses, and items 05–06
compute `P_N(E_bip)` from the full component-size partition, not from
the largest component alone. On the graphs checked the two differ at
`k = pw` on `0.3%` of graphs at 7 vertices and `2.2%` at 9 (§2.4,
column "`E_relax ⊋ E_bip`"), so at these sizes the relaxation is nearly
free; nothing here says what it costs at the scale of the rate.

### 2.3 L2 — the closed pair, by the alternating closure

**Lemma L2.** Let `(A, R)` be an empty pair with `|A| ≥ t`,
`|R| ≥ N − t` and `|V ∖ (A ∪ R)| ≤ k`. Put

    R* = V ∖ N[A],      A* = V ∖ N[R*],      S* = V ∖ (A* ∪ R*).

Then: (i) `A ⊆ A*` and `R ⊆ R*` (monotone); (ii) `(A*, R*)` is an empty
pair; (iii) `R* = V ∖ N[A*]` and `A* = V ∖ N[R*]` (a **closed pair**), so
the alternating closure `R₁ = V ∖ N[A]`, `A₁ = V ∖ N[R₁]`, `R₂ = V ∖ N[A₁]`,
`A₂ = V ∖ N[R₂]`, … is constant from `(A₁, R₁) = (A*, R*)` on — it stops
after **one round**, not after an unbounded iteration; (iv)
`S* = N(A*) ∩ N(R*)`; (v) `|A*| ≥ t`, `|R*| ≥ N − t`, `|S*| ≤ k`.
Conversely, every closed pair `(A, R)` (one with `A = V ∖ N[R]` and
`R = V ∖ N[A]`) is empty with `V ∖ (A ∪ R) = N(A) ∩ N(R)`, and is
determined by either side.

*Proof.* (Galois step) For any `X, Y ⊆ V`: `Y ⊆ V ∖ N[X]` iff `Y ∩ X = ∅`
and no edge joins `X` to `Y`, iff `X ⊆ V ∖ N[Y]`, by the symmetry of
adjacency; and `X ⊆ X′` implies `N[X] ⊆ N[X′]` (monotone step).
(i) `(A, R)` is empty, so `R ⊆ V ∖ N[A] = R*` by the Galois step.
`R* ∩ N[A] = ∅` by definition, so `(A, R*)` is empty and the Galois step
gives `A ⊆ V ∖ N[R*] = A*`. (ii) `A* ∩ N[R*] = ∅` by definition.
(iii) From (ii) and the Galois step, `R* ⊆ V ∖ N[A*]`; from `A ⊆ A*` and
the monotone step, `V ∖ N[A*] ⊆ V ∖ N[A] = R*`. So `R* = V ∖ N[A*]`, and
`A* = V ∖ N[R*]` is the definition. Hence `R₂ = V ∖ N[A₁] = R₁` and
`A₂ = V ∖ N[R₂] = A₁`, and by induction every later term equals these.
(iv) `v ∈ S*` iff `v ∉ A*` and `v ∉ R*`; `v ∉ A* = V ∖ N[R*]` means
`v ∈ N[R*]`, which with `v ∉ R*` is `v ∈ N(R*)`; symmetrically
`v ∈ N(A*)`. Conversely a vertex of `N(A*) ∩ N(R*)` is outside `A*` and
outside `R*` by the definition of the outer boundary. (v) From (i),
`|A*| ≥ |A| ≥ t` and `|R*| ≥ |R| ≥ N − t`; then
`|S*| = n − |A*| − |R*| ≤ n − t − (N − t) = k`. The converse is (ii)–(iv)
read with `A* = A`, `R* = R`; "determined by either side" is
`R = V ∖ N[A]`. ∎

*Remarks.* (i) **The fixpoint is a representative, not the
representative.** Closing `R` first gives `(V ∖ N[R], V ∖ N[V ∖ N[R]])`,
which can differ from `(A*, R*)`: on the graphs checked the two maps
disagree on `7–10%` of exact-size pairs at 7–9 vertices (§2.4, column
"closures differ"). A union bound over closed pairs needs only *a*
map from exact-size pairs to closed pairs of the forced sizes, and L2
gives one (`A` first; the mirror is another); it does not need the map
to be canonical, and this document never says it is. (ii) The item
expected an iteration `A ⊆ A₁ ⊆ A₂ ⊆ …`; (iii) says the chain is
`A ⊆ A₁ = A₂ = …`, `R ⊆ R₁ = R₂ = …`. Monotonicity holds as asserted
(with equality from the second step), which is what the check verifies
at every step — the item's expectation is corrected, not contradicted.
(iii) Because every closed pair is determined by `A`, the closed pairs
of the forced sizes (`X₃` below) are enumerated exactly by running over
all `A ⊆ V`, setting `R = V ∖ N[A]` and testing `A = V ∖ N[R]` and the
sizes; no pair is reached twice. (iv) The image of the exact-size pairs
under the `A`-first closure (`X₃′`) can be a proper subset of `X₃`: a
closed pair of the forced sizes contains exact-size sub-pairs, but
closing a sub-pair may land on a *larger* closed pair (its `V ∖ N[A′]`
contains `V ∖ N[A]`). Both counts are valid first moments; item 03
measures both.

### 2.4 The check, before any of the above was called a lemma

`reports/scratch/separator_moment/02_lemmas/check.py` (log beside it),
on the functions of `learning/separator_moment.py` (tested in
`tests/test_separator_moment.py`, which also re-enumerates every
labelled graph to 6 vertices and pins the subset DP to
`learning.first_moment.vertex_separation_brute` and
`fixed_parameter_algorithm.pathwidth.compute_pathwidth`). For each graph,
`k = pw(G)` by the subset DP; then

* **L1**: `X₁ > 0`, where `X₁` is the number of ordered exact-size empty
  pairs (`|A| = t`, `|R| = N − t`; for `N` even `(A, R)` and `(R, A)` are
  both counted);
* **L1′**: `X₂ > 0`, `X₂ ≤ X₂′`, and `X₁ > 0 ⟺ X₂ > 0`, where `X₂`, `X₂′`
  are the numbers of `k`-sets `S` in `E_bip` and `E_relax`, computed from
  the components of `G − S` and a subset-sum over their sizes;
* **L2**: from every exact-size pair (all of them when `X₁ ≤ 200`, the
  first 200 otherwise), the closure sequence is monotone at every step,
  the second round repeats the first, the fixpoint is closed, empty, of
  the forced sizes, with `S* = N(A*) ∩ N(R*)`, and lies in `X₃` (all
  closed pairs of the forced sizes, by the enumeration of remark (iii));
  the share of pairs whose `A`-first and `R`-first fixpoints differ;
* **L3** (covers only): a pair is empty iff no pattern meets both sides
  (on every exact-size pair and on 20 random disjoint pairs per
  instance), and every customer of `S*` shares a pattern with `A*` and
  with `R*`;
* at `k = pw − 1`: whether an exact-size pair (equivalently a `k`-set in
  `E_bip`) and whether a `k`-set in `E_relax` still exist — the necessary
  condition's slack at these sizes.

**Results** (`check.log`, `summary.csv`; 2026-11-01, 4 workers at nice 19, 113 s wall; the
rows for 1–3 vertices — 7 graphs, zero violations — are omitted). Medians and
maxima are over the graphs of the row at `k = pw`; `X₃′` is computed only on
graphs with `X₁ ≤ 200`, so its maximum at `n ≥ 10` is over that subset;
"`E_relax ⊋ E_bip`" is the share of graphs with `X₂′ > X₂`; "closures differ"
is the share of closed pairs whose `A`-first and `R`-first fixpoints differ,
over the pairs closed; the last two columns are the shares of graphs with
`pw ≥ 1` on which the structure still exists at `k = pw − 1`.

| graphs | count | viol. | `X₁` med / max | `X₂` med / max | `X₂′` med / max | `X₃` med / max | `X₃′` med / max | `E_relax ⊋ E_bip` | pairs closed | closures differ | L1 at `pw − 1` | `E_relax` at `pw − 1` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| geng n=4 | 11 | 0 | 4 / 8 | 2 / 4 | 2 / 4 | 2 / 6 | 2 / 6 | 0.0% | 48 | 4.2% | 40.0% | 40.0% |
| geng n=5 | 34 | 0 | 6 / 18 | 3 / 9 | 3 / 9 | 3 / 10 | 3 / 10 | 0.0% | 218 | 8.7% | 42.4% | 42.4% |
| geng n=6 | 156 | 0 | 6.5 / 36 | 4 / 16 | 4 / 16 | 4 / 20 | 4 / 20 | 0.0% | 1,318 | 10.1% | 43.9% | 44.5% |
| geng n=7 | 1,044 | 0 | 8 / 84 | 4 / 25 | 4 / 25 | 4 / 35 | 4 / 35 | 0.3% | 10,530 | 9.9% | 45.6% | 46.1% |
| geng n=8 | 12,346 | 0 | 8 / 200 | 5 / 52 | 5 / 52 | 5 / 70 | 5 / 70 | 1.0% | 137,152 | 8.4% | 43.1% | 43.6% |
| geng n=9 | 274,668 | 0 | 9 / 450 | 6 / 105 | 6 / 105 | 6 / 126 | 6 / 126 | 2.2% | 3,243,462 | 6.7% | 38.5% | 39.0% |
| random n=10 | 6,667 | 0 | 13 / 1050 | 7 / 92 | 7 / 92 | 8 / 252 | 8 / 127 | 4.4% | 187,528 | 14.4% | 44.1% | 44.6% |
| random n=11 | 6,667 | 0 | 14 / 2310 | 8 / 145 | 8 / 145 | 9 / 420 | 8 / 122 | 5.9% | 209,294 | 11.6% | 43.2% | 43.7% |
| random n=12 | 6,666 | 0 | 16 / 3192 | 9 / 161 | 9 / 161 | 10 / 582 | 10 / 141 | 7.9% | 224,689 | 9.9% | 42.8% | 43.2% |
| covers n<=10 | 2,000 | 0 | 5 / 74 | 4 / 30 | 4 / 30 | 2 / 30 | 2 / 30 | 2.2% | 13,042 | 3.1% | 27.0% | 27.2% |

**Total: 310,266 graphs, 4,027,298 closures checked, zero violations of any
kind** (the script's fourteen violation flags all stayed at zero; `grep -c
VIOLATION check.log` is `0`). Read across: `X₁ ≥ X₂` always (several pairs per
separator), `X₂ = X₂′` in every maximum and median at these sizes (the
relaxation adds separators on 0.3–8% of graphs, growing with `n` and with
the random graphs' density), `X₃′ < X₃` on 2.8% of graphs at 7 vertices, 1.8% at 8
and 0.9% of the random graphs at 10–12 where computed (closed pairs that
the closure of no exact-size pair reaches, remark (iv) of §2.3;
`x3_vs_x3prime.log`), and the covers behave like sparse graphs (fewer closed pairs than
separators, the closure orders rarely differing).

### 2.5 L3 — the MOSP forms

Let the instance have customers `C` (`|C| = n`) and patterns
`S_1, …, S_m ⊆ C`; its MOSP graph `mospGraph` (`MOSPGraph.lean`;
`coverGraph` in `CliqueCoverMoment.lean`) joins two distinct customers
iff some pattern contains both, and `mospValue = pw(mospGraph) + 1`
(`MOSPGraph.lean`, both directions). With `k = mospValue − 1 < n`:

**Lemma L3.** (a) For disjoint `A, R ⊆ C`, `(A, R)` is an empty pair of
`mospGraph` iff no pattern meets both `A` and `R`
(`isEmptyPair_coverGraph_iff`). (b) L1, L1′ and L2 hold for `mospGraph`
with `S` a set of `k` customers; in particular every instance with
`mospValue ≤ k + 1` has `k` customers whose removal leaves customer
classes of sizes `t` and `N − t` such that no pattern meets both classes.
(c) In a closed pair `(A*, R*)` of `mospGraph`, a customer `c` lies in
`S* = N(A*) ∩ N(R*)` iff `c ∉ A* ∪ R*`, some pattern contains `c` and a
customer of `A*`, and some pattern contains `c` and a customer of `R*`.

*Proof.* (a) is the cited lemma. (b) is L1, L1′, L2 applied to the graph
`mospGraph`, with `k ≥ pw` given by the equality theorem. (c) `c ∈ N(X)`
for `mospGraph` means `c ∉ X` and `c` is adjacent to some `x ∈ X`, i.e.
some pattern contains both `c` and `x`; apply L2 (iv). ∎

The check of §2.4 runs L1, L1′, L2 on the MOSP graphs of 2,000 random
covers and tests (a) and (c) directly against the matrix.

### 2.6 Lean-ready statements for item 10

All over `{V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
[DecidableRel G.Adj]`, in the vocabulary of `EmptyPair.lean`
(`closedNbhd`, `IsEmptyPair` from `FirstMoment.lean`), with `n = Fintype.card V`,
`t = (n − k + 1) / 2`, `N − t = (n − k) / 2` in `ℕ` arithmetic.

| name | hypotheses | conclusion | rests on |
|---|---|---|---|
| `exists_balanced_separator` (L1) | `pathwidth G ≤ k`, `k < n` | `∃ A R S : Finset V`, pairwise disjoint, `A ∪ R ∪ S = univ`, `A.card = t`, `R.card = N − t`, `S.card = k`, `∀ u ∈ A, ∀ v ∈ R, ¬ G.Adj u v` | `vertexSeparation_eq_pathwidth`, `exists_empty_pair_of_layout` at `i = t − 1`, `Finset.exists_subset_card_eq`, `Finset.card_sdiff` |
| `IsBalancedBip G S k` (def) | — | `∃ A R, Disjoint A R ∧ A ∪ R = univ \ S ∧ A.card = t ∧ R.card = N − t ∧ IsEmptyPair G A R` — the pair form of `E_bip`, which L1′ (c) shows equivalent to the component form | — |
| `exists_isBalancedBip` (L1′ a) | `pathwidth G ≤ k`, `k < n` | `∃ S, S.card = k ∧ IsBalancedBip G S k` | `exists_balanced_separator` |
| `connectedComponent_subset_side` (connectivity step) | `IsEmptyPair G A R`, `C` a connected component of `G.induce (A ∪ R)` | `C ⊆ A ∨ C ⊆ R` | induction on `SimpleGraph.Walk` in the induced graph |
| `isBalancedBip_iff_components` (L1′ c) | `S.card = k` | `IsBalancedBip G S k ↔` the components of `G.induce (univ \ S)` admit a grouping into sizes `t`, `N − t` | the previous row; the converse by taking unions |
| `IsRelax G S k` (def) and `isRelax_of_isBalancedBip` (L1′ b) | `IsBalancedBip G S k` | every component of `G.induce (univ \ S)` has `card ≤ t` | `connectedComponent_subset_side`, `Finset.card_le_card` |
| `not_isBalancedBip_threeEdges` (L1′ d) | the graph `3K₂` on `Fin 6`, `k = 0`, `S = ∅` | `IsRelax ∧ ¬ IsBalancedBip` | `decide` |
| `subset_compl_closedNbhd_iff` (Galois step) | — | `R ⊆ univ \ closedNbhd G A ↔ Disjoint A R ∧ ∀ u ∈ A, ∀ v ∈ R, ¬ G.Adj u v` | `mem_closedNbhd_iff`, `G.adj_symm` |
| `closedNbhd_mono` | `A ⊆ A'` | `closedNbhd G A ⊆ closedNbhd G A'` | `Finset.biUnion_subset_biUnion_of_subset_left` |
| `IsClosedPair G A R` (def) | — | `A = univ \ closedNbhd G R ∧ R = univ \ closedNbhd G A` | — |
| `closure_subset` (L2 i) | `IsEmptyPair G A R` | `A ⊆ univ \ closedNbhd G (univ \ closedNbhd G A)` and `R ⊆ univ \ closedNbhd G A` | `subset_compl_closedNbhd_iff` twice |
| `closure_isClosedPair` (L2 ii–iii) | `IsEmptyPair G A R` | `IsClosedPair G (univ \ closedNbhd G (univ \ closedNbhd G A)) (univ \ closedNbhd G A)` | `closure_subset`, `closedNbhd_mono`, `subset_compl_closedNbhd_iff` |
| `sdiff_isClosedPair_eq_inter_boundary` (L2 iv) | `IsClosedPair G A R` | `univ \ (A ∪ R) = (closedNbhd G A \ A) ∩ (closedNbhd G R \ R)` | `mem_closedNbhd_iff` |
| `closure_card` (L2 v) | `IsEmptyPair G A R`, `t ≤ A.card`, `N − t ≤ R.card`, `(univ \ (A ∪ R)).card ≤ k` | the same three bounds for the closed pair | `closure_subset`, `Finset.card_le_card`, `Finset.card_sdiff` |
| `exists_closedPair_of_pathwidth_le` (L1 + L2) | `pathwidth G ≤ k`, `k < n` | `∃ A R, IsClosedPair G A R ∧ IsEmptyPair G A R ∧ t ≤ A.card ∧ N − t ≤ R.card ∧ (univ \ (A ∪ R)).card ≤ k` | the two rows above and `exists_balanced_separator` |
| `mem_boundary_coverGraph_iff` (L3 c) | `S : Fin m → Finset C` | `c ∈ closedNbhd (coverGraph S) A \ A ↔ c ∉ A ∧ ∃ j, c ∈ S j ∧ ∃ a ∈ A, a ≠ c ∧ a ∈ S j` | `coverGraph`'s adjacency, `mem_closedNbhd_iff` |
| `exists_balanced_separator_cover` (L3 b) | an instance with `mospValue ≤ k + 1`, `k < n` | `exists_balanced_separator` for `mospGraph`, with the empty pair stated as "no pattern meets both" | `MOSPGraph.lean`'s equality, `isEmptyPair_coverGraph_iff` |

Obstacle noted for item 10, not for this item: `isBalancedBip_iff_components`
needs connected components of an induced subgraph as `Finset`s with their
cardinalities, which the development has not used so far (Mathlib's
`SimpleGraph.ConnectedComponent` is a quotient type; `Fintype` instances
exist, the union-of-supports bookkeeping does not). The pair form
`IsBalancedBip` is what the probabilistic statement of item 08 needs, and
it is cheap; the component form is for the LDP comparison and can be
left as a named `Prop` with this obstacle if it does not fit.

### 2.7 Regenerate, size range, kill verdict, what this does not claim

* **Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/02_lemmas/check.py --max-n 9 --workers 8`
  (run with 4 workers on 2026-11-01 because the one-minute load was
  above 24; the log says the wall time); `python3 -m pytest tests/test_separator_moment.py`.
* **Size range.** Every graph on 1–9 vertices; 20,000 random `G(n, p)`
  graphs at `n = 10, 11, 12` with `p ∈ {0.15, 0.3, 0.45, 0.6}` (seed = job
  index); 2,000 random covers with 4–10 customers, `m ∈ {n, 2n}`, 2–4
  customers per pattern (`generate_structured_instance(n, m, cpp, seed = index)`).
  The lemmas are for every graph; the counts in the table are for these
  sizes only.
* **Kill verdict: not met.** Zero counterexamples to L1, L1′, L2 or L3 on
  310,266 graphs. The item's premise — that a narrow layout forces a
  balanced separator, a balanced empty bipartition and a closed pair at the
  forced sizes — stands; the three structures exist on every graph checked
  at `k = pw`, and at `k = pw − 1` they exist on 39–46% of graphs at
  7–9 vertices (27% of the covers), so at these sizes the *necessary* condition is far from
  sufficient — the slack the loop is about is already visible on nine
  vertices, and it is the condition's, not only the union bound's.
* **Does not claim.** Anything probabilistic: no rate, no constant, no
  statement about `P_N(E_bip)`. That the closed pair is canonical (the
  `A`-first and `R`-first fixpoints differ on 3–14% of the pairs
  checked). That `E_relax` is a cheap relaxation at scale (it differs from
  `E_bip` on 2.2% of graphs at 9 vertices and 8% of the random graphs at
  12; the rate question is item 05's). That the share of graphs with a structure at `k = pw − 1` says
  anything beyond nine vertices. The Lean rows of §2.6 are statements,
  not proofs; item 10 proves them or names the obstacle.

---

## 3. The clumping decomposed: pairs, separators, closed pairs and move-classes on instances with exact pathwidth (item 03, 2026-11-01)

**Question (B of the brief).** On a graph of pathwidth `k`, how many
exact-size empty pairs are there (`X₁`), how many distinct separators
among them (`X₂`), how many closed pairs of the forced sizes (`X₃`; and
`X₃′`, the image of the exact-size pairs under the `A`-first closure of
L2), and how many move-classes (`X₄`)? How fast do the ratios `X₁/X₂`,
`X₁/X₃`, `X₁/X₄` grow with `n`, in nats per vertex, against the `0.066`
that a `0.02` gain in `β` needs at `c = 10` (the pair exponent's slope at
`β*` is `3.3` per unit of `β` there; `3.4, 3.9` at `c = 6, 4`;
`rate_preview.log`)? Each ratio is what one representative count merges:
`X₂` merges every pair with the same separator (the component flips of
plan §0, and the reversal), `X₃` merges every pair with the same closure,
`X₄` merges every pair reachable by single swaps.

**The events counted, exactly.** `X₁` is the number of ordered pairs
`(A, R)` with `|A| = t`, `|R| = N − t`, no `A–R` edge (the count of
`FirstMoment.lean`). `X₂` is the number of distinct `S = V ∖ (A ∪ R)` over
those pairs, which by L1′ (c) is the number of `k`-sets in `E_bip`. `X₃` is
the number of ordered closed pairs with `|A| ≥ t`, `|R| ≥ N − t`,
`|S| ≤ k` (§2.3; enumerated by the pruned search of
`closed_pairs_pruned`, which agrees with the `2ⁿ` enumeration of
`closed_pairs` on all 2,200 rows at `n ≤ 16`, `k = pw`). `X₄` is the
number of connected components of the graph on exact-size pairs in which
two pairs are adjacent when their labellings `V → {A, R, S}` differ on at
most two vertices; at exact sizes a single vertex cannot change class, so
an edge is exactly one swap of two vertices between two classes
(`A ↔ S`, `R ↔ S` or `A ↔ R`). When `N` is even, `(R, A)` is an exact-size
pair whenever `(A, R)` is, with the same `S`: the reversal is in `X₁` and
not in `X₂`, and the parity split below separates it from everything else.

### 3.1 Instances

| source | cells | per cell | instances | exact value from |
|---|---|---|---|---|
| fresh `G(n, c/n)` | `n ∈ {14, 16, 18, 20, 22, 24}` × `c ∈ {4, 6, 8, 10}` | 200 | 4,800 | the C program `pathwidth_solver/cli/pathwidth -l -t 60` (every graph proved, `refutation` or `bound`; the layout kept in `instances.csv`); at `n ≤ 16` the subset DP `vertex_separation` agrees on all 1,600 |
| pilot `G(20, c/20)` | `c ∈ {4, 6, 8, 10}` | 137 | 548 | on record (`gnp_pilot/results.csv`); the overlap check at one size |
| certified covers, fixed generator | `n ∈ {10, 15, 20, 25}` × `d ∈ {4, 6}`, `m = n` | 150 | 1,200 | on record (`learning/data/ensemble/results.csv`, `pw = optimum − 1`); regenerated from seed; the DP agrees at `n ≤ 16` |

Seeds of the fresh graphs: `crc32("sep03:{n}:{c}:{i}")`, `i < 200`;
generator `networkx.gnp_random_graph(n, c/n, seed)` as in the pilot.
Nothing on record was re-solved. The counts are taken at
`k = pw − 1, pw, pw + 1, pw + 2` on every instance (caps on the
enumeration were never reached: no row is marked skipped). The whole run
is **7 s** for the solves and **66 s** for the counts on 8 workers at nice 19
(516 s of enumeration in total, about 0.15 core-hours against the 3
budgeted; the one-minute load was below 2).

### 3.2 The counts at `k = pw`

Geometric means over the cell (every instance has `X₁ > 0` at `k = pw`, as
L1 says). `X₁/X₂` and the others are geometric means of the per-instance
ratios. (`cells.csv`; the medians and maxima are there too.)

**Fresh `G(n, c/n)`:**

| `c` | `n` | mean `pw/n` | `X₁` | `X₁/X₂` | `X₁/X₃` | `X₁/X₃′` | `X₁/X₄` | max `X₁/X₂` | max `X₁/X₃` | max `X₁/X₄` |
|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 14 | 0.310 | 18.8 | 1.82 | 1.55 | 1.55 | 2.15 | 8.4 | 7.4 | 200 |
| 4 | 16 | 0.291 | 27.8 | 1.94 | 1.59 | 1.59 | 2.29 | 5.6 | 9.9 | 120 |
| 4 | 18 | 0.280 | 32.1 | 1.81 | 1.54 | 1.54 | 2.02 | 6.3 | 10.2 | 44.5 |
| 4 | 20 | 0.269 | 54.1 | 2.05 | 1.64 | 1.64 | 2.53 | 6.7 | 11.9 | 97.5 |
| 4 | 22 | 0.266 | 61.2 | 2.04 | 1.57 | 1.57 | 2.27 | 11.5 | 15.5 | 41.7 |
| 4 | 24 | 0.259 | 62.4 | 1.99 | 1.48 | 1.48 | 2.03 | 6.4 | 5.4 | 37.3 |
| 6 | 14 | 0.449 | 12.5 | 1.63 | 1.39 | 1.39 | 1.57 | 7.3 | 7.6 | 18.4 |
| 6 | 24 | 0.370 | 33.1 | 1.63 | 1.41 | 1.41 | 1.62 | 4.5 | 9.5 | 19.0 |
| 8 | 14 | 0.562 | 9.4 | 1.58 | 1.37 | 1.37 | 1.48 | 4.0 | 6.1 | 15.3 |
| 8 | 24 | 0.468 | 26.0 | 1.58 | 1.40 | 1.40 | 1.52 | 4.0 | 17.0 | 34.0 |
| 10 | 14 | 0.654 | 8.0 | 1.38 | 1.39 | 1.39 | 1.44 | 3.0 | 4.7 | 6.6 |
| 10 | 16 | 0.621 | 9.5 | 1.62 | 1.29 | 1.29 | 1.36 | 3.7 | 4.5 | 10.0 |
| 10 | 18 | 0.594 | 12.4 | 1.41 | 1.35 | 1.35 | 1.42 | 2.8 | 5.0 | 9.0 |
| 10 | 20 | 0.573 | 14.7 | 1.44 | 1.32 | 1.32 | 1.37 | 2.5 | 5.2 | 6.7 |
| 10 | 22 | 0.556 | 17.4 | 1.53 | 1.33 | 1.33 | 1.39 | 2.9 | 5.6 | 9.8 |
| 10 | 24 | 0.545 | 19.6 | 1.43 | 1.31 | 1.31 | 1.39 | 2.4 | 7.0 | 10.3 |
| pilot 10 | 20 | 0.571 | 13.7 | 1.50 | 1.30 | 1.30 | 1.36 | 2.6 | 4.9 | 7.5 |
| pilot 4 | 20 | 0.272 | 44.4 | 1.90 | 1.58 | 1.58 | 2.21 | 5.5 | 7.5 | 82.6 |

**Certified covers (`m = n`):**

| `d` | `n` | mean `pw/n` | `X₁` | `X₁/X₂` | `X₁/X₃` | `X₁/X₄` |
|---|---|---|---|---|---|---|
| 4 | 10 | 0.612 | 5.6 | 1.64 | 1.75 | 2.07 |
| 4 | 15 | 0.540 | 12.3 | 1.44 | 1.95 | 2.22 |
| 4 | 20 | 0.496 | 16.9 | 1.49 | 1.71 | 1.88 |
| 4 | 25 | 0.468 | 28.3 | 1.47 | 2.03 | 2.26 |
| 6 | 10 | 0.846 | 4.8 | 1.43 | 3.30 | 4.71 |
| 6 | 15 | 0.764 | 6.6 | 1.45 | 2.02 | 2.32 |
| 6 | 20 | 0.729 | 11.5 | 1.40 | 1.91 | 2.03 |
| 6 | 25 | 0.695 | 11.0 | 1.44 | 1.69 | 1.80 |

What the table says, at these sizes:

- **A typical instance at its own pathwidth has few witnesses.** `X₁` is
  8–62 (geometric mean) on `G(n, c/n)` at `n = 14–24`, 5–28 on the covers,
  falling with density and rising with `n` at `0.09–0.13` nats per vertex
  (fitted, §3.3). The pilot's `n = 20` cells agree with the fresh ones
  (`pw` means within 0.1, `X₁` and the ratios within 10–20%).
- **One separator carries, at the median, one pair — and its reverse.**
  `X₁/X₂` is 1.4–2.0 on the graphs and 1.4–1.6 on the covers, and the
  parity split shows what it is (`checks.log`): when `N` is odd (no
  reversal) the ratio is **1.08, 1.14, 1.23, 1.57** at `c = 10, 8, 6, 4`
  and **1.03–1.09** on the covers; when `N` is even it is **2.04, 2.05,
  2.14, 2.43** and `2.0–2.04`. So beyond the reversal a separator merges
  a factor of `1.03–1.6` of pairs, more on sparse graphs; `X₂ = X₁` outright
  on 13–14% of the graphs and 29% of the covers. The maximum over 200
  instances is 2.4–11.5.
- **The closure merges a factor 1.3–1.6 on the graphs, 1.7–3.3 on the
  covers**, and **`X₃′ = X₃` on every fresh and pilot graph at `k = pw`**
  (99.8% of the covers): at the pathwidth, every closed pair of the forced
  sizes is the closure of some exact-size pair, so the two counts of §2.3
  remark (iv) are one count here. They separate at `pw + 2` (`X₃′ < X₃`
  on 27–40% of instances), where the closed pairs that no exact-size
  pair reaches appear.
- **The move-classes merge a factor 1.4–2.5 on the graphs**, `X₄ = X₁` on
  39% of the graphs (every pair alone in its class), and the maximum over
  a cell is 7–200: the clusters a typical instance carries at `k = pw`
  are small, and the large ones are rare instances.

### 3.3 The rates

OLS slope of the per-instance `log` against `n` at fixed `c` (fresh graphs,
`n = 14–24`, 1,200 instances per `c`) and against `n` on the covers
(`n = 10–25`, 600 per `d`), with its standard error; nats per vertex of
`n`. (`slopes.csv`.)

| source | `c` or `d` | `k` | slope `log X₁` | slope `log X₁/X₂` | slope `log X₁/X₃` | slope `log X₁/X₃′` | slope `log X₁/X₄` |
|---|---|---|---|---|---|---|---|
| fresh | 4 | `pw` | 0.127 ± 0.011 | 0.010 ± 0.003 | −0.003 ± 0.004 | −0.003 ± 0.004 | −0.001 ± 0.007 |
| fresh | 6 | `pw` | 0.100 ± 0.010 | 0.004 ± 0.003 | 0.002 ± 0.004 | 0.002 ± 0.004 | 0.003 ± 0.005 |
| fresh | 8 | `pw` | 0.100 ± 0.009 | 0.002 ± 0.003 | 0.002 ± 0.003 | 0.002 ± 0.003 | 0.003 ± 0.004 |
| **fresh** | **10** | **`pw`** | 0.092 ± 0.008 | **0.000 ± 0.003** | **−0.003 ± 0.003** | −0.003 ± 0.003 | **−0.003 ± 0.004** |
| cover | 4 | `pw` | 0.104 ± 0.007 | −0.006 ± 0.002 | 0.006 ± 0.005 | 0.006 ± 0.005 | 0.002 ± 0.006 |
| cover | 6 | `pw` | 0.060 ± 0.007 | −0.000 ± 0.003 | −0.041 ± 0.005 | −0.041 ± 0.005 | −0.061 ± 0.005 |
| fresh | 10 | `pw + 1` | 0.193 ± 0.006 | 0.001 ± 0.003 | 0.007 ± 0.002 | 0.005 ± 0.002 | −0.070 ± 0.006 |
| fresh | 10 | `pw + 2` | 0.328 ± 0.004 | 0.005 ± 0.002 | 0.060 ± 0.002 | 0.038 ± 0.002 | −0.152 ± 0.007 |
| fresh | 4 | `pw + 2` | 0.280 ± 0.007 | 0.015 ± 0.003 | 0.015 ± 0.003 | 0.014 ± 0.003 | −0.126 ± 0.010 |

At `k = pw` **no ratio grows**: every slope of `log X₁/X₂`, `log X₁/X₃`,
`log X₁/X₄` is within `0.01` of zero at every `c` and both `d`, and at
`c = 10` the two the kill names are `0.000 ± 0.003` and `−0.003 ± 0.003`
— more than twenty standard errors below `0.066`. In the conversion of the
header, the separator and the closure merge **at most `0.01` nats per
vertex, i.e. at most `0.003` in `β`** at these sizes, against the `0.02`
the brief's kill asks for. The covers at `d = 6` show the closure and
move-class ratios *falling* with `n` (the `n = 10` cell, `pw/n = 0.85`, is
nearly complete and its forced sizes are 1–2, where everything closes to
everything). At `k = pw + 2`, with 100× more pairs, the closure merges
more as `n` grows (`0.06` per vertex at `c = 10`, `0.04` for the image
`X₃′`) while the move-classes multiply *faster* than the pairs (`−0.15`):
abundant pairs fragment into many small classes rather than one fat one.
These `pw + 2` rows are at a fixed offset, not a fixed `β`, and are not
comparable across `n` as rates.

At `k = pw − 1` the share of instances with no exact-size pair at all
(the necessary condition alone refutes `pw − 1`) is 43–57% at `c = 4`,
60–68% at `c = 6`, 62–72% at `c = 8` and 65–74% at `c = 10` on the graphs,
47–87% on the covers, with no trend in `n` at these sizes; where a pair
exists the median count is 1–4 (two is a pair and its reverse).

**Beside them, the second moment on `G(n, c/n)`** (`second_moment_rate_gnp`,
the `3 × 3` overlap table of `second_moment_rate` with Bernoulli edges:
two pairs are empty together iff no edge lies in `A × R ∪ A′ × R′`, of size
`2 t r − |A ∩ A′||R ∩ R′| − |A ∩ R′||R ∩ A′|`; exact finite form checked
against the enumeration of every pair of pairs at `n = 8, 10`; the
asymptotic sup checked against a `61⁴` grid at five `(a, c)`, agreeing to
four decimals; `second_moment_gnp.csv`, `checks.log`):

| `c` | at the cells' mean `β` (`n = 14 → 24`): `g(a)` | ratio exponent `sup − 2g` | maximiser | at `β*`: ratio exponent | maximiser |
|---|---|---|---|---|---|
| 4 | 0.62 → 0.54 | 0.12 → 0.16 | symmetric (`AA′ = AR′ = RA′ = RR′`) | 0.390 | same pair (`AA′ = RR′ = 0.221`) |
| 6 | 0.61 → 0.50 | 0.08 → 0.13 | symmetric | 0.370 | same pair (`0.259`) |
| 8 | 0.61 → 0.49 | 0.04 → 0.09 | symmetric | 0.335 | reversed pair (`AR′ = RA′ = 0.252`) |
| 10 | 0.59 → 0.49 | 0.02 → 0.06 | symmetric | 0.300 | reversed pair (`0.233`) |

At `β*` the Bernoulli second moment reproduces §8.5 (a)'s picture
exactly: `E[X²]/E[X]² = e^{0.30–0.39 n}`, carried by the pair itself or
its reverse perturbed through `S` (the two are mirror images of one
cluster). At the `β` where typical instances sit (`g(a) ≈ 0.5–0.6 > 0`,
`E[X] = e^{0.5 n}`) the maximiser is the *symmetric* table — the second
pair overlaps `A` and `R` equally — and the ratio exponent is `0.02–0.16`.
So the `e^{0.23 n}` is a statement about the large-deviation regime, where
`E[X]` is carried by rare instances; this item measures the typical
regime, and the two are different questions (the kill criterion says so).

### 3.4 The overlap distribution at `n = 20`, `c = 10`

Twenty fresh graphs (`pw` mean `11.25`, `β = 0.5625`, `a = 0.219`), every
ordered pair of *distinct* exact-size empty pairs at `k = pw` (23,412 of
them), the `3 × 3` table in units of `n` (`overlap_summary.csv`,
`overlap_hist.csv`, `overlap_per_graph.csv`):

| cell | measured mean | median | p90 | extremal table at this `a` | product table |
|---|---|---|---|---|---|
| `A ∩ A′` | 0.061 | 0.05 | 0.15 | 0.056 | 0.048 |
| `A ∩ R′` | 0.059 | 0.05 | 0.15 | 0.056 | 0.048 |
| `A ∩ S′` | 0.084 | 0.10 | 0.15 | 0.106 | 0.123 |
| `S ∩ S′` | **0.453** | 0.45 | 0.55 | 0.350 | 0.316 |

![Overlap of pairs of exact-size empty pairs at n = 20, c = 10, k = pw](scratch/separator_moment/03_clumping/overlap_hist.png)

*The overlap of two empty pairs on the same instance, `n = 20`, `c = 10`,
`k = pw`, over 23,412 ordered pairs of distinct pairs on 20 graphs: the
shares of `n` in `A ∩ A′`, `A ∩ R′`, `A ∩ S′` and `S ∩ S′`, with the
maximising table of the Bernoulli second moment at this `a` (solid) and
the product of the margins (dashed).*

**Is §8.5 (a)'s extremal table what instances show?** Not at `k = pw`. On
the instances, two pairs share **`0.45 n` of their separators** (`|S| =
0.56 n`, so 80% of `S`; median one vertex of `A` in `A′` and one in `R′`),
against `0.35 n` for the extremal table at this `a` and `0.32 n` for
the product: pairs on an instance are *closer* to each other through `S`
than the extremal table says, and `A′` meets `A` and `R` equally (the
symmetric picture of §3.3, not the reversed pair of the large-deviation
regime). `A ∩ S′` sits *below* both reference tables: fewer vertices of
`A` move into `S′` than independence would give, i.e. the second pair is a
small perturbation of the first that keeps most of the separator and
swaps one or two vertices — the move-class picture, with the small
classes §3.2 counts.

### 3.5 Kill verdict

**Pre-registered criterion 1: met.** At `c = 10`, `k = pw`, the slope of
`log(X₁/X₂)` is `0.000 ± 0.003` and of `log(X₁/X₃)` is `−0.003 ± 0.003`
nats per vertex, below `0.066` by more than twice the standard error (by
twenty times). **Prediction recorded: the separator count and the
closed-pair count fail item 06's kill** (`β_sep − β* < 0.02` and
`β_closed − β* < 0.02` at `c = 6` and `10`); by this instrument each
merges at most `0.01` nats per vertex, `0.003` in `β`. The prediction is at
`k = pw` on typical instances at `n ≤ 24`, not in the large-deviation
regime at `β*`, where the maximising overlap is a different table (§3.3);
**items 05–06 are kept and only item 06 decides.** Item 09, the weighted
count, is the route this item points to.

**Pre-registered criterion 2: not met.** `X₁/X₄` does not grow at
`≥ 0.15` nats per vertex (`−0.003 ± 0.004` at `c = 10`; within `0.01` of
zero everywhere at `k = pw`). The clusters on typical instances are not
fat: the move-classes merge a factor 1.4–2.5, flat in `n`. §8.5's
`e^{0.23 n}` is therefore **not the typical cluster** at these sizes — it
is the second moment's statement about the rare instances that carry
`E[X]` at `β*`, and item 04 (the planted model, which *is* that regime)
is where its cluster is measured; this item's finding is that the planted
measurement cannot be replaced by typical instances.

### 3.6 Regenerate, size range, what this does not claim

* **Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/03_clumping/run.py --workers 8`
  (stages `solve`, `count`, `rates`, `overlap`; 7 + 66 + 1 + 1 s on 8
  workers); `python3 reports/scratch/separator_moment/03_clumping/checks.py`
  (the grid check of the maximiser, the parity split, the `X₃` cross-check,
  the pilot against the fresh cells); `python3 -m pytest tests/test_separator_moment.py`
  (37 tests, 16 new: the enumeration against `exact_pairs`,
  `count_exact_pairs`, `empty_pair_count_brute` and `count_separators`;
  the pruned closed pairs against the direct enumeration and
  `X₃′ ⊆ X₃`; the down-closed family against brute force; move-classes on
  the path `P₆` and on two triangles with a pendant, against a BFS over the
  relation; the Bernoulli second moment against the enumeration of pairs
  of pairs at `n = 8, 10` and the rate against the finite form at
  `n = 30–120`; the overlap tables' margins).
* **Size range.** `n = 14–24` for the fresh graphs (`c = 4, 6, 8, 10`,
  200 per cell), `n = 20` for the pilot (137 per `c`), `n = 10–25` for the
  covers (`d = 4, 6`, `m = n`, 150 per cell); `k = pw − 1 … pw + 2`.
* **Does not claim.** Anything asymptotic: the slopes are fitted over
  six sizes at the small-size end (`n ≤ 24`, where §14 of
  `reports/ml_nature.md` found `n ≤ 40` constants failing at 125) and are
  reported with their standard errors and no extrapolation; "flat in `n`"
  means within `0.01` nats per vertex over `14–24`. Anything about the
  large-deviation regime at `β*`: the counts here are at `k = pw` on
  typical instances, and the second-moment table says the two regimes
  have different maximisers. That `β_sep` or `β_closed` will fail item
  06's kill — that is a *prediction* from this instrument, recorded as
  the kill asks, and item 06 decides it. That the overlap histogram at one
  cell (`n = 20`, `c = 10`, 20 graphs) is the picture at other `c` or
  sizes. The `pw + 2` rows are at a fixed offset from the pathwidth, not
  at a fixed `β`, and their slopes are not rates of anything.


---

## 4. The planted cluster: typical, or a rare-instance artefact of `E[X²]`? (item 04, 2026-11-01)

**Question.** Given one exact-size empty pair, how many *other* exact-size
empty pairs does the instance typically have, how far away are they, and
by what mechanism? §8.5 (a) of `reports/excess_phase_diagram.md` found
`E[X²]/E[X]² = e^{0.23 n}` at `(6, 1)`, `β*`, and §3 of this report found
that typical instances at their own pathwidth carry no such cluster. The
planted model is the large-deviation regime itself: `E[X²]/E[X]²` is the
mean of `X` under the law `P(· | P₀ empty)`, over the unconditional mean.
If the *median* of `X′ = X − 1` under that law grows at the mean's rate,
the cluster is typical and a representative that merges it gains the
whole exponent; if the median grows far slower, the second moment is
carried by rare planted instances.

**What the planted measure is, and is not.** `P(· | P₀ empty)` weights an
instance by the number of its empty pairs: an instance with `X` pairs is
drawn with probability proportional to `X`. Nothing here is a value of
`P(X > 0)` or of `P(pw ≤ k)`; the planted measure is the *right* measure
for the cluster question precisely because it is tilted by `X`. No
pathwidth is computed: the planted pair makes `X ≥ 1` by construction and
the pathwidth of a planted instance is irrelevant to the question.

**Two identities, used throughout** (both from exchangeability of the
vertex labels, which `G(n, p)` and the uniform-pattern cover model have;
both checked exactly against enumeration in `tests/test_separator_moment.py`):

1. `E[X² ] = Σ_P P(P empty) · E[X | P empty] = E[X] · E[X | P₀ empty]`, so
   **`E[X′ | P₀ empty] = E[X²]/E[X] − 1`** — the planted mean is the
   second-moment ratio times the unconditional mean, computed exactly at
   the cell's `(n, t, r)` by the `3 × 3` overlap sum (`planted_mean_gnp`,
   `planted_mean_cover`; `second_moment_exact_cover` is the general-`r`
   form of `second_moment_exact`, pinned to it at `r = t − 1`). Checked
   against a simulation of the planted law at `n = 9`
   (`test_planted_mean_is_the_mean_of_the_other_pairs_on_gnp`).
2. `Σ_P 1[P empty] / X = 1[X > 0]`, so **`P(X > 0) / E[X] = E[1/X | P₀
   empty]`** — the whole slack of the union bound at a cell is the mean of
   `1/X` under the planted law, a bounded statistic that 200 planted
   instances estimate with a standard error of `0.01–0.03`, where the mean
   of `X` itself is dominated by the tail. Checked on every labelled graph
   at `n = 6` (`test_planted_inverse_mean_is_the_union_bound_slack`).

**The events counted.** On `G(n, c/n)`: delete every `A–R` edge of a
fresh graph for a fixed `A` (`|A| = t`) and `R` (`|R| = r = N − t`), which
is exactly the conditional law. On covers at `(6, 1)`: `m = n` patterns,
each a uniform 6-set conditioned to meet at most one side (rejection
sampling; acceptance 0.28–0.43), which is exactly the conditional law
of the i.i.d.-pattern model of `CliqueCoverMoment.lean` (not the
ensemble's `fixed` generator, which repairs empty rows). `X` is the number
of ordered exact-size empty pairs (item 03's enumerator); `X′ = X − 1`;
for every other pair its `3 × 3` overlap table with `P₀` (`overlap_table`),
its Hamming distance `d = n − |A ∩ A′| − |R ∩ R′| − |S ∩ S′|` from `P₀`,
and the same distance from the *reversed* planted pair `(R, A)`, which is
itself an exact-size empty pair whenever `N` is even (`has_reverse`) and
sits at distance `N`; "far" means `d > 0.2 n`. `X₂`, `X₃`, `X₃′`, `X₄` and
the move-class of `P₀` as in §3.

### 4.1 Instances

| model | cells | per cell | instances | `k` |
|---|---|---|---|---|
| planted `G(n, c/n)` | `n ∈ {16, 20, 24, 28, 32}` × `c ∈ {6, 10}` × `β ∈ {β*(c), β*(c) + 0.1}` | 200 | 4,000 | `round(β n)`; `β*(6) = 0.1706`, `β*(10) = 0.3371` (`beta_star_gnp`, the root of `H(a, a, 1 − 2a) − c a²`) |
| planted covers `(6, 1)` | `n ∈ {16, 20, 24, 28}` × `β ∈ {β*, β* + 0.1}` | 200 | 1,600 | `β*(6, 1) = 0.5132` (`beta_star`) |

Seeds `crc32("sep04:{source}:{n}:{c}:{β label}:{i}")`; the planted sides are
the first `t` and the next `r` vertices. The realised `β = k/n` is in the
table below (rounding moves it by up to `0.03`); every prediction uses the
realised `(n, t, r)`. The whole run is **305 s on 8 workers at nice 19**
(0.6 core-hours against 3 budgeted); 7 instances of the 5,600 are censored
(more than 2 million pairs, `G(32, 6/32)` at `β* + 0.1`) and enter the
medians as "above the cap", the means without them (which biases those two
means down), and `E[1/X]` as zero.

### 4.2 The table: median against mean against prediction

Per cell; `gm` is the geometric mean over `X′ > 0`; `E[X′ | planted]` is
identity 1 at the realised sizes; the last column is the asymptotic
exponent `sup − g(a)` of `second_moment_rate_gnp` / `second_moment_rate`
at `a = (1 − β)/2`, for reference only. (`cells.csv`.)

| model | `β` | `n` | `k` | `N`, `t`, `r` | `X′ = 0` | median `X′` | p90 | max | gm (`X′ > 0`) | mean ± se | `E[X′ ∣ planted]` | top 10% share of `ΣX′` | `log med / n` | `log mean / n` | `log E / n` | asymptotic `sup − g` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `G(n, 6/n)` | `β*` | 16 | 3 | 13, 7, 6 | 30% | 2 | 29.1 | 486 | 5.72 | 12.37 ± 2.79 | 16.49 | 0.64 | 0.043 | 0.157 | 0.175 | 0.396 |
| `G(n, 6/n)` | `β*` | 20 | 3 | 17, 9, 8 | 18% | 3 | 62.1 | 1493 | 8.99 | 42.32 ± 10.84 | 29.7 | 0.79 | 0.055 | 0.187 | 0.170 | 0.338 |
| `G(n, 6/n)` | `β*` | 24 | 4 | 20, 10, 10 | 0% | 19 | 316.2 | 3173 | 15.96 | 126.69 ± 24.48 | 168 | 0.75 | 0.123 | 0.202 | 0.213 | 0.364 |
| `G(n, 6/n)` | `β*` | 28 | 5 | 23, 12, 11 | 4% | 39 | 988.9 | 17712 | 54.93 | 639.75 ± 152.57 | 928.54 | 0.84 | 0.131 | 0.231 | 0.244 | 0.382 |
| `G(n, 6/n)` | `β*` | 32 | 5 | 27, 14, 13 | 7% | 64 | 737.4 | 120314 | 70.02 | 1478.51 ± 655.35 | 1538 | 0.94 | 0.130 | 0.228 | 0.229 | 0.348 |
| `G(n, 6/n)` | `β* + 0.1` | 16 | 4 | 12, 6, 6 | 0% | 13 | 87 | 3813 | 10.26 | 64.35 ± 20.48 | 50.5 | 0.76 | 0.160 | 0.260 | 0.245 | 0.490 |
| `G(n, 6/n)` | `β* + 0.1` | 20 | 5 | 15, 8, 7 | 3% | 35 | 371.9 | 6800 | 38.86 | 179.81 ± 39.34 | 291.83 | 0.67 | 0.178 | 0.260 | 0.284 | 0.490 |
| `G(n, 6/n)` | `β* + 0.1` | 24 | 6 | 18, 9, 9 | 0% | 146 | 3561.8 | 25899 | 161.14 | 1442.13 ± 268.8 | 1791.02 | 0.74 | 0.208 | 0.303 | 0.312 | 0.490 |
| `G(n, 6/n)` | `β* + 0.1` | 28 | 8 | 20, 10, 10 | 0% | 3219 | 38406.6 | 739273 | 2518.27 | 21400 ± 4951.56 | 35937.9 | 0.72 | 0.288 | 0.356 | 0.375 | 0.537 |
| `G(n, 6/n)` | `β* + 0.1` | 32 | 9 | 23, 12, 11 | 0% | 11067 | 161619 | 1.65489e+06 | 10440.4 | 78278.7 ± 14632.4 (7 censored) | 230946 | 0.67 | 0.291 | 0.352 | 0.386 | 0.531 |
| `G(n, 10/n)` | `β*` | 16 | 5 | 11, 6, 5 | 74% | 0 | 2 | 11 | 2.11 | 0.83 ± 0.15 | 0.7 | 0.78 | −∞ | -0.012 | -0.022 | 0.273 |
| `G(n, 10/n)` | `β*` | 20 | 7 | 13, 7, 6 | 53% | 0 | 10 | 38 | 3.22 | 3.02 ± 0.46 | 4.23 | 0.66 | −∞ | 0.055 | 0.072 | 0.315 |
| `G(n, 10/n)` | `β*` | 24 | 8 | 16, 8, 8 | 0% | 1 | 33 | 251 | 2.83 | 11.58 ± 1.99 | 11.56 | 0.64 | 0.000 | 0.102 | 0.102 | 0.296 |
| `G(n, 10/n)` | `β*` | 28 | 9 | 19, 10, 9 | 36% | 1 | 43.2 | 6724 | 7.31 | 58.92 ± 34.32 | 22.61 | 0.92 | 0.000 | 0.146 | 0.111 | 0.283 |
| `G(n, 10/n)` | `β*` | 32 | 11 | 21, 11, 10 | 14% | 5.5 | 127.4 | 1104 | 11.29 | 47.09 ± 8.47 | 112.05 | 0.68 | 0.053 | 0.120 | 0.147 | 0.308 |
| `G(n, 10/n)` | `β* + 0.1` | 16 | 7 | 9, 5, 4 | 45% | 1 | 9.1 | 113 | 3.13 | 4.12 ± 0.86 | 3.54 | 0.69 | 0.000 | 0.089 | 0.079 | 0.431 |
| `G(n, 10/n)` | `β* + 0.1` | 20 | 9 | 11, 6, 5 | 14% | 8 | 62 | 367 | 10.85 | 23.34 ± 3.09 | 25.37 | 0.52 | 0.104 | 0.158 | 0.162 | 0.448 |
| `G(n, 10/n)` | `β* + 0.1` | 24 | 10 | 14, 7, 7 | 0% | 14 | 125.6 | 2813 | 11.28 | 78.05 ± 19.98 | 59.84 | 0.79 | 0.110 | 0.182 | 0.171 | 0.403 |
| `G(n, 10/n)` | `β* + 0.1` | 28 | 12 | 16, 8, 8 | 0% | 58 | 707.8 | 11727 | 52.12 | 396.66 ± 91.84 | 377.72 | 0.76 | 0.145 | 0.214 | 0.212 | 0.419 |
| `G(n, 10/n)` | `β* + 0.1` | 32 | 14 | 18, 9, 9 | 0% | 227 | 3220.4 | 69365 | 190.47 | 1792.35 ± 462.26 | 2534.07 | 0.78 | 0.170 | 0.234 | 0.245 | 0.431 |
| cover `(6, 1)` | `β*` | 16 | 8 | 8, 4, 4 | 0% | 1 | 9 | 29 | 1.4 | 2.39 ± 0.28 | 3.03 | 0.48 | 0.000 | 0.054 | 0.069 | 0.223 |
| cover `(6, 1)` | `β*` | 20 | 10 | 10, 5, 5 | 0% | 1 | 11 | 111 | 1.68 | 4.41 ± 0.79 | 5.61 | 0.59 | 0.000 | 0.074 | 0.086 | 0.223 |
| cover `(6, 1)` | `β*` | 24 | 12 | 12, 6, 6 | 0% | 1 | 15 | 167 | 2.75 | 10.66 ± 1.87 | 10.79 | 0.65 | 0.000 | 0.099 | 0.099 | 0.223 |
| cover `(6, 1)` | `β*` | 28 | 14 | 14, 7, 7 | 0% | 1 | 44.4 | 911 | 4.15 | 22.92 ± 5.76 | 21.4 | 0.73 | 0.000 | 0.112 | 0.109 | 0.223 |
| cover `(6, 1)` | `β* + 0.1` | 16 | 10 | 6, 3, 3 | 0% | 1 | 19 | 39 | 2.75 | 5.69 ± 0.53 | 6.26 | 0.41 | 0.000 | 0.109 | 0.115 | 0.322 |
| cover `(6, 1)` | `β* + 0.1` | 20 | 12 | 8, 4, 4 | 0% | 3 | 29 | 251 | 4.11 | 12.4 ± 2.04 | 12.72 | 0.55 | 0.055 | 0.126 | 0.127 | 0.298 |
| cover `(6, 1)` | `β* + 0.1` | 24 | 15 | 9, 5, 4 | 8% | 20 | 154.2 | 1538 | 21.84 | 63.45 ± 11.47 | 62.97 | 0.61 | 0.125 | 0.173 | 0.173 | 0.322 |
| cover `(6, 1)` | `β* + 0.1` | 28 | 17 | 11, 6, 5 | 4% | 28.5 | 206.9 | 3498 | 28.42 | 110.01 ± 22.61 | 124.86 | 0.65 | 0.120 | 0.168 | 0.172 | 0.304 |

What the table says:

- **The formula and the enumerator agree where the tail is sampled.** In
  20 of the 26 uncensored cells the sample mean of `X′` is within two
  standard errors of `E[X²]/E[X] − 1`; the six exceptions are *all below*
  the prediction (`z = −2.3` to `−7.7`), the largest at `G(32, 10/32)`,
  `β*` (47 ± 8 against 112), and the censored cell is below it by its
  censoring. A sample mean under a heavy tail is biased down when the
  instances that carry the mean are rarer than one in 200, and these
  cells are where the top 10% carry 68–94% of the sum. The identity is
  checked exactly at small `n` in the tests; here the agreement in 20
  cells and the sign of every disagreement are what the enumerator and
  the formula could show.
- **The mean is carried by the tail.** The top 10% of instances carry
  48–94% of `ΣX′` at `β*` (42–79% at `β* + 0.1`); at `G(32, 6/32)`, `β*`,
  the median is 64 against a mean of 1,479 and a maximum of 120,314. The
  planted mean is not what a planted instance looks like.
- **At `β*` the median planted instance has a small cluster.** `G(n, 6/n)`:
  median `X′` = 2, 3, 19, 39, 64 at `n = 16 … 32`; `G(n, 10/n)`: 0, 0, 1, 1,
  5.5 (the "1" is the reversed pair where `N` is even); covers `(6, 1)`:
  **`X′ = 1` at every size, the reversed pair and nothing else** (`N` is
  even in all four cells), with `X′ ≥ 2` on 16, 21, 36 and 47% of the
  instances at `n = 16, 20, 24, 28` — growing with `n`, but not yet the
  median — and `X′ = 1` on the rest. At `β* + 0.1` the counts are large everywhere (median
  11,067 at `G(32, 6/32)`), but there `E[X] = e^{g n}` with `g > 0` and the
  other pairs are the instance's own population, not a cluster of `P₀`
  (§4.4).
- **Finite sizes.** The exact planted mean's exponent at `n = 32` is
  `0.23` (`c = 6`), `0.15` (`c = 10`), `0.11` (covers, `n = 28`) against
  asymptotic `0.35, 0.31, 0.22`: at these `n` nothing is near its limit,
  and the asymptotic `0.23` of §8.5 (a) is at `n = ∞`; the finite exact
  value is what the medians are compared with.

### 4.3 Growth in `n`, and the fork

OLS slopes in `n` (nats per vertex, fitted over five sizes for the cell
statistics and over 645–987 instances for the per-instance one; `slopes.csv`):

| model | `β` | sizes | slope `log(median X′)` | slope `log E[X′]` | slope `log(mean X′)` | per-instance slope `log X′` (`X′ > 0`) | at the largest `n`: `log med / n` | `log E / n` | ratio |
|---|---|---|---|---|---|---|---|---|---|
| cover `(6, 1)` | `β*` | 16–28 | 0.000 ± 0.000 | 0.163 ± 0.003 | 0.192 ± 0.009 | 0.094 ± 0.010 | 0.000 | 0.109 | **0.00** |
| cover `(6, 1)` | `β* + 0.1` | 16–28 | 0.299 ± 0.051 | 0.265 ± 0.032 | 0.263 ± 0.035 | 0.216 ± 0.012 | 0.120 | 0.172 | **0.69** |
| `G(n, 6/n)` | `β*` | 16–32 | 0.237 ± 0.033 | 0.313 ± 0.034 | 0.307 ± 0.015 | 0.172 ± 0.012 | 0.130 | 0.229 | **0.57** |
| `G(n, 6/n)` | `β* + 0.1` | 16–32 | 0.450 ± 0.050 | 0.542 ± 0.031 | 0.475 ± 0.039 | 0.450 ± 0.012 | 0.291 | 0.386 | **0.75** |
| `G(n, 10/n)` | `β*` | 16–32 | 0.213 ± 0.123 | 0.296 ± 0.027 | 0.276 ± 0.045 | 0.116 ± 0.013 | 0.053 | 0.147 | **0.36** |
| `G(n, 10/n)` | `β* + 0.1` | 16–32 | 0.321 ± 0.029 | 0.396 ± 0.026 | 0.375 ± 0.010 | 0.249 ± 0.012 | 0.170 | 0.245 | **0.69** |

**The fork, by the item's letter** (`log(median X′)/n` against `log
E[X′ | planted]/n` at the largest `n`): ratio **0.57** at `G(32, 6/32)`,
`β*` (within a factor 2 — "typical"); **0.36** at `G(32, 10/32)`, `β*`
(between a quarter and a half — "both"); **0 on covers at `β*`** (the
median has no pair beyond the reverse at any size — "artefact"); 0.69–0.75
at `β* + 0.1` ("typical", but see §4.4: there the pairs are not a cluster
of `P₀`). The growth rates say the same with less noise: at `β*` the
median grows at `0.24 ± 0.03` (`c = 6`) against the mean's `0.31 ± 0.03`,
and the per-instance geometric mean at `0.17 ± 0.01` (`c = 6`) and `0.12 ±
0.01` (`c = 10`) against `0.31` and `0.30`; on covers the median does not
grow at all (`0.00`) against `0.16`. So at `β*`: **the cluster exists on
the typical planted instance and grows exponentially on `G(n, c/n)` at
roughly half the mean's rate, and does not grow at all on the `(6, 1)`
covers, where §8.5's `e^{0.23 n}` lives.** The second moment at `(6, 1)`
is a rare-instance artefact; on `G(n, c/n)` it is half typical and half
tail, and the "in between" branch of the fork applies.

### 4.4 Where the other pairs are: two lobes, and an empty middle

![Hamming distance of the other exact-size empty pairs from the planted pair, per cell at the largest n](scratch/separator_moment/04_planted/distance_hist.png)

*Distance from the planted pair in units of `n`, pooled over the 200
planted instances of each cell at the largest `n` (`distance_hist.csv`);
the solid line is the far/near cut at `0.2 n`, the dashed line the
position of the reversed pair, `N/n`.*

At `β*` the histogram is **bimodal with an empty middle**: one lobe at
`d ≈ 0.1–0.4 n` (perturbations of `P₀`), one at `d ≈ N/n ± 0.15` (perturbations
of the reversed pair), and almost nothing at `d ≈ 0.5–0.6 n` on `G(32, 6/32)`
(5,000 of 295,701 pairs at `d = 17–19`, 1.7%) and nothing at all on covers
(none at `d = 10–11`, four of 4,584 at `d = 9–12`). At `β* + 0.1` on `G(n, c/n)` the middle
fills and the distribution is broad and unimodal around `0.55–0.6 n`:
the other pairs are then the instance's whole pair population. The shares
(pooled over pairs; `cells.csv`):

| model | `β` | `n` | share far (`d > 0.2 n`) | within `0.05 n` of `P₀` / of `P₀` or its reverse | `0.1 n` | `0.2 n` | `0.3 n` | per-instance median share within `0.2 n` of `P₀` or reverse | far pairs with `∣A′ ∩ R∣ ≥ ∣A′ ∩ A∣` | median move-class of `P₀` (max) | `X/X₄` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `G(n, 6/n)` | `β*` | 16 | 0.77 | 0.000 / 0.000 | 0.000 / 0.033 | 0.234 / 0.434 | 0.390 / 0.675 | 0.79 | 0.53 | 1 (356) | 1.81 |
| `G(n, 6/n)` | `β*` | 24 | 0.87 | 0.000 / 0.008 | 0.039 / 0.086 | 0.134 / 0.276 | 0.295 / 0.598 | 0.86 | 0.59 | 2 (1423) | 3.50 |
| `G(n, 6/n)` | `β*` | 28 | 0.90 | 0.000 / 0.001 | 0.012 / 0.020 | 0.102 / 0.183 | 0.296 / 0.548 | 0.63 | 0.54 | 9 (10680) | 4.79 |
| `G(n, 6/n)` | `β*` | 32 | 0.90 | 0.000 / 0.001 | 0.011 / 0.019 | 0.098 / 0.176 | 0.289 / 0.507 | 0.88 | 0.50 | 8 (71548) | 5.17 |
| `G(n, 6/n)` | `β* + 0.1` | 16 | 0.93 | 0.000 / 0.015 | 0.000 / 0.015 | 0.073 / 0.162 | 0.137 / 0.290 | 0.55 | 0.60 | 1 (3810) | 2.76 |
| `G(n, 6/n)` | `β* + 0.1` | 24 | 0.97 | 0.000 / 0.001 | 0.006 / 0.013 | 0.034 / 0.068 | 0.160 / 0.322 | 0.24 | 0.54 | 37.5 (25712) | 7.38 |
| `G(n, 6/n)` | `β* + 0.1` | 28 | 0.99 | 0.000 / 0.000 | 0.001 / 0.002 | 0.012 / 0.024 | 0.082 / 0.163 | 0.07 | 0.54 | 1151 (243332) | 16.44 |
| `G(n, 6/n)` | `β* + 0.1` | 32 | 0.99 | 0.000 / 0.000 | 0.001 / 0.001 | 0.012 / 0.023 | 0.062 / 0.122 | 0.08 | 0.51 | 4196 (267543) | 20.38 |
| `G(n, 10/n)` | `β*` | 16 | 0.43 | 0.000 / 0.000 | 0.000 / 0.066 | 0.572 / 0.958 | 0.602 / 1.000 | 1.00 | 0.93 | 1 (7) | 1.15 |
| `G(n, 10/n)` | `β*` | 24 | 0.68 | 0.000 / 0.086 | 0.160 / 0.406 | 0.320 / 0.726 | 0.421 / 0.929 | 1.00 | 0.80 | 1 (125) | 1.66 |
| `G(n, 10/n)` | `β*` | 28 | 0.84 | 0.000 / 0.004 | 0.046 / 0.074 | 0.156 / 0.289 | 0.357 / 0.711 | 1.00 | 0.60 | 1 (2759) | 1.87 |
| `G(n, 10/n)` | `β*` | 32 | 0.64 | 0.000 / 0.004 | 0.102 / 0.175 | 0.361 / 0.672 | 0.493 / 0.903 | 1.00 | 0.72 | 1 (654) | 2.19 |
| `G(n, 10/n)` | `β* + 0.1` | 16 | 0.73 | 0.000 / 0.000 | 0.000 / 0.028 | 0.267 / 0.481 | 0.445 / 0.766 | 1.00 | 0.55 | 1 (96) | 1.36 |
| `G(n, 10/n)` | `β* + 0.1` | 24 | 0.89 | 0.000 / 0.013 | 0.039 / 0.091 | 0.112 / 0.237 | 0.262 / 0.537 | 0.78 | 0.57 | 1 (1407) | 2.37 |
| `G(n, 10/n)` | `β* + 0.1` | 28 | 0.90 | 0.000 / 0.003 | 0.016 / 0.034 | 0.095 / 0.193 | 0.278 / 0.558 | 0.46 | 0.57 | 9 (5652) | 3.54 |
| `G(n, 10/n)` | `β* + 0.1` | 32 | 0.94 | 0.000 / 0.001 | 0.006 / 0.013 | 0.059 / 0.119 | 0.159 / 0.319 | 0.34 | 0.55 | 19 (67758) | 4.05 |
| cover `(6, 1)` | `β*` | 16 | 0.74 | 0.000 / 0.418 | 0.000 / 0.418 | 0.264 / 0.946 | 0.291 / 1.000 | 1.00 | 0.96 | 1 (15) | 1.28 |
| cover `(6, 1)` | `β*` | 28 | 0.63 | 0.000 / 0.044 | 0.158 / 0.359 | 0.370 / 0.784 | 0.478 / 1.000 | 1.00 | 0.83 | 1 (456) | 2.92 |
| cover `(6, 1)` | `β* + 0.1` | 16 | 0.71 | 0.000 / 0.176 | 0.000 / 0.176 | 0.292 / 0.759 | 0.390 / 0.951 | 1.00 | 0.84 | 1 (20) | 1.98 |
| cover `(6, 1)` | `β* + 0.1` | 28 | 0.77 | 0.000 / 0.002 | 0.060 / 0.082 | 0.227 / 0.328 | 0.567 / 0.810 | 0.70 | 0.42 | 7.5 (2898) | 5.90 |

Three readings. (i) **Few other pairs are small perturbations of `P₀`
alone**: within `0.05 n` of `P₀` or its reverse sit 0–4% of the other
pairs at the largest `n` (the single-swap neighbours are a negligible
share); within `0.1 n` of `P₀` itself, 1% (`c = 6`), 10% (`c = 10`) and 16%
(covers); within `0.1 n` of `P₀` *or its reverse*, 2%, 18% and 36%. Within
`0.3 n` of either, 51% (`c = 6`), 90% (`c = 10`) and 99.96% (covers). (ii) **The per-instance
median is tighter than the pool**: on the median planted instance at
`β*`, 88% (`c = 6`), 100% (`c = 10`, covers) of the other pairs sit within
`0.2 n` of `P₀` or its reverse, against 18%, 67%, 78% pooled — the far pairs
belong to the rare instances with large `X′`, which is the tail of §4.2
again. (iii) **The reversed pair is half the cluster.** At `c = 6` the far
pairs split evenly between the two orientations (50–59% have `|A′ ∩ R| ≥
|A′ ∩ A|` over the five sizes); at `c = 10` and on covers the reversed
lobe dominates (72%, 83% at the largest `n`). The move-class of `P₀`
(single swaps) holds 8–9 pairs at the median on `G(n, 6/n)`, `β*`, at
`n = 28–32` (1–2 below; max 71,548), and 1 — `P₀` alone — at `c = 10` and
on covers; `X/X₄` is 1.2–5.2 at `β*` and up to 20 at `β* + 0.1`.

The far and near pairs have different mean overlap tables
(`overlap_far_near.csv`, `n = 32`, `c = 6`, `β*`, in units of `n`): near
pairs keep `A ∩ A′ = 0.39`, `R ∩ R′ = 0.36`, `S ∩ S′ = 0.095` with
`A ∩ R′ = R ∩ A′ = 0.02` (`P₀` with a few swaps); far pairs average `A ∩ A′
= A ∩ R′ = R ∩ A′ = 0.19` — the average of the two lobes, not a table any
pair has. At `c = 10` the far table is the reversed pair's (`A ∩ R′ = R ∩
A′ = 0.21`, `A ∩ A′ = 0.08`), which is §8.5 (a)'s extremal table with
`S ∩ S′ = 0.25` of `|S| = 0.34 n`.

### 4.5 The mechanism

For every far pair, the vertices of `S` that joined a side (`S ∩ (A′ ∪
R′)`), their degree into the planted sides `A ∪ R`, and how many of those
neighbours were *evicted* into `S′` (a side neighbour of a vertex now in
`A′` must be in `A′` or in `S′`); against the degree law of all `S`
vertices (`mechanism.csv`, `mechanism_summary.csv`; the mechanism is
sampled at 200,000 far pairs per instance where there are more):

| model | `β` | `n` | moved `S` vertices (far pairs) | their planted-side degree: mean | share `≤ 1` | all `S` vertices: mean | share `≤ 1` | evicted neighbours: mean | share 0 | share `≤ 1` |
|---|---|---|---|---|---|---|---|---|---|---|
| `G(n, 6/n)` | `β*` | 16 | 3,141 | 2.87 | 0.23 | 4.95 | 0.017 | 0.80 | 0.42 | 0.80 |
| `G(n, 6/n)` | `β*` | 32 | 864,223 | 2.67 | 0.24 | 5.11 | 0.028 | 0.64 | 0.51 | 0.87 |
| `G(n, 6/n)` | `β* + 0.1` | 16 | 24,378 | 2.21 | 0.35 | 4.53 | 0.028 | 0.83 | 0.38 | 0.82 |
| `G(n, 6/n)` | `β* + 0.1` | 32 | 38,802,029 | 3.07 | 0.14 | 4.29 | 0.056 | 1.11 | 0.30 | 0.69 |
| `G(n, 10/n)` | `β*` | 16 | 65 | 3.79 | 0.00 | 6.83 | 0.000 | 0.69 | 0.42 | 0.89 |
| `G(n, 10/n)` | `β*` | 32 | 17,567 | 4.45 | 0.02 | 6.59 | 0.004 | 1.35 | 0.18 | 0.60 |
| `G(n, 10/n)` | `β* + 0.1` | 16 | 1,136 | 3.18 | 0.09 | 5.58 | 0.003 | 1.29 | 0.17 | 0.64 |
| `G(n, 10/n)` | `β* + 0.1` | 32 | 1,697,525 | 3.80 | 0.03 | 5.68 | 0.009 | 1.91 | 0.10 | 0.38 |
| cover `(6, 1)` | `β*` | 28 | 5,636 | 5.10 | 0.00 | 9.09 | 0.000 | 1.27 | 0.21 | 0.64 |
| cover `(6, 1)` | `β* + 0.1` | 28 | 58,721 | 4.25 | 0.04 | 6.72 | 0.004 | 2.08 | 0.07 | 0.33 |

**The hypothesis holds in direction and not in its strong form.** The
separator vertices that recombine into a side have about half the
planted-side degree of a typical `S` vertex (2.7 against 5.1 at `c = 6`,
4.4 against 6.6 at `c = 10`, 5.1 against 9.1 on covers at `β*`), but they
are not degree-zero vertices: at the largest sizes 0–1% have no side
neighbour (14% at `G(16, 6/16)`) and 0.1–24% at most one. What is small is the number they *evict*: at `β*` the
moved vertex evicts no neighbour in 18–51% of cases and at most one in
60–87%, with a mean of 0.6–1.4 — the rest of its side neighbours are on
its own new side. So the recombination is "a low-degree separator vertex
whose side neighbours mostly lie on one side joins that side, pushing
one or two of its other-side neighbours into the separator", and on the
reversed lobe the same with the sides exchanged.

### 4.6 The union bound's slack, measured directly

By identity 2, `P(X > 0)/E[X] = E[1/X | P₀ empty]`, and the planted sample
gives it with a standard error of `0.01–0.03` (`cells.csv`,
`inv_X_mean`). The conversion to `β` uses the pair exponent's slope at
`β*`: `3.38` per unit of `β` at `c = 6`, `3.30` at `c = 10`, `2.82` on
`(6, 1)` covers (computed here by central differences of
`gnp_pair_rate` / `rate`; the header's `3.3–3.4` for `c = 6–10`).

| model | `β` | `n` | `E_planted[1/X]` ± se | `−log E_planted[1/X]` (nats) | per vertex | in `β` | `log E[X′ ∣ planted] / n` |
|---|---|---|---|---|---|---|---|
| `G(n, 6/n)` | `β*` | 16 | 0.453 ± 0.027 | 0.79 | 0.050 | 0.015 | 0.175 |
| `G(n, 6/n)` | `β*` | 20 | 0.337 ± 0.025 | 1.09 | 0.054 | 0.016 | 0.170 |
| `G(n, 6/n)` | `β*` | 24 | 0.155 ± 0.013 | 1.86 | 0.078 | 0.023 | 0.213 |
| `G(n, 6/n)` | `β*` | 28 | 0.116 ± 0.016 | 2.15 | 0.077 | 0.023 | 0.244 |
| `G(n, 6/n)` | `β*` | 32 | 0.124 ± 0.018 | 2.08 | 0.065 | 0.019 | 0.229 |
| `G(n, 6/n)` | `β* + 0.1` | 16 | 0.183 ± 0.014 | 1.70 | 0.106 | 0.031 | 0.245 |
| `G(n, 6/n)` | `β* + 0.1` | 20 | 0.105 ± 0.014 | 2.25 | 0.113 | 0.033 | 0.284 |
| `G(n, 6/n)` | `β* + 0.1` | 24 | 0.043 ± 0.007 | 3.14 | 0.131 | 0.039 | 0.312 |
| `G(n, 6/n)` | `β* + 0.1` | 28 | 0.004 ± 0.001 | 5.41 | 0.193 | 0.057 | 0.375 |
| `G(n, 6/n)` | `β* + 0.1` | 32 | 0.003 ± 0.001 | 5.95 | 0.186 | 0.055 | 0.386 |
| `G(n, 10/n)` | `β*` | 16 | 0.835 ± 0.021 | 0.18 | 0.011 | 0.003 | -0.022 |
| `G(n, 10/n)` | `β*` | 20 | 0.667 ± 0.027 | 0.41 | 0.020 | 0.006 | 0.072 |
| `G(n, 10/n)` | `β*` | 24 | 0.344 ± 0.014 | 1.07 | 0.044 | 0.013 | 0.102 |
| `G(n, 10/n)` | `β*` | 28 | 0.499 ± 0.029 | 0.70 | 0.025 | 0.008 | 0.111 |
| `G(n, 10/n)` | `β*` | 32 | 0.291 ± 0.024 | 1.23 | 0.039 | 0.012 | 0.147 |
| `G(n, 10/n)` | `β* + 0.1` | 16 | 0.613 ± 0.027 | 0.49 | 0.031 | 0.009 | 0.079 |
| `G(n, 10/n)` | `β* + 0.1` | 20 | 0.260 ± 0.023 | 1.35 | 0.067 | 0.020 | 0.162 |
| `G(n, 10/n)` | `β* + 0.1` | 24 | 0.176 ± 0.014 | 1.74 | 0.072 | 0.022 | 0.171 |
| `G(n, 10/n)` | `β* + 0.1` | 28 | 0.081 ± 0.010 | 2.51 | 0.090 | 0.027 | 0.212 |
| `G(n, 10/n)` | `β* + 0.1` | 32 | 0.039 ± 0.007 | 3.25 | 0.102 | 0.031 | 0.245 |
| cover `(6, 1)` | `β*` | 16 | 0.439 ± 0.010 | 0.82 | 0.051 | 0.018 | 0.069 |
| cover `(6, 1)` | `β*` | 20 | 0.416 ± 0.012 | 0.88 | 0.044 | 0.016 | 0.086 |
| cover `(6, 1)` | `β*` | 24 | 0.348 ± 0.015 | 1.06 | 0.044 | 0.016 | 0.099 |
| cover `(6, 1)` | `β*` | 28 | 0.298 ± 0.016 | 1.21 | 0.043 | 0.015 | 0.109 |
| cover `(6, 1)` | `β* + 0.1` | 16 | 0.323 ± 0.014 | 1.13 | 0.071 | 0.025 | 0.115 |
| cover `(6, 1)` | `β* + 0.1` | 20 | 0.274 ± 0.015 | 1.29 | 0.065 | 0.023 | 0.127 |
| cover `(6, 1)` | `β* + 0.1` | 24 | 0.172 ± 0.020 | 1.76 | 0.073 | 0.026 | 0.173 |
| cover `(6, 1)` | `β* + 0.1` | 28 | 0.117 ± 0.015 | 2.15 | 0.077 | 0.027 | 0.172 |

At `β*` and the largest sizes the union bound is loose by **0.065 nats
per vertex at `c = 6`, 0.039 at `c = 10`, 0.043 on `(6, 1)` covers** —
**0.019, 0.012 and 0.015 in `β`** — against planted-mean exponents of
0.23, 0.15 and 0.11 that the second-moment ratio would suggest. The
total slack in nats (`−log E[1/X]`) is 0.8, 1.1, 1.9, 2.2, 2.1 at `n = 16
… 32` on `G(n, 6/n)` and 0.8, 0.9, 1.1, 1.2 on covers at `n = 16 … 28`:
growing slowly and sub-linearly at these sizes, so the per-vertex figures
above are upper estimates of the rate and the limit is not determined by
this instrument. The rows at `β* + 0.1` are not a gain in the constant:
there `E[X] = e^{g n}` with `g > 0` and `E[X]/P(X > 0) ≥ E[X]`.

This is the number items 09, 11 and 12 need, and it is small: the *entire*
union-bound slack at these cells, if the per-vertex figure held
asymptotically, is `0.012–0.019` in `β`, below the brief's kill of `0.02`
for any single representative count and consistent with §3's prediction
(`≤ 0.003` for the separator and closure) plus the reversed lobe (a factor
2 where `N` is even) plus the component flips. The ideal weighted count
`Y = Σ_P 1[P empty]/X` is exactly `1[X > 0]`, so no choice of `Z ≤ X` in
item 09 can gain more than this at the same `(n, k)`.

### 4.7 Kill verdict (the fork), and what it sends on

**Stated as a fork, decided per model.** On `G(n, c/n)` at `β*` the
ratio is 0.57 (`c = 6`) and 0.36 (`c = 10`): the letter says "typical" at
`c = 6` and "in between" at `c = 10`; the growth rates (median at about
half the mean's rate; per-instance geometric mean at 0.4–0.55 of it) put
both in the item's middle branch, and **both are written up with the
numbers**. On `(6, 1)` covers at `β*` the median `X′` is 1 — the reversed
pair — at every size and the ratio is 0: **the `e^{0.23 n}` of §8.5 (a)
is a rare-instance artefact of `E[X²]` on the cell it was computed for**,
and the closed-pair count is near-tight for `P(X > 0)` there in the sense
of identity 2: the union bound's measured slack is `0.04` nats per vertex
(`0.015` in `β`).

For **item 09**: the weighted count's gain is bounded by §4.6 at these
sizes (`0.012–0.019` in `β` at `β*`), and the planted lower tail is
dominated by instances with `X ≤ 2` (the pair and its reverse) on covers
(53–84% of planted instances at `n = 28 … 16`) and by `X ≤ 65` on
`G(32, 6/32)`: item 09 is
reduced to the paragraph the fork prescribes, with the Laplace-transform
computation optional. For **item 12**: say that `P(X > 0)` is within
`e^{0.04–0.07 n}` of `E[X]` at `n ≤ 32` (measured, by identity 2), that the
remaining gap to the fitted slopes (`0.08–0.10` in `β` on `G(n, c/n)`,
`0.06` on `(6, 1)`) is therefore mostly the **necessary condition** — empty
pairs exist on instances whose pathwidth is larger — and not the union
bound; and that the cluster around a planted pair is two lobes (the pair
and its reverse, each with its single-swap perturbations) with an empty
middle at `β*`.

### 4.8 Regenerate, size range, what this does not claim

* **Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/04_planted/run.py --workers 8`
  (stages `run`, `stats`, `draw`; 305 + 1 + 1 s; `--probe` times the
  largest cells on three instances each); `python3 -m pytest
  tests/test_separator_moment.py` (50 tests, 14 new: planting deletes
  exactly the forbidden edges and is symmetric and idempotent; the planted
  cover meets at most one side per pattern; the overlap table sums to `n`,
  agrees with `overlap_tables` and with the Hamming distance; `lq_sides`
  against `lq` and against counting; `second_moment_exact_cover` against
  `second_moment_exact` at `r = t − 1`; identity 1 against simulation and
  against the finite forms; identity 2 on every labelled graph at `n = 6`;
  `beta_star_gnp` against the record).
* **Size range.** `n = 16–32` planted `G(n, c/n)` at `c = 6, 10`; `n =
  16–28` planted `(6, 1)` covers; `β ∈ {β*, β* + 0.1}` rounded to integer
  `k`; 200 instances per cell.
* **Does not claim.** A value of `P(X > 0)` or `P(pw ≤ k)`: the planted
  law weights instances by `X`. Anything asymptotic: the fork is decided
  at `n ≤ 32` with the growth in `n` beside it, the per-vertex slack of
  §4.6 is sub-linear in `n` over the range and is an upper estimate of its
  rate, and the exact planted mean at `n = 32` is itself a third below its
  limit. That the mechanism of §4.5 is the only one: it is the dominant
  one on far pairs at these sizes. That `β_sep` or `β_closed` fail item
  06's kill — §4.6 makes that likelier than §3 did, and item 06 decides
  it. That the `0.23` of §8.5 (a) is wrong: it is the planted mean's
  asymptotic exponent and this item measured its finite form exactly
  (identity 1) and found it correct; what is withdrawn is the reading that
  it is the typical cluster.

---

## 5. The inner probability, exactly: `P(G(N, p)` has a balanced empty bipartition`)` (item 05, 2026-11-01)

**Question (C of the brief).** For a fixed `k`-set `S`, `G − S` is
`G(N, p)` with `N = n − k`. What is `P_N(E_bip)` exactly at small `N`, what
is its exponential rate in `N`, and how much smaller is it than the
product bound `C(N, t)(1 − p)^{t(N − t)}` that the pair count uses for the
same event?

**Events counted.** `E_bip` = the components of `G(N, p)` can be grouped
into two sides of sizes `t = ⌈N/2⌉` and `N − t`; `E_relax` = no component
has more than `t` vertices (`E_bip ⊆ E_relax`, §2.2). The product bound is
the union bound over the `C(N, t)` bipartitions, each empty with
probability `(1 − p)^{t(N − t)}`; when `N` is even it counts every
bipartition twice. The finite bounds at a pilot cell are
`B_pair = C(n, t) C(n − t, t − 1)(1 − p)^{t(t − 1)}` (the Lean convention of
`FirstMoment.lean`, `finite_bound.py`, with `|R| = t − 1`),
`B_xpair = C(n, k) · C(N, t)(1 − p)^{t(N − t)}` (the exact-size pair count,
sides `t` and `N − t`), `B_sep = C(n, k) · P_N(E_bip)` and
`B_rel = C(n, k) · P_N(E_relax)`; each is an upper bound on `P(pw ≤ k)`
(L1′, §2.2; the separator form is item 08's theorem on paper).

**Size range.** `P_N(E_bip)` exact for `N ≤ 120` (the item asked for 60,
80 if cheap); `P_N(E_relax)` exact to `N = 400`; the finite table at
`n = 60, 120`, `c = 3, 4, 6, 8, 10`, every `k`; the rate at
`c′ ∈ {2, 3, 4, 5, 6.6, 8, 10}`. Checks: Gilbert's recursion against the
enumeration of every labelled graph at `j ≤ 6` and Monte Carlo at `j = 20`;
the partition law sums to one at `N ≤ 20`; `P_N(E_bip)` against the
enumeration of every labelled graph at `N ≤ 6` (every `t`) and at `N = 7`
(2,097,152 graphs) and Monte Carlo at `N = 20`, `p = 0.1`;
`P(E_bip) ≤ P(E_relax) ≤ 1` and `P(E_bip) ≤` product bound on a grid
(`run.log`).

**Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/05_inner/run.py --max-N 120`
(stages `check`, `inner`, `rates`, `draw`; 9 + 193 + 24 + 2 s on 8 workers
at nice 19, about 0.5 core-hours against 1 budgeted; `--max-N 60` is the
item's command and takes 40 s less). Outputs beside it: `inner.csv` (every
`(n, c, k)`: the four finite bounds and the three inner quantities),
`floors.csv`, `rates.csv` (every `(N, c′)`), `rate_fits.csv`, `rates.png`,
`run.log`. Tests: `python3 -m pytest tests/test_separator_moment.py`
(60 tests, 10 new).

### 5.1 Method

Four functions in `learning/separator_moment.py`:

* `connected_probs(N, p)` / `log_connected`: Gilbert's recursion
  `C_1 = 1`, `C_j = 1 − Σ_{i<j} C(j−1, i−1) C_i (1−p)^{i(j−i)}` in `mpmath`;
  the subtraction cancels to `C_j ≈ e^{−j(1−p)^j}` at small `p`, so the
  working precision is `60 + 0.6 · N(1−p)^{N−1}` digits (94 at `N = 400`,
  `c′ = 2`). The item's 60 digits would have failed at `N = 400`, `c′ = 2`
  (`C_400 ≈ e^{−54}`, 24 digits of cancellation, and the terms carry the
  rounding of 400 further subtractions).
* `log_prob_partition(λ, N, p)`: `N!/(Π λ_i! Π_s m_s!) · Π C_{λ_i} · (1−p)^{(N² − Σ λ_i²)/2}`.
  With `a(s) = log C_s − log s! − (s²/2) log(1−p)` this is
  `N! (1−p)^{N²/2} Π_s e^{m_s a(s)}/m_s!`, i.e. the exponential formula:
  the sum over all partitions is `[x^N] exp(Σ_s e^{a(s)} x^s)`.
* `log_prob_rel(N, p, M)`: that coefficient with the sum cut at `s ≤ M`,
  the `O(N · M)` recursion the item asked for (over the multiplicity of the
  largest part rather than the component of the first vertex; the two are
  the same table). `N = 400` in under a second once `C_j` is known.
* `log_prob_bip(N, p, t)`: the sum over the partitions with a sub-multiset
  summing to `t`, by a **memoised recursion over the part sizes** (largest
  first) carrying the set of achievable sub-sums as a bitset, with two
  closures: a branch whose bitset already contains `t` is closed by the
  coefficient table (every completion qualifies; this is what makes it
  fast), and a part larger than `t` closes a branch at zero. The bitset is
  reduced to the bits in `[t − r, t]` before memoisation (`r` the vertices
  left to place), which is what keeps the state count polynomial-looking in
  practice: 20,863 states at `N = 60` (0.1 s), 115,065 at 80 (0.5 s),
  514,206 at 100 (2.5 s), 1,980,380 at 120 (18 s). The item's plain
  enumeration of the 966,467 partitions of 60 was never needed; `N = 160`
  would be about 8 M states and was not run.

All sums are of positive terms and are done in floating-point logs; only
the connectedness recursion needs multiple precision.

### 5.2 The finite table at the pilot cells

Largest `k` with each bound below `1` and below `0.01`; `β*(c)·n` the
asymptotic threshold of the pair count; the pilot's observed minimum
pathwidth where the cell is proved (`n = 60`) and the solver's smallest
lower bound where it is not (`n = 120`, 13 graphs per cell, none proved
at `c ≥ 4`, 3 of 13 at `c = 3`; `reports/scratch/gnp_pilot/results.csv`).

| `n` | `c` | pair `< 1` | pair `< .01` | xpair `< 1` | xpair `< .01` | **sep `< 1`** | **sep `< .01`** | relax `< 1` | relax `< .01` | `β*n` | graphs | exact | min pw | min LB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 60 | 3 | 1 | — | 1 | 0 | **3** | **1** | 3 | 1 | 0.5 | 136 | 136 | 5 | — |
| 60 | 4 | 5 | 3 | 5 | 3 | **6** | **4** | 6 | 4 | 3.7 | 136 | 136 | 8 | — |
| 60 | 6 | 11 | 11 | 12 | 11 | **12** | **11** | 12 | 11 | 10.2 | 134 | 134 | 16 | — |
| 60 | 8 | 17 | 17 | 18 | 17 | **18** | **17** | 18 | 17 | 15.8 | 132 | 132 | 20 | — |
| 60 | 10 | 23 | 21 | 23 | 21 | **23** | **22** | 23 | 22 | 20.2 | 133 | 133 | 25 | — |
| 120 | 3 | 1 | 1 | 2 | 1 | **5** | **4** | 5 | 4 | 1.0 | 13 | 3 | 11 | 12 |
| 120 | 4 | 9 | 7 | 9 | 7 | **11** | **10** | 11 | 10 | 7.4 | 13 | 0 | — | 17 |
| 120 | 6 | 21 | 21 | 22 | 21 | **24** | **22** | 24 | 22 | 20.5 | 13 | 0 | — | 25 |
| 120 | 8 | 33 | 33 | 34 | 33 | **34** | **33** | 34 | 33 | 31.5 | 13 | 0 | — | 34 |
| 120 | 10 | 43 | 41 | 43 | 42 | **44** | **42** | 44 | 42 | 40.5 | 13 | 0 | — | 41 |

(`inner.csv`, `floors.csv`.) Read it by the 0.01 column, where the pair
count's parity rounding (`B_pair` depends on `k` only through `t`) does
not confuse the count:

* **At `c ≥ 6` the separator floor is the pair floor or one stack above
  it** in all six cells (`+0, +0, +1` at `n = 60`; `+1, +0, +1` at 120),
  and never above the exact-size pair floor by more than one. That is the
  kill criterion, met (§5.5).
* **At `c = 3–4` it is two to three stacks above**: `−1 → 1` and `3 → 4`
  at `n = 60`; `1 → 4` and `7 → 10` at `n = 120`. Against the data these
  are still far below the truth (observed minimum 5 at `(60, 3)`, 8 at
  `(60, 4)`; lower bounds 12 and 17 at `n = 120`): the separator count
  moves the floor from "excludes nothing" to "excludes a few stacks" on
  the sparse flank and no further.
* **The relaxed and the bipartition floors coincide in every cell** at
  both thresholds. The number-partitioning condition costs nothing at
  these sizes (§5.4).
* The gain per vertex `(log B_pair − log B_sep)/n` at the pair's 0.01
  floor: `0.058, 0.023, 0.011, 0.006` at `c = 4, 6, 8, 10` (`n = 60`);
  `0.113, 0.065, 0.026, 0.013, 0.007` at `c = 3 … 10` (`n = 120`). Against
  the exact-size pair at the separator's own floor:
  `0.106, 0.062, 0.023, 0.011, 0.014` and `0.116, 0.068, 0.028, 0.013,
  0.010`. In `β` (÷ 3.3 at `c ≥ 6`): `0.003–0.008` at `c = 6–10`,
  `0.015–0.020` at `c = 4`, `0.02–0.035` at `c = 3` (÷ 5.5).

At `(120, 10)` around the floors, in decades: `k = 43`: pair `−0.99`,
xpair `−0.99`, sep `−1.38`; `k = 44`: pair `+1.76`, xpair `+0.40`,
**sep `−0.17`**, relax `−0.16`; `k = 45`: sep `+1.33`. So at `n = 120` the
separator count says `P(pw ≤ 44) ≤ 0.68` where the pair count says
nothing, and the solver's lower bounds there are 41–42 with the truth
`≥ 44` almost surely by either count. The inner numbers behind that row:
`log` product bound `−75.36`, `log P(E_bip)` `−76.65`, `log P(E_relax)`
`−76.64` — the separator count is 1.3 nats below the product bound at
`N = 76`, `c′ = 6.3`, of which `ln 2 = 0.69` is the double count of each
bipartition at even `N`.

### 5.3 The rate

`−log P_N(E_bip)/N` at `N = 20 … 120` and `−log P_N(E_relax)/N` to
`N = 400`, with linear fits in `N` (intercept free; "fitted"), fits with a
`log N` term (`−log P = I N + b log N + a`, the form a polynomial
prefactor gives), the plan's analytic routes — the pair count's rate
`c′/4 − ln 2` (a lower bound on the rate, from `P(E_bip) ≤` product
bound), `c′/4` (an upper bound, from one fixed bipartition) and the
thinning route `c′/2 − ln 2 + ln 2 · ln(2 ln 2/c′)` — and the LDP rate
`I_{c′}(½)` for `E_relax` quoted in §1.4 (`rate_check.py`).

| `c′` | `−log P_bip/N` at `N = 20` | at 60 | at 120 | linear fit, bip, `N ≥ 60` | log-fit, bip, `N ≥ 40` | `−log P_rel/N` at 400 | linear fit, rel, `N ≥ 200` | log-fit, rel, `N ≥ 100` | `c′/4 − ln 2` | `c′/4` | thinning | **LDP `I(½)`** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 0.107 | 0.060 | 0.049 | 0.0383 | 0.0392 | 0.0414 | 0.0380 | 0.0375 | 0 | 0.500 | 0.053 | **0.0362** |
| 3 | 0.308 | 0.221 | 0.202 | 0.1825 | 0.1864 | 0.1896 | 0.1846 | 0.1853 | 0.057 | 0.750 | 0.272 | **0.1831** |
| 4 | 0.571 | 0.436 | 0.407 | 0.3767 | 0.3818 | 0.3877 | 0.3799 | 0.3812 | 0.307 | 1.000 | 0.572 | **0.3796** |
| 5 | 0.877 | 0.682 | 0.639 | 0.5955 | 0.6013 | 0.6107 | 0.5991 | 0.6005 | 0.557 | 1.250 | 0.918 | **0.5997** |
| 6.6 | 1.432 | 1.110 | 1.040 | 0.9704 | 0.9793 | 0.9938 | 0.9744 | 0.9759 | 0.957 | 1.650 | 1.525 | **0.9756** |
| 8 | 1.983 | 1.504 | 1.407 | 1.3097 | 1.3256 | 1.3421 | 1.3148 | 1.3163 | 1.307 | 2.000 | 2.092 | **1.3161** |
| 10 | 2.894 | 2.091 | 1.945 | 1.7995 | 1.8358 | 1.8496 | 1.8091 | 1.8115 | 1.807 | 2.500 | 2.937 | **1.8102** |

(`rates.csv`, `rate_fits.csv`; standard errors of the linear slopes
`0.0001–0.0025`, meaningless as uncertainty since the residual is the
`log N` term, not noise.) Figure: `rates.png`, `−log P/N` against `N` per
`c′` with the bracket shaded, the LDP rate dashed.

**What the table says.**

1. **The exact computation reproduces the quoted large-deviation rate.**
   The log-corrected fit of `E_relax` over `N = 100–400` agrees with
   `I_{c′}(½)` to `0.0003–0.002` at every `c′`, and the linear fit over
   `N ≥ 200` to `0.001–0.002`. Item 01 could check the quoted formula only
   at its zero and its sign (§1.8); this is an independent check of its
   *value* at `u = ½` for seven `c′`, by an exact finite computation that
   shares nothing with the formula. The misprint risk recorded in §1.6 is
   retired for the form used in `rate_check.py`.
2. **`E_bip` has the rate of `E_relax`.** `log P(E_bip) − log P(E_relax)`
   at `N = 120` is `−0.0001` to `−0.008` nats in total (not per vertex),
   and the bip fits sit on the relax fits. The reading of the AKP
   minimiser in §1.8 ("the rate of `E_bip` equals that of `E_relax`") is
   confirmed to `N = 120` by exact computation and remains unproved as a
   limit; the finite inequality `P(E_bip) ≤ P(E_relax)` is exact.
3. **The bracket holds, in the form the finite computation can test.**
   The fitted rate lies in `[c′/4 − ln 2, min(c′/4, thinning)]` at every
   `c′` for the log-corrected fit, and for the linear fit at every `c′`
   but 10, where the linear slope over `N = 60–120` (`1.7995`) falls
   `0.007` below the asymptotic lower end (`1.8069`). That is the `log N`
   term, not an error: the lower route is the product bound, and the same
   linear fit of `−log` product bound over the same `N` gives `1.7927`,
   below the bip fit as it must be (`rate_fits.csv`,
   `above_finite_lower = True` at every `c′`); the log-corrected fit
   gives `1.836`, inside. The item's "the fitted rate must lie in the
   bracket, or the computation is wrong" is satisfied once the bracket is
   read at finite `N`; the asymptotic ends are limits and a linear fit
   on `N ≤ 120` is biased by `b/N` with `b ≈ −½` to `−3`.
4. **The thinning route is never the binding end** and at `c′ ≥ 5` lies
   above `c′/4`. Both of the planner's routes sit far above the truth at
   every `c′` (at `c′ = 5`: 0.918 and 1.25 against 0.600), as §1.6
   predicted from the quotation. The plan's bracket at `c = 6` was
   `[0.552, 1.245]`; the rate is `0.600` at `c′ = 5`.

### 5.4 How much smaller than the product bound

`log[C(N, t)(1−p)^{t(N−t)}] − log P_N(E_bip)`, total nats and per vertex of
`N` (`N` even throughout, so `ln 2 = 0.693` of it is the double count):

| `c′` | `N = 20` | 40 | 60 | 80 | 100 | 120 | per vertex at 120 | growth per vertex, 60 → 120 |
|---|---|---|---|---|---|---|---|---|
| 2 | 3.74 | 7.99 | 12.41 | 16.89 | 21.41 | 25.96 | 0.216 | 0.226 |
| 3 | 2.03 | 4.11 | 6.39 | 8.75 | 11.15 | 13.60 | 0.113 | 0.120 |
| 4 | 1.23 | 2.23 | 3.40 | 4.65 | 5.96 | 7.29 | 0.061 | 0.065 |
| 5 | 0.89 | 1.35 | 1.93 | 2.58 | 3.28 | 4.00 | 0.033 | 0.035 |
| 6.6 | 0.72 | 0.84 | 1.01 | 1.22 | 1.45 | 1.70 | 0.014 | 0.012 |
| 8 | 0.70 | 0.73 | 0.78 | 0.84 | 0.92 | 1.01 | 0.008 | 0.004 |
| 10 | 0.69 | 0.70 | 0.70 | 0.71 | 0.73 | 0.74 | 0.006 | 0.0007 |

**At `c′ ≥ 8` the whole gain is the factor 2**: the gap is `ln 2` plus
`0.01–0.3` nats at `N = 120` and grows at under `0.004` nats per vertex.
What the separator count merges there is the two orientations of one
bipartition and nothing else, as item 03 measured on typical instances
(`X₁/X₂ = 2.0–2.4` with `N` even, §3.2) and as the LDP says in the limit
(`I(½) − (c′/4 − ln 2) = 0.009` at `c′ = 8`, `0.003` at 10). **Below
`c′ ≈ 5` the gap is linear in `N`** at `0.035, 0.065, 0.120, 0.226` nats
per vertex of `N` for `c′ = 5, 4, 3, 2`, the limit values being
`I(½) − max(0, c′/4 − ln 2) = 0.043, 0.073, 0.126, 0.036`
(at `c′ = 2` the pair count's rate is negative, so the pair bound is
vacuous and the gap per vertex is `ln 2 − c′/4` plus the rate: the
finite table's `0.226` has the product bound still *growing*). This is
the component structure doing real work: the bipartitions of `G(N, c′/N)`
that are empty cluster onto the same component partition, and the
smaller `c′` the more of them per partition.

In the loop's units (nats per vertex of `n`, then `β`): at a pilot cell
`N = (1 − β) n`, so the gain per vertex of `n` is `(1 − β)` times the
column above at `c′ = c(1 − β)`. Linearising the pair exponent at `β*`
with the LDP value of the gain gives `+0.023, +0.020, +0.011, +0.006,
+0.004` in `β` at `c = 3, 4, 6, 8, 10` — the same numbers as §1.6's
preview from the quotation (`+0.028, +0.021, +0.011, +0.004` at
`c = 3, 4, 6, 10`, by the exact root rather than the linearisation), now
resting on the exact finite computation at `N ≤ 120` and the fitted
rate beyond. Item 06 computes `β_sep(c)` properly; this is the preview
it inherits.

### 5.5 Kill verdict

**Met for the headline cells.** At every pilot cell with `c ≥ 6` the
separator floor at `< 0.01` exceeds the pair floor by at most one stack
(`+0, +0, +1, +1, +0, +1`), so **the separator count is recorded as a
rounding at these sizes**, as the exact-size pair was in
`excess_phase_diagram.md` §8.6 (4), and item 06 is told so. The rate
comparison ran as the item requires, and is where the item's value is:
§5.3 (1)–(2) settle the two open readings of item 01, and §5.4 locates
the gain on the sparse flank (`c′ ≤ 5`, i.e. `c ≤ 6` at `β*`), two to
three stacks at `n = 120`, `c = 3–4`.

**Prediction for item 06**: `β_sep(c) = β_relax(c)` of §1.6 to the
accuracy of the fit (the two events have the same rate to `N = 120` and
to three decimals in the fit); gains of `+0.011` at `c = 6` and `+0.004`
at 10 against the kill of `0.02`, so **item 06's kill is predicted met
at `c = 6` and `10`**, and not met at `c ≤ 4`. The prediction of §3.5
(the separator count merges at most `0.003` in `β` at `c = 10`, measured
at `k = pw` on typical instances) is consistent with the `0.004` at `β*`.

### 5.6 What this does not claim

* **A limit.** The rate of `E_bip` is computed exactly to `N = 120` and
  fitted beyond; the rate of `E_relax` is exact to `N = 400` and fitted
  beyond. That either equals `I_{c′}(½)` is a fit agreeing to three
  decimals, not a theorem; the LDP itself is cited (O'Connell 1998 via
  Puhalskii 2005), not proved here, and the upper-bound half of it is
  what a separator first moment would use. That `E_bip` and `E_relax`
  have the same rate is exact to `N = 120` and conjectural beyond.
* **The finite inequalities are the only things proved**, and the
  separator one on paper only after item 08 (the deterministic lemma is
  §2's L1′; the union bound over `S` with the inner probability is the
  statement item 08 writes and item 10 formalises). `B_pair` is the
  Lean theorem; `B_xpair`, `B_sep`, `B_rel` are valid by L1′ and the
  union bound and are not yet in Lean.
* The floors at `n = 120` are against the solver's *lower bounds* on
  unproved graphs (3 of 13 proved at `c = 3`, none at `c ≥ 4`), not
  against pathwidths; the comparison with the truth is at `n = 60` only.
* The `β` conversions in §5.4 are linearisations at `β*` for a preview;
  item 06 owns the constants.
* The thinning route's formula is the plan's, evaluated as written; the
  plan's value `1.19` at `c′ = 4.98` does not reproduce from it (`0.91`),
  and nothing rests on it since it is never the binding end.
* Nothing about covers (item 07): there is no LDP to quote there and the
  inner probability of a random clique cover minus a customer set is not
  `G(N, p)`.

---

## 6. `β_sep(c)`, `β_closed(c)` and `β_comb(c)`: the constants, against `β*(c)` and the slopes (item 06, 2026-11-01)

**Question (D of the brief).** What constant does the separator first
moment give on `G(n, c/n)` — the root `β_sep(c)` of
`H(β) − (1 − β) I(c(1 − β)) = 0`, `I(c′)` the rate in `N` of the inner event —
what does the closed-pair count give (`β_closed`), what does a combination
give (`β_comb`), how do the three compare with `β*(c)` and with the fitted
slopes at `c = 2–20`, and does the method's threshold move from `4 ln 2`?

**Events counted.** Three first moments, each a valid upper bound on
`P(pw(G(n, c/n)) ≤ βn)` by L1′ and L2 of §2 and the union bound:

1. the **separator count** `C(n, k) · P_N(E_bip)`, `N = n − k`, and its
   relaxation with `P_N(E_relax)`; item 05 found the two inner
   probabilities equal in rate to `N = 120`, and the rate used here is the
   relaxed one (exact to `N = 400`, fitted beyond; the cited LDP rate is for
   `E_relax`);
2. the **closed-pair count** `E[X₃]`: ordered triples `(A, R, S)` partitioning
   `V`, `|A| ≥ t`, `|R| ≥ N − t`, `|S| ≤ k`, no `A–R` edge, every vertex of `S`
   adjacent to `A` and to `R` (`S = N(A) ∩ N(R)`, §2.3);
3. the **combined count**: closed pairs grouped by their separator `S*`,
   `|S*| = s′ ≤ k`. Given `G − S`, the empty bipartitions `(A, R)` with
   `|A| ∈ [t, t + k − s′]` (so that `|R| ≥ N − t`) are 2-colourings of the
   components of `G − S`, at most `2^κ` of them (`κ` the number of
   components), and each is closed with probability
   `Π_{v∈S} q_{|A|} q_{|R|} ≤ Qmax(s′)^{s′}` (`q_x = 1 − (1 − p)^x`; the edges
   from `S` to `G − S` are independent of `G − S`, and for distinct `v ∈ S`
   they are disjoint edge sets). Hence

       P(pw ≤ k) ≤ Σ_{s′ ≤ k} C(n, s′) · Qmax(s′)^{s′} · E_{N′ = n − s′}[ 1[E_win] · 2^κ ],

   with `E_win` the window bipartition event (one side between `t` and
   `t + k − s′` vertices; `E_bip` at `s′ = k`) or its relaxation (no
   component larger than `t + k − s′`). The inner factor is a *tilted*
   partition sum, computed exactly by the recursions of §5.1 with every
   part weighted by 2 (`tilt = ln 2` in `log_prob_bip` / `log_prob_rel`).

**Size range.** Asymptotic constants (roots of exponents per vertex);
fitted rates from exact inner sums at `N = 100–400`; the threshold check at
`N ≤ 400`; the finite form at `n = 60, 120`, `c = 3, 4, 6, 8, 10`, every `k`
around the floors. Checks on record (`check.log`): the window and tilted
recursions against the enumeration of every labelled graph at `N ≤ 6`
(every window, both tilts; max difference `3 × 10⁻¹³`); the fast relaxed
recursion against the table one at `N ≤ 6` and `N = 60, 120, 200`
(`6 × 10⁻¹⁴`); the finite closed count against the enumeration of closed
pairs over every labelled graph at `n ≤ 6` (`3 × 10⁻¹³`) and Monte Carlo
at `n = 7, 8` (20,000 graphs each: `2.1, 0.8, 0.2` standard errors);
`β_sep` with the bracket's lower end equals `β*` at six `c` (to `2 × 10⁻⁶`);
Edwards & McDermid's Corollary 5.2 reproduces `0.183, 0.458, 0.656`.

**Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/06_constants/run.py`
(stages `check`, `grid`, `constants`, `threshold`, `finite`, `draw`; 18 + 8 +
30 + 4 + 5 + 2 s, the grid and the finite stage on 8 workers at nice 19;
about 0.05 core-hours against 0.2 budgeted). Outputs beside it:
`rate_grid.csv` (every `(c′, N, u)`), `rate_fits.csv` (the fitted rates per
`c′`), `constants.csv` (the table), `threshold.csv`, `finite.csv` and
`finite_floors.csv`, `check.log`, `run.log`, `beta_vs_c.png`. Tests:
`python3 -m pytest tests/test_separator_moment.py` (70 tests, 10 new).

### 6.1 Method

**(a) `β_sep(c)` from three rates.** `sep_exponent(c, β, I) = H(β) − (1 − β) I(c(1 − β))`
and `beta_sep(c, I)` its root, for three rate functions `I(c′)`:

* **fitted**: the log-corrected fit `−log P_N(E_relax) = I N + b log N + a`
  over `N = 100, 150, …, 400` (item 05's `logfit`, the form a polynomial
  prefactor gives), on a grid of 77 values `c′ = 1.00, 1.25, …, 20.00`,
  linearly interpolated between them (`rate_fits.csv`, column
  `fit_rel_half`; `load_fitted` in `run.py`);
* **bracket**: the plan's two analytic ends, `c′/4 − ln 2` (the product
  bound, i.e. the pair count's own rate) and `min(c′/4, thinning)`, each
  giving a root; the lower end gives `β*(c)` *exactly*, because
  `H(a, a, 1 − 2a) − c a² = H(β) − (1 − β)(c′/4 − ln 2)` at `a = (1 − β)/2`
  (`pair_exponent_beta`; tested);
* **cited**: `I_{c′}(½)`, the large-deviation rate of the largest component
  of `G(N, c′/N)` at `u = ½` in O'Connell's form as restated by Puhalskii
  (2005, *Ann. Probab.* 33, Cor. 2.4(3) and (2.13)–(2.14); §1.3 Table B),
  ported from item 01's `rate_check.py` into `ldp_rate`, whose value item 05
  checked against the exact computation to `0.0003–0.002` at seven `c′`.

**(b) `β_closed(c)`.** The closed-pair exponent per vertex at side
fractions `(a, r, s)`, `a + r + s = 1`, is

    g_closed(a, r, s) = H(a, r, s) − c a r + s ln q(a) + s ln q(r),   q(x) = 1 − e^{−cx}:

the multinomial counts the ordered triples; `(1 − p)^{|A||R|} → e^{−c a r n}`
is the empty-pair probability; and given `(A, R)` the events "`v` sees `A`
and `v` sees `R`" for the `s n` vertices of `S` are independent (disjoint
edge sets) with probability `(1 − (1 − p)^{an})(1 − (1 − p)^{rn}) → q(a) q(r)`.
`closed_rate(β, c)` is its supremum over the admissible region of L2
(`a, r ≥ (1 − β)/2`, `s = 1 − a − r ∈ [0, β]`; a grid over the triangle then
Nelder–Mead), and `β_closed(c)` the root of the supremum. Checks: without
the `q` terms the exponent at the corner `a = r = (1 − β)/2`, `s = β` is
the pair exponent (tested); the finite count
`Σ n!/(a! r! s!) (1 − p)^{ar} q_a^s q_r^s` over the admissible integer sizes
(`log_closed_count`) equals the enumeration of `closed_pairs` over every
labelled graph at `n ≤ 6` for every `k` (§6's check). **At every `c` of the
table the supremum sits at the corner** (`a = r = (1 − β)/2`, `s = β`;
`constants` stage), so the closed count's gain over the pair count is the
`q` terms alone: `2β ln q((1 − β)/2)` nats per vertex at `β*`
(`−0.027` at `c = 10`, `−0.033` at `c = 6`, `−0.005` at `c = 3`), the
probability that every separator vertex of the planted pair sees both
sides.

**(c) `β_comb(c)`.** The combined count's `s′`-term exponent per vertex is

    g_comb(s′; β) = H(s′) + 2 s′ ln q((1 − s′)/2) − (1 − s′) J(c(1 − s′), u),   u = ((1 + β)/2 − s′)/(1 − s′),

where `J(c′, u)` is the rate in `N′` of `E[1[no component > uN′] 2^κ]`
(`u` is the largest allowed component as a fraction of `N′`; at `s′ = β`,
`u = ½`). `J` is **fitted only**: there is no LDP to cite for the tilted
event, and the fit is the same log-corrected fit over `N = 100–400` on the
grid `c′ × u ∈ {0.5, 0.55, …, 0.8}` (`rate_fits.csv`, columns
`fit_tilted_u*`), bilinearly interpolated. `combined_rate(c, β)` is the
supremum over `s′ ∈ [0, β]` on 42 points and `β_comb` its root; at every
`c` in the table the supremum is at `s′ = β` (`run.log`, the profiles at
`c = 3, 6, 10`: the exponent rises monotonically in `s′` to `0` at `s′ = β`).

### 6.2 The rates on the grid, against item 05 and the LDP

(`rate_fits.csv`; `fit_rel(½)` is the fitted rate used for the "fitted"
column; `item05` is item 05's `logfit_rel_slope_N100` at its seven `c′`.)

| `c′` | fitted `I(½)` | LDP `I(½)` | fitted − LDP | item 05 | tilted fit `u = 0.5` | `0.6` | `0.7` | `0.8` |
|---|---|---|---|---|---|---|---|---|
| 1.0 | 0.0001 | 0 | +0.0001 | — | −0.4431 | −0.4431 | −0.4431 | −0.4431 |
| 1.5 | 0.0021 | 0.0015 | +0.0006 | — | −0.3181 | −0.3181 | −0.3181 | −0.3181 |
| 2.0 | 0.0375 | 0.0362 | +0.0013 | 0.0375 | −0.1928 | −0.1930 | −0.1932 | −0.1932 |
| 2.5 | 0.1025 | 0.1006 | +0.0019 | — | −0.0894 | −0.0987 | −0.1041 | −0.1038 |
| 3.0 | 0.1852 | 0.1831 | +0.0022 | 0.1853 | 0.0238 | −0.0019 | −0.0297 | −0.0526 |
| 4.0 | 0.3812 | 0.3796 | +0.0017 | 0.3812 | 0.2829 | 0.2269 | 0.1553 | 0.0744 |
| 5.0 | 0.6005 | 0.5997 | +0.0009 | 0.6005 | 0.5499 | 0.4804 | 0.3654 | 0.2260 |
| 6.0 | 0.8328 | 0.8324 | +0.0004 | — | 0.8052 | 0.7375 | 0.5873 | 0.3879 |
| 8.0 | 1.3164 | 1.3161 | +0.0003 | 1.3163 | 1.3072 | 1.2343 | 1.0382 | 0.7232 |
| 10.0 | 1.8115 | 1.8102 | +0.0013 | 1.8115 | 1.8081 | 1.7229 | 1.4743 | 1.0627 |
| 12.0 | 2.3116 | 2.3081 | +0.0035 | — | 2.3101 | 2.2081 | 1.9039 | 1.3996 |
| 16.0 | 3.3178 | 3.3070 | +0.0108 | — | 3.3175 | 3.1769 | 2.7558 | 2.0573 |
| 20.0 | 4.3298 | 4.3069 | +0.0230 | — | 4.3298 | 4.1489 | 3.6077 | 2.7104 |

The fitted rate reproduces item 05's at all seven of its `c′` (to
`10⁻⁴`) and the LDP to `0.0004–0.002` for `c′ ≤ 10`; above `c′ = 12` the
fit drifts above the LDP (`+0.004` to `+0.023`), the `log N` term growing
with `c′` — the fit is a fit, and the LDP is what the "cited" column uses.
The constants only ever need `c′ = c(1 − β) ≤ 8.9` (at `c = 20`), where the
two agree to `0.0005`. **The tilted rate is negative for `c′ ≤ 2.5`** at
every `u` (the `2^κ` factor grows faster than the probability decays: the
number of components of `G(N, c′/N)` is a positive fraction of `N` there)
and costs, at `u = ½`, `0.161, 0.098, 0.051, 0.028, 0.009, 0.003` nats per
vertex of `N` relative to the untilted rate at `c′ = 3, 4, 5, 6, 8, 10`,
**more than the separator count gained over the product bound at the same
`c′`** (§5.4: `0.126, 0.073, 0.043, 0.026, 0.009, 0.003`; the
`E[2^κ 1[E]]` is dominated by partitions with more components than those
dominating `P(E)`, Jensen's inequality in the exponent).

### 6.3 The table

(`constants.csv`. `β_sep` three ways: fitted rate / bracket `[β*, root of
the optimistic end]` / cited LDP rate; `β_comb` fitted only; the slope is
the pilot's fitted `β_∞` where the cell has one, survey §7(d); E–M is
Edwards & McDermid 2015 Cor. 5.2 on Poisson(`c`) degrees, the published
upper line (owner's note of 2026-11-01); `dg/dβ` is the pair exponent's slope
at `β*` in nats per unit of `β`, the conversion of the gains.)

| `c` | `β*` | `β_closed` | `β_sep` fitted | bracket | `β_sep` cited | `β_comb` fitted | slope | E–M | `dg/dβ` | gain sep (fitted) | gain closed | gain comb |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 0 | 0 | 0.0059 | [0, 0.0087] | 0.0056 | 0 | 0.040 | 0.085 | 7.21 | +0.0059 (0.043 nats) | 0 | 0 |
| 2.5 | 0 | 0 | 0.0190 | [0, 0.0283] | 0.0185 | 0 | — | 0.132 | 7.46 | +0.0190 (0.142) | 0 | 0 |
| 3 | 0.0087 | 0.0096 | 0.0374 | [0.0087, 0.0558] | 0.0368 | 0.0035 | 0.099 | 0.183 | 5.53 | **+0.0287** (0.159) | +0.0009 (0.005) | −0.0052 |
| 4 | 0.0613 | 0.0671 | 0.0833 | [0.0613, 0.1210] | 0.0827 | 0.0594 | 0.158 | 0.285 | 3.91 | **+0.0220** (0.086) | +0.0058 (0.023) | −0.0019 |
| 6 | 0.1706 | 0.1803 | 0.1820 | [0.1706, 0.2480] | 0.1817 | 0.1782 | 0.268 | 0.458 | 3.38 | +0.0113 (0.038) | +0.0097 (0.033) | +0.0076 |
| 8 | 0.2628 | 0.2722 | 0.2691 | [0.2628, 0.3490] | 0.2690 | 0.2716 | 0.360 | 0.576 | 3.29 | +0.0063 (0.021) | +0.0094 (0.031) | +0.0088 |
| 10 | 0.3371 | 0.3453 | 0.3410 | [0.3371, 0.4266] | 0.3409 | 0.3451 | 0.415 | 0.656 | 3.30 | +0.0038 (0.013) | +0.0082 (0.027) | +0.0080 |
| 12 | 0.3973 | 0.4043 | 0.3999 | [0.3973, 0.4871] | 0.3998 | 0.4043 | — | 0.711 | 3.34 | +0.0025 (0.009) | +0.0069 (0.023) | +0.0069 |
| 16 | 0.4882 | 0.4933 | 0.4895 | [0.4882, 0.5750] | 0.4895 | 0.4934 | — | 0.782 | 3.45 | +0.0013 (0.005) | +0.0050 (0.017) | +0.0051 |
| 20 | 0.5535 | 0.5573 | 0.5543 | [0.5535, 0.6356] | 0.5542 | 0.5574 | — | 0.826 | 3.56 | +0.0008 (0.003) | +0.0038 (0.014) | +0.0038 |

What the table says:

1. **The separator count's gain is a near-threshold gain.** `+0.029` at
   `c = 3` (32% of the gap of 0.090 to the fitted slope), `+0.022` at `c = 4`
   (23%), `+0.011` at `c = 6` (12%), `+0.004` at `c = 10` (5%), `+0.0008` at
   `c = 20`; and a positive constant at `c = 2` and `2.5`, where `β* = 0`
   (`+0.006` and `+0.019`; 15% of the gap at `c = 2`). The fitted and the
   cited columns agree to `0.0006` everywhere; the bracket's optimistic end
   is far above both (`0.248` against `0.182` at `c = 6`) and is not the
   truth, as §5.3 said. §1.6's preview from the quotation alone is
   reproduced to `0.0005` at every `c`.
2. **The closed-pair count's gain is a dense-side gain**: `+0.001` at
   `c = 3`, `+0.006` at 4, `+0.010` at 6, `+0.009` at 8, `+0.008` at 10,
   `+0.004` at 20 — 1%, 6%, 10%, 10%, 11% of the gap where a slope exists.
   The planner's `0.1803 / 0.3453` at `c = 6 / 10` (plan §0) are reproduced
   exactly. The separator count wins at `c ≤ 6` (by a hair at 6: `0.1820`
   against `0.1803`), the closed count at `c ≥ 8`.
3. **The combined count, as constructed, is not the best on the ladder.**
   Its constant lies below the closed count's at every `c` and *below `β*`*
   at `c ≤ 4` (`0.0035` against `0.0087` at `c = 3`): the `2^κ` bound on the
   number of balanced 2-colourings of the components costs more than the
   separator count gained (§6.2), so grouping the closed pairs by `S` with
   that bound gives the separator's gain back and keeps only the `q` terms,
   less a little. At `c ≥ 8` it is within `0.0006` of the closed count. The
   best *valid* first moment at each `c` is the larger of `β_sep` and
   `β_closed`, both valid separately; a combination that beats both needs
   the closedness condition inside the component law (the probability that
   *some* balanced colouring of the components of `G − S` has every vertex
   of `S` adjacent to both colours), which is not a tilt of the partition
   sum and is not computed here.
4. **Against the data**: the best of the three constants sits at `0.037,
   0.083, 0.182, 0.272, 0.345` against fitted slopes `0.099, 0.158, 0.268,
   0.360, 0.415` at `c = 3, 4, 6, 8, 10`, closing 32%, 23%, 12%, 10%, 11%
   of the gap. The provable sandwich with the published upper line is
   `[0.037, 0.183]`, `[0.182, 0.458]`, `[0.345, 0.656]` at `c = 3, 6, 10`
   (was `[0.009, 0.183]`, `[0.171, 0.458]`, `[0.337, 0.656]` with `β*`);
   the ratio upper/lower at `c = 3` falls from 21 to 4.9.
5. **In nats**: the separator gain at `β*` is `0.159, 0.086, 0.038, 0.021,
   0.013` nats per vertex of `n` at `c = 3, 4, 6, 8, 10` (the slopes `dg/dβ`
   are `5.53, 3.91, 3.38, 3.29, 3.30`, so `g/3.3` is the conversion at
   `c ≥ 6` and `g/5.5` at `c = 3`); the closed gain `0.005, 0.023, 0.033,
   0.031, 0.027`. Item 04's measured union-bound slack on `G(n, c/n)` at `β*`
   and `n ≤ 32` was `0.065` and `0.039` nats at `c = 6` and `10` (§4.6):
   the separator count recovers 59% and 33% of it, the closed count 51%
   and 69%, and neither both.

### 6.4 The threshold

**Proposition (conditional).** *Suppose that for every `c′ > 2 ln 2` there
is `I(c′) > 0` with `P(no component of G(N, c′/N) has more than N/2
vertices) ≤ e^{−(I(c′) − o(1)) N}`, with `I` continuous in `c′`. Then
`β_sep(c) > 0` for every `c > 2 ln 2`: there is `β₀ = β₀(c) > 0` with
`P(pw(G(n, c/n)) ≤ β₀ n) → 0`.* Proof: by L1′ (§2.2) and the union bound,
`P(pw ≤ βn) ≤ C(n, βn) P_{N}(E_relax) ≤ e^{n[H(β) − (1 − β) I(c(1 − β)) + o(1)]}`;
as `β → 0`, `H(β) → 0` and `(1 − β) I(c(1 − β)) → I(c) > 0`, so the exponent
is negative for all small `β > 0`. ∎ (The pair count's exponent at `β → 0`
is `ln 2 − c/4`, negative only for `c > 4 ln 2`; the true threshold of linear
pathwidth is `c = 1`, Lee–Lee–Oum 2012 via `tw ≤ pw`, survey §1.1.)

**Status of the hypothesis: cited, not verified by us as a theorem.** It is
the upper-bound half of the large-deviation principle for the largest
component of `G(N, c′/N)` at scale `N`, applied to the closed set
`[0, ½]`: O'Connell 1998 (*not held*; Theorem 3.1 as restated), Puhalskii
2005 (*Ann. Probab.* 33(2), held; Cor. 2.4(3), p. 8 of the arXiv version,
with the rate function (2.13)–(2.14) and the remark that O'Connell's
statement has a misprint), Andreis–König–Patterson 2021 (held; Cor. 1.3
gives the macroscopic contraction). `I_{c′}(½) > 0` iff `c′ > 2 ln 2`
(§1.4, `rate_check.log`), and continuity in `c′` is read off the formula.
What *is* verified here is the value of the quoted formula at finite `N`
(§5.3; §6.2), not the principle.

**Numerical check at `N ≤ 400`** (`threshold.csv`; `−log P_N(E_relax)/N` by
the exact recursion; the log-corrected fit over `N ≥ 100`):

| `c` | `I_c(½)` | `N = 50` | 100 | 200 | 300 | 400 | log-fit `I` (`b`) |
|---|---|---|---|---|---|---|---|
| 1.2 (control, below) | 0 | 0.0042 | 0.0013 | 0.0003 | 0.0001 | 0.00005 | +0.0002 (−0.12) |
| 2 ln 2 (threshold) | 0 | 0.0111 | 0.0055 | 0.0029 | 0.0020 | 0.0015 | +0.0001 (+0.02) |
| 1.5 | 0.0015 | 0.0175 | 0.0102 | 0.0066 | 0.0053 | 0.0046 | +0.0021 (+0.12) |
| 2 | 0.0362 | 0.0646 | 0.0514 | 0.0449 | 0.0427 | 0.0414 | +0.0375 (+0.16) |
| 2.5 | 0.1006 | 0.1372 | 0.1191 | 0.1107 | 0.1080 | 0.1066 | +0.1025 (−0.01) |

At `c = 2` and `2.5` the finite rate is bounded away from zero at every
`N` and the fit lands `0.001–0.002` above the cited value; at `c = 1.5` the
finite values are still falling at `N = 400` (`0.0046` against a cited
limit of `0.0015`) and the fit gives `0.0021`, of the limit's order but
not a confirmation; the controls at and below `2 ln 2` fall like `1/N`
(`b ≈ 0`, `I ≈ 0`). So the check is consistent with the proposition at
`c = 2, 2.5`, undecided by itself at `c = 1.5`, and no finite computation
can establish a limit. `P_N(E_bip)` at `N = 100` equals `P_N(E_relax)` to
four decimals at every `c` in the table (column `rate_bip`).

### 6.5 The finite form at `n = 60` and `120`, in stacks

Largest `k` with each bound below `1` and below `0.01` (`finite_floors.csv`;
pair, exact-size pair and separator from item 05's `inner.csv`; the closed
and combined counts new; `comb` is the relaxed-window form, `comb_bip` the
bipartition-window form at `n = 60` only; the pilot's observed minimum
pathwidth at 60 and the solver's lower bound at 120, §5.2):

| `n` | `c` | pair `<1` / `<.01` | xpair | **sep** | **closed** | comb | comb_bip | `β*n` | min pw / LB |
|---|---|---|---|---|---|---|---|---|---|
| 60 | 3 | 1 / −1 | 1 / 0 | **3 / 1** | 1 / 0 | 0 / −1 | 0 / −1 | 0.5 | 5 |
| 60 | 4 | 5 / 3 | 5 / 3 | **6 / 4** | 5 / 4 | 4 / 3 | 4 / 3 | 3.7 | 8 |
| 60 | 6 | 11 / 11 | 12 / 11 | 12 / 11 | **13 / 11** | 12 / 10 | 12 / 10 | 10.2 | 16 |
| 60 | 8 | 17 / 17 | 18 / 17 | 18 / 17 | **19 / 17** | 18 / 16 | 18 / 16 | 15.8 | 20 |
| 60 | 10 | 23 / 21 | 23 / 21 | 23 / 22 | 23 / 22 | 23 / 21 | 23 / 21 | 20.2 | 25 |
| 120 | 3 | 1 / 1 | 2 / 1 | **5 / 4** | 2 / 1 | 0 / −1 | — | 1.0 | 11 / 12 |
| 120 | 4 | 9 / 7 | 9 / 7 | **11 / 10** | 9 / 8 | 8 / 6 | — | 7.4 | — / 17 |
| 120 | 6 | 21 / 21 | 22 / 21 | 24 / 22 | 24 / 22 | 22 / 21 | — | 20.5 | — / 25 |
| 120 | 8 | 33 / 33 | 34 / 33 | 34 / 33 | **35 / 34** | 34 / 33 | — | 31.5 | — / 34 |
| 120 | 10 | 43 / 41 | 43 / 42 | 44 / 42 | **44 / 43** | 43 / 42 | — | 40.5 | — / 41 |

In stacks the picture is the asymptotic one: at `c = 3–4` the separator
count is the best by 2–3 stacks over everything else; at `c ≥ 6` the
closed count ties or beats the separator count by one stack (`+1` at
`(60, 6)`, `(60, 8)` at `< 1`; `+1` at `(120, 8)`, `(120, 10)` at `< 0.01`),
and both are one to two stacks above the pair count; the combined count
is one stack below the closed count or worse. At `(120, 10)` the closed
count says `P(pw ≤ 44) ≤ 0.10` where the separator count said `0.68` and
the pair count nothing, against solver lower bounds of 41–42; the decades
around the floor (`run.log`): `k = 43`: closed `−2.28`, sep `−1.38`, pair
`−0.99`; `k = 44`: closed `−0.98`, sep `−0.17`, pair `+1.76`; `k = 45`:
closed `+0.28`. The bipartition-window and the relaxed-window forms of
the combined count agree to `0.01` decades at every `(60, c, k)`: the
number-partitioning condition is free here too (§5.4).

### 6.6 The figure

`beta_vs_c.png`: left, `β` against `c` — `β*`, `β_sep` (cited rate) with
the bracket shaded, `β_closed`, the pilot's fitted slopes, and Edwards &
McDermid's published upper line, with the two thresholds `2 ln 2` and
`4 ln 2` marked; right, the gains over `β*` — the separator count (cited
and fitted), the closed count, the combined count, the bracket, and the
gap to the fitted slope, with the brief's kill line at `0.02`. The four
lower curves on the left are indistinguishable at the scale of the
sandwich, which is the finding; the right panel is where they separate.
(Categorical palette validated: six slots, all checks pass with the
contrast warning on three, relieved by the legend and direct labels.)

### 6.7 Kill verdict

**The brief's kill: met.** `β_sep(fitted) − β* = +0.0113` at `c = 6` and
`+0.0038` at `c = 10`, both below `0.02`; **the separator route is closed
for the headline constants**, as items 03 and 05 predicted (§3.5: at most
`0.003` at `c = 10`; §5.5: `+0.011` and `+0.004`). Beside it, as the item
asks: the closed-pair gain is `+0.0097 / +0.0082`, the combined count's
`+0.0076 / +0.0080`; none of the three, nor their maximum, reaches `0.02`
at either `c`.

**The pre-registered separate findings, and what they are worth.**

* *Near the threshold* the separator count is not a rounding: `+0.029` at
  `c = 3` and `+0.022` at `c = 4` in `β`, 32% and 23% of the gap to the
  fitted slopes — above the brief's kill and at the top of what §1.4's
  record of representative counts ever bought (1.7–25% of a gap) — and a
  positive constant at `c = 2, 2.5` where the pair count is vacuous. The
  plan's bracket at `c = 3` was `[0.009, 0.056]`; the answer is `0.037`,
  against a slope of `0.099`. These rest on the relaxed event's rate,
  cited (the LDP) and reproduced by exact computation to `N = 400`.
* *The threshold* moves from `4 ln 2 = 2.77` to `2 ln 2 = 1.39`,
  conditional on the cited LDP upper bound (§6.4, hypothesis explicit);
  the truth is `1`. In the logarithm this is half of the way.
* *The closed-pair count* is the better of the two at `c ≥ 8`, by the `q`
  terms alone (the supremum sits at the corner at every `c`); its gain is
  `+0.008–0.010` at `c = 6–12`, exactly the planner's estimate.

**Where this corrects the loop's own predictions.** §3.5 predicted from
typical instances at `k = pw` that the closed count merges at most `0.003`
in `β` at `c = 10`; the asymptotic constant gains `0.008`. The instrument
of §3 (ratios of counts on typical instances) sees the typical regime;
the first moment is decided in the rare-instance regime, where the
maximisers differ (§3.3's two regimes). The separator prediction
(`0.003` measured, `0.004` asymptotic) held.

### 6.8 Where the record corrects the item

* The item's "combined count … stated as the best valid first moment on
  the ladder" is not what the construction gives: with the `2^κ` bound on
  the colourings it is weaker than the closed count at every `c` and weaker
  than the pair count at `c ≤ 4` (§6.3 (3)). It is stated, valid, and
  not the best; the best valid bound at each `c` is `max(β_sep, β_closed)`.
* The item's test "`β_closed ≥ β*` at every `c`" holds numerically at every
  `c` tested (the supremum is at least the corner value, and at the corner
  the `q` terms lower the exponent — so the inequality is not automatic
  from the formula, and is tested, not proved).
* The bracket's lower end reproduces `β*` *exactly*, not approximately
  (an identity, §6.1 (a)), so "the bracket on `β_sep`" is `[β*, β_opt]`.
* The item's threshold check at `c = 1.5` is undecidable at `N ≤ 400`
  (§6.4): the limit is `0.0015`, the finite rate `0.0046` and still
  falling.
* The fitted rate's drift above the LDP at `c′ ≥ 12` (§6.2) is outside the
  range the constants use, and the "cited" column is the one quoted.

### 6.9 What this does not claim

* **A limit, or a theorem.** `β_sep` (fitted) rests on a fit of exact
  values at `N ≤ 400`; `β_sep` (cited) on an LDP we cite and did not prove;
  `β_comb` on a fit alone. The finite inequalities of §6.5 are exact and
  valid (L1′, L2, the union bound, the recursions checked by enumeration),
  and the separator and closed-pair ones are item 08's to write on paper
  and item 10's to formalise; `B_pair` is the only one in Lean.
* **The constant.** Every `β` here is a lower bound on `lim inf pw/n`
  whatever the rate, and none is claimed to be the limit; the fitted
  slopes are fits from `n ≤ 70–120` (survey §7(d)) and the gaps "closed"
  are fractions of a fitted number.
* **That `E_bip` and `E_relax` have the same rate** beyond `N = 120`
  (§5.6); the "fitted" and "cited" columns use `E_relax`, which is the
  valid relaxation either way.
* **That the closed count's supremum is at the corner for every `c`**: it
  is, at the ten `c` of the table, by numerical search; no proof.
* **Priority** for the separator count, the closed-pair count or the
  threshold statement: §1 found no prior separator first moment with an
  exact inner probability for pathwidth, and the threshold `2 ln 2` is the
  bisection threshold of Luczak–McDiarmid for the same reason (§1.3); "we
  found no prior statement" is the strongest wording.
* Nothing about covers (item 07), and nothing about the weighted count
  (item 09) beyond the §4.6 ceiling the gains here are measured against.
