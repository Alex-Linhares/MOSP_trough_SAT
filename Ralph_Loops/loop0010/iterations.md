# loop0010 — a one-parameter theory of MOSP in the excess: items

The parameter is the **excess** `e = (n_ones − m) / n` of an instance with
`n` customers, `m` patterns and `n_ones` ones: the mean number of patterns per
customer minus one, `r (c − 1)` for `r = m / n` and `c` customers per pattern.
The incidence graph `B` (customers and patterns as vertices, a one as an edge)
has cyclomatic number `γ = n_ones − n − m + κ` (`κ` components), so
`γ / n = e − 1 + κ / n`. Three lines of constant excess are on record:
`e = 1`, where the first-moment lower bound turns on (`β*(d, μ) > 0` iff
`μ (d − 1) > 1`, `reports/scratch/clique_cover_moment/REPORT_generator.md` §3);
`e ≈ 2–2.4`, the hardness ridge (`reports/ml_nature.md` §25, §36); and the
giant component of `B` at `e_g(r) = (√(r² + 4r) − r) / 2` (0.62 at `r = 1`;
§36 (a)). Industry (SCOOP) sits at median 1.35, the Chu & Stuckey `d = 2`
classes at 1.6–2.0, `d = 4` at 3.0–3.6 (`learning/data/instances.csv`).

Phase 1 (01–04) measures; phase 2 (05–10) analyses; 11 is Lean; 12 writes;
13 is the reserve. Every item: one session, `nice -n 19`, at most 8 workers
(4 if the one-minute load in `uptime` is above 24), nothing solved twice.

- [x] **01 The map: every instance on record placed by its excess.**
  - **Question.** Where does every instance we hold sit in the excess, how
    far is each from an incidence forest, and do the three lines (`e_g`, 1,
    the ridge) separate the collections?
  - **Method.** New module `learning/excess.py`. For every instance of the
    corpus (6,376, through `learning.dataset` / `learning/data/instances.csv`
    and the files under `benchmarks/instances/`), the four ensemble frames
    (`learning/data/ensemble/results.csv`, `results_upward.csv`,
    `results_ratio.csv`, `results_height.csv`; regenerate each instance from
    its seed with `learning.ensemble.generate(Cell.parse(...), index)`, never
    re-solve) and the 7,200 generator simulations of
    `reports/scratch/clique_cover_moment/floor_violation.csv` (witnesses in
    `sim_solutions/`): `n`, `m`, `n_ones`, `e`, `r = m / n`, `c = n_ones / m`,
    the incidence graph's `κ`, `γ`, `γ / n`, the size of its largest
    component as a fraction, whether it is a forest (`γ = 0`), the size of
    its 2-core (`learning.cover_excess.peel(matrix, 2, 2)`), and the
    certified optimum where there is one. Write `learning/data/excess.csv`
    (one row per instance; git-ignored if above 5 MB, with a regenerate
    command). Then the tables: per collection (SCOOP, Faggioli–Bentivoglio,
    Chu & Stuckey by class, Harvey, Simonis, Shaw, Wilson, Miller, Challenge)
    the quantiles of `e`, `γ / n`, the forest share and the 2-core share; the
    same per ensemble series `(generator, r, param, n)`; and, against the
    prediction, the largest-component fraction of `B` as a function of `e`
    per `r`, with `e_g(r)` marked. Also: the 338 bound-gap instances of §6
    (`learning/data/bound_gap.csv`, regenerate with
    `python -m learning.bound_gap --workers 8` if missing) — their `e` and
    `γ / n` against the rest of the corpus at equal size.
  - **Deliverable.** `learning/excess.py` with `python -m learning.excess`
    (≤ 10 min on 8 workers), `learning/data/excess.csv`, tests
    (`tests/test_excess.py`: `e`, `γ`, `κ` by hand on three small matrices,
    a forest and a non-forest, and `e = r (c − 1)` as an identity), and
    `reports/excess_phase_diagram.md` §1 "The map", every table in full,
    with the regenerate command.
  - **Kill criterion.** None; descriptive. One stated check: the measured
    largest-component fraction of `B` must cross 0.5 within ±0.15 in `e` of
    `e_g(r)` for every ensemble series at `n ≥ 50`; if it does not, say so
    and do not use `e_g` later.
  - **Size range.** 9–134 customers (corpus), 10–100 (ensembles).
  - **Does not claim.** Anything about the optimum; the map is a
    description of the instances we happen to hold.

- [x] **02 `opt / n` against the excess: one parameter, or two?**
  - **Question.** B(i) and B(iii) of the plan. On random clique covers, is
    `lim opt / n` a function of `e` alone, or of `(d, μ)` separately? And how
    far is the two-key closing rule from the exact optimum as a function of
    `e`?
  - **Data.** The ~50,700 certified random covers already on record (the
    four ensemble frames of item 01: fixed `d` and Bernoulli `p`, `m / n ∈
    {1/8, 1/4, 1/2, 1, 2, 4, 8}`, `n = 10–100`) and the 200 Chu & Stuckey
    instances. **No instance is solved again.** The one new computation is
    the two-key rule (`satisfiability.heuristics.two_key_rule`, registered
    2026-09-27, after the campaign ran, so the frames lack it) on every
    instance: about 1 ms each, a scoring run, written to
    `learning/data/excess_rule.csv`, never to the compute ledger.
  - **Method.** (a) Per series `(generator, r, param)` with three or more
    `n`, fit `opt = a + b n` (the form of §12 and
    `reports/random_intersection_pathwidth.md` §3) and report `b` with its
    standard error; the realised `e` of the series (mean over instances;
    the repairs inflate it, so never the nominal `r (d − 1)`). (b) The
    one-parameter test: pair series whose realised `e` agree within ±0.05
    but whose `(d, μ)` differ (the fixed generator has `e = 2` at `(3, 1)`,
    `(5, ½)`, `(2, 2)`, `(9, ¼)` and `e = 3` at `(4, 1)`, `(7, ½)`, and `(12, ¼)` at 2.75,
    all on record at `n = 50–75`); compare slopes. (c) The first-moment
    constant `β*(d, μ)` from the quenched exponent of
    `reports/scratch/clique_cover_moment/asymptotic_cs.py` (move that code
    and `bound_lib.py`'s finite floor into a new `learning/first_moment.py`
    with tests reproducing `asymptotic_cs.log` and `finite_bound_cs.log` to
    the printed digits), evaluated at each series' realised size histogram,
    beside `b`. (d) The rule: `(rule − opt)` and `rule / n` per series and
    per `e` bin; exactness share; worst case. (e) A figure: `b`, the rule's
    `width / n` at the largest `n`, and `β*` against `e`, one marker per
    series, coloured by `r`. Read the dataviz skill before drawing it.
  - **Deliverable.** `learning/first_moment.py` (with tests),
    `learning/excess.py` extended (`--stage rule`, `--stage slopes`),
    `learning/data/excess_rule.csv`, `reports/figures/excess_opt.png`,
    `reports/excess_phase_diagram.md` §2 with the regenerate commands.
  - **Kill criterion.** The hypothesis "a function of `e` alone" is dead if,
    on at least half of the `e`-matched pairs in (b), the slopes differ by
    more than twice the larger standard error. Either outcome is the
    finding; record which.
  - **Size range.** `n = 10–100`; slopes fitted on `n ≥ 30`.
  - **Does not claim.** A limit: `pw / n` falls with `n` at every fixed
    density to 75 and §14 showed `n ≤ 40` constants fail at 125; `b` is a
    finite-range slope. The rule is a heuristic, not a bound.

- [x] **03 The forest regime, by brute force.**
  - **Question.** A, first half. When the incidence graph is a forest the
    MOSP graph is a block graph whose blocks are the pattern cliques. What is
    its pathwidth as a function of the largest pattern `ω` and the shape of
    the forest — additive in `ω` and a depth, or multiplicative?
  - **Method.** (a) *Clique trees* `CT(s, h, b)`: one clique `K_s`; every
    customer of every clique at depth below `h` is the hub of `b` new cliques
    of size `s` (the `b = 2`, `s = 2` case is the tree the branch lemma
    `Sandwich.lean: branch_lemma` bites on). Exact pathwidth of every
    `CT(s, h, b)` with `s ∈ {2, 3, 4, 5}`, `h ∈ {1, 2, 3}`, `b ∈ {1, 2, 3}` and
    at most 400 vertices, by the C program `pathwidth_solver/cli/pathwidth`
    (graph6 on stdin, `-t 600`, `nice -n 19`; `networkx.to_graph6_bytes`);
    censored runs are intervals, never values. (b) *Random block trees*: start
    from one pattern, attach a new pattern of random size (Chu & Stuckey's
    size law at `d ∈ {2, 3, 4}`, `REPORT_generator.md` §1.2) at a uniformly
    random existing customer; `n ≤ 120`, 50 instances per `(d, n)`; and the
    forest instances item 01 found (corpus and ensembles, by `γ = 0`), which
    carry certified optima. (c) Candidates, each as a function computable
    from the forest: `ω − 1` (the floor), `ω − 1 + pw(B)` (additive, `B` the
    incidence tree, its pathwidth by the C program), `ω − 1 + h`, the blow-up
    bound `ω · (pw(B) + 1) − 1`, the TreeBound form
    `ω · (tb(n + m) + 1) − 1` with `tb(N)` the least `k` with
    `N ≤ (5·3^k − 3)/2` (`reports/scratch/tree_bound/compare_bound.py`), and
    the caterpillar-of-cliques test (a chain of `s`-cliques with a pendant
    `s`-clique at every non-shared customer), where the additive form and
    the multiplicative form differ most. Report, per candidate, violations
    (a value below the exact pathwidth, for a would-be upper bound), the
    exact share and the mean slack. (d) A literature check before any
    proof: pathwidth of block graphs — search for an exact or polynomial
    result (the survey `reports/random_graph_pathwidth_survey.md` and
    `paper1/ijoc_literature.md` first, then OpenAlex); record what is found
    with the source, or "we found no prior statement".
  - **Deliverable.** `reports/scratch/forest_regime/` (scripts, graph6
    files, logs, the exact values as CSV) and
    `reports/excess_phase_diagram.md` §3 with the table of `CT(s, h, b)`
    values and the verdict on each candidate. ≤ 6 core-hours.
  - **Kill criterion.** If no candidate of the form `α (ω − 1) + β·h + γ`
    with small integer constants fits every `CT(s, h, b)` value exactly, the
    additive theorem is dropped and item 06 proves the blow-up bound only.
  - **Size range.** ≤ 400 vertices for the clique trees, ≤ 120 customers
    for the random block trees.
  - **Does not claim.** A theorem. These are exact values on a family; the
    proof is item 06.

- [x] **04 Industrial instances: the 24 SCOOP instances in the excess.**
  - **Question.** F, measurement half. For each industrial instance: its
    excess, cyclomatic number, certified optimum, the deterministic lower
    bound, the first-moment floor it would have as a random cover of its
    size law, the two-key rule's value, and what the certification cost.
  - **Method.** The 24 SCOOP instances (`benchmarks/instances/MOSP_Instances/
    SCOOP/`, all certified in `solutions/`), and, as the structured but not
    industrial comparison, the 300 Faggioli–Bentivoglio instances (the
    README under `benchmarks/instances/MOSP_Instances/` says how they were
    generated; quote it). Per instance: `n`, `m`, `n_ones`, `e`, `γ`, `κ`,
    forest or not, 2-core size, `optimum` (from `solutions/`, provenance
    read), `lb_best` and `ub_best` from `learning/data/instances.csv`, the
    rule's value (item 02's CSV), the finite 0.01 floor from the instance's
    own pattern sizes (`learning/first_moment.py`), the nodes and seconds
    of the refutation from `benchmarks/results/compute_ledger.csv` and the
    sweep CSVs (say "not recorded" where the ledger has no row; **do not
    re-run** — these are certified), and the cost model's prediction
    (`learning.cost_model`). Then the one-page statement a planner could
    use, written as a draft of the paper's paragraph: from an order book's
    `(n, m, n_ones)` read `e`; below `e_g(r)` the forest bound of item 03/06
    applies; between `e_g` and 1 the first moment says nothing and the
    deterministic bounds are what there is; above 1 the floor is positive
    and the two-key rule gives a value within the measured margin of item
    02; the certification cost from the cost model with its stated decade
    of error. Every number with its source.
  - **Deliverable.** `reports/excess_phase_diagram.md` §4 (the table in
    full, the statement), `learning/data/excess_scoop.csv`.
  - **Kill criterion.** None. One check: every optimum must sit at or above
    its 0.01 floor (it is a random-model statement, so a violation is not a
    contradiction, but it must be reported).
  - **Size range.** 13–134 customers.
  - **Does not claim.** That 24 instances from one source are "industry";
    say "24 instances from the SCOOP set, all under excess 2.5". No new
    certification.

- [ ] **05 `β⁺` by simulation: the width of explicit constructions at large `n`.**
  - **Question.** B(ii), first half. For the random cover model at fixed
    `(d, μ)`, what width per customer do explicit layouts reach as `n`
    grows: the two-key closing rule, the BFS-layer layout, the
    independence-number bound and the greedy independent set, and the
    edge-count bound?
  - **Method.** Fresh random covers from `benchmarks.generator.
    generate_structured_instance(n, m, d, seed)` (fixed sizes) and from the
    fitted Chu & Stuckey generator (`reports/scratch/clique_cover_moment/
    gen_candidates.py`, the best-fit family: Bernoulli, customers padded to
    ≥ 1, patterns to ≥ 2, disconnected discarded), at `(d, μ)` on the grid
    `d ∈ {2, 3, 4, 6, 8, 10}`, `μ ∈ {½, 1, 2}`, `n ∈ {100, 200, 500, 1000,
    2000, 5000}`, 10 instances per cell (fewer at 5000 if the rule is slow:
    it is `O(n²)` in Python with popcounts; time it at 1000 first). **No
    exact solve**; nothing here is certified. Per instance: the rule's
    width (`two_key_rule`), the BFS layout's vertex separation (layers of
    the MOSP graph from a random root, listed layer by layer; the
    separation computed exactly from the neighbour masks; also the bound
    `max_i (|L_i| + |L_{i+1}|) − 1`), `n − α_greedy` (greedy independent set
    by minimum degree; `IndependenceBound.lean`'s `pathwidth_le_card_sub_indepNum`
    makes `n − α` an upper bound on pathwidth), and the edge-count bound
    `|E| / 5.769` of the survey §1.4 (cite as the survey does). Fit
    `width / n = β⁺ + a / n` per construction and cell; compare with item
    02's slope `b` at `n ≤ 100` and with `β*(d, μ)`.
  - **Deliverable.** `learning/excess.py --stage constructions`,
    `learning/data/excess_constructions.csv`, `reports/figures/
    excess_beta_plus.png`, `reports/excess_phase_diagram.md` §5: a table of
    `β⁺` per construction and cell with `β*` and `b` beside it. ≤ 8
    core-hours at `nice -n 19`.
  - **Kill criterion.** The extrapolation is not trusted — and later items
    may not quote it — for any cell where the rule's `width / n` at the
    largest `n` and item 02's slope at `n ≤ 100` differ by more than 0.03.
  - **Size range.** `n = 100–5000`.
  - **Does not claim.** A limit or a bound: the rule's number is measured;
    only `n − α` and the edge-count bound are proved upper bounds, and only
    at the `n` where they were computed.

- [ ] **06 The forest regime, on paper.**
  - **Question.** A, second half: the theorem item 03's data supports.
  - **Method.** State and prove, in `reports/excess_phase_diagram.md` §6
    in the style of `reports/random_graph_first_moment.md` (every step a
    numbered lemma, every inequality named):
    *Theorem F1 (blow-up).* If the incidence graph `B` of `M` is a forest,
    then `pw(G_M) ≤ ω · (pw(B) + 1) − 1`, where `ω` is the largest pattern:
    take a path decomposition of `B`, replace every pattern node by its
    customers; a customer's nodes in `B` (itself and its patterns) form a
    star, so its bags stay an interval; every edge of `G_M` lies in a
    pattern. With `TreeBound.lean`'s `tree_pathwidth_le_treeBound` on each
    component, `pw(B) ≤ tb(n + m)`, hence
    `MOSP(M) ≤ ω · (⌊log₃((6(n + m) + 3) / 5)⌋ + 1)`.
    *Theorem F2 (the sharper form)*, only if item 03 found an exact fit:
    state it, prove it by the path and centroid lemmas of `TreeBound.lean`
    adapted to blocks, and give the extremal family. If item 03 killed the
    additive form, state instead the lower bound the branch lemma gives on
    `CT(s, h, 2)` and the gap to F1, and say the truth is between.
    *Before any statement is called a theorem, check it by brute force* on
    every `CT(s, h, b)` and random block tree of item 03 and on every
    forest instance of item 01 (`learning/excess.py --stage forest_check`):
    two earlier `sorry`s hid false statements (`CLAUDE.md`, "Lessons that
    cost sessions").
    Then the random-model consequence, stated as a corollary with its
    hypothesis explicit: below `e_g(r)` the largest component of `B` is
    `O(log n)` whp (cite Molloy–Reed / the configuration-model result §36
    used, by name and page from a held copy, else "not verified"), so
    `MOSP = O(ω · log log n)` on random covers there, with the non-giant
    components handled by F1 and the sizes by the survey §2 argument.
  - **Deliverable.** §6 of the report with the proofs; the forest check's
    log; the exact Lean-ready statements listed for item 11.
  - **Kill criterion.** If the brute-force check finds a counterexample to
    F1 as stated, the item stops with the counterexample drawn and the
    statement withdrawn.
  - **Size range.** The check covers item 03's sizes; the theorem is for
    every instance with a forest incidence graph.
  - **Does not claim.** Tightness of F1 (it is a factor `ω` loose on chains
    of cliques); anything above `e_g(r)` for random instances.

- [ ] **07 `β⁺` on paper: the provable constructions analysed.**
  - **Question.** B(ii), second half. An explicit upper constant
    `β⁺(d, μ)` for the random cover model, with a proof or a precisely
    stated conjecture, from the constructions whose width is analysable.
  - **Method.** Two constructions, in this order, in `reports/
    excess_phase_diagram.md` §7. (a) *The BFS layer layout.* Deterministic
    lemma: for any graph and any BFS layering `L_0, L_1, …`, the layout
    that lists the layers in order has vertex separation at most
    `max_i (|L_i| + |L_{i+1}|) − 1` (check on 1,000 random graphs before
    stating). Random part: the layer fractions `x_i` of the MOSP graph of
    a random cover follow the two-type exploration recursion (customers
    → patterns of size `d` → customers), the analogue of
    `x_{i+1} = u_i (1 − e^{−c x_i})`, `u_{i+1} = u_i − x_{i+1}` for
    `G(n, c/n)`; derive it, and state `β⁺_BFS(d, μ) = max_i (x_i + x_{i+1})`
    as the limit, with the concentration step cited (Wormald's
    differential-equation method, or the branching-process coupling of the
    exploration process; from a held copy, else marked "not verified").
    (b) *The greedy independent set.* `pw ≤ n − α` is a theorem
    (`IndependenceBound.lean`); the minimum-degree greedy independent set
    of the random cover is a Karp–Sipser-type process whose yield has a
    known differential-equation limit for `G(n, c/n)` (cite from a held
    copy); derive the analogue for the cover model or, if the derivation
    does not fit the session, state the recursion as a conjecture with the
    simulation of item 05 as its check. Define `β⁺(d, μ)` as the smaller of
    the two and tabulate it beside `β*(d, μ)`, item 02's `b` and the rule's
    measured width on the item 05 grid. Say in one paragraph why the rule
    is not analysed: it is a greedy with state (the opened set), and no
    exploration-process description of it is on record.
  - **Deliverable.** §7 of the report with the derivations and the table;
    a script `reports/scratch/beta_plus/recursion.py` evaluating both
    recursions and comparing them with item 05's simulation at every cell
    (relative error reported).
  - **Kill criterion.** If `β⁺(d, μ) − β*(d, μ) > 0.5` at every cell of the
    grid, the analytic constant is recorded as uninformative and the gap is
    attributed to the constructions, not to the analysis; no further
    analysis item is added.
  - **Size range.** Recursions checked against simulation at `n = 100–5000`.
  - **Does not claim.** That `β⁺` is near the truth; that the concentration
    step is re-proved here.

- [ ] **08 The structured count: can a richer first moment lift `β*`?**
  - **Question.** C. The first moment over single empty pairs gives
    `β*(d, μ)`, 0.06–0.10 below the certified `opt / n` at 125 × 125. A
    layout of width `k` has an empty pair at *every* position, nested
    (`A_i ⊂ A_{i+1}`, `R_i ⊃ R_{i+1}`). Does the first moment over `ℓ`
    nested empty pairs at positions spaced `n / (ℓ + 1)` apart give a
    larger constant?
  - **Method.** In `learning/first_moment.py`: the expected number of
    `ℓ`-nested empty pairs with the sizes a width-`k` layout forces at the
    chosen positions, exactly for the cover model given sizes (the
    per-pattern factor is the probability that a `d`-set avoids every one
    of the `ℓ` forbidden `A_i × R_i` crossings, by inclusion–exclusion over
    the `2ℓ + 1` cells of the partition; the cells are disjoint, so it is
    a single multinomial count), and its exponent at `m = μ n`; `β*_ℓ` as
    the root; `ℓ = 1` must reproduce `β*`. Evaluate at `(d, μ) ∈ {2, 3, 4,
    6, 8, 10} × {½, 1, 2}` for `ℓ ≤ 4`, and the finite-`n` floor at
    `ℓ = 2` on the 200 Chu & Stuckey instances against the certified optima
    (zero violations required). Beside it, the *diagnostic*: the second
    moment of the single-pair count `X` at `(6, 1)`, `n = 125`, by
    simulation (`E[X²] / E[X]²` over 2,000 instances), to say whether the
    slack is in the union bound (pairs are correlated, `X` is concentrated
    away from 0) or in the necessary condition (empty pairs exist on
    instances whose pathwidth is larger). State plainly that a second
    moment bounds `P(X > 0)` from below and cannot lift `β*` by itself.
  - **Deliverable.** `learning/first_moment.py` extended with tests
    (`ℓ = 1` equals the old constant at every grid point; the finite count
    matches a brute-force enumeration at `n ≤ 7`, `ℓ = 2`), the table of
    `β*_ℓ`, and `reports/excess_phase_diagram.md` §8.
  - **Kill criterion.** If `β*_ℓ(6, 1) − β*(6, 1) < 0.03` for every
    `ℓ ≤ 4`, stop: the structured count does not pay, and the report says
    where the slack is by the diagnostic.
  - **Size range.** Asymptotic constants; the finite check at 30–125.
  - **Does not claim.** The constant: a first moment is a lower bound on
    the truth whatever `ℓ`.

- [ ] **09 The ridge mechanism: one hypothesis, one test.**
  - **Question.** D. §36 found the ridge is where the number of closed
    sets reachable through fitting steps peaks, and could not say where
    that is in terms of the generator. Test: **H1, the ridge is where the
    gap between the exact optimum and the first-moment floor is largest.**
  - **Method.** For every ensemble series of item 02 at `n ∈ {50, 60, 75}`
    (25 series, `m / n ∈ {2, 1, ½, ¼, ⅛}`, both generators — §25's peaks to
    the digit through `learning.ridge_theory.load_frames`): per cell the
    mean of `(opt − floor_{0.01}) / n` with the floor from each instance's
    own sizes (`learning/first_moment.py`, finite form, as
    `finite_bound_cs.py`), and of `(opt / n − β*)` with the asymptotic
    constant at the cell's size law; the cell where each peaks, interpolated
    in `log10 col_mean` as §25 (b) does, against §25's node-count peak and
    its bootstrap interval. Score as §25 (d): `|log10(predicted /
    measured)|` per series, mean and worst. Secondary (not a kill): at
    `n = 20`, 150 instances per cell of the `m ∈ {n, 2n}` campaign, the
    number of optimal closing orders under the construction value
    (`learning.degeneracy.lattice_counts`, exact), its cell median against
    the node peak — §8 found the share tracks `opt / n` (ρ 0.70) at
    `n ≤ 15`, which predicts monotone, not peaked.
  - **Deliverable.** `learning/excess.py --stage ridge`, the two tables,
    `reports/excess_phase_diagram.md` §9, the figure
    `reports/figures/excess_ridge.png` (peak locations per series, both
    quantities and the nodes).
  - **Kill criterion.** H1 is dead if the gap's peak lies outside the node
    peak's bootstrap interval on more than half of the 25 series, or if its
    mean score exceeds 0.15 decades. Either way the section records the
    numbers; a dead H1 is a result.
  - **Size range.** `n = 50–75` for H1; `n = 20` for the secondary.
  - **Does not claim.** A mechanism. A coincidence of peaks on 25 series is
    evidence for one; the derivation of the reachable count in the random
    model is the open problem §36 named, and this item does not attempt it.

- [ ] **10 Validity under the real generator, on paper.**
  - **Question.** E. The first-moment inequality assumes patterns uniform
    given their sizes; the fitted Chu & Stuckey generator pads short
    patterns and empty customers and rejects disconnected instances
    (`REPORT_generator.md` §1.3). Measured: the repairs make empty pairs
    rarer (§2.1), 7,200 instances with zero floor violations (§2.2). What is
    proved?
  - **Method.** Write `reports/excess_phase_diagram.md` §10 with: (a) the
    exact bound on the *pre-repair* Bernoulli matrix,
    `P(pair empty) = [(1 − p)^t + (1 − p)^{t−1} − (1 − p)^{2t−1}]^m`, a
    product of independent patterns; (b) the monotone coupling: fix the
    auxiliary randomness of the repairs as a list of candidate additions,
    so the padded matrix is a superset of the unpadded one for every
    outcome; an empty pair of the padded matrix is an empty pair of the
    unpadded one; hence the first-moment bound with Bernoulli sizes holds
    for the padded matrix; (c) the rejection: write out whether "the MOSP
    graph of the padded matrix is connected" is an increasing event of the
    Bernoulli entries under the coupling of (b) — **it need not be**, since
    the pads depend on the base — and give the two bounds that are
    rigorous regardless: the trivial `P(pw ≤ k | accepted) ≤ P(pw ≤ k) /
    P(accepted)`, with `P(accepted)` measured per class (from the fit logs:
    0.005 at the sparse 100 × 50 classes, ≈ 1 at `d ≥ 6`), and Harris–FKG
    where monotonicity does hold (state the exact condition). (d) The
    numerical consequence: the rigorous floors at the 40 classes beside the
    measured-model floors of `finite_bound_cs.log`; the table says where
    the two differ by more than one stack. Every lemma checked on small
    cases by `reports/scratch/validity/check.py` before it is stated (the
    coupling on 10,000 random draws at `n = 8`: the padded matrix is a
    superset in every draw; the empty-pair inclusion in every draw).
  - **Deliverable.** §10 of the report; the check script and log; a
    sentence for the paper replacing "a proof would couple the padded
    instance to the unpadded one" with what is now proved and what is not.
  - **Kill criterion.** If (c) cannot be made rigorous for the rejection,
    the item ends with the `1 / P(accepted)` form and the measured
    acceptance, and says so; that is an acceptable deliverable.
  - **Size range.** The theorem is for every `n`; the check at `n = 8`.
  - **Does not claim.** The inequality with *realised* sizes under the
    generator; that stays measured.

- [ ] **11 Lean: the forest regime.**
  - **Question.** G. Which of items 06, 07 and 10 is within a session in
    Lean, and prove it.
  - **Method.** In order of reach, stop at the first that fills the
    session: (a) **F1's blow-up lemma**: in a new file
    `lean/MOSPFormalization/ForestCover.lean`, imported by
    `lean/MOSPFormalization.lean`: the incidence graph of a `MOSPInstance`
    as a `SimpleGraph (C ⊕ P)`; from a `PathDecomposition` of it of width
    `w`, a path decomposition of `mospGraph M` of width `≤ (w + 1) · ω − 1`
    (bags: the customers of the bag plus the customers of its patterns);
    then, with `TreeBound.lean`'s `tree_pathwidth_le_treeBound` (per
    component via `pathwidth_induce_le_of_forall_connected`), the
    statement `IsAcyclic (incidence M) → mospValue M ≤ ω · (tb (n + m) + 1)`.
    Check the statement numerically first on every forest instance of item
    03 (`learning/sandwich.py` pins Lean definitions to the corpus
    implementations; extend it). (b) The BFS layer lemma of item 07 (a),
    deterministic: `vertexSeparation G ≤ max_i (|L_i| + |L_{i+1}|) − 1` for
    the layer layout. (c) The coupling inclusion of item 10 (b) as a
    statement about finsets: `A ⊆ A' → IsEmptyPair (coverGraph A') X Y →
    IsEmptyPair (coverGraph A) X Y`, which is a two-line monotonicity
    lemma over `CliqueCoverMoment.lean`'s definitions — do this one first
    if (a) looks like more than a session, since it is cheap and the paper
    can cite it.
  - **Rules.** No `sorry`, no `axiom`; `lake build` passes; new theorems in
    the new file only; `paper1/axiom_check.lean` extended; a stated gap is
    acceptable only as a named `Prop` with the obstacle in PROGRESS.md.
  - **Deliverable.** The Lean file; its names and axiom lines in
    `reports/excess_phase_diagram.md` §11; `learning/sandwich.py`'s sorry
    inventory still at zero.
  - **Kill criterion.** None; "blocked with the obstacle" is a deliverable.
  - **Size range.** Not applicable.
  - **Does not claim.** Anything the Lean statement does not say; the
    random-model corollaries stay on paper.

- [ ] **12 The write-up: the phase diagram and the paper's paragraphs.**
  - **Question.** H. One document a reader can follow, and the paper's
    text.
  - **Method.** (a) Assemble `reports/excess_phase_diagram.md`: a two-page
    opening that states the parameter, the three lines, the four regimes
    (`e < e_g(r)`: forests, MOSP `O(ω log log n)` by F1; `e_g ≤ e ≤ 1`: the
    giant component with no first-moment floor; `1 < e ≲ 2.4`: the floor
    turns on, industry and the `d = 2` benchmarks live here, certification
    cost climbs to the ridge; `e > 2.4`: `β*` within 0.06–0.10 of the
    truth, cost falls) with every claim's status — *theorem* (Lean name),
    *proved on paper* (section), *measured* (size range, regenerate
    command), *conjectured* — then the sections items 01–11 wrote, in
    order, edited for one voice; then "What this is not" and "Open". (b)
    The paper: a new subsection of `paper1/latex/sec9e_appendix_random.tex`
    after "The benchmark generator", at most two pages: the excess defined,
    the forest theorem, the `β⁺` constructions, the structured count's
    verdict, the industrial statement (24 instances, named as such), the
    phase-diagram figure as a print vector (regenerate script under
    `paper1/latex/figures/`, test in `tests/test_paper1_latex.py` that the
    figure's numbers come from the CSVs); Appendix A rows and axiom lines
    for every new Lean theorem (`make -C paper1/latex axioms`); references
    with checked DOIs through `paper1/latex/check_refs.py`. Wording:
    "we found no prior statement", never "first"; a measurement is never
    called a theorem; "24 instances", never "industry shows". (c) The
    `CLAUDE.md` paragraph the owner will need, written into
    `reports/excess_phase_diagram.md` §"For CLAUDE.md"; do not edit
    `CLAUDE.md`.
  - **Deliverable.** The report; the paper builds (`make -C paper1/latex`
    then `make check`), page count before and after recorded; the gate
    passes.
  - **Kill criterion.** None.
  - **Size range.** As stated per claim.
  - **Does not claim.** Beyond what the items proved or measured.

- [ ] **13 Reserve.** The best remaining gap from items 01–12, one session:
  a killed item's cheapest surviving variant, a Lean statement left as a
  named `Prop`, or the ridge-side cell the data lacked. Say in PROGRESS.md
  why this one.
