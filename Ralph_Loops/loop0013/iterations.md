# loop0013 — the duality gap of each lower-bound obstruction family, found by search: items

The lower half of every certified optimum rests on bounds that were only ever
*computed* (one formula, one greedy rule, one budget each); the upper half is a
tuned search. This loop runs a real search over each obstruction family on
instances whose optimum is known and measures the **duality gap**
`optimum − best certified bound` per family. The plan,
`reports/obstruction_search_plan.md`, fixes the one correction that shapes
everything (§0.2: the empty-pair and Harper bounds are *universal* statements,
so a search gives a **ceiling** on what the family can certify, and the valid
**floor** needs the inner minimum proved; cliques, minors and separator
branches are genuine maximisations whose search gives a floor with a
certificate), the families (E = expansion, M = contraction minors, B =
separator branches; C and P on record), the design decisions (§0.5: modules,
the C-program call, the SAT encoding with DRAT, the certificate formats, the
checker that shares no code), the frozen target sets (§0.5 (g)) and the kill
criteria per family (§0.9). Nine corrections to the brief are in §0.4; the
planner's ten-second checks in §0 are never quoted as results.

Phase 1 (01) measures the record; phase 2 (02–03) is the cheap family E;
phase 3 (04–05) the expensive family M; 06 is B; 07 the open classes, after
the search is validated on known optima; 08 the map; 09 Lean; 10 writes; 11
is the reserve. Every item: one session, `nice -n 19`, at most 8 workers (4
if the one-minute load in `uptime` is above 24), nothing solved twice, the C
program only on minors and branches under caps, every certificate checked by
`paper1/obstruction_check.py`, every run persisted under
`reports/scratch/obstruction_search/<item>/`, every bound in optimum units
with its Lean theorem named, every non-bound called an estimate or a ceiling.

- [x] **01 Baseline ledger and the frozen targets: every bound on record against the optimum, on the corpus and the dataset.**
  - **Question.** A of the brief. Before any search: for every certified
    corpus instance, what are the bounds already on record — `lb_trivial`,
    `lb_contraction`, `lb_best`, Harper at the recorded cap and at cap 12,
    `tw + 1` where treewidth is exact, Lemma P, the contraction-minor
    certificates on record — against the optimum; what is the gap
    distribution per bound, per collection and per size band; and for the
    dataset's 16,636 certified classes, how do the cheap floors (degeneracy,
    MMD+ with both rules, the clique number) sit against the proved width?
    And which instances are the targets, frozen once?
  - **Method.** New module `learning/obstruction_ledger.py`. (a) *Corpus.*
    Read `learning/data/instances.csv` (regenerate with
    `python -m learning.dataset --workers 8` if missing, 90 s) for
    `optimum`, `lb_trivial`, `lb_contraction`, `lb_best`, `tw_min_fill`,
    `ub_best`, `collection`, `n_customers`, `n_patterns`, `n_ones`;
    `learning/data/ensemble/conjecture_invariants.csv.gz` (rows with
    `source == "corpus"`) for `omega`, `contraction`, `exp`, `exp_cap`,
    `tw_lo`, `tw_hi`, `tw_exact`; the excess `e = (n_ones − m) / n`
    (`learning/excess.py` if it exposes it, else the formula); Lemma P from
    loop0010 item 13's `harness_values.csv` under
    `reports/scratch/excess_phase_diagram/13_reserve/` (find it; if absent,
    recompute with the harness's `--extra` and the candidate loop0010 wrote,
    8 workers, 19 s); Harper at cap 12 by
    `satisfiability.expansion_bound.expansion_bound(inst, max_t=12, time_budget=60)`
    on every instance (record `value`, `cap`, `complete`, seconds; this is
    the family's *floor on record* and the only new computation here; about
    1 core-hour on 8 workers, dense 125s at the 60 s limit are censored and
    say so); the minor certificates on record
    (`reports/scratch/minor_certificates/*.json`: `2-3_0`, `2-1_0`, `6-1_0`,
    `SP4`; and `reports/scratch/minor_bound/` for `4-1_0` 54 and `8-2_0` 92 —
    read the survey §5 table and cite it if the files are not there). Per
    instance: every bound, `gap_<bound> = optimum − bound`, the best floor
    on record `floor0 = max(lb_best, tw_lo + 1, harper12, lemmaP, minor)` and
    its source. Tables: tight / gap 1 / gap ≥ 2 counts per bound; the gap
    distribution of `floor0` by collection and by size band; the 338
    (`optimum − lb_best ≥ 2`) against `floor0` (how many does the record
    already close that `lb_best` does not — §38 says 8 by exact treewidth,
    §16 says 3 by Lemma P, survey §5 says 4 of the 125s by minors); the 200
    Chu & Stuckey by class `(n, m, d)`. (b) *Dataset.* For the 16,636
    certified classes of `paper1/data/dataset/pathwidth_dataset.jsonl.gz`
    (`edges`, `width`, `provenance`): degeneracy, MMD+ (least-c and min-d)
    and the clique number under a 2 s budget (`networkx.find_cliques` with
    an `islice` cap, §38's method note), each against `width`; by
    collection; the 430 `certified:minor` classes with their certificate's
    `size / n`; skip components above 1,024 vertices and the 78 header-only
    graphs and say so. Bit-mask adjacency throughout. (c) *Targets.* Write
    `reports/scratch/obstruction_search/01_ledger/targets.json`: `gap338`,
    `cs200`, `open24` (from
    `reports/scratch/dataset_open/unsolved_unlimited.csv`, with each class's
    recorded `lower` from `reports/scratch/dataset_open/results.csv` where
    present, else the dataset's floor from (b)), `rest500`
    (`numpy.random.default_rng(0)`, stratified by the seven size bands of
    the harness, from the corpus minus `gap338 ∪ cs200`), `small` (every
    corpus instance at `n ≤ 22`); record the seed and the counts. (d)
    *Report.* Create `reports/obstruction_search.md` with the document's
    header (what the loop is, the families and the direction of each —
    plan §0.2's table — the units, the reference, the targets) and §1 with
    the tables of (a)–(c). Tests in `tests/test_obstruction_ledger.py`:
    `floor0 ≤ optimum` on every corpus row (a violation is a finding, see
    kill); the targets' counts and disjointness; the dataset floors never
    above the width; the ledger's reading of a minor certificate on record
    agrees with `reports/minor_bound_verification.md`'s table.
  - **Deliverable.** `learning/obstruction_ledger.py` with tests;
    `reports/scratch/obstruction_search/01_ledger/{ledger_corpus.csv, ledger_dataset.csv.gz, targets.json, run.log}`;
    `reports/obstruction_search.md` created with its header and §1.
  - **Regenerate.** `nice -n 19 python3 -m learning.obstruction_ledger --stage corpus --workers 8`; `--stage dataset --workers 8`; `--stage targets`; `--stage tables`.
  - **Kill criterion.** None for the item; a guard: any bound on record
    above a certified optimum (or a dataset floor above a certified width)
    stops the item there, goes to the top of PROGRESS.md and the report, and
    ends the session — that would be a wrong value on record or a wrong
    bound, the most important possible finding.
  - **Size range.** Corpus 9–134 customers, all 6,376; dataset classes to
    1,024 vertices per component (the rest reported as skipped); Harper at
    cap 12 under 60 s per instance.
  - **Does not claim.** Anything about what a search would find; that
    `floor0` is the best bound obtainable from the record (the minor
    certificates on record are those of seven instances only).

- [x] **02 Family E by search: the ceiling on every target; exact `f` and `s*` at `n ≤ 22`; the floor by branch and bound.**
  - **Question.** B and the first half of C of the brief, corrected by plan
    §0.2. On every target, how far below the optimum is the **ceiling**
    `max_t (f̂(t) − t) + 1` that a search for small-neighbourhood sets
    certifies (and the empty-pair ceiling `n − 2ŝ − 1`), i.e. what the
    expansion family could at most certify; on the instances small enough to
    enumerate, does the search find the true minima `f(t)` at every `t`; and
    where does the cap-12 branch-and-bound floor sit between?
  - **Method.** New module `learning/obstruction_expansion.py`. (a) *The
    search* as plan §0.5 (c): for every `t` from 1 to `n − 1`, tabu search on
    swaps minimising `|N[C]|` (bit masks; tenure 7; 2,000 swaps per restart;
    restarts from the BFS ball of radius 1–2 around every vertex, from every
    maximal clique under an `islice` cap of 200, from the certified witness's
    prefix sets (`solutions/<name>.json`'s `ordering` turned into a customer
    closing order by the instance's simulation, or the dataset's `layout`),
    and from the best set at `t − 1` plus one vertex); `f̂(t)` and the set per
    `t`; the ceiling, its argmax `t*`, the empty-pair ceiling with `ŝ`;
    seconds. A found set is a certificate of `f(t) ≤ |N[C]|` and nothing
    more: store it. (b) *Exact at `n ≤ 22`*: enumerate every subset (a C
    helper compiled on the fly as `learning/treewidth.c` is, or numpy over
    `2^n` masks with popcounts), giving `f(t)` for every `t`, the exact
    Harper bound `max_t (f(t) − t) + 1`, the exact `s*` and `n − 2s* − 1`;
    on `targets.small` (every corpus instance at `n ≤ 22`) compare: the share
    of instances where `f̂(t) = f(t)` at every `t`, where the ceiling equals
    the exact bound, and where the exact bound equals the optimum (how often
    Harper is *tight* at these sizes; `exists_closedNbhd_card_le` gives
    validity, tightness is the measurement). (c) *The floor*: item 01's cap-12
    branch and bound (`expansion_bound`, `max_t=12`, 60 s), rerun with
    `time_budget=None` on the 338 only where item 01 censored it, under a
    10-minute cap per instance (sample if the 338's dense ones exceed the
    item's budget and say so). (d) *Tables*: per target set and size band,
    the ceiling's gap, the floor's gap, the bracket width (ceiling − floor),
    the share where the ceiling is at the optimum (the search found nothing
    below the witness's prefixes), the share where the ceiling is strictly
    below the optimum (the family can never close these), `t*` against `n`;
    on the 338, how many the floor already closes and how many the ceiling
    rules out; on the 200 Chu & Stuckey by class; cost per instance (ms).
    Through the harness: the *floor* as an `--extra` candidate on the corpus
    (`python -m learning.bound_harness --stage validity --workers 8 --sources corpus --extra learning.obstruction_expansion:harper_floor`),
    which checks "above optimum (must be 0)". Tests: the ceiling is never
    below the exact bound and never above the optimum (both theorems) on
    the small set; the exact enumeration agrees with `expansion_bound`'s
    levels at `t ≤ 12` on 50 instances; the empty-pair ceiling equals
    `n − 2ŝ − 1` with `ŝ` from `f̂`; the search is label-invariant up to the
    seed.
  - **Deliverable.** `learning/obstruction_expansion.py` (search, exact,
    `harper_floor` candidate) with tests;
    `reports/scratch/obstruction_search/02_expansion/{ceiling.csv, exact_small.csv, floor.csv, sets/ (one JSON per instance, the best set per t), run.log}`;
    `reports/obstruction_search.md` §2.
  - **Regenerate.** `nice -n 19 python3 -m learning.obstruction_expansion --stage ceiling --targets all --workers 8`; `--stage exact --targets small`; `--stage floor --targets gap338`; `--stage tables`.
  - **Kill criterion.** Plan §0.9 E-search: if at `n ≤ 22` the search attains
    `f(t)` at every `t` on fewer than 90% of instances, report the ceiling as
    "search-limited" (it is valid regardless) and tell item 03 to seed from
    the exact values where they exist. A ceiling below the floor, or a floor
    above the optimum, is a bug: stop and record.
  - **Size range.** Ceiling: every target (9–134 customers; `open24` is
    item 07's); exact: `n ≤ 22`; floor: the 338 at cap 12.
  - **Does not claim.** That the ceiling is attained by any computation;
    that the floor is the family's best (the exact half is item 03); any
    solver change.

- [x] **03 Family E exact at full depth: the inner minimum by SAT with DRAT; the gap bracket closed where it settles.**
  - **Question.** The second half of C of the brief. Where the branch and
    bound cannot prove `f(t)` (above `t = 12`), can a SAT decision — "no
    `t`-set has `|N[C]| ≤ b`" — with a DRAT proof checked by `drat-trim`
    prove it, so that the expansion family's floor meets its ceiling; on how
    many of the 338 does Harper, searched and proved, close the gap; and
    where is the boundary in `(n, t)`?
  - **Method.** In `learning/obstruction_expansion.py`: `exact_sat(adj, t, b, proof_dir)`
    as plan §0.5 (d) — `x_v`, `y_v`, clauses `x_u → y_v` for `v ∈ N[u]`,
    totalizers `Σ x ≥ t` and `Σ y ≤ b` with disjoint auxiliary ranges (reuse
    `learning/proofs.py::solve_with_proof`'s CaDiCaL-with-proof call and its
    drat-trim wrapper; CaDiCaL 1.9.5 through pysat, a conflict budget per
    call, default 2 × 10⁶, and a 120 s deadline). Driver `--stage sat`: for
    each instance of `gap338` then `cs200`, at the levels `t` the ceiling
    marks relevant (`f̂(t) − t ≥ floor − 1`, at most 8 levels per instance,
    nearest `t*` first), binary search `b` down from `f̂(t) − 1`: UNSAT at
    `(t, b)` proves `f(t) ≥ b + 1` and the level is settled when
    `f(t) = f̂(t)`; SAT returns a set that lowers `f̂(t)` (a new incumbent:
    the ceiling drops, re-mark the levels). Per settled level: the CNF's
    SHA-256 (clauses sorted, variables in a fixed order so the checker can
    regenerate it), `(t, b)`, the proof gzipped (kept under 50 MB, else the
    hash only), the `drat-trim` verdict and seconds. The family's **exact
    floor** on an instance is `max over settled t of (f(t) − t) + 1`
    combined with the cap-12 levels, and the bracket is closed when the
    argmax level settles. (b) *The checker*: `paper1/obstruction_check.py`
    created here with its own instance reader and its own CNF generator for
    family E (the format and variable order documented in the module's
    docstring, which is the only thing the two share): `check-expansion
    <instance> <certificate.json>` regenerates the CNF, compares the hash,
    runs `drat-trim`, and prints the bound the certificate proves with the
    theorem it rests on (`exists_closedNbhd_card_le` contrapositive, item 09
    names it). (c) *Tables*: settled levels and seconds against `(n, t)`;
    the share of the 338 whose bracket closes; on the 338 and the 200, the
    exact floor's gap, how many it closes (`floor = optimum`), how many the
    ceiling rules out, how many stay open with a bracket; the `(n, t)`
    boundary beyond which no call finishes (the analogue of §17's
    `m² · k ≈ 10⁴`); cost. Budget 6 core-hours, 8 workers, `gap338` first,
    smallest `n` first, `cs200` with what is left; sample and say so.
  - **Deliverable.** `exact_sat` and `--stage sat` in
    `learning/obstruction_expansion.py`; `paper1/obstruction_check.py` with
    `check-expansion`; tests (`tests/test_obstruction_expansion.py`: the CNF
    agrees with the enumeration at `n ≤ 12` on 100 random graphs for every
    `(t, b)` — UNSAT iff `f(t) > b`; a genuine certificate verifies, a
    damaged one is rejected; the checker's CNF hash equals the search's on
    20 instances); `reports/scratch/obstruction_search/03_sat/{levels.csv, certificates/<instance>/, boundary.csv, run.log}`;
    `reports/obstruction_search.md` §3.
  - **Regenerate.** `nice -n 19 python3 -m learning.obstruction_expansion --stage sat --targets gap338,cs200 --workers 8 --core-hours 6`; `python3 paper1/obstruction_check.py check-expansion <instance> <cert>`.
  - **Kill criterion.** Plan §0.9 E-exact: if the argmax level settles on
    fewer than 50% of the 338 within the budget, record "Harper exact is out
    of reach by SAT above cap 12 at these sizes" with the boundary; the
    floor stays the cap-12 one. Any UNSAT at a `(t, b)` where the
    enumeration (item 02) has a set is a bug in the encoding: stop and
    record.
  - **Size range.** The 338 (20–134 customers) and the 200 (30–125); the
    encoding's self-test at `n ≤ 12`.
  - **Does not claim.** That the SAT route scales beyond the boundary it
    measures; that a level censored by the conflict budget says anything;
    any solver change.

- [x] **04 Family M: the contraction-sequence search, its certificate and checker; the 338 at `n ≤ 60` against the greedy ladder.**
  - **Question.** D of the brief, first half. Over contraction sequences of
    the MOSP graph, does a local search find minors whose proved pathwidth
    exceeds what the greedy ladder (both rules, 50–95%) proves at the same
    caps and total time; what is the minor family's duality gap on the 338
    at `n ≤ 60`; and what does a minimal certifying minor look like?
  - **Method.** New module `learning/obstruction_minor.py`, plan §0.5 (e):
    the state is a sequence of `(v, u)` pairs in the instance's customer
    labels; `replay` (own code, mirroring `relaxation.minor_groups`'s
    checks); moves delete / insert / retarget / move-earlier; tabu tenure
    10; restarts from `relaxation.minor_sequence(inst, size, rule)` at sizes
    50, 60, 70, 80, 90, 95% for both rules and from the incumbent; a
    candidate minor is skipped without a C call when the certified witness
    lifted to it (or the greedy layout on it) has width at most the best
    floor so far; otherwise one C call,
    `printf '%s\n' "$g6" | nice -n 19 pathwidth_solver/cli/pathwidth -t 2 -l -v -m min_vertices=1000000`
    (graph6 by networkx from the quotient's edge list, labels in increasing
    order of the surviving representative), parsed for `pathwidth <w> <status>`
    and `lower=`; the floor certified is `w` on `refutation` or `bound`, the
    printed `lower` on `upper` (both valid; record which). Objective: the
    certified floor in optimum units, ties by fewer vertices; the baseline
    is the ladder (both rules, 50–85% in 5% steps, then 90, 95) driven by
    the same evaluation at the same cap; both get the same total seconds
    per instance (60 s at `n ≤ 40`, 120 s at 41–60). Certificate per
    instance (the best minor): plan §0.5 (e)'s JSON, with the C output
    verbatim and the binary's SHA-256. (b) *The checker*:
    `paper1/obstruction_check.py check-minor <instance> <cert>`: reads the
    instance with its own reader, builds the MOSP graph itself, replays the
    sequence with its own contraction code (every pair an edge at its step,
    `u = −1` only for an isolated `v`), rebuilds the quotient from the
    branch sets and compares the edge hash, re-runs the C program on the
    minor with the same cap ×5 and compares the proved width, and, where
    `m ≤ 80`, compiles and runs `reports/scratch/minor_certificates/vsmemo.c`
    (`-o`, cap 300 s, 8 GB) and `checkF.c` for a rule-free refutation of
    `w − 1` on the minor, recording which of the three checks passed. (c)
    *Validation before the 338*: on 50 random corpus instances at `n ≤ 16`
    (plus every minor the search proposes on them), the C's proved width of
    the minor equals `learning.first_moment.vertex_separation_brute`; on the
    six certificates of `reports/minor_bound_verification.md`, the checker
    accepts the recorded sequences and the C program reproduces the refuted
    widths. (d) *Run*: the 251 instances of `gap338` at `n ≤ 60`, 8 workers,
    about 8 core-hours (search and ladder each at the same total). Tables:
    per band, the ladder's floor gap and the search's; where the search
    beats the ladder (count, by how much); where either reaches the optimum;
    the minimal certifying minor's `m / n` against `n` and the excess;
    checker verdicts (all three checks / C only / replay only); C calls per
    instance and seconds. Through the harness: the search's floor as an
    `--extra` candidate on the 251 (it reads certificates, so it is a
    lookup, flagged as such) for the "must be 0" column.
  - **Deliverable.** `learning/obstruction_minor.py` with tests
    (`tests/test_obstruction_minor.py`: replay rejects a non-edge pair;
    the quotient equals `relaxation.minor_groups`'s on 50 instances; a
    retargeted pair is repaired or dropped; the lifted-witness skip never
    skips a minor whose C-proved width exceeds the floor, on 30 instances;
    the certificate round-trips through the checker); the checker's
    `check-minor`; `reports/scratch/obstruction_search/04_minor/{search.csv, ladder.csv, certificates/<instance>.json, validation.log, run.log}`;
    `reports/obstruction_search.md` §4.
  - **Regenerate.** `nice -n 19 python3 -m learning.obstruction_minor --stage validate`; `--stage run --targets gap338 --max-n 60 --workers 8 --seconds 60,120`; `python3 paper1/obstruction_check.py check-minor <instance> <cert>`; `--stage tables`.
  - **Kill criterion.** Plan §0.9 M, on this item's 251: if the search beats
    the ladder on fewer than 10% of them, record "greedy is enough at
    `n ≤ 60`" (item 05 still runs, on the larger instances, where the ladder
    is known to miss). A minor whose C-proved width exceeds the brute-force
    pathwidth in (c), or any certificate the checker rejects, stops the item.
  - **Size range.** 20–60 customers (251 of the 338); validation at
    `n ≤ 16` and on the six recorded certificates (70–120 vertices).
  - **Does not claim.** That the search is optimal among contraction minors;
    that a C `refutation` on a minor is independent of the search rules (it
    rests on the corrected rules proved sound in Lean; the rule-free check
    is the independent one where it fits); any solver change.

- [ ] **05 Family M at scale: the 338 above 60 and the 200 Chu & Stuckey; `Random-125-125-2-2_0` and `2-3_0`.**
  - **Question.** D of the brief, second half. On the 87 gap instances above
    60 customers and the 200 Chu & Stuckey instances (262 distinct), what
    floor does the minor search certify against the ladder; on the two
    125-customer ridge instances, does a searched minor refute 23 (pw units)
    for `2-2_0` at any size, where every greedy minor to 95 admits 24 and
    100–105 ran out of budget; and is `2-3_0`'s 70-vertex certificate the
    smallest the search finds?
  - **Method.** `learning/obstruction_minor.py --stage run` on
    `targets.cs200 ∪ (gap338 at n > 60)`, caps 5 s at 61–100 and 10 s at
    101–134 per C call, total per instance 180 s at 61–100 and 300 s at
    101–134 for the search and the same for the ladder, 8 workers (4 if the
    load is above 24), smallest `n` first, **20 core-hours hard cap**: the
    driver stops starting instances at 18 core-hours and the report says
    which were not reached. The two ridge instances get a separate stage:
    `--stage ridge --instances Random-125-125-2-2_0,Random-125-125-2-3_0 --core-hours 2`
    — first the two greedy rules at 100, 102, 105, 108, 110 with a 120 s cap
    each (the survey's unfinished sizes under a larger cap), then the
    search from the best of them with a 60 s cap per call; for `2-3_0`, the
    search from the 70-vertex certificate downward (does a smaller minor
    refute 20?). Certificates and the checker as item 04 (the rule-free
    check where `m ≤ 80`; the 87-vertex scale needs 20 GB and is not run).
    Tables: by Chu & Stuckey class `(n, m, d)` and by band for the gap
    instances, the ladder's and the search's floor gaps; where the search
    beats the ladder; the floors against the record's seven (survey §5) and
    against the exact expansion floor of item 03 (which family is tighter
    where: the expectation from the record is minors on the sparse ridge,
    expansion on the dense classes — measure it); the minimal certifying
    minor's `m / n`; the two ridge instances in full (every size, rule, cap,
    status, nodes, seconds); C calls and seconds; the "must be 0" column
    through the harness as in item 04.
  - **Deliverable.** `reports/scratch/obstruction_search/05_minor_scale/{search.csv, ladder.csv, ridge.csv, certificates/, run.log}`;
    `reports/obstruction_search.md` §5.
  - **Regenerate.** `nice -n 19 python3 -m learning.obstruction_minor --stage run --targets cs200,gap338 --min-n 61 --workers 8 --seconds 180,300 --core-hours 18`; `--stage ridge …`; `--stage tables`.
  - **Kill criterion.** Plan §0.9 M on the 338 as a whole (items 04 + 05): if
    the search beats the ladder on fewer than 10% of the 338, record "greedy
    is enough". For `2-2_0`: no certificate within the 2 core-hours is a
    recorded negative, not a kill. The budget is the kill: at 18 core-hours
    the driver stops.
  - **Size range.** 61–134 customers; the 200 at 30–125; the two ridge
    instances at 125.
  - **Does not claim.** That `2-2_0` has no minor certificate (only that
    none was found under this budget); that a floor below the optimum says
    anything about the optimum (all are certified already); any solver
    change; nothing about the C program's speed (plan §0.4 (9)).

- [ ] **06 Family B: separators with certified branches on the residual gap instances; the trees-of-cliques family.**
  - **Question.** E of the brief. On the gap instances where families E and
    M leave `floor < optimum` after items 03–05, does a separator-branch
    certificate (`branch_lemma_separator`: three connected branches of
    certified width `≥ k`, pairwise linked through `S`, force `k + 1`) with
    the branches' widths **proved by the C program or by M** — not seeded by
    treewidth as §38's candidates were — certify any of them; and on the
    *trees of cliques with branching* family §6 named, specifically?
  - **Method.** New module `learning/obstruction_branch.py`, plan §0.5 (f):
    candidate `S` from `learning.bound_harness.family_separators` plus a
    local search over `S` (add / drop, `|S| ≤ 6`, tabu 5); components of
    `G − S` with `≥ 2` vertices; each component's width by one C call (cap
    5 s, `-m min_vertices=1000000`, cached by vertex set across all `S`),
    exact on `refutation`/`bound`, its printed `lower` otherwise, or an M
    certificate from item 04/05 when the component is the whole graph minus
    little; `linked_third` from the harness for the pairwise-link
    condition; value = third-largest linked width + 1; depth 2 (a component
    may itself carry a B certificate). Certificate: `S`, `A, B, D`, the
    three `Q ⊆ S` with their two edges each, the leaves' certificates (C
    output, M certificate or a clique), `k`. Checker
    `paper1/obstruction_check.py check-branch`: disjointness, connectivity
    of `A, B, D` by its own BFS, each `Q` connected and adjacent to both
    sides, the leaves recursively (re-running the C program on a leaf,
    `check-minor` on an M leaf, the clique by inspection), `k + 1`. Run on
    the residual set (every instance of `gap338` with `floor < optimum`
    after items 03–05; expected most of the 338), 8 workers, 4 core-hours,
    120 s per instance; and on the §6 ten smallest gap instances and the
    harness's hand instances (the theta graph, the spider of spiders) as a
    validation that the value equals what §38 reports where seeds coincide.
    Tables: residual instances closed / raised / unchanged by B; the `|S|`
    and the branch widths of every certificate; against §38's seeded
    candidates (where exact branch widths add over `max(ω − 1, tw)`); the
    family's gap by band and excess.
  - **Deliverable.** `learning/obstruction_branch.py` with tests
    (`tests/test_obstruction_branch.py`: the theta graph gives 3 at
    `S = {a, b}`; the spider of spiders 3; a damaged link is rejected by the
    checker; value never above the optimum on 100 random instances at
    `n ≤ 14` with brute-force leaves); `check-branch`;
    `reports/scratch/obstruction_search/06_branch/{search.csv, certificates/, run.log}`;
    `reports/obstruction_search.md` §6.
  - **Regenerate.** `nice -n 19 python3 -m learning.obstruction_branch --stage run --targets residual --workers 8 --core-hours 4`; `--stage tables`.
  - **Kill criterion.** Plan §0.9 B: if no B certificate exceeds
    `max(lb_best, tw + 1, M floor, E floor)` on any residual instance,
    record "branching is closed", as §38 did for the seeded form, and say
    whether exact branch widths changed anything at all.
  - **Size range.** The residual of the 338 (20–134 customers); validation
    at `n ≤ 14` and on the hand instances.
  - **Does not claim.** That depth 2 is enough; that the separator family
    plus a 6-vertex local search sees every separator; any solver change.

- [ ] **07 The 24 open classes: family E's ceiling, M and B as lower-bound searches only; `BalancedTree_3_5` by the branch lemma; the evidence rows.**
  - **Question.** F of the brief. On the 24 dataset classes with no proof
    after 76–237 core-hours of the C program each (216–712 vertices,
    recorded widths 5–11, recorded floors below), does any family certify a
    floor above the recorded one — and `pwc-15933`, the complete ternary
    tree of height 5, first, on paper?
  - **Method.** (a) *The tree.* `BalancedTree_3_5` (364 vertices, 363
    edges): check it is a tree with the dataset's edges (own code); the
    branch lemma down the tree: a complete ternary tree of height `h` has
    `pw ≥ h` by induction (`branch_lemma` in `Sandwich.lean`, `S = {root}`,
    three subtrees of height `h − 1`; `h = 1` is `K_{1,3}` with `pw = 1`),
    so `pw ≥ 5`, and the recorded layout has width 5: the class is closed.
    Write the certificate as a nested B certificate (item 06's format, with
    leaves at height 1) and verify it with `check-branch`; state that
    Ellis, Sudborough & Turner (1994) compute tree pathwidth in linear time
    (the `cut-branch` recursion is their algorithm's lower half), so the
    *value* is classical and only the certificate on the record is new;
    note the C program spent 237 core-hours on it. (b) *The other 23.*
    Family E's ceiling by item 02's search (minutes each; a ceiling below
    the recorded width says Harper cannot close the class, which is itself
    worth knowing); family M by item 04's search with caps 20 s per C call,
    minors at 30–85% of `n` **only** (never above 90%: a minor that is
    nearly the whole graph would be a refutation run on an open instance,
    which this loop does not do), 20 minutes per class; family B with
    components' widths by C calls capped at 20 s. Budget 10 core-hours, 4
    workers (these graphs are large; check `uptime`; the owner's
    `run_unlimited.py` may be running — leave it its cores). (c) *The
    evidence rows*, plan §0.4 (3): `reports/scratch/obstruction_search/07_open/results_obstruction.csv`
    in the `results_unlimited.csv` format (`FIELDS` of
    `reports/scratch/dataset_open/run_unlimited.py`), in the
    representative's labels (compute the representative as `fold` does,
    from the values on record), one row per class whose floor **meets** the
    recorded width (`proof=minor` with the certificate JSON in the `minor`
    column, or — for the tree — `proof=theorem` with the B certificate,
    which `fold` does not yet read: say so); and `lower_bounds.csv` (class
    id, recorded width, recorded floor, new floor, family, certificate path,
    checker verdict) for floors that do not close. Propose in the report,
    with the exact diff, the `OPEN_RUNS` addition and a `lower` field on
    `solution` rows; apply the `OPEN_RUNS` line only if
    `python3 paper1/dataset_check.py` and the gate still pass and no dataset
    rebuild is needed to pass them; never run `paper1.dataset run` or
    `write`.
  - **Deliverable.** `reports/scratch/obstruction_search/07_open/{tree_certificate.json, ceiling.csv, minor.csv, branch.csv, results_obstruction.csv, lower_bounds.csv, certificates/, run.log}`;
    `reports/obstruction_search.md` §7 with the table of the 24 (recorded
    width, recorded floor, E ceiling, M floor, B floor, best new floor,
    closed?).
  - **Regenerate.** `nice -n 19 python3 -m learning.obstruction_minor --stage open --targets open24 --workers 4 --core-hours 8`; `python3 -m learning.obstruction_branch --stage open --targets open24`; `python3 -m learning.obstruction_expansion --stage ceiling --targets open24`; `python3 paper1/obstruction_check.py check-branch BalancedTree_3_5 tree_certificate.json`.
  - **Kill criterion.** Plan §0.9 open classes: zero new floors on the 23 is
    a verdict ("open for a reason the families can see"), not a failure. A
    floor above a recorded upper bound is a wrong value on record: stop,
    top of PROGRESS.md and the report, end the session.
  - **Size range.** 216–712 vertices, the 24 classes; the tree exactly.
  - **Does not claim.** That any class other than the tree is closed; that
    a floor one below the recorded width makes the width likely (the
    recorded width is an upper bound and nothing here refutes anything);
    that the tree's value is new (it is not).

- [ ] **08 The duality-gap map: gap by family against excess, size and density; what no family closes; kill verdicts.**
  - **Question.** G of the brief. Over the corpus targets, with every
    family's floor and E's ceiling on record from items 01–07: which family
    is tight where, in the excess `e`, the size and the density; which
    instances no family closes, and what they look like; and the kill
    verdict of each family, stated once.
  - **Method.** New module `learning/obstruction_map.py` reading the items'
    CSVs (nothing recomputed): per instance the floors `lb_best`, `tw + 1`,
    E floor (cap 12 / SAT), E ceiling, M floor (search, ladder), B floor, P,
    and `best = max` with its family; the gap of each by band, collection,
    Chu & Stuckey class, and excess decile (`learning/data/excess.csv` or
    the formula); the share tight per family per cell; the instances no
    family closes (count, their `(n, m, e)`, their §6 cluster, the ten
    smallest drawn as matrices with `learning.extremal.draw`); the
    "dominance" table (for every pair of families, on how many instances
    one is strictly above the other); a figure (PNG; read the dataviz skill
    first; no title inside): gap of the best floor against `e` by size
    band, with the E ceiling's gap beside it, and a second panel of the 200
    Chu & Stuckey by class. The kill verdicts of plan §0.9, each with the
    number that decides it. Cost ledger: core-hours per item from the run
    logs, so the loop's total is regenerated and not carried by hand.
  - **Deliverable.** `learning/obstruction_map.py` with a test that the map
    reproduces item 01's `floor0` where no search ran; `reports/scratch/obstruction_search/08_map/{map.csv, uncovered.csv, families.png}`;
    `reports/obstruction_search.md` §8 (the tables in full, the figure, the
    verdicts).
  - **Regenerate.** `python3 -m learning.obstruction_map --stage all`.
  - **Kill criterion.** None of its own; it states the families'.
  - **Size range.** Whatever items 01–07 covered, stated per table.
  - **Does not claim.** A bound (nothing here is one); any solver change;
    that the uncovered instances share one structure (the description is
    what the data say).

- [ ] **09 Lean: a checked certificate implies the bound — the contrapositive of Harper, the min-degree-minor certificate, one `decide`d instance each.**
  - **Question.** H of the brief. The theorems behind every certificate are
    in `EmptyPair.lean`, `Minor.lean` and `Sandwich.lean`; what is missing is
    the statement that a *checked certificate* implies the bound, in the
    form the checker's output cites. Which of these fit a session, and can
    one concrete small instance be closed by `decide`?
  - **Method.** New file `lean/MOSPFormalization/ObstructionCertificate.lean`,
    imported by `lean/MOSPFormalization.lean`, `#print axioms` lines in
    `paper1/axiom_check.lean`, names folded into `learning/sandwich.py`'s
    `ALL_PROVED` as loop0012's `STEP_BOUND_PROVED` was. **State before you
    prove, and check before you state**: every statement first checked by
    brute force on every graph to 8 vertices
    (`reports/scratch/obstruction_search/09_lean/check.py`, the
    `reports/scratch/empty_pair/check.py` pattern, log kept). In order of
    reach: (i) `pathwidth_ge_of_forall_closedNbhd`: for `j ≤ n`,
    `(∀ A : Finset V, A.card = j → j + k < (closedNbhd G A).card) → k + 1 ≤ pathwidth G`
    — the contrapositive of `exists_closedNbhd_card_le`, the theorem an E
    certificate (UNSAT at `(t, b)`) rests on, with its MOSP form through
    `mospValue_eq_pathwidth_add_one`; (ii) `pathwidth_ge_of_minor_minDegree`:
    `IsContractionSeq G seq → (∀ v, v ∉ removed seq → d ≤ (minorOf G seq).degree v) → d ≤ pathwidth G`
    via `minDegreeIn_le_degeneracy` / `degeneracy_le_pathwidth` on the minor
    and `pathwidth_minorOf_le` — the C program's `bound` status on a minor
    and `paper1/dataset.py`'s `minor_certificate`, both covered by one
    theorem; (iii) a `Bool` checker `checkSeq : SimpleGraph V → List (V × Option V) → Bool`
    with `checkSeq G seq = true → IsContractionSeq G seq` and
    `minDegreeOfMinor`, so that on a concrete `SimpleGraph (Fin n)` with
    decidable adjacency a certificate is checked by `decide` (or
    `decide +kernel` as `Search/BetterMove.lean` does); (iv) one concrete
    instance: the smallest gap instance of §6 whose M certificate (item 04)
    has a `bound` status, or failing that an 8-vertex graph with a
    3-vertex min-degree-2 minor, closed by `decide`; (v) if time, the E
    contrapositive `decide`d on a 7-vertex graph over all `Finset (Fin 7)`
    of size `j`. The branch-certificate theorem is `branch_lemma_separator`
    as it stands; a `decide`-able connectivity check is out of reach in a
    session and is said so.
  - **Deliverable.** `ObstructionCertificate.lean` (no `sorry`, no `axiom`),
    the axiom-check lines, the sandwich entries, the brute-force check and
    its log; `reports/obstruction_search.md` §9 with the statements, which
    checker output cites which theorem, and what was not reached.
  - **Regenerate.** `python3 reports/scratch/obstruction_search/09_lean/check.py`; `cd lean && lake build`; `make -C paper1/latex axioms`; `python -m learning.sandwich --stage lean`, then `--stage degree_bound` (so `reports/sandwich_tables.md` is restored; loop0012's note).
  - **Kill criterion.** A statement false on a graph to 8 vertices is
    corrected before it is stated (two earlier `sorry`s hid false
    statements); nothing is stated that is not checked.
  - **Size range.** Every finite simple graph for the theorems; `decide` at
    `n ≤ 8`.
  - **Does not claim.** That the C program's `refutation` on a minor is
    checked in Lean (it rests on `Search/`'s soundness theorems and the
    binary's faithfulness, as before); that `decide` scales past toy sizes.

- [ ] **10 The write-up: the report's summary, the paper's paragraph, the `CLAUDE.md` paragraph (drafted, not applied).**
  - **Question.** I of the brief. What did the loop establish, in one page,
    with every number carrying its size range and regenerate command?
  - **Method.** (a) `reports/obstruction_search.md` §0, the two-page summary
    in the style of `reports/excess_phase_diagram.md` §0: the question, the
    correction (plan §0.2), the families and the direction of each, the
    duality-gap map's headline numbers per family on the 338, the 200 and
    the 24, what no family closes, the kill verdicts, the certificates and
    their checkers with the Lean theorems, the cost ledger (core-hours and
    dollars from the logs), what is open. (b) The paper's paragraph for
    `paper1/latex/sec5_results.tex` (the subsection "A checkable proof of a
    refutation", or Appendix `sec9b_appendix_machinery.tex` if the owner
    prefers — write it once, place it in Section 5, and say in the report
    where else it could go): the searched lower bounds as the counterpart
    of the searched upper bounds, the ceiling / floor distinction, the
    certificate formats, the numbers; "we found no prior report", never
    "first"; `\leanentry` rows for item 09's theorems in
    `sec9a_appendix_lean.tex`; `make -C paper1/latex` and `make check`;
    `tests/test_paper1_latex.py` passes. (c) The `CLAUDE.md` paragraph,
    drafted in the report's §10.3 in the style of the existing bounds
    section (the owner places it); `CLAUDE.md` is not edited. (d) The
    `README` line for `learning/README.md` if that file lists the modules
    (one line per new module).
  - **Deliverable.** `reports/obstruction_search.md` §0 and §10; the paper's
    paragraph and Lean rows; the drafted `CLAUDE.md` paragraph.
  - **Regenerate.** `make -C paper1/latex && make -C paper1/latex check`; `python -m pytest tests/test_paper1_latex.py -q`.
  - **Kill criterion.** None; a number without a regenerate command does not
    go in.
  - **Size range.** As the items state, repeated beside every number.
  - **Does not claim.** More than items 01–09 measured.

- [ ] **11 Reserve.** The best remaining gap from items 01–10, one session,
  chosen and priced at the start of the session and written down first, in
  this order of preference unless the record says otherwise: (a) **F5,
  combinations** — an M search whose objective is the exact E floor of the
  minor (item 03's SAT on the minor, which is smaller) or B on the minor,
  on the ten residual instances with the smallest gap after item 08; (b)
  the `2-2_0` minor search continued for 2 core-hours from item 05's best
  sequence; (c) the E contrapositive `decide`d (item 09 (v)) if it was not
  reached; (d) the harness's adversary (`learning.extremal.local_search`,
  8–15) against the M search's floor to look for a certificate the checker
  rejects. Same seven fields in the PROGRESS.md entry; same rules; ≤ 4
  core-hours.
