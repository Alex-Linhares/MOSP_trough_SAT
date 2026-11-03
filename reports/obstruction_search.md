# The duality gap of each lower-bound obstruction family, found by search

*Ralph loop0013, 2026-11-02 onward. The plan is `reports/obstruction_search_plan.md`
(§0.2 is the correction everything rests on; §0.5 the design decisions; §0.9
the kill criteria per family). §0 is the two-page summary, written last (item
10); then one section per item. Nothing here changes a solver default;
nothing re-solves an instance that is already proved; nothing is written
under `solutions/`.*

## What this document is about

**The question.** Every certified optimum in this project is a sandwich: a
witness layout above, found by a tuned search over orderings, and a
refutation below, a search tree whose dominance rules are proved sound. The
*bounds* that start the descent — the trivial bound, the clique bound,
contraction degeneracy + 1, Harper's expansion bound at a cap, the greedy
contraction-minor step — have only ever been **computed**: one formula, one
greedy rule, one budget each. None was ever **searched**. This loop runs a
real search over each family of lower-bound obstructions on instances whose
optimum is already known, so that every answer is a measurement, and reports
the family's **duality gap**: `optimum − best certified bound`.

**The families, and the direction of each** (plan §0.2). Two of the five
families the brief listed are *universal* statements, not maximisations, and
that shapes what a search can give:

| family | object | search gives | exact half | certificate | Lean |
|---|---|---|---|---|---|
| **E** (expansion: Harper and the empty pair) | `f(t) = min_{|C|=t} |N[C]|`; `s* = max_t min(t − 1, n − f(t))` | a **ceiling** `max_t (f̂(t) − t) + 1`: a found set only proves `f(t) ≤ b` | branch and bound to cap 12; SAT with DRAT per `(t, b)` | the CNF's hash and the DRAT proof per level | `exists_closedNbhd_card_le`, `card_sub_two_mul_emptyPairIndex_sub_two_le_pathwidth` (`EmptyPair.lean`) |
| **M** (contraction minors) | contraction sequences | a **floor**: the minor's proved width | the C program's refutation on the minor | the sequence, the minor's edge hash, the C output | `pathwidth_gt_of_minorOf`, `lt_mospValue_of_minorOf` (`Minor.lean`) |
| **B** (separator branches) | a separator `S` and three branches | a **floor**: third-largest certified branch width + 1 | branch widths by the C program, or M recursively | `S`, `A, B, D`, the links, the leaves' certificates | `branch_lemma_separator`, `branch_lemma` (`Sandwich.lean`) |
| **C** (baseline) | cliques; min-degree minors | floors on record (`lb_best`) | — | the clique; the ops list | `card_le_pathwidth_add_one_of_isClique`; `minDegreeIn_le_degeneracy`, `degeneracy_le_pathwidth` |
| **P** (on record) | pendant cliques | floor on record (loop0010 item 13) | — | `R, Q_i` | `pathwidth_ge_of_pendant_cliques` (`PendantCliques.lean`) |

The bound of family E is `pw ≥ min_{|A|=t} |N[A]| − t` for every `t` (Harper
1966; `exists_closedNbhd_card_le`), a minimum over **all** `t`-sets; a set
found by search gives a value *above* the true bound and is not a bound at
all. The exact floor needs the inner minimum proved, and the search's value
is a **ceiling** on what the family could ever certify. Cliques, minors and
separator branches are genuine maximisations whose search gives a floor with
a certificate.

**Units.** Every corpus bound is in optimum units (`pathwidth + 1`); "gap" is
`optimum − bound` in those units. The dataset's `width` is a pathwidth and its
floors are stated in pathwidth units (`degeneracy ≤ pw`, `MMD+ ≤ tw ≤ pw`,
`ω − 1 ≤ pw`); a gap is the same number in either unit. A value that is not a
valid bound is called a ceiling or an estimate in every table, never a bound.

**The reference.** `max(lb_best, tw + 1)` is the harness's reference
(`learning/bound_harness.py`; `ml_nature.md` §38); this loop's reference is
`floor0`, the best floor **on record** per instance (§1), which adds Harper at
cap 12, Lemma P and the minor certificates on record to it.

**The targets** (frozen by item 01 in
`reports/scratch/obstruction_search/01_ledger/targets.json`; nothing else
decides membership): `gap338` (the 338 corpus instances with
`optimum − lb_best ≥ 2`), `cs200` (the 200 Chu & Stuckey instances), `open24`
(the 24 open classes of the pathwidth dataset), `rest500` (500 other corpus
instances, stratified by the harness's seven size bands,
`numpy.random.default_rng(0)`) and `small` (every corpus instance at
`n ≤ 22`, for the exact comparisons).

**What is on record and is not solved twice** (plan §0.3): 6,376 certified
optima (`solutions/`), the feature table `learning/data/instances.csv`, the
invariants table `learning/data/ensemble/conjecture_invariants.csv.gz`,
Lemma P's corpus values (`reports/scratch/pendant_cliques/harness_values.csv`),
the contraction-minor certificates (`reports/scratch/minor_certificates/`,
`reports/scratch/minor_bound/`; `reports/minor_bound_verification.md`), the
pathwidth dataset (`paper1/data/dataset/pathwidth_dataset.jsonl.gz`, 16,636
certified classes) and its 24 open classes (`reports/scratch/dataset_open/`).

**Compute and rules.** `nice -n 19`, at most 8 workers; the C program only on
minors and branches under caps; never the Python pathwidth solver; never a
whole proved graph re-solved. Every certificate is checked by
`paper1/obstruction_check.py`, which shares no code with the searches.
"We found no prior report", never "first". Harper (1966) and Ellis,
Sudborough & Turner (1994) are cited where the loop meets them.

---

## 0. Summary

*(written by item 10)*

---

## 1. The baseline ledger and the frozen targets (item 01)

*2026-11-02. Code `learning/obstruction_ledger.py`; tests
`tests/test_obstruction_ledger.py` (12); files under
`reports/scratch/obstruction_search/01_ledger/`: `ledger_corpus.csv` (6,376
rows, every bound on record and `floor0`), `harper12.csv` (the one new
computation), `ledger_dataset.csv.gz` (16,636 rows), `targets.json`,
`tables.md` (the tables below, generated), `run.log`, `harper_run.out`,
`gate_run.out`. Regenerate:
`nice -n 19 python3 -m learning.obstruction_ledger --stage corpus --workers 8`
(8 min wall; the Harper run resumes from `harper12.csv`), `--stage dataset
--workers 8` (6 s), `--stage targets`, `--stage tables`. Size range: corpus
9–134 customers, all 6,376; dataset classes to 1,024 vertices per component
(22 classes, all VSPLIB grids, have a larger component and their floors are
over the rest of the graph); Harper at cap 12 under 60 s per instance.*

### 1.1 What was done

**The record, joined.** For every certified corpus instance: `optimum`,
`lb_trivial`, `lb_contraction`, `lb_best`, `tw_min_fill`, `ub_best` from
`learning/data/instances.csv`; `omega`, `contraction`, `exp` (Harper at the
recorded cap, `exp_cap`), `tw_lo`, `tw_hi`, `tw_exact` from the invariants
table; Lemma P (`pendant`, optimum units) from loop0010 item 13's
`reports/scratch/pendant_cliques/harness_values.csv`; the excess
`e = (n_ones − m) / n`; the collection and the Chu & Stuckey class `(n, m, d)`
from the file path and the name; the provenance and value of every
`solutions/` file, read directly (`instances.csv` is a feature table of
2026-09-25 and lists four 125 × 125 instances as `solution`; the files say
`certified:refutation` on 6,374 and `certified:bound` on 2, and the values
agree on all 6,376). The contraction-minor certificates on record were read
from their files: `reports/scratch/minor_certificates/<name>_m*.json` (claim
`pw(G) ≥ K`, floor `K + 1`) and
`reports/scratch/minor_bound/<name>_*_recorded_certificate.json` (`refuted`
in MOSP units, floor `refuted + 1`; the `.out` files beside them confirm the
unit: `lower = refuted + 1`). That is **twelve** instances with a file-backed
minor floor, not the seven the survey's §5 table lists: loop0010's
`large@recorded` run left certificates for `Random-125-125-2-4_0`, `2-5_0`,
`4-2_0`, `4-4_0` and `4-5_0` as well. Two values of the survey table have no
file (`4-1_0` = 54 at 100 vertices min-d, `8-2_0` = 92 at 115–120; logged in
`reports/scratch/pw_lower_bounds/corpus_minor.out` and `corpus_minor_hi.out`);
they are carried in the column `minor_survey`, cited, and **not** inside
`floor0`.

**The one new computation: Harper at cap 12.** `expansion_bound(inst,
max_t=12, time_budget=60)` on all 6,376 instances, cheapest first, 8 workers
at `nice -n 19`: 479 s wall, **1.01 core-hours**. 6,341 instances completed
every level to cap 12; **35 were censored at the 60 s limit** (13 at 76–100
customers, 22 at 101–134; 33 of them Chu & Stuckey), having completed caps 7
to 11 — a censored value is still a valid floor, because the module discards
an abandoned level rather than using its incumbent (its docstring: an
overestimate of `f(T + 1)` would be a wrong answer, not a slow bound). The
cap-12 value is never below the recorded `exp` and improves it on **442**
instances, by up to 21 stacks (`Random-125-125-10-5_0`: 99 = optimum, from
the recorded cap). Per instance the ledger keeps `harper12`, the cap reached,
`complete`, seconds and the levels `f(1..t)`.

**`floor0`.** The best floor on record per instance,
`floor0 = max(lb_best, tw_lo + 1, harper12, lemmaP, minor)`, with the parts
attaining it in `floor0_source`. The harness's reference is
`max(lb_best, tw + 1)`; `floor0` adds Harper at cap 12, Lemma P and the minor
certificates to it.

**The guard.** Every bound column against the optimum, and the dataset's
cheap floors against the width: **zero violations** on 6,376 × 9 bound
columns and 16,636 × 4 floors. `tests/test_obstruction_ledger.py` asserts
this on the committed files.

**The dataset.** For the 16,636 certified classes of
`paper1/data/dataset/pathwidth_dataset.jsonl.gz`: degeneracy, MMD+ with both
rules (least-c, min-d) and the largest clique `networkx.find_cliques` reaches
within 2 s or 200,000 cliques, each per connected component on bit masks, the
row's value the maximum over its components of at most 1,024 vertices; 48
core-seconds in all. No row of the jsonl lacks its edge list (the "78
header-only graphs" of the item's brief are not in this file; three classes
are edgeless, width 0, and are kept); 5 of the 430 `certified:minor` rows
carry no `minor_certificate` (`pwc-05116`, `05456`, `05480`, `14181`,
`14639`); 17 clique enumerations were censored.

### 1.2 Findings

1. **On the record, 89.9% of the corpus is closed by a bound** (`floor0`
   tight on 5,732 of 6,376) against 77.0% for the solver's own `lb_best`
   (4,909); the instances at gap ≥ 2 fall from 338 to **122**, the mean gap
   from 0.43 to 0.18 stacks, the maximum from 30 to 23. Treewidth + 1 is the
   strongest single bound (tight on 5,653; attains `floor0` alone on 898 and
   is the only part above `lb_best` on 789 tight instances). Harper at cap
   12 is tight on 4,065, above `lb_best` on 145, and the sole attainer on
   88. Lemma P is the sole attainer on 5 instances (gap 0 on 2 of them). The
   minor certificates attain alone on 11 and close 7.

2. **Of the 338, the record already closes 81 (24.0%)**: 67 by exact
   treewidth alone (the "67 gap instances would become bound-certified" of
   `ml_nature.md` §24, reproduced), **7 by Harper at cap 12 alone**
   (`Random-100-100-8-2_0`, `Random-125-125-10-3_0`, `Random-125-125-10-5_0`,
   `Random-75-75-6-3_0`, two Warwick 30-customer instances, `p4040n4_0`),
   **7 by a minor certificate alone** (`2-1_0`, `2-3_0`, `2-4_0`, `2-5_0`,
   `4-5_0`, `6-1_0`, `SP4`), none by Lemma P (it beats `lb_best` on 3 by one
   stack, as `excess_phase_diagram.md` §16 says). Against the harness's
   reference `max(lb_best, tw + 1)`, which closes 67, `floor0` is strictly
   above the reference on 104 corpus instances (96 of them in the 338) and
   closes 14 more. What is left on the 338: 135 at gap 1, 122 at gap ≥ 2
   (50 at 2, 12 at 3, 9 at 4, 8 at 5, 10 at 6, 33 at 7–23). The survey's "4
   of the 125s by minors" is 7 of 12 on file once loop0010's `large` records
   are counted (`2-2_0` at 24 of 25, `4-1_0` at 53 of 57, `4-2_0` at 55 of
   57, `4-4_0` at 50 of 51, `8-2_0` at 87 of 93 are the five short ones; the
   survey's file-less 54 and 92 would raise two of them by one and five).

3. **Where the record misses is where the solver is slow.** By size band
   (table a3) the mean `floor0` gap is 0.05 at 9–20 customers, 0.96 at
   41–60, 5.48 at 76–100 and 4.89 at 101–134; by collection (a2), Chu &
   Stuckey has 72 instances at gap ≥ 2 out of 200, Faggioli–Bentivoglio 33
   of 300, and every other collection at most 7. By Chu & Stuckey class (a6):
   mean `floor0` gap 0.2, 0.2, 0.64, 2.72, 6.64 and 4.96 at 30, 40, 50, 75,
   100 and 125 customers against `lb_best`'s 0.56, 0.84, 1.40, 4.52, 10.34,
   14.0; the 125 row sits below the 100 row only because the 125s have minor
   certificates on record and the 100s have none. Harper at cap 12 is the
   part that does the work on the **dense** classes (`125-125-10`: mean gap
   0.2; `100-100-8`: 0.8; `100-50-10`: 4.0 from `lb_best`'s 11.4) and is
   worse than `lb_best` on the sparse ones (`100-100-2`: 12.2 against 7.8;
   `75-75-2`: 6.4 against 4.8; `125-125-2`: 15.8 against 9.8) — the ridge
   classes, where contraction minors are the only part that reaches the
   optimum (`125-125-2`: 4 of 5 closed, mean gap 0.2). Pathwidth provably
   exceeds treewidth (`optimum > tw_hi + 1`) on 564 corpus instances and on
   156 of the 338: on those, no treewidth-side bound can close the gap.

4. **The dataset's cheap floors are tight on 31.4%** (5,231 of 16,636;
   table b1); MMD+ least-c is the best of the three (tight on 5,059; above
   min-d on 3,786 classes, below on 552; degeneracy alone 2,130; `ω − 1`
   970), with gap ≥ 2 on 5,541 classes and a maximum gap of 86 (the
   Carvalho & Soma MOSP classes, mean gap 63.9, where the floor is a degree
   bound on a graph of width 133). By provenance: the 3,535
   `certified:bound` classes are all tight (by construction), 1,696 of the
   12,630 `certified:refutation` classes, **0 of the 430 `certified:minor`**
   (mean gap 4.6: a class gets a minor certificate exactly where the cheap
   floor failed) and 0 of the 41 grids (gap 31.7). The 425 minor
   certificates all refute `width − 1` (so each proves its class exactly);
   their minors have median `size / n` 0.505 (0.33–0.84); the rule is min-d
   on 379 and least-c on 46. Rome (11,199 classes) has mean gap 1.29 and
   maximum 6; the control-flow graphs 0.41.

5. **The targets, frozen** (`targets.json`, seed 0, ledger sha256
   `e5918a4c…`): `gap338` 338 (102 of them Chu & Stuckey, 17 at `n ≤ 22`),
   `cs200` 200, `open24` 24 — every one with a recorded floor (`lower`) from
   `reports/scratch/dataset_open/results_quick.csv` and
   `results_quick_rescued.csv`, not from `results.csv` as the plan's §0.3
   says (that file holds solved classes only): the floor is `width − 1` on
   18 of the 24, and `pwc-15933` 4 of 5, `pwc-16471` 6 of 7, `pwc-17043` 2
   of 8, `pwc-04526` 3 of 10, `pwc-04517` 2 of 10, `pwc-17317` 3 of 10 on
   the other six — `rest500` 500 drawn from the 5,940 other corpus instances in
   proportion to the seven size bands (345 / 140 / 11 / 3 / 0 / 1 / 0; the
   pool has no instance above 100 customers outside `gap338 ∪ cs200`),
   disjoint from both, and `small` 4,123 (every corpus instance at
   `n ≤ 22`). The test re-derives `rest500` from the ledger and the seed.

### 1.3 Kill verdict and what this does not claim

**Kill: none for the item; the guard passed** (no bound on record above a
certified optimum; no dataset floor above a certified width). The harness's
validity stage (`learning/bound_harness.py`, "above optimum" must be 0) was
not re-run on the new floor: the ledger's guard is that same check, applied
to every bound column on every corpus instance, and the test asserts it on
the committed file. The item does
not claim anything about what a search would find; that `floor0` is the best
bound obtainable from the record (the minor certificates on file are those
of twelve instances; Harper is at cap 12 and censored on 35); that the
dataset's floors are more than the three cheap ones (its 430 minor
certificates are a fourth, exact by construction, not folded into
`floor_cheap`); or that the 24 open classes' recorded floors are the best
the record holds (they are the `lower` of the last quick run).

### 1.4 Tables (generated; `tables.md`)


#### (a1) every bound on record, corpus, optimum units

| bound          |   instances |   tight |   gap 1 |   gap ≥ 2 |   mean gap |   max gap |   above optimum |
|:---------------|------------:|--------:|--------:|----------:|-----------:|----------:|----------------:|
| lb_trivial     |        6376 |     238 |     726 |      5412 |       6.15 |        86 |               0 |
| lb_contraction |        6376 |    4164 |    1083 |      1129 |       0.98 |        44 |               0 |
| lb_best        |        6376 |    4909 |    1129 |       338 |       0.43 |        30 |               0 |
| omega          |        6376 |    2803 |     877 |      2696 |       2.95 |        86 |               0 |
| exp_rec        |        6376 |    3996 |    1688 |       692 |       0.81 |        40 |               0 |
| harper12       |        6376 |    4065 |    1790 |       521 |       0.58 |        30 |               0 |
| tw1            |        6376 |    5653 |     531 |       192 |       0.63 |        61 |               0 |
| lemmaP         |        6376 |    2809 |     895 |      2672 |       2.84 |        86 |               0 |
| minor          |          12 |       7 |       2 |         3 |       1.17 |         6 |               0 |
| floor0         |        6376 |    5732 |     522 |       122 |       0.18 |        23 |               0 |

#### (a2) floor0 by collection

| collection           |   instances |   lb_best tight |   lb_best mean gap |   floor0 tight |   floor0 gap 1 |   floor0 gap ≥ 2 |   floor0 mean gap |   floor0 max gap |
|:---------------------|------------:|----------------:|-------------------:|---------------:|---------------:|-----------------:|------------------:|-----------------:|
| Challenge            |          46 |              31 |               0.91 |             37 |              6 |                3 |              0.52 |                9 |
| Chu & Stuckey        |         200 |              53 |               5.42 |             88 |             40 |               72 |              2.83 |               23 |
| Faggioli-Bentivoglio |         300 |             125 |               1.02 |            168 |             99 |               33 |              0.57 |                4 |
| Harvey               |        2130 |            1605 |               0.28 |           2000 |            128 |                2 |              0.06 |                2 |
| Miller               |           1 |               1 |               0.00 |              1 |              0 |                0 |              0.00 |                0 |
| SCOOP                |          24 |               6 |               1.04 |              7 |             14 |                3 |              1.00 |                6 |
| Shaw                 |          25 |              14 |               0.44 |             20 |              5 |                0 |              0.20 |                1 |
| Simonis              |        3630 |            3058 |               0.18 |           3394 |            229 |                7 |              0.07 |                2 |
| Wilson               |          20 |              16 |               1.55 |             17 |              1 |                2 |              0.50 |                6 |

#### (a3) floor0 by size band

| band    |   instances |   lb_best tight |   lb_best mean gap |   floor0 tight |   floor0 gap 1 |   floor0 gap ≥ 2 |   floor0 mean gap |   floor0 max gap |
|:--------|------------:|----------------:|-------------------:|---------------:|---------------:|-----------------:|------------------:|-----------------:|
| 9–20    |        4122 |            3617 |               0.13 |           3913 |            208 |                1 |              0.05 |                2 |
| 21–30   |        1816 |            1134 |               0.45 |           1598 |            208 |               10 |              0.13 |                2 |
| 31–40   |         197 |              99 |               0.82 |            143 |             46 |                8 |              0.31 |                2 |
| 41–60   |         121 |              45 |               1.64 |             51 |             34 |               36 |              0.96 |                4 |
| 61–75   |          30 |               5 |               4.47 |              6 |             11 |               13 |              2.77 |                9 |
| 76–100  |          63 |               9 |               8.78 |             11 |             12 |               40 |              5.48 |               17 |
| 101–134 |          27 |               0 |              13.26 |             10 |              3 |               14 |              4.89 |               23 |

#### (a4) which part attains floor0

| part     |   attains floor0 |   attains alone |   attains alone and tight |   on the 338: attains alone |   on the 338: closes alone |
|:---------|-----------------:|----------------:|--------------------------:|----------------------------:|---------------------------:|
| lb_best  |             5344 |              16 |                         0 |                          16 |                          0 |
| tw1      |             6172 |             898 |                       789 |                         176 |                         67 |
| harper12 |             4480 |              88 |                        13 |                          82 |                          7 |
| lemmaP   |             2920 |               5 |                         2 |                           3 |                          0 |
| minor    |               11 |              11 |                         7 |                          11 |                          7 |

#### (a5) the 338 against the record

| bound    |   with a value |   closes (gap 0) |   gap 1 |   gap ≥ 2 |   mean gap |   max gap |   beats lb_best |
|:---------|---------------:|-----------------:|--------:|----------:|-----------:|----------:|----------------:|
| lb_best  |            338 |                0 |       0 |       338 |       4.78 |        30 |               0 |
| tw1      |            338 |               67 |     116 |       155 |       8.88 |        61 |             199 |
| harper12 |            338 |                7 |      41 |       290 |       3.99 |        30 |             127 |
| lemmaP   |            338 |                0 |       3 |       335 |      13.80 |        83 |               3 |
| minor    |             12 |                7 |       2 |         3 |       1.17 |         6 |              12 |
| floor0   |            338 |               81 |     135 |       122 |       2.33 |        23 |             290 |

#### (a6) the 200 Chu & Stuckey by class

|   n |   m |   d |   instances |   mean opt |   lb_best gap |   harper12 gap |   tw1 gap |   lemmaP gap |   floor0 gap |   floor0 tight |   harper12 complete |   harper12 s |
|----:|----:|----:|------------:|-----------:|--------------:|---------------:|----------:|-------------:|-------------:|---------------:|--------------------:|-------------:|
|  30 |  30 |   2 |           5 |       8.60 |          1.00 |           1.40 |      0.80 |         3.20 |         0.80 |              2 |                   5 |         0.21 |
|  30 |  30 |   4 |           5 |      16.00 |          1.00 |           1.00 |      0.00 |         7.00 |         0.00 |              5 |                   5 |         0.06 |
|  30 |  30 |   6 |           5 |      21.20 |          0.40 |           0.40 |      0.20 |         8.40 |         0.20 |              4 |                   5 |         0.02 |
|  30 |  30 |   8 |           5 |      25.20 |          0.20 |           0.20 |      0.00 |         6.60 |         0.00 |              5 |                   5 |         0.01 |
|  30 |  30 |  10 |           5 |      27.00 |          0.20 |           0.40 |      0.20 |         2.60 |         0.00 |              5 |                   5 |         0.00 |
|  40 |  40 |   2 |           5 |      11.00 |          2.20 |           1.60 |      0.20 |         4.20 |         0.20 |              4 |                   5 |         0.87 |
|  40 |  40 |   4 |           5 |      20.20 |          1.40 |           1.00 |      1.60 |        11.40 |         0.80 |              1 |                   5 |         0.36 |
|  40 |  40 |   6 |           5 |      28.20 |          0.40 |           0.40 |      0.00 |        15.80 |         0.00 |              5 |                   5 |         0.13 |
|  40 |  40 |   8 |           5 |      32.60 |          0.20 |           0.20 |      0.00 |        15.00 |         0.00 |              5 |                   5 |         0.02 |
|  40 |  40 |  10 |           5 |      35.40 |          0.00 |           0.00 |      0.00 |        11.20 |         0.00 |              5 |                   5 |         0.01 |
|  50 |  50 |   2 |           5 |      13.20 |          3.20 |           2.80 |      2.20 |         6.60 |         2.00 |              0 |                   5 |         2.90 |
|  50 |  50 |   4 |           5 |      23.80 |          3.60 |           1.20 |      6.80 |        14.60 |         1.20 |              0 |                   5 |         1.76 |
|  50 |  50 |   6 |           5 |      35.20 |          0.80 |           0.80 |      3.60 |        22.00 |         0.80 |              1 |                   5 |         0.43 |
|  50 |  50 |   8 |           5 |      40.40 |          0.20 |           0.20 |      0.00 |        21.60 |         0.00 |              5 |                   5 |         0.09 |
|  50 |  50 |  10 |           5 |      44.40 |          0.40 |           0.40 |      0.00 |        19.40 |         0.00 |              5 |                   5 |         0.02 |
|  50 | 100 |   2 |           5 |      21.20 |          4.80 |           2.00 |      9.40 |        14.40 |         2.00 |              0 |                   5 |         5.10 |
|  50 | 100 |   4 |           5 |      34.60 |          0.40 |           0.40 |      5.40 |        23.60 |         0.40 |              3 |                   5 |         0.57 |
|  50 | 100 |   6 |           5 |      42.40 |          0.20 |           0.20 |      0.00 |        23.20 |         0.00 |              5 |                   5 |         0.06 |
|  50 | 100 |   8 |           5 |      46.20 |          0.20 |           0.20 |      0.00 |        16.40 |         0.00 |              5 |                   5 |         0.01 |
|  50 | 100 |  10 |           5 |      47.80 |          0.20 |           0.20 |      0.00 |         5.40 |         0.00 |              5 |                   5 |         0.00 |
|  75 |  75 |   2 |           5 |      15.80 |          4.80 |           6.40 |      9.40 |         9.20 |         4.80 |              0 |                   5 |        27.47 |
|  75 |  75 |   4 |           5 |      34.20 |         12.80 |           6.80 |     22.00 |        24.80 |         6.80 |              0 |                   5 |         9.78 |
|  75 |  75 |   6 |           5 |      50.00 |          4.00 |           1.00 |     27.80 |        37.00 |         1.00 |              1 |                   5 |        13.31 |
|  75 |  75 |   8 |           5 |      59.40 |          0.60 |           0.60 |     26.00 |        41.20 |         0.60 |              2 |                   5 |         2.39 |
|  75 |  75 |  10 |           5 |      64.80 |          0.40 |           0.40 |     20.00 |        42.00 |         0.40 |              3 |                   5 |         0.46 |
| 100 |  50 |   2 |           5 |      11.60 |          2.80 |           7.40 |      3.80 |         3.80 |         2.80 |              0 |                   5 |        15.84 |
| 100 |  50 |   4 |           5 |      26.40 |         10.40 |          12.40 |     17.00 |        16.80 |        10.40 |              0 |                   5 |        22.83 |
| 100 |  50 |   6 |           5 |      44.00 |         18.00 |          11.80 |     30.20 |        31.40 |        11.80 |              0 |                   5 |        20.15 |
| 100 |  50 |   8 |           5 |      56.20 |         15.60 |           7.60 |     35.40 |        40.00 |         7.60 |              0 |                   5 |        23.44 |
| 100 |  50 |  10 |           5 |      67.20 |         11.40 |           4.00 |     38.20 |        49.00 |         4.00 |              0 |                   5 |        13.70 |
| 100 | 100 |   2 |           5 |      20.20 |          7.80 |          12.20 |     11.80 |        11.80 |         7.80 |              0 |                   0 |        60.00 |
| 100 | 100 |   4 |           5 |      45.00 |         19.20 |          13.80 |     32.60 |        34.80 |        13.80 |              0 |                   1 |        54.13 |
| 100 | 100 |   6 |           5 |      64.60 |         14.00 |           6.60 |     42.00 |        51.40 |         6.60 |              0 |                   3 |        43.73 |
| 100 | 100 |   8 |           5 |      76.60 |          3.40 |           0.80 |     41.40 |        59.20 |         0.80 |              1 |                   5 |        42.63 |
| 100 | 100 |  10 |           5 |      84.60 |          0.80 |           0.80 |     36.20 |        63.60 |         0.80 |              1 |                   5 |         9.07 |
| 125 | 125 |   2 |           5 |      22.80 |          9.80 |          15.80 |     15.80 |        15.80 |         0.20 |              4 |                   0 |        60.00 |
| 125 | 125 |   4 |           5 |      53.00 |         27.40 |          25.00 |     41.60 |        43.00 |         6.00 |              1 |                   0 |        60.00 |
| 125 | 125 |   6 |           5 |      78.40 |         22.20 |          15.60 |     55.80 |        65.00 |        13.60 |              1 |                   0 |        60.00 |
| 125 | 125 |   8 |           5 |      93.60 |          8.80 |           4.80 |     57.40 |        77.00 |         4.80 |              0 |                   0 |        60.00 |
| 125 | 125 |  10 |           5 |     103.20 |          1.80 |           0.20 |     52.00 |        83.40 |         0.20 |              4 |                   3 |        52.67 |

#### (a7) Harper at cap 12 by band

| band    |   instances |   run |   complete to cap 12 |   censored at 60 s |   mean cap reached |   core-seconds |   harper12 > exp_rec |   harper12 > lb_best |   harper12 tight |
|:--------|------------:|------:|---------------------:|-------------------:|-------------------:|---------------:|---------------------:|---------------------:|-----------------:|
| 9–20    |        4122 |  4122 |                 4122 |                  0 |               1.47 |           3.14 |                   10 |                    0 |             2933 |
| 21–30   |        1816 |  1816 |                 1816 |                  0 |               2.88 |          35.83 |                  203 |                   32 |              989 |
| 31–40   |         197 |   197 |                  197 |                  0 |               4.56 |          38.28 |                   64 |                   26 |               92 |
| 41–60   |         121 |   121 |                  121 |                  0 |               6.93 |         122.51 |                   68 |                   26 |               31 |
| 61–75   |          30 |    30 |                   30 |                  0 |               8.67 |         317.28 |                   21 |                   12 |                6 |
| 76–100  |          63 |    63 |                   50 |                 13 |               9.08 |        1651.41 |                   49 |                   31 |               10 |
| 101–134 |          27 |    27 |                    5 |                 22 |               9.93 |        1471.06 |                   27 |                   18 |                4 |

Harper rows without a value (not reached under the wall): 0.

#### (a8) the instances with a minor certificate on record

| instance_name        |   optimum |   lb_best |   harper12 |   tw1 |   lemmaP |   minor | minor_source                                                                       |   minor_survey |   floor0 |
|:---------------------|----------:|----------:|-----------:|------:|---------:|--------:|:-----------------------------------------------------------------------------------|---------------:|---------:|
| Random-125-125-2-1_0 |        24 |        13 |          8 |     8 |        8 |      24 | reports/scratch/minor_certificates/Random-125-125-2-1_0_m87.json                   |            nan |       24 |
| Random-125-125-2-2_0 |        25 |        13 |          7 |     6 |        6 |      24 | reports/scratch/minor_bound/Random-125-125-2-2_0_large_recorded_certificate.json   |            nan |       24 |
| Random-125-125-2-3_0 |        21 |        12 |          6 |     7 |        7 |      21 | reports/scratch/minor_certificates/Random-125-125-2-3_0_m70.json                   |            nan |       21 |
| Random-125-125-2-4_0 |        24 |        15 |          8 |     8 |        8 |      24 | reports/scratch/minor_bound/Random-125-125-2-4_0_large_recorded_certificate.json   |            nan |       24 |
| Random-125-125-2-5_0 |        20 |        12 |          6 |     6 |        6 |      20 | reports/scratch/minor_bound/Random-125-125-2-5_0_large_recorded_certificate.json   |            nan |       20 |
| Random-125-125-4-1_0 |        57 |        27 |         33 |    12 |       10 |      53 | reports/scratch/minor_bound/Random-125-125-4-1_0_default_recorded_certificate.json |             54 |       53 |
| Random-125-125-4-2_0 |        57 |        27 |         32 |    12 |       11 |      55 | reports/scratch/minor_bound/Random-125-125-4-2_0_large_recorded_certificate.json   |            nan |       55 |
| Random-125-125-4-4_0 |        51 |        24 |         21 |    11 |        9 |      50 | reports/scratch/minor_bound/Random-125-125-4-4_0_large_recorded_certificate.json   |            nan |       50 |
| Random-125-125-4-5_0 |        46 |        23 |         23 |    10 |        8 |      46 | reports/scratch/minor_bound/Random-125-125-4-5_0_large_recorded_certificate.json   |            nan |       46 |
| Random-125-125-6-1_0 |        81 |        63 |         71 |    23 |       14 |      81 | reports/scratch/minor_certificates/Random-125-125-6-1_0_m120.json                  |            nan |       81 |
| Random-125-125-8-2_0 |        93 |        84 |         89 |    37 |       16 |      87 | reports/scratch/minor_bound/Random-125-125-8-2_0_default_recorded_certificate.json |             92 |       89 |
| SP4                  |        53 |        37 |         44 |    16 |       13 |      53 | reports/scratch/minor_certificates/SP4_m96.json                                    |            nan |       53 |

#### (b1) dataset: 16636 certified classes, cheap floors against the width (pathwidth units)

| floor (pw units)   |   classes |   tight |   gap 1 |   gap ≥ 2 |   mean gap |   max gap |   above width |
|:-------------------|----------:|--------:|--------:|----------:|-----------:|----------:|--------------:|
| degeneracy         |     16636 |    2130 |    3106 |     11400 |       3.63 |       109 |             0 |
| mmd_leastc         |     16636 |    5059 |    5804 |      5773 |       1.70 |        86 |             0 |
| mmd_mind           |     16636 |    4744 |    5347 |      6545 |       1.94 |        88 |             0 |
| omega1             |     16636 |     970 |    2626 |     13040 |       4.47 |       249 |             0 |
| floor_cheap        |     16636 |    5231 |    5864 |      5541 |       1.67 |        86 |             0 |

Rows with a component above 1024 vertices (floors over the rest): 22; omega censored (2 s / 200000 cliques): 17; edgeless classes: 3; seconds total: 48.

#### (b2) by collection

| collection                   |   classes |   mean n |   mean width |   floor_cheap tight |   gap ≥ 2 |   mean gap |   max gap |   skipped |
|:-----------------------------|----------:|---------:|-------------:|--------------------:|----------:|-----------:|----------:|----------:|
| Rome graphs                  |     11199 |    52.87 |         5.49 |                2896 |      3916 |       1.29 |         6 |         0 |
| MOSP: Challenge 2005         |      3169 |    21.86 |        14.37 |                1459 |       794 |       0.97 |        26 |         0 |
| freetdi control-flow graphs  |      1061 |    55.78 |         2.66 |                 662 |        35 |       0.41 |         3 |         0 |
| MOSP: Faggioli & Bentivoglio |       274 |    31.66 |         8.42 |                  74 |       125 |       1.53 |         5 |         0 |
| MOSP: Chu & Stuckey          |       200 |    71.25 |        40.16 |                   3 |       183 |      12.71 |        44 |         0 |
| PACE 2017 exact              |       129 |   254.86 |        33.81 |                   7 |       116 |       5.33 |        15 |         0 |
| freetdi named graphs         |       126 |    42.79 |        15.63 |                  23 |        84 |       6.71 |        52 |         0 |
| Small (Marti et al. 2008)    |        84 |    20.29 |         3.13 |                  52 |         0 |       0.38 |         1 |         0 |
| PACE 2017 bonus              |        78 |   197.22 |        15.29 |                   0 |        77 |       6.12 |        14 |         0 |
| PACE 2016                    |        70 |    83.66 |        20.09 |                  20 |        31 |       4.10 |        29 |         0 |
| VSPLIB grids                 |        50 |  1078.50 |        29.50 |                   0 |        49 |      26.88 |        54 |        22 |
| VSPLIB Harwell-Boeing        |        44 |   230.73 |        13.73 |                   8 |        29 |       3.64 |        14 |         0 |
| MOSP: Carvalho & Soma 2015   |        38 |   167.11 |       133.18 |                   0 |        38 |      63.89 |        86 |         0 |
| TreewidthLIB colouring       |        33 |   124.24 |        36.79 |                  13 |        15 |       9.27 |        60 |         0 |
| VSPLIB trees                 |        28 |   137.71 |         4.43 |                   0 |        28 |       3.43 |         4 |         0 |
| MOSP: SCOOP                  |        24 |    45.71 |         6.75 |                   6 |         3 |       1.08 |         6 |         0 |
| PACE 2017 heuristic          |        19 |   176.63 |        61.26 |                   3 |        15 |       6.11 |        25 |         0 |
| VLSI gate matrix circuits    |        10 |    30.10 |         7.80 |                   5 |         3 |       0.90 |         3 |         0 |

#### (b3) the certified:minor classes

|   certified:minor classes |   with certificate |   mean size/n |   median size/n |   min size/n |   max size/n |   least-c |   min-d |   refuted = width − 1 |   floor_cheap tight |
|--------------------------:|-------------------:|--------------:|----------------:|-------------:|-------------:|----------:|--------:|----------------------:|--------------------:|
|                       430 |                425 |         0.568 |           0.505 |        0.329 |        0.838 |        46 |     379 |                   425 |                   0 |

#### (c) targets

```
{
 "gap338": 338,
 "cs200": 200,
 "open24": 24,
 "rest500": 500,
 "small": 4123,
 "pool_for_rest500": 5940,
 "pool_by_band": {
  "9\u201320": 4105,
  "21\u201330": 1659,
  "31\u201340": 131,
  "41\u201360": 32,
  "61\u201375": 3,
  "76\u2013100": 10,
  "101\u2013134": 0
 },
 "rest500_by_band": {
  "9\u201320": 345,
  "21\u201330": 140,
  "31\u201340": 11,
  "41\u201360": 3,
  "76\u2013100": 1
 },
 "gap338_and_cs200": 102,
 "small_and_gap338": 17
}
```

---

## 2. Family E by search: the ceiling on every target, the exact profile at `n ≤ 22`, the floor by branch and bound (item 02)

*2026-11-03. Code `learning/obstruction_expansion.py` and its C helper
`learning/obstruction_expansion.c` (compiled on the fly, as `treewidth.c` is);
tests `tests/test_obstruction_expansion.py` (9); files under
`reports/scratch/obstruction_search/02_expansion/`: `ceiling.csv` (4,697
rows: the search's ceiling on every target), `ceiling_s2x3.csv` (a second
search pass, seed 2, triple budget, on `gap338 ∪ cs200`), `exact_small.csv`
(4,123 rows, the exact profile), `floor.csv` (35 rows, the cap-12 branch and
bound rerun where item 01 censored it), `sets/` (one JSON per target: `fhat`,
the best set per `t`, the witness profile, and on the small set the exact
`f` and its minimisers; 10.7 MB) and `sets_s2x3/`, `tables.md` (every table
below, generated), `harness_values.csv` and `harness_table.md` (the floor
through `learning/bound_harness.py`), `run_harness.py`, `run.log`,
`*_run.out`. Regenerate: `nice -n 19 python3 -m learning.obstruction_expansion
--stage ceiling --targets all --workers 8` (65 s wall), `--stage exact
--targets small --workers 4` (1 s), `--stage floor --targets gap338 --workers
8` (22 min wall), `--stage ceiling --targets gap338 --seed 2 --budget-scale 3
--tag s2x3` then the same with `--targets cs200`, `--stage tables`;
`nice -n 19 python3 reports/scratch/obstruction_search/02_expansion/run_harness.py --workers 8`.
Size range: ceiling 9–134 customers (every corpus target; `open24` is item
07's); exact `n ≤ 22`; floor the 35 instances of the 338 item 01 censored
(100–125 customers). Units: optimum units throughout; the ceiling is not a
bound.*

### 2.1 What was done

**The object and the direction.** For the MOSP graph of an instance,
`f(t) = min_{|C| = t} |N[C]|`. Harper's bound is `pw ≥ f(t) − t` at every `t`
(`exists_closedNbhd_card_le`), so family E's bound in optimum units is
`max_t (f(t) − t) + 1`; the empty-pair bound `n − 2 s* − 2 ≤ pw`
(`card_sub_two_mul_emptyPairIndex_sub_two_le_pathwidth`) is the same profile
read through `s* = max_t min(t − 1, n − f(t))`. `satisfiability/expansion_bound.py`'s
`max_i (i − M(i))` with `M(i) = max{t : f(t) ≤ i}` is the same number as
`max_t (f(t) − t)` (take `i = f(t) − 1` one way and `t = M(i) + 1` the
other), so item 01's `harper12` *is* this family's floor at cap 12. A set
`C` of size `t` found by any search proves `f(t) ≤ |N[C]|` and nothing else;
the search's value `max_t (f̂(t) − t) + 1`, `f̂ ≥ f`, is a **ceiling**: if it
is below the optimum, no computation of this family can close the instance.

**The search** (plan §0.5 (c)). Per level `t = 1 … n − 1`, tabu search on
swaps minimising `|N[C]|` over `|C| = t`, on bit masks in C: cover
multiplicities per vertex, a shortlist of six entering vertices by gain and
six leaving by loss, the best of the 36 exact swap deltas applied (tenure
7 ± 2 on both moved vertices, aspiration on the global best), at most
2,000 swaps and a stall limit per restart (40 non-improving swaps in the
sweep, 150 in the focus rounds). Restarts from: every maximal clique
(`networkx.find_cliques` under `islice(200)`), the certified witness's
prefix sets, BFS balls of radius 1 and 2 around every vertex, and the best
set at `t − 1` (ascending sweep) and `t + 1` (descending sweep); then
*focus rounds* on the levels attaining the current `max_t (f̂(t) − t)` —
the ceiling drops only when every argmax level drops — until a round
improves nothing or the wall budget (`0.005 n²` s in `[2, 90]`) runs out.
Every incumbent is re-evaluated in Python from its set before it is
recorded. **The witness's prefixes**: the pattern ordering in
`solutions/<name>.json` induces the customer layout by *opening* time
(first pattern needed); a placed vertex with a neighbour outside the prefix
is open at the next opening position, and so is the vertex opening there,
so this layout's vertex separation is at most `optimum − 1`, and on all
4,697 targets it is exactly `optimum − 1` (`witness_vs_opening` in
`ceiling.csv`; `tests/test_obstruction_expansion.py` asserts it). Its
finished sets `C_i = {v ∈ V_i : N[v] ⊆ V_i}` give `f̂(t) ≤ t + pw` at every
`t`, which is why the ceiling starts at the optimum. **A correction to the
item's text**: the layout by *closing* time (what "a customer closing order
by the instance's simulation" suggests) carries no such guarantee under the
prefix definition — the cost of a layout is not reversal-invariant — and on
`Random-125-125-2-2_0` it has vertex separation 56 against the optimum's 24.
Its finished sets are used as seeds like any other; the guarantee rests on
the opening layout.

**Exact at `n ≤ 22`.** Every subset, by the recurrence
`cover(S) = cover(S ∖ low(S)) ∪ N[low(S)]` over `2^n` masks (16 MB at
`n = 22`, 0.4 ms median): `f(t)` and one minimiser per `t`, the exact Harper
value, `s*` and `n − 2s* − 1`. Checked against a pure-Python enumeration on
150 random graphs and against `expansion_bound`'s levels on 50 corpus
instances (the tests), and on every small instance the ceiling is at least
the exact value.

**The floor.** `expansion_bound(max_t = 12)` rerun on the 35 instances of
the 338 that item 01 censored at 60 s (33 Chu & Stuckey at 100–125, SP4
twice), under 600 s where item 01's cap was at most 10 and 300 s at cap 11
(the item's 10-minute cap halved where only `f(13)` was missing, to fit the
budget; said so here). 26 of 35 completed cap 12; **2.83 core-hours**.

**Through the harness.** `harper_floor` is registered as an `--extra`
candidate (`learning.obstruction_expansion:harper_floor`: the cap-12 branch
and bound under the harness's budget, 10 s) and run through the validity
stage on the whole corpus; the table is `harness_table.md` (§2.3).

### 2.2 Numbers

**The ceiling, 4,697 targets** (`gap338 ∪ cs200 ∪ rest500 ∪ small`; 65 s
wall, **0.14 core-hours**; the search ended on a non-improving focus round
on 4,640, never on the budget). Ceiling above the optimum: **0**; below the
exact bound (small set): **0**; below `harper12`: **0**.

| target | instances | ceiling = optimum | ceiling < optimum | ceiling gap mean / max | floor gap mean / max | floor tight | bracket 0 | bracket mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `gap338` | 338 | 18 | **320** | 1.66 / 5 | 3.79 / 27 | 7 | 193 | 2.13 |
| `cs200` | 200 | 64 | 136 | 0.90 / 3 | 3.90 / 27 | 57 | 116 | 3.00 |
| `rest500` | 500 | 341 | 159 | 0.37 / 4 | 0.37 / 4 | 341 | 499 | 0.01 |
| `small` | 4,123 | 2,933 | 1,190 | 0.32 / 4 | 0.32 / 4 | 2,933 | 4,122 | 0.00 |
| all | 4,697 | 3,099 | 1,598 | 0.42 / 5 | 0.58 / 27 | 3,088 | 4,547 | 0.16 |

(The floor here is `max(harper12, floor rerun)`; "bracket" is
`ceiling − floor`; "bracket 0" means the family's duality gap is exact.)
The ceiling's gap is 1 on 1,259 instances, 2 on 295, 3 on 37, 4 on 6 and 5
on 1 (`scoop-A_FA+AA-_6_0`, 79 customers, optimum 13, ceiling 8; the four
at 4 are two Harvey instances at 30, `p1550n8_0` and `p1550n1_0`); on the
338 it is 0 / 1 / 2 / 3 / 4 / 5 on 18 / 112 / 181 / 22 / 4 / 1.

**What the ceiling says about the 338.** On **320 of 338 the ceiling is
below the optimum: the expansion family cannot close them under any
computation**, however deep the cap. The 18 where it could — the ceiling
sits at the optimum — are two Harvey (`n = 30`), five Faggioli–Bentivoglio
(39–50) and eleven Chu & Stuckey (`50-50-2-1`, `75-75-6-3`, `100-100-4-2`,
`100-100-6-3`, `100-100-8-2`, `100-50-10-1`, `125-125-10-3`, `125-125-10-5`,
`125-125-8-1`, `125-125-8-3`, `125-125-8-4`); the floor already closes 7 of
them (`floor_tight` on `gap338`), and 11 are open between floor and
ceiling — item 03's list. Against the record: the ceiling is at or below
`floor0` on **249 of the 338** (family E can never beat what the other
families already proved there) and above it on 89, all Chu & Stuckey,
Faggioli–Bentivoglio at 40–50 and the SP instances. Over all 4,697 targets
the ceiling equals `floor0` on 3,352, is below it on 1,256 and above it on
the same 89.

**By size and class.** The ceiling's gap is about one stack everywhere
(band means 0.32 at 9–20, 0.9–1.5 above) and does not grow with `n`; the
*floor's* gap does (0.32, 1.16, 1.32, 1.88, 3.26, 7.39, 10.19 across the
seven bands), so the bracket opens from 0 at `n ≤ 30` to 9.1 at 101–134: on
the large instances almost all of the family's duality gap is *unknown
side*, the part item 03's exact half must settle. On the 200 Chu & Stuckey
by class (`tables.md` (d)): the ceiling is at the optimum on 0 of 5 in
every density-2 and density-4 class from 30 to 125 customers and on 3–5 of
5 at density 8–10; the gap is 2.0 on `125-125-2` and 0.2 on `125-125-10`.
The argmax level `t*` sits at a fraction of `n` that falls with density:
median `t*/n` 0.37 on `125-125-2`, 0.25 on `125-125-4`, 0.09 on
`125-125-10`; 0.10 over all targets.

**The search against the witness.** The witness's own prefixes give a
ceiling at the optimum on 4,577 of 4,697 and below it on 120; the search
lowers the witness's value at 79% of the levels at 101–134 customers (14% at
9–20) and lowers the *ceiling* below the witness's on 1,519 instances. So
the planner's third risk (§0.8: "the ceiling is the optimum almost
everywhere") did not materialise: the search finds sets the witness does
not, and the ceiling is strictly informative on a third of the targets and
on 95% of the 338.

**The second pass** (`s2x3`: seed 2, budget ×3, 436 instances of
`gap338 ∪ cs200`, 0.13 core-hours): the ceiling is equal on 432, lower on 1
(`HS problem 1195`, 13 → 12) and higher on 3 (`HS problem 1181`,
`Random-100-50-10-4_0`, `Random-100-50-6-3_0`, each by one). The ceiling is
therefore a search artefact at the ±1 level on about 1% of the instances at
30–100 customers; the minimum of the two passes is below the optimum on 365
of the 436 (pass 1 alone: 364). Both passes are valid ceilings; the tables
quote pass 1.

**Exact at `n ≤ 22`** (4,123 instances, 0.4 ms median each). The search
attains `f(t)` at every `t` on **4,090 of 4,123 (99.2%)**; the 33 misses
are one level each, by exactly one vertex, 31 of them at `n = 20` and 2 at
`n = 15`, and none at an argmax level: the ceiling equals the exact bound
on **4,123 of 4,123**. Harper exact equals the optimum on **2,933 (71.1%)**:
78% at `n = 10`, 75% at 15, 59% at 20; the empty-pair value equals the
optimum on 748 (18.1%) and is never above the Harper value (it is a
weakening of the same profile: strictly below on 3,473 of the 4,697
targets, equal on 1,224). Against the record: the exact bound exceeds
`harper12` on one instance (`scoop-B_18CR1_33_0`, `n = 19`, optimum 4,
where `expansion_bound` reports 0 for "no level improves" and the exact
value is 1 — a convention, not a bound) and exceeds `lb_best` and `floor0`
on **none**: at these sizes the full-depth expansion family adds nothing to
what is on record.

**The floor rerun** (35 instances, `tables.md` (e)). The floor rose on 32 of
35, by 1.9 stacks on average and by up to **6** (`Random-125-125-6-4_0`
63 → 69, `6-3_0` 64 → 70, `8-5_0` 83 → 88 — all still 5–11 below the
optimum); it is **above `floor0`, the best floor on record, on 17 of the
35** (every density-6 and density-8 125 × 125 instance, `4-1_0`, `4-3_0`,
`100-100-4-2_0`, …): the cap-12 branch and bound at ten minutes is a new
record floor there. The bracket closes on 2 (`125-125-10-2_0`, floor =
ceiling = 103 against 104: the family's duality gap is exactly 1 and it can
never close the instance; `125-125-10-5_0`, floor = ceiling = optimum = 99)
and the floor equals the optimum on 1. On the ridge classes it buys one
stack from a floor of 6–8 against optima of 20–25 (`125-125-2`), and there
the minor certificates on record (`floor0` 20–24) are the whole story.
Nine of the 35 did not complete cap 12 in 600 s (every `125-125-2` but
`2-1_0`, `4-3_0`, `6-1_0`, `6-4_0`, `6-5_0`, `8-5_0`); their values are
valid at the cap reached.

### 2.3 Through the harness

`python3 reports/scratch/obstruction_search/02_expansion/run_harness.py
--workers 8` (the CLI form `python -m learning.bound_harness --stage validity
--workers 8 --sources corpus --candidates "" --extra
learning.obstruction_expansion:harper_floor`, written to the item's
directory so that loop0004's values file is left alone): 6,376 corpus
instances, 10 s per instance, 144 s wall, **0.32 core-hours**, no
candidate censored, no error. `harness_table.md`:

| bound | rows | above optimum (must be 0) | tight, all | > `lb_best`, all | tight, gap | > `lb_best`, gap | > reference, gap | beats reference, gap (count) | mean shortfall, gap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `tw + 1` (`tw_lo`) | 6,376 | 0 | 0.887 | 0.146 | 0.198 | 0.589 | 0 | 0 | 8.88 |
| `lb_best` | 6,376 | 0 | 0.770 | 0 | 0 | 0 | 0 | 0 | 4.78 |
| reference `max(lb_best, tw + 1)` | 6,376 | 0 | 0.896 | 0.146 | 0.198 | 0.589 | 0 | 0 | 3.92 |
| **`harper-floor`** (cap 12, 10 s) | 6,376 | **0** | 0.637 | 0.021 | 0.012 | 0.337 | 0.216 | **73** | 4.49 |

"Above optimum" is 0, which is the check the acceptance criteria ask for.
At 10 s the floor is tight on 63.7% of the corpus (item 01's 60 s run:
`harper12` tight on more, the dense instances needing the time) and beats
the harness's reference on 73 of the 338 gap instances — the same family
that §38 of `ml_nature.md` found no branching candidate could beat. It is a
floor of a different kind from the reference's two (degree and treewidth),
which is why it passes the treewidth ceiling the bounds section of
`CLAUDE.md` describes.

### 2.4 Kill verdict and compute

**Kill criterion (plan §0.9, E-search): not met.** The search attains
`f(t)` at every `t` on 99.2% of the instances at `n ≤ 22`, against the
criterion's 90%; the ceiling is not search-limited there and equals the
exact bound on every one. Above 22 the second pass moves it by ±1 on 1% of
the instances. Item 03 can seed its SAT calls from the search's sets and,
where they exist, from the exact minimisers (`sets/<name>.json`, keys
`sets` and `exact_sets`). The two bug conditions — a ceiling below the
floor, a floor above the optimum — occurred on **0** instances.

**Compute.** Ceiling 0.14, exact 0.00, floor 2.83, second pass 0.13,
harness 0.32: **3.4 core-hours** against the item's 3. The floor's
ten-minute cap was halved where only one level was missing; the overrun is
the second pass (a robustness check the item did not ask for) and the
harness run the acceptance criteria require.

### 2.5 What this does not claim

That the ceiling is attained by any computation (a ceiling is an upper
estimate of what the family can prove; the family's true value sits in
`[floor, ceiling]`); that the floor is the family's best (the exact half
above cap 12 is item 03); that the search's `f̂` equals `f` above 22
customers (measured only to 22; the second pass's ±1 says it does not
always); that any of this changes a solver (no candidate reaches
`_lower_bound`); that the 17 new record floors are anything but the cap-12
bound given more time. The closing-layout correction is a statement about
our construction of seeds, not about Yanasse's equivalence. "We found no
prior report" of a searched vertex-isoperimetric ceiling on benchmark
instances; the bound itself is Harper (1966).

## 3. Family E exact at full depth: the inner minimum by SAT with DRAT; the gap bracket closed where it settles (item 03)

*Size range: the 338 bound-gap instances (20–134 customers) and the 200
Chu & Stuckey instances (30–125); the encoding's self-test at `n ≤ 12`.
Regenerate: `nice -n 19 python3 -m learning.obstruction_expansion --stage sat
--targets gap338,cs200 --workers 8 --core-hours 6`, then `--stage sat-tables`;
`python3 reports/scratch/obstruction_search/03_sat/recheck_certificates.py
--workers 8` (every certificate through the checker);
`python3 reports/scratch/obstruction_search/03_sat/run_harness.py --workers 8`
(the validity stage); `python3 paper1/obstruction_check.py check-expansion
<instance.mosp> <certificate.json>` on any one certificate. Outputs under
`reports/scratch/obstruction_search/03_sat/`: `levels.csv` (344 calls),
`instances.csv` (144 instances), `boundary.csv`, `tables.md`, `joined.csv`,
`checker_verdicts.csv`, `harness_values.csv`, `harness_table.md`,
`certificates/<instance>/`, `run.log`, `../03_sat_run.out`. Tests:
`tests/test_obstruction_expansion.py` (24, of which 6 are this item's).*

### 3.1 What was done

**The question.** Item 02 left family E bracketed on 148 of the 436 targets
in `gap338 ∪ cs200` (145 of the 338, 3 more Chu & Stuckey): the ceiling
(the search's `max_t (f̂(t) − t) + 1`) above the floor (Harper's bound with
`f` proved by branch and bound to cap 12). Above cap 12 the branch and bound
does not finish, so this item asks the inner minimum of a SAT solver: for a
level `t` and a target `b`, "is there a set `C` of at least `t` customers
with `|N[C]| ≤ b`?" UNSAT proves `f(t) ≥ b + 1`, hence `pw ≥ b + 1 − t` and
`MOSP ≥ b + 2 − t` by the contrapositive of `exists_closedNbhd_card_le`
(`lean/MOSPFormalization/EmptyPair.lean`) and `mospValue_eq_pathwidth_add_one`;
SAT returns a set that lowers `f̂(t)`, so the ceiling drops. Either answer
moves one half of the bracket, and the level is settled when the two meet.

**The encoding** (`learning/obstruction_expansion.py::expansion_cnf`, the
contract `ENCODING_SPEC`, plan §0.5 (d)): `x_v` (`v ∈ C`), `y_v`
(`v ∈ N[C]`), the clauses `x_u → y_v` for every `v ∈ N[u]` including `u`, a
full totalizer over the `x` with the unit `o_t` (`Σ x ≥ t`) and one over the
`y` with the unit `¬o_{b+1}` (`Σ y ≤ b`), the auxiliaries of the two
totalizers in disjoint ranges allocated in a fixed order (the
`mosp_encoding.py` discipline). The totalizer is ours, not pysat's
`CardEnc`: the contract has to fix every variable number so that the
checker can regenerate the clause set, and a library's allocation order is
not a contract. The clause set is canonical (sorted literals, sorted
distinct clauses) and the certificate carries the SHA-256 of its DIMACS
text. `exact_sat(closed, t, b, proof_dir)` solves it with CaDiCaL 1.9.5
through pysat with proof logging, under a conflict budget (2 × 10⁶) and a
wall deadline (120 s) — pysat's CaDiCaL cannot be interrupted, so with a
deadline the call runs in a forked child that is killed at the deadline
and dies with its parent (`PR_SET_PDEATHSIG`); the proof is read after a
C-side flush, as `learning/proofs.py` learnt to; every UNSAT is checked by
`drat-trim` at once and the certificate JSON (`(t, b)`, the CNF's hash
and size, the gzipped proof and its hash, the solver, the conflicts, the
checker's binary hash and verdict) is written beside it. A SAT model's set
is re-evaluated from the masks and never read from the `y` variables; a
model with more than `t` members is cut to `t` (a subset's closed
neighbourhood is smaller).

**The driver** (`--stage sat`): for each instance of `gap338` then `cs200`,
smallest `n` first, the levels the ceiling marks relevant — `t` above the
proved cap with `f̂(t) − t + 1 > floor` (the item's `≥ floor − 1` in
pathwidth units includes equality; a level at the floor can neither raise
it nor move the bracket, so equality is left out), nearest the argmax `t*`
first, at most 8 per instance — and at each level a descent in `b` from
`f̂(t) − 1`: the first probe asks whether the incumbent is the minimum
(UNSAT settles the level in one call, which is the common case: item 02's
search attains `f` at 99.2% of levels at `n ≤ 22`); after a SAT answer
(a new incumbent, `f̂(t)` falls) or a censored call the next probe is the
midpoint of what is unresolved, so a censored boundary still leaves the
cheaper, lower `b` to try; an UNSAT at any `b` raises the floor to
`b + 2 − t` even when the level is not settled ("partial"). 240 s per
instance, a hard stop at 6 core-hours (wall × workers), 8 workers at
`nice 19`, the machine's load 2–6 during the run. The exact floor after the
run is the cap-12 floor raised by every SAT-proved level; the ceiling after
the run is `max_t (f̂(t) − t) + 1` over the incumbents with the proved levels
exact. Outputs: `levels.csv` (one row per call), `instances.csv` (one row
per instance), `certificates/<instance>/` (`instance.mosp` in the standard
format, `calls.jsonl`, `summary.json`, and per proved level
`t<t>_b<b>.json` with `t<t>_b<b>.drat.gz`), `boundary.csv`, `tables.md`.

**The checker** (`paper1/obstruction_check.py check-expansion <instance.mosp>
<certificate.json>`): its own reader of the standard format, its own MOSP
graph (a clique per pattern), its own totalizer from the contract, which it
carries verbatim in its docstring (the test pins the two texts equal; the
checker imports nothing from `learning/`, `satisfiability/`,
`pathwidth_solver/` or `mosp/`), regenerates the CNF, compares its hash and
size with the certificate's, compares the SHA-256 of the instance's rows,
decompresses the proof, runs `drat-trim` on the regenerated CNF and prints
the bound with the theorems it rests on; exit status 0 only when every
check passes. The instance file the checker reads is the one the run wrote
beside the certificate; the certificate records the benchmark file it came
from (`source_file`), and the rows' hash ties the two.

### 3.2 Numbers

**The headline.** Of the 148 targets with a bracket after item 02 (145 of
the 338, 3 more in `cs200`), 144 were reached within the budget and the
bracket closed on **72**: the family's duality gap is now exact on 264 of
the 338 (193 after item 02), the floor rose on 85 targets and the ceiling
fell on 3. **Where it closes is a question of size, not of level**: every
bracket at 30–60 customers closed (1 + 19 + 48 of 68, all argmax levels
settled, every one in a single UNSAT call at the incumbent or after one SAT
answer), 2 of 13 at 75, 1 of 41 at 76–100 (a SCOOP instance), 0 of 22 at
101–134. The run used **5.76 core-hours** of instance time and stopped at
its 6-core-hour cap with 3 instances not reached (`Random-125-125-8-5_0` of
the 338; `Random-100-50-2-2_0` and `Random-100-50-2-4_0` of `cs200` only).

| target | had bracket | reached | bracket closed | argmax settled | floor raised | ceiling lowered | floor gap before → after | bracket before → after | closed by floor | ruled out by ceiling | open with bracket | floor > reference |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gap338` | 145 | 143 | 71 | 70 | 84 | 3 | 3.79 → 3.41 | 2.13 → 1.74 | 7 → **12** | 320 | 11 → **6** | 87 → **98** |
| `cs200` | 84 | 81 | 15 | 15 | 27 | 0 | 3.90 → 3.68 | 3.00 → 2.79 | 57 → 58 | 136 | 7 → 6 | 70 → 74 |

(`tables.md` (a); "reference" is the harness's `max(lb_best, tw + 1)`.)
The five instances the exact floor newly closes on the 338 are `p2540n3_0`
(8 → 10 = optimum), `Random-50-50-2-1_0` (13 → 15), `p4050n10_0` (11 → 14),
`p4050n4_0` and `p4050n7_0` (12 → 14); on all five the cap-12 branch and
bound had the right argmax level in sight and the SAT call proved its
incumbent in under 6 s. The six of the 338 still open with a bracket are
all dense and large — `Random-100-100-4-2_0` (floor 40, ceiling = optimum
50), `100-100-6-3_0` (55 / 61), `100-50-10-1_0` (64 / 68), `125-125-8-1_0`
(94 / 95), `8-3_0` (92 / 95), `8-4_0` (93 / 94) — the instances where Harper
*could* be tight and the inner minimum at `t ≈ 15–25` on a 100–125-vertex
graph is what no call finishes (below).

**The floor, by band of the 338** (`tables.md` (b); mean gap `optimum −
floor`, optimum units): 9–20: 2.06 → 2.06 (no bracket to close; the family
is ruled out by its ceiling on all 17); 21–30: 1.98 → 1.98; 31–40: 1.96 →
**1.49**; 41–60: 2.78 → **1.43**; 61–75: 4.88 → 3.65; 76–100: 8.51 → 8.29;
101–134: 11.00 → 10.84. Where the floor rose, it rose by 1.15 at 31–40
(max 2), 1.52 at 41–60 (max 3), 2.33 at 61–75 (max 4), 1.67 at 76–100 and
2.0 at 101–134 (max 3): the SAT half adds one to four stacks to the cap-12
floor, and at 41–60 it removes half of the family's remaining gap. Thirteen
instances had their floor raised by a *partial* level alone (an UNSAT at a
`b` below the incumbent, the level itself unsettled) — the midpoint probe
after a censored call is what bought these.

**The ceiling fell on three instances**, all by one and all through the SAT
answers' sets: `Warwick 1299` (11 → 10 = floor: duality gap exactly 2
against an optimum of 12), `p2550n8_0` (9 → 8 = floor; optimum 11) and
**`scoop-A_FA+AA-_6_0`** (79 customers; 8 → 7 = floor; optimum **13**),
where nine SAT answers at `t = 30–52` each found a `t`-set one below the
search's incumbent (the sets' values are in `levels.csv`, column `nbhd`),
so the family's exact value on that SCOOP instance is **7, six stacks
below the optimum**, settled on both sides: the exact duality gap of the
expansion family on an industrial instance. Item 02's second pass had
already moved the ceiling by ±1 on 1% of the instances at 30–100; the 18
SAT answers (3 at `n ≤ 40`, 3 at 50, 9 on the 79-vertex SCOOP instance,
2 at 105, 1 at 134) are the exact-half view of the same ±1 artefact: on
sparse SCOOP graphs the tabu search's incumbents are off by one at several
levels at once.

**The boundary in `(n, t)`** (`tables.md` (d), (e); `boundary.csv`). Of 344
calls, 155 UNSAT (every one verified by drat-trim), 18 SAT, 79 out of
conflicts (2 × 10⁶), 92 killed at the 120 s deadline, 0 errors. Finished
share by band of `n` and `t`:

| `n` | `t` 13–15 | 16–20 | 21–25 | 26–30 | 31–40 | 41+ | median s (finished) |
|---|---:|---:|---:|---:|---:|---:|---:|
| ≤ 60 | 36/36 | 49/49 | — | — | — | — | 0.1–0.8 |
| 61–75 | 2/2 | 8/17 | 11/19 | 5/10 | 2/4 | — | 15 |
| 76–100 | 2/6 | 2/23 | 6/31 | 9/19 | 8/28 | 23/29 | 0.8–48 |
| 101–134 | 0/8 | 0/12 | 0/15 | 0/3 | 3/18 | 7/15 | 15–44 |

Every call at `n ≤ 50` finished (max `t` settled 20 at `n = 50`, in 0.58 s
at the median, 281 k conflicts at most); at `n = 75` the finished share is
28 of 52 and the deepest settled level is 15 (`Random-75-75-6-4_0`), the
shallowest censored 19; at `n = 100` 22 of 108 finished and no level at
all settled on the `Random` instances (max `t` settled: none), while the
two SCOOP instances at 79 and 105 settled levels at `t = 52` and `t = 46`
(28 of 28 and 4 of 5 calls finished: their graphs are sparse, `optimum / n
≈ 0.1–0.16`, and the CNF a third the size); at `n = 125` 3 of 62 finished,
all at `t ≥ 33` and `b ≤ 49`, levels the ceiling marks but far from the
argmax. **The boundary is `n ≈ 60–75` on the Chu & Stuckey graphs at the
levels that matter (`t* ≈ 0.2–0.35 n`), and it is a boundary in `n` at a
given density rather than in `t`**: the finished share at 76–100 *rises*
with `t` (0.09 at 16–20 to 0.79 at 41+) because the deep levels are the
sparse instances' and `b` is close to `n` there (the `Σ y ≤ b` totalizer is
nearly free), while at 101–134 nothing below `t = 31` finishes. Clause
counts are 4–6 k at `n ≤ 50`, 14 k at 75, 24–26 k at 100 and 36–41 k at 125;
the finished calls' conflicts reach 1.3 M at 75 and 1.1 M at 100, so the
2 × 10⁶ budget is binding at the boundary rather than generous: a 10× budget
would move it by one band at most, on the exponential the `t`-profile
shows, and is not what the plan's §0.8 (1) risk asked (the risk is
realised as stated). The analogue of §17's `m² · k ≈ 10⁴` is **`n ≈ 75` at
`optimum / n ≈ 0.2–0.5`**, i.e. the dense half of the Chu & Stuckey corpus
above 60 customers is out of the exact half's reach at 2 × 10⁶ conflicts
and 120 s per call; drat-trim's check costs 0.3–3× the solve (median 15–45 s
at 75–125, 1,127 s in total for the 158 certificates on disk, the largest
proof 38.7 MB gzipped, every one under the 50 MB per-file limit). **The
proofs are kept on disk and not in the repository**: 1.3 GB over 158 files
is not a committable artifact, so `.gitignore` carries
`reports/scratch/obstruction_search/**/*.drat.gz` (as `learning/data/proofs/`
is ignored for `learning.proofs`); every certificate JSON beside them records
the proof's SHA-256, size and lemma count, and the stage's command regenerates
them. A checkout without the proofs has the hashes and the CNF contract, and
the checker reports "proof present: False" rather than a verdict.

**The certificates.** 158 certificate files on disk (155 from the 144
reached instances, with their rows in `levels.csv`; 3 on the two `cs200`
instances the cap interrupted, valid but outside the tables — they prove
`f(43) ≥ 46` on `Random-100-50-2-2_0` and `f(45) ≥ 48` on `-2-4_0`, both
below those instances' floors), **158 of 158 verified** by
`paper1/obstruction_check.py` (`checker_verdicts.csv`): the regenerated CNF's
hash and size equal the certificate's on every one, the rows' hash ties the
instance, drat-trim verifies the proof on the regenerated CNF, max 45 s.
Every bound the item claims is read off a certificate in that file and
rests on `exists_closedNbhd_card_le` (contrapositive) and
`mospValue_eq_pathwidth_add_one`, both `sorry`-free in the development; the
checker trusts drat-trim and those two theorems and nothing of ours.

### 3.3 Through the harness

`run_harness.py --workers 8`: the exact floor as a lookup candidate
(`sat_floor`: the run's `floor_after` by the SHA-256 of the instance's rows,
1 where the run has no record) through `learning.bound_harness`'s validity
stage on all 6,376 corpus instances (`harness_table.md`): **above optimum
0**; beats the reference `max(lb_best, tw + 1)` on **74 of the 338** (item
02's cap-12 floor at 10 s: 73; at item 01's 60 s and item 02's 600 s, the
cap-12 floor already stood above the reference on 87 of the 338, and the
exact floor on 98, `tables.md` (a) — the harness's 74 counts the 144
instances the run reached and nothing else). The ledger's guard (item 01)
and the run's own guard (`floor_after ≤ optimum`, `floor_after ≤
ceiling_after`, asserted in `tests/test_obstruction_expansion.py::test_committed_sat_files`)
hold on every row.

### 3.4 Kill verdict and compute

**Kill criterion (plan §0.9, E-exact): met, narrowly on the sensible
reading and clearly on the literal one.** SAT settled the argmax level on
70 of the 145 instances of the 338 that had a bracket (48.3%, against the
criterion's 50%); counted over the 338, the argmax level is settled on 264
(78.1%) after the run, 70 of them by SAT (20.7%). The record therefore
says: **Harper exact is out of reach by SAT above cap 12 at 75 customers and
beyond on the Chu & Stuckey graphs** (boundary `n ≈ 60–75` at the argmax
levels, 2 × 10⁶ conflicts, 120 s per call) **and fully in reach to 60**,
where every bracket closed in seconds. The family's floor downstream is the
exact floor where a verified certificate proves it (144 instances,
`instances.csv::floor_after`) and the cap-12 floor elsewhere; nothing in
the floor rests on the search's quality or on a censored level. The second
kill condition — an UNSAT at a `(t, b)` where item 02's enumeration has a
set — occurred on **0** calls (the self-test at `n ≤ 12` agrees with the
enumeration on 3,000+ `(t, b)` pairs over 100 graphs, and the run's SAT
answers all have `|N[set]| ≤ b` re-evaluated from the masks).

**Compute.** Instance time 5.76 core-hours (solve 5.24, in-run drat-trim
0.45, the rest the forks and the writes), the checker sweep 0.31, the
harness run under 0.01 (a lookup), the smoke run and four timing probes
≈ 0.1: **≈ 6.2 core-hours** against the item's 6; the overrun is the
independent re-check the acceptance criteria require. 8 workers at
`nice 19`; the machine's one-minute load was 2–8 during the run (the
owner's `run_unlimited.py` was not running). Wall 45 min.

### 3.5 What this does not claim

That the SAT route scales beyond the boundary it measures (a call censored
by its conflict budget or its deadline says nothing about `f(t)`, and no
censored call contributes to any floor); that a larger budget would not
move the boundary (not measured; the conflict counts of the finished calls
at 75–100 say a 10× budget would at most reach one more band); that the
exact floor on the 144 reached instances is the family's best (levels the
ceiling did not mark, and the three unreached instances, were not asked;
at most 8 levels per instance and 240 s, which at `n ≥ 75` meant one or
two levels); that the ceiling after the run is the family's value (it is an
upper estimate still, exact only where it meets the floor: 72 targets); any
solver change (no candidate reaches `_lower_bound`; the family's bound as a
bound inside the search was a net loss, `reports/expansion_bound.md`, which
this item does not revisit). The certificate for an instance is a proof
about *that instance file*: the checker reads the `.mosp` file the run
wrote beside it and ties it to the benchmark source by the rows' hash
recorded in the certificate, not by re-reading the benchmark file's own
format. "We found no prior report" of DRAT-certified vertex-isoperimetric
profiles on MOSP instances; the bound is Harper (1966), the totalizer
Bailleux & Boufkhad (2003), the checker drat-trim (Wetzler, Heule & Hunt
2014).
