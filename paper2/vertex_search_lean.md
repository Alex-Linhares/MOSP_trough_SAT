# The vertex search of Bienstock, Robertson, Seymour & Thomas: proved in Lean

Written 2026-10-09. Sources: BRST (1991) §5, pp. 282–283, read from the scan
(`literature/1991-Bienstock-Robertson-Seymour-Thomas-Quickly-Excluding-Forest-JCTB.pdf`,
`pdftotext -layout`); the Lean file
`lean/MOSPFormalization/Complex/VertexSearch.lean` (888 lines); the brute force
`paper2/vertex_search_check.py`.

**Verdict.** Proved, with no `sorry` and no axioms beyond `propext`,
`Classical.choice` and `Quot.sound`. On every finite graph with at least one
vertex, edgeless graphs included, the least `n` with a successful search of
BRST with every `|X_i| ≤ n` equals `pw(G) + 1`. The least `n` with a
*monotone* successful search equals it too. On a graph with an edge, both
equal the node search number. With no vertices, both are `0`. This was the
only row of paper 2 not proved in Lean, and now it is.

---

## 1. The definition, as formalised, against BRST's text

BRST p. 282 (the scan's text layer garbles the symbols; checked against the
page image): "let us say a *search* in G is a sequence (X_1, …, X_m) of
subsets of V(G), such that X_1 = ∅ and for 1 ≤ i < m, either X_{i+1} ⊆ X_i or
X_i ⊆ X_{i+1}. … Let B_1 = V(G), and inductively let B_i be the set of all
vertices v of G such that there is a path P of G between v and some vertex of
B_{i−1}, with V(P) ∩ X_i = ∅. … The search is *successful* if B_m = ∅. … A
successful search is *monotone* if B_1 ⊇ B_2 ⊇ … ⊇ B_m = ∅." (5.1): for an
integer n ≥ 0 the following are equivalent: (i) a successful search with each
|X_i| ≤ n; (ii) no blockage of order n; (iii) path-width ≤ n − 1; (iv) a
monotone successful search with each |X_i| ≤ n. (The text layer prints
"path-width < n − 1"; the page reads ≤.)

| BRST | Lean |
|---|---|
| sequence (X_1, …, X_m) of subsets of V(G) | `X : List (Finset V)` |
| X_1 = ∅ | `IsVertexSearch.head_eq : X.head? = some ∅` (so m ≥ 1) |
| X_{i+1} ⊆ X_i or X_i ⊆ X_{i+1}, 1 ≤ i < m | `IsVertexSearch.chain : X.IsChain (fun A B => B ⊆ A ∨ A ⊆ B)` |
| B_1 = V(G) | `regionSeq G X = regionsFrom G univ X.tail`, head `univ` |
| B_i: v with a path P from v to a vertex of B_{i−1}, V(P) ∩ X_i = ∅ | `nextRegion G X_i B_{i−1}`: `∃ u ∈ B, ∃ p : G.Walk v u, p.IsPath ∧ ∀ w ∈ p.support, w ∉ X` |
| successful: B_m = ∅ | `IsSuccessfulVertexSearch`: `(regionSeq G X).getLast? = some ∅` |
| monotone: B_1 ⊇ … ⊇ B_m | `IsMonotoneVertexSearch`: successful and `(regionSeq G X).IsChain (fun A B => B ⊆ A)` |
| least n in (i) | `vertexSearchNumber G := sInf {n \| ∃ X, IsSuccessfulVertexSearch G X ∧ ∀ Y ∈ X, Y.card ≤ n}` |
| least n in (iv) | `monotoneVertexSearchNumber G` (the same over monotone searches) |

Checks on the details:

* The path may have length zero (`Walk.nil`), so a vertex of `B_{i−1}` outside
  `X_i` stays in `B_i` (`sdiff_subset_nextRegion`). A vertex of `X_i` is never
  in `B_i`, because the path's support contains its start
  (`not_mem_of_mem_nextRegion`).
* `X_1` is not used to compute anything, as in the source: `B_1 = V(G)` by fiat.
* The search is "a path", so `IsPath` is required. `mem_nextRegion` shows
  this is equivalent to reachability through vertices outside `X`
  (`FreeReach G X`, from `NodeSearch.lean`), because any walk shortens to a
  path on a subset of its support.
* The length of `regionSeq G X` is `m`, one region per position.

Blockages (BRST's (ii)) are not formalised. The cycle (i) ⇒ (iii) ⇒ (iv) ⇒ (i)
closes without them.

## 2. The proof route

**(iii) ⇒ (iv), BRST's own construction.** Take a path decomposition
`(W_0, …, W_L)` of width `pw`. The search is `(∅, W_0, W_0 ∩ W_1, W_1, …,
W_{L−1} ∩ W_L, W_L)` (`bagPositions`, `PathDecomposition.isMonotoneVertexSearch`).
Write `U_j = W_0 ∪ … ∪ W_j`. A vertex of `U_j` with a neighbour outside `U_j`
lies in `W_j ∩ W_{j+1}`, by edge coverage and the interval property
(`IsBagSequence.boundary`). So after `W_j`, and again after `W_j ∩ W_{j+1}`,
the region is exactly `V − U_j` (`nextRegion_compl`, `foldl_bagPositions`).
The regions decrease (`isChain_regionsFrom_bagPositions`), and `U_L = V`. Each
position has at most `pw + 1` vertices. BRST give the construction in one
line; the proof that it works is ours.

**(i) ⇒ (iii), by reduction to node search.** BRST derive (i) ⇒ (ii) and then
use their (2.1). We instead reduce to the node search game of
`NodeSearch.lean`. Its full-game lower bound `vs + 1 ≤ ns`, recontamination
included, is already proved in `NodeMonotonicity.lean` by Bienstock–Seymour's
crusade argument. Play each change of position `X_i → X_{i+1}` as single
moves: remove the searchers of `X_i \ X_{i+1}`, then place those of
`X_{i+1} \ X_i` (`transitionMoves`, `simMoves`). Because consecutive
positions are nested, only one of the two lists is non-empty. The invariant
is that **every contaminated edge has an endpoint in the current region**:

* *while removing*, the region reachable from `B_i` while avoiding the
  current searchers (`touches_runSearch_remove`). This needs no hypothesis,
  because the region only grows as searchers leave;
* *while placing*, `B_i` minus the current searchers
  (`touches_runSearch_place`). An edge whose region endpoint was just covered
  has an unguarded other endpoint, and that endpoint is in `B_i` because
  `B_i` is closed under searcher-free steps;
* both rest on one step lemma (`touches_step`). A set that is unguarded,
  closed under searcher-free steps, and touched by every edge the move leaves
  contaminated is also touched by every recontaminated edge.

After the last position the region is `B_m = ∅`, so no edge is contaminated.
At every intermediate state the guards lie between `X_i` and `X_{i+1}`, so
there are at most `n` searchers. Hence a successful vertex search with all
`|X_i| ≤ n` is a node search with `n` searchers
(`isNodeSearch_of_isSuccessfulVertexSearch`), and `ns(G) ≤` the vertex search
number (`nodeSearch_le_vertexSearchNumber`). With an edge, `ns = pw + 1`
(`nodeSearch_eq_pathwidth_add_one`) gives `pw + 1 ≤` the vertex search
number. On an edgeless graph, `pw = 0` (`pathwidth_of_edgeless`), and with a
vertex, a search with no searchers leaves `B_m = V` (`one_le_vertexSearchNumber`).

The converse direction of the node reduction (a node search giving a vertex
search) is not needed and is false on edgeless graphs.

## 3. Theorem names (namespace `MOSPFormalization.Complex` unless noted)

| Statement | Name |
|---|---|
| vs-number = pw + 1, `[Nonempty V]` | `vertexSearchNumber_eq_pathwidth_add_one` |
| monotone vs-number = pw + 1, `[Nonempty V]` | `monotoneVertexSearchNumber_eq_pathwidth_add_one` |
| recontamination does not help | `vertexSearchNumber_eq_monotoneVertexSearchNumber` |
| (5.1) for each n: (i) ⇔ pw + 1 ≤ n ⇔ (iv) | `vertexSearch_iff` |
| = node search, graphs with an edge | `vertexSearchNumber_eq_nodeSearch` |
| edgeless: vs-number 1, ns 0 | `vertexSearchNumber_of_edgeless` |
| no vertices: both numbers 0 (and pw + 1 = 1) | `vertexSearchNumber_of_isEmpty`, `pathwidth_add_one_of_isEmpty` |
| (iii) ⇒ (iv) | `MOSPFormalization.PathDecomposition.isMonotoneVertexSearch`, `monotoneVertexSearchNumber_le_pathwidth_add_one` |
| (i) ⇒ node search | `isNodeSearch_of_isSuccessfulVertexSearch`, `nodeSearch_le_vertexSearchNumber` |
| (i) ⇒ (iii) | `pathwidth_add_one_le_vertexSearchNumber` |

`vertexSearch_iff` reads (iii) as `pw + 1 ≤ n`. This agrees with BRST's
`pw ≤ n − 1` for `n ≥ 1`. At `n = 0` with a vertex present, natural-number
subtraction would make `pw ≤ 0 − 1` true for an edgeless graph while (i) is
false. BRST's integers do not have this artefact.

## 4. Brute force

`python paper2/vertex_search_check.py` (about 20 s, one core):

* **(1)** The vertex search number, computed by search over states `(X, B)`
  (`brst_search` of `complex_members_check.py`), minus `pw + 1`, over all
  graphs on 1–7 vertices (networkx atlas): `{0: 52}` on ≤ 5, `{0: 208}` on
  ≤ 6, **`{0: 1252}` on ≤ 7**.
* **(2)** The reduction: 200,000 random searches on random graphs with ≤ 8
  vertices, each played as single node-search moves under Kirousis &
  Papadimitriou's semantics. In 109,234 of them the vertex search succeeded.
  **Zero violations** of the invariant at any position, and every successful
  vertex search left no contaminated edge.

## 5. Build and axiom check

* `cd lean && lake build`: completed successfully (1,671 jobs). The new
  module builds with no warnings. The only `sorry` in the build is the
  existing one in `Sandwich.lean` (the §24 conjecture).
* `lean/MOSPFormalization.lean` imports `MOSPFormalization.Complex.VertexSearch`.
* `paper1/axiom_check.lean` has eleven new `#print axioms` lines before the
  control. `cd lean && lake env lean ../paper1/axiom_check.lean` reports
  `[propext, Classical.choice, Quot.sound]` for every one of them:
  `isNodeSearch_of_isSuccessfulVertexSearch`, `nodeSearch_le_vertexSearchNumber`,
  `PathDecomposition.isMonotoneVertexSearch`, `pathwidth_add_one_le_vertexSearchNumber`,
  `vertexSearchNumber_eq_pathwidth_add_one`, `monotoneVertexSearchNumber_eq_pathwidth_add_one`,
  `vertexSearchNumber_eq_monotoneVertexSearchNumber`, `vertexSearch_iff`,
  `vertexSearchNumber_eq_nodeSearch`, `vertexSearchNumber_of_edgeless`,
  `vertexSearchNumber_of_isEmpty`. The control still shows `sorryAx`.

## 6. Suggested text for paper 2 (not applied; `paper1/latex/` untouched)

**Table 1.1, footnote d** (`sec1_intro.tex`), replacing "Exact on every graph,
… not proved in Lean.":

> $^{d}$Added by us. Searchers occupy vertices and an invisible fugitive moves
> along unguarded paths. Exact on every graph with a vertex, edgeless ones
> included \citep[(5.1)]{BRST1991}, and equal to node search when $G$ has an
> edge. We prove it in Lean (Appendix~\ref{app:thirteenth}).

**Master table row** (`sec2_equivalences.tex`, line 178):

> `Vertex search & \citet{BRST1991} & $=\pw+1$ ($V\ne\emptyset$), $=\ns$ ($E\ne\emptyset$) & exact \\`

**Theorem 2.x (exact core), a new item** after progressive pebbling. Then
delete the paragraph "One more member rests on a published proof … the
edgeless ones included." and begin the next sentence with "For the table,
this makes …":

> \item Vertex search: if $V\ne\emptyset$, the least $n$ admitting a
>   successful search of \citet[\S5]{BRST1991} with every $|X_i|\le n$ is
>   $\pw(G)+1$, monotone or not, and it equals $\ns(G)$ when $G$ has an
>   edge \citep[(5.1)]{BRST1991}~\leanref{vsearch}.

**Appendix A entry** (`sec9a_appendix_lean.tex`, after `pebbling`):

> `\leanentry{vsearch}{The vertex search is in the exact core (Appendix~\ref{app:thirteenth})} \leannames{vertexSearchNumber_eq_pathwidth_add_one, monotoneVertexSearchNumber_eq_pathwidth_add_one, isNodeSearch_of_isSuccessfulVertexSearch, vertexSearchNumber_eq_nodeSearch, vertexSearchNumber_of_isEmpty} \\`

**Appendix B paragraph** (`sec9b_appendix_machinery.tex`, "The vertex
search"), replacing the last sentence ("We have not formalised it; …"):

> We prove it in Lean~\leanref{vsearch}, both the equality and its monotone
> form. The upper bound is their construction: from a path decomposition
> $(W_1,\dots,W_r)$, the search
> $(\emptyset,W_1,W_1\cap W_2,W_2,\dots,W_r)$ is monotone, because after
> $W_j$ the fugitive's region is the set of vertices in no earlier bag. For the lower
> bound we do not use blockages, as they do. We reduce to node search: play
> each change of position as single placements and removals. Then every
> contaminated edge keeps an endpoint in the fugitive's region, so a
> successful vertex search with $n$ searchers is a node search with $n$
> searchers, and $\ns=\pw+1$ on graphs with an edge. On an edgeless graph
> $\pw=0$ and one searcher is needed. With no vertices the search
> $(\emptyset)$ already succeeds, so the value is $0$. A brute force over all
> 1,252 graphs with at most seven vertices agrees.

**Figure 2.1** (caption in `sec2_equivalences.tex`; drawing in
`paper1/section3_figure.py`): draw the vertex-search edge solid black like the
other exact edges, not grey. In the caption, replace "the grey edge is exact by
a published proof \citep[(5.1)]{BRST1991}, checked by brute force and not in
Lean, and holds whenever $G$ has an edge (the vertex search is $\pw+1$ on
every graph)." with:

> the vertex search edge holds whenever $G$ has an edge, and the vertex search
> is $\pw+1$ on every graph with a vertex
> \citep[(5.1)]{BRST1991}~\leanref{vsearch}.

Also update the opening sentence of that caption, "Solid edges are exact
relations and dashed edges bands, both proved in Lean", so that it covers
every edge but LaPaugh's dotted one.

**Section 2 summary** (line 386 onward): "Three problems the table does not
list are exact as well" can stay as written. The phrase "and gives an exact
variant…" is unaffected.
