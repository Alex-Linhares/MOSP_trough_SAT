# loop0011 — counting events, not witnesses: the separator first moment: items

The proved first-moment lower bound on pathwidth counts *empty pairs*
`(A, R)` at exact sizes `|A| = t = ⌈(n − k)/2⌉`, `|R| = N − t`, `N = n − k`
(`FirstMoment.lean`, `CliqueCoverMoment.lean`), and its constant `β*` sits
`0.08–0.10` below the measured slopes on `G(n, c/n)` at `c = 3–10` and
`0.04–0.10` below the certified slopes on random covers
(`reports/separator_moment_plan.md` §0). loop0010 item 08 showed the slack is
the union bound over clustered pairs (`reports/excess_phase_diagram.md` §8.5)
and that naming more vertices cannot help (§8.6 (2)). This loop counts the
*event* instead: a `k`-set `S` whose removal leaves a balanced empty
bipartition, once per `S`, with the inner probability from the component
structure of `G − S`; and two further representatives on the same ladder,
the closed pair (`S = N(A) ∩ N(R)`) and the weighted count
`Y = Σ_P 1[P empty] / Z(P)`. The planner's estimates (plan §0; never quoted
as results) say the gain at `c = 6–10` is `+0.004–0.010` in `β`, that the
bracket at `c = 3` is `[0.009, 0.056]` against a slope of `0.099`, and that the
method's threshold moves from `4 ln 2` to `2 ln 2` if the giant's lower tail
is exponentially small. Items 03–04 decide which representative is right
before items 05–07 compute constants.

Phase 1 (01–04) reads and de-risks; phase 2 (05–07) computes; 08 proves on
paper; 09 is the branch; 10 is Lean; 11 is the ledger; 12 writes; 13 is the
reserve. Every item: one session, `nice -n 19`, at most 8 workers (4 if the
one-minute load in `uptime` is above 24), nothing solved twice, every new
layout persisted under `reports/scratch/separator_moment/<item>/`.

- [x] **01 Literature: who counts separators, and what the inner probability is known to be.**
  - **Question.** G of the brief. Has anyone counted balanced *vertex*
    separators (or bisections, or cuts) of sparse random graphs with an
    inner probability finer than the product over edges, for pathwidth or
    any width or cut parameter? What is the large-deviation rate for the
    giant component's lower tail and for the cluster sizes of `G(N, c/N)`?
    Did a representative or locally-optimal count ever move a first-moment
    cut constant, and by how much?
  - **Method.** (a) Read in full the held papers (`literature/`):
    `2022-Diaz-Diner-Serna-Serra-Vertex-Bisection-Width-Random-Regular-Graphs`
    (the vertex-cut cousin: what inner probability, what gain over the
    product bound), `2023-Lichev-Mitsche-Minimum-Bisection-Random-3-Regular-Graphs`,
    `2017-Coja-Oghlan-Cooley-Kang-Skubch-Minimum-Bisection-Planted-Bisection-Model`,
    `2014-Perarnau-Serra-Tree-Depth-Random-Graphs` (their triple count, p. 5–6),
    `2012-Lee-Lee-Oum` (not a first moment; the `c > 1` truth), `2024-Do-Erde-Kang`,
    `2004-Bezrukov-Elsasser-Monien-Preis-Tillich-Spectral-Lower-Bounds-Bisection-Width`,
    `2008-Feige-Hajiaghayi-Lee` (vertex separators, for the vocabulary),
    `2007-Behrisch-Component-Evolution-Random-Intersection-Graphs` and
    `2008-Lageras-Lindholm-Component-Structure-Random-Intersection-Graphs`
    (the component law item 07 needs), `2001-Diaz-Petit-Serna-Trevisan`,
    `reports/scratch/first_moment/lit/turner1986.txt`. (b) Fetch what is
    open and not held, into `literature/` with the repository's naming:
    Dembo, Montanari & Sen 2017, *Extremal cuts of sparse random graphs*
    (arXiv 1503.03923; the bisection constant via the Parisi formula);
    Andreis, König & Patterson 2021, *A large-deviations principle for all
    the cluster sizes of a sparse Erdős–Rényi graph* (arXiv; RSA);
    O'Connell 1998, *Some large deviation results for sparse random graphs*
    (PTRF 110; try the author's page / Semantic Scholar; if paywalled,
    record "not held" and cite only through AKP's restatement);
    Puhalskii 2005 (*Stochastic processes and their applications*, the LDP
    for the giant); Díaz, Serna & Wormald 2007, *Bounds on the bisection
    width for random d-regular graphs* (TCS 382); Kolesnik & Wormald 2014,
    *Lower bounds for the isoperimetric numbers of random regular graphs*
    (SIDMA; arXiv 1109.0689); Luczak & McDiarmid 2001, *Bisecting sparse
    random graphs* (RSA 18); Bollobás 1988, *The isoperimetric number of
    random regular graphs* (EJC 9). Kloks 1994 is held as a two-page
    preview only: say "as restated by Gao / Perarnau–Serra" or obtain
    chapter 12 of LNCS 842; do not assert his inner probability from
    memory. Extract text with `pdftotext` into
    `reports/scratch/separator_moment/lit/`; execute nothing from a
    download. (c) Write `reports/separator_moment.md` §1 with three
    tables: *who counts what* (object counted; inner probability — product
    over edges, exact component law, configuration-model exact; parameter;
    random model; the constant obtained; page); *the rates* (the giant's
    lower tail: statement, rate function, hypotheses, which paper, page;
    the cluster-size LDP likewise; whether either gives, as a corollary,
    `P(G(N, c'/N)` has no component larger than `N/2) ≤ e^{−I N}` with `I > 0`
    for every `c' > 2 ln 2`, with the exact statement quoted); *the
    representative counts* (Díaz–Serna–Wormald's locally optimal
    bisections, Kolesnik–Wormald's method: what they merge, the gain in the
    constant, in their units and converted to a fraction of the gap to the
    truth where a truth is known). (d) One paragraph answering the brief's
    question in the brief's terms: "the new idea is a better estimate of
    the inner probability, not a new object" — is that so, or does someone
    already have the exact inner probability for a cut-type first moment?
  - **Deliverable.** `reports/separator_moment.md` created, with the
    document's header (what the loop is, the three events, the notation
    `t, N, S, A, R`, `q(x) = 1 − e^{−cx}`) and §1; the fetched PDFs; a
    `literature/MISSING.md` entry for anything not obtained; the DOIs
    checked by `paper1/latex/check_refs.py` conventions for later
    citation.
  - **Regenerate.** None (reading). The text extracts are regenerated by
    `pdftotext` from the PDFs.
  - **Kill criterion.** None. One stop rule: if a held or fetched paper
    already states the separator first moment for pathwidth or vertex
    separation of `G(n, c/n)` with an exact inner probability and a
    constant, record it at the top of §1 and tell items 05–06 to compare
    against it rather than re-derive; that is the most useful possible
    outcome of this item.
  - **Size range.** Not applicable.
  - **Does not claim.** Priority for anything; "we found no prior
    statement" is the strongest wording allowed, and only after (a) and
    (b) were done.

- [x] **02 The deterministic lemmas: balanced separator, its relaxation, the closed pair.**
  - **Question.** A of the brief. Exactly which structures does
    `pw(G) ≤ k < n` force, in a form a first moment can count once per
    separator?
  - **Method.** State, on paper in `reports/separator_moment.md` §2, in the
    style of `reports/random_graph_first_moment.md` (numbered lemmas, every
    step named): **L1 (balanced separator, exact sizes).** With
    `N = n − k`, `t = ⌈N/2⌉`: there are pairwise disjoint `A, R, S` with
    `A ∪ R ∪ S = V`, `|A| = t`, `|R| = N − t`, `|S| = k`, and no edge
    between `A` and `R`. Proof: `exists_empty_pair_of_layout` at the prefix
    of size `t` gives `A` and an inactive suffix `R₀` with
    `|R₀| ≥ n − t − k = N − t` (`card_inactiveSuffix`); take `R ⊆ R₀` of size
    `N − t` and `S = V ∖ (A ∪ R)`. **L1′ (the relaxation).** Hence a `k`-set
    `S` such that every component of `G − S` has at most `t` vertices, and
    such that the components can be grouped into two classes of sizes `t`
    and `N − t` (the bipartition event `E_bip`); L1′ without the grouping is
    the event `E_rel`; `E_bip ⊆ E_rel` strictly (give a 6-vertex example).
    **L2 (the closed pair).** From any empty pair `(A, R)` with `|A| ≥ t`,
    `|R| ≥ N − t` and `|V ∖ (A ∪ R)| ≤ k`, the alternating closure
    `R₁ = V ∖ N[A]`, `A₁ = V ∖ N[R₁]`, `R₂ = V ∖ N[A₁]`, … is monotone
    (`A ⊆ A₁ ⊆ A₂ …`, `R ⊆ R₁ ⊆ …`; prove the two inclusions) and stops at
    a pair `(A*, R*)` with `A* = V ∖ N[R*]`, `R* = V ∖ N[A*]`, i.e.
    `S* = N(A*) ∩ N(R*)`, no `A*–R*` edge, sides at least the forced sizes,
    `|S*| ≤ k`. Note that the fixpoint may depend on which side is closed
    first (the count does not need uniqueness; say so). **L3 (the MOSP
    forms).** L1 and L2 on `mospGraph`: `S` is a set of customers; a pair
    is empty iff no pattern meets both sides (`isEmptyPair_coverGraph_iff`);
    `S* = N(A*) ∩ N(R*)` reads "every customer of `S*` shares a pattern with
    `A*` and one with `R*`". **Before any is called a lemma**, check all
    three by brute force: every graph on 1–9 vertices from `nauty-geng`
    (288,266 to 9; the pattern of `reports/scratch/empty_pair/check.py`,
    pathwidth by the subset DP), 20,000 random graphs at 10–12 and 2,000
    random covers at `n ≤ 10` (`benchmarks.generator.generate_structured_instance`,
    pathwidth of the MOSP graph by the DP): for `k = pw(G)` the structures
    of L1, L1′ and L2 exist (report the counts of each); for `k = pw − 1`
    report how often each still exists (the necessary condition's slack at
    these sizes; L1′ will hold more often than L1 — record the share);
    the closure's monotonicity asserted at every step. 8 workers, about
    0.5 core-hours. Script and log in `reports/scratch/separator_moment/02_lemmas/`.
  - **Deliverable.** §2 of the report with the three statements, proofs
    and the check's table; `reports/scratch/separator_moment/02_lemmas/{check.py, check.log}`;
    the Lean-ready statements listed for item 10 (names, hypotheses,
    conclusions, which existing lemma each rests on).
  - **Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/02_lemmas/check.py --max-n 9 --workers 8`.
  - **Kill criterion.** A counterexample to L1, L1′ or L2 stops the item
    with the graph drawn and the statement withdrawn; it also stops the
    loop's premise, so write it at the top of PROGRESS.md.
  - **Size range.** Every graph to 9 vertices; samples to 12; covers to 10
    customers. The lemmas are for every graph.
  - **Does not claim.** Anything probabilistic; that the closed pair is
    canonical (it is a representative, not the representative).

- [x] **03 The clumping decomposed: pairs, separators, closed pairs and move-classes on instances with exact pathwidth.**
  - **Question.** B of the brief. On a graph of pathwidth `k`, how many
    exact-size empty pairs `X₁` are there, how many distinct separators
    `X₂` among them, how many closed pairs `X₃` (sides `≥` forced sizes,
    `|S| ≤ k`), and how many move-classes `X₄` (connected components of the
    graph on empty pairs where two pairs are adjacent if one vertex changed
    class or two vertices swapped classes)? How fast do `X₁/X₂`, `X₁/X₃`,
    `X₁/X₄` grow with `n`, in nats per vertex, against the `0.066` that a
    `0.02` gain in `β` needs at `c = 10` (plan §0)?
  - **Method.** (a) *Instances.* Fresh `G(n, c/n)` at `n ∈ {14, 16, 18, 20,
    22, 24}`, `c ∈ {4, 6, 8, 10}`, 200 per cell, seeds recorded; exact
    pathwidth by `learning.first_moment.vertex_separation_brute` (`n ≤ 16`)
    and by the C program `pathwidth_solver/cli/pathwidth -l -t 60` on
    graph6 (`networkx.to_graph6_bytes`; `n ≥ 18`), the layout kept in the
    CSV; the pilot's `n = 20` cells (137 proved each, layouts in
    `reports/scratch/gnp_pilot/results.csv`) as the overlap check at one
    size; and certified random covers from `learning/data/ensemble/results.csv`
    (`fixed`, `n ∈ {10, 15, 20, 25}` where present, `d ∈ {4, 6}`, `m = n`,
    regenerated from seed; `pw = optimum − 1`). No instance of the record
    is re-solved. (b) *Enumeration.* All exact-size empty pairs at `k = pw`:
    enumerate `t`-sets `A` with `|N[A]| ≤ n − (N − t)` by the pruned search
    of `satisfiability/expansion_bound.py::_f_exact` (adapted to list the
    sets rather than the minimum), then every `(N − t)`-subset `R` of
    `V ∖ N[A]`; `X₂` = distinct `V ∖ (A ∪ R)`; `X₃` by closing every pair
    and deduplicating, and independently by direct enumeration of closed
    pairs at `n ≤ 16`; `X₄` by union–find over the adjacency defined above.
    Also at `k = pw + 1` and `pw + 2` (the counts grow; the ratios are what
    matter) and `k = pw − 1` (`X₁` may be 0: report the share). (c) *Rates.*
    Per cell, the geometric mean and median of `X₁`, `X₁/X₂`, `X₁/X₃`,
    `X₁/X₄`; the slope of `log(geometric mean)` against `n` at fixed `c`
    with its standard error; the same on the covers against `n`. Beside
    them the second-moment prediction for `G(n, c/n)` at `β = pw/n` (the
    `3 × 3` overlap table of `learning.first_moment.second_moment_rate`
    rewritten for Bernoulli edges: a one-function addition
    `second_moment_rate_gnp(a, c)`, tested against enumeration at `n = 10`).
    (d) *The overlap distribution.* For 20 graphs per cell at `n = 20`,
    `c = 10`: the overlap table of every pair of empty pairs, histogrammed
    by `|A ∩ A'|/n`, `|A ∩ R'|/n`, `|A ∩ S'|/n` — is the extremal table of
    §8.5 (a) (sides exchanged with `S`) what instances show? About 3
    core-hours on 8 workers at nice 19; sample down and say so if the 4 h
    cap approaches.
  - **Deliverable.** `learning/separator_moment.py` begun
    (`enumerate_empty_pairs`, `separators_of`, `close_pair`, `closed_pairs`,
    `move_classes`, `second_moment_rate_gnp`) with `tests/test_separator_moment.py`
    (the enumeration against `empty_pair_count_brute` at `n ≤ 12`; closure
    idempotent and monotone; move-classes on a hand-built example; the
    Bernoulli second moment against enumeration); the instance CSV with
    seeds and layouts under `reports/scratch/separator_moment/03_clumping/`;
    `reports/separator_moment.md` §3 with the rate table and the overlap
    histogram (PNG, dataviz skill read first).
  - **Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/03_clumping/run.py --workers 8` (stages `solve`, `count`, `rates`, `overlap`).
  - **Kill criterion.** Pre-registered: if the slope of `log(X₁/X₂)` and of
    `log(X₁/X₃)` against `n` at `c = 10` is below `0.066` nats per vertex
    (twice the standard error), the separator and closed-pair counts are
    predicted to fail item 06's kill, and item 09 (the weighted count) is
    the route; record the prediction and keep items 05–06 (the prediction
    is at `k = pw` on typical instances, not in the large-deviation regime
    at `β*`, and only item 06 decides). If `X₁/X₄` grows at `≥ 0.15` nats
    per vertex while `X₁/X₃` does not, the clusters are fat and not
    closure classes — exactly §8.5's picture — and item 04 must measure
    them in the planted model.
  - **Size range.** `n = 14–24` for graphs (fresh), 20 (pilot), 10–25 for
    covers.
  - **Does not claim.** Anything asymptotic; `n ≤ 24` growth rates are the
    small-size end (CLAUDE.md, §14 of `reports/ml_nature.md`), reported
    with their standard errors and no extrapolation.

- [x] **04 The planted cluster: typical, or a rare-instance artefact of `E[X²]`?**
  - **Question.** Given one empty pair, how many other empty pairs of the
    forced sizes does the instance *typically* have, how far away are
    they, and by what mechanism? `E[X²]/E[X]² = e^{0.23 n}` at `(6, 1)`
    (§8.5 (a)) is `E[X′ | planted]`; if the median of `X′` under the planted
    measure grows at the same rate, the cluster is typical and a
    representative merging it would gain the whole `0.23`; if the median
    grows far slower, the second moment is carried by rare planted
    instances and the closed-pair count is near-tight for `P(X > 0)`.
  - **Method.** (a) *Planting.* `G(n, c/n)` with the edges between a fixed
    `A` (`|A| = t`) and `R` (`|R| = N − t`) deleted, at `n ∈ {16, 20, 24, 28,
    32}`, `c ∈ {6, 10}`, `β ∈ {β*(c), β*(c) + 0.1}` rounded to integer `k`,
    200 instances per cell; no pathwidth is computed (the planted pair makes
    `X ≥ 1` by construction; pathwidth is irrelevant here). The cover
    analogue at `(6, 1)`, `n ∈ {16, 20, 24, 28}`: patterns of size 6 drawn
    uniformly among those meeting at most one side. (b) *Counting.* All
    exact-size empty pairs by item 03's enumerator; `X′ = X − 1`; the
    overlap table of each with the planted pair; the closed pairs and
    move-classes as in item 03. (c) *The statistics.* Per cell: median,
    geometric mean and mean of `X′`; `log(mean)/n` against the
    second-moment prediction `log(E[X²]/E[X]²)/n` for the cell
    (`second_moment_rate_gnp` of item 03; `second_moment_rate` for the
    cover) — the means must agree within sampling error, as a check of the
    formula and the enumerator; `log(median)/n` with its growth in `n`; the
    share of `X′` within Hamming distance `εn` of the planted pair for
    `ε ∈ {0.05, 0.1, 0.2, 0.3}`; the share of far pairs that are reversed
    perturbations (`|A′ ∩ R| ≥ |A′ ∩ A|`). (d) *The mechanism.* For each
    far pair, which vertices moved from `S` into a side and how many
    neighbours they had on that side in the planted graph (the hypothesis:
    low-degree separator vertices recombined, their few neighbours
    evicted); the histogram of those degrees against the degree law of `S`
    vertices. About 3 core-hours on 8 workers at nice 19.
  - **Deliverable.** `reports/scratch/separator_moment/04_planted/{run.py, planted.csv, run.log}`;
    `reports/separator_moment.md` §4 with the table (median vs mean vs
    prediction per cell), the distance histogram and the mechanism
    paragraph; `learning/separator_moment.py` extended (`plant_pair`,
    `overlap_table`) with tests (planting leaves exactly the forbidden
    edges absent; the overlap table sums to `n`).
  - **Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/04_planted/run.py --workers 8`.
  - **Kill criterion.** Stated as a fork, not a kill: if `log(median X′)/n`
    at the largest `n` is within a factor 2 of `log(E[X′])/n`, the cluster
    is typical, and item 09 is the loop's main analytic route (the weighted
    count with a lower-tail estimate); if it is below a quarter of it, the
    cluster is a rare-instance artefact, item 09 is reduced to one
    paragraph, and item 12 must say that `P(X > 0)` is near the closed-pair
    first moment and the remaining gap to the slopes is not the union
    bound. In between, both are written up with the numbers.
  - **Size range.** `n = 16–32` planted graphs, `16–28` planted covers; the
    growth in `n` is reported and no limit is taken.
  - **Does not claim.** A value of `P(X > 0)`: the planted measure is
    `P(· | one pair empty)`, which weights instances by `X`, and the item
    says so in its first paragraph.

- [ ] **05 The inner probability, exactly: `P(G(N, p)` has a balanced empty bipartition`)`.**
  - **Question.** C of the brief. For a fixed `S`, `G − S` is `G(N, p)` with
    `N = n − k`; what is `P_N(E_bip)` exactly at small `N`, what is its
    exponential rate in `N`, and how much smaller is it than the product
    bound `C(N, t)(1 − p)^{t(N − t)}` the pair count uses?
  - **Method.** In `learning/separator_moment.py`: (a) `log_connected(N, p)`:
    Gilbert's recursion `C_1 = 1`, `C_j = 1 − Σ_{i<j} C(j−1, i−1) C_i (1−p)^{i(j−i)}`
    in `mpmath` at 60 digits (the subtraction cancels at small `p`), checked
    against enumeration of all labelled graphs at `j ≤ 6` and against
    `networkx` Monte Carlo at `j = 20`. (b) `log_prob_partition(λ, N, p)`:
    the probability that the component sizes are the multiset `λ ⊢ N`,
    `N!/(Π λ_i! Π_s m_s!) · Π C_{λ_i}(p) · (1−p)^{(N² − Σ λ_i²)/2}`, summed
    over all partitions to check it is 1 at `N ≤ 20`. (c) `log_prob_bip(N, p, t)`:
    the sum over partitions `λ` of `N` that admit a sub-multiset summing to
    exactly `t` (subset sum over the parts with a bitset), exact for
    `N ≤ 60` (966,467 partitions; `N = 80` has 15.8 M — do it only if `N = 60`
    takes under 10 minutes, else stop at the largest feasible `N` and say
    so); `log_prob_rel(N, p, M)`: the relaxed event "no component larger
    than `M`" by the `O(N²)` recursion over the component of the first
    vertex, to `N = 400`. Check `prob_bip ≤ prob_rel` everywhere and
    `prob_bip` against enumeration of labelled graphs at `N ≤ 7` and Monte
    Carlo at `N = 20`, `p = 0.1`. (d) *The comparison.* At `p = c/n` for
    `(n, c)` on the pilot grid (`n = 60, 120`; `c = 3, 4, 6, 8, 10`) and
    `k` from `0` to `n`: `log B_pair(n, k, p)` (the exact pair bound of
    `random_graph_first_moment.md` §5, `finite_bound.py`),
    `log B_sep = log C(n, k) + log_prob_bip(n − k, p, t)`, `log B_rel` with
    `prob_rel`; the largest `k` with each below `1` and below `0.01`; the
    ratio `(log B_pair − log B_sep)/n` per cell. Against the pilot: at
    `n = 60` the observed minimum pathwidth per cell; at `n = 120` the
    solver's lower bounds only (the graphs are unproved there; say so). (e)
    *The rate.* `−log_prob_bip(N, c′/N)/N` for `N = 20, 30, …, 60(80)` at
    `c′ ∈ {2, 3, 4, 5, 6.6, 8, 10}`; a linear fit in `N` with the intercept
    free, labelled "fitted"; beside it the two analytic routes of the plan
    (`c′/4 − ln 2`, the pair count's rate, a lower bound on the rate; and
    `min(c′/4, c′/2 − ln 2 + ln 2 · ln(2 ln 2/c′))`, an upper bound) — the
    fitted rate must lie in the bracket, or the computation is wrong.
    About 1 core-hour.
  - **Deliverable.** The four functions with tests; `reports/scratch/separator_moment/05_inner/{run.py, inner.csv, rates.csv, run.log}`;
    `reports/separator_moment.md` §5 with the finite table at the pilot
    cells (pair / separator / relaxed floors at `< 1` and `< 0.01`, the
    observed minima), the rate table, and the figure of `−log P/N` against
    `N` with the bracket (PNG, dataviz skill).
  - **Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/05_inner/run.py --max-N 60`.
  - **Kill criterion.** If at every pilot cell with `c ≥ 6` the separator
    floor at `< 0.01` exceeds the pair floor by at most one stack, the
    separator count is recorded as a rounding at these sizes (as the
    exact-size pair was in §8.6 (4)), and item 06 is told so; the rate
    comparison still runs.
  - **Size range.** Exact to `N = 60` (`80` if cheap); the relaxed event to
    `N = 400`; the finite table at `n = 60, 120`.
  - **Does not claim.** A limit: the rate is fitted on `N ≤ 60–80` and
    bracketed, not proved; the finite inequality is exact and is the
    only thing quoted as proved (after item 08).

- [ ] **06 `β_sep(c)` and `β_closed(c)`: the constants, against `β*(c)` and the slopes.**
  - **Question.** D of the brief. What constant does the separator first
    moment give, `H(β) + (1 − β)·log P_{N}(E_bip)/N → 0`, what does the
    closed-pair count give, what does their combination give, and how do
    they compare with `β*(c)` and with the fitted slopes at `c = 2–20`?
    Does the method's threshold move from `4 ln 2`?
  - **Method.** (a) `beta_sep(c)` from three rates: the fitted rate of item
    05 (labelled), the bracket's two ends (giving a bracket on `β_sep`),
    and, if item 01 found a usable statement, the literature rate for
    `E_rel` (O'Connell's lower tail of the giant; AKP's cluster-size LDP
    specialised) — each as its own column, with "fitted", "bracket",
    "cited (paper, theorem)" in the header. (b) `beta_closed(c)`: the root
    of `sup_{a, r ≥ (1−β)/2, s ≤ β} [H(a, r, s) − c a r + s ln q(a) + s ln q(r)]`,
    `q(x) = 1 − e^{−cx}` — derive the exponent from the closed-pair count
    of item 02 L2 (the `s` factors are the probabilities that each
    separator vertex sees both sides, independent given `A, R` for
    Bernoulli edges), check it against enumeration of closed pairs at
    `n ≤ 8` (the finite count: `Σ_{a,r,s} multinomial · (1−p)^{ar} · (1 − (1−p)^a)^s (1 − (1−p)^r)^s`),
    and the combined count (closed pairs grouped by `S`, inner probability
    from (a) with the closure factor) stated as the best valid first
    moment on the ladder. (c) The table at `c ∈ {2, 2.5, 3, 4, 6, 8, 10, 12,
    16, 20}`: `β*`, `β_closed`, `β_sep` (three columns), the combination,
    the fitted slope where the pilot has one (`0.040, 0.099, 0.158, 0.268,
    0.360, 0.415` at `c = 2, 3, 4, 6, 8, 10`, survey §7(d)); the exponent's
    slope at `β*` per cell (for the nats-to-`β` conversion). (d) The
    threshold: state as a proposition with its hypothesis explicit —
    *if* `P(G(N, c′/N)` has no component larger than `N/2) ≤ e^{−I(c′) N}`
    with `I(c′) > 0` for every `c′ > 2 ln 2` (the giant's lower tail), then
    `β_sep(c) > 0` for every `c > 2 ln 2`; give the status of the hypothesis
    from item 01 (cited with page, or "not verified"); note the pair
    count's `4 ln 2` and the truth `1`. Check numerically at `c = 1.5, 2,
    2.5` with item 05's exact `prob_rel` at `N ≤ 400`: is `−log P_N(E_rel)/N`
    bounded away from `0` there? (e) The finite form at `n = 60` and `120`
    for `c = 6, 10` beside the pilot (from item 05's table), restated in
    stacks.
  - **Deliverable.** `learning/separator_moment.py` extended (`beta_sep`,
    `beta_closed`, `closed_rate`, `combined_rate`) with tests (`β_closed ≥ β*`
    at every `c`; the closed exponent at `s = 0`… reduces to the pair
    exponent; the finite closed count against enumeration at `n ≤ 8`);
    `reports/scratch/separator_moment/06_constants/{run.py, constants.csv, run.log}`;
    `reports/separator_moment.md` §6 with the table, the threshold
    proposition and its status, and the figure `β` against `c` (`β*`, the
    bracket on `β_sep`, the slopes; PNG, dataviz skill).
  - **Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/06_constants/run.py`.
  - **Kill criterion.** The brief's: if `β_sep(c) − β*(c) < 0.02` at both
    `c = 6` and `c = 10` (using the fitted rate; the bracket's optimistic
    end is not the test), the separator route is closed for the headline
    constants; record it, and record the closed-pair and combined gains
    beside it. **Separately pre-registered**: the near-threshold gains at
    `c = 2.5, 3, 4` and the threshold statement are findings regardless of
    the kill; say what they are worth (the bracket at `c = 3` is
    `[0.009, 0.056]` by the plan's estimate, against a slope of `0.099`).
  - **Size range.** Asymptotic constants; the finite form at `n = 60, 120`;
    the threshold check at `N ≤ 400`.
  - **Does not claim.** That a fitted rate is the rate; that the threshold
    is proved (its hypothesis is cited or marked not verified); the
    constant (`β_sep` is a lower bound on the truth whatever the rate).

- [ ] **07 The MOSP version: random clique covers.**
  - **Question.** E of the brief. On random clique covers (`m = μ n`
    patterns, sizes `d` or the empirical law), what do the closed-pair
    count, the component flips and the half-giant line give, against
    `β*(d, μ)` and the certified slopes `b` of `excess_phase_diagram.md`
    §2.5; and where does the floor now turn on in excess coordinates?
  - **Method.** (a) *The closed pair on covers.* `E[#closed empty pairs]`
    with sides `(a, r)` and separator `s`: the probability that no pattern
    meets both `A` and `R` *and* every `v ∈ S` shares a pattern with `A`
    and one with `R`, by inclusion–exclusion over the set `T ⊆ S` of
    "bad" vertices with the 4-cell structure `(A, R, T, F)` and the
    `NestedStructure` / `_mobius_coefficients` machinery of
    `learning/first_moment.py` (per pattern of size `s`: the avoid
    probability over unions of cells); the alternating sum over `|T|` in
    exact rationals (`fractions`) or `mpmath` at 200 digits — check against
    enumeration of every cover at `n ≤ 8`, `m ≤ 3` first. The exponent at
    `m = μ n` and its root `β_closed(d, μ)`. (b) *The flips.* Given `(A, R)`
    empty, the two sides are independent random covers; the number of
    isolated customers on a side has the generating function
    `E[z^I] = Σ_i (z − 1)^i C(a, i) Π_j C(a − i, s_j)/C(a, s_j)` (binomial
    moments; check at `n ≤ 8` by enumeration); the first instance of the
    weighted-count identity (item 08 L4): `P(E_S) ≤ Σ_{(A,R)} P(empty) ·
    E[1/C(I_A + I_R, I_A) | empty]`, evaluated exactly from the two
    generating functions; its exponent and the gain in nats per customer.
    (c) *The half-giant line.* The giant component of the random
    intersection graph with fixed pattern size `d` and `m = μ n`: the
    two-type branching process (customer → patterns → customers) and its
    survival probability `θ(d, μ)`; the line `θ = 1/2` in the `(d, μ)` plane
    and in excess `e = μ(d − 1)`, per `r = μ ∈ {⅛, ¼, ½, 1, 2}`, beside
    `e_g(r)` (branching factor 1) and `e = 1` (the pair count's threshold);
    checked against the measured largest-component fractions in
    `learning/data/excess.csv` (item 01 of loop0010; regenerate with
    `python -m learning.excess`). State the proposition: *if* the giant of
    the random intersection graph has an exponentially small lower tail
    (Behrisch 2007 / Lagerås–Lindholm 2008 for the component law; the LDP
    is not in a held paper — say "not verified" unless item 01 found it),
    the separator count's floor is positive above the half-giant line.
    (d) *The constants.* On the grid `d ∈ {2, 3, 4, 6, 8, 10}`, `μ ∈ {½, 1, 2}`:
    `β*`, `β_closed`, the flip gain, the combination; the certified slope
    `b` from §2.5 and the Chu & Stuckey classes' `b`; the exponent's slope
    at `β*` per cell. (e) *The finite floors.* On the 200 Chu & Stuckey
    instances with their empirical sizes (`learning.first_moment.chu_stuckey_sizes`):
    the old pair floor, the exact-size floor, the closed-pair floor and
    the flip floor at `< 1` and `< 0.01`, against the certified optima
    (`learning/data/excess.csv`, provenance read): **zero violations
    required** at `< 0.01`; class means in the format of §8.4. About 1
    core-hour.
  - **Deliverable.** `learning/separator_moment.py` extended
    (`closed_cover_log_bound`, `isolated_pgf`, `flip_log_bound`,
    `rig_giant`, `half_giant_line`) with tests (enumeration at `n ≤ 8`;
    the pgf sums to 1; `θ(d, μ) = 0` exactly at branching factor `≤ 1`);
    `reports/scratch/separator_moment/07_cover/{run.py, grid.csv, floors_cs.csv, run.log}`;
    `reports/separator_moment.md` §7 with the grid table, the floors table
    and the phase-diagram line (a one-line addition to the figure of
    `paper1/latex/figures/excess_phase_diagram.py` is proposed, not made,
    until item 12).
  - **Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/07_cover/run.py --workers 4`.
  - **Kill criterion.** The brief's: `< 0.02` gain over `β*` at `(6, 1)` and
    `(4, 1)` → closed for the headline constants. **Separately
    pre-registered**: the half-giant onset line and the floors on the 200
    instances are findings regardless; a floor violation at `< 0.01` is the
    stop condition of TASK.md.
  - **Size range.** Asymptotic constants; floors at 30–125 customers; the
    half-giant check at `n = 50–75` (the ensemble's largest-component
    fractions).
  - **Does not claim.** Validity under the padded generator beyond what
    §10 of `excess_phase_diagram.md` proved (pre-repair sizes; the
    rejection costs `1/P(accepted)`); the exact inner probability for
    covers (the partition sum is not attempted on covers; the closed pair
    and the flips are the rigorous instances).

- [ ] **08 The theorems on paper: the separator first moment in finite form, the closed-pair count, the weighted-count identity.**
  - **Question.** F of the brief, first half. What exactly is proved, in a
    form items 10 and 12 can carry?
  - **Method.** Write `reports/separator_moment.md` §8 in the style of
    `reports/random_graph_first_moment.md` §1–§2: **Theorem S (separator
    first moment, finite form).** For `k < n`, `0 ≤ p ≤ 1`, `N = n − k`,
    `t = ⌈N/2⌉`: `P(pw(G(n, p)) ≤ k) ≤ C(n, k) · P(G(N, p) ∈ E_bip(t))`,
    where the inner probability is the weighted count
    `Σ_{H on N labelled vertices, H ∈ E_bip} p^{|E(H)|} (1−p)^{C(N,2) − |E(H)|}`.
    Proof: L1 (item 02); the union bound over the `C(n, k)` sets `S`; for a
    fixed `S` the factorisation of the `G(n, p)` weight into the weight of
    `G[V ∖ S]` times the weight of the edges touching `S`, the latter
    summing to `1` (write the bijection between graphs on `V` and pairs
    (graph on `V ∖ S`, edge set touching `S`) explicitly, since item 10 must
    formalise it). **Corollary S′.** The same with `E_rel(t)` (every
    component `≤ t`), weaker but with an `O(N²)` evaluation (Lemma: Gilbert's
    recursion and the first-vertex-component recursion, each stated and
    proved). **Theorem Cl (closed pairs).** `P(pw ≤ k) ≤ Σ_{a ≥ t, r ≥ N − t,
    a + r + s = n, s ≤ k} n!/(a! r! s!) · (1−p)^{ar} · (1 − (1−p)^a)^s (1 − (1−p)^r)^s`
    (from L2; independence of the `s` separator vertices' adjacencies given
    `A, R`). **Lemma W (the weighted-count identity).** For any
    `Z : pairs → ℕ_{≥1}` with `Z(P) ≤ X` on `{P empty}`, `Y = Σ_P 1[P empty]/Z(P) ≥ 1[X > 0]`,
    hence `P(X > 0) ≤ Σ_P P(P empty) · E[1/Z(P) | P empty]`; its first
    instance with `Z = C(I_A + I_R, I_A)` (the flips; item 07 (b)) and the
    exact evaluation of `E[1/Z | planted]` from the generating function.
    **Proposition T (the threshold).** With the hypothesis of item 06 (d)
    explicit. **Every statement checked first**: Theorem S and Cl at
    `n ≤ 7` by enumeration of all labelled graphs at `p = 1/2` and at
    `p = 1/3` with exact rationals (the pattern of
    `reports/scratch/first_moment/check.py`), Lemma W on 1,000 random
    instances at `n = 10` with `Z` = the move-class size and `Z` = the flip
    count; logs kept.
  - **Deliverable.** §8 of the report; `reports/scratch/separator_moment/08_theorems/{check.py, check.log}`;
    the list of Lean targets for item 10 with, for each, the existing lemma
    it rests on and the one new ingredient (the factorisation for S; the
    closure's termination for Cl; nothing new for W beyond finite sums).
  - **Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/08_theorems/check.py --max-n 7`.
  - **Kill criterion.** A counterexample in the check stops the item with
    the statement withdrawn (top of PROGRESS.md).
  - **Size range.** The theorems are for every `n`; the checks at `n ≤ 7`
    and `n = 10`.
  - **Does not claim.** Any rate: Theorem S's inner probability is a finite
    weighted count; its asymptotics are item 06's and are fitted or
    bracketed, not proved here.

- [ ] **09 The branch: the weighted count's lower tail — can any computable `Z` merge the far pairs?**
  - **Question.** Item 04 measured whether the `e^{0.23 n}` cluster is
    typical under the planted measure. If it is, Lemma W with
    `Z(P)` = the number of recombinations around `P` (low-degree separator
    vertices moved across, their few neighbours evicted; the mechanism of
    item 04 (d)) would gain its whole logarithm — *if* `E[1/Z | planted]` is
    small, which is a lower-tail question. What does the lower tail of the
    recombination count cost, and what constant would the weighted count
    give?
  - **Method.** (a) *Definition.* `Z_j(P)` = the number of pairs `(A′, R′)`
    obtained from `P = (A, R, S)` by choosing `U_A ⊆ A`, `U_R ⊆ R` of size
    `j` and `W_A, W_R ⊆ S` with `|W_A| = |U_R| + 1`, `|W_R| = |U_A| − 1`,
    `N_A(W_A) ⊆ U_A`, `N_R(W_R) ⊆ U_R`, no `W_A–W_R` edge; `A′ = (R ∖ U_R) ∪ W_A`,
    `R′ = (A ∖ U_A) ∪ W_R` (check the sizes and that `(A′, R′)` is empty in
    the planted graph: a lemma, brute-force checked). `Z = 1 + max_j Z_j` is
    a valid `Z` for Lemma W. (b) *The measured lower tail.* On item 04's
    planted instances, `Z_j` for `j ≤ 4` by enumeration, the distribution
    of `log Z` and its lower quantiles per cell; against `log X′` (how much
    of the cluster the recombinations account for). (c) *The computable
    bound.* Given `A, R`, the sets `N_A(w)` for `w ∈ S` are independent
    (disjoint edge sets), so `Z_j ≥ C(L_A(j), …) …` with `L_A(j)` = the number
    of `w ∈ S` with `|N_A(w)| ≤ j` (binomial); write the cleanest valid
    lower bound `Z ≥ Ẑ(L_A, L_R, …)` whose Laplace transform
    `E[1/Ẑ | planted]` is a finite sum of binomial probabilities; evaluate
    its exponent at `c = 6, 10`, `β = β*`; the constant it gives through
    Lemma W, `β_W(c)`. Pre-registered expectation (plan §0): the lower tail
    is dominated by "no movable vertex" at cost `q β` per side, so `β_W`
    sits near `β_closed`; the measurement in (b) says whether the typical
    `Z` is much larger than `Ẑ` (the lost gain, in nats). (d) If item 04
    found the cluster to be a rare-instance artefact, do (a)–(c) in one
    page and spend the rest of the session on item 06's near-threshold
    numbers at finer `c` (`2.0, 2.2, …, 4.0`) with item 05's exact
    computation at `N = 60`, since that is where the separator count's
    gain is predicted largest. About 0.5 core-hours.
  - **Deliverable.** `learning/separator_moment.py` extended (`recombinations`,
    `z_hat_log_laplace`, `beta_weighted`) with tests (the recombined pair is
    empty on 200 planted instances; `Ẑ ≤ Z` on every one);
    `reports/scratch/separator_moment/09_lower_tail/{run.py, tail.csv, run.log}`;
    `reports/separator_moment.md` §9.
  - **Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/09_lower_tail/run.py`.
  - **Kill criterion.** If `β_W(c) − β_closed(c) < 0.02` at `c = 6` and `10`
    for the best computable `Ẑ`, the weighted count is closed on this
    record, with the mechanism stated (which lower-tail event dominates
    and what it costs); the measured gap between `Z` and `Ẑ` is recorded
    as the price of computability.
  - **Size range.** Measured at `n = 16–32`; constants asymptotic.
  - **Does not claim.** That no `Z` exists: only that none of the ones
    written down here, with a Laplace transform in closed form, moves the
    constant by `0.02`.

- [ ] **10 Lean: the deterministic lemmas and the union bound over separators.**
  - **Question.** F of the brief, second half. Which of item 08's
    statements are within a session in Lean, and prove them.
  - **Method.** New file `lean/MOSPFormalization/SeparatorMoment.lean`,
    imported by `lean/MOSPFormalization.lean`, importing `EmptyPair`,
    `FirstMoment`, `CliqueCoverMoment`. In order of reach, stop at the
    first that fills the session: (a) **L1** `exists_balanced_separator`:
    `pathwidth G ≤ k → k < n → ∃ A R S : Finset V, Disjoint A R ∧ Disjoint A S ∧ Disjoint R S ∧ A ∪ R ∪ S = univ ∧ A.card = t ∧ R.card = n − k − t ∧ S.card = k ∧ IsEmptyPair G A R`
    (from `exists_empty_pair_of_layout` and `Finset.exists_subset_card_eq`);
    its MOSP form on `mospGraph` through `coverGraph`. (b) **L1′**
    `exists_separator_components_le`: every component of `G.induce (V ∖ S)`
    has at most `t` vertices (a component of `G − S` lies inside `A` or
    inside `R` because no edge crosses; use `ConnectedComponent` and
    `SimpleGraph.induce`). (c) **L2** `exists_closed_empty_pair`: the
    closure as a function `close : Finset V × Finset V → Finset V × Finset V`
    iterated; monotonicity (`A ⊆ A₁`, `R ⊆ R₁` as item 02 proves them);
    termination by `|V ∖ (A ∪ R)|` strictly decreasing until the fixpoint;
    the fixpoint's property `S* = N(A*) ∩ N(R*)` (define
    `closedNbhd` from `EmptyPair.lean`). (d) **Theorem S's union bound**
    `weightedSum_graphsOfPathwidthLe_le_separator`: with `gnpWeight` and
    `graphsOfPathwidthLe` from `FirstMoment.lean`, the sum over graphs with
    `pw ≤ k` is at most `C(n, k)` times the sum of `gnpWeight p` over the
    graphs `H` on `V ∖ S`… — state it on a fixed `S : Finset V` first
    (`weightedSum_restrict_le`: the sum of `gnpWeight p G` over graphs `G`
    whose induced graph on `Sᶜ` lies in a set `𝓗` equals the sum of
    `gnpWeight p H` over `H ∈ 𝓗` on `Sᶜ`; the bijection of item 08) and
    then take the union over `S`. If (d) does not fit, leave it as a named
    `Prop` (`SeparatorFactorisation`) with the obstacle in PROGRESS.md and
    the report; the paper then cites Theorem S as "on paper, deterministic
    part in Lean". (e) `paper1/axiom_check.lean` extended with every new
    theorem; `learning/sandwich.py` inventory still at zero `sorry`; a
    numerical pin: `python -m learning.sandwich --stage separator` checks
    L1 and L2's conclusions on 500 random graphs against the Python
    `close_pair` of item 03.
  - **Rules.** No `sorry`, no `axiom`; `lake build` passes; new theorems in
    the new file only; no existing proof edited.
  - **Deliverable.** The Lean file; its names and axiom lines in
    `reports/separator_moment.md` §10; the sandwich stage; the Appendix A
    rows drafted for item 12 (not yet in the paper).
  - **Regenerate.** `cd lean && lake build`; `make -C paper1/latex axioms`; `python -m learning.sandwich --stage separator`.
  - **Kill criterion.** None; "blocked with the obstacle" is a deliverable,
    and (a)–(c) are expected to be proved.
  - **Size range.** Not applicable.
  - **Does not claim.** Anything about `P_N(E_bip)`'s value or rate; the
    inner count stays a finite weighted sum in Lean and is evaluated on
    paper (item 05).

- [ ] **11 The slack ledger: in stacks, what each count buys and what is left.**
  - **Question.** For a reader of the paper: on certified instances, how
    far is each floor from the pathwidth, and where does the remaining
    slack sit — in the union bound (floor to Harper) or in the necessary
    condition (Harper to pathwidth)?
  - **Method.** (a) On the 650 certified `(6, 1)` instances at `n = 30–75`
    whose Harper values are on record
    (`reports/scratch/structured_count/slack_6_1.csv`; regenerate from seeds
    only if a column is missing, never re-solve): per instance the old
    pair floor, the exact-size pair floor (`nested_floors(1, …)`), the
    closed-pair floor and the flip floor of item 07, Harper, `pw = opt − 1`;
    the quantiles of each consecutive difference per `n`, in stacks. (b) On
    the pilot's `c = 10` cells at `n = 30–60` (`gnp_pilot/results.csv`,
    proved graphs only): the pair floor, the separator floor of item 05 and
    the closed floor of item 06 (finite forms, per graph since `p` and `n`
    are the cell's), Harper (a graph version of `expansion_bound`, closed
    masks from the adjacency, 60 s cap, censoring reported as §8.5 (b)
    does), `pw`; the same quantiles. (c) One paragraph per model saying, in
    stacks at the largest `n`, what the separator and closed counts buy and
    what is left, and whether the leftover grows with `n`. About 0.5
    core-hours (Harper on the pilot graphs).
  - **Deliverable.** `reports/scratch/separator_moment/11_ledger/{run.py, ledger_6_1.csv, ledger_gnp.csv, run.log}`;
    `reports/separator_moment.md` §11 with the two tables and the
    paragraph; the figure of the ladder (floor → … → Harper → `pw`) per
    `n` (PNG, dataviz skill).
  - **Regenerate.** `nice -n 19 python3 reports/scratch/separator_moment/11_ledger/run.py --workers 6`.
  - **Kill criterion.** None (descriptive). A floor above a certified
    optimum is the stop condition of TASK.md.
  - **Size range.** `n = 30–75` covers; `n = 30–60` pilot graphs.
  - **Does not claim.** Anything above 75 customers; Harper under a cap is a
    lower bound on the true Harper value and the differences are stated in
    the direction that survives that (§8.5 (b)).

- [ ] **12 The write-up: the report's summary, the paper's paragraph, the `CLAUDE.md` paragraph.**
  - **Question.** H of the brief. One document a reader can follow, and
    the paper's text.
  - **Method.** (a) `reports/separator_moment.md` §0, a two-page opening:
    the three events (pair, separator, closed pair) and the weighted
    identity; the ladder of counts with, for each, its status — *theorem*
    (Lean name), *on paper* (section), *measured* (size range, regenerate
    command), *fitted*, *conjectured*; the constants table (`β*`, `β_closed`,
    `β_sep` with its basis, the slopes) for `G(n, c/n)` and for covers; the
    threshold statements with their hypotheses' status; the clumping
    decomposed (items 03–04) in one paragraph; the kill verdicts in one
    table; "What this is not" and "Open" sections; then §1–§11 edited for
    one voice. (b) The paper: in `paper1/latex/sec9e_appendix_random.tex`,
    replace the last two sentences of "Why the first moment is loose" and
    the closing sentence of the section ("closing it would need a count
    over one representative per cluster…") with what is now known — at
    most one page: the separator count, its finite theorem, the threshold
    `2 ln 2` with its hypothesis, the constants at `c = 3` and `c = 10` with
    their basis, the closed-pair count, what the planted measurement says
    the cluster is, and the honest sentence on the gap that remains;
    Appendix A rows and axiom lines for the new Lean theorems
    (`make -C paper1/latex axioms`); references with checked DOIs
    (`paper1/latex/check_refs.py`) for every paper item 01 cited. Wording:
    "we found no prior statement", never "first"; a fitted rate is called
    fitted; a measurement is never called a theorem. (c) The `CLAUDE.md`
    paragraph the owner will need, written into
    `reports/separator_moment.md` §"For CLAUDE.md" in the format of the
    existing "The excess phase diagram" paragraph; do not edit `CLAUDE.md`.
    (d) `reports/excess_phase_diagram.md` §14 item 1 struck through with a
    pointer to the new report (one line; nothing else in that file changes).
  - **Deliverable.** The report; the paper builds (`make -C paper1/latex`
    then `make check`), page count before and after recorded; the gate
    passes.
  - **Regenerate.** `make -C paper1/latex && make -C paper1/latex check`.
  - **Kill criterion.** None.
  - **Size range.** As stated per claim.
  - **Does not claim.** Beyond what the items proved, measured or fitted.

- [ ] **13 Reserve.** The best remaining gap from items 01–12, one session:
  a killed item's cheapest surviving variant (the near-threshold constants
  at finer `c`, or the cover-model partition sum for `E_bip` at small `N`),
  a Lean statement left as a named `Prop`, or the planted measurement at
  one larger `n` with a pruned enumerator. Say in PROGRESS.md why this one.
