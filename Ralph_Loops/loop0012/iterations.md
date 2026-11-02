# loop0012 — the Edwards–McDermid degree-sequence bound: verified, then formalised: items

Edwards & McDermid (2015, *Algorithmica* 72:940–968) prove
`pw(G) ≤ Σ_{v ∈ V(r(G))} g_{1/6}(d_{r(G)}(v)) + τ(n) + O(log n)` for every
graph `G` (Corollary 5.2), with `r(G)` the series-parallel reduction of `G`,
`g_{1/6}(2) = 0`, `g_{1/6}(3) = 1/6`, `n g(n) = (n − 2) g(n − 1) + g(n − 2) + 1`,
and `τ(n) = o(n)` Fomin & Høie's error term for cubic graphs. On Poisson(`c`)
degrees it is the best published upper bound on `pw(G(n, c/n))/n` at every
`c` from 2 to about 32 (`0.183, 0.458, 0.656` at `c = 3, 6, 10`;
`reports/random_graph_pathwidth_literature_2.md` §3.3). The plan
`reports/edwards_mcdermid_plan.md` quotes every statement the loop needs
(§0.2), names the two cited results the formalisation is conditional on —
the cubic base case `CubicPathwidthBound τ` and the reduction lemma
`ReductionPathwidthBound ρ` (§0.3) — lists where the paper and the record
correct the brief (§0.4: the paper gives no constants; the "simple kind" has
pathwidth `Θ(log n)`, not a constant; Fomin–Høie's transfer is one bisection,
not a recursion; no finite graph can violate the stated corollary; Kneis et
al. is not held), and fixes the Lean design (§0.5).

Phase 1 (01–02) verifies and states; phase 2 (03–09) proves in Lean, in order
of reach, with the independent cut lemma early; 10 writes; 11 is the reserve.
Every item: one session, `nice -n 19`, at most 8 workers (4 if the one-minute
load in `uptime` is above 24), nothing solved twice, every brute-force check
persisted under `reports/scratch/edwards_mcdermid/<item>/`, every Lean
statement checked on small graphs before it is stated.

- [x] **01 Fetch the manuscript; evaluate Corollary 5.2 and Theorem 5.3 on every graph with a proved pathwidth.**
  - **Question.** A of the brief. With the lower-order terms spelled out as
    the paper states them, does `pw(G) ≤ Σ_{v ∈ r(G)} g(d_{r(G)}(v)) + τ(n) + O(log n)`
    hold on every graph whose pathwidth is on record, what is the per-graph
    slack of the main term, how far is the reduced sum below the unreduced
    histogram sum, does the Poisson evaluation match the per-graph values on
    `G(n, c/n)` at `n = 60–120`, and what does Theorem 5.3's average-degree
    form give where it applies? And, since the paper gives no constants for
    its base case: what budget do the cubic graphs on record require?
  - **Method.** (a) *Fetch.* `curl -L` the accepted manuscript from
    `https://discovery.dundee.ac.uk/ws/portalfiles/portal/6880233/edwmcd_2_.pdf`
    into `reports/scratch/edwards_mcdermid/em2015.pdf` (a new, empty
    directory; nothing executed from it), `pdftotext -layout` to
    `em2015.txt`; record the SHA-256 and the download date; if the URL
    fails, use `/tmp/lit_random/em2.pdf` if it still exists and say so, else
    work from the plan's §0.2 quotations and record "not re-fetched". Read
    Sections 1, 3, 5 and the Appendix against the plan's quotations; any
    discrepancy goes at the top of the report. (b) *Code.* New module
    `learning/edwards_mcdermid.py`: `g(n)` in `fractions.Fraction` with a
    float shadow (`g(0) = g(1) = g(2) = 0`), `g_prime`, `reduce(adj)` — the
    four operations on bit-mask adjacency with a bucket queue of vertices by
    degree, returning the reduced adjacency and the removed set (linear in
    the number of steps; the dataset has graphs to 2,916 vertices, so never
    recompute all degrees per step), `main_term(adj)` = `Σ_{v ∈ r(G)} g(deg)`,
    `histogram_term(adj)` = `Σ_{d ≥ 3} g(d) n_d(G)`, `average_degree_term`
    = `g(d̄) · n` with the linear interpolation of the paper (p. 6),
    `fminus(adj)` (per component, for item 02), `poisson_value(c)`.
    Tests in `tests/test_edwards_mcdermid.py`: the `g` table of the plan
    (p. 7 of the paper) to `d = 8` exactly; properties 3, 4, 6 and the
    closed form (Lemma 8.1) to `n = 30`; `reduce` on a tree (empty), a cycle
    (a triangle: operation 3 until three vertices remain), `K_4` (fixed),
    a subdivided `K_4` (back to `K_4`), and the fact that no surviving
    vertex's degree rises (checked on 200 random graphs);
    `main_term ≤ histogram_term` on the same 200. (c) *Sources.* Every
    graph with a proved pathwidth: the pilot (`reports/scratch/gnp_pilot/results.csv`,
    rows with `status ∈ {refutation, bound, minor}`, regenerated as
    `nx.gnp_random_graph(n, c/n, seed=seed)` and checked against the `m`
    column; `upper` rows carried separately with their `lower` column
    only), the dataset (`paper1/data/dataset/pathwidth_dataset.jsonl.gz`,
    `provenance` starting with `certified`; `solution` rows carried
    separately as upper bounds), the ensembles (`learning/data/ensemble/results*.csv`,
    `certified == True`, instance from seed, MOSP graph, `pw = optimum − 1`;
    deduplicate by canonical form within a cell if `learning.canonical` is
    cheap, else keep repeats and say so). Per graph: `n, m, pw, main_term,
    histogram_term, deficit = pw − main_term, deficit_hist = pw − histogram_term,
    n_reduced, components, connected, avg_degree, avg_term (where connected
    or d̄ ≥ 5)`. 8 workers, about 1 core-hour; one CSV per source. (d) *The
    lower-order term as the paper states it.* Report, per source and per
    `n`-band, the deficit's maximum, 99th percentile, median; the share of
    graphs with `deficit ≤ 0` (the main term alone already bounds); the
    budget the record needs, `B(n) = max{deficit : |V| ≤ n}`, tabulated
    at `n = 10, 20, 40, 60, 100, 200, 500, 1000, 2916`; and beside it
    Fomin–Høie's explicit budget `τ_FH(n) = min{εn : n > (8/ε) ln(1/ε)(1 + 1/ε²)} + 1/6`
    (plan §0.3), which is expected to exceed every deficit by a wide margin
    — state that the corollary with that budget is therefore satisfied on
    every graph and that the informative column is `B(n)`. (e) *The
    base case measured.* All cubic graphs to 16 vertices by
    `nauty-geng -c -d3 -D3 N` (connected; counts 1, 2, 5, 19, 85, 509, 4,060
    at `N = 4, 6, …, 16`), pathwidth by the subset DP; the 42 certified
    cubic graphs of the dataset (`N` to 120; identify them by degree); per
    `N` the maximum of `pw − (N/6 − 1/6)`, and the smallest `c` with
    `pw ≤ N/6 − 1/6 + c` on all of them, labelled "measured to `N = 16`
    exhaustively and on 42 certified graphs to 120". (f) *Poisson.* On the
    pilot cells at `n ∈ {60, 70, 80, 90, 100, 120}`, `c ∈ {3, 4, 6, 8, 10}`
    (all rows, proved or not — the main term needs no pathwidth): the mean
    and spread of `histogram_term/n` and `main_term/n` against
    `poisson_value(c)`; the difference between the two terms is the
    reduction's gain on `G(n, c/n)` (expected large at `c = 3`, where most
    vertices have degree ≤ 2 or hang on trees, small at `c = 10`); a figure
    (PNG, dataviz skill read first) of the three against `c` at `n = 120`.
    The survey §7(e)-style column for the pilot: per cell, `pw/n` (proved
    rows), `main_term/n`, the ratio. (g) *Theorem 5.3.* On every connected
    graph of the record and every graph with `d̄ ≥ 5`:
    `deficit_avg = pw − g(d̄) n`; its maximum per source; the count of
    graphs with `main_term > g(d̄) n` (Jensen says none when connected or
    `d̄ ≥ 5` — the Edwards–Farr averaging lemma — so a positive count is a
    finding to report, not a violation of anything proved here).
  - **Deliverable.** `reports/edwards_mcdermid.md` created, with the
    document's header (what the loop is, the statement with the quotation's
    page, the two hypotheses, the notation `g, g', f, f⁻, r(G)`), §1 with
    the tables of (d)–(g) and the figure; `learning/edwards_mcdermid.py`
    with tests; `reports/scratch/edwards_mcdermid/em2015.{pdf,txt}`,
    `SHA256`, `01_verify/{run.py, pilot.csv, dataset.csv, ensemble.csv, cubic.csv, run.log}`.
  - **Regenerate.** `nice -n 19 python3 reports/scratch/edwards_mcdermid/01_verify/run.py --workers 8` (stages `pilot`, `dataset`, `ensemble`, `cubic`, `tables`).
  - **Kill criterion.** The brief's, applied where it is falsifiable: if any
    proved graph has `pw > main_term + τ_FH(n)` (which the plan says cannot
    happen at our sizes), or if `main_term > histogram_term` on any graph,
    or if `reduce` ever raises a degree, our reading of the statement is
    wrong: stop, re-read Section 3.2 and Corollary 5.2, and write the
    correction at the top of the report before anything else. A graph with
    `pw − main_term` above `B(n)` of the plan's expectation is not a kill;
    it is the number this item exists to measure.
  - **Size range.** Every proved graph on record: pilot `n = 20–120`,
    dataset `n ≤ 2,916`, ensembles `n = 10–100`; cubic graphs exhaustively
    to 16 and certified to 120; the Poisson check at `n = 60–120`.
  - **Does not claim.** Anything about the constants in the paper's
    `o(n) + O(log n)` beyond what the record shows at these sizes; that the
    paper's bound is tight anywhere; that `B(n)` is a bound for graphs not
    on record.

- [x] **02 The exact statement to formalise, every intermediate lemma brute-force checked.**
  - **Question.** B of the brief. Written out over `SimpleGraph V` in the
    plan's §0.5 design, what exactly are the statements items 03–09 will
    prove, and do they hold on every graph to 9 vertices?
  - **Method.** (a) *The statements*, in `reports/edwards_mcdermid.md` §2,
    numbered, each with its hypotheses, conclusion, the paper's location,
    and the existing Lean lemma it will rest on: **W1–W5** the weight
    lemmas (recurrence; `g` non-decreasing, Lemma 8.3; `g'` non-increasing
    from 3, Lemma 8.4; property 6; `0 ≤ g < 1`, `0 ≤ g' ≤ 1/6` for `d ≥ 3`;
    the closed form, Lemma 8.1, optional). **C1** the cut lemma: for any
    partition `V = V_1 ⊔ V_2` with boundaries `∂_i` (vertices of `V_i` with
    a neighbour across), `pw(G) ≤ max(pw(G[V_1]) + |∂_1|, pw(G[V_2]) + |∂_2|, |∂_1| + |∂_2| − 1)`;
    **C2** its iterated form for a recursive bisection of depth `h` with
    boundary budgets `b_1, …, b_h` per level: `pw(G) ≤ Σ_i 2 b_i + max_leaf pw`
    (write the exact statement; the factor 2 is `|∂_1| + |∂_2|`), and a
    note that Fomin–Høie reach `n/6` with one level and Lemma 4, not with
    C2 (plan §0.4 (3)). **P1** `f(G − w) = f(G) − g(d(w)) − Σ_{v ∈ N(w)} g'(d(v))`;
    **P2** if every degree is 0 or ≥ 3, `w` has maximum degree `Δ ≥ 4` and
    some neighbour of degree `≤ Δ − 1`, then `f(G − w) ≤ f(G) − 1`; if `G`
    is `Δ`-regular, `f(G − w) ≤ f(G) − 1 + g'(Δ − 1) − g'(Δ)`. **R1** every
    `SPStep` lowers the total degree, so `SPReduces` terminates and a
    reduced reduct exists; **R2** no surviving vertex's degree rises along
    `SPReduces`, hence `f(H') ≤ f(H)` and, if `v` is isolated by the
    reduction, `f(H) − f(H') ≥ g(d_H(v))`; **R3** the commutation lemma:
    `SPStep H H'` at `v`, `w ≠ v` ⇒ `SPReduces (H − w) (H' − w)` in 0 or 1
    step; **R4** its lift: `SPReduces H H'`, `X` disjoint from the vertices
    the sequence acts on ⇒ `SPReduces (H − X) (H' − X)`. **S1** the step
    inequality: `G` connected on its support, every degree 0 or ≥ 3, not
    basic, `w` of maximum degree chosen with the lowest-degree neighbour
    (ties arbitrary), `G* ` any reduced reduct of `G − w` ⇒
    `1 + f⁻(G*) ≤ f⁻(G)`; **S1′** the same for *every* maximum-degree `w`
    (to be measured: if it holds, item 07 may pick `w` by
    `Finset.exists_max_image` alone). **T1** Theorem 3.2 in the plan's
    form (existence of `X`, `B`). **A1** the assembly: under
    `CubicPathwidthBound τ` and `ReductionPathwidthBound ρ`,
    `pw(G) ≤ f⁻(G) + τ(n) + 2ρ(n) + 1` for reduced `G`; **A2** Corollary
    5.2's form with `3ρ`. **B1** basic graphs: on a second-kind component
    `f⁻ ≥ 5/6`; on a cubic component `f⁻ = N/6 − 1/6`; `f⁻ ≥ f⁻` of each
    component (additivity). (b) *The checks*, script
    `reports/scratch/edwards_mcdermid/02_lemmas/check.py` in the pattern of
    `reports/scratch/empty_pair/check.py`, every graph on 1–9 vertices from
    `nauty-geng` (288,266 graphs; 8 workers, about 1.5 core-hours; if the
    9-vertex `S1′` sweep is slow, do it to 8 and say so), pathwidth by the
    subset DP: W1–W5 to `n = 40` in exact rationals; C1 on every graph with
    every partition to 7 vertices and 2,000 random partitions per graph at
    8–9; P1–P2 for every `w`; R1–R2 along a canonical reduction and along
    200 random reduction orders per graph (also recording whether all
    orders reach the same reduct — the paper's uniqueness claim, measured);
    R3 for every (graph, step, `w`) to 8 vertices; S1 for the paper's
    choice of `w` and S1′ for every max-degree `w`, on every connected
    non-basic graph of minimum degree 3 (the first such graphs appear at 5
    vertices); T1 through Algorithm X; A1–A2 as an inequality *about the
    budgets*: on every graph, `pw − f⁻` for reduced graphs and
    `pw − main_term` for all, their maxima per `n` (these are the `τ + 2ρ + 1`
    the record needs at `n ≤ 9`, nothing more); and (H3)'s shape:
    `pw(H) − pw(r(H))` for every graph to 9 vertices, its maximum per `n`
    (expected ≤ 2). Every check prints its counts; a violation prints the
    graph6 string and stops.
  - **Deliverable.** §2 of the report with the statements, their check
    counts and the two measurements (uniqueness of the reduct; `S1′`);
    `reports/scratch/edwards_mcdermid/02_lemmas/{check.py, check.log, violations.txt}`;
    the Lean-ready list for items 03–09 (names, hypotheses, conclusions,
    file, which existing lemma each rests on), in the report and copied
    into PROGRESS.md.
  - **Regenerate.** `nice -n 19 python3 reports/scratch/edwards_mcdermid/02_lemmas/check.py --max-n 9 --workers 8`.
  - **Kill criterion.** A counterexample to any of W1–W5, C1, P1–P2, R1–R4,
    S1, T1, B1 stops the item with the graph drawn and the statement
    withdrawn or corrected; it also stops the loop's premise for the Lean
    items that rest on it, so write it at the top of PROGRESS.md. A
    counterexample to S1′ alone is a finding (item 07 then keeps the
    paper's tie-break). A reduct that depends on the order is a finding
    (the Lean design does not need uniqueness).
  - **Size range.** Every graph to 9 vertices (8 for R3 and S1′ if needed);
    weights to `n = 40`.
  - **Does not claim.** Anything for `n > 9`; that (H1) or (H3) hold (they
    are cited, and only their shape is looked at here).

- [x] **03 Lean (i): the weights `g`, `g'` and their lemmas.**
  - **Question.** Can the function `g_{1/6}` and the five properties the
    reduction theorem uses be proved in Lean in `ℚ`?
  - **Method.** New file `lean/MOSPFormalization/DegreeBound/Weights.lean`,
    imported by `lean/MOSPFormalization.lean`. `def g : ℕ → ℚ` by
    well-founded (or two-step structural) recursion with `g 0 = g 1 = g 2 = 0`,
    `g 3 = 1/6`, `g (n + 2) = ((n) * g (n + 1) + g n + 1) / (n + 2)` for
    `n + 2 ≥ 4`; `g' n := g n − g (n − 1)`. Theorems, in this order, each
    checked against item 02's table first: `g_table` (the eight values to
    `d = 9`, by `norm_num [g]` or `decide`-free unfolding); `g_lt_one`;
    `g_nonneg`; `g_mono` (Lemma 8.3: the coupled invariant
    `g (n − 1) ≤ g n ≤ (1 + g (n − 1)) / 2` by induction from `n = 3`);
    `g'_nonneg`, `g'_le_sixth` (`g' n ≤ 1/6` for `n ≥ 3`); `g'_antitone`
    (Lemma 8.4: derive `n g' n = (n − 3) g' (n − 1) + g' (n − 2)` for
    `n ≥ 5` and the sandwich `g' (n − 1) ≥ g' n ≥ g' (n − 1) / 3` by
    induction with the base `g' 3 ≥ g' 4 ≥ g' 3 / 3`, i.e. `1/6 ≥ 1/6 ≥ 1/18`);
    `one_sub_g_eq` (property 6: `1 − g n = (n − 1) g' n + g' (n − 1)` for
    `n ≥ 4`); if time remains, `g_closed_form` (Lemma 8.1 with
    `altFactorial`) and `g_div_antitone` (Lemma 8.5, `g n / n` strictly
    decreasing from 5). Then `learning/sandwich.py --stage degree_bound`:
    the Lean recursion transcribed and compared with
    `learning.edwards_mcdermid.g` to `n = 200` in exact rationals; the
    `DEGREE_BOUND_PROVED` name list. `#print axioms` lines for every
    theorem in `paper1/axiom_check.lean`.
  - **Rules.** No `sorry`, no `axiom`; `lake build` passes; nothing outside
    the new file, the root import, the axiom check and the sandwich stage.
  - **Deliverable.** The file; `reports/edwards_mcdermid.md` §3 with the
    names, statements and axiom lines; `reports/scratch/edwards_mcdermid/03_weights/{lake_build.log, axiom_check.log, sandwich.log}`.
  - **Regenerate.** `cd lean && lake build`; `make -C paper1/latex axioms`; `python -m learning.sandwich --stage degree_bound`.
  - **Kill criterion.** None; the two inductions are the paper's and were
    checked in item 02. If `g'_antitone` does not fit, leave it last and
    say so: items 05–07 need it, and 07 will not start without it.
  - **Size range.** Not applicable (every `n`).
  - **Does not claim.** Anything about `g_α` for `α ≠ 1/6`, or about the
    real-interpolated `g` (Theorem 5.3's form is not formalised).

- [x] **04 Lean (v): the cut lemma and its iterated form — independent of the hypotheses, reusable.**
  - **Question.** Can the one-cut transfer — a vertex partition with
    boundaries gives a path decomposition from decompositions of the two
    sides — and its recursive iteration be proved in Lean, as a tool that
    does not depend on either named hypothesis?
  - **Method.** New file `lean/MOSPFormalization/DegreeBound/CutLemma.lean`.
    Definitions: `boundary G A := A.filter (fun a => ∃ b ∉ A, G.Adj a b)`.
    **C1** `pathwidth_le_of_partition`: for `A : Finset V`,
    `pathwidth G ≤ max (max (pathwidth G[A] + |∂A|) (pathwidth G[Aᶜ] + |∂Aᶜ|)) (|∂A| + |∂Aᶜ| − 1)`
    (in `ℕ` with the `− 1` handled as the paper's width convention; state
    it with `+ 1` on the left if that is cleaner, and say which). Proof:
    `PathDecomposition.extend`-style addition of `∂A` to every bag of a
    decomposition of `G[A]` (`TreeBound.lean` adds `Sᶜ` to every bag; the
    same construction with a different set), a final bag `∂A`, a middle bag
    `∂A ∪ ∂Aᶜ`, the mirrored construction on `Aᶜ`, concatenation by the
    `cat`/`glue` pattern; the three coverage conditions and the interval
    property case by case on `v ∈ A ∖ ∂A`, `v ∈ ∂A`, `v ∈ ∂Aᶜ`, `v ∈ Aᶜ ∖ ∂Aᶜ`.
    **C2** `pathwidth_le_of_bisection_tree`: a recursive bisection given as
    a function from depth-`h` binary addresses to finsets partitioning `V`
    level by level, with `b i` bounding every boundary at level `i`:
    `pathwidth G ≤ Σ_{i < h} 2 b i + max over leaves of pathwidth G[leaf]`
    — by induction on `h` through C1 (state exactly; if the general tree
    is awkward, prove the two-level case and the statement "C1 applied
    `h` times" as a `List`-indexed induction). Before either is stated:
    `reports/scratch/edwards_mcdermid/04_cut/check.py` checks C1 on every
    graph to 7 vertices with every `A`, and C2 at depth 2 on 2,000 random
    graphs at 10–12 vertices with random balanced partitions (item 02 did
    C1; repeat the C2 check here since its statement is this item's). In
    the report: what Fomin–Høie's one-level argument adds (Lemma 4's
    `max{|X|, n/3 + 1} + (2/3) log_3 n + 1` with the boundary as the end
    bag, and the sweep that holds the middle at `|∂V_1| + 1` for maximum
    degree 3), quoted from the plan, stated as a lemma and **not** proved —
    a candidate for item 11.
  - **Deliverable.** The file; §4 of the report (statements, Lean names,
    axiom lines, the check's counts, the Fomin–Høie paragraph); the check
    script and log; `#print axioms` lines.
  - **Regenerate.** `cd lean && lake build`; `make -C paper1/latex axioms`; `nice -n 19 python3 reports/scratch/edwards_mcdermid/04_cut/check.py --max-n 7`.
  - **Kill criterion.** A counterexample in the check stops the item with
    the statement withdrawn. If C2 does not fit, C1 alone is the
    deliverable and C2 is stated in the report as "C1 iterated; not in
    Lean".
  - **Size range.** Checks to 7 (C1) and 12 (C2); the lemmas are for every
    graph.
  - **Does not claim.** Fomin–Høie's `n/6` (which needs Lemma 4 and the
    sweep, not C1–C2); anything about bisection *widths* of random graphs.

- [x] **05 Lean (ii): the potential and the one-deletion degree accounting.**
  - **Question.** Can `f(G − w) = f(G) − g(d(w)) − Σ_{v ∈ N(w)} g'(d(v))` and
    its consequence `f(G − w) ≤ f(G) − 1` (for `w` of maximum degree `≥ 4`
    with a lower-degree neighbour, in a graph whose degrees are 0 or `≥ 3`)
    be proved in Lean?
  - **Method.** New file `lean/MOSPFormalization/DegreeBound/Potential.lean`,
    importing `Weights` and `Minor` (`isolate`). `def potential (G) : ℚ := Σ_v g (G.degree v)`
    (`f`); `degree_isolate`: `(G.isolate w).degree v = G.degree v − 1` if
    `G.Adj w v`, `= 0` if `v = w`, unchanged otherwise (from
    `neighborFinset` of `isolate`); **P1** `potential_isolate`: the exact
    identity, by splitting `Finset.univ` into `{w}`, `G.neighborFinset w`
    and the rest (`Finset.sum_erase`, `Finset.sum_filter`); **P2**
    `potential_isolate_le_sub_one`: with `hdeg : ∀ v, G.degree v = 0 ∨ 3 ≤ G.degree v`,
    `hmax : ∀ v, G.degree v ≤ Δ`, `hw : G.degree w = Δ`, `h4 : 4 ≤ Δ`,
    `hlow : ∃ v, G.Adj w v ∧ G.degree v ≤ Δ − 1`:
    `potential (G.isolate w) ≤ potential G − 1` — from P1, `one_sub_g_eq`
    at `Δ` and `g'_antitone` (every neighbour has degree between 3 and
    `Δ`, one at most `Δ − 1`); **P2′** `potential_isolate_le_regular`: with
    all neighbours of degree `Δ`, `≤ potential G − 1 + g' (Δ − 1) − g' Δ`.
    Also the component potential: `minDeg G C` (`Finset.inf'` of the
    degree over `C.supp`, or over a `reachSet`-style finset — follow
    `TreeBound.lean`'s `reachSet` if Mathlib's `ConnectedComponent.supp` as a
    `Finset` is awkward), `potentialMinus G := potential G − Σ_C g' (minDeg G C)`
    (`f⁻`), `potentialMinus_le_potential`, and `potentialMinus_add` for a
    graph that is a disjoint union of two graphs on `V` with no shared
    non-isolated vertex (the additivity the disconnected case of Theorem
    3.2 needs; state it as `potentialMinus (G₁ ⊔ G₂) = potentialMinus G₁ + potentialMinus G₂`
    under `Disjoint (support G₁) (support G₂)` — isolated vertices
    contribute `g' 0 = 0`). Before stating: item 02's P1–P2 checks cover
    the first two; add `reports/scratch/edwards_mcdermid/05_potential/check.py`
    for `potentialMinus_add` on 2,000 random disjoint unions at `n ≤ 12`.
  - **Deliverable.** The file; §5 of the report; the check script and log;
    `#print axioms` lines; the sandwich stage extended with `fminus` on 500
    random graphs against `learning.edwards_mcdermid.fminus`.
  - **Regenerate.** `cd lean && lake build`; `make -C paper1/latex axioms`; `python -m learning.sandwich --stage degree_bound`.
  - **Kill criterion.** None; if `potentialMinus_add` does not fit, it is
    the first thing item 08 must do and PROGRESS.md says so.
  - **Size range.** Not applicable.
  - **Does not claim.** Anything about reductions (item 06) or pathwidth
    (item 09).

- [x] **06 Lean (iii): the series-parallel reduction system, basic graphs, degree monotonicity, and the commutation of deletion with reduction.**
  - **Question.** Can the four operations, their closure, "reduced",
    "basic", the facts the step inequality needs (R1, R2) and the local
    commutation lemma that replaces the paper's appeal to Kneis et al.'s
    confluence (R3, R4) be defined and proved in Lean?
  - **Method.** New file `lean/MOSPFormalization/DegreeBound/SPReduction.lean`,
    importing `Potential`. `inductive SPStep (G G' : SimpleGraph V) : Prop`
    with four constructors: `isolated`/`pendant` (a vertex `v` with
    `G.degree v ≤ 1`, `G' = G.isolate v`), `suppress` (`G.degree v = 2`,
    neighbours `x ≠ y`, `¬ G.Adj x y`, `G' = (G.isolate v) ⊔ edge x y`),
    `triangle` (`G.degree v = 2`, neighbours adjacent, `G' = G.isolate v`);
    `SPReduces := Relation.ReflTransGen SPStep`; `IsSPReduced G := ∀ v, G.degree v = 0 ∨ 3 ≤ G.degree v`;
    `support G := univ.filter (fun v => 0 < G.degree v)`;
    `IsBasic G := ∀ C (a component of the support, as a finset of vertices
    reachable from a non-isolated vertex), (∀ v ∈ C, G.degree v = 3) ∨ ∃ v ∈ C, SPReduces ((G.induce_on C).isolate v) ⊥`
    (state with the induced-on-`C` graph kept on `V`: edges inside `C`
    only). Theorems: **R1** `SPStep` strictly lowers `Σ_v degree`
    (`sum_degrees_eq_twice_card_edges` or a direct count), hence
    `exists_reduced_reduct : ∃ H, SPReduces G H ∧ IsSPReduced H`
    (well-founded on the degree sum); **R2** `degree_le_of_spStep`:
    `G'.degree v ≤ G.degree v` for every `v` (suppression: `x` loses `v`
    and gains `y`), lifted to `SPReduces`; `potential_le_of_spReduces`;
    `potential_sub_ge_of_isolated`: if `SPReduces G H` and `H.degree v = 0 < G.degree v`
    then `potential G − potential H ≥ g (G.degree v)` (every summand of
    the difference is `≥ 0` by R2 and `g_mono`, and `v`'s is `g (deg v) − g 0`);
    **R3** `spStep_isolate_comm`: `SPStep G G'` acting at `v`, `w ≠ v` ⇒
    `SPReduces (G.isolate w) (G'.isolate w)` with at most one step — the
    cases of plan §3 risk 3 (not adjacent: the same step; `w` a neighbour of
    a degree-2 `v`: a pendant deletion; `w` the neighbour of a degree-1
    `v`: an isolated deletion; the degree-0 case: zero steps; in the
    suppression case with `w ∈ {x, y}`, `(G.isolate w).isolate v = G'.isolate w`
    since the added edge `xy` vanishes with `w`); **R4** the lift to
    `SPReduces` and to a finset `X` disjoint from the acted-on vertices
    (`Relation.ReflTransGen.head_induction_on`, then `Finset.induction`).
    Before stating R3: item 02 checked it to 8 vertices; re-run that
    check's R3 stage here and keep its log beside the file. If R3's
    "acted-on vertex" needs to be recorded, make `SPStep` carry it
    (`SPStep v G G'`) from the start.
  - **Deliverable.** The file; §6 of the report; `reports/scratch/edwards_mcdermid/06_reduction/{check_r3.log, lake_build.log}`;
    `#print axioms` lines.
  - **Regenerate.** `cd lean && lake build`; `make -C paper1/latex axioms`.
  - **Kill criterion.** None; "blocked with the obstacle" is a deliverable.
    If R3 does not fit, R1–R2 are the deliverable, R3–R4 are named in the
    report as the gap, and item 08 states Theorem 3.2 with
    `SPReduces (G − X) B` replaced by the paper's own hypothesis form
    (`r(G − X) = B`, with `r` a chosen reduced reduct and Lemma 3.1 as a
    named `Prop` `ReductionConfluence`) — say which in PROGRESS.md.
  - **Size range.** Not applicable.
  - **Does not claim.** Uniqueness of the reduct (not needed; measured in
    item 02); that `SPReduces G ⊥` characterises series-parallel graphs
    (the paper's "it follows from the definition" is not formalised and
    "series-parallel" does not appear in Lean).

- [x] **07 Lean (iv-a): the step inequality `1 + f⁻(G*) ≤ f⁻(G)` for a connected non-basic graph.**
  - **Question.** The heart of Theorem 3.2's proof (pp. 10–12): with `w` a
    maximum-degree vertex whose lowest-degree neighbour is as low as
    possible, `G' = G − w`, `G*` a reduced reduct of `G'`, does
    `1 + f⁻(G*) ≤ f⁻(G)` hold, in all the paper's cases, in Lean?
  - **Method.** New file `lean/MOSPFormalization/DegreeBound/Step.lean`,
    importing `SPReduction`. Hypotheses, named once in a `structure StepData`:
    `G` with `IsSPReduced G`, connected on its support, not basic,
    `Δ = max degree ≥ 4`, `w` with `degree w = Δ` and
    `∀ u, degree u = Δ → lowNbr w ≤ lowNbr u` (the tie-break; drop it if item
    02's S1′ held for every max-degree `w` — then only `degree w = Δ` is
    needed, and say so), `SPReduces (G.isolate w) G*`, `IsSPReduced G*`,
    `G* ≠ ⊥`. Lemmas: `j4_ge`: if `v ≠ w` and `3 ≤ (G.isolate w).degree v = d`,
    then `potential (G.isolate w) − potential G* + g' (minDeg G*) ≥ g' d`
    (the two cases of p. 11: `v` survives with degree `≤ d` — `minDeg G* ≤ d`
    and `g'_antitone`; or `v` is isolated in `G*` — `potential_sub_ge_of_isolated`
    and `g d ≥ g' d`); `step_regular`: all neighbours of degree `Δ` ⇒ a
    neighbour has degree `Δ − 1 ≥ 3` in `G − w`, so `j ≥ g' Δ`; `step_low_survivor`:
    some `v ≠ w` with `3 ≤ (G − w).degree v ≤ δ(G)`; `step_delta_three`: the
    two sub-cases with `δ(G) = 3` and every degree-3 vertex adjacent to `w`
    (`d(v_Δ) > 3`; all neighbours of degree 3, reduced away, and a vertex
    `v` not adjacent to `w` with `(G − w).degree v ≥ 3` — this needs `G* ≠ ⊥`
    and R2). Assemble **S1** `one_add_potentialMinus_le`:
    `1 + potentialMinus G* ≤ potentialMinus G`. Note `potentialMinus G = potential G − g' (δ G)`
    for connected `G` (one component) and `potentialMinus G* ≤ potential G* − g' (minDeg G*)`
    (the global minimum is one of the components' minima and the other
    terms are `≥ 0`) — the paper's inequality (2), which is what makes the
    per-component `f⁻` disappear from this item. Before stating: item 02's
    S1 check (every connected non-basic graph of minimum degree 3 to 9
    vertices) is the small-instance check; cite its counts in the file
    header.
  - **Deliverable.** The file; §7 of the report with the case table (which
    lemma covers which of the paper's paragraphs); `#print axioms` lines.
  - **Regenerate.** `cd lean && lake build`; `make -C paper1/latex axioms`.
  - **Kill criterion.** None. If the item cannot finish all cases, it
    proves the non-regular cases and states the regular case
    (`step_regular`) as a lemma whose proof is the one gap, named in
    PROGRESS.md; item 08 then takes `S1` as a hypothesis of its theorem
    (`(hstep : ∀ data : StepData, 1 + potentialMinus data.G* ≤ potentialMinus data.G)`)
    and says so. No `sorry`.
  - **Size range.** Not applicable (checked to 9 in item 02).
  - **Does not claim.** The existence of `X` (item 08); anything about
    pathwidth.

- [x] **08 Lean (iv-b): Theorem 3.2 — the reduction theorem by induction.**
  - **Question.** Does the induction on the support size assemble, from
    items 05–07, the statement: for every `G` with `IsSPReduced G` there
    are `X ⊆ support G` and `B` with `SPReduces (G.deleteVerts X) B`
    (deletion = iterated `isolate`), `B ≠ ⊥`, `IsSPReduced B`, `IsBasic B`
    and `|X| + potentialMinus B ≤ potentialMinus G`?
  - **Method.** New file `lean/MOSPFormalization/DegreeBound/ReductionTheorem.lean`,
    importing `Step`. Strong induction on `(support G).card`. Cases as the
    paper's (p. 9): `G = ⊥` is excluded by the statement (require
    `G ≠ ⊥`; the paper's "if `n < 4` there is nothing to prove" becomes
    "a reduced non-empty graph has a component with at least 4 vertices");
    basic: `X = ∅`, `B = G`; disconnected: split off one component `C`
    (`reachSet`-style finset of the support), `G = G|_C ⊔ G|_{Cᶜ}` as
    graphs on `V`, apply the hypothesis to both (each has a smaller
    support), union the `X`s, `SPReduces` on a disjoint union from
    `SPReduces` on each part (a lemma: steps inside `C` commute with the
    other part — immediate from the operations touching only `v` and its
    neighbours), `potentialMinus_add` from item 05; connected non-basic:
    `w` as in item 07 (`Finset.exists_max_image` for `Δ`, then the
    tie-break among max-degree vertices), `G* ` from `exists_reduced_reduct`,
    the hypothesis on `G*` gives `X*, B`, set `X = insert w X*`, and
    `SPReduces (G.deleteVerts X) B` from R4 (`X* ⊆ support G*` is disjoint
    from the vertices the reduction `G − w →* G*` acted on, since those
    are isolated in `G*`), and the inequality from S1. State **T1**
    `exists_reduction_set`. Also the corollary used by item 09:
    `IsBasic B → every component is cubic or second-kind`, and
    `potentialMinus_basic_component` (cubic: `= N/6 − 1/6`; second kind:
    `≥ 5/6`, with `N ≥ 5` from `Δ ≥ 4`). Before stating: item 02's T1
    check through Algorithm X.
  - **Deliverable.** The file; §8 of the report; `#print axioms` lines.
  - **Regenerate.** `cd lean && lake build`; `make -C paper1/latex axioms`.
  - **Kill criterion.** None. If item 07 left `S1` as a hypothesis, this
    theorem carries it as `(hstep : …)` and the report's table marks
    Theorem 3.2 "proved modulo the regular-case lemma"; if item 06 left
    R3–R4 out, the conclusion is stated with the named `Prop`
    `ReductionConfluence` as PROGRESS.md of item 06 prescribed.
  - **Size range.** Not applicable.
  - **Does not claim.** Anything about pathwidth; uniqueness of `X`.

- [x] **09 Lean (iv-c, vi): the pathwidth assembly under the named hypotheses, Corollary 5.2's form, the axiom check.**
  - **Question.** With `CubicPathwidthBound τ` and `ReductionPathwidthBound ρ`
    as named `Prop`s, does Lemma 5.1's assembly go through, giving
    `pw(G) ≤ f⁻(G) + τ(n) + 2ρ(n) + 1` for reduced `G` and
    `pw(G) ≤ Σ_v g(deg_{B}(v)) + τ(n) + 3ρ(n) + 1` for every `G` and every
    reduced reduct `B` of `G` (hence for the histogram of `G` itself)?
  - **Method.** New file `lean/MOSPFormalization/DegreeBound/Pathwidth.lean`,
    importing `ReductionTheorem`, `CutLemma` (not needed by the proof;
    imported so one file closes the development), `TreeBound`, `Minor`.
    `def CubicPathwidthBound (τ : ℕ → ℚ) : Prop := ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected → (∀ v, G.degree v = 3) → (pathwidth G : ℚ) ≤ (Fintype.card V : ℚ) / 6 − 1/6 + τ (Fintype.card V)`
    with its docstring quoting the paper's sentence (plan §0.2, Section 5:
    "Hence for 3-regular graphs, there is a function `τ`, with `τ(n) = o(n)`,
    such that `pw(G) ≤ n/6 − 1/6 + τ(n) + O(log n)`") and Fomin & Høie's
    Theorem 5 verbatim; `def ReductionPathwidthBound (ρ : ℕ → ℚ) : Prop := ∀ (V : Type) … (G H : SimpleGraph V) …, SPReduces G H → (pathwidth G : ℚ) ≤ pathwidth H + ρ (Fintype.card V)`
    with the docstring quoting "It follows from the results of [21] that …
    `pw(G − X_G) = pw(r(G − X_G)) + O(log n)`" and "series-parallel graphs
    … The pathwidth of these graphs is `O(log n)`", and the note that
    Kneis et al. 2009 is not held. Neither is asserted anywhere. Lemmas:
    `pathwidth_basic_le`: for `IsSPReduced B`, `IsBasic B`, `B ≠ ⊥`, under
    the two hypotheses (monotone budgets), `pathwidth B ≤ potentialMinus B + τ n + ρ n + 1`
    — by `pathwidth_induce_le_of_forall_connected` over the components
    (cubic: H1 on the induced graph, transported by `pathwidth_eq_of_iso`
    or stated on `G.induce C` directly; second kind:
    `pathwidth_le_pathwidth_erase_add_one` then H3 to `⊥`, `pathwidth ⊥ = 0`,
    and `potentialMinus ≥ 5/6 ≥ 0`); `pathwidth_deleteVerts_le`:
    `pathwidth G ≤ pathwidth (G.deleteVerts X) + |X|` (from
    `pathwidth_le_pathwidth_induce_add_card_compl` and `pathwidth_mono`,
    since `G.deleteVerts X ≤ G` and equals `G` on `Xᶜ`); **A1**
    `pathwidth_le_potentialMinus_of_hypotheses`: `pathwidth G ≤ potentialMinus G + τ n + 2 ρ n + 1`
    for `IsSPReduced G`, `G ≠ ⊥`, from T1 (`|X| + f⁻(B) ≤ f⁻(G)`), H3 on
    `SPReduces (G − X) B`, and `pathwidth_basic_le`; **A2**
    `pathwidth_le_degreeSum_of_hypotheses`: for every `G ≠ ⊥` and reduced
    reduct `B`, `pathwidth G ≤ Σ_v g (B.degree v) + τ n + 3 ρ n + 1`
    (`potentialMinus ≤ potential`), and `pathwidth_le_histogram_of_hypotheses`:
    `≤ Σ_v g (G.degree v) + τ n + 3 ρ n + 1` by R2 and `g_mono`. Then (vi):
    `#print axioms` for every theorem of the seven files in
    `paper1/axiom_check.lean`, expecting `[propext, Classical.choice, Quot.sound]`
    (the hypotheses are arguments, not axioms); `make -C paper1/latex axioms`;
    the sandwich stage's `DEGREE_BOUND_PROVED` list completed; a numerical
    pin: on 500 random graphs at `n ≤ 12`, `pw ≤ Σ_{r(G)} g + B(n)` with
    item 02's measured `B(n)` (a consistency check of the pipeline, not of
    the theorem, whose budgets are abstract). Before stating A1–A2: item
    02's A1–A2 budget measurement is the small-instance check.
  - **Deliverable.** The file; §9 of the report (the two named `Prop`s
    verbatim with their quotations, the theorem statements, the axiom
    lines, the table "what is proved / what is cited"); the Appendix A rows
    drafted for item 10 (`\leanentry{degreebound}{…}\leannames{…}`, not
    yet in the paper); `reports/scratch/edwards_mcdermid/09_assembly/{lake_build.log, axiom_check.log, sandwich.log}`.
  - **Regenerate.** `cd lean && lake build`; `make -C paper1/latex axioms`; `python -m learning.sandwich --stage degree_bound`.
  - **Kill criterion.** None. If an upstream item left a gap, the theorem
    carries it as a hypothesis and the report's table says exactly which
    hypotheses the final theorem has beyond H1 and H3.
  - **Size range.** Not applicable.
  - **Does not claim.** H1 or H3 (cited, named, never asserted); Theorem
    5.3 (the averaging lemma is Edwards & Farr's; verified in item 01
    only); any value of `τ` or `ρ`.

- [ ] **10 The write-up: the report's summary, the paper's paragraph, the survey's sentence, the `CLAUDE.md` paragraph.**
  - **Question.** D of the brief. One document a reader can follow, and the
    texts the owner will place.
  - **Method.** (a) `reports/edwards_mcdermid.md` §0, a two-page opening:
    the statement (Corollary 5.2 verbatim, page), the verification tables
    in one table (per source: graphs, max deficit, share with deficit `≤ 0`,
    `B(n)` at three sizes; the Poisson check at `n = 120`; the cubic
    measurement), the Lean chain as a table — statement, Lean name, file,
    status (*proved*; *proved under* H1/H3; *cited, named Prop*; *verified
    numerically, not formalised* for Theorem 5.3; *stated, not proved* for
    Fomin–Høie's Lemma 4 and the sweep), what is conditional on what in one
    sentence ("every theorem of `DegreeBound/` depends on standard axioms
    only; the two results of the literature enter as named hypotheses `τ`
    and `ρ`, and the bound's lower-order term is `τ(n) + 3ρ(n) + 1`"), the
    kill verdicts in one table, "What this is not" and "Open"; then §1–§9
    edited for one voice. (b) The paper: in
    `paper1/latex/sec9e_appendix_random.tex`, at the two places that cite
    `EdwardsMcDermid2015`, at most half a page in total: that the bound
    was evaluated on every graph of the record with the main-term slack
    reported and the lower-order term made explicit; that Lemma 5.1 and
    Corollary 5.2 are formalised in Lean conditional on the cubic base case
    and the reduction lemma, each a named hypothesis; the explicit form of
    the lower-order term; the Appendix A rows (`sec9a_appendix_lean.tex`)
    and axiom lines (`make -C paper1/latex axioms`); references with
    checked DOIs (`paper1/latex/check_refs.py`) for Edwards & McDermid 2015
    (already present), Fomin & Høie 2006, Kneis et al. 2009, Edwards & Farr
    2012, Monien & Preis 2006. Wording: "this is a formalisation of a
    published theorem"; "we found no prior statement" only if something
    here is new (the explicit budget accounting `τ + 3ρ + 1` is a reading
    of the paper, not a result; say "made explicit"); a measurement is
    never called a theorem. (c) The survey: one sentence for
    `reports/random_graph_pathwidth_survey.md` §1.4 and one for §7(a)'s
    table note, drafted in the report's §"For the survey" — do not edit
    the survey if the branch `appendix-picture` has its own edits pending
    (it does; say so and leave the sentence drafted). (d) The `CLAUDE.md`
    paragraph the owner will need, in the format of the existing "The
    excess phase diagram" paragraph (CLAUDE.md line 1340), written into
    `reports/edwards_mcdermid.md` §"For CLAUDE.md"; do not edit `CLAUDE.md`.
    (e) `reports/random_graph_pathwidth_literature_2.md` is on another
    branch: list in the report the two lines there that this loop
    supersedes (its "Not verified" entry for the displayed equality and
    the Poisson evaluation's assumption), for the owner to carry over at
    the merge.
  - **Deliverable.** The report; the paper builds (`make -C paper1/latex`
    then `make check`), page count before and after recorded; the gate
    passes.
  - **Regenerate.** `make -C paper1/latex && make -C paper1/latex check`.
  - **Kill criterion.** None.
  - **Size range.** As stated per claim.
  - **Does not claim.** Beyond what the items proved, measured or cited.

- [ ] **11 Reserve.** The best remaining gap from items 01–10, one session,
  chosen in this order of value and stated in PROGRESS.md with the reason:
  (1) a Lean gap left by 06–09 (R3–R4, the regular case of S1, C2); (2)
  Fomin–Høie's Lemma 4 in Lean for maximum degree 3 — the statement with
  `X` as the end bag, `tree_pathwidth_le_log` as its tree case, the three
  cases of its proof — which with C1 and a stated Monien–Preis bisection
  would make the base case itself conditional only on the bisection
  theorem; (3) the per-step `pw(H) ≤ pw(H') + 1` for one series-parallel
  operation (unconditional, cheap, and *not* the reduction lemma — say so),
  with the measured `pw(H) − pw(r(H))` of item 02 extended to 10 vertices;
  (4) Theorem 5.3's averaging lemma fetched from Edwards & Farr 2012 (EJC,
  open) and checked on the record. Compute at most 1 core-hour; nothing
  proved is re-solved.
