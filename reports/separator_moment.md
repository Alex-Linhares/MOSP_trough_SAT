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
