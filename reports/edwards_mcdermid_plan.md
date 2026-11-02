# The Edwards–McDermid degree-sequence bound on pathwidth, verified and formalised — plan for Ralph loop0012

*2026-11-01. Written while loop0011 runs; nothing here was executed beyond
reading and ten-second checks. The loop files are `Ralph_Loops/loop0012/`;
each item there is self-contained. This document says what the loop stands
on (with the source quoted in full, so that a session can work from it if the
manuscript's temporary copy is gone), what it asks, in what order and at what
price, and where the paper and the repository correct the brief that produced
it. Nothing here changes a solver default; nothing re-solves an instance that
is already proved.*

## 0. What the loop stands on

### 0.1 The source

Keith Edwards and Eric McDermid, *A general reduction theorem with
applications to pathwidth and the complexity of MAX 2-CSP*, **Algorithmica**
72(4):940–968, 2015, DOI 10.1007/s00453-014-9883-7. The accepted manuscript
(dated April 29, 2014, 29 pages) is open at the University of Dundee's
Discovery portal:

    https://discovery.dundee.ac.uk/ws/portalfiles/portal/6880233/edwmcd_2_.pdf

A copy sat in `/tmp/lit_random/em2.pdf` (text `em2.txt`) on 2026-11-01 and may
be gone; **item 01 re-fetches it into `reports/scratch/edwards_mcdermid/`**
(not `literature/`: the owner's note in loop0011's TASK.md says nothing is
added to `literature/` from that pass, and this plan keeps to that) and
extracts the text with `pdftotext`. Page numbers below are the manuscript's.

What was found by it, in the second literature pass
(`reports/random_graph_pathwidth_literature_2.md` §3.3, branch
`appendix-picture`): on Poisson(`c`) degrees Corollary 5.2 gives
`pw/n ≤ 0.183, 0.458, 0.656` at `c = 3, 6, 10` (re-checked here: 0.1826,
0.4575, 0.6558), below every upper bound in the survey's §7(a) table at every
`c` from 2 to about 32, and within a factor 1.6–1.85 of the fitted slopes; the
paper's Appendix E already cites it (`paper1/latex/sec9e_appendix_random.tex`,
lines 364 and 554). This loop does what the project's rule requires before a
cited bound becomes a line in a figure: **verify it on every graph whose
pathwidth is on record, then formalise it**, conditional on the one external
theorem it rests on.

### 0.2 The statements, verbatim

**The weights** (manuscript p. 6, "Definition of functions `g_α` and `g'_α`"):

> For any `n ≥ 2`, and `α` with `0 ≤ α ≤ 1`, define the function `g_α(n)` by
> setting `g_α(2) = 0`, `g_α(3) = α`, and for any `n ≥ 4`,
> `n g_α(n) = (n − 2) g_α(n − 1) + g_α(n − 2) + 1`.
> We extend `g_α` to all real numbers at least 2 by linear interpolation, i.e.,
> if `r = n + x`, where `n ≥ 2` is an integer, and `0 ≤ x ≤ 1`, then we set
> `g_α(r) = (1 − x) g_α(n) + x g_α(n + 1)`. Also, for any `n ≥ 3`, define
> `g'_α(n) = g_α(n) − g_α(n − 1)`.

Its properties (p. 6–7, proved in the Appendix, Lemmas 8.1–8.5):

> 1. For any integer `n ≥ 2`,
>    `g_α(n) = (4 − 3α) A(n)/n! + (2 − 3α) (−1)^n/n! − (3 − 3α)`
>    where `A(n)` is the alternating factorial function given by
>    `A(n) = n! − (n − 1)! + … − (−1)^n · 1!`.
> 2. For all real `d ≥ 2`, `g_α(d) = 1 − (4 − 3α)/(d + 1) + O(1/d³)`.
> 3. If `α ≤ 1/2`, then `g_α` is non-decreasing, i.e., `g_α(n + 1) ≥ g_α(n)`
>    for all integers `n ≥ 2`.
> 4. If `1/6 ≤ α ≤ 3/10`, then `g'_α` is non-increasing, i.e.,
>    `g'_α(n + 1) ≤ g'_α(n)` for all integers `n ≥ 3`.
> 5. If `1/6 ≤ α ≤ 3/10`, `g_α(n)/n` is strictly decreasing for `n ≥ 5`.
> 6. For all `n ≥ 4`, `1 − g_α(n) = (n − 1) g'_α(n) + g'_α(n − 1)`.
>    This is just a rearrangement of the defining recurrence.

The table of values (p. 7), at `α = 1/6`, which is the pathwidth case:

| `d` | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|
| `g_{1/6}(d)` | 0 | 1/6 | 1/3 | 13/30 | 23/45 | 359/630 | 1553/2520 | 14827/22680 |
| `g'_{1/6}(d)` | — | 1/6 | 1/6 | 1/10 | 7/90 | 37/630 | 13/280 | 85/2268 |

(The `d = 9` column and the `g'` row are this plan's, from the recurrence in
exact rationals; properties 3, 4, 5, 6 and the closed form 1 were checked to
`n = 15` in ten seconds. Note `g'(3) = g'(4) = 1/6`: at `α = 1/6` the first
two increments are equal.) The paper's remark (p. 7): "For `α` outside the
range `[1/6, 3/10]`, the function `g'_α` is not monotone, and the reduction
method used below breaks down."

**The potentials** (p. 7):

> For any graph `G` with minimum degree at least 2, define `f_α(G)` by
> `f_α(G) = Σ_{v ∈ V(G)} g_α(d_G(v))`.
> Although `f_α(G)` is the main upper bound of interest, the inductive proof
> relies crucially on a small negative term, which depends on the minimum
> degree of each component. If `G` has minimum degree at least 3, with
> connected components `G_1, …, G_k`, set
> `f⁻_α(G) = f_α(G) − Σ_{i=1}^{k} g'_α(δ(G_i)) = Σ_{i=1}^{k} f⁻_α(G_i)`.
> Note that despite the negative term, `f⁻_α(G)` is always strictly positive.

**The reductions and basic graphs** (p. 8):

> Let `G` be a graph, and consider the following four operations on `G`:
> 1. Delete an isolated vertex of `G`.
> 2. Delete a vertex of degree 1 (and its incident edge).
> 3. Let `v` be a vertex of degree 2 with non-adjacent neighbours `x` and `y`;
>    delete `v` (and edges `vx`, `vy`) and add an edge between `x` and `y`.
> 4. Let `v` be a vertex of degree 2 with adjacent neighbours; delete `v` (and
>    incident edges).
> Let `r(G)` be a graph obtained from `G` by applying operations 1, 2, 3, 4
> above repeatedly until none is possible (because the graph has minimum
> degree at least 3 or is empty). It follows from the definition of the
> series-parallel property that `G` is series-parallel if and only if `r(G)`
> is empty. These reductions have been used by many authors, for example
> [5, 11, 14, 28]. (The resulting graph `r(G)` is in fact unique.)
>
> We will say a connected graph of minimum degree at least 3 is *basic* if
> either `G` is cubic or `r(G − v)` is empty for some `v ∈ V`. A graph is basic
> if every component is basic.

"Series-parallel" is defined on p. 5: "by a series-parallel graph we mean here
a simple graph with no `K_4`-minor or, equivalently, a graph of treewidth at
most 2"; and on p. 5, "It is well known that trees (with at least one edge)
have treewidth 1, and series-parallel graphs have treewidth at most 2. The
pathwidth of these graphs is `O(log n)`."

**Lemma 3.1** (p. 8): "Let `G = (V, E)` be a graph, `w` be a vertex of `G`,
and `X` be a subset of `V(r(G − w))`. Then `r(G − (X ∪ {w})) = r(r(G − w) − X)`."
Its proof invokes Kneis et al. [21]: "they define a valid reduction sequence to
be a sequence of operations, each of which is either a series-parallel
reduction of a vertex not in `D`, or removal of a vertex in `D`. They prove
that any two maximal valid reduction sequences produce the same graph."

**Theorem 3.2** (p. 9, the general reduction theorem):

> Let `G = (V, E)` be a graph with `n` vertices and minimum degree `δ ≥ 3`.
> Then there is a set `X_G ⊆ V` such that (i) `r(G − X_G)` is non-empty and
> basic, and (ii) `|X_G| + f⁻_α(r(G − X_G)) ≤ f⁻_α(G)` for any `α`,
> `1/6 ≤ α ≤ 3/10`.

Its proof (pp. 9–12) is by induction on `n`: basic graphs take `X_G = ∅`;
disconnected graphs take the union over components (additivity of `f⁻`);
for a connected non-basic `G` (so `Δ > 3`), "let `w` be a vertex of maximum
degree in `G`, chosen so that the degree of its lowest degree neighbour is as
small as possible", `v_1, …, v_Δ` its neighbours with
`d(v_1) ≤ … ≤ d(v_Δ)`, `G' = G − w`, `G* = r(G')` (non-empty since `G` is not
basic), `X_G = X_{G*} ∪ {w}`, and it suffices (equation (1)) to show
`1 + f⁻_α(G*) ≤ f⁻_α(G) = f_α(G) − g'_α(δ(G))`. The accounting (equations
(2)–(5)):

> `1 + f_α(G') = f_α(G) + (Δ − 1) g'_α(Δ) + g'_α(Δ − 1) − Σ_{i=1}^{Δ} g'_α(d_G(v_i))`
> (using property 6) `= f_α(G) − j_1(G) − j_2(G) − j_3(G)` with
> `j_1(G) = g'_α(d_G(v_1)) − g'_α(Δ − 1)`, `j_2(G) = g'_α(d_G(v_2)) − g'_α(Δ)`,
> `j_3(G) = Σ_{i=3}^{Δ} (g'_α(d_G(v_i)) − g'_α(Δ))`,
> `j_4(G) = f_α(G') − f_α(G*) + g'_α(δ(G*))`,
> and "it suffices to establish that, in all cases,
> `j(G) = j_1(G) + j_2(G) + j_3(G) + j_4(G) ≥ g'_α(δ(G))`."

The cases: "if `G'` contains a vertex `v` of degree `d ≥ 3`, then
`j_4(G) ≥ g'_α(d)`" (either `v` survives into `G*` with degree `≤ d`, so
`g'_α(δ(G*)) ≥ g'_α(d)` by property 4, or `v` is reduced away, so
`f_α(G') − f_α(G*) ≥ g_α(d) ≥ g'_α(d)`); if `G` is `Δ`-regular then
`j_1 = g'(Δ) − g'(Δ − 1) ≤ 0` but `G'` has a vertex of degree `Δ − 1`, so
`j ≥ j_1 + j_4 ≥ g'(Δ) = g'(δ(G))`; otherwise `j_1 ≥ 0`, and either `G'` has a
vertex `v` with `δ(G) ≥ d_{G'}(v) ≥ 3` (then `j ≥ j_4 ≥ g'(δ(G))`), or
`δ(G) = 3` with every degree-3 vertex adjacent to `w`, and then either
`d(v_Δ) > 3` (so `j ≥ j_1 + j_4 ≥ g'(3)`) or all neighbours of `w` have
degree 3, are reduced away, and `G*` non-empty forces a vertex `v` not
adjacent to `w` with `d_{G'}(v) ≥ 3`, so `j ≥ j_2 + j_4 ≥ g'(3)`. Remarks
(p. 12): "the set `X_G` is not necessarily unique", and Algorithm X
(choose a non-basic component, a max-degree vertex with a lower-degree
neighbour if possible, `G ← r(G − w)`, `X_G ← X_G ∪ {w}`) finds one.

**Section 5, the pathwidth application** (p. 19):

> Fomin and Høie [12] showed that a 3-regular graph `G` with `m` edges has
> pathwidth at most `(1/9 + o(1)) m + O(log n) = (1/6 + o(1)) n + O(log n)`.
> Hence for 3-regular graphs, there is a function `τ`, with `τ(n) = o(n)`,
> such that `pw(G) ≤ n/6 − 1/6 + τ(n) + O(log n)` (the negative term is
> needed below). We can also assume that `τ` is an increasing function of `n`
> (otherwise replace `τ` with `σ` given by `σ(n) = max_{i ≤ n} τ(i)`).
>
> **Lemma 5.1** Let `G = (V, E)` be a graph with `n` vertices and minimum
> degree `δ ≥ 3`. Then `pw(G) ≤ Σ_{v ∈ V(G)} g_{1/6}(d(v)) + τ(n) + O(log n)`.
>
> *Proof.* We will show that `pw(G) ≤ f⁻_{1/6}(G) + τ(n) + O(log n)`. […] We
> first show that for any basic graph `G`, we have
> `pw(G) ≤ f⁻_{1/6}(G) + τ(n) + O(log n)`. For a connected cubic graph `G`,
> `pw(G) ≤ n/6 − 1/6 + τ(n) + O(log n) = f⁻_{1/6}(G) + τ(n) + O(log n)` by
> the result of Fomin and Høie [12] above (this is where we use the negative
> term, since for a cubic graph `f⁻_{1/6}(G) = n/6 − 1/6`). If `r(G − v)` is
> empty, then `G − v` is series-parallel and so has pathwidth `O(log n)`, so
> `pw(G) = O(log n)` as required. If `G` is basic with connected components
> `G_1, …, G_k`, then `pw(G) = max_i pw(G_i) ≤ max_i (f⁻_{1/6}(G_i) + τ(|V(G_i)|) + O(log |V(G_i)|)) ≤ f⁻_{1/6}(G) + τ(n) + O(log n)`
> (Note that the fact that we have a maximum rather than a sum here is
> crucial.) Now for any graph `G` with minimum degree at least 3, there is a
> set `X_G` such that `|X_G| + f⁻_{1/6}(r(G − X_G)) ≤ f⁻_{1/6}(G)` and
> `r(G − X_G)` is basic and non-empty. It follows from the results of [21]
> that `pw(G) ≤ |X_G| + pw(G − X_G)` and that
> `pw(G − X_G) = pw(r(G − X_G)) + O(log n)`, so we have
> `pw(G) ≤ |X_G| + pw(G − X_G) = |X_G| + pw(r(G − X_G)) + O(log n) ≤ |X_G| + f⁻_{1/6}(r(G − X_G)) + τ(n) + O(log n) ≤ f⁻_{1/6}(G) + τ(n) + O(log n)`,
> as required.
>
> **Corollary 5.2** Let `G` be a graph, and `r(G)` be the reduced graph of
> `G`. Then
> `pw(G) ≤ Σ_{v ∈ V(r(G))} g_{1/6}(d_{r(G)}(v)) + τ(|V(G)|) + O(log |V(G)|) = Σ_{d ≥ 3} g_{1/6}(d) n_d + o(|V(G)|)`.
>
> **Theorem 5.3** Let `G` be a graph of average degree `d ≥ 2`, with `n`
> vertices and `m` edges. Then if `G` is connected, or `d ≥ 5`,
> `pw(G) ≤ (g_{1/6}(d) + o(1)) n = (2 g_{1/6}(d)/d + o(1)) m = (1 − (7/2)/(d + 1) + O(1/d³)) n`.

Theorem 5.3 rests on an averaging statement the paper attributes to Edwards &
Farr [8] (p. 18, proof of Theorem 4.9): "it can be shown that if `G` is a
graph with `n` vertices and average degree at most `d`, where `d ≥ 2`, and if
(i) `G` is connected or (ii) `d ≥ 5`, then we have
`f_α(r(G)) = Σ_{v ∈ V(r(G))} g_α(d_{r(G)}(v)) ≤ g_α(d) n` provided
`1/6 ≤ α ≤ 3/10`." That is not proved in this paper. On p. 20 they add: "It
follows easily from the results of Golovnev and Kutzkov [17] that for each
constant `0 < ε < 1` there exists a constant `d_ε = O(exp(1/ε))` such that if
`d_ε ≤ d ≤ n/(1 + ε)`, then `pw(G) ≤ (1 − 4ε ln d / d) n`."

**The base case, as Fomin & Høie state it** (held:
`literature/2006-Fomin-Hoie-Pathwidth-Cubic-Graphs-Exact-Algorithms-IPL.pdf`,
IPL 97:191–196; text at `/tmp/lit_random/held/…Fomin-Hoie….txt`, regenerate
with `pdftotext`):

> **Theorem 2** (Monien and Preis [19]). For any `ε > 0` there exists an
> integer `n_ε` such that for any 3-regular graph `G` with `|V(G)| > n_ε`
> there is a cut `(V_1, V_2)` of size at most `(1/6 + ε)|V(G)|` and such that
> `||V_1| − |V_2|| ≤ 1`.
> It follows from the proof in [19] that the value `n_ε` can be taken at most
> `(4/ε) · ln(1/ε) · (1 + 1/ε²)`. Also it is easy to check that the bound in
> Theorem 2 valid not only for 3-regular graphs but for graphs of maximum
> vertex degree at most three as well.
>
> **Theorem 3** (Ellis et al. [6]). For any tree `T` on `n ≥ 3` vertices,
> `pw(T) ≤ log_3 n`.
>
> **Lemma 4.** Let `G` be a graph on `n` vertices and with maximum vertex
> degree at most 3. Then for any vertex subset `X ⊆ V(G)` there is a path
> decomposition `P = (X_1, X_2, …, X_r)` of `G` of width at most
> `max{|X|, n/3 + 1} + (2/3) log_3 n + 1` and such that `X = X_r`.
>
> **Theorem 5.** For any `ε > 0`, there exists an integer `n_ε` such that
> for every graph `G` with maximum vertex degree at most three and with
> `|V(G)| > n_ε`, `pw(G) ≤ (1/6 + ε)|V(G)|`.
>
> *Proof.* For `ε > 0`, let `G` be a graph on `n > n_ε = (8/ε) · ln(1/ε) · (1 + 1/ε²)`
> vertices and with maximum vertex degree at most three. By Theorem 2, there
> is a bisection `V_1, V_2` of `G` such that there is at most `(1/6 + ε/2)|V(G)|`
> edges with endpoints in `V_1` and `V_2`. Let `∂(V_1)` (`∂(V_2)`) be the set
> of vertices in `V_1` (`V_2`) having a neighbor in `V_2` (`V_1`). Note that
> `|∂(V_i)| ≤ (1/6 + ε/2) n`, `i = 1, 2`. By Lemma 4, there is a path
> decomposition `P_1 = (A_1, …, A_p)` of `G[V_1]` and a path decomposition
> `P_3 = (C_1, …, C_s)` of `G[V_2]` of width at most
> `max{(1/6 + ε/2) n, n/6 + 1} + (2/3) log_3 n + 1 ≤ (1/6 + ε) n` such that
> `A_p = ∂(V_1)` and `C_1 = ∂(V_2)`. It remains to show how the path
> decomposition `P` of `G` can be obtained from path decompositions `P_1` and
> `P_3`. To construct `P` we show that there is a path decomposition
> `P_2 = (B_1, …, B_r)` of `G[∂(V_1) ∪ ∂(V_2)]` of width `≤ (1/6 + ε) n` and
> with `B_1 = ∂(V_1)`, `B_r = ∂(V_2)`. The union of `P_1`, `P_2`, and `P_3`,
> i.e., `(A_1, …, A_p, B_1, …, B_r, C_1, …, C_s)` will be the path
> decomposition of `G` of width `≤ (1/6 + ε) n`. The path decomposition `P_2`
> is constructed as follows. We put `B_1 = ∂(V_1)`. In a bag `B_j`, where
> `j ≥ 1` is odd, we choose a vertex `v ∈ B_j ∖ ∂(V_2)`. We put
> `B_{j+1} = B_j ∪ (N(v) ∩ ∂(V_2))` and `B_{j+2} = B_{j+1} ∖ {v}`. […] we argue
> that for any `j`, `|B_j| ≤ (1/6 + ε) n + 1`. [the count by `D_m`, the
> vertices of `∂(V_1)` with exactly `m` neighbours in `∂(V_2)`:
> `|D_1| + 2|D_2| + 3|D_3| ≤ (1/6 + ε) n`, so `|B_1| ≤ (1/6 + ε) n − |D_2| − 2|D_3|`
> and every bag is within `|D_2| + 2|D_3| + 1` of `|B_1|`.]

So the base case is a **one-level** construction: one near-equal bisection
with few cut edges (Monien–Preis), Lemma 4 on each side with the boundary as
the end bag (its `n/3 + 1` and `(2/3) log_3 n` come from the tree pathwidth
bound, Theorem 3), and a sweep across the boundary. Nothing recursive.

### 0.3 The two hypotheses the formalisation is conditional on

The chain `Lemma 5.1 → Corollary 5.2` uses three external facts and nothing
else beyond Theorem 3.2 (which is self-contained combinatorics) and
`pw(G) ≤ |X| + pw(G − X)` (which is `pathwidth_le_pathwidth_induce_add_card_compl`
in `TreeBound.lean`):

- **(H1) the cubic base case.** For every connected cubic `G` on `N`
  vertices, `pw(G) ≤ N/6 − 1/6 + τ(N) + O(log N)`, `τ` increasing,
  `τ(N) = o(N)`. Source: Fomin & Høie Theorem 5 (for *every* graph of maximum
  degree 3, so a fortiori connected cubic). **The paper gives no constants**:
  `τ` is "a function with `τ(n) = o(n)`" and the `O(log n)` is unspecified.
  The brief's "with the constants as the paper gives them via Fomin–Høie"
  cannot be met because there are none; the plan therefore parameterises the
  hypothesis by an arbitrary monotone budget `τ : ℕ → ℚ`:

      CubicPathwidthBound τ := ∀ V (G : SimpleGraph V), G.Connected → (∀ v, G.degree v = 3) →
                               (pathwidth G : ℚ) ≤ |V|/6 − 1/6 + τ |V|

  and everything downstream is stated with `τ` explicit. Fomin–Høie's own
  explicit form, read off their Theorem 5, is `τ_FH(N) = min{εN : N > (8/ε) ln(1/ε)(1 + 1/ε²)} + 1/6`:
  `n_ε = 55, 389, 1,674, 18,605` at `ε = 0.5, 0.3, 0.2, 0.1` (ten-second
  check), so at every size on our record (`N ≤ 2,916`) the explicit budget
  exceeds `0.2 N` and the hypothesis with that budget says nothing a graph
  could violate. Items 01–02 therefore also **measure** the budget the
  record needs: the smallest `c` with `pw ≤ N/6 − 1/6 + c` on every cubic
  graph to 16 vertices (all of them, `nauty-geng -d3 -D3`) and on the 42
  certified cubic graphs of the dataset (`N` up to 120).
- **(H3) the reduction lemma.** `pw(H) ≤ pw(r(H)) + O(log |V(H)|)` for every
  `H`, attributed to Kneis, Mölle, Richter & Rossmanith [21] (SIAM J.
  Discrete Math. 23(1):407–427, 2009, DOI 10.1137/080715482), which **is not
  held** (closed; abstract only, `literature/MISSING.md`, and the second
  literature pass could find no open copy). With `r(H)` empty it contains "a
  series-parallel graph has pathwidth `O(log n)`", which is what the basic
  graphs of the second kind need. One named Prop covers both uses:

      ReductionPathwidthBound ρ := ∀ V (G H : SimpleGraph V), SPReduces G H →
                                   (pathwidth G : ℚ) ≤ pathwidth H + ρ |V|

  with `SPReduces` the reflexive–transitive closure of the four operations
  (on `SimpleGraph V`, a removed vertex being isolated; §0.5). The brief's
  item (iii) asked for "pathwidth of the simple kind ≤ a small constant":
  **that is false** — series-parallel graphs include all trees, whose
  pathwidth is `Θ(log n)` (`TreeBound.lean`: the complete ternary tree of
  height `h` has pathwidth `h`), and the paper itself says `O(log n)`. What
  is cheap and unconditional is the per-step statement
  `pw(H) ≤ pw(H') + 1` for one operation `H → H'` (a bag of size at most
  three inserted beside the bag holding the neighbours), which does **not**
  iterate to `O(log n)` and is not what the proof needs. Proving (H3) in
  Lean means proving the series-parallel pathwidth bound (a balanced
  decomposition-tree or separator argument, with `tree_pathwidth_le_log`
  as its tree case) and the gluing of series-parallel pieces into a
  decomposition of `r(H)`; that is a loop of its own, and this plan does not
  attempt it. It is a named Prop here, quoted from the paper, exactly as
  `EdgeSearchMonotonicity` is in `Complex/EdgeSearch.lean`.
- **The averaging lemma behind Theorem 5.3** (`f_α(r(G)) ≤ g_α(d) n` for
  connected `G` or `d ≥ 5`), attributed to Edwards & Farr 2012 (EJC 19(2)
  #P25, open access) and not proved in this paper. Verified numerically in
  item 01; not formalised.

**What is then a theorem in Lean, conditional on (H1) and (H3) only:**

    pathwidth_le_potential_of_hypotheses :
      CubicPathwidthBound τ → ReductionPathwidthBound ρ → Monotone τ → Monotone ρ →
      ∀ G with every degree 0 or ≥ 3,
        (pathwidth G : ℚ) ≤ fminus G + τ n + 2 ρ n + 1

    pathwidth_le_degreeSum_of_hypotheses :
      … → ∀ G, (pathwidth G : ℚ) ≤ Σ_v g (degree_{r G} v) + τ n + 3 ρ n + 1
          and, since reduction never raises a surviving degree and g is monotone,
          ≤ Σ_v g (degree_G v) + τ n + 3 ρ n + 1          (g 0 = g 1 = g 2 = 0)

where the lower-order term is **explicit in the budgets**: `τ(n)` once (the
cubic base case, applied to a component of at most `n` vertices with `τ`
monotone), `ρ(n)` twice in Lemma 5.1 (once for `G − X →* B`, once inside a
basic component of the second kind, `C − v →* ∅`) and a third time for
`G →* r(G)` in Corollary 5.2, and `+1` for the vertex `v` of a second-kind
component (`f⁻ ≥ 5/6` there, so the paper's `O(log n)` absorbs it; the
explicit form keeps it). The paper's `τ(n) + O(log n)` is this with
`ρ = O(log n)`.

### 0.4 Where the paper and the repository correct the brief

1. **The base case is not "connected cubic ⇒ `pw ≤ N/6 + c₁ log N + c₂`".**
   Quoted in full above: it is "a 3-regular graph … has pathwidth at most
   `(1/6 + o(1)) n + O(log n)`", restated as `n/6 − 1/6 + τ(n) + O(log n)`
   with `τ = o(n)` unspecified; Fomin–Høie's Theorem 5 is for every graph of
   maximum degree 3 and gives `n_ε`, not `c₁, c₂`. The named hypothesis is
   parameterised by a budget function; the record is used to *measure* the
   budget at small sizes, never to fix it.
2. **"The simple kind has pathwidth ≤ a small constant" is false**; it is
   `O(log n)` (trees), and that is the paper's own log term. §0.3.
3. **Fomin–Høie's transfer is one bisection, not a recursion**, and a
   recursive bisection summed down the levels would give `n/3`, not `n/6`
   (each level's Monien–Preis cut is `(1/6 + ε)` of the current piece, and
   `Σ_i (n/2^i)/6 = n/3`). The general cut lemma the brief's item (v)
   describes is true, reusable and independent of the hypotheses, and item
   04 proves it with its iterated corollary; but it must not be presented as
   "how Fomin–Høie reach `n/6`" — that needs Lemma 4 (degree 3 only, with
   the tree term) and the boundary sweep, both quoted above and neither
   attempted here beyond a reserve option.
4. **No finite graph can violate Corollary 5.2 as stated**, because its
   lower-order term is an unspecified `o(n) + O(log n)`; with Fomin–Høie's
   explicit `n_ε` the budget is vacuous below `n ≈ 10⁴`. The brief's kill
   ("a single violation on a proved graph means our reading is wrong") is
   kept where it is falsifiable: on the **deterministic intermediate
   statements** (Theorem 3.2's inequality through Algorithm X, the
   `j`-inequality, the commutation of deletion with reduction, the cut
   lemma, the degree monotonicity of reduction) checked on every graph to 9
   vertices, and on the main-term deficit `pw − Σ_{r(G)} g`, whose
   distribution is reported with the budget it would need.
5. **Kneis et al. 2009 is not held and not obtainable** (closed; the second
   pass checked Unpaywall, Semantic Scholar, CORE). Lemma 3.1's confluence
   appeal and the `pw(G − X) = pw(r(G − X)) + O(log n)` step both cite it.
   The plan avoids the confluence appeal (§0.5: deletion commutes with
   reduction locally, which is all the induction needs) and names the
   pathwidth step as (H3).
6. **Corollary 5.2's displayed "`=`" is a "`≤`"** (already noted in the
   second pass): the sum over `r(G)` is at most the sum over `G`'s own degree
   histogram because no operation raises a surviving vertex's degree and `g`
   is non-decreasing; the paper's `n_d` on that line is not defined. Both
   forms are computed in item 01 and the gap between them reported.
7. **Theorem 5.3 is not self-contained** (the averaging lemma is Edwards &
   Farr's); it is verified on the record and stated in the report as
   "verified numerically; not formalised".
8. **Mathlib has no series-parallel graphs and no minors** (checked:
   `grep` over `Mathlib/Combinatorics` finds neither; it has
   `SimpleGraph.degree` and `sum_degrees_eq_twice_card_edges`). The
   reduction system is therefore defined from scratch on `SimpleGraph V`
   (§0.5), and "series-parallel" never appears in Lean except as
   "`SPReduces H ⊥`".
9. **The repository's tools cover the graph side already**:
   `pathwidth_le_pathwidth_erase_add_one`, `pathwidth_le_pathwidth_induce_add_card_compl`
   (both needed), `pathwidth_induce_union_le_max` and
   `pathwidth_induce_le_of_forall_connected` (the max over components),
   `pathwidth_eq_of_iso`, `pathwidth_mono` (`Minor.lean`),
   `PathDecomposition.extend` / `cat` / `glue` (`TreeBound.lean`; the cut
   lemma is `extend` on each side and `cat` with a middle bag),
   `tree_pathwidth_le_log` (the tree case of Fomin–Høie's Lemma 4, should
   the reserve take it). `treewidth` exists in `Sandwich.lean` but is not
   needed.
10. **The data are richer than the brief lists**: the dataset holds 16,636
    certified classes (not 16,635; `provenance` field; `n` up to 2,916; the
    MOSP corpus's 3,705 distinct graphs are among them, plus Rome 11,199,
    freetdi, PACE, VSPLIB, TreewidthLIB), of which **42 are cubic** (`N` = 4
    to 120) — the only direct data on (H1) above 16 vertices; the pilot has
    6,542 proved graphs (`status ∈ {refutation, bound, minor}`; 173 `upper`
    rows are unproved and are used only through their `lower` column); the
    ensembles hold 50,716 certified covers whose MOSP graphs have
    `pw = optimum − 1`.

### 0.5 The Lean design (the decisions a session should not have to make)

- **Graphs live on one vertex type.** Every graph in the induction is a
  `SimpleGraph V` on the same `V`; "deleting" a vertex isolates it
  (`Minor.lean`'s `isolate`), and the series-parallel operations are:
  (1)/(2) isolate a vertex of degree ≤ 1; (3) for `v` of degree 2 with
  non-adjacent neighbours `x, y`: isolate `v` and add the edge `xy`; (4) for
  `v` of degree 2 with adjacent neighbours: isolate `v`. `SPStep H H'` is
  the one-step relation, `SPReduces` its `Relation.ReflTransGen`,
  `IsSPReduced H` is "every vertex has degree 0 or ≥ 3", `IsBasic H` is
  "every component of the support is cubic, or has a vertex `v` with
  `SPReduces (H.isolate v) ⊥`" (`⊥` = edgeless; "empty" in the paper).
  Isolated vertices are the removed ones; with `g 0 = g 1 = g 2 = 0` and
  `g' d = 0` for `d ≤ 2` they contribute nothing to `f` and `f⁻`, and the
  pathwidth of a graph with isolated vertices is that of its support.
- **No `r(·)` as a function and no confluence.** Theorem 3.2 is stated as:
  for every `G` with every degree 0 or ≥ 3 there are `X : Finset V` inside
  the support and `B` with `SPReduces (G.deleteVerts X) B`, `B ≠ ⊥`,
  `IsSPReduced B`, `IsBasic B`, and `|X| + fminus B ≤ fminus G`. The
  inductive step produces `X = X* ∪ {w}` from `SPReduces (G − w) G*` and the
  induction hypothesis on `G*`, through the **commutation lemma**: if
  `SPStep H H'` acts at `v` and `w ≠ v`, then `SPReduces (H − w) (H' − w)` in
  zero or one step (an operation on `v` may change type after `w`'s
  deletion — a suppression becomes a degree-1 deletion if `w` was one of
  the neighbours — or vanish — if `v` was already isolated by `w`'s
  removal). Lifted to sequences and to finsets by induction, it gives
  `SPReduces (G − w − X*) (G* − X*)`, which is what the paper gets from
  Lemma 3.1. This replaces the appeal to [21]'s confluence theorem by a
  local case analysis that item 02 checks on every graph to 9 vertices
  first.
- **The potential is the paper's `f⁻`, per component** (additive, as the
  disconnected case of Theorem 3.2 needs). `fminus H = f H − Σ_{C : H.ConnectedComponent} g' (minDeg H C)`
  with `minDeg` the `Finset.inf'` of the degree over `C.supp` (singleton
  components of isolated vertices contribute `g' 0 = 0`). A global-minimum
  variant `F H = f H − g' (δ H)` was considered and rejected for Theorem 3.2
  (it is not additive; the disconnected case loses up to `(k − 1)/6`), though
  it would do for the pathwidth assembly alone; the session should not
  re-litigate this.
- **The arithmetic is in `ℚ`.** `g : ℕ → ℚ` by well-founded recursion on
  `n` (values at 0, 1, 2 are 0; at 3 is `1/6`), `g' n = g n − g (n − 1)`;
  `norm_num` and `decide` on the finite table; the inductions of Lemmas
  8.3–8.4 as stated in the paper (the coupled invariant
  `g(n − 1) ≤ g(n) ≤ (1 + g(n − 1))/2`, the recurrence
  `n g'(n) = (n − 3) g'(n − 1) + g'(n − 2)` for `n ≥ 5` and the sandwich
  `g'(n − 1) ≥ g'(n) ≥ g'(n − 1)/3`). Only `α = 1/6` is formalised; `g_α` for
  general `α` is not needed and would double the work.
- **Named Props, no `sorry`, no `axiom`**, `allowed_sorries.txt` empty; every
  new theorem in `paper1/axiom_check.lean`; the numerical pin in
  `learning/sandwich.py` (`--stage degree_bound`: `g` transcribed from Lean
  against the Python `g`; `fminus` on 500 random graphs against
  `learning/edwards_mcdermid.py`).
- **Files**: `lean/MOSPFormalization/DegreeBound/Weights.lean` (item 03),
  `DegreeBound/CutLemma.lean` (04), `DegreeBound/Potential.lean` (05),
  `DegreeBound/SPReduction.lean` (06), `DegreeBound/Step.lean` (07),
  `DegreeBound/ReductionTheorem.lean` (08), `DegreeBound/Pathwidth.lean`
  (09), each imported by `lean/MOSPFormalization.lean` (the gate checks
  this), none editing an existing proof.

### What the planner computed before writing the items (ten seconds of Python; to be replaced by item 01's numbers, never quoted)

The recurrence, the closed form (Lemma 8.1), properties 3–6, the Poisson
values `0.1826, 0.4575, 0.6558` at `c = 3, 6, 10`, `g(c) = 0.1667, 0.5111,
0.6846` (Theorem 5.3's main term at the mean degree), `1 − 3.5/(c + 1) =
0.125, 0.5, 0.682`, Fomin–Høie's `n_ε` values, and the floor `f⁻ ≥ 5/6` on
second-kind basic graphs (`g(4) + 4 g(3) − g'(3)`) were all confirmed. The
dataset has 16,636 certified classes with 42 cubic graphs; the pilot has
6,542 proved rows.

## 1. The questions and their items

Verification first, the exact statement second, Lean in order of reach with
the independent cut lemma early, the write-up last, one reserve. Eleven
items, one session each, in `Ralph_Loops/loop0012/iterations.md` with the
seven fields (question, method, deliverable, regenerate, kill criterion, size
range, does not claim).

| # | item | depends on | what it settles |
|---|---|---|---|
| 01 | Fetch the manuscript; verify Corollary 5.2 and Theorem 5.3 on every graph with a proved pathwidth (A) | — | the per-graph deficit `pw − Σ_{r(G)} g`, the reduced vs unreduced main terms, the Poisson check at `n = 60–120`, the budget the record needs; (H1)'s constants measured on the cubic data |
| 02 | The exact statement to formalise, with every intermediate lemma brute-force checked on every graph to 9 vertices (B) | 01 | the Lean-ready statements of §0.3–0.5, confirmed or corrected; (H3)'s gap `pw(H) − pw(r(H))` measured to 9 vertices |
| 03 | Lean (i): `g`, `g'` and their lemmas | 02 | `Weights.lean`; the sandwich pin |
| 04 | Lean (v): the cut lemma and its iterated form (independent of the hypotheses) | 02 | `CutLemma.lean`; what Fomin–Høie's one-level argument adds, stated and not proved |
| 05 | Lean (ii): the potential and the one-deletion degree accounting | 03 | `Potential.lean`: `f (G − w) = f G − g (deg w) − Σ_{v ~ w} g' (deg v)` and the `≤ f G − 1` consequence |
| 06 | Lean (iii): the reduction system, basic graphs, degree monotonicity, and deletion–reduction commutation | 03 | `SPReduction.lean`; the local lemma that replaces Lemma 3.1 |
| 07 | Lean (iv-a): the connected non-basic step, `1 + f⁻(G*) ≤ f⁻(G)` | 05, 06 | `Step.lean`: the `j`-inequality in all its cases |
| 08 | Lean (iv-b): Theorem 3.2 by induction (components, the step, `X` assembled) | 07 | `ReductionTheorem.lean` |
| 09 | Lean (iv-c, vi): the pathwidth assembly under the named hypotheses; Corollary 5.2's form; axiom check; sandwich stage | 04, 08 | `Pathwidth.lean`; `#print axioms`; the Appendix A rows |
| 10 | Write-up (D): `reports/edwards_mcdermid.md` §0, the paper's paragraph, the survey's §1.4 sentence, the `CLAUDE.md` paragraph drafted | 01–09 | one document, every number with its size range and regenerate command |
| 11 | Reserve: the best remaining gap | 10 | see the item |

Items 03 and 04 are independent of each other and of 05–06; 05 and 06 are
independent of each other; the driver runs them in listed order, and a
blocked item (`- [!]`) must be visible to its dependants: 07 depends on 05
and 06 being `[x]`, 08 on 07, 09 on 04 and 08. If an item is blocked, its
dependants state the named Prop that stands in for it and proceed with what
is independent.

## 2. Budget

Modelled on loop0010 (13 items, 13 sessions, 10.5 h wall, $176) and loop0011
(13 items planned at ≈ 14 h, $230; its sessions ran 7–115 minutes and $9–35
each, the Lean item at 1.5 h and $35). Compute is small: no pathwidth is
solved except by the subset DP on graphs of at most 16 vertices (all graphs
to 9 by `nauty-geng`, cubic graphs to 16), and the per-graph bound is a
degree histogram.

| item | sessions | wall-clock | dollars | compute (core-hours, nice 19, ≤ 8 workers) |
|---|---|---|---|---|
| 01 fetch and verify | 1 | 1.5 h | 20 | ≤ 1 (reduction + histogram on ~74,000 graphs; cubic DP to 16) |
| 02 exact statement, brute-force checks | 1 | 1.5 h | 25 | ≤ 2 (all graphs to 9 vertices, several checks each) |
| 03 Lean: weights | 1 | 1.5 h | 25 | 0 (lake build) |
| 04 Lean: cut lemma | 1 | 1.5 h | 25 | 0 |
| 05 Lean: potential, deletion accounting | 1 | 1.5 h | 25 | 0 |
| 06 Lean: reduction system, commutation | 1 | 2 h | 35 | 0 |
| 07 Lean: the step inequality | 1 | 2 h | 35 | 0 |
| 08 Lean: Theorem 3.2 | 1 | 2 h | 35 | 0 |
| 09 Lean: pathwidth assembly, axioms | 1 | 1.5 h | 25 | 0 |
| 10 write-up | 1 | 1 h | 20 | 0 |
| 11 reserve | 1 | 1 h | 20 | ≤ 1 |
| **total** | **11–12** | **≈ 17 h** | **≈ $290** | **≤ 4** |

Per-session cap 4 h (`knobs.json`, unchanged from loop0011), fix cap 45 min,
three fix attempts, 16 iterations at most; the gate (lake build, two pytest
suites, the paper's `make check`) takes about 10 minutes and runs once per
item. The estimate is above loop0011's because six of the eleven items are
Lean; the two most uncertain (06, 07) carry 2 h each.

## 3. Risks

1. **The degree accounting after deletion (items 05, 07) is the hard part
   of the paper, and it looks it.** On paper, (3)–(4) are a re-indexing of
   one `Finset.sum` (neighbours of `w` lose one degree, nobody else changes)
   plus property 6; in Lean that is a sum over `univ` split into `N(w)`,
   `{w}` and the rest, with `degree (G.isolate w) v = degree G v − 1` for
   `v ∈ N(w)` — routine but long. The step inequality (item 07) is where
   the paper spends three pages of cases: regular `G`; a surviving vertex of
   degree between 3 and `δ(G)`; `δ(G) = 3` with every degree-3 vertex next to
   `w` and `d(v_Δ) > 3`; all neighbours of degree 3 and reduced away. Each
   case needs facts about `G*` that come from item 06 (no degree rises under
   reduction; a reduced-away vertex loses its whole `g`; `G* ≠ ⊥`); the
   `j_4 ≥ g'(d)` lemma is the hinge. Item 02's brute-force check of the
   inequality for the paper's choice of `w` — and the measurement of whether
   it also holds for *every* max-degree `w`, which would let Lean pick `w`
   by `Finset.exists_max_image` without the secondary tie-break — is what
   makes 07 feasible in one session. If 07 does not fit, it proves the
   non-regular cases and leaves the regular case as a stated lemma that 08
   takes as a hypothesis; 10 says so.
2. **The series-parallel side cannot be proved here, and the brief expected
   it could.** §0.3–0.4: the "simple kind" has pathwidth `Θ(log n)`, the
   reduction lemma is Kneis et al.'s and the paper is not held, and Mathlib
   has no series-parallel graphs. The loop's Lean theorem is honest about it
   — conditional on `ReductionPathwidthBound ρ` as well as on the cubic base
   case, with both quoted. What *is* proved on that side: the reduction
   system with its termination, degree monotonicity, the commutation lemma,
   and (item 02) the measured gap `pw(H) − pw(r(H))` on every graph to 9
   vertices, which is a check of (H3)'s shape (it should be at most 2 there)
   and not of its constant.
3. **The commutation lemma (item 06) may have a case the paper never
   wrote**, since the paper cites confluence from [21] instead. The cases:
   `w` not adjacent to `v` (the step repeats verbatim); `w` a neighbour of a
   degree-2 `v` (suppression or triangle deletion becomes a degree-1
   deletion); `w` the only neighbour of a degree-1 `v` (the step becomes an
   isolated-vertex deletion); `w = x` or `y` in operation 3 (the added edge
   `xy` disappears with `w`, and `v` has degree 1 in `H − w`: one step of
   type 2 reaches `H' − w`). Item 02 enumerates every (graph, step, `w`)
   to 8 vertices before item 06 states it; a counterexample there would
   change the formalisation's route back to a confluence proof (Newman's
   lemma over the four operations), a session the budget does not hold.

Two smaller ones: the per-component potential needs `ConnectedComponent` as
a `Fintype` with `Finset.sum` over it and a split lemma for a graph that is a
disjoint union — `TreeBound.lean`'s `reachSet` pattern (walks avoiding a set)
is the proven route and item 08 is told to use it rather than Mathlib's
quotient where the two differ; and the dataset's largest graphs (`n` to
2,916) make the brute-force reduction in Python a loop over `n` steps with
degree updates, which is fine, but a naive "recompute degrees each step"
would be quadratic — item 01 is told to use a bucket queue.

## 4. What would count as success

The bound evaluated, with the lower-order terms spelled out and their
vacuity at our sizes stated, on every graph with a proved pathwidth (zero
deficits above the stated budget, the deficit distribution per source and
per `n`, the Poisson check at `n = 60–120`, Theorem 5.3's form on the
connected graphs and on `d̄ ≥ 5`); (H1)'s constant measured on every cubic
graph to 16 vertices and on the 42 certified cubic graphs; every deterministic
statement in the chain checked on every graph to 9 vertices before it is
stated; `g` and its five lemmas, the cut lemma and its iterated form, the
potential's deletion accounting, the reduction system with the commutation
lemma, the step inequality, Theorem 3.2 and the pathwidth assembly in Lean
with no `sorry`, standard axioms, and the two external inputs as named Props
quoted from their sources; and a report that says plainly "this is a
formalisation of a published theorem, conditional on two cited results", with
the paper's paragraph, the survey's sentence and the `CLAUDE.md` paragraph
drafted. The plan does not promise the series-parallel lemma or Fomin–Høie's
Lemma 4 in Lean; it promises to say exactly what is proved, what is cited,
and what the record says about each.
