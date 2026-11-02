# The Edwards–McDermid degree-sequence bound on pathwidth: verified on the record, formalised conditional on the cubic base case

*Ralph loop0012, 2026-11-02 onward. The plan is `reports/edwards_mcdermid_plan.md`
(its §0.2 quotes every statement used, verbatim; §0.3 names the two hypotheses;
§0.5 fixes the Lean design). One section per item; §0 (the summary) is written
by item 10. Nothing here changes a solver default; nothing re-solves an
instance that is already proved.*

## What this document is about

**The source.** Keith Edwards and Eric McDermid, *A general reduction theorem
with applications to pathwidth and the complexity of MAX 2-CSP*, Algorithmica
72(4):940–968, 2015, DOI 10.1007/s00453-014-9883-7. The accepted manuscript
(dated April 29, 2014, 29 pages) is at
`reports/scratch/edwards_mcdermid/em2015.pdf`, text `em2015.txt`, fetched on
2026-11-02 00:26 UTC from the University of Dundee's Discovery portal
(`SHA256` beside it: `f94e8c08…8665`; the file is 31 pages, two portal cover
sheets carrying the download date and then the manuscript, which is why its
hash differs from the copy of 2026-11-01). Page numbers are the manuscript's.

**The statement** (Corollary 5.2, p. 20; Lemma 5.1 and the base case, p. 19):

> Let `G` be a graph, and `r(G)` be the reduced graph of `G`. Then
> `pw(G) ≤ Σ_{v ∈ V(r(G))} g_{1/6}(d_{r(G)}(v)) + τ(|V(G)|) + O(log |V(G)|) = Σ_{d ≥ 3} g_{1/6}(d) n_d + o(|V(G)|)`.

Here `g = g_{1/6}` is the weight function of their Section 3.1 (p. 6),
`r(G)` the series-parallel reduction of Section 3.2 (p. 8), and `τ(n) = o(n)`
is the error term of Fomin & Høie's cubic bound, "a function `τ`, with
`τ(n) = o(n)`, such that `pw(G) ≤ n/6 − 1/6 + τ(n) + O(log n)`" (p. 19), for
which **the paper gives no constants**. The displayed `=` is a `≤` (plan §0.4
item 6), both forms are computed below.

**This is a verification and a formalisation of a published theorem**,
conditional on two cited results that are taken as named hypotheses and never
asserted (plan §0.3):

- **(H1) `CubicPathwidthBound τ`** — every connected cubic graph on `N`
  vertices has `pw ≤ N/6 − 1/6 + τ(N)`; the source is Fomin & Høie (2006)
  Theorem 5, which gives `pw ≤ (1/6 + ε) N` for `N > n_ε = (8/ε) ln(1/ε)(1 + 1/ε²)`,
  so its explicit budget is `τ_FH(N) = min{εN : N > n_ε} + 1/6`;
- **(H3) `ReductionPathwidthBound ρ`** — `pw(H) ≤ pw(r(H)) + ρ(|V(H)|)` for
  every `H`, with `ρ = O(log n)`; the source is Kneis, Mölle, Richter &
  Rossmanith (2009), not held.

The theorem the loop proves in Lean (items 03–09) is
`pw G ≤ fminus G + τ n + 2ρ n + 1` for graphs with every degree 0 or ≥ 3, and
`pw G ≤ Σ_v g(degree_{r G} v) + τ n + 3ρ n + 1` for every `G`, with both
budgets explicit. The paper's `τ(n) + O(log n)` is this with `ρ = O(log n)`.

**Notation.** `g(0) = g(1) = g(2) = 0`, `g(3) = 1/6`,
`n g(n) = (n − 2) g(n − 1) + g(n − 2) + 1` for `n ≥ 4`
(`1/6, 1/3, 13/30, 23/45, 359/630, 1553/2520, 14827/22680` at `d = 3..9`;
the paper's table p. 7 to `d = 8`, reproduced exactly); `g'(d) = g(d) − g(d − 1)`
(`1/6, 1/6, 1/10, 7/90, 37/630, 13/280` at `d = 3..8`; zero for `d ≤ 2`);
`f(G) = Σ_v g(d(v))`; `f⁻(G) = f(G) − Σ_{components C} g'(δ(C))` (p. 7, per
component); `r(G)` the reduced graph, kept on the same vertex set with the
removed vertices isolated (plan §0.5). The **main term** is
`Σ_{v ∈ V(r(G))} g(d_{r(G)}(v))`; the **histogram term** is `Σ_{d ≥ 3} g(d) n_d(G)`
over `G`'s own degrees; the **deficit** of a graph is `pw − main term`, the
part of the bound the lower-order terms must cover. Code:
`learning/edwards_mcdermid.py` (tests `tests/test_edwards_mcdermid.py`).

---

## 1. Corollary 5.2 and Theorem 5.3 on every graph with a proved pathwidth (item 01, 2026-11-02)

**Regenerate.** `nice -n 19 python3 reports/scratch/edwards_mcdermid/01_verify/run.py --workers 8`
(stages `pilot, dataset, ensemble, cubic, tables`; 75 s on 8 workers at load
0.1; outputs `pilot.csv`, `dataset.csv`, `ensemble.csv`, `cubic.csv`,
`tables.md` with every table below in full, `poisson_n120.png`, `run.log`).

**The manuscript against the plan's quotations.** Sections 1, 3, 5 and the
Appendix were read against plan §0.2: the weights and their six properties,
the table of values, the four operations, the definition of basic graphs,
Lemma 3.1 with its appeal to Kneis et al., Theorem 3.2 with its full case
analysis and Algorithm X, the base case paragraph, Lemma 5.1 and its proof,
Corollary 5.2, Theorem 5.3 and the Golovnev–Kutzkov remark, Lemmas 8.1–8.5
with their proofs, all agree with the quotations word for word. Two trivia:
Corollary 5.2 and Theorem 5.3 sit on p. 20 (the plan says "Section 5, p. 19",
which is where the section and Lemma 5.1 begin); and the portal's citation
sheet gives the year 2015, the manuscript's own cover sheet 2014. **No
discrepancy of substance.**

**Size range.** Every graph on record with a proved pathwidth, 63,330 in all:
the pilot's 6,542 proved `G(n, c/n)` graphs (`n = 20–120`, `c = 0.5–10`,
regenerated from their seeds and checked against the `m` column); the
dataset's 16,635 certified non-empty classes (`n = 1–2,916`; the 16,636th is
the empty graph); the ensembles' 50,701 certified random covers (`n = 10–100`,
four frames), of which 40,153 are distinct within their cell by the stored
nauty certificate — the 10,548 isomorphic repeats are evaluated and dropped
from every statistic below. The 173 unproved pilot rows and the 336 dataset
`solution` rows are carried separately. Pathwidths are the record's; the only
new solves are the 4,681 connected cubic graphs on 4–16 vertices (`nauty-geng
-c -d3 -D3`, subset DP, 43 s), which the item allows.

### 1.1 Kill checks: none fired

| check | result |
|---|---|
| a proved graph with `pw > main term + τ_FH(n)` | **0** of 63,330 |
| a graph with `main term > histogram term` | **0** of 63,330 (and 0 of the 509 unproved) |
| `reduce` raising a surviving vertex's degree | **0** (every surviving degree `≥ 3` and `≤` its original on all 63,839 graphs; the module's tests check it on 200 random graphs and the four named cases) |

So the reading of Section 3.2 and Corollary 5.2 stands, and the corollary
with Fomin–Høie's explicit budget holds on every graph on record. That is
no information: `τ_FH(n)` exceeds `0.17 n` at every size on record (next
table), and the informative column is what the record actually needs.

### 1.2 The deficit `pw − main term`, per source (d)

| source | graphs | `n` | max deficit | p99 | median | share `≤ 0` | max `pw − histogram` | share `≤ 0` (histogram) | mean (histogram − main) | max |
|---|---|---|---|---|---|---|---|---|---|---|
| dataset | 16,635 | 1–2,916 | 5.000 | 3.000 | 0.657 | 38.1% | 4.333 | 63.6% | 1.349 | 70.0 |
| ensemble (distinct) | 40,153 | 10–100 | 4.000 | 2.667 | −2.716 | 74.1% | 2.667 | 77.7% | 0.283 | 7.99 |
| pilot | 6,542 | 20–120 | 3.333 | 3.000 | 0.647 | 46.3% | 2.500 | 58.5% | 0.681 | 6.10 |
| **all** | **63,330** | 1–2,916 | **5.000** | — | — | **61.8%** | **4.333** | 72.0% | — | — |

The main term alone bounds the pathwidth on 61.8% of the record; the
histogram term alone on 72.0%. Only 122 graphs have deficit above 3, and 17
above 4. Where the deficit sits is structural, and the split says which
lower-order term it belongs to:

| source | kind | graphs | `n` | max deficit | attained by | p99 | median | share `≤ 0` |
|---|---|---|---|---|---|---|---|---|
| dataset | reduces to empty | 2,263 | 1–637 | **5.000** | VSPLIB `TREE_202_5` (|V| = 202, pw 5) | 4.000 | 2.000 | 0.1% |
| dataset | `r(G)` cubic | 803 | 4–261 | **4.333** | Coxeter graph (|V| = 28, pw 9) | 3.667 | 2.333 | 1.1% |
| dataset | `r(G)` non-cubic | 13,569 | 6–2,916 | 3.333 | pwc-09237 (|V| = 38, pw 5) | 2.667 | 0.178 | 46.7% |
| ensemble | reduces to empty | 2,166 | 10–60 | 4.000 | `f_n30_m30_d2` #23 (pw 4) | 3.000 | 2.000 | 0.1% |
| ensemble | `r(G)` cubic | 1,432 | 10–75 | 3.333 | `f_n40_m40_d2` #8 (pw 4) | 3.333 | 2.333 | 0.1% |
| ensemble | `r(G)` non-cubic | 36,555 | 10–100 | 3.667 | `f_n100_m100_d2` #22 (pw 5) | 2.333 | −3.428 | 81.4% |
| pilot | reduces to empty | 2,356 | 20–120 | 3.000 | `n50_c2` #0 (pw 3) | 3.000 | 2.000 | 0.1% |
| pilot | `r(G)` cubic | 199 | 20–120 | 3.333 | `n60_c1.5` #54 (pw 4) | 3.333 | 2.333 | 0.0% |
| pilot | `r(G)` non-cubic | 3,987 | 20–120 | 3.000 | `n50_c2` #2 (pw 4) | 2.667 | −2.485 | 75.9% |

- **Where `r(G)` is empty** (10.7% of the record: trees, cycles, every
  series-parallel graph), the main term is 0 and the deficit *is* the
  pathwidth: this is the paper's `O(log n)` term, (H3) with `r(G) = ∅`. On
  the 6,785 such graphs the maximum of `pw − log₃ n` is 0.904 and the
  maximum pathwidth 5 (the seven VSPLIB trees on 202 vertices, the extremal
  trees of `TreeBound.lean`). That is the measured *shape* of the reduction
  lemma's term at these sizes, not its constant.
- **Where `r(G)` is cubic** (3.8%), the deficit is the cubic base case's:
  `pw(r(G)) − |V(r(G))|/6`, and the record's maximum, 4.333, is the Coxeter
  graph. The 70 of the 122 deficits above 3 that are not series-parallel
  graphs are all here but three.
- **Where `r(G)` is neither** (85.5%), the main term already bounds on
  47–81% and the maximum deficit is 3.667.

The twelve largest deficits on record are the 202-vertex VSPLIB trees at
pathwidth 5 (main term 0; histogram term 8.7–11.0, which the reduction gives
back).

### 1.3 The budget the record needs, `B(n) = max{deficit : |V| ≤ n}`, beside Fomin–Høie's explicit `τ_FH(n)` (d)

| `n` | graphs with `|V| ≤ n` | `B(n)` | attained by | `B(n)` over `r(G) ≠ ∅` | `B(n)/n` | `τ_FH(n)` | `τ_FH(n)/n` |
|---|---|---|---|---|---|---|---|
| 10 | 3,045 | 3.333 | Petersen graph (|V| = 10, pw 5) | 3.333 | 0.333 | 7.46 | 0.746 |
| 20 | 14,492 | 4.000 | Pappus graph (|V| = 18, pw 7) | 4.000 | 0.200 | 12.85 | 0.643 |
| 40 | 39,934 | 4.333 | Coxeter graph (|V| = 28, pw 9) | 4.333 | 0.108 | 21.82 | 0.546 |
| 60 | 53,489 | 4.333 | Coxeter graph | 4.333 | 0.072 | 29.59 | 0.493 |
| 100 | 62,718 | 4.333 | Coxeter graph | 4.333 | 0.043 | 43.24 | 0.432 |
| 200 | 63,103 | 4.333 | Coxeter graph | 4.333 | 0.022 | 71.96 | 0.360 |
| 500 | 63,281 | 5.000 | VSPLIB `TREE_202_5` (|V| = 202, pw 5) | 4.333 | 0.010 | 140.19 | 0.280 |
| 1,000 | 63,307 | 5.000 | the same | 4.333 | 0.005 | 231.28 | 0.231 |
| 2,916 | 63,330 | 5.000 | the same | 4.333 | 0.002 | 498.43 | 0.171 |

`τ_FH` exceeds every deficit by a factor of 2.2 at `n = 10` and 100 at
`n = 2,916`: the corollary with that budget is satisfied everywhere on record
and says nothing a graph could violate. **`B(n)` is the informative column**:
a constant 5 covers every proved graph on record, 4.333 every graph whose
reduction is non-empty, and both are attained by graphs that are small and
famous (cages, extremal trees), not by the large ones. The unproved rows
cannot raise it: the 173 `upper` pilot rows (`n = 80–120`) have
`lower − main term ≤ −3.06` (median −20.4), and the 336 dataset `solution`
rows (`n = 90–1,024`) have `upper − main term ≤ 5.33` (median −57.8), the
5.33 being a cubic graph on 112 vertices whose witness has width 24 and whose
optimum is unknown.

### 1.4 The base case measured (e)

`pw − (N/6 − 1/6)` on every connected cubic graph to 16 vertices (exhaustive)
and on the dataset's certified cubic graphs:

| `N` | connected cubic graphs | pw min | pw max | max excess | `N/6 − 1/6` | graphs at the max |
|---|---|---|---|---|---|---|
| 4 | 1 | 3 | 3 | 2.500 | 0.500 | 1 (`K_4`) |
| 6 | 2 | 3 | 3 | 2.167 | 0.833 | 2 |
| 8 | 5 | 3 | 4 | 2.833 | 1.167 | 2 |
| 10 | 19 | 3 | 5 | 3.500 | 1.500 | 1 (Petersen) |
| 12 | 85 | 3 | 5 | 3.167 | 1.833 | 7 |
| 14 | 509 | 3 | 6 | **3.833** | 2.167 | 1 (Heawood) |
| 16 | 4,060 | 3 | 6 | 3.500 | 2.500 | 23 |

The dataset holds 47 cubic classes (42 certified, 5 `solution`; all
connected; `N = 4–126`). The 13 at `N ≤ 16` were matched by isomorphism to
the exhaustive sweep: all 13 matched and **all 13 pathwidths agree** (a free
consistency check of the record, no new solve). Above 16 the certified
excesses are: Pappus (18) 4.167, McGee (24) 4.167, Coxeter (28) **4.500**,
pwc-16065 (30) 4.167, Gray (54) 4.167, three graphs on 70 vertices at 3.500,
and negative values down to −7.83 on the structured cubic graphs at 78–120
vertices (prisms and the like, whose pathwidth stays small).

**The smallest `c` with `pw ≤ N/6 − 1/6 + c` is 3.833 on every connected
cubic graph to 16 vertices (exhaustive, 4,681 graphs) and 4.500 on the 42
certified connected cubic graphs to `N = 120`**, attained by the Coxeter
graph. The sequence of record-holders, `K_4`, Petersen, Heawood, Pappus,
McGee, Coxeter, is the small cages: high girth is what makes `pw/N` large.
Measured to `N = 16` exhaustively and on 42 certified graphs to 120; a
constant budget is not claimed beyond that, and the `solution` row for the
112-vertex cubic graph (excess 5.5 as an upper bound) shows where the record
stops.

### 1.5 The Poisson evaluation on the pilot (f)

On `G(n, c/n)` the degree law is Poisson(`c`) in the limit, so the histogram
term per vertex should be `Σ_d P_c(d) g(d)` (`poisson_value(c)`: 0.1826,
0.2853, 0.4575, 0.5761, 0.6558 at `c = 3, 4, 6, 8, 10`). All rows of the
cells, proved or not (the terms need no pathwidth); the full table for
`n = 60, 70, 80, 90, 100, 120` is in `tables.md`, two sizes here:

| `n` | `c` | rows | proved | Poisson | histogram/n (mean ± sd) | main/n (mean ± sd) | gain (hist − main)/n | pw/n (proved) | pw/main (proved) |
|---|---|---|---|---|---|---|---|---|---|
| 60 | 3 | 136 | 136 | 0.1826 | 0.1767 ± 0.034 | 0.1532 ± 0.038 | 0.0235 | 0.1355 | 0.906 |
| 60 | 4 | 136 | 136 | 0.2853 | 0.2827 ± 0.035 | 0.2734 ± 0.038 | 0.0093 | 0.2045 | 0.751 |
| 60 | 6 | 134 | 134 | 0.4575 | 0.4539 ± 0.032 | 0.4526 ± 0.032 | 0.0013 | 0.3129 | 0.692 |
| 60 | 8 | 132 | 132 | 0.5761 | 0.5768 ± 0.025 | 0.5766 ± 0.025 | 0.0002 | 0.4005 | 0.694 |
| 60 | 10 | 133 | 133 | 0.6558 | 0.6547 ± 0.017 | 0.6547 ± 0.017 | 0.0000 | 0.4634 | 0.708 |
| 120 | 3 | 13 | 3 | 0.1826 | 0.1820 ± 0.029 | 0.1604 ± 0.033 | 0.0216 | 0.1000 | 0.819 |
| 120 | 4 | 13 | 0 | 0.2853 | 0.2830 ± 0.023 | 0.2745 ± 0.026 | 0.0085 | — | — |
| 120 | 6 | 13 | 0 | 0.4575 | 0.4454 ± 0.033 | 0.4442 ± 0.033 | 0.0012 | — | — |
| 120 | 8 | 13 | 0 | 0.5761 | 0.5685 ± 0.017 | 0.5684 ± 0.017 | 0.0001 | — | — |
| 120 | 10 | 13 | 0 | 0.6558 | 0.6511 ± 0.012 | 0.6511 ± 0.012 | 0.0000 | — | — |

The histogram term matches the Poisson value to within 0.012 per vertex at
every cell (the sample sd is 0.012–0.041, and the finite-`n` degree law is
Binomial(`n − 1`, `c/n`)). **The reduction's gain** on `G(n, c/n)` is 0.021–0.025
per vertex at `c = 3` (vertices of degree ≤ 2 and pendant trees), 0.009 at
`c = 4`, 0.001 at `c = 6` and nothing from `c = 8`: the two forms of
Corollary 5.2 are the same bound above `c ≈ 6` and differ by 12% of the bound
at `c = 3`. Against the proved pathwidths the bound is 1.1–1.2× the truth at
`c = 3` and 1.4–1.5× at `c = 6–10` (`n = 60`); the survey's §7(d) put the
same factor at 1.6–1.85 against the *fitted slopes*, which sit below the
finite-size `pw/n` by the fit's positive intercept (0.268 against 0.313 at
`c = 6`), so the two numbers agree.

![histogram term, main term and the Poisson value per vertex against c at n = 120](scratch/edwards_mcdermid/01_verify/poisson_n120.png)

The survey §7(e)-style column (per pilot cell: `pw/n` over proved rows,
`main/n` over all rows, their ratio and the cell's maximum deficit) is the
second table of `tables.md` §(f), 81 cells. Its shape: at `c ≤ 1` the main
term is 0 (every graph reduces to empty) and the deficit is the pathwidth,
2–3; at `c = 1.5–2` the ratio `pw/main` is 1.2–4 and the deficit's maximum
3–3.3 at every `n`; from `c = 3` at `n ≥ 50` and from `c = 4` at `n = 30` the
main term alone bounds every proved graph in the cell (maximum deficit
negative, down to −13 at `n = 70, c = 10`).

### 1.6 Theorem 5.3's average-degree form (g)

`g(d̄) n` with the paper's linear interpolation, where the theorem applies
(connected, or `d̄ ≥ 5`):

| source | graphs where it applies | connected | `d̄ ≥ 5` | max `pw − g(d̄)n` | median | share `≤ 0` | `main term > g(d̄) n` | median (`g(d̄)n` − main) |
|---|---|---|---|---|---|---|---|---|
| dataset | 16,499 | 16,446 | 3,659 | 4.333 | 0.000 | 53.4% | **0** | 0.667 |
| ensemble | 33,652 | 31,764 | 31,053 | 2.667 | −4.622 | 85.9% | **0** | 0.627 |
| pilot | 2,596 | 2,527 | 2,075 | 2.667 | −6.254 | 97.2% | **0** | 1.217 |

The Edwards–Farr averaging lemma (`f(r(G)) ≤ g(d̄) n` for connected `G` or
`d̄ ≥ 5`, attributed to [8] and not proved in the paper) holds on all 52,747
graphs where it applies, with a median slack of 0.6–1.2. **Its hypothesis is
needed**: among the 5,487 proved graphs that are disconnected with
`2 ≤ d̄ < 5`, `main term > g(d̄) n` on 1,431 (a component of high degree
beside a sparse one; Jensen runs the other way across components). The
maximum of `pw − g(d̄) n` where the theorem applies is again the Coxeter
graph (cubic, so `g(d̄) n = N/6` is the main term).

**Kill verdict: not met** (no violation of any deterministic statement; no
graph with `main term > histogram term`; no degree raised). The brief's
"violation of Corollary 5.2" is unfalsifiable at these sizes, as the plan said
(§0.4 item 4), and the table of §1.3 is what the item exists to measure.

**What this does not claim.** Anything about the constants in the paper's
`o(n) + O(log n)` beyond what the record shows at these sizes (`n ≤ 2,916`;
cubic graphs to 16 exhaustively and 42 certified to 120); that `B(n) = 5` or
`c = 4.5` bounds any graph not on record (the record-holders are cages and
the record's cages stop at 28 and 54 vertices; nothing on it says how the
excess grows with `N`); that the paper's bound is tight
anywhere (it is 1.1–1.5× the truth on the pilot); anything about Theorem 5.3
beyond the numerical check of its averaging lemma (not formalised); that
`τ_FH` is the paper's `τ` (the paper leaves `τ` unspecified; `τ_FH` is read
off Fomin & Høie's Theorem 5).
