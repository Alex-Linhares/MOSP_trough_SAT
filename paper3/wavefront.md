# The maximum wavefront of a symmetric matrix: an exact member of the pathwidth complex

Candidate row 8 of `complex_members.md`. Written 2026-10-09. Its sources are
Kumfert & Pothen (1997), read first-hand; a brute-force check
(`paper3/wavefront_check.py`); and a Lean proof
(`lean/MOSPFormalization/Complex/Wavefront.lean`).

**Verdict.** Under Kumfert & Pothen's definition, the minimum over symmetric
orderings of the maximum wavefront equals `pw(G) + 1` on every graph with at
least one vertex. Here `G` is the adjacency graph of the matrix's nonzero
pattern. The equality holds per ordering as well as at the optimum. It is
proved in Lean with no `sorry` and no axioms beyond the standard three, and
checked on 5.4 million (graph, ordering) pairs. Kumfert & Pothen state the
definition and nothing about pathwidth or separation. **Their wavefront is,
set for set, Kornai & Tuza's out-sequence narrowness shack.** The row is
therefore a new *name and discipline* for an existing row, not new
mathematics. Section 6 recommends adding it on those terms.

---

## 1. What Kumfert & Pothen say

Source: G. Kumfert and A. Pothen, *Two improved algorithms for envelope and
wavefront reduction*, ICASE Report No. 97-33 (NASA CR-201714), July 1997. The
documentation page says "To appear in BIT, 1997", and Díaz, Petit & Serna
(2002) cite it as *BIT* 37(3). Page numbers below are the report's printed
numbers, with the PDF page in brackets.

**The setting** (§2.1, p. 3 [PDF 7]): "Consider a sparse symmetric n × n
matrix A = [a_ij], whose diagonal elements are all nonzero. We consider only
the lower triangle of A (including the diagonal)."

**The definition** (§2.1, p. 4 [PDF 8], verbatim):

> Consider the ith step of Cholesky factorization where only the lower triangle
> of A is stored. An equation (row) k is *active* at the ith step if k ≥ i and
> there exists a column l ≤ i such that a_kl ≠ 0. The ith *wavefront* of A,
> wf_i(A), is the set of *active* equations during the ith step of Cholesky
> factorization. We can describe the ith wavefront in three ways that are more
> intuitive. It is the set of rows that have nonzeros in the submatrix
> consisting of the first i columns of A and rows i to n. It is also the set of
> rows in the ith column that are within the envelope of the matrix, where the
> ith row is also included. We can also define the ith wavefront in terms of
> the adjacency graph of A. If X is a set of vertices in a graph, then its
> adjacency set adj(X) = (∪_{v∈X} adj(v)) \ X. In the adjacency graph of A, the
> ith wavefront consists of the vertex i together with the set of vertices
> adjacent to the vertices numbered from 1 to i. Formally, the ith wavefront is
> wf_i(A) = v_i ∪ adj({v_1, v_2, …, v_i}).
>
> The n wavefront sizes (one for each column) can be characterized by the
> values *maximum wavefront* and *mean-square wavefront*
> maxwf(A) = max_{1≤i≤n} {|wf_i(A)|},  mswf(A) = (1/n) Σ_{i=1}^n |wf_i(A)|².
>
> The maximum wavefront size measures the maximum storage needed for a frontal
> matrix during a frontal factorization, while the mean square wavefront
> measures the number of floating point operations in the factorization.
> Duff, Reid, and Erisman [9] discuss the application of wavefront reducing
> orderings to frontal factorization. It is easy to verify the identity
> Σ_{i=1}^n |wf_i(A)| = n + Σ_{i=1}^n rw_i(A) = n + E_size.

On orderings (same page): "The envelope and wavefront parameters depend on the
order in which vertices of the graph are numbered and are independent of the
numerical values of the actual matrix elements. This process of vertex
numbering permutes the corresponding matrix symmetrically by rows and columns
… A′ = PAP^T."

So, point by point:

- **Row or column.** A wavefront is a set of *rows* (equations), indexed by
  the step, which is a *column*: "the n wavefront sizes (one for each
  column)".
- **Maximum or mean.** Both are defined. `maxwf` is the maximum, and `mswf`
  is the mean of the squares. Only `maxwf` is a pathwidth quantity (§2.3).
- **The diagonal counts.** Row `i` is active at step `i` because `a_ii ≠ 0`
  is assumed. The graph form says "the vertex i together with …". In §3.1,
  p. 10 [PDF 14] they repeat it: "(Recall that the definition of the
  wavefront includes the diagonal element.)"
- **Symmetry.** `A` is symmetric, only its lower triangle is used, and the
  ordering is a symmetric permutation `PAP^T`. That is what makes the
  problem a graph problem on the adjacency graph.
- **Relations stated.**
  - The identity `Σ|wf_i| = n + E_size` with the envelope size (profile
    minus the diagonal), on p. 4.
  - Frontal factorisation: `maxwf` is the frontal-matrix storage (p. 4), and
    the work is `(1/2) Σ |wf_i| (|wf_i| + 3)` (§6.1, p. 25 [PDF 29]).
  - Bandwidth: "the Sloan, spectral, and the hybrid algorithms all reduce the
    wavefront size and envelope size at the expense of increased bandwidth"
    (§5.2, p. 24 [PDF 28]).
  - Separators, as an upper bound only: overlap graphs with
    `O(n^{(d−1)/d})` separators have maximum wavefront `O(n^{(d−1)/d})`
    under a modified nested dissection ordering (Appendix A, pp. 32–33
    [PDF 36–37]). The introduction (p. 2) also cites George & Pothen for
    mean-square wavefront bounds on graphs with small separators.
- **A loose sentence to set aside.** §3.1, p. 10, says "At any step k, the
  sum of the sizes of the active vertices is exactly the size of the
  wavefront at that step". There, "active" means unnumbered and adjacent to
  a numbered vertex. Read literally, this omits the vertex being numbered
  when that vertex is not yet active. It describes the bookkeeping of
  Sloan's algorithm and is not a definition. The §2.1 definition and the
  "Recall …" sentence govern.
- **Citations for the definition.** Kumfert & Pothen give none for the
  definition itself. They cite Duff, Reid & Erisman [9] (*Direct Methods for
  Sparse Matrices*, 1986) for the application to frontal factorisation, and
  Sloan [39] (1986, "An algorithm for profile and wavefront reduction of
  sparse matrices") for the algorithm and for the term *profile*. **Everstine
  (1979) is not cited.** It reaches this repository only through Díaz, Petit
  & Serna (2002, §10.4), who cite it in a list of heuristic papers.
- **Pathwidth and vertex separation.** **Nothing.** The words pathwidth,
  path-width, vertex separation, interval graph and gate matrix do not occur
  in the report. A scan of every PDF in `literature/` for "wavefront", "wave
  front" and "frontwidth" finds only this report (79 lines) and two lines of
  Díaz, Petit & Serna, both bibliographic. **The equality is stated in no
  held source.**

## 2. The definition paper 2 should use

### 2.1 Problem / Instance / Question

**1.14 Maximum wavefront (frontal elimination of a sparse symmetric matrix)**

**Instance.** A symmetric `n × n` matrix `A` with every diagonal entry
nonzero, given by its nonzero pattern, and an integer `K`.

**Question.** Is there a symmetric permutation `A' = PAP^T` with
`maxwf(A') ≤ K`? Here `wf_i(A')` is the set of rows `k ≥ i` that have a
nonzero `a'_kl` in some column `l ≤ i`, and `maxwf(A') = max_{1≤i≤n} |wf_i(A')|`.

The least such `K` is `wf(A)`. (Kumfert & Pothen 1997, §2.1, p. 4.)

**On graphs.** Let `G = G(A)` be the adjacency graph: vertex set `{1..n}`,
with `kl ∈ E` iff `k ≠ l` and `a_kl ≠ 0`. A symmetric permutation is a
layout `v_1, …, v_n`. Let `V_i = {v_1, …, v_i}` and `N(X) = ∪_{x∈X} N(x)`.

- For `k > i`: row `k` is active at step `i` iff `v_k` has a neighbour in
  `V_i`. Since `l ≤ i < k`, we have `l ≠ k`, so the nonzero is
  off-diagonal.
- For `k = i`: row `i` is always active, through `a_ii ≠ 0` with `l = i`.

Hence

    wf_i = {v_i} ∪ (N(V_i) \ V_i),     |wf_i| = 1 + |N(V_i) \ V_i|        (1)

This is Kumfert & Pothen's own graph form, `v_i ∪ adj(V_i)`, and it derives
from their matrix form. The `+1` is `v_i`, the diagonal. The step index runs
`i = 1..n`, so the boundary term ranges over
`|N(V_1)\V_1|, …, |N(V_n)\V_n| = 0`. It never includes `V_0 = ∅`.

Every matrix pattern with nonzero diagonal is a graph, and every graph is a
pattern (take `I` + adjacency matrix). So `wf` is a graph invariant, `wf(G)`.

### 2.2 The off-by-one, checked against their definition

`complex_members.md` paraphrased the wavefront as
`{v_i} ∪ (N(V_i) \ V_i)` with `|wf_i| = 1 + |N(V_i) \ V_i|`. Equation (1)
derives that from the matrix definition (rows `k ≥ i`, columns `l ≤ i`,
diagonal nonzero), so the paraphrase is right.

`wavefront_check.py figure1` also reproduces Kumfert & Pothen's Figure 1(c)
row for row:

- the 4×4 grid numbered along anti-diagonals has
  `f_i = 1,1,1,2,2,3,4,4,5,6,7,8,9,11,12,14`;
- `rw_i` matches the figure;
- `wf_i = 3,4,4,5,5,5,5,5,5,4,4,4,3,3,2,1`;
- `E_size = 46`, `bw = 4`, `maxwf = 5`, `mswf = 16.375` (they print ≈ 16.4).

So the coded definition is theirs, including `wf_1 = 3 = 1 + deg(v_1)` and
`wf_n = 1`. The pathwidth of the 4×4 grid is 4, and `maxwf = 5 = pw + 1` for
this ordering, which is therefore optimal.

### 2.3 Variants, for the record

| variant | relation to pw |
|---|---|
| Kumfert & Pothen `maxwf` (diagonal counted) | **exact, `pw + 1`** (`n ≥ 1`) |
| wavefront without row `i`, i.e. `max_i \|N(V_i)\V_i\|` (active rows *after* step `i`) | exact, `pw` (the same proof, minus the 1) |
| mean wavefront `(1/n)Σ\|wf_i\|` | `1 + E_size/n`: the profile / sum-cut problem (Díaz, Petit & Serna §2: PROFILE ≡ SUMCUT), not a pathwidth quantity |
| mean-square `mswf` | a sum-type cost like the profile; not a pathwidth quantity, and no fixed offset |

Only the maximum is in the complex. Paper 2 should use `maxwf` exactly as
Kumfert & Pothen define it, which gives offset `+1`.

## 3. The theorem and its proofs

**Theorem W.** Let `A` be a symmetric matrix with nonzero diagonal, and let
`G` be its adjacency graph on `n ≥ 1` vertices. Then:

1. *Per ordering*: for every layout `σ = (v_1, …, v_n)`,
   `maxwf(σ) = vs(σ^rev) + 1`, where `vs` is Kinnersley's vertex separation
   of a layout. Equivalently, `maxwf(σ) = 1 + max_i |N(V_i) \ V_i|`.
2. *At the optimum*: `wf(A) = min_σ maxwf(σ) = vs(G) + 1 = pw(G) + 1`.

**Edge cases.**

- *No rows* (`n = 0`): there are no steps, and `wf = 0` under the Lean
  convention (`minMaxWavefront_of_isEmpty`), while `pw + 1 = 1`. Hence the
  hypothesis `n ≥ 1`, the same as for narrowness and interval thickness.
- *Diagonal matrix* (edgeless `G`): every `wf_i = {v_i}`, so `wf = 1 = pw + 1`.
- *1 × 1 matrix*: `wf = 1 = pw + 1`.
- *Zero diagonal entries* are excluded by Kumfert & Pothen's hypothesis. If
  `a_ii = 0` were allowed, row `i` could be inactive at step `i`, and the
  value could fall to the variant `max_i |N(V_i)\V_i|`, or between the two.
  It is no longer a function of `G` alone.
- *Disconnected* `G` needs nothing special.

**Proof.** Fix `σ`. By (1), `|wf_i| = 1 + |N(V_i) \ V_i|` for `1 ≤ i ≤ n`.
Let `σ^rev = (v_n, …, v_1)`, and let `L = σ^rev` as a layout, so that its
prefix of length `j` is `U_j = V \ V_{n−j}`. Kinnersley's separating set of
`L` at `j` is

  `V_L(j) = { u ∈ U_j : u has a neighbour outside U_j }`
  `= { u ∉ V_{n−j} : u has a neighbour in V_{n−j} } = N(V_{n−j}) \ V_{n−j}`.

So for `1 ≤ i ≤ n − 1`, `|N(V_i) \ V_i| = |V_L(n − i)|`, with `n − i`
ranging over `1, …, n − 1`, which is exactly the range in the definition of
`vs` (§1.2 of `problem_transformations.md`). At `i = n` the term is `0`. As
`n ≥ 1`, the maximum over `i` is attained, and

  `maxwf(σ) = 1 + max(0, max_{1≤j<n} |V_L(j)|) = 1 + vs_L = vs(σ^rev) + 1`.

Reversal is a bijection on layouts, so minimising over `σ` gives
`wf(A) = vs(G) + 1`, and (E1), Kinnersley 1992 Thm 3.1, gives
`vs(G) = pw(G)`. `□`

(In the Lean library's suffix convention, `activeSuffix σ i` is the set of
suffix vertices with a neighbour in the prefix, which is `N(V_i) \ V_i`
itself. There the identity is `|wf_i| = vertexSepAt σ i + 1` with no
reversal. The reversal is only the change between the two conventions, as
for narrowness in (E6).)

**Corollary (the coincidence).** In Kornai & Tuza's out-sequence version of
narrowness (§2), the vertex `v` enters the shack just before the first `w_j`
in its closed neighbourhood leaves. The shack just before `w_i` leaves is
therefore `{ v : position(v) ≥ i, some u ∈ N[v] has position ≤ i }`. That is
Kumfert & Pothen's set of active rows word for word, so `maxwf(σ)` is the
out-sequence narrowness of `σ`, and `wf(G) = ν(G)` on every graph, the empty
one included. The same set is Chu & Stuckey's closing-order cost
`|N[U_i] \ U_{i−1}|` (`pathwidth_solver/pathwidth/graph.py::search_cost`).
So in the MOSP graph, the open stacks of a customer closing order are the
wavefronts of that order.

**In plain English.** Gaussian elimination works through the matrix one
column at a time. At step `i`, the rows still "in play" are row `i` itself,
plus every later row that has a nonzero entry in one of the columns already
processed. In graph terms, the rows in play are the current vertex plus
every not-yet-processed vertex with a processed neighbour. Now run the order
backwards. The not-yet-processed vertices become the ones processed first,
and "an unprocessed vertex touching a processed one" becomes "a vertex
already placed that still has a neighbour to come". That is the count vertex
separation measures. So the largest set of rows in play is one more than the
vertex separation of the reversed order, and the best order gives pathwidth
plus one, the one being the diagonal entry of the current row.

## 4. Brute force

`paper3/wavefront_check.py` was run on one core per process, at most two
processes at once. It computes the wavefront from the **matrix** definition:
it builds `PAP^T` and counts the rows `k ≥ i` with a nonzero in a column
`≤ i`, diagonal set nonzero. It does not use the graph paraphrase.

| check | scope | result |
|---|---|---|
| `figure1` | Kumfert & Pothen Fig. 1(c) | `f_i`, `rw_i`, `wf_i`, `E_size = 46`, `bw = 4`, `maxwf = 5`, `mswf = 16.375` reproduced |
| `atlas` | all 1,252 graphs on 1–7 vertices (networkx atlas), **every ordering**: 5,378,453 (graph, ordering) pairs | per ordering, `maxwf = 1 + vs(reversed)` (textbook `vs`) on all; matrix form = Kumfert & Pothen's graph form on all; `Σ wf_i = n + E_size` on all. `min maxwf − pw = 1` on **1,252 / 1,252**, with `pw` from `pathwidth_solver` and equal to the exhaustive `min vs`; an independent subset DP for `min maxwf` agrees on 1,252 / 1,252. 2 min 17 s |
| `random 3000` | 3,000 `G(n, p)`, `n ∈ 8..16`, `p ∈ {.1,.2,.3,.5,.7}` | `min maxwf` (subset DP over placed sets, no vs code) `− pw` (`pathwidth_solver`, proved) = 1 on **3,000 / 3,000**. 89 s |
| `orders 1000` | 1,000 `G(n, p)`, `n ∈ 20..80`, 5 random orderings each | per-order identity `maxwf = 1 + vs(reversed) = 1 + vertex_separation_masks(closed masks, order)` on **5,000 / 5,000**; the solver's optimal order has `maxwf = pw + 1` on all 328 graphs with `n ≤ 40` it proved within 20 s |

No exception was found. The earlier check, `complex_members_check.py wave`,
used the graph paraphrase and one DP. This one adds the matrix definition,
exhaustive orderings, the per-order identity and the external solver.

## 5. Lean

File: `lean/MOSPFormalization/Complex/Wavefront.lean`. It is imported in
`lean/MOSPFormalization.lean`, and **`lake build` passes** (1,670 jobs). The
one `sorry` warning in the build is the pre-existing §24 conjecture in
`Sandwich.lean`. The new file contains no `sorry` and no `axiom`.

**Definitions.**

- `MatrixNonzero G k l := k = l ∨ G.Adj k l`: a nonzero diagonal, plus the
  off-diagonal pattern given by `G`.
- `wavefront G σ i`: the rows `k` with `i ≤ σ k` and some `l` with
  `σ l ≤ i ∧ MatrixNonzero G k l`. This is Kumfert & Pothen's
  active-equation definition, verbatim.
- `maxWavefront G σ`: the sup over `Fin n`.
- `minMaxWavefront G`: the `sInf` over layouts.

**Theorems.**

| theorem | statement |
|---|---|
| `wavefront_eq_insert_activeSuffix` | `wavefront G σ i = insert (σ.symm i) (activeSuffix G σ i)` |
| `card_wavefront` | `(wavefront G σ i).card = vertexSepAt G σ i + 1` (per step) |
| `maxWavefront_eq_vertexSepOfLayout_add_one` | `[Nonempty V]`: `maxWavefront G σ = vertexSepOfLayout G σ + 1` (per ordering) |
| `minMaxWavefront_eq_vertexSeparation_add_one` | `[Nonempty V]`: `minMaxWavefront G = vertexSeparation G + 1` |
| `minMaxWavefront_eq_pathwidth_add_one` | `[Nonempty V]`: `minMaxWavefront G = pathwidth G + 1` (via `vertexSeparation_eq_pathwidth`) |
| `minMaxWavefront_of_isEmpty` | `[IsEmpty V]`: `minMaxWavefront G = 0` |
| `wavefront_eq_outShackBeforeMove` | `wavefront G τ i = outShackBeforeMove G τ i` (Kornai & Tuza's out-sequence shack) |
| `wavefront_eq_shackAfterPut_reverse` | the reversal statement in the textbook (prefix-boundary) convention: `wavefront G τ i = shackAfterPut G (reverseLayout τ) (rev i)` |
| `maxWavefront_eq_outNarrowness`, `minMaxWavefront_eq_narrowness` | `maxwf = ` out-narrowness per ordering; `minMaxWavefront G = narrowness G` on every graph |

The library's `vertexSepAt` uses the active-suffix convention. In that
convention the per-step identity needs **no** reversal. The reversal appears
only against the textbook convention, through
`wavefront_eq_shackAfterPut_reverse`.

**Axiom check.** `cd lean && lake env lean ../paper2/axiom_check.lean`. Nine
`#print axioms` lines were added before the control line. Every one prints
`[propext, Classical.choice, Quot.sound]`. The control
`conjecture_sqrt_tw_f6` still shows `sorryAx`, as intended.

## 6. Recommendation

**Add it to Table 1.1 as a new exact row**, marked "New: not in Linhares and
Yanasse (2002)" like pebbling, but described honestly:

- *Discipline:* Numerical linear algebra (sparse matrices, frontal
  elimination). It is the only row from that field, which is the case for
  including it: the table's point is that one quantity was studied under
  different names in fields that do not read each other.
- *Reference:* Kumfert & Pothen (1997), *BIT* 37(3), or the held ICASE
  Report 97-33, §2.1, for the definition. Optionally cite Sloan (1986) or
  Duff, Erisman & Reid (1986) as the origin of the quantity in frontal
  methods. Neither is held, so cite them only after obtaining them.
- *What differs from pebbling.* For pebbling, the theorems were published
  and the membership was new. Here **the definition is published and the
  equality is ours**. It is elementary, two lines from (1) plus Kinnersley,
  and doubtless folklore in sparse-matrix work, but no held source states
  it.
- *The caveat the footnote must carry.* The row is not a new problem in
  disguise. Kumfert & Pothen's set of active equations is, verbatim, Kornai
  & Tuza's out-sequence shack. So `wf(G) = ν(G)` on every graph (Lean:
  `minMaxWavefront_eq_narrowness`), and the row is narrowness under its
  numerical-linear-algebra name. It is not a mathematically independent
  witness of the complex.
- *Side effect for the owner.* The Table 1.1 caption says "the last row,
  below the rule: a thirteenth member". It would need "the last two rows …
  two members the table missed", and the "Thirteenth member" paragraph would
  become "Two more members". The master table (`tab:master`) and Appendix
  `app:lean` would each gain one line.

**Not recommended:** the mean-square or mean wavefront. These are
profile-type sums with no fixed offset to `pw`.

### Drafted LaTeX (not applied; `paper2/latex/` untouched)

Row, below the pebbling row, inside the "New" block:

```latex
\emph{Progressive pebbling}$^{c}$ & Graph theory & \citet{LY2002ref10} & exact: $\pw+1$ \\
\emph{Maximum wavefront}$^{d}$ & Numerical linear algebra & \citet{KumfertPothen1997} & exact: $\pw+1$ \\
\multicolumn{4}{@{}l@{}}{\footnotesize\emph{New: not in \citet{LY2002}.}} \\
```

Footnote, appended after `$^{c}$…`:

```latex
$^{d}$Added by us. The least, over symmetric orderings of a sparse symmetric
matrix with nonzero diagonal, of the largest wavefront (the rows active at a
step of the elimination, the current row included), as defined by
\citet[\S2.1, p.~4]{KumfertPothen1997}; as a graph parameter it is
narrowness read in the out-sequence form, set for set. The equality with
$\pw+1$ (for a nonempty matrix) is not stated in the source; we prove it in
Lean (Appendix~\ref{app:thirteenth}).
```

Bibliography entry (BIT pages to be confirmed against the journal before use;
the held copy is the ICASE report):

```bibtex
@article{KumfertPothen1997,
  author  = {Kumfert, Gary and Pothen, Alex},
  title   = {Two improved algorithms for envelope and wavefront reduction},
  journal = {BIT Numerical Mathematics},
  volume  = {37},
  number  = {3},
  year    = {1997},
  note    = {Also ICASE Report No.~97-33, NASA CR-201714, July 1997}
}
```

Introduction paragraph, after the pebbling paragraph (or merged into it as
"Two more members"):

```latex
\paragraph{A fourteenth member.} The table also has no row from numerical
linear algebra, although one of its quantities is a staple there. In the
frontal method for a sparse symmetric matrix, the \emph{wavefront} at step
$i$ is the set of rows still active, the current row together with every later
row that has a nonzero in a column already eliminated, and its maximum over
the steps is the storage the frontal matrix needs
\citep[\S2.1]{KumfertPothen1997}. Reordering the matrix to make that maximum
small is exactly the problem of the table: the least maximum wavefront over
symmetric orderings is the pathwidth of the matrix's adjacency graph plus one,
on every nonempty matrix, and the wavefront is, row for row, the shack of
narrowness read in its out-sequence form. The source defines the quantity but
does not state the equality; we prove it in Lean
(Appendix~\ref{app:thirteenth}).
```

## Files

- `paper3/wavefront.md` — this report.
- `paper3/wavefront_check.py` — `figure1 | atlas | random N | orders N`.
- `lean/MOSPFormalization/Complex/Wavefront.lean` — new, sorry-free.
- `lean/MOSPFormalization.lean` — one import added.
- `paper2/axiom_check.lean` — nine `#print axioms` lines added before the
  control.
