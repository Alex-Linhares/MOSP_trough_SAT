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

## 4. Family M by search: the contraction-sequence search, its certificate and checker; the 338 at `n ≤ 60` against the greedy ladder (item 04)

*Size range: the 251 instances of `gap338` with at most 60 customers (in
fact 20–50: the set has nothing at 51–60); validation on 50 corpus instances
at `n ≤ 16` and on the six certificates of
`reports/minor_bound_verification.md` (58–120-vertex minors). Regenerate:
`nice -n 19 python3 -m learning.obstruction_minor --stage validate`;
`nice -n 19 python3 -m learning.obstruction_minor --stage run --targets
gap338 --max-n 60 --workers 8 --seconds 60,120`; `--stage check --workers 8`
(every certificate through the independent checker, rule-free included);
`python3 reports/scratch/obstruction_search/04_minor/run_harness.py
--workers 8` (the validity stage); `--stage tables`; `python3
paper1/obstruction_check.py check-minor <instance.mosp> <certificate.json>`
on any one certificate. Outputs under
`reports/scratch/obstruction_search/04_minor/`: `search.csv` (251 rows, the
ladder's and the search's result per instance), `ladder.csv` (2,155 ladder
points), `joined.csv`, `certificates/<instance>/{instance.mosp, search.json,
ladder.json, ladder_points.json}`, `checker_verdicts.csv`, `validation.log`,
`validation_small.csv`, `validation_recorded.csv`, `validation_recorded/`,
`harness_values.csv`, `harness_table.md`, `tables.md`, `run.log`, the three
`check_attempt*.out` of §4.1, and `../04_minor_{validate,run,check}.out`.
Tests: `tests/test_obstruction_minor.py` (11).*

### 4.1 What was done

**The question.** Family M is the one obstruction family on record that
reaches the ridge instances (item 01: minors close 4 of the 5
`Random-125-125-2` instances) and the one that is a genuine maximisation
(plan §0.2): any contraction minor `H` of the MOSP graph with a proved
pathwidth `p` certifies `MOSP ≥ p + 1`, by minor monotonicity
(`pathwidth_gt_of_minorOf`, `lean/MOSPFormalization/Minor.lean`) and
`mospValue_eq_pathwidth_add_one`. What is on record is the *greedy ladder*
(`satisfiability/relaxation.py::minor_sequence`, the C program's own minor
step): two contraction rules (`min-d`, `least-c`), fixed sizes, a refutation
attempted on each. This item asks whether a local search over contraction
*sequences* finds minors the ladder misses, at equal caps and equal total
time; what the family's duality gap is on the 338 at `n ≤ 60`; and what a
minimal certifying minor looks like.

**The search** (`learning/obstruction_minor.py`, plan §0.5 (e)). The state
is a sequence of `(v, u)` pairs in the instance's customer labels (contract
`v` into `u`; `(v, −1)` deletes an isolated `v`), replayed by `replay`, which
mirrors `relaxation.minor_groups`'s checks on masks (every pair an edge of
the current graph, a deletion only of an isolated vertex) and raises on any
violation. Moves: delete a pair (the minor grows by a vertex), insert a pair
(an edge of the current minor), retarget a pair to another current
neighbour of `v`, move a pair earlier; the result goes through `repair`
(a dead `v` drops the pair, a `u` no longer adjacent is retargeted to `v`'s
current neighbour of least degree, a `v` left with no neighbour becomes a
deletion). Tabu tenure 10 on the absorbed vertex, with aspiration; restarts
cycle through the two greedy rules at 50, 60, 70, 80, 90 and 95% and the
incumbent, 25 moves each; plateau moves are accepted (equal floor, at most
one vertex larger). **Evaluation** of a candidate minor `H`: the certified
witness's opening layout lifted to `H` (each branch set at its first
member's position; a proof that the lifted layout's vertex separation never
exceeds the original's is in `lifted_layout`'s docstring and the inequality
is asserted on 300 random graphs by a test) and a greedy layout give an
upper bound on `pw(H)`; a candidate whose upper bound cannot improve the
best floor so far is not sent to the C program (a cache by edge hash
removes repeats); otherwise one call
`printf '%s\n' "$g6" | nice -n 19 pathwidth_solver/cli/pathwidth -t 2 -l -v -m min_vertices=1000000`
(graph6 by networkx, labels `0..m−1` in increasing order of the surviving
representative; the C's own minor step disabled, so the certificate is
ours), parsed for `pathwidth <w> <status>` and stderr's `lower=`: the floor
certified is `w + 1` on `refutation` or `bound`, `lower + 1` on `upper`.
The objective is the certified floor in optimum units, ties by fewer
vertices. **The baseline** is the ladder — both rules, 50–85% in 5% steps
then 90 and 95% — through the same evaluator at the same cap; it stops
when its floor reaches the optimum (its points come in increasing size, so
the first is its smallest certifying point). Both get the same budget per
instance, 60 s at `n ≤ 40` and 120 s at 41–60; the search runs its whole
budget, minimising the vertex count once at the optimum. The C binary's
SHA-256 (`6560b809…`) is in every certificate.

**The certificate** (`certificates/<instance>/search.json`, format
`obstruction-minor-1`): instance name, `n`, the SHA-256 of the rows and of
`G`'s edge list, the sequence, `m`, the minor's labels, edges and edge hash
(the contract: SHA-256 of `"m e\n"` then one `"a b\n"` per sorted edge),
the C's width, status and `lower`, the pathwidth proved and the width
refuted, the C's stdout and stderr verbatim, its binary's SHA-256, the cap,
the seconds, and the theorems. The ladder's best point is written beside it
as `ladder.json`, with every ladder point in `ladder_points.json`.

**The checker** (`paper1/obstruction_check.py check-minor`; imports nothing
from `learning/`, `satisfiability/`, `pathwidth_solver/`, `mosp/` or
networkx — a test pins this): its own `.mosp` and edge-list readers, its own
MOSP graph, its own contraction replay (dict-of-sets, as `mc_graph.py`),
the quotient rebuilt from the branch sets and compared with the replayed
minor, the edge hash compared with the certificate's, its own graph6
encoder (equal to networkx's on 300 random graphs, by a test), the C program
re-run on the minor at the cap ×5 and accepted only if it proves at least
the claimed pathwidth, and, where `m ≤ 80`, `vsmemo.c` and `checkF.c` from
`reports/scratch/minor_certificates/` compiled into a temporary directory
and run for a rule-free refutation of `claim − 1` (`vsmemo -o -w F`, cap
300 s, 10⁸ states, an 8 GB address-space limit) with `checkF` on the family
of sets. The verdict is `verified` when replay, hash and C agree; the
rule-free outcome (`verified` / `unknown` / `skipped` / `failed` / `sat`)
is recorded beside it, and a `sat` or `failed` rejects.

**Validation before the 338** (`validation.log`). (i) 50 corpus instances
at `n ≤ 16` (seed 0 from `targets.small`): every ladder point with the skip
disabled and every minor the search proposed in 10 s — **1,485 distinct
minors, 1,485 C calls** — compared with
`learning.first_moment.vertex_separation_brute`: **0 disagreements**. (ii)
The six recorded certificates (`Random-125-125-2-3_0` m70, `2-1_0` m87,
`6-1_0` m120, `SP4` m96, `myciel6` m58, `myciel7` m110), converted from
`mc_graph.py`'s `[keep, absorbed]` convention to this item's `[absorbed,
keep]` and run through the checker with the C at 60 s: **6 of 6 replay,
6 of 6 hash-match, 6 of 6 re-proved by the C at exactly the recorded
width** (statuses all `refutation`; 0.03–28 s, the 87-vertex minor the
slowest). The rule-free check was not repeated on them (they are
rule-free certified on record).

**The run** (`run.log`). 251 instances, started at 8 workers under a
one-minute load of 2.4; after 74 instances the load rose to 48–59 from the
owner's chrome/puppeteer processes and the run was stopped and resumed at 4
workers (the stage resumes by instance name; the in-progress instances were
redone), then at 8 again when the load fell to 4 after 114. The search's
budgets are wall-clock, so the instances run under load got fewer moves per
second; nothing else changes. Wall 1,084 + 604 + 1,015 s in the three
segments.

**Three checker attempts, two bugs in the checker, none in a certificate**
(`check_attempt{1,2,3}.out`). The first sweep crashed with "branch sets do
not partition the vertex set": the checker's partition check ignored
isolated-vertex deletions. The second, counting the deleted vertex, still
rejected 5 certificates (`p1540n3_0`, `p1550n8_0`, `p2050n4_0`, `p2550n4_0`,
`p2550n5_0`): in each, a whole component (a 4-customer pattern clique, e.g.
`{9, 14, 23, 37}` of `p1540n3_0`) had been contracted to one vertex and
*then* deleted as isolated — a valid minor operation that deletes the whole
branch set, which the check now counts. The third found a sort slip in the
new check itself. The sequence of fixes is in
`tests/test_obstruction_minor.py::test_checker_accepts_deletion_of_a_contracted_component`.
The search module's own quotient code had none of these: its branch sets
are keyed by surviving representatives and the deleted ones simply leave.

### 4.2 Numbers

**The family closes every one of the 251** (`tables.md` (a), (c)). The
search's floor equals the optimum on **251 of 251**; the ladder's on 222
(88.4%), one below on the other 29. The record before this item (`floor0`,
the best of `lb_best`, `tw + 1`, Harper at cap 12, Lemma P and the file-backed
minors) was tight on 70 of the 251 and family E's exact floor after item 03
on 8; `tw + 1` alone on 67, `lb_best` and the clique bound on 0. On the 55
instances where `floor0` is 2 or more below the optimum (46 by 2, 8 by 3, 1
by 4), the ladder alone closes 53 and the search the other 2. The search's
floor is above `floor0` on 181 of the 251 and above the harness's reference
`max(lb_best, tw + 1)` on 184; through the harness's validity stage on all
6,376 corpus instances it is **above the optimum on 0** (`harness_table.md`;
the candidate is a lookup of the run's certificates, 1 elsewhere, as item
03's was).

| band | instances | ladder tight | search tight | search > ladder | `floor0` tight | family E tight |
|---|---|---|---|---|---|---|
| 9–20 | 17 | 12 | 17 | 5 | 4 | — |
| 21–30 | 133 | 115 | 133 | 18 | 47 | — |
| 31–40 | 47 | 42 | 47 | 5 | 13 | — |
| 41–60 | 54 | 53 | 54 | 1 | 6 | — |
| all | 251 | 222 | 251 | 29 | 70 | 8 |

**Where the search beats the ladder** ((b)): 29 of 251 (11.6%), always by
exactly one stack and always to the optimum; 14 Harvey, 10 Simonis, 4
Faggioli–Bentivoglio, 1 Chu & Stuckey (`Random-40-40-4-2_0`); 5 at 20
customers, 18 at 30, 5 at 40, 1 at 50. In every case the ladder's 95% point
(at 20 customers, one contraction) fails to prove `optimum − 1` on the
minor while the search's minor, of the same size or up to 9 vertices larger
(median 2), does — the greedy choice of *which* edge to contract is what
the ladder gets wrong, not the size. **Never the other way**: the search's
floor is below the ladder's on 0 instances (its restarts contain the
ladder's 50–95% points).

**The minimal certifying minor** ((d)). Over the 251 the search's smallest
minor at the optimum has `m / n` median 0.66 (IQR 0.52–0.77), against the
ladder's first certifying point at 0.80 (0.70–0.90; the ladder reaches the
optimum first at 95% on 43 instances, 85% on 37, 80% on 32, 50% on 12).
By band the median falls with `n`: 0.75, 0.70, 0.55, 0.51 at 9–20, 21–30,
31–40, 41–60; it rises with the excess (0.55, 0.62, 0.80 across excess
terciles; Pearson 0.68 with the realised excess, 0.82 with the graph
density, 0.88 with `optimum / n`, −0.53 with `n`). The minor is never
smaller than the optimum plus 2 vertices (median `m − optimum` 7,
`m / optimum` 1.48), as it cannot be: a graph on `m` vertices has pathwidth
at most `m − 1`. Every one of the 251 floors is a C `refutation` on the
minor (0 by the C's `bound`, 0 by its printed `lower`); of the 2,155 ladder
points 1,523 were refutations, 378 met the C's degeneracy bound and 254 were
skipped by the lifted-witness rule. The ladder's best point came from
`min-d` on 235 instances and `least-c` on 16.

**Checker verdicts** ((e)): **251 of 251 verified, all three checks**
(replay and hash, the C re-proof, and the rule-free `vsmemo` + `checkF`
refutation of `optimum − 2` on the minor: median 0.14 s, maximum 0.15 s;
the minors have 12–40 vertices). So every floor this item reports rests on
minor monotonicity and an 80-line checker, not on the search rules.

**Cost** ((f)): the ladder used **0.007 core-hours** on the 251 (median 5–9
C calls per instance, 0.0–0.1 s); the search used its whole budget, **5.08
core-hours**, of which 1.02 in the C program (951,248 calls, median 21.5
per second, each a process start on a 12–40-vertex graph) and the rest in
the Python moves (median 6,900 per second, 608 skipped candidates per
second). The budgets are "the same total seconds" in the sense the item
asks; the ladder needs a hundredth of them. Validation 0.3, the checker
sweeps 0.03, the harness under 0.01 (a lookup, 3 s), the two restarts'
redone instances about 0.2: **≈ 5.6 core-hours** against the item's 8.

### 4.3 Kill verdict and what this does not claim

**Kill criterion (plan §0.9 M): not met**, by a small margin. The search
beats the ladder on 29 of 251, 11.6%, against the 10% that would have
recorded "greedy is enough at `n ≤ 60`". The honest reading is narrower
than the number: the ladder closes 222 and is never more than one stack
short, and where the search wins it wins by one, at the minor sizes the
ladder already visits, by choosing a different contraction. The family's
duality gap on the 338 at `n ≤ 60` is **zero**: exact on all 251, with the
certificates on disk. The stop conditions did not fire: no minor's C-proved
width exceeded brute force (1,485 of 1,485), and no certificate was
rejected by a correct checker (the 5 rejections of the second sweep were
the checker's, §4.1). Item 05 runs the search on the 87 larger instances
of the 338 and the 200 Chu & Stuckey, where the ladder is known to miss.

**What this does not claim.** That the search is optimal among contraction
minors, or that the minimal minor it reports is the smallest certifying
minor (a search's failure to shrink further is not a proof); that a C
`refutation` on a minor is independent of the search rules (it rests on
the corrected rules proved sound in Lean; the rule-free `vsmemo` + `checkF`
check is the independent one, and here it ran on all 251 because the
minors are small — it does not scale to the 87-vertex minors of the record,
which took 255 s and 19.7 GB there); that the 11.6% would hold at larger
sizes or other budgets (the search spent its whole 60–120 s and the ladder
0.1 s, so at equal *spent* time the ladder is the better use of a second;
a search given the ladder's time would evaluate a few dozen candidates);
that the `m / n` figures describe anything but this search's minima under
this evaluator (ties by fewer vertices; cap 2 s); any solver change (the C
program's minor step and `relaxation.py` are untouched). The comparison with
family E uses item 03's `floor_after` where it exists and item 02's / item
01's cap-12 floor elsewhere; family E's ceiling is below the optimum on
most of these instances (item 02), so its 8 tight instances are a property
of the family, not of its search. "We found no prior report" of a local
search over contraction sequences for pathwidth lower bounds on MOSP
instances; the ladder is Chu & Stuckey's contraction relaxation
(2009, §3.5) as the record implements it, minor monotonicity is Fellows &
Langston (1987, Lemma 4.2), and the rule-free checker is the one of
`reports/minor_bound_verification.md`.

### 4.4 Tables (generated; `tables.md`)

## (a) Per band: the ladder's floor gap and the search's (optimum units)

| band   |   instances |   ladder gap mean |   ladder tight |   search gap mean |   search tight |   search > ladder |   tie, fewer vertices |   search < ladder |   floor0 gap mean |   search > floor0 |   best gap mean |   best tight |
|:-------|------------:|------------------:|---------------:|------------------:|---------------:|------------------:|----------------------:|------------------:|------------------:|------------------:|----------------:|-------------:|
| 9–20   |          17 |              0.29 |             12 |                 0 |             17 |                 5 |                    11 |                 0 |              0.76 |                12 |               0 |           17 |
| 21–30  |         133 |              0.14 |            115 |                 0 |            133 |                18 |                   107 |                 0 |              0.65 |                77 |               0 |          133 |
| 31–40  |          47 |              0.11 |             42 |                 0 |             47 |                 5 |                    41 |                 0 |              0.98 |                38 |               0 |           47 |
| 41–60  |          54 |              0.02 |             53 |                 0 |             54 |                 1 |                    53 |                 0 |              1.85 |                54 |               0 |           54 |
| all    |         251 |              0.12 |            222 |                 0 |            251 |                29 |                   212 |                 0 |              0.98 |               181 |               0 |          251 |
## (b) Where the search beats the ladder's floor

| instance_name                                                    |   n |   optimum |   ladder_floor |   ladder_m |   search_floor |   search_m | search_source   |   by |   search_calls |   search_seconds |
|:-----------------------------------------------------------------|----:|----------:|---------------:|-----------:|---------------:|-----------:|:----------------|-----:|---------------:|-----------------:|
| HS problem 2215 size 20 20 density  0.20                         |  20 |        13 |             12 |         14 |             13 |         18 | c_refutation    |    1 |           6101 |          60      |
| HS problem 690 size 20 10 density  0.30                          |  20 |        15 |             14 |         19 |             15 |         19 | c_refutation    |    1 |           1203 |          60      |
| HS problem 721 size 20 10 density  0.35                          |  20 |        16 |             15 |         17 |             16 |         19 | c_refutation    |    1 |            631 |          60      |
| Warwick 871: balanced orders, 4 orders per product               |  20 |         6 |              5 |         11 |              6 |         13 | c_refutation    |    1 |          11736 |          60      |
| Warwick 879: balanced orders, 4 orders per product               |  20 |         8 |              7 |         10 |              8 |         13 | c_refutation    |    1 |           9891 |          60      |
| HS problem 1159 size 30 10 density  0.25                         |  30 |        13 |             12 |         15 |             13 |         19 | c_refutation    |    1 |           7532 |          60      |
| HS problem 1168 size 30 10 density  0.25                         |  30 |        17 |             16 |         20 |             17 |         23 | c_refutation    |    1 |          10321 |          60.0001 |
| HS problem 1193 size 30 10 density  0.25                         |  30 |        20 |             19 |         24 |             20 |         28 | c_refutation    |    1 |           9999 |          60.0001 |
| HS problem 1215 size 30 10 density  0.30                         |  30 |        20 |             19 |         20 |             20 |         24 | c_refutation    |    1 |           2737 |          60.0001 |
| HS problem 1223 size 30 10 density  0.30                         |  30 |        20 |             19 |         21 |             20 |         27 | c_refutation    |    1 |           8665 |          60      |
| HS problem 2428 size 30 15 density  0.20                         |  30 |        16 |             15 |         26 |             16 |         27 | c_refutation    |    1 |          19048 |          60.0009 |
| Warwick 1309: balanced orders, 7 orders per product              |  30 |        15 |             14 |         22 |             15 |         24 | c_refutation    |    1 |            934 |          60.0001 |
| Warwick 1315: balanced orders, 8 orders per product              |  30 |        18 |             17 |         21 |             18 |         26 | c_refutation    |    1 |          13566 |          60      |
| Warwick 1356: balanced orders, 12 orders per product             |  30 |        24 |             23 |         26 |             24 |         28 | c_refutation    |    1 |           1617 |          60      |
| Warwick 1391: balanced products, 2 products per order            |  30 |        15 |             14 |         20 |             15 |         21 | c_refutation    |    1 |            769 |          60      |
| Warwick 1407: balanced products, 3 products per order            |  30 |        22 |             21 |         24 |             22 |         26 | c_refutation    |    1 |            413 |          60      |
| Warwick 1405: balanced products, 3 products per order            |  30 |        24 |             23 |         28 |             24 |         30 | c_refutation    |    1 |           3923 |          60.0003 |
| Warwick 1449: balanced orders and products, 3 products per order |  30 |        23 |             22 |         28 |             23 |         29 | c_refutation    |    1 |           4661 |          60      |
| Warwick 1488: balanced orders, 5 orders per product              |  30 |        12 |             11 |         15 |             12 |         24 | c_refutation    |    1 |          22054 |          60      |
| Warwick 1509: balanced orders, 7 orders per product              |  30 |        20 |             19 |         24 |             20 |         27 | c_refutation    |    1 |           1225 |          60      |
| Warwick 1613: balanced products, 4 products per order            |  30 |        23 |             22 |         26 |             23 |         27 | c_refutation    |    1 |            676 |          60      |
| Warwick 1676: balanced orders and products, 4 products per order |  30 |        24 |             23 |         28 |             24 |         30 | c_refutation    |    1 |           2973 |          60      |
| Warwick 1729: balanced orders, 3 orders per product              |  30 |         9 |              8 |         15 |              9 |         17 | c_refutation    |    1 |          15013 |          60.0009 |
| HS problem 3419 size 40 20 density  0.20                         |  40 |        28 |             27 |         36 |             28 |         39 | c_refutation    |    1 |            747 |          60.1304 |
| Random-40-40-4-2_0                                               |  40 |        21 |             20 |         30 |             21 |         31 | c_refutation    |    1 |            785 |          60.0002 |
| p2040n9_0                                                        |  40 |         9 |              8 |         20 |              9 |         22 | c_refutation    |    1 |           2295 |          60.0002 |
| p2540n9_0                                                        |  40 |        10 |              9 |         20 |             10 |         22 | c_refutation    |    1 |           4044 |          60.0075 |
| p3040n4_0                                                        |  40 |        12 |             11 |         20 |             12 |         27 | c_refutation    |    1 |          10679 |          60.0028 |
| p2550n10_0                                                       |  50 |        11 |             10 |         35 |             11 |         37 | c_refutation    |    1 |           1478 |         120.09   |

By how much: {1: 29}; reaching the optimum: 29 of 29.

## (c) Reaching the optimum

|   ladder reaches optimum |   search reaches optimum |   either |   search beats floor0 |   search beats max(lb_best, tw+1) |   best floor tight (floor0 or search) |   instances |
|-------------------------:|-------------------------:|---------:|----------------------:|----------------------------------:|--------------------------------------:|------------:|
|                      222 |                      251 |      251 |                   181 |                               184 |                                   251 |         251 |
## (d) The minimal certifying minor: `m / n` by band and by the ladder's rule

| band   |   instances |   search m/n median | search m/n IQR   |   ladder m/n median |   excess median |   corr(m/n, excess) |   source refutation |   source bound |   source lower |
|:-------|------------:|--------------------:|:-----------------|--------------------:|----------------:|--------------------:|--------------------:|---------------:|---------------:|
| 9–20   |          17 |                0.75 | 0.70–0.90        |               0.9   |             2   |               0.855 |                  17 |              0 |              0 |
| 21–30  |         133 |                0.7  | 0.60–0.80        |               0.867 |             2.1 |               0.631 |                 133 |              0 |              0 |
| 31–40  |          47 |                0.55 | 0.45–0.59        |               0.65  |             1.8 |               0.777 |                  47 |              0 |              0 |
| 41–60  |          54 |                0.51 | 0.45–0.61        |               0.76  |             1.7 |               0.71  |                  54 |              0 |              0 |

Ladder rule of the best ladder point: {'min-d': 235, 'least-c': 16}.

## (e) Checker verdicts

| verdict   | checks             |   certificates |
|:----------|:-------------------|---------------:|
| verified  | replay+C+rule-free |            251 |

Rule-free outcomes: {'verified': 251}; rule-free seconds median 0.14, max 0.2; checker seconds median 0.1.

## (f) C calls per instance and seconds

| band   |   instances |   budget s |   ladder calls median |   ladder skipped median |   ladder seconds median |   search calls median |   search skipped median |   search seconds median |   search moves median |   search restarts median |   ladder core-h |   search core-h |
|:-------|------------:|-----------:|----------------------:|------------------------:|------------------------:|----------------------:|------------------------:|------------------------:|----------------------:|-------------------------:|----------------:|----------------:|
| 9–20   |          17 |         60 |                     9 |                       1 |                     0   |                  4570 |                   75990 |                      60 |           1.19991e+06 |                    47997 |               0 |            0.28 |
| 21–30  |         133 |         60 |                     8 |                       0 |                     0   |                  2371 |                   55165 |                      60 |      504450           |                    20178 |               0 |            2.22 |
| 31–40  |          47 |         60 |                     5 |                       0 |                     0   |                   744 |                   16757 |                      60 |      125610           |                     5025 |               0 |            0.78 |
| 41–60  |          54 |        120 |                     6 |                       0 |                     0.1 |                  1168 |                   20425 |                     120 |      137144           |                     5486 |               0 |            1.8  |

Total: ladder 0.01 core-hours, search 5.08; C calls 1792 and 951248.

## (g) By collection

| collection           |   instances |   ladder gap mean |   search gap mean |   search > ladder |   search tight |   floor0 gap mean |   search > floor0 |
|:---------------------|------------:|------------------:|------------------:|------------------:|---------------:|------------------:|------------------:|
| Challenge            |           1 |              0    |                 0 |                 0 |              1 |              3    |                 1 |
| Chu & Stuckey        |          22 |              0.05 |                 0 |                 1 |             22 |              1.41 |                19 |
| Faggioli-Bentivoglio |          83 |              0.05 |                 0 |                 4 |             83 |              1.41 |                77 |
| Harvey               |          71 |              0.2  |                 0 |                14 |             71 |              0.48 |                32 |
| Simonis              |          73 |              0.14 |                 0 |                10 |             73 |              0.79 |                51 |
| Wilson               |           1 |              0    |                 0 |                 0 |              1 |              3    |                 1 |

## 5. Family M at scale: the 87 gap instances above 60 customers and the 200 Chu & Stuckey; `Random-125-125-2-2_0` and `2-3_0` (item 05)

*Size range: 207 distinct instances — the 87 of `gap338` above 60
customers (75–134) and the 200 of `cs200` (30–125), of which 185 were run
here (107 at 61–134, 78 at 30–50) and 22 (the Chu & Stuckey gap instances
at 30–50) are carried from item 04's run unchanged (`carried_item04.csv`,
their certificates and verdicts under `carried_item04/`); the two ridge
instances at 125. Regenerate: `nice -n 19 python3 -m learning.obstruction_minor
--stage run --out 05_minor_scale --targets cs200,gap338 --min-n 61 --max-n 134
--workers 8 --seconds 60,120,180,300 --core-hours 18 --order small-first`;
the same with `--targets cs200 --min-n 0 --max-n 60` (the 78); `--stage
ridge --out 05_minor_scale --core-hours 2 --workers 2`; `--stage check
--out 05_minor_scale --workers 8 --rulefree-cap 120`; `python3
reports/scratch/obstruction_search/05_minor_scale/run_harness.py --workers 4`;
`--stage tables --out 05_minor_scale`. Outputs under
`reports/scratch/obstruction_search/05_minor_scale/`: `search.csv` (185
rows), `ladder.csv` (every ladder point), `carried_item04.csv` (22),
`joined.csv` (207), `certificates/<instance>/{instance.mosp, search.json,
ladder.json, ladder_points.json}`, `ridge.csv` (every C call of the ridge
stage), `ridge_summary.csv`, `ridge/<instance>/{instance.mosp, search.json,
calls.csv}`, `checker_verdicts.csv`, `harness_values.csv`,
`harness_table.md`, `tables.md`, `run.log`, `gate_run.out`, and
`../05_minor_scale_{run,small_run,ridge,check}.out`. Tests:
`tests/test_obstruction_minor.py` (17, six new).*

### 5.1 What was done

**The question.** Item 04 showed the family closing every one of the 251
gap instances at 20–50 customers, with the search beating the ladder on
11.6% of them. This item takes the search to the sizes where the ladder is
known to miss: the 87 instances of the 338 above 60 customers and the 200
Chu & Stuckey instances (`targets.cs200`; 207 distinct in all, of which the
22 at 30–50 that are also in `gap338` were run by item 04 and are carried
from there), and to the two 125-customer ridge instances with the budget
the survey's unfinished sizes never had.

**The code** is item 04's `learning/obstruction_minor.py` with four
additions: `set_out` (every path under
`reports/scratch/obstruction_search/05_minor_scale/`), the C cap and the
per-instance budget by size (`cap_for`: 2 s at `n ≤ 60`, 5 s at 61–100,
10 s at 101–134, plan §0.5 (e); `budget_for`: 60, 120, 180 and 300 s per
band for the ladder and the same for the search), a scheduler in `run`
that starts an instance only while the core-hours spent plus the budgets
of the running ones stay below `--core-hours` and lists the rest in
`not_reached.txt`, and a `ridge` stage. The C's `nodes=` is now parsed
from its stderr and written into every certificate (`c_nodes`). The
search, the ladder, the evaluator (the lifted-witness skip, the cache by
edge hash), the certificate format and the checker are item 04's,
unchanged; `search` takes an optional list of start sequences, which only
the ridge stage uses.

**The ridge stage** (`--stage ridge`, 2 core-hours, one worker per
instance, 3,600 s each). First the two greedy rules at 100, 102, 105, 108
and 110 vertices with a 120 s cap per C call, every point sent to the C
program whatever its upper bound (the item asks for every size, rule,
status, node count and seconds); then, for `Random-125-125-2-2_0`, the
tabu search restarting from those ten points, best floor first, with a
60 s cap per call and 10 moves per restart; for `Random-125-125-2-3_0`,
the search restarting from the recorded 70-vertex least-c certificate
(`reports/scratch/minor_certificates/Random-125-125-2-3_0_m70.json`,
converted from `mc_graph.py`'s `[keep, absorbed]` to this module's
`(absorbed, keep)`; its replay gives the record's 70 representatives, by a
test), the objective minimising the vertex count at floor 21 — does a
smaller minor refute 20? Every C call is a row of `ridge.csv`; the
per-instance summary is `ridge_summary.csv`; the best minor's certificate
is `ridge/<instance>/search.json`.

### 5.2 Numbers

**The 87 gap instances above 60 customers** (`tables.md` (b)). Family M's
floor — the better of the ladder's and the search's certificate — equals
the optimum on **73 of the 87**: 17 of 17 at 61–75, 43 of 45 at 76–100,
13 of 25 at 101–134. The record before this loop (`floor0`) was tight on
11 of the 87 and family E's floor after item 03 on 4. The search alone is
tight on 72, the ladder alone on 58; the search beats the ladder on 16
(by one stack on 13, two on 3) and finishes below it on 3. The 14
the family leaves open, all Chu & Stuckey at 100 and 125
customers, by one to four stacks:

| instance | optimum | ladder | search | `floor0` | E floor | gap left |
|---|---|---|---|---|---|---|
| `Random-100-100-4-1_0` | 46 | 45 | 43 | 33 | 34 | 1 |
| `Random-100-100-4-3_0` | 43 | 41 | 42 | 26 | 26 | 1 |
| `Random-125-125-2-1_0` | 24 | 23 | 23 | 24 (record's 87-vertex minor) | 9 | 1 |
| `Random-125-125-2-2_0` | 25 | 24 | 24 | 24 | 8 | 1 |
| `Random-125-125-4-1_0` | 57 | 53 | 53 | 53 | 37 | 4 |
| `Random-125-125-4-2_0` | 57 | 54 | 53 | 55 | 35 | 3 |
| `Random-125-125-4-3_0` | 54 | 52 | 52 | 31 | 34 | 2 |
| `Random-125-125-4-4_0` | 51 | 49 | 49 | 50 | 24 | 2 |
| `Random-125-125-4-5_0` | 46 | 45 | 45 | 46 (loop0010's file-backed minor) | 24 | 1 |
| `Random-125-125-6-1_0` | 81 | 80 | 80 | 81 (record's 120-vertex minor) | 73 | 1 |
| `Random-125-125-6-2_0` | 77 | 76 | 76 | 60 | 61 | 1 |
| `Random-125-125-6-3_0` | 80 | 79 | 79 | 64 | 70 | 1 |
| `Random-125-125-6-4_0` | 80 | 78 | 78 | 63 | 69 | 2 |
| `Random-125-125-6-5_0` | 74 | 71 | 71 | 56 | 59 | 3 |

Three of the fourteen are closed by a floor already on record (`2-1_0`
and `6-1_0` by the survey's minors at 87 and 120 vertices, found with
40–80 s refutations where this item's cap is 10 s; `4-5_0` by loop0010's
file-backed minor certificate, item 01's `minor` column),
so **the 338 as a whole stand at 324 closed by family M (251 in item 04,
73 here), 3 more by the record, and 11 open after this item**, all `Random-100-100-4` and `Random-125-125-4/6`:
the dense shoulder of the ridge, exactly where item 03 left the six E
brackets open.

**The 200 Chu & Stuckey instances** ((a)). The family's floor is tight on
**186 of 200**: all 125 at 30–75 customers, 48 of 50 at 100, 13 of 25 at
125. `floor0` was tight on 88, family E on 58. By density at 125: density
2, 3 of 5 (the two above, each one stack short); density 4, 0 of 5 (one to
four short); density 6, 0 of 5 (one to three); densities 8 and 10, 5 of 5
each. **The expectation from the record — minors on the sparse ridge,
expansion on the dense classes — is half right**: family M is at least as
tight as family E on every one of the 200 (tighter on 142, tied on 58,
never looser), and at density 10 the two tie at the optimum (E exact there,
item 03); where E is 12–22 stacks short at 125 (densities 2–6), M is 0.4–2.6
short. What M misses is the dense shoulder, not the ridge.

**Where the search beats the ladder, and why** ((c)). On the 185 instances
this item ran, 60 (32%): by one on 44, two on 14, three on 2; on 41 of the
60 the certifying minor has **more than 95% of the vertices** (at
`Random-125-125-10` and `-8`, 116–122 of 125; at `Random-100-100-10`, 97–99
of 100), and on 49 of the 60 the ladder's best point was its last, the 95%
point. The ladder's size grid stops where the dense instances' certifying
minors start: on them the family's duality gap is zero and the ladder's
one to three stacks is a grid artefact (a 97, 98, 99% rung would close it,
a change to `relaxation.py`'s ladder proposed and not applied). On the
sparse classes the two agree, and the search's gain is a smaller minor.
The search finishes **below the ladder on 3** (`Random-100-100-4-1_0` and
`-4-4_0` by two and one, `Random-125-125-4-2_0` by one): at 5–10 s per
call its 180–300 s buy 67–146 C calls, fewer than the moves from its
50–95% restarts need to reach the ladder's 85–95% rungs, so the family's
certificate on those three is the ladder's (`ladder.json`, checked). The
item's "same total seconds" is again a cap and not a spend: the ladder
used 0.31 core-hours on the 185, the search 8.13.

**The record's seven** ((d)). `Random-125-125-8-2_0`: **93 = optimum** at
118 vertices (the survey had 92 at 115–120, item 01 carried 87 file-backed
and 92 as `minor_survey`); `SP4`: 53 = optimum at 90 (record 96);
`Random-125-125-2-3_0`: 21 = optimum at 53 in the main run and **51 in the
ridge stage** (record 70); `2-2_0`: 24 at 70 (the file-backed 24;
optimum 25); `2-1_0`: 23 at 61–62 against the record's 24 at 87; `4-1_0`:
53 at 88 against the survey's 54 at 100; `6-1_0`: 80 at 117 against the
record's 81 at 120. On the last three the record's refutations took 28–80 s
on minors of 87–120 vertices, above this item's 10 s cap; the caps are the
item's and the comparison is at unequal budgets, said so.

**The minimal certifying minor** ((f)). Where the search reaches the
optimum, `m / n` has median 0.83–0.94 by band at 61–134 against item 04's
0.51–0.75 at 20–60: at these sizes the certifying minors are large, and the
figure tracks density (Pearson 0.93 with `optimum / n`, 0.73 with the
excess, −0.16 with `n`). The sparse classes keep small certificates
(`Random-125-125-2`: 46–70 of 125; `Random-100-100-2`: 51 of 100 at the
median; the SCOOP instances 37–52 of 79–134), the dense ones need nearly
the whole graph. Every floor of the 185 is a C `refutation` on the minor,
for the ladder and for the search alike (0 by the C's `bound`, 0 by its
printed `lower`).

**The two ridge instances** ((g), `ridge.csv`, 645 C calls in all).

- *`Random-125-125-2-2_0`* (optimum 25; needs a minor refuting 23 in
  pathwidth units). The two greedy rules reach the same minor at each of 100,
  102, 105, 108 and 110 (different sequences, the same quotient, caught by
  the evaluator's cache), so five distinct 120 s calls: all `upper`, 2.1–2.3 × 10⁸ nodes each; at 100
  vertices the C finds a **layout of width 23**, so that minor cannot
  certify 25 (it is one the survey's "every minor ≤ 95 admits 24" extends
  to 100); at 102–110 it finds width 24 and decides nothing. The search
  from those points, 60 s per call, made 50 calls at 97–107 vertices, all
  `upper`: on 22 of them the C found a layout of width 23 or 22 (the
  minor is useless), on 28 width 24 (undecided), median 1.1 × 10⁸ nodes
  per call. Floor at the end: 14, the C's printed degeneracy bound. **No
  certificate for 25 was found within one core-hour** — a recorded
  negative, as the item says, and not a kill: it says nothing about
  whether one exists.
- *`Random-125-125-2-3_0`* (optimum 21). The greedy minors at 100–110 do
  **not** refute 20 in 120 s (all `upper`, 2.6–3.1 × 10⁸ nodes; the C
  finds width 20 or 21) while the recorded 70-vertex least-c minor
  refutes it in **757,009 nodes and 0.5 s** — the record's count to the
  node. From that certificate the search shrank the minor one vertex at a
  time: a refuting minor at every size from 69 down to **51** (574 calls,
  19 refutations, the rest exact widths of 19 on the candidates), the
  51-vertex one refuting 19 in **145,355 nodes and 0.12 s**; 367 candidates
  at 50 vertices all have pathwidth exactly 19. So a 51-vertex contraction
  minor certifies `Random-125-125-2-3_0 ≥ 21`, 19 vertices below the record
  and 5.2× fewer nodes; whether a 50-vertex one exists the search cannot
  say.

**Checker** ((h)): **190 of 190 verified** (`checker_verdicts.csv`: the 185 search
certificates, the 3 `ladder.json` where the ladder is the family's
certificate, the 2 ridge ones): replay and edge hash on all; the C
re-proof at the certificate's own cap × 5 on all (186 `refutation`, 3
`bound`, and 1 `upper` whose printed lower bound meets the claim — the
`2-2_0` ridge floor of 14); and the rule-free `vsmemo` + `checkF`
refutation on the **137 with at most 80 vertices** (8–80; median 0.14 s,
maximum 51.5 s), skipped on the 53 larger ones (81–122 vertices, the 87-vertex
scale the item excludes). The 51-vertex certificate of `2-3_0` is among
the rule-free verified (0.45 s), so that floor rests on minor monotonicity
and the 80-line checker alone, as the record's 70-vertex one does.

**Harness** (`harness_table.md`): the item's floor (a lookup of the 185
search certificates and the two ridge ones; 1 elsewhere) through the
validity stage on all 6,376 corpus instances: **above the optimum on 0**,
beats the reference `max(lb_best, tw + 1)` on 87 of the 338.

**Cost** ((i)): the main run 6.56 core-hours on the 107 at 61–134 (3,111 s
wall at 8 workers, load 8–10, no instance cut by the 18-core-hour cap) and
1.88 on the 78 at 30–50 (905 s wall): ladder 0.31 core-hours in all (1,783
C calls), search 8.13 (278,571 C calls, 3.35 core-hours inside the C);
the ridge stage 2.0 (645 C calls, 1.18 core-hours inside the C); the
checker 0.15 (seconds summed over the 190 checks); the harness 0.01. **≈ 10.6 core-hours** against the
item's 20 + 2.

### 5.3 Kill verdict and what this does not claim

**Kill criterion (plan §0.9 M, the 338 as a whole): not met.** The search
beats the ladder on 29 of the 251 at `n ≤ 60` (item 04) and 16 of the 87
above, **45 of 338, 13.3%**, against the 10% that would record "greedy is
enough". The reading stays the one of §4.3: the ladder is never more than
three stacks short, the search wins by one to three, and above 60
customers most of its wins are the 95% rung of the ladder's grid, which a
longer ladder would take at a hundredth of the search's time. For
`Random-125-125-2-2_0`, no certificate within the budget is a recorded
negative, not a kill. The budget was the kill on nothing: the 18-core-hour
driver stop was not reached. The stop conditions did not fire: no floor
above an optimum (harness and ledger), no certificate rejected by the
checker.

**What this does not claim.** That `Random-125-125-2-2_0` has no minor
certificate (55 C calls at 97–110 vertices under one core-hour found
none; the record's certificates for `2-1_0` and `6-1_0` needed calls this
item's caps do not allow); that the 51-vertex minor of `2-3_0` is the
smallest (367 failures at 50 are a search's failures); that the family's
floor on the 11 open instances is its best (the search spent 180–300 s
at 5–10 s per call; the three "below the ladder" show the budget binding);
that the `m / n` figures describe anything but this search's minima under
this evaluator; that a C `refutation` on a minor is independent of the
search rules where the rule-free check did not run (the 53 certificates with 81–122 vertices rest on the corrected rules proved sound in Lean, as the record's 87- and 120-vertex ones do); any
solver change (the 97–99% rungs are a proposal; `relaxation.py` and the
C's minor step are untouched); nothing about the C program's speed (plan
§0.4 (9)). The comparison with family E uses item 03's `floor_after` where
it exists, item 02's rerun floor and item 01's cap-12 floor elsewhere.
Yanasse (1997a) Proposition 2 and Fellows & Langston (1987) Lemma 4.2 are
the monotonicity behind every floor here; the ladder is Chu & Stuckey's
contraction relaxation (2009, §3.5) as the record implements it. "We found
no prior report" of the 51-vertex certificate or of a search over
contraction sequences at these sizes.

### 5.4 Tables (generated; `tables.md`)

*Generated by `python3 -m learning.obstruction_minor --stage tables --out 05_minor_scale` on 2026-11-03 06:11; 207 instances (`cs200` ∪ `gap338` at n > 60; n = 30–134).*
## (a) By Chu & Stuckey class `(n, m, d)` (the instances this item ran; item 04 covered the 22 gap instances at n ≤ 60 separately)

| class             |   instances |   ladder gap mean |   ladder tight |   search gap mean |   search tight |   search > ladder |   search < ladder |   floor0 gap mean |   search > floor0 |   E gap mean |   M tighter |   E tighter |   best gap mean |   best tight |
|:------------------|------------:|------------------:|---------------:|------------------:|---------------:|------------------:|------------------:|------------------:|------------------:|-------------:|------------:|------------:|----------------:|-------------:|
| Random-30-30-2    |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              0.8  |                 3 |         1.4  |           5 |           0 |            0    |            5 |
| Random-30-30-4    |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              0    |                 0 |         1    |           5 |           0 |            0    |            5 |
| Random-30-30-6    |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              0.2  |                 1 |         0.4  |           2 |           0 |            0    |            5 |
| Random-30-30-8    |           5 |              0.4  |              3 |              0    |              5 |                 2 |                 0 |              0    |                 0 |         0.2  |           1 |           0 |            0    |            5 |
| Random-30-30-10   |           5 |              0.2  |              4 |              0    |              5 |                 1 |                 0 |              0    |                 0 |         0.4  |           2 |           0 |            0    |            5 |
| Random-40-40-2    |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              0.2  |                 1 |         1.2  |           5 |           0 |            0    |            5 |
| Random-40-40-4    |           5 |              0.2  |              4 |              0    |              5 |                 1 |                 0 |              0.8  |                 4 |         1    |           5 |           0 |            0    |            5 |
| Random-40-40-6    |           5 |              0.2  |              4 |              0    |              5 |                 1 |                 0 |              0    |                 0 |         0.4  |           2 |           0 |            0    |            5 |
| Random-40-40-8    |           5 |              0.4  |              3 |              0    |              5 |                 2 |                 0 |              0    |                 0 |         0.2  |           1 |           0 |            0    |            5 |
| Random-40-40-10   |           5 |              1    |              0 |              0    |              5 |                 5 |                 0 |              0    |                 0 |         0    |           0 |           0 |            0    |            5 |
| Random-50-50-2    |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              2    |                 5 |         1.2  |           4 |           0 |            0    |            5 |
| Random-50-50-4    |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              1.2  |                 5 |         1    |           5 |           0 |            0    |            5 |
| Random-50-50-6    |           5 |              0.2  |              4 |              0    |              5 |                 1 |                 0 |              0.8  |                 4 |         0.8  |           4 |           0 |            0    |            5 |
| Random-50-50-8    |           5 |              0.2  |              4 |              0    |              5 |                 1 |                 0 |              0    |                 0 |         0.2  |           1 |           0 |            0    |            5 |
| Random-50-50-10   |           5 |              0.6  |              2 |              0    |              5 |                 3 |                 0 |              0    |                 0 |         0.4  |           2 |           0 |            0    |            5 |
| Random-50-100-2   |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              2    |                 5 |         1    |           5 |           0 |            0    |            5 |
| Random-50-100-4   |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              0.4  |                 2 |         0.4  |           2 |           0 |            0    |            5 |
| Random-50-100-6   |           5 |              1    |              1 |              0    |              5 |                 4 |                 0 |              0    |                 0 |         0.2  |           1 |           0 |            0    |            5 |
| Random-50-100-8   |           5 |              1.2  |              1 |              0    |              5 |                 4 |                 0 |              0    |                 0 |         0.2  |           1 |           0 |            0    |            5 |
| Random-50-100-10  |           5 |              1    |              0 |              0    |              5 |                 5 |                 0 |              0    |                 0 |         0.2  |           1 |           0 |            0    |            5 |
| Random-75-75-2    |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              4.8  |                 5 |         4.6  |           5 |           0 |            0    |            5 |
| Random-75-75-4    |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              6.8  |                 5 |         4.6  |           5 |           0 |            0    |            5 |
| Random-75-75-6    |           5 |              0.4  |              3 |              0    |              5 |                 2 |                 0 |              1    |                 4 |         0.8  |           4 |           0 |            0    |            5 |
| Random-75-75-8    |           5 |              0.4  |              3 |              0    |              5 |                 2 |                 0 |              0.6  |                 3 |         0.6  |           3 |           0 |            0    |            5 |
| Random-75-75-10   |           5 |              1.8  |              0 |              0    |              5 |                 5 |                 0 |              0.4  |                 2 |         0.4  |           2 |           0 |            0    |            5 |
| Random-100-50-2   |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              2.8  |                 5 |         6.6  |           5 |           0 |            0    |            5 |
| Random-100-50-4   |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |             10.4  |                 5 |        12.4  |           5 |           0 |            0    |            5 |
| Random-100-50-6   |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |             11.8  |                 5 |        11.8  |           5 |           0 |            0    |            5 |
| Random-100-50-8   |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              7.6  |                 5 |         7.4  |           5 |           0 |            0    |            5 |
| Random-100-50-10  |           5 |              0.2  |              4 |              0    |              5 |                 1 |                 0 |              4    |                 5 |         3.8  |           5 |           0 |            0    |            5 |
| Random-100-100-2  |           5 |              0    |              5 |              0    |              5 |                 0 |                 0 |              7.8  |                 5 |        11.2  |           5 |           0 |            0    |            5 |
| Random-100-100-4  |           5 |              0.6  |              3 |              1    |              2 |                 1 |                 2 |             13.8  |                 5 |        12.4  |           5 |           0 |            1    |            2 |
| Random-100-100-6  |           5 |              0.4  |              3 |              0    |              5 |                 2 |                 0 |              6.6  |                 5 |         6.2  |           5 |           0 |            0    |            5 |
| Random-100-100-8  |           5 |              1    |              1 |              0    |              5 |                 4 |                 0 |              0.8  |                 4 |         0.8  |           4 |           0 |            0    |            5 |
| Random-100-100-10 |           5 |              2    |              0 |              0    |              5 |                 5 |                 0 |              0.8  |                 4 |         0.8  |           4 |           0 |            0    |            5 |
| Random-125-125-2  |           5 |              0.4  |              3 |              0.4  |              3 |                 0 |                 0 |              0.2  |                 0 |        14.6  |           5 |           0 |            0.2  |            4 |
| Random-125-125-4  |           5 |              2.4  |              0 |              2.6  |              0 |                 0 |                 1 |              6    |                 1 |        22.2  |           5 |           0 |            1.8  |            1 |
| Random-125-125-6  |           5 |              1.6  |              0 |              1.6  |              0 |                 0 |                 0 |             13.6  |                 4 |        12    |           5 |           0 |            1.4  |            1 |
| Random-125-125-8  |           5 |              1    |              1 |              0    |              5 |                 4 |                 0 |              4.8  |                 5 |         2    |           5 |           0 |            0    |            5 |
| Random-125-125-10 |           5 |              1.8  |              0 |              0    |              5 |                 5 |                 0 |              0.2  |                 1 |         0.2  |           1 |           0 |            0    |            5 |
| all Chu & Stuckey |         200 |              0.52 |            126 |              0.14 |            185 |                61 |                 3 |              2.83 |               108 |         3.68 |         142 |           0 |            0.11 |          188 |
## (b) The gap instances (`gap338` at n > 60) by band

| band    |   instances |   ladder gap mean |   ladder tight |   search gap mean |   search tight |   search > ladder |   search < ladder |   floor0 gap mean |   search > floor0 |   E gap mean |   M tighter |   E tighter |   best gap mean |   best tight |
|:--------|------------:|------------------:|---------------:|------------------:|---------------:|------------------:|------------------:|------------------:|------------------:|-------------:|------------:|------------:|----------------:|-------------:|
| 21–30   |           1 |              0    |              1 |              0    |              1 |                 0 |                 0 |              2    |                 1 |         2    |           1 |           0 |            0    |            1 |
| 31–40   |           6 |              0.17 |              5 |              0    |              6 |                 1 |                 0 |              0.5  |                 3 |         1.17 |           6 |           0 |            0    |            6 |
| 41–60   |          15 |              0    |             15 |              0    |             15 |                 0 |                 0 |              1.73 |                15 |         1.07 |          14 |           0 |            0    |           15 |
| 61–75   |          17 |              0.12 |             15 |              0    |             17 |                 2 |                 0 |              4.41 |                16 |         3.65 |          16 |           0 |            0    |           17 |
| 76–100  |          45 |              0.22 |             37 |              0.11 |             42 |                 7 |                 2 |              7.47 |                43 |         8.29 |          44 |           0 |            0.11 |           42 |
| 101–134 |          25 |              1.24 |              6 |              0.92 |             13 |                 7 |                 1 |              5.28 |                13 |        10.84 |          23 |           0 |            0.68 |           16 |
| all     |         109 |              0.4  |             79 |              0.26 |             94 |                17 |                 3 |              5.27 |                91 |         6.71 |         104 |           0 |            0.2  |           97 |
## (c) Where the search beats the ladder's floor

| instance_name         |   n |   optimum |   ladder_floor |   ladder_m |   search_floor |   search_m | search_source   |   by |   search_calls |   search_seconds |
|:----------------------|----:|----------:|---------------:|-----------:|---------------:|-----------:|:----------------|-----:|---------------:|-----------------:|
| Random-100-100-10-1_0 | 100 |        87 |             84 |         95 |             87 |         99 | c_refutation    |    3 |           1238 |         180.003  |
| Random-125-125-10-1_0 | 125 |       105 |            102 |        119 |            105 |        122 | c_refutation    |    3 |            829 |         300      |
| Random-50-100-6-2_0   |  50 |        44 |             42 |         48 |             44 |         50 | c_refutation    |    2 |           2660 |         120.001  |
| Random-50-100-8-1_0   |  50 |        47 |             45 |         48 |             47 |         50 | c_refutation    |    2 |            262 |         120      |
| Random-50-100-8-2_0   |  50 |        47 |             45 |         48 |             47 |         49 | c_refutation    |    2 |            267 |         120      |
| Random-75-75-10-1_0   |  75 |        66 |             64 |         71 |             66 |         74 | c_refutation    |    2 |           2156 |         180      |
| Random-75-75-10-3_0   |  75 |        65 |             63 |         71 |             65 |         74 | c_refutation    |    2 |           3259 |         180      |
| Random-75-75-10-4_0   |  75 |        65 |             63 |         71 |             65 |         73 | c_refutation    |    2 |           2551 |         180.005  |
| Random-75-75-10-2_0   |  75 |        65 |             63 |         71 |             65 |         73 | c_refutation    |    2 |           3352 |         180.353  |
| Random-100-100-10-2_0 | 100 |        85 |             83 |         95 |             85 |         99 | c_refutation    |    2 |            536 |         180.001  |
| Random-100-100-10-3_0 | 100 |        83 |             81 |         95 |             83 |         99 | c_refutation    |    2 |            856 |         180.012  |
| Random-100-100-10-5_0 | 100 |        84 |             82 |         95 |             84 |         97 | c_refutation    |    2 |           1356 |         180.004  |
| Random-100-100-8-4_0  | 100 |        77 |             75 |         95 |             77 |         97 | c_refutation    |    2 |           1124 |         180.03   |
| Random-125-125-10-2_0 | 125 |       104 |            102 |        119 |            104 |        122 | c_refutation    |    2 |            943 |         300.015  |
| Random-125-125-10-4_0 | 125 |       105 |            103 |        119 |            105 |        121 | c_refutation    |    2 |            862 |         300      |
| Random-125-125-8-1_0  | 125 |        95 |             93 |        119 |             95 |        118 | c_refutation    |    2 |            331 |         300.018  |
| Random-30-30-10-5_0   |  30 |        28 |             27 |         27 |             28 |         30 | c_refutation    |    1 |             59 |          60      |
| Random-30-30-8-1_0    |  30 |        25 |             24 |         26 |             25 |         28 | c_refutation    |    1 |           1382 |          60.0001 |
| Random-30-30-8-5_0    |  30 |        25 |             24 |         26 |             25 |         28 | c_refutation    |    1 |           1601 |          60.0001 |
| Random-40-40-10-1_0   |  40 |        36 |             35 |         38 |             36 |         39 | c_refutation    |    1 |            351 |          60.0001 |
| Random-40-40-10-2_0   |  40 |        36 |             35 |         38 |             36 |         39 | c_refutation    |    1 |            822 |          60.0003 |
| Random-40-40-10-3_0   |  40 |        34 |             33 |         36 |             34 |         37 | c_refutation    |    1 |           1360 |          60.0001 |
| Random-40-40-10-4_0   |  40 |        36 |             35 |         38 |             36 |         39 | c_refutation    |    1 |            769 |          60.0001 |
| Random-40-40-10-5_0   |  40 |        35 |             34 |         36 |             35 |         37 | c_refutation    |    1 |            811 |          60      |
| Random-40-40-6-2_0    |  40 |        30 |             29 |         36 |             30 |         37 | c_refutation    |    1 |           4611 |          60      |
| Random-40-40-8-1_0    |  40 |        34 |             33 |         38 |             34 |         39 | c_refutation    |    1 |           2004 |          60.0003 |
| Random-40-40-8-5_0    |  40 |        34 |             33 |         36 |             34 |         38 | c_refutation    |    1 |           1155 |          60.0002 |
| Random-40-40-4-2_0    |  40 |        21 |             20 |         30 |             21 |         31 | c_refutation    |    1 |            785 |          60.0002 |
| Random-50-100-10-1_0  |  50 |        48 |             47 |         48 |             48 |         49 | c_refutation    |    1 |             93 |         120      |
| Random-50-100-10-2_0  |  50 |        48 |             47 |         48 |             48 |         49 | c_refutation    |    1 |             10 |         120      |
| Random-50-100-10-3_0  |  50 |        48 |             47 |         48 |             48 |         49 | c_refutation    |    1 |             22 |         120      |
| Random-50-100-10-4_0  |  50 |        48 |             47 |         48 |             48 |         49 | c_refutation    |    1 |             70 |         120      |
| Random-50-100-10-5_0  |  50 |        47 |             46 |         48 |             47 |         49 | c_refutation    |    1 |            148 |         120      |
| Random-50-100-6-1_0   |  50 |        44 |             43 |         48 |             44 |         49 | c_refutation    |    1 |           1969 |         120.002  |
| Random-50-100-6-3_0   |  50 |        42 |             41 |         48 |             42 |         47 | c_refutation    |    1 |            646 |         120      |
| Random-50-100-6-4_0   |  50 |        42 |             41 |         48 |             42 |         47 | c_refutation    |    1 |           4389 |         120      |
| Random-50-100-8-3_0   |  50 |        46 |             45 |         48 |             46 |         49 | c_refutation    |    1 |            428 |         120      |
| Random-50-100-8-4_0   |  50 |        46 |             45 |         48 |             46 |         49 | c_refutation    |    1 |            878 |         120      |
| Random-50-50-10-3_0   |  50 |        44 |             43 |         48 |             44 |         48 | c_refutation    |    1 |           1884 |         120      |
| Random-50-50-10-4_0   |  50 |        45 |             44 |         48 |             45 |         49 | c_refutation    |    1 |            975 |         120      |
| Random-50-50-10-5_0   |  50 |        46 |             45 |         48 |             46 |         49 | c_refutation    |    1 |            816 |         120.002  |
| Random-50-50-6-2_0    |  50 |        35 |             34 |         45 |             35 |         46 | c_refutation    |    1 |           3125 |         120      |
| Random-50-50-8-4_0    |  50 |        42 |             41 |         48 |             42 |         48 | c_refutation    |    1 |           3707 |         120      |
| Random-75-75-10-5_0   |  75 |        63 |             62 |         71 |             63 |         72 | c_refutation    |    1 |           2124 |         180      |
| Random-75-75-6-2_0    |  75 |        52 |             51 |         71 |             52 |         70 | c_refutation    |    1 |           2794 |         180.006  |
| Random-75-75-6-5_0    |  75 |        51 |             50 |         68 |             51 |         68 | c_refutation    |    1 |           3735 |         180.025  |
| Random-75-75-8-4_0    |  75 |        59 |             58 |         71 |             59 |         72 | c_refutation    |    1 |           3981 |         180.002  |
| Random-75-75-8-5_0    |  75 |        59 |             58 |         71 |             59 |         71 | c_refutation    |    1 |           2395 |         180.006  |
| Random-100-100-10-4_0 | 100 |        84 |             83 |         95 |             84 |         97 | c_refutation    |    1 |           1665 |         180.005  |
| Random-100-100-6-1_0  | 100 |        68 |             67 |         95 |             68 |         96 | c_refutation    |    1 |            242 |         180.012  |
| Random-100-100-6-4_0  | 100 |        65 |             64 |         95 |             65 |         95 | c_refutation    |    1 |            240 |         180.015  |
| Random-100-100-4-3_0  | 100 |        43 |             41 |         70 |             42 |         80 | c_refutation    |    1 |            134 |         180.016  |
| Random-100-100-8-1_0  | 100 |        79 |             78 |         95 |             79 |         96 | c_refutation    |    1 |            984 |         180.013  |
| Random-100-100-8-3_0  | 100 |        76 |             75 |         95 |             76 |         97 | c_refutation    |    1 |           1012 |         180.012  |
| Random-100-100-8-5_0  | 100 |        75 |             74 |         95 |             75 |         93 | c_refutation    |    1 |           1164 |         180.008  |
| Random-100-50-10-3_0  | 100 |        68 |             67 |         90 |             68 |         92 | c_refutation    |    1 |            995 |         180.009  |
| Random-125-125-10-3_0 | 125 |       103 |            102 |        119 |            103 |        120 | c_refutation    |    1 |           1008 |         300.009  |
| Random-125-125-10-5_0 | 125 |        99 |             98 |        119 |             99 |        118 | c_refutation    |    1 |            654 |         300.003  |
| Random-125-125-8-2_0  | 125 |        93 |             92 |        119 |             93 |        118 | c_refutation    |    1 |            327 |         300.018  |
| Random-125-125-8-3_0  | 125 |        95 |             94 |        119 |             95 |        121 | c_refutation    |    1 |            245 |         300.014  |
| Random-125-125-8-5_0  | 125 |        91 |             90 |        119 |             91 |        121 | c_refutation    |    1 |             66 |         300.018  |

By how much: {1: 45, 2: 14, 3: 2}; reaching the optimum: 60 of 61; below the ladder: 3.

## (d) Against the record's seven (survey §5) and the file-backed minors of item 01

| instance             |   optimum |   survey minor | at m (rule)                      | ridge stage   |   file-backed (item 01) |   ladder |   ladder m |   search |   search m |   E floor |
|:---------------------|----------:|---------------:|:---------------------------------|:--------------|------------------------:|---------:|-----------:|---------:|-----------:|----------:|
| Random-125-125-2-1_0 |        24 |             24 | 87 (min-d)                       |               |                      24 |       23 |         62 |       23 |         61 |         9 |
| Random-125-125-2-3_0 |        21 |             21 | 70 (least-c)                     | 21 @ 51       |                      21 |       21 |         75 |       21 |         53 |         8 |
| Random-125-125-2-2_0 |        25 |            nan | none ≤ 95; 100–105 out of budget | 14 @ 97       |                      24 |       24 |         75 |       24 |         70 |         8 |
| Random-125-125-4-1_0 |        57 |             54 | 100 (min-d)                      |               |                      53 |       53 |         88 |       53 |         88 |        37 |
| Random-125-125-6-1_0 |        81 |             81 | 120 (both)                       |               |                      81 |       80 |        119 |       80 |        117 |        73 |
| Random-125-125-8-2_0 |        93 |             92 | 115–120                          |               |                      87 |       92 |        119 |       93 |        118 |        91 |
| SP4                  |        53 |             53 | 96 (both)                        |               |                      53 |       53 |         95 |       53 |         90 |        45 |
## (e) Family M against family E, by class and band: which is tighter where

| class             |   instances |   M floor gap mean |   E floor gap mean |   M tighter |   E tighter |   tie |   excess median |
|:------------------|------------:|-------------------:|-------------------:|------------:|------------:|------:|----------------:|
| Random-30-30-2    |           5 |                0   |                1.4 |           5 |           0 |     0 |            1.7  |
| Random-30-30-4    |           5 |                0   |                1   |           5 |           0 |     0 |            3.2  |
| Random-30-30-6    |           5 |                0   |                0.4 |           2 |           0 |     3 |            4.97 |
| Random-30-30-8    |           5 |                0   |                0.2 |           1 |           0 |     4 |            6.83 |
| Random-30-30-10   |           5 |                0   |                0.4 |           2 |           0 |     3 |            8.93 |
| Random-40-40-2    |           5 |                0   |                1.2 |           5 |           0 |     0 |            1.8  |
| Random-40-40-4    |           5 |                0   |                1   |           5 |           0 |     0 |            3.25 |
| Random-40-40-6    |           5 |                0   |                0.4 |           2 |           0 |     3 |            4.92 |
| Random-40-40-8    |           5 |                0   |                0.2 |           1 |           0 |     4 |            6.97 |
| Random-40-40-10   |           5 |                0   |                0   |           0 |           0 |     5 |            8.9  |
| Random-50-50-2    |           5 |                0   |                1.2 |           4 |           0 |     1 |            1.78 |
| Random-50-50-4    |           5 |                0   |                1   |           5 |           0 |     0 |            3.28 |
| Random-50-50-6    |           5 |                0   |                0.8 |           4 |           0 |     1 |            5.34 |
| Random-50-50-8    |           5 |                0   |                0.2 |           1 |           0 |     4 |            7.2  |
| Random-50-50-10   |           5 |                0   |                0.4 |           2 |           0 |     3 |            9.08 |
| Random-50-100-2   |           5 |                0   |                1   |           5 |           0 |     0 |            3.14 |
| Random-50-100-4   |           5 |                0   |                0.4 |           2 |           0 |     3 |            6.36 |
| Random-50-100-6   |           5 |                0   |                0.2 |           1 |           0 |     4 |           10.32 |
| Random-50-100-8   |           5 |                0   |                0.2 |           1 |           0 |     4 |           13.84 |
| Random-50-100-10  |           5 |                0   |                0.2 |           1 |           0 |     4 |           18.02 |
| Random-75-75-2    |           5 |                0   |                4.6 |           5 |           0 |     0 |            1.87 |
| Random-75-75-4    |           5 |                0   |                4.6 |           5 |           0 |     0 |            3.24 |
| Random-75-75-6    |           5 |                0   |                0.8 |           4 |           0 |     1 |            5.12 |
| Random-75-75-8    |           5 |                0   |                0.6 |           3 |           0 |     2 |            7.24 |
| Random-75-75-10   |           5 |                0   |                0.4 |           2 |           0 |     3 |            9.08 |
| Random-100-50-2   |           5 |                0   |                6.6 |           5 |           0 |     0 |            1.22 |
| Random-100-50-4   |           5 |                0   |               12.4 |           5 |           0 |     0 |            1.85 |
| Random-100-50-6   |           5 |                0   |               11.8 |           5 |           0 |     0 |            2.82 |
| Random-100-50-8   |           5 |                0   |                7.4 |           5 |           0 |     0 |            3.67 |
| Random-100-50-10  |           5 |                0   |                3.8 |           5 |           0 |     0 |            4.68 |
| Random-100-100-2  |           5 |                0   |               11.2 |           5 |           0 |     0 |            1.75 |
| Random-100-100-4  |           5 |                1   |               12.4 |           5 |           0 |     0 |            3.18 |
| Random-100-100-6  |           5 |                0   |                6.2 |           5 |           0 |     0 |            5.17 |
| Random-100-100-8  |           5 |                0   |                0.8 |           4 |           0 |     1 |            7.13 |
| Random-100-100-10 |           5 |                0   |                0.8 |           4 |           0 |     1 |            9.18 |
| Random-125-125-2  |           5 |                0.4 |               14.6 |           5 |           0 |     0 |            1.73 |
| Random-125-125-4  |           5 |                2.6 |               22.2 |           5 |           0 |     0 |            3.29 |
| Random-125-125-6  |           5 |                1.6 |               12   |           5 |           0 |     0 |            5.13 |
| Random-125-125-8  |           5 |                0   |                2   |           5 |           0 |     0 |            7.18 |
| Random-125-125-10 |           5 |                0   |                0.2 |           1 |           0 |     4 |            9.18 |

| band    |   instances |   M floor gap mean |   E floor gap mean |   M tighter |   E tighter |   tie |
|:--------|------------:|-------------------:|-------------------:|------------:|------------:|------:|
| 21–30   |          25 |               0    |               0.68 |          15 |           0 |    10 |
| 31–40   |          25 |               0    |               0.56 |          13 |           0 |    12 |
| 41–60   |          50 |               0    |               0.56 |          26 |           0 |    24 |
| 61–75   |          27 |               0    |               2.48 |          21 |           0 |     6 |
| 76–100  |          53 |               0.09 |               7.34 |          51 |           0 |     2 |
| 101–134 |          27 |               0.85 |              10.04 |          23 |           0 |     4 |
## (f) The minimal certifying minor: `m / n` where the search reaches the optimum

| band    |   at optimum |   search m/n median | search m/n IQR   |   ladder m/n median |   excess median |
|:--------|-------------:|--------------------:|:-----------------|--------------------:|----------------:|
| 21–30   |           25 |               0.8   | 0.63–0.90        |               0.867 |            4.97 |
| 31–40   |           25 |               0.85  | 0.75–0.93        |               0.875 |            4.92 |
| 41–60   |           50 |               0.92  | 0.78–0.97        |               0.93  |            6.72 |
| 61–75   |           27 |               0.88  | 0.71–0.95        |               0.907 |            5.07 |
| 76–100  |           50 |               0.83  | 0.58–0.92        |               0.9   |            3.63 |
| 101–134 |           15 |               0.944 | 0.42–0.97        |               0.576 |            7.18 |

Sources of the search's floor: {'c_refutation': 204, 'c_bound': 3}; of the ladder's: {'c_refutation': 202, 'c_bound': 5}; ladder rule: {'min-d': 197, 'least-c': 10}.

## (g) The two ridge instances: every C call of the ridge stage

The ladder points and the recorded certificate (every call; the search's calls are summarised below and listed in full in `ridge.csv` and `ridge/<instance>/calls.csv`):

| instance_name        | phase    | label               |   m |   cap |   upper_pw |   floor | source       |   c_width | c_status   |   c_lower |   c_nodes |   c_seconds | cached   |
|:---------------------|:---------|:--------------------|----:|------:|-----------:|--------:|:-------------|----------:|:-----------|----------:|----------:|------------:|:---------|
| Random-125-125-2-3_0 | ladder   | min-d@100           | 100 |   120 |         20 |      13 | c_lower      |        20 | upper      |        12 | 269869056 |  120.01     | False    |
| Random-125-125-2-3_0 | ladder   | least-c@100         | 100 |   120 |         20 |      13 | c_lower      |        20 | upper      |        12 | 269869056 |  120.01     | True     |
| Random-125-125-2-3_0 | ladder   | min-d@102           | 102 |   120 |         20 |      13 | c_lower      |        20 | upper      |        12 | 312639488 |  120.011    | False    |
| Random-125-125-2-3_0 | ladder   | least-c@102         | 102 |   120 |         20 |      13 | c_lower      |        20 | upper      |        12 | 312639488 |  120.011    | True     |
| Random-125-125-2-3_0 | ladder   | min-d@105           | 105 |   120 |         20 |      13 | c_lower      |        20 | upper      |        12 | 287139266 |  120.015    | False    |
| Random-125-125-2-3_0 | ladder   | least-c@105         | 105 |   120 |         20 |      13 | c_lower      |        20 | upper      |        12 | 287139266 |  120.015    | True     |
| Random-125-125-2-3_0 | ladder   | min-d@108           | 108 |   120 |         20 |      13 | c_lower      |        21 | upper      |        12 | 259338240 |  120.011    | False    |
| Random-125-125-2-3_0 | ladder   | least-c@108         | 108 |   120 |         20 |      13 | c_lower      |        21 | upper      |        12 | 259338240 |  120.011    | True     |
| Random-125-125-2-3_0 | ladder   | min-d@110           | 110 |   120 |         20 |      13 | c_lower      |        20 | upper      |        12 | 259735552 |  120.013    | False    |
| Random-125-125-2-3_0 | ladder   | least-c@110         | 110 |   120 |         20 |      13 | c_lower      |        20 | upper      |        12 | 259735552 |  120.013    | True     |
| Random-125-125-2-3_0 | recorded | least-c@70 (record) |  70 |    60 |         20 |      21 | c_refutation |        20 | refutation |        12 |    757009 |    0.500904 | False    |
| Random-125-125-2-2_0 | ladder   | min-d@100           | 100 |   120 |         24 |      13 | c_lower      |        23 | upper      |        12 | 214891493 |  120.01     | False    |
| Random-125-125-2-2_0 | ladder   | least-c@100         | 100 |   120 |         24 |      13 | c_lower      |        23 | upper      |        12 | 214891493 |  120.01     | True     |
| Random-125-125-2-2_0 | ladder   | min-d@102           | 102 |   120 |         24 |      13 | c_lower      |        24 | upper      |        12 | 231133184 |  120.013    | False    |
| Random-125-125-2-2_0 | ladder   | least-c@102         | 102 |   120 |         24 |      13 | c_lower      |        24 | upper      |        12 | 231133184 |  120.013    | True     |
| Random-125-125-2-2_0 | ladder   | min-d@105           | 105 |   120 |         24 |      13 | c_lower      |        24 | upper      |        12 | 219222016 |  120.014    | False    |
| Random-125-125-2-2_0 | ladder   | least-c@105         | 105 |   120 |         24 |      13 | c_lower      |        24 | upper      |        12 | 219222016 |  120.014    | True     |
| Random-125-125-2-2_0 | ladder   | min-d@108           | 108 |   120 |         24 |      13 | c_lower      |        24 | upper      |        12 | 223170560 |  120.011    | False    |
| Random-125-125-2-2_0 | ladder   | least-c@108         | 108 |   120 |         24 |      13 | c_lower      |        24 | upper      |        12 | 223170560 |  120.011    | True     |
| Random-125-125-2-2_0 | ladder   | min-d@110           | 110 |   120 |         24 |      13 | c_lower      |        24 | upper      |        12 | 228847616 |  120.011    | False    |
| Random-125-125-2-2_0 | ladder   | least-c@110         | 110 |   120 |         24 |      13 | c_lower      |        24 | upper      |        12 | 228847616 |  120.011    | True     |

| instance             |   search calls | m range   |   cap s |   refutations |   upper (undecided) | widths found (status upper)   |   best floor |   smallest m at best floor |   nodes median |   C seconds |
|:---------------------|---------------:|:----------|--------:|--------------:|--------------------:|:------------------------------|-------------:|---------------------------:|---------------:|------------:|
| Random-125-125-2-2_0 |             50 | 97–107    |      60 |             0 |                  50 | {22: 1, 23: 21, 24: 28}       |           14 |                         97 |      110618624 |      2998.6 |
| Random-125-125-2-3_0 |            574 | 50–69     |      60 |           574 |                   0 | {}                            |           21 |                         51 |          74901 |        56.5 |

| instance_name        |   n |   optimum |   seconds_budget |   seconds |   ladder_floor |   ladder_m |   search_floor |   search_m | search_source   |   calls |   search_calls |   skipped |   c_seconds |   restarts |    moves | reached_optimum   | from_recorded   |
|:---------------------|----:|----------:|-----------------:|----------:|---------------:|-----------:|---------------:|-----------:|:----------------|--------:|---------------:|----------:|------------:|-----------:|---------:|:------------------|:----------------|
| Random-125-125-2-3_0 | 125 |        21 |             3600 |   3600    |             13 |        100 |             21 |         51 | c_refutation    |     580 |            574 |      2420 |     657.079 |    1406774 | 14067735 | True              | True            |
| Random-125-125-2-2_0 | 125 |        25 |             3600 |   3600.01 |             13 |        100 |             14 |         97 | c_lower         |      55 |             50 |         0 |    3598.67  |          9 |       88 | False             | False           |
## (h) Checker verdicts

| verdict   | checks             |   certificates |
|:----------|:-------------------|---------------:|
| verified  | replay+C           |             53 |
| verified  | replay+C+rule-free |            137 |

Rule-free outcomes: {'verified': 137, 'skipped': 53}; rule-free seconds median 0.14, max 51.5; checker seconds median 0.1, max 300.0; minors m = 8–122.

## (i) C calls per instance and seconds

| band    |   instances |   budget s |   C cap s |   ladder calls median |   ladder seconds median |   search calls median |   search skipped median |   search seconds median |   search moves median |   ladder core-h |   search core-h |
|:--------|------------:|-----------:|----------:|----------------------:|------------------------:|----------------------:|------------------------:|------------------------:|----------------------:|----------------:|----------------:|
| 21–30   |          25 |         60 |         2 |                     8 |                     0   |                 483   |                 47431   |                      60 |                447033 |            0    |            0.42 |
| 31–40   |          25 |         60 |         2 |                    10 |                     0   |                 822   |                 21885   |                      60 |                161873 |            0    |            0.42 |
| 41–60   |          50 |        120 |         2 |                    10 |                     0   |                2496.5 |                 28792.5 |                     120 |                208994 |            0    |            1.67 |
| 61–75   |          27 |        180 |         5 |                    10 |                     0.2 |                2551   |                 19116   |                     180 |                 82358 |            0    |            1.35 |
| 76–100  |          53 |        180 |         5 |                    10 |                     0.6 |                 846   |                  5273   |                     180 |                 15279 |            0.03 |            2.65 |
| 101–134 |          27 |        300 |        10 |                    12 |                     8   |                 245   |                   789   |                     300 |                  2021 |            0.27 |            2.25 |

Total: ladder 0.31 core-hours, search 8.75; C calls 1942 and 375526; C seconds 0.30 and 3.53 core-hours.

Not reached under the core-hour cap: none.

