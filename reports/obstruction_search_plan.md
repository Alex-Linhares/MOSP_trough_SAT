# The duality gap of the lower-bound obstruction families, by search — plan for Ralph loop0013

*Written 2026-11-02 while loop0012 was finishing its last gate. Nothing here
has been run; every number in §0 is a ten-second check or a figure read from
the record, to be replaced by the items' own. The loop directory is
`Ralph_Loops/loop0013/` (`TASK.md`, `iterations.md`, `PROGRESS.md`,
`loop.py`, `gate.py`, `knobs.json`, `allowed_sorries.txt`). Not launched.*

## 0. The question, and the one correction that shapes the whole plan

### 0.1 The question

Every certified optimum in this project is a sandwich: a witness layout above
(the upper half, found by a *tuned search over orderings*, each layout its own
certificate) and a refutation below (the lower half, a search tree that is a
proof only because its dominance rules are proved sound). The *bounds* that
start the descent — the trivial bound, the clique bound, contraction
degeneracy + 1, Harper's expansion bound at a cap, the greedy contraction-minor
step with a node budget — have only ever been **computed**: one formula, one
greedy rule, one budget each. None was ever **searched**. The lower half of the
sandwich has no counterpart to the tabu, the restarts and the two-key seed that
the upper half enjoys.

The loop asks, on instances whose optimum is already known, so that every
answer is a measurement and nothing is solved twice: **for each family of
lower-bound obstructions, what is the best certified bound a real search finds,
and how far is it from the optimum?** That distance is the family's *duality
gap*. The map of these gaps over the 6,376-instance corpus — and over the 338
instances where the solver's own bound misses by two or more, the 200 Chu &
Stuckey instances, and the 24 open classes of the pathwidth dataset — says
which family is tight where, which family could ever close a gap, and what
the stacks the proved bounds miss are made of.

### 0.2 The correction: two of the five families are not maximisations

The brief states the families as maximisations over obstructions, with F1
(empty-pair sets) "a pure maximisation": find `A` maximising
`min(|A| − 1, n − |N[A]|)` and read off `pw ≥ n − 2s − 2`. **That is backwards,
and the plan is built on the corrected reading.** The Lean theorem
`card_sub_two_mul_emptyPairIndex_sub_two_le_pathwidth` (`EmptyPair.lean`) says
`n − 2·s*(G) − 2 ≤ pw(G)` with `s*` the **maximum over all** `A`. A set found by
search has `s_found ≤ s*`, hence `n − 2 s_found − 2 ≥ n − 2 s* − 2`: the value a
found set gives is *above* the true bound, and it is not a lower bound on
pathwidth at all. Ten-second check (planner, 200 random graphs on 8 vertices,
exact pathwidth by the subset DP): the exact empty-pair bound holds on 200 of
200; the "found-`A`" value, taken as the best of five random sets, **exceeds the
pathwidth on 50 of 200**. The same holds of Harper's bound
(`exists_closedNbhd_card_le`: `pw ≥ min_{|A|=t} |N[A]| − t` for every `t`),
where the brief already says that a heuristic inner minimum gives an invalid
bound. The empty-pair bound is a weakening of Harper's at one `t`
(`s* = max_t min(t − 1, n − f(t))`, so it is computable from the same `f`),
and the two are **one family**, the *expansion family*, with one object: the
vertex-isoperimetric profile `f(t) = min_{|C| = t} |N[C]|`.

What a search does for a universal family is still valuable, and in a precise
way: a found `C` of size `t` with `|N[C]| = b` proves `f(t) ≤ b`, hence the
family's bound is **at most** `max_t (f̂(t) − t)` with `f̂` the best incumbents.
The search computes a **ceiling** on what the family can ever certify, valid
whatever the search's quality. The witness layout's prefixes already give
`f̂(t) ≤ t + pw` for every `t`, so the ceiling starts at the optimum itself, and
every set the search finds that beats the witness's prefix at its size lowers
the ceiling by the margin. If the ceiling sits below the optimum on an
instance, the expansion family cannot close that instance *under any
computation*. The exact **floor** — the valid bound — needs `f(t)` *proved*:
exhaustive branch and bound where it finishes (`satisfiability/expansion_bound.py`,
cap 12), and, where it does not, a SAT decision "no `t`-set has `|N[C]| ≤ b`"
with a DRAT proof checked by `drat-trim` (§0.5 (d)), which is a certificate a
third party can check. The duality gap of the expansion family is therefore
**bracketed**: `optimum − ceiling ≤ gap ≤ optimum − floor`, and it is exact
where the SAT or the branch and bound settles the argmax level.

The three other families are genuine maximisations, and there a search gives a
**floor** (a valid bound with a certificate) directly: cliques (certificate: the
clique; `card_le_pathwidth_add_one_of_isClique`), minors whose pathwidth the C
program proves (certificate: the contraction sequence and the refutation;
`pathwidth_gt_of_minorOf`, `lt_mospValue_of_minorOf`), minors of minimum
degree `d` (the contraction-degeneracy certificate `paper1/dataset.py`
already emits; `minDegreeIn_le_degeneracy`, `degeneracy_le_pathwidth`,
`pathwidth_minorOf_le`), and separator-branch certificates
(`branch_lemma_separator`, with the branches' widths certified recursively).
Their ceiling is the optimum, trivially.

So the plan's families are:

| family | object | search gives | exact half | certificate | checker recomputes | Lean |
|---|---|---|---|---|---|---|
| **E** (brief's F1 + F2) | `f(t) = min_{|C|=t} |N[C]|`; `s*` | a **ceiling** `max_t (f̂(t) − t)`; incumbents that seed the exact half | B&B to cap 12; SAT + DRAT per `(t, b)` | the CNF's hash and the DRAT proof per level | regenerates the CNF, `drat-trim` | `exists_closedNbhd_card_le`, `card_sub_two_mul_emptyPairIndex_sub_two_le_pathwidth`; a new contrapositive form (item 09) |
| **M** (brief's F3) | contraction sequences | a **floor**: the minor's proved width | the C program's refutation on the minor | the sequence, the minor's edge hash, the C output | replays the sequence with its own code; re-runs the C program; rule-free `vsmemo` + `checkF` where it fits | `pathwidth_gt_of_minorOf`, `pathwidth_gt_of_iso_minorOf`, `lt_mospValue_of_minorOf`; the min-degree form (item 09) |
| **B** (brief's F4) | a separator `S` and three branches | a **floor**: third-largest certified branch width + 1 | branch widths by the C program, or M recursively | `S`, `A, B, D`, the three link witnesses, the leaves' certificates | disjointness, connectivity, links, leaves | `branch_lemma_separator`, `branch_lemma` |
| **C** (baseline) | cliques; min-degree minors | floors on record (`lb_best`) | — | the clique; the ops list | — | `card_le_pathwidth_add_one_of_isClique`; `degeneracy_le_pathwidth` |
| **P** (on record) | pendant cliques | floor on record (loop0010 item 13: above the reference on 3 of 338) | — | `R, Q_i` | — | `pathwidth_ge_of_pendant_cliques` |

F5 (combinations) is the reserve's first candidate, not an item.

### 0.3 What is on record (nothing to solve twice)

- **The corpus**: 6,376 certified optima in `solutions/` (6,374
  `certified:refutation`, 2 `certified:bound`; read-only), their feature
  table `learning/data/instances.csv` (git-ignored, `python -m learning.dataset`,
  90 s; columns `lb_trivial`, `lb_contraction`, `lb_best`, `tw_min_fill`,
  `ub_best`, `optimum`) and the invariants table
  `learning/data/ensemble/conjecture_invariants.csv.gz` (committed; 50,949
  rows, 39 columns: `contraction`, `omega`, `exp`, `exp_cap`, `tw_lo`,
  `tw_hi`, `tw_exact`, …; **no `lb_best` column** — that is in
  `instances.csv`). The corpus's `exp` is Harper at cap 1 on 4,124 rows and
  at most 6; `tw_exact` on 97.2%.
- **The 338 bound-gap instances**: `optimum − lb_best ≥ 2` in `instances.csv`
  (deterministic; `learning/data/bound_gap.csv` is git-ignored and lists the
  same 338 with their §6 cluster). 20–134 customers, median 40; gap median 2,
  136 at ≥ 3, 83 at ≥ 5, max 30; by band 17 / 133 / 47 / 54 / 17 / 45 / 25 at
  9–20 / 21–30 / 31–40 / 41–60 / 61–75 / 76–100 / 101–134. 102 are Chu &
  Stuckey. On them the harness's reference `max(lb_best, tw + 1)` is beaten
  by no branching candidate (`ml_nature.md` §38) and by Lemma P on 3, by one
  stack (`excess_phase_diagram.md` §16).
- **The 200 Chu & Stuckey instances**: mean gap `optimum − lb_best` 0.56,
  0.84, 1.40, 4.52, 10.34, 14.0 at 30, 40, 50, 75, 100, 125 customers (max
  30 at 125). The minor certificates on record
  (`reports/minor_bound_verification.md`, `reports/scratch/minor_certificates/`):
  `2-3_0 = 21` (70-vertex least-c minor, rule-free certificate kept), `2-1_0
  = 24` (87, min-d), `6-1_0 = 81` (120), `SP4 = 53` (96), and **`2-2_0 = 25`
  has none: every greedy minor to 95 customers admits 24 and 100–105 ran out
  of budget** (`pathwidth_lower_bounds_survey.md` §5). `4-1_0`: 54 of 57 at
  100; `8-2_0`: 92 of 93.
- **The pathwidth dataset** (`paper1/data/dataset/pathwidth_dataset.jsonl.gz`):
  16,636 certified classes (12,630 refutation, 3,535 bound, 430 minor, 41
  theorem) and 336 `solution` rows; a `certified:minor` record carries
  `minor_certificate = {refuted, size, rule, contractions}`.
- **The 24 open classes** (`reports/scratch/dataset_open/unsolved_unlimited.csv`):
  216–712 vertices, recorded widths 5–11, 76–237 core-hours of the C program
  each with no result. Their recorded floors are in
  `reports/scratch/dataset_open/results.csv` (`lower` column, e.g.
  `pwc-17436` 10 against width 11; `pwc-15933` 4 against 5). **One of them is a
  tree**: `pwc-15933`, `BalancedTree_3_5`, 364 vertices, 363 edges, the
  complete ternary tree of height 5, recorded width 5, floor 4. The branch
  lemma applied down the tree gives `pw ≥ 5` in five lines (each node has
  three subtrees of the height below; `branch_lemma` in `Sandwich.lean`), so
  this class is closed on paper by family B before the loop starts — a
  finding item 07 records, with the certificate, and a reminder that the
  dataset's `certified:theorem` channel exists for grids only.
- **The earlier annealer** in `reports/scratch/minor_certificates/vsanneal.c`
  is **not** an annealer over contraction sequences: it anneals *layouts*
  (upper bounds; reinsert one vertex within distance `D`), and was used for
  myciel7's width-71 search. Its traces are the `myciel7_anneal_s*.out`
  files. Nothing on record searches contraction sequences; the greedy ladder
  (`pathwidth_solver/pathwidth/minor.py`, `satisfiability/relaxation.py::minor_sequence`,
  both rules, sizes 50–85% in 5% steps) is the only minor search that exists.
- **The harness**: `learning/bound_harness.py` takes any bound as
  `f(graph, matrix, budget) -> int` in optimum units, validates on 49,862
  certified instances, attacks at 8–25 with the exact solver as oracle, and
  reports tightness on the 338 against the reference. Every floor this loop
  produces goes through it.
- **The C program**: `pathwidth_solver/cli/pathwidth` (graph6 on stdin; `-t`
  seconds, `-l` layout, `-v` statistics on stderr with `lower=`, `-L` floor,
  `-u` layout file, `-m key=value` for the `MinorConfig` fields; prints
  `pathwidth <w> <status>` with status `refutation | bound | minor | upper`,
  and with `-l` on a `minor` proof the line `minor refuted <w> size <m> rule
  <r> contractions v,u v,u …`). `-m min_vertices=1000000` disables its own
  minor step, so a call on a minor we built proves *that* minor's width and
  the certificate is ours.
- **The rule-free checker**: `reports/scratch/minor_certificates/vsmemo.c`
  (`-o`, outer-boundary DFS over prefixes, stores failures) and `checkF.c`
  (80 lines; checks the refuted-prefix family), validated against brute force
  on 1,500 graphs; 2.8 s on a 70-vertex minor, 255 s and 20 GB on an
  87-vertex one. Where a minor fits, it replaces trust in the search rules.
- **DRAT**: `learning/proofs.py` (`solve_with_proof`, CaDiCaL through pysat
  `with_proof=True`, `drat-trim` in `tools/drat-trim/`); pysat 1.9 with
  `CardEnc` is installed.

### 0.4 Corrections to the brief, numbered

1. **F1 is not a maximisation that yields a bound** (§0.2): a found set gives
   a ceiling, and F1 and F2 are one family. The brief's deliverable B ("F1 by
   search on all targets; gap; where it beats `lb_best`") becomes: the
   ceiling by search on all targets; the exact `s*` and `f` at `n ≤ 22`; the
   floor by branch and bound; "where it beats `lb_best`" is asked of the
   *floor*, and "where it could never" of the ceiling.
2. **`vsanneal` anneals layouts, not contraction sequences** (§0.3). No
   contraction-sequence search exists to reuse; item 04 writes one.
3. **`paper1.dataset.fold` records no lower bound that does not close a
   class.** Its open-run channel (`OPEN_RUNS`, `results_unlimited.csv`
   format) takes rows with a `width`, an `order` and a `proof`, and reads the
   `minor` JSON only when the proof is `minor`; a `lower` column exists in
   the run files and is not consumed. The `certified:theorem` channel is the
   grids file only. So "any lower bound above the recorded floor goes into
   the dataset's evidence files via `paper1.dataset` conventions" needs a
   channel that does not exist. Item 07 writes its rows in the
   `results_unlimited.csv` format (closing bounds as `proof=minor` with the
   certificate, in the representative's labels, so `fold` would accept them
   if the file were added to `OPEN_RUNS`), writes non-closing floors to a
   separate `lower_bounds.csv` with their certificates, and **proposes** the
   one-line `OPEN_RUNS` addition and a `lower` field for `solution` rows in
   the report; it does not edit `paper1/dataset.py` unless the gate's
   `dataset_check` still passes with the change, and it never rebuilds the
   dataset.
4. **`conjecture_invariants.csv.gz` has 39 columns and no `lb_best`**; the
   corpus's Harper value there is at cap 1 on 65% of rows. The baseline
   ledger reads `lb_best` and its components from `instances.csv` and
   recomputes Harper at cap 12 itself.
5. **The loop costs quoted in the brief are the planners' estimates, which
   the loops exceeded.** Measured from the session logs: loop0010, 13 items,
   22:30 → 08:57 (10.5 h), 27 sessions including fixes, **$356**; loop0011,
   13 items, 12:37 → 00:11 (11.6 h), 40 sessions, **$389**; loop0012, 11
   items, 00:25 → about 07:40 (≈ 7.2 h), 21 sessions, **$212**. This plan's
   estimate (§0.7) is calibrated on the measured figures.
6. **`Random-125-125-2-2_0` has no minor certificate at any size tried**, not
   only "below 95": greedy minors to 95 all admit 24 (so refute nothing), and
   100–105 ran out of the 120 s budget. The question for item 05 is whether a
   *searched* minor at any size refutes 23 (pw units), with the two greedy
   rules at 100–105 under a larger cap as the first thing tried.
7. **The branch lemma on a tree is exact and closes an open class** (§0.3,
   `pwc-15933`). The brief lists the 24 as "the only open targets; no
   refutation runs"; a theorem is not a run. Item 07 records it first.
8. **The expansion bound inside the search was a net loss** (`CLAUDE.md`, the
   bounds section; `reports/expansion_bound.md` §6–§7) — a statement about
   the *solver's clock*, which this loop never touches. The loop measures the
   bound's *strength*; it proposes no solver change.
9. **No run on a full proved graph.** The C program is called on minors and
   on branches only, each under a cap, never on a whole certified instance
   (that would be a re-certification, which the owner's rule forbids without
   an explicit request). The baseline for the minor search is the greedy
   ladder *re-driven by our code* at the same caps, not a C descent on the
   whole graph.

### 0.5 Design decisions (fixed; an item that finds one wrong says so and does the smallest sound thing)

(a) **Modules**, flat in `learning/` as the repository does:
`learning/obstruction_ledger.py` (item 01), `learning/obstruction_expansion.py`
(02–03), `learning/obstruction_minor.py` (04–05, 07),
`learning/obstruction_branch.py` (06), `learning/obstruction_map.py` (08);
tests `tests/test_obstruction_*.py`. The independent checker is
`paper1/obstruction_check.py`: it imports nothing from `learning/`,
`satisfiability/`, `pathwidth_solver/` or `mosp/` (it reads instance files and
edge lists with its own 40-line readers, as `mc_graph.py` and
`paper1/dataset_check.py` do) and it is what every certificate claim in the
report cites. Scratch per item under `reports/scratch/obstruction_search/<item>/`
(scripts, logs, CSVs, certificates; anything over 50 MB is not kept and its
SHA-256 is logged). The report is `reports/obstruction_search.md`, one section
per item, created by item 01.

(b) **Graphs as bit masks.** The MOSP graph of a corpus instance is built as
`satisfiability/expansion_bound.py::_closed_masks` does (a clique per
pattern), never through networkx inside a search loop; dataset classes come
from the jsonl's `edges`. Every search works on `adj: list[int]` of length `n`.

(c) **The expansion search** (family E): for each `t`, minimise `|N[C]|` over
`|C| = t` by tabu search on swaps (one in, one out; tabu tenure 7–10 on moved
vertices; 2,000 swaps per restart; restarts from BFS balls around every vertex,
from the maximal cliques, from the certified witness's prefix sets, and from
the best set at `t ± 1`), recording the best set per `t` and its `|N[C]|`. The
ceiling is `max_t (f̂(t) − t) + 1` in optimum units; the empty-pair ceiling is
`n − 2 ŝ − 2 + 1` with `ŝ = max_t min(t − 1, n − f̂(t))`. Exact at `n ≤ 22`:
enumerate all subsets (`2^22` popcounts, numpy or a 30-line C helper compiled
on the fly as `learning/treewidth.c` is).

(d) **The exact inner minimum by SAT** (item 03): variables `x_v` (`v ∈ C`)
and `y_v` (`v ∈ N[C]`); clauses `x_u → y_v` for every `v ∈ N[u]` including
`u`; `Σ x_v ≥ t` and `Σ y_v ≤ b` as pysat `CardEnc` totalizers with disjoint
auxiliary ranges (the `mosp_encoding.py` discipline, not `encoding.py`'s
collision); CaDiCaL with `with_proof=True`; UNSAT at `(t, b)` proves
`f(t) ≥ b + 1`; SAT returns a set, which is a new incumbent (lowers the
ceiling). Binary search on `b` from the incumbent downward at each `t` the
ceiling marks as relevant (`f̂(t) − t ≥ floor − 1`). Certificate per level: the
CNF's SHA-256, `(t, b)`, the DRAT proof (gzipped, kept under 50 MB), the
`drat-trim` verdict; the checker regenerates the CNF from the instance with
its own encoder (the clause set is canonical: sorted) and compares the hash
before re-running `drat-trim`. **Nothing in the exact half rests on the
search's quality**: the search only chooses which `(t, b)` to ask.

(e) **The minor search** (family M): the state is a contraction sequence in
the graph's own labels (pairs `(v, u)`: contract `v` into `u`; `(v, −1)`:
delete an isolated `v`), replayed by the same rule as `minor.py`'s `replay`
and `relaxation.minor_groups` (every pair must be an edge of the current
graph; an invalid pair after a move is repaired to `v`'s current neighbour of
least degree, or dropped). Moves: delete one pair (the minor grows by one
vertex), insert one pair (an edge of the current minor), retarget one pair
to another current neighbour, move one pair earlier. Tabu tenure 10 on the
vertices touched; restarts from the two greedy rules at sizes 50–95% and
from the best sequence found. **Evaluation** of a candidate minor `H` of `m`
vertices: first the cheap upper bounds (the certified witness lifted to `H`,
as `cheap_width` does, and the greedy layout) — a candidate whose upper
bound is at most the best floor so far cannot improve it and is not sent to
the C program; then `printf '%s\n' "$g6" | nice -n 19 pathwidth_solver/cli/pathwidth -t CAP -l -v -m min_vertices=1000000`
with graph6 from networkx (`to_graph6_bytes(header=False)`, labels
`0..m−1` in increasing order of the surviving representative), parsing
`pathwidth <w> <status>` and stderr's `lower=`; the floor the candidate
certifies is `w` when the status is `refutation` or `bound`, and the printed
`lower` (the C's degeneracy/MMD+ floor on `H`, valid by the same theorems)
when it is `upper`. The objective is the certified floor, ties broken by
fewer vertices. Caps: 2 s per call at `n ≤ 60`, 5 s at 61–100, 10 s at
101–134, 20 s on the two ridge instances; a total per instance set by the
item. **Certificate**: instance name, `n`, the SHA-256 of the edge list, the
sequence, `m`, the minor's edge hash, the width refuted, the C program's exact
output lines and its binary's SHA-256, seconds. **Checker**: replays the
sequence with its own contraction code, checks every pair is an edge at its
step, rebuilds the quotient from the branch sets and compares the hash,
re-runs the C program on the minor and, where `m ≤ 80` and the family fits,
`vsmemo -o` + `checkF` (rule-free). The baseline is the greedy ladder (both
rules, sizes 50–85% in 5% steps, then 90 and 95%) driven by the same code at
the same caps.

(f) **The branch search** (family B): candidate separators `S` from
`bound_harness.family_separators` (cut vertices, clique glue sets, clique-tree
adhesions, edges on small graphs) plus a local search over `S` (add / drop a
vertex, `|S| ≤ 6`); for each `S` the components of `G − S` with at least two
vertices; the width of a component by the C program (cap 5 s; cached by
vertex set) — exact when the status proves it, else its printed `lower`; the
third-largest certified width among components pairwise linked through a
connected subset of `S` (the harness's `linked_third`), plus one; recursion
depth 2 (a branch's width may itself be a B certificate). Certificate: `S`,
`A, B, D`, for each pair the connected `Q ⊆ S` with its two edges, and the
three leaves' certificates (a C-program proof, an M certificate, or a clique).
Checker: disjointness, connectivity of `A, B, D` by its own BFS, the three
links, the leaves recursively, `k + 1`.

(g) **Target sets, frozen by item 01** in `reports/scratch/obstruction_search/01_ledger/targets.json`:
`gap338` (the 338, by `instance_name`), `cs200` (the 200 Chu & Stuckey),
`open24` (the 24 class ids), `rest500` (500 of the other corpus instances,
`numpy.random.default_rng(0)`, stratified by the seven size bands), and
`small` (every corpus instance at `n ≤ 22`, for the exact comparisons). Every
later item reads this file and nothing else decides membership.

(h) **Units.** Every bound is reported in optimum units (`pathwidth + 1`), as
the harness does, with the pathwidth beside it where a graph class is
concerned; "gap" is `optimum − bound` in those units; "ceiling" and "floor"
are family E's two halves; a value that is not a valid bound is called an
estimate or a ceiling in every table, never a bound.

(i) **Compute.** `nice -n 19`; 8 workers, 4 if the one-minute load is above
24; no job in the background across a turn; the C program only on minors and
branches, under caps; nothing under `solutions/`; never the Python pathwidth
solver (`pathwidth_solver/pathwidth/`); never `benchmarks.csearch`,
`benchmarks.recertify`, `benchmarks.solve_parallel` or `paper1/dataset.py run`.
Per-item core-hour budgets in `iterations.md`, total about 56.

### 0.6 Items, one line each, in dependency order

| item | title | depends on | core-h | session |
|---|---|---|---|---|
| 01 | Baseline ledger and the frozen targets: every bound on record against the optimum, on the corpus and the dataset | — | 1.5 | 1 h |
| 02 | Family E by search: the ceiling on every target; exact `f` and `s*` at `n ≤ 22`; the floor by branch and bound at cap 12 | 01 | 3 | 1.5 h |
| 03 | Family E exact at full depth: the inner minimum by SAT with DRAT; the gap bracket closed where it settles | 02 | 6 | 2 h |
| 04 | Family M: the contraction-sequence search, its certificate and checker; the 338 at `n ≤ 60` against the greedy ladder | 01 | 8 | 2.5 h |
| 05 | Family M at scale: the 338 above 60 and the 200 Chu & Stuckey; `2-2_0` and `2-3_0` | 04 | 20 | 3.5 h |
| 06 | Family B: separators with certified branches on the residual gap instances; the trees-of-cliques family | 04, 05 | 4 | 1.5 h |
| 07 | The 24 open classes: E's ceiling, M and B as lower-bound searches only; `BalancedTree_3_5` by the branch lemma; the evidence rows | 03–06 | 10 | 2.5 h |
| 08 | The duality-gap map: gap by family against excess, size and density; what no family closes; kill verdicts | 02–07 | 0.5 | 1 h |
| 09 | Lean: checked certificates imply the bound — the contrapositive of Harper, the min-degree-minor certificate, one `decide`d instance each | 04 | 0 | 1.5 h |
| 10 | The write-up: the report's summary, the paper's paragraph, the `CLAUDE.md` paragraph (drafted, not applied) | 01–09 | 0 | 1 h |
| 11 | Reserve: F5 combinations, or the best remaining gap from 01–10 | all | ≤ 4 | 1.5 h |

Measurements and the baseline first (01); the cheap family before the
expensive one (02–03 before 04–05); the open classes after the search is
validated on known optima (07 after 03–06); the write-up last; one reserve.

### 0.7 Estimate

Eleven items, one session each, plus the gate (about 12 min: `lake build`,
two pytest suites, `make check`) and the fix sessions the record says to
expect (loop0010–0012: 27, 40, 21 sessions for 13, 13, 11 items). **Wall-clock
≈ 14–17 h** (items 04, 05 and 07 carry 2.5–3.5 h of foreground compute under
the 4 h cap), **≈ $260–340** (loop0012's $19 per item at the low end, loops
0010–0011's $28–30 at the high end, and this loop's items are longer),
**≈ 56 core-hours** of our own compute (E 9, M 28, B 4, open classes 10,
ledger and map 2, reserve ≤ 4), all at `nice -n 19` on at most 8 cores.

### 0.8 The three biggest risks

1. **The SAT inner minimum does not scale past the branch and bound** (item
   03). "No `t`-set has `|N[C]| ≤ b`" at `t ≈ 40` on a 125-vertex graph is a
   cardinality-constrained problem with no symmetry breaking; it may be as
   hard as the dense-subgraph problems it resembles. If it is, the expansion
   family's floor stays at cap 12 and the bracket stays open on the large
   instances; the ceiling is still measured. The kill criterion is stated
   and the item records the boundary `(n, t)` the way §17 recorded
   `m² · k ≈ 10⁴`.
2. **The minor search does not beat the greedy ladder** (items 04–05). The
   ladder already reaches the optimum on four of the seven hard instances of
   survey §5; the room is the three it misses (`2-2_0`, `4-1_0`, `8-2_0`) and
   the 338. The search's evaluation is a C call of seconds, so an instance
   gets a few hundred candidates; if the ladder's minors are near-optimal
   among contraction minors of their size, the search records "greedy is
   enough", which is a result and the kill. The risk to the *loop* is cost:
   the 20 core-hour cap on item 05 is a hard stop, sampled if needed.
3. **The ceiling is the optimum almost everywhere and says nothing.** The
   witness's prefixes give `f̂(t) ≤ t + pw`, so the ceiling starts at the
   optimum; if the search rarely finds a `t`-set below the witness's prefix,
   the ceiling stays at the optimum and family E's duality gap is bracketed
   only from below by the floor. That outcome is informative (it says Harper
   *could* be tight, and the hard question is purely the exact half), but it
   makes item 02's headline a null result. The exact comparison at `n ≤ 22`
   settles whether the search is finding the true minima or merely the
   witness's.

A fourth, smaller: the C program's status `bound` on a minor is a min-degree
floor of the minor, which the checker reproduces with its own degeneracy code;
`refutation` on a minor rests on the corrected search rules (proved sound in
Lean), and the rule-free re-check fits only minors of about 80 vertices on
sparse graphs. The report says which of the two every M certificate rests on.

### 0.9 Kill criteria, per family (restated in each item)

- **E, the search**: if at `n ≤ 22` the searched `f̂(t)` equals the exact `f(t)`
  at every `t` on fewer than 90% of instances, the ceiling is reported as
  "search-limited" and item 03's SAT calls start from the exact small values;
  the ceiling itself needs no trust.
- **E, the exact half**: if SAT settles the argmax level on fewer than 50% of
  the 338 within the item's budget, record "Harper exact is out of reach by
  SAT above cap 12 at these sizes" with the `(n, t)` boundary; the family's
  floor is then the cap-12 branch and bound.
- **M**: if the search beats the greedy ladder (at equal caps and total time)
  on fewer than 10% of the 338, record "greedy is enough".
- **B**: if no B certificate exceeds `max(lb_best, tw + 1, M's floor)` on any
  residual gap instance, record "branching is closed", as §38 did for the
  seeded form.
- **Open classes**: zero floors above the recorded ones (the tree aside) is a
  verdict, not a failure: it says the 24 are open for a reason the obstruction
  families can see.

## 1. The items

The full text of every item, with its seven fields (question, method and
commands, deliverable, regenerate, kill criterion, size range, does not claim),
is `Ralph_Loops/loop0013/iterations.md`. The rules the sessions run under are
`Ralph_Loops/loop0013/TASK.md`.

## 2. What this plan does not claim

That any family closes any gap instance; that the ceiling of family E is
attained by any computation; that a searched minor exists below 95 vertices
for `Random-125-125-2-2_0`; that the SAT route to the exact inner minimum
scales; that any of this changes the solver (it does not: no candidate
reaches `_lower_bound` or any path that decides `k`); that the branch lemma
on `BalancedTree_3_5` is new (Ellis, Sudborough & Turner 1994 compute the
pathwidth of trees in linear time; what is new to the record is the
certificate for this class). "We found no prior report" of a searched
contraction-minor or searched vertex-isoperimetric lower bound for pathwidth
on benchmark instances; never "first".
